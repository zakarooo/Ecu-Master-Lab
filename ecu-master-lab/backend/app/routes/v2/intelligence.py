"""
PHASE 7 — ECU Intelligence API Routes.

POST /api/ecu/identify      — Identify ECU from binary
POST /api/ecu/detect-maps   — Detect maps with DAMOS
GET  /api/knowledge/search  — Semantic search
GET  /api/knowledge/statistics — KB statistics
POST /api/knowledge/embeddings — Compute embeddings
GET  /api/knowledge/quality — Quality report
"""

import os
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ecu_engine.ecu_analyst import ECUAnalystAgent
from app.ecu_engine.ecu_matcher import ECUMatcher
from app.ecu_engine.semantic_search import SemanticSearchEngine
from app.ecu_engine.damos_quality_report import generate_quality_report
from app.ecu_engine.map_normalizer import MapNormalizer

logger = logging.getLogger("routes.intelligence")

router = APIRouter(prefix="/api", tags=["ECU Intelligence"])


@router.post("/ecu/identify")
async def identify_ecu(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Identify ECU from uploaded binary file."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(400, "Empty file")

        matcher = ECUMatcher(db)
        result = matcher.identify_ecu(content, file.filename or "")

        return {
            "status": "success",
            "filename": file.filename,
            "identification": {
                "ecu_name": result.ecu_name,
                "ecu_family": result.ecu_family,
                "confidence": round(result.confidence * 100, 1),
                "match_method": result.match_method,
                "db_model_match": result.db_model_match,
                "damos_match": result.damos_match,
                "warnings": result.warnings,
                "candidates": [
                    {
                        "model": c.model_name,
                        "vendor": c.vendor_id,
                        "family": c.family,
                        "processor": c.processor,
                        "flash_size_kb": c.flash_size,
                        "description": c.description,
                        "confidence": round(c.confidence * 100, 1),
                        "match_method": c.match_method,
                    }
                    for c in result.candidates[:5]
                ],
                "fingerprint": result.fingerprint,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ECU identification failed: %s", exc)
        raise HTTPException(500, "Identification failed: %s" % str(exc))


@router.post("/ecu/analyze")
async def analyze_ecu(
    file: UploadFile = File(...),
    use_damos: bool = Query(True, description="Use DAMOS data"),
    use_llm: bool = Query(False, description="Use LLM for insights"),
    run_quality: bool = Query(False, description="Run quality report"),
    db: Session = Depends(get_db),
):
    """Full ECU analysis with all KB layers."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(400, "Empty file")

        agent = ECUAnalystAgent(db)
        result = agent.analyze_binary(
            content,
            filename=file.filename or "",
            use_damos=use_damos,
            use_llm=use_llm,
            run_quality=run_quality,
        )

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": result.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ECU analysis failed: %s", exc)
        raise HTTPException(500, "Analysis failed: %s" % str(exc))


@router.post("/ecu/detect-maps")
async def detect_maps_from_file(
    file: UploadFile = File(...),
    ecu_name: Optional[str] = Query(None, description="ECU name for DAMOS lookup"),
    db: Session = Depends(get_db),
):
    """Detect maps with optional DAMOS metadata."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(400, "Empty file")

        damos_maps = []
        known_strings = []

        if ecu_name:
            from sqlalchemy import text
            rows = db.execute(text("""
                SELECT id, map_name, category, offset_hex, offset_dec,
                       size_bytes, unit
                FROM known_maps
                WHERE ecu_model_name LIKE :ecu
                ORDER BY offset_dec ASC
            """), {"ecu": "%" + ecu_name + "%"}).fetchall()

            damos_maps = [
                {
                    "id": r[0], "map_name": r[1], "category": r[2],
                    "offset_hex": r[3], "offset_dec": r[4] or 0,
                    "size_bytes": r[5] or 256, "unit": r[6],
                }
                for r in rows
            ]

            str_rows = db.execute(text("""
                SELECT DISTINCT string_content FROM known_strings
                WHERE LENGTH(string_content) >= 4
                LIMIT 200
            """)).fetchall()
            known_strings = [r[0] for r in str_rows if r[0]]

        from app.ecu_engine.map_detector import detect_maps
        result = detect_maps(
            content,
            damos_maps=damos_maps,
            known_strings=known_strings,
        )

        return {
            "status": "success",
            "filename": file.filename,
            "ecu_name": ecu_name,
            "damos_maps_loaded": len(damos_maps),
            "detection": {
                "total_maps": result.total_maps_found,
                "total_bytes": result.total_map_bytes,
                "confidence": round(result.confidence * 100, 1),
                "explanation": result.explanation,
                "maps": [
                    {
                        "name": m.name,
                        "category": m.category,
                        "offset": hex(m.offset),
                        "offset_dec": m.offset,
                        "size": m.size,
                        "rows": m.rows,
                        "cols": m.cols,
                        "data_type": m.data_type.value,
                        "min_value": m.min_value,
                        "max_value": m.max_value,
                        "avg_value": round(m.avg_value, 2),
                        "entropy": round(m.entropy, 3),
                        "non_empty_ratio": round(m.non_empty_ratio, 3),
                        "status": m.status,
                        "method": m.detection_method,
                        "damos_map_id": m.damos_map_id,
                    }
                    for m in result.maps
                ],
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Map detection failed: %s", exc)
        raise HTTPException(500, "Detection failed: %s" % str(exc))


@router.get("/knowledge/search")
async def search_knowledge(
    q: str = Query(..., description="Search query"),
    ecu: Optional[str] = Query(None, description="Filter by ECU"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search knowledge base maps."""
    try:
        engine = SemanticSearchEngine(db)
        results = engine.search(q, ecu_filter=ecu, category_filter=category, limit=limit)

        return {
            "status": "success",
            "query": q,
            "filters": {"ecu": ecu, "category": category},
            "total_results": len(results),
            "results": results,
        }
    except Exception as exc:
        logger.error("Search failed: %s", exc)
        raise HTTPException(500, "Search failed: %s" % str(exc))


@router.get("/knowledge/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get knowledge base statistics."""
    try:
        engine = SemanticSearchEngine(db)
        stats = engine.get_statistics()
        return {"status": "success", "statistics": stats}
    except Exception as exc:
        logger.error("Statistics failed: %s", exc)
        raise HTTPException(500, "Statistics failed: %s" % str(exc))


@router.post("/knowledge/embeddings")
async def compute_embeddings(
    batch_size: int = Query(500, ge=10, le=2000),
    db: Session = Depends(get_db),
):
    """Compute vector embeddings for maps (requires pgvector)."""
    try:
        engine = SemanticSearchEngine(db)
        engine.ensure_vector_column()
        engine.compute_embeddings(batch_size=batch_size)
        return {"status": "success", "message": "Embeddings computed"}
    except Exception as exc:
        logger.error("Embeddings failed: %s", exc)
        raise HTTPException(500, "Embeddings failed: %s" % str(exc))


@router.get("/knowledge/quality")
async def get_quality_report(db: Session = Depends(get_db)):
    """Get data quality report."""
    try:
        report = generate_quality_report(db)
        return {"status": "success", "report": report.to_dict()}
    except Exception as exc:
        logger.error("Quality report failed: %s", exc)
        raise HTTPException(500, "Quality report failed: %s" % str(exc))


@router.get("/ecu/list")
async def list_ecus(db: Session = Depends(get_db)):
    """List all known ECU models with map counts."""
    try:
        matcher = ECUMatcher(db)
        ecus = matcher.get_ecu_list()
        return {"status": "success", "ecus": ecus, "total": len(ecus)}
    except Exception as exc:
        logger.error("ECU list failed: %s", exc)
        raise HTTPException(500, "ECU list failed: %s" % str(exc))


@router.get("/ecu/{ecu_name}/coverage")
async def get_ecu_coverage(ecu_name: str, db: Session = Depends(get_db)):
    """Get map coverage for a specific ECU."""
    try:
        matcher = ECUMatcher(db)
        coverage = matcher.get_map_coverage(ecu_name)
        return {"status": "success", "coverage": coverage}
    except Exception as exc:
        logger.error("Coverage failed: %s", exc)
        raise HTTPException(500, "Coverage failed: %s" % str(exc))
