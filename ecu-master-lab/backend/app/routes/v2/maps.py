from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import Map, MapAxis, MapCategory, MapUnit
from app.schemas.ecu_schemas import (
    MapCategoryCreate,
    MapCategoryResponse,
    MapUnitCreate,
    MapUnitResponse,
    MapAxisCreate,
    MapAxisResponse,
    MapCreate,
    MapResponse,
)
from app.services.v2.ecu_services import MapCategoryService, MapUnitService, MapAxisService, MapService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/maps", tags=["V2 - Maps"])


# ─── Map Categories ─────────────────────────────────────────────────────────

@router.get("/categories", response_model=PaginatedResponse)
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MapCategory)
    if search:
        q = q.filter(MapCategory.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(MapCategory.sort_order, MapCategory.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/categories/roots", response_model=PaginatedResponse)
def list_root_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MapCategory).filter(MapCategory.parent_id.is_(None))
    items, total = paginate_query(q.order_by(MapCategory.sort_order, MapCategory.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/categories/{category_id}", response_model=MapCategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    c = MapCategoryService(db).get_by_id(category_id)
    if not c:
        raise HTTPException(404, "Map category not found")
    return c


@router.post("/categories", response_model=MapCategoryResponse, status_code=201)
def create_category(
    data: MapCategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MapCategoryService(db).create(data)


# ─── Map Units ──────────────────────────────────────────────────────────────

@router.get("/units", response_model=PaginatedResponse)
def list_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MapUnit)
    if search:
        q = q.filter(MapUnit.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(MapUnit.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/units/{unit_id}", response_model=MapUnitResponse)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    u = MapUnitService(db).get_by_id(unit_id)
    if not u:
        raise HTTPException(404, "Map unit not found")
    return u


@router.post("/units", response_model=MapUnitResponse, status_code=201)
def create_unit(
    data: MapUnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MapUnitService(db).create(data)


# ─── Map Axes ───────────────────────────────────────────────────────────────

@router.get("/axes", response_model=PaginatedResponse)
def list_axes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MapAxis)
    if search:
        q = q.filter(MapAxis.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(MapAxis.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/axes/{axis_id}", response_model=MapAxisResponse)
def get_axis(
    axis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    a = MapAxisService(db).get_by_id(axis_id)
    if not a:
        raise HTTPException(404, "Map axis not found")
    return a


@router.post("/axes", response_model=MapAxisResponse, status_code=201)
def create_axis(
    data: MapAxisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MapAxisService(db).create(data)


# ─── Maps ───────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
def list_maps(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Map)
    if search:
        q = q.filter(Map.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Map.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/search", response_model=PaginatedResponse)
def search_maps(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Map).filter(Map.name.ilike(f"%{q}%"))
    items, total = paginate_query(query.order_by(Map.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_maps_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Map).filter(Map.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(Map.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/category/{category_id}", response_model=PaginatedResponse)
def list_maps_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Map).filter(Map.category_id == category_id)
    items, total = paginate_query(q.order_by(Map.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{map_id}", response_model=MapResponse)
def get_map(
    map_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    m = MapService(db).get_by_id(map_id)
    if not m:
        raise HTTPException(404, "Map not found")
    return m


@router.post("", response_model=MapResponse, status_code=201)
def create_map(
    data: MapCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return MapService(db).create(data)
