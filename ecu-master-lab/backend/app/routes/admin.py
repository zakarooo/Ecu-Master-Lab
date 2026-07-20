import os
import shutil
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import require_admin
from app.models.models import User, Project, ProjectStatus, AuditLog, UserRole
from app.models.new.ecu_models import ECUFile
from app.models.schemas import AdminStats, AdminUserUpdate, UserResponse, ProjectResponse
from typing import List, Optional

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


class PaginatedUsers(BaseModel):
    items: List[UserResponse]
    total: int

class PaginatedProjects(BaseModel):
    items: List[ProjectResponse]
    total: int

@router.get("/users", response_model=PaginatedUsers)
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    total = db.query(func.count(User.id)).scalar()
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return PaginatedUsers(items=[UserResponse.model_validate(u) for u in users], total=total)


@router.put("/users/{user_id}")
def update_user(user_id: int, data: AdminUserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Impossible de modifier votre propre compte")
    if data.role is not None:
        user.role = UserRole(data.role)
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    return {"message": "Utilisateur mis à jour"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte")

    project_count = db.query(func.count(Project.id)).filter(Project.user_id == user_id).scalar()
    if project_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cet utilisateur possède {project_count} projet(s). Transférez-les d'abord."
        )

    log = AuditLog(
        user_id=admin.id, action="ADMIN_DELETE_USER", resource_type="user",
        resource_id=user.id, details=f"Utilisateur {user.email} supprimé par admin #{admin.id}",
    )
    db.add(log)
    db.delete(user)
    db.commit()

    return {"message": f"Utilisateur {user.email} supprimé"}


@router.get("/projects", response_model=PaginatedProjects)
def list_all_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    total = db.query(func.count(Project.id)).scalar()
    projects = db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return PaginatedProjects(items=[ProjectResponse.model_validate(p) for p in projects], total=total)


@router.get("/audit-logs")
def list_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    total = db.query(func.count(AuditLog.id)).scalar()
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "items": [
            {
                "id": l.id, "user_id": l.user_id, "action": l.action,
                "resource_type": l.resource_type, "resource_id": l.resource_id,
                "details": l.details, "created_at": l.created_at,
            }
            for l in logs
        ],
        "total": total,
    }


class TransferRequest(BaseModel):
    target_user_id: int


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    project_dir = os.path.join(os.path.dirname(project.ecu_file_path or ""), "..") if project.ecu_file_path else None
    if project_dir and os.path.isdir(project_dir):
        try:
            shutil.rmtree(project_dir)
        except Exception:
            pass

    ecu_files = db.query(ECUFile).filter(ECUFile.project_id == project_id).all()
    for ef in ecu_files:
        db.delete(ef)
    db.flush()

    log = AuditLog(
        user_id=admin.id, action="ADMIN_DELETE_PROJECT", resource_type="project",
        resource_id=project.id, details=f"Supprimé par admin #{admin.id}",
    )
    db.add(log)
    db.delete(project)
    db.commit()

    return {"message": "Projet supprimé"}


@router.post("/projects/{project_id}/transfer")
def transfer_project(project_id: int, data: TransferRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    target = db.query(User).filter(User.id == data.target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur cible non trouvé")

    old_user_id = project.user_id
    project.user_id = data.target_user_id
    db.commit()

    log = AuditLog(
        user_id=admin.id, action="ADMIN_TRANSFER_PROJECT", resource_type="project",
        resource_id=project.id, details=f"Transféré de user #{old_user_id} vers user #{data.target_user_id}",
    )
    db.add(log)
    db.commit()

    return {"message": f"Projet transféré vers l'utilisateur #{data.target_user_id}"}
