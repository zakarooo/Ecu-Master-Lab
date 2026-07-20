"""
Routes API — Base de connaissances ECU.

Permet d'enregistrer des fichiers connus, de consulter la base,
et de soumettre des corrections.
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_expert_or_admin
from app.models.new.ecu_models import (
    AnalysisCorrection,
    KnownChecksum,
    KnownEcuFile,
    KnownMap,
    KnownSegment,
    KnownSignature,
    KnownString,
)
from app.routes.v2.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/knowledge", tags=["Knowledge"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ecu_files" if hasattr(settings, "UPLOAD_DIR") else Path("uploads/ecu_files")


# --- Schemas ---

class RegisterKnownFileRequest(BaseModel):
    ecu_model_name: str
    manufacturer_name: Optional[str] = None
    ecu_model_id: Optional[int] = None
    notes: Optional[str] = None


class RegisterKnownFileResponse(BaseModel):
    status: str
    known_file_id: Optional[int] = None
    signatures: int = 0
    strings: int = 0
    segments: int = 0
    message: str = ""


class CorrectionRequest(BaseModel):
    analysis_id: int
    corrected_model_name: str
    corrected_manufacturer: Optional[str] = None
    comment: Optional[str] = None


class CorrectionResponse(BaseModel):
    status: str
    correction_id: int
    message: str


class KnownFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sha256: str
    filename: Optional[str] = None
    file_size: Optional[int] = None
    ecu_model_name: Optional[str] = None
    manufacturer_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


class SignatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ecu_model_name: Optional[str] = None
    category: str
    pattern_hex: str
    context_hex: Optional[str] = None
    occurrence_count: Optional[int] = 1
    confidence: Optional[float] = 0.5


class StringResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ecu_model_name: Optional[str] = None
    string_value: str
    category: Optional[str] = None
    occurrence_count: Optional[int] = 1
    confidence: Optional[float] = 0.5


class KnowledgeStats(BaseModel):
    total_known_files: int
    total_signatures: int
    total_strings: int
    total_maps: int
    total_checksums: int
    total_segments: int
    total_corrections: int
    ecu_models_covered: int


# --- Routes ---

@router.get("/stats")
def get_knowledge_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.routes.v2.intelligence import get_statistics
    return get_statistics(db=db, current_user=current_user)


@router.post("/register", response_model=RegisterKnownFileResponse, status_code=201)
def register_known_file(
    file: UploadFile = File(...),
    ecu_model_name: str = Form(""),
    manufacturer_name: str = Form(""),
    ecu_model_id: Optional[int] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(require_expert_or_admin),
):
    """Register a known ECU file and extract its features into the knowledge DB."""
    content = file.file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    from app.ecu_engine.knowledge_extractor import extract_and_store

    import re
    safe_name = re.sub(r'[^\w\-.]', '_', file.filename or "unknown")
    file_path = str(UPLOAD_DIR / safe_name)
    result = extract_and_store(
        db=db,
        data=content,
        filename=file.filename or "unknown",
        file_path=file_path,
        ecu_model_name=ecu_model_name,
        manufacturer_name=manufacturer_name,
        ecu_model_id=ecu_model_id,
        user_id=current_user.id,
        notes=notes,
    )

    return RegisterKnownFileResponse(
        status=result.get("status", "ok"),
        known_file_id=result.get("known_file_id"),
        signatures=result.get("signatures", 0),
        strings=result.get("strings", 0),
        segments=result.get("segments", 0),
        message="File registered and features extracted" if result.get("status") != "already_registered" else "File already in knowledge DB",
    )


@router.get("/known-files", response_model=PaginatedResponse)
def list_known_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(KnownEcuFile)
    if search:
        q = q.filter(
            KnownEcuFile.ecu_model_name.ilike(f"%{search}%")
            | KnownEcuFile.filename.ilike(f"%{search}%")
        )
    items, total = paginate_query(q.order_by(KnownEcuFile.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/signatures", response_model=PaginatedResponse)
def list_signatures(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    ecu_model: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(KnownSignature)
    if search:
        q = q.filter(KnownSignature.pattern_hex.ilike(f"%{search}%"))
    if ecu_model:
        q = q.filter(KnownSignature.ecu_model_name.ilike(f"%{ecu_model}%"))
    items, total = paginate_query(q.order_by(KnownSignature.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/strings", response_model=PaginatedResponse)
def list_strings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(KnownString)
    if search:
        q = q.filter(KnownString.string_value.ilike(f"%{search}%"))
    if category:
        q = q.filter(KnownString.category == category)
    items, total = paginate_query(q.order_by(KnownString.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/corrections", response_model=CorrectionResponse, status_code=201)
def submit_correction(
    req: CorrectionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_expert_or_admin),
):
    """Submit a correction for an analysis result."""
    correction = AnalysisCorrection(
        analysis_id=req.analysis_id,
        original_prediction="",
        corrected_model_name=req.corrected_model_name,
        corrected_manufacturer=req.corrected_manufacturer,
        comment=req.comment,
        corrected_by=current_user.id,
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)

    return CorrectionResponse(
        status="ok",
        correction_id=correction.id,
        message="Correction submitted. The knowledge base will be enriched.",
    )
