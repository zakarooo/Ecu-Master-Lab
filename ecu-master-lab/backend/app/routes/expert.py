from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_expert_or_admin
from app.models.models import User, Project, ProjectStatus, AuditLog

router = APIRouter(prefix="/api/expert", tags=["Expert"])


class RejectRequest(BaseModel):
    reason: str


@router.get("/projects/pending-review")
def list_pending_review(
    db: Session = Depends(get_db),
    admin: User = Depends(require_expert_or_admin),
):
    projects = db.query(Project).filter(
        Project.status == ProjectStatus.NEEDS_REVIEW
    ).order_by(Project.created_at.desc()).all()

    result = []
    for p in projects:
        result.append({
            "id": p.id,
            "name": p.name,
            "status": p.status.value,
            "vehicle_make": p.vehicle_make,
            "vehicle_model": p.vehicle_model,
            "vehicle_year": p.vehicle_year,
            "ecu_filename": p.ecu_filename,
            "ai_detected_ecu": p.ai_detected_ecu,
            "ai_confidence": p.ai_confidence,
            "ai_analysis_json": p.ai_analysis_json,
            "created_at": p.created_at,
            "user_id": p.user_id,
        })
    return result


@router.post("/projects/{project_id}/approve")
def approve_project(
    project_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_expert_or_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status != ProjectStatus.NEEDS_REVIEW:
        raise HTTPException(status_code=400, detail="Ce projet n'est pas en attente de revue")

    project.status = ProjectStatus.ANALYZED
    db.commit()

    log = AuditLog(
        user_id=admin.id,
        action="EXPERT_APPROVE",
        resource_type="project",
        resource_id=project.id,
        details=f"Approuvé par expert #{admin.id}",
    )
    db.add(log)
    db.commit()

    return {"message": "Projet approuvé. Le traitement peut continuer."}


@router.post("/projects/{project_id}/reject")
def reject_project(
    project_id: int,
    data: RejectRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_expert_or_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status != ProjectStatus.NEEDS_REVIEW:
        raise HTTPException(status_code=400, detail="Ce projet n'est pas en attente de revue")

    project.status = ProjectStatus.FAILED
    project.rejection_reason = data.reason
    db.commit()

    log = AuditLog(
        user_id=admin.id,
        action="EXPERT_REJECT",
        resource_type="project",
        resource_id=project.id,
        details=f"Rejeté par expert #{admin.id}: {data.reason}",
    )
    db.add(log)
    db.commit()

    return {"message": "Projet rejeté."}
