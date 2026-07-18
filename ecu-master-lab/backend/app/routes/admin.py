from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import require_admin
from app.models.models import User, Project, ProjectStatus, AuditLog, UserRole
from app.models.schemas import AdminStats, AdminUserUpdate, UserResponse, ProjectResponse
from typing import List

router = APIRouter(prefix="/api/admin", tags=["Administration"])


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return AdminStats(
        total_users=db.query(func.count(User.id)).scalar(),
        total_projects=db.query(func.count(Project.id)).scalar(),
        pending_projects=db.query(func.count(Project.id)).filter(Project.status == ProjectStatus.PENDING).scalar(),
        completed_projects=db.query(func.count(Project.id)).filter(Project.status == ProjectStatus.COMPLETED).scalar(),
        analyzing_projects=db.query(func.count(Project.id)).filter(Project.status.in_([
            ProjectStatus.ANALYZING, ProjectStatus.PROCESSING
        ])).scalar(),
        failed_projects=db.query(func.count(Project.id)).filter(Project.status == ProjectStatus.FAILED).scalar(),
    )


@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}")
def update_user(user_id: int, data: AdminUserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if data.role is not None:
        user.role = UserRole(data.role)
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    return {"message": "Utilisateur mis à jour"}


@router.get("/projects", response_model=List[ProjectResponse])
def list_all_projects(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/audit-logs")
def list_audit_logs(limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id, "user_id": l.user_id, "action": l.action,
            "resource_type": l.resource_type, "resource_id": l.resource_id,
            "details": l.details, "created_at": l.created_at,
        }
        for l in logs
    ]
