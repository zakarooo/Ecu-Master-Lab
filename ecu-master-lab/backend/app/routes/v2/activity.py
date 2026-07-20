from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_expert_or_admin
from app.models.models import User, UserRole
from app.models.new.ecu_models import ActivityLog
from app.schemas.ecu_schemas import (
    ActivityLogCreate,
    ActivityLogResponse,
)
from app.services.v2.ecu_services import ActivityLogService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/activity", tags=["V2 - Activity Logs"])


@router.get("", response_model=PaginatedResponse)
def list_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ActivityLog)
    if current_user.role != UserRole.ADMIN:
        q = q.filter(ActivityLog.user_id == current_user.id)
    if search:
        q = q.filter(ActivityLog.action.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ActivityLog.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{log_id}", response_model=ActivityLogResponse)
def get_activity_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    l = ActivityLogService(db).get_by_id(log_id)
    if not l:
        raise HTTPException(404, "Activity log not found")
    if current_user.role != UserRole.ADMIN and l.user_id != current_user.id:
        raise HTTPException(404, "Activity log not found")
    return l


@router.get("/user/{user_id}", response_model=PaginatedResponse)
def list_logs_by_user(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN and user_id != current_user.id:
        raise HTTPException(404, "Activity log not found")
    q = db.query(ActivityLog).filter(ActivityLog.user_id == user_id)
    items, total = paginate_query(q.order_by(ActivityLog.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/resource/{resource_type}/{resource_id}", response_model=PaginatedResponse)
def list_logs_by_resource(
    resource_type: str,
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ActivityLog).filter(
        ActivityLog.resource_type == resource_type,
        ActivityLog.resource_id == resource_id,
    )
    if current_user.role != UserRole.ADMIN:
        q = q.filter(ActivityLog.user_id == current_user.id)
    items, total = paginate_query(q.order_by(ActivityLog.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=ActivityLogResponse, status_code=201)
def create_activity_log(
    data: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_expert_or_admin),
):
    return ActivityLogService(db).create(data)
