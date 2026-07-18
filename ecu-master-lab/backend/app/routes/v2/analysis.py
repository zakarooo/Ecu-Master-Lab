from __future__ import annotations

import asyncio
import hashlib
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.new.ecu_models import (
    Analysis,
    AnalysisHypothesis,
    AnalysisResult,
    AnalysisScore,
    ChecksumResult,
    DetectedMap,
    DetectedSegment,
    ECUFile,
)
from app.schemas.ecu_schemas import (
    AnalysisHypothesisResponse,
    AnalysisResponse,
    AnalysisResultResponse,
    AnalysisScoreResponse,
    ChecksumResultResponse,
    DetectedMapResponse,
    DetectedSegmentResponse,
    ECUFileCreate,
    ECUFileResponse,
)
from app.services.v2.ecu_services import AnalysisService, ECUFileService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/analysis", tags=["V2 - Analysis"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ecu_files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ecu_file: ECUFileResponse
    analysis: Optional[AnalysisResponse] = None


class FullAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis: AnalysisResponse
    hypotheses: List[AnalysisHypothesisResponse] = []
    scores: List[AnalysisScoreResponse] = []
    detected_maps: List[DetectedMapResponse] = []
    detected_segments: List[DetectedSegmentResponse] = []
    checksums: List[ChecksumResultResponse] = []
    results: List[AnalysisResultResponse] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _detect_file_format(filename: str) -> Optional[str]:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext in ("bin", "hex", "s19", "srec", "mot", "mpc", "i28", "hex8", "raf"):
        return ext
    return None


def _run_engine_analysis(file_path: str, raw_data: bytes, db=None) -> Dict[str, Any]:
    from app.agents.ecu_ai_engine import analyze_ecu_file

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(analyze_ecu_file(file_path, raw_data, db=db))
    finally:
        loop.close()


def _build_full_analysis(
    svc: AnalysisService, analysis_id: int
) -> FullAnalysisResponse:
    analysis = svc.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(404, "Analysis not found")

    hypotheses = svc.hypothesis_repo.list_by_analysis(analysis_id)
    scores = svc.score_repo.list_by_analysis(analysis_id)
    detected_maps = svc.detected_map_repo.list_by_analysis(analysis_id)
    detected_segments = svc.detected_segment_repo.list_by_analysis(analysis_id)
    checksums = svc.checksum_repo.list_by_analysis(analysis_id)
    results = svc.result_repo.list_by_analysis(analysis_id)

    return FullAnalysisResponse(
        analysis=analysis,
        hypotheses=hypotheses,
        scores=scores,
        detected_maps=detected_maps,
        detected_segments=detected_segments,
        checksums=checksums,
        results=results,
    )


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=UploadResponse, status_code=201)
def upload_ecu_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Query(None),
    run_analysis: bool = Form(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = file.file.read()
    file.file.seek(0)
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(400, "Uploaded file is empty")

    sha256 = _compute_sha256(content)

    file_svc = ECUFileService(db)
    existing = file_svc.get_by_sha256(sha256)
    if existing:
        ecu_file = existing
    else:
        safe_name = "{}_{}".format(uuid.uuid4().hex[:12], file.filename or "upload")
        dest_dir = UPLOAD_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / safe_name

        with open(str(dest_path), "wb") as f:
            f.write(content)

        file_format = _detect_file_format(file.filename or "")

        ecu_file = file_svc.create(
            ECUFileCreate(
                project_id=project_id,
                filename=file.filename or safe_name,
                file_path=str(dest_path.resolve()),
                file_size=file_size,
                sha256=sha256,
                md5=None,
                file_format=file_format,
                uploaded_by=current_user.id,
            )
        )

    analysis_result = None
    if run_analysis:
        file_path = str(Path(ecu_file.file_path).resolve())
        if not file_path or not os.path.isfile(file_path):
            raise HTTPException(400, "ECU file binary not found on disk")

        with open(file_path, "rb") as f:
            raw_data = f.read()

        engine_result = _run_engine_analysis(file_path, raw_data, db=db)

        svc_analysis = AnalysisService(db)
        analysis_result = svc_analysis.save_analysis(
            ecu_file_id=ecu_file.id, engine_result=engine_result
        )

        # Auto-populate knowledge base after successful analysis
        if analysis_result:
            try:
                from app.ecu_engine.knowledge_extractor import extract_and_store
                ecu_model = engine_result.get("ecu_model", engine_result.get("file_name", "Unknown"))
                extract_and_store(
                    db=db,
                    data=raw_data,
                    filename=ecu_file.filename or "unknown",
                    file_path=ecu_file.file_path or "",
                    ecu_model_name=ecu_model,
                    manufacturer_name=engine_result.get("manufacturer", ""),
                )
                db.commit()
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "Knowledge extraction failed after analysis: %s", exc
                )

    return UploadResponse(ecu_file=ecu_file, analysis=analysis_result)


# ---------------------------------------------------------------------------
# ECU Files
# ---------------------------------------------------------------------------

@router.get("/files", response_model=PaginatedResponse)
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUFile)
    if search:
        q = q.filter(ECUFile.filename.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ECUFile.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/files/{file_id}", response_model=ECUFileResponse)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = ECUFileService(db)
    f = svc.get_by_id(file_id)
    if not f:
        raise HTTPException(404, "ECU file not found")
    return f


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------

@router.get("/analyses", response_model=PaginatedResponse)
def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Analysis)
    if search:
        q = q.filter(Analysis.detected_ecu_model.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Analysis.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = AnalysisService(db)
    a = svc.get_by_id(analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found")
    return a


@router.get("/analyses/file/{ecu_file_id}", response_model=PaginatedResponse)
def list_analyses_by_file(
    ecu_file_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Analysis).filter(Analysis.ecu_file_id == ecu_file_id)
    items, total = paginate_query(q.order_by(Analysis.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------

@router.post(
    "/analyses/{ecu_file_id}/run",
    response_model=AnalysisResponse,
    status_code=201,
)
def run_analysis(
    ecu_file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc_file = ECUFileService(db)
    ecu_file = svc_file.get_by_id(ecu_file_id)
    if not ecu_file:
        raise HTTPException(404, "ECU file not found")

    file_path = str(Path(ecu_file.file_path).resolve())
    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(400, "ECU file binary not found on disk")

    with open(file_path, "rb") as f:
        raw_data = f.read()

    engine_result = _run_engine_analysis(file_path, raw_data, db=db)

    svc_analysis = AnalysisService(db)
    created = svc_analysis.save_analysis(
        ecu_file_id=ecu_file_id, engine_result=engine_result
    )

    # Auto-populate knowledge base after successful analysis
    if created:
        try:
            from app.ecu_engine.knowledge_extractor import extract_and_store
            ecu_model = engine_result.get("ecu_model", engine_result.get("file_name", "Unknown"))
            extract_and_store(
                db=db,
                data=raw_data,
                filename=ecu_file.filename or "unknown",
                file_path=ecu_file.file_path or "",
                ecu_model_name=ecu_model,
                manufacturer_name=engine_result.get("manufacturer", ""),
            )
            db.commit()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Knowledge extraction failed after analysis: %s", exc
            )

    return created


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------

@router.get("/analyses/{analysis_id}/full", response_model=FullAnalysisResponse)
def get_full_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = AnalysisService(db)
    return _build_full_analysis(svc, analysis_id)


# ---------------------------------------------------------------------------
# Sub-result endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/analyses/{analysis_id}/results",
    response_model=PaginatedResponse,
)
def list_analysis_results(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(AnalysisResult.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/analyses/{analysis_id}/hypotheses",
    response_model=PaginatedResponse,
)
def list_analysis_hypotheses(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AnalysisHypothesis).filter(AnalysisHypothesis.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(AnalysisHypothesis.rank), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/analyses/{analysis_id}/scores",
    response_model=PaginatedResponse,
)
def list_analysis_scores(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AnalysisScore).filter(AnalysisScore.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(AnalysisScore.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/analyses/{analysis_id}/detected-maps",
    response_model=PaginatedResponse,
)
def list_detected_maps(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(DetectedMap).filter(DetectedMap.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(DetectedMap.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/analyses/{analysis_id}/detected-segments",
    response_model=PaginatedResponse,
)
def list_detected_segments(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(DetectedSegment).filter(DetectedSegment.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(DetectedSegment.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/analyses/{analysis_id}/checksums",
    response_model=PaginatedResponse,
)
def list_checksum_results(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ChecksumResult).filter(ChecksumResult.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(ChecksumResult.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)
