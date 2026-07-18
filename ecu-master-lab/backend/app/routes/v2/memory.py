from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import MemoryLayout, MemorySegment
from app.schemas.ecu_schemas import (
    MemoryLayoutCreate,
    MemoryLayoutResponse,
    MemorySegmentCreate,
    MemorySegmentResponse,
)
from app.services.v2.ecu_services import MemoryLayoutService, MemorySegmentService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/memory", tags=["V2 - Memory"])


# ─── Memory Layouts ─────────────────────────────────────────────────────────

@router.get("/layouts", response_model=PaginatedResponse)
def list_layouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MemoryLayout)
    if search:
        q = q.filter(MemoryLayout.notes.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(MemoryLayout.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/layouts/{layout_id}", response_model=MemoryLayoutResponse)
def get_layout(
    layout_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    l = MemoryLayoutService(db).get_by_id(layout_id)
    if not l:
        raise HTTPException(404, "Memory layout not found")
    return l


@router.get("/layouts/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_layouts_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MemoryLayout).filter(MemoryLayout.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(MemoryLayout.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/layouts", response_model=MemoryLayoutResponse, status_code=201)
def create_layout(
    data: MemoryLayoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MemoryLayoutService(db).create(data)


# ─── Memory Segments ────────────────────────────────────────────────────────

@router.get("/segments", response_model=PaginatedResponse)
def list_segments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MemorySegment)
    if search:
        q = q.filter(MemorySegment.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(MemorySegment.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/segments/{segment_id}", response_model=MemorySegmentResponse)
def get_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = MemorySegmentService(db).get_by_id(segment_id)
    if not s:
        raise HTTPException(404, "Memory segment not found")
    return s


@router.get("/segments/layout/{layout_id}", response_model=PaginatedResponse)
def list_segments_by_layout(
    layout_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MemorySegment).filter(MemorySegment.layout_id == layout_id)
    items, total = paginate_query(q.order_by(MemorySegment.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/segments", response_model=MemorySegmentResponse, status_code=201)
def create_segment(
    data: MemorySegmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MemorySegmentService(db).create(data)
