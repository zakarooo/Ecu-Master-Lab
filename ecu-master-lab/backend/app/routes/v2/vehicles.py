from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import VehicleBrand, VehicleModel, VehicleEngine
from app.schemas.ecu_schemas import (
    VehicleBrandCreate,
    VehicleBrandResponse,
    VehicleModelCreate,
    VehicleModelResponse,
    VehicleEngineCreate,
    VehicleEngineResponse,
)
from app.services.v2.ecu_services import VehicleBrandService, VehicleModelService, VehicleEngineService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/vehicles", tags=["V2 - Vehicles"])


# ─── Vehicle Brands ──────────────────────────────────────────────────────────

@router.get("/brands", response_model=PaginatedResponse)
def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(VehicleBrand)
    if search:
        q = q.filter(VehicleBrand.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(VehicleBrand.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/brands/{brand_id}", response_model=VehicleBrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    b = VehicleBrandService(db).get_by_id(brand_id)
    if not b:
        raise HTTPException(404, "Vehicle brand not found")
    return b


@router.post("/brands", response_model=VehicleBrandResponse, status_code=201)
def create_brand(
    data: VehicleBrandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return VehicleBrandService(db).create(data)


# ─── Vehicle Models ──────────────────────────────────────────────────────────

@router.get("/models", response_model=PaginatedResponse)
def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(VehicleModel)
    if search:
        q = q.filter(VehicleModel.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(VehicleModel.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/models/{model_id}", response_model=VehicleModelResponse)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    m = VehicleModelService(db).get_by_id(model_id)
    if not m:
        raise HTTPException(404, "Vehicle model not found")
    return m


@router.get("/models/brand/{brand_id}", response_model=PaginatedResponse)
def list_models_by_brand(
    brand_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(VehicleModel).filter(VehicleModel.brand_id == brand_id)
    items, total = paginate_query(q.order_by(VehicleModel.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/models", response_model=VehicleModelResponse, status_code=201)
def create_model(
    data: VehicleModelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return VehicleModelService(db).create(data)


# ─── Vehicle Engines ─────────────────────────────────────────────────────────

@router.get("/engines", response_model=PaginatedResponse)
def list_engines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(VehicleEngine)
    if search:
        q = q.filter(VehicleEngine.engine_code.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(VehicleEngine.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/engines/{engine_id}", response_model=VehicleEngineResponse)
def get_engine(
    engine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    e = VehicleEngineService(db).get_by_id(engine_id)
    if not e:
        raise HTTPException(404, "Vehicle engine not found")
    return e


@router.get("/engines/model/{model_id}", response_model=PaginatedResponse)
def list_engines_by_model(
    model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(VehicleEngine).filter(VehicleEngine.model_id == model_id)
    items, total = paginate_query(q.order_by(VehicleEngine.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/engines", response_model=VehicleEngineResponse, status_code=201)
def create_engine(
    data: VehicleEngineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return VehicleEngineService(db).create(data)
