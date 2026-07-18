from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import HardwareVersion, SoftwareVersion
from app.schemas.ecu_schemas import (
    SoftwareVersionCreate,
    SoftwareVersionResponse,
    HardwareVersionCreate,
    HardwareVersionResponse,
)
from app.services.v2.ecu_services import SoftwareVersionService, HardwareVersionService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/versions", tags=["V2 - Versions"])


# ─── Software Versions ──────────────────────────────────────────────────────

@router.get("/software", response_model=PaginatedResponse)
def list_software_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(SoftwareVersion)
    if search:
        q = q.filter(SoftwareVersion.sw_number.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(SoftwareVersion.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/software/{sw_id}", response_model=SoftwareVersionResponse)
def get_software_version(
    sw_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    v = SoftwareVersionService(db).get_by_id(sw_id)
    if not v:
        raise HTTPException(404, "Software version not found")
    return v


@router.get("/software/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_software_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(SoftwareVersion).filter(SoftwareVersion.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(SoftwareVersion.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/software", response_model=SoftwareVersionResponse, status_code=201)
def create_software_version(
    data: SoftwareVersionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return SoftwareVersionService(db).create(data)


# ─── Hardware Versions ──────────────────────────────────────────────────────

@router.get("/hardware", response_model=PaginatedResponse)
def list_hardware_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(HardwareVersion)
    if search:
        q = q.filter(HardwareVersion.hw_number.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(HardwareVersion.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hardware/{hw_id}", response_model=HardwareVersionResponse)
def get_hardware_version(
    hw_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    v = HardwareVersionService(db).get_by_id(hw_id)
    if not v:
        raise HTTPException(404, "Hardware version not found")
    return v


@router.get("/hardware/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_hardware_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(HardwareVersion).filter(HardwareVersion.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(HardwareVersion.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/hardware", response_model=HardwareVersionResponse, status_code=201)
def create_hardware_version(
    data: HardwareVersionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return HardwareVersionService(db).create(data)
