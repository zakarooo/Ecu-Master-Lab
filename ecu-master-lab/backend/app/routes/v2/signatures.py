from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import BinaryPattern, ECUSignature
from app.schemas.ecu_schemas import (
    ECUSignatureCreate,
    ECUSignatureResponse,
    BinaryPatternCreate,
    BinaryPatternResponse,
)
from app.services.v2.ecu_services import ECUSignatureService, BinaryPatternService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/signatures", tags=["V2 - Signatures"])


# ─── ECU Signatures ─────────────────────────────────────────────────────────

@router.get("/ecu-signatures", response_model=PaginatedResponse)
def list_ecu_signatures(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUSignature)
    if search:
        q = q.filter(ECUSignature.signature_name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ECUSignature.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/ecu-signatures/{sig_id}", response_model=ECUSignatureResponse)
def get_ecu_signature(
    sig_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = ECUSignatureService(db).get_by_id(sig_id)
    if not s:
        raise HTTPException(404, "ECU signature not found")
    return s


@router.get("/ecu-signatures/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_ecu_signatures_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUSignature).filter(ECUSignature.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(ECUSignature.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/ecu-signatures", response_model=ECUSignatureResponse, status_code=201)
def create_ecu_signature(
    data: ECUSignatureCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ECUSignatureService(db).create(data)


# ─── Binary Patterns ────────────────────────────────────────────────────────

@router.get("/binary-patterns", response_model=PaginatedResponse)
def list_binary_patterns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(BinaryPattern)
    if search:
        q = q.filter(BinaryPattern.pattern_name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(BinaryPattern.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/binary-patterns/{pattern_id}", response_model=BinaryPatternResponse)
def get_binary_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = BinaryPatternService(db).get_by_id(pattern_id)
    if not p:
        raise HTTPException(404, "Binary pattern not found")
    return p


@router.get("/binary-patterns/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_binary_patterns_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(BinaryPattern).filter(BinaryPattern.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(BinaryPattern.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/binary-patterns", response_model=BinaryPatternResponse, status_code=201)
def create_binary_pattern(
    data: BinaryPatternCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return BinaryPatternService(db).create(data)
