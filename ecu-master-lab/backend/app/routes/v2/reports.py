from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import Export, Report
from app.schemas.ecu_schemas import (
    ReportCreate,
    ReportResponse,
    ExportCreate,
    ExportResponse,
)
from app.services.v2.ecu_services import ReportService, ExportService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/reports", tags=["V2 - Reports"])


@router.get("", response_model=PaginatedResponse)
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Report)
    if search:
        q = q.filter(Report.title.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Report.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/analysis/{analysis_id}", response_model=PaginatedResponse)
def list_reports_by_analysis(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Report).filter(Report.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(Report.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/exports", response_model=PaginatedResponse)
def list_exports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Export)
    if search:
        q = q.filter(Export.export_format.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Export.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/exports/{export_id}", response_model=ExportResponse)
def get_export(export_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    e = ExportService(db).get_by_id(export_id)
    if not e:
        raise HTTPException(404, "Export not found")
    return e


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = ReportService(db).get_by_id(report_id)
    if not r:
        raise HTTPException(404, "Report not found")
    return r


@router.post("", response_model=ReportResponse, status_code=201)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ReportService(db).create(data)


@router.post("/exports", response_model=ExportResponse, status_code=201)
def create_export(
    data: ExportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ExportService(db).create(data)
