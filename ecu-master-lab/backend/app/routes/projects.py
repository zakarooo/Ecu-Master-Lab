import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.models import User, Project, ProjectStatus, FileVersion, AuditLog
from app.models.schemas import ProjectCreate, ProjectResponse, ModificationSelect
from app.services.file_service import save_uploaded_file, save_version
from app.agents.ecu_ai_engine import analyze_ecu_file, generate_modified_file
from typing import List, Optional

router = APIRouter(prefix="/api/projects", tags=["Projets ECU"])

ALLOWED_EXTENSIONS = {".bin", ".ori", ".hex", ".frf", ".mpc", ".bdm", ".zip"}


@router.post("", response_model=ProjectResponse)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = Project(
        name=data.name,
        user_id=current_user.id,
        vehicle_make=data.vehicle_make,
        vehicle_model=data.vehicle_model,
        vehicle_year=data.vehicle_year,
        vehicle_engine=data.vehicle_engine,
        vehicle_power=data.vehicle_power,
        vehicle_ecu_type=data.vehicle_ecu_type,
        vehicle_mileage=data.vehicle_mileage,
        vehicle_gearbox=data.vehicle_gearbox,
        vehicle_vin=data.vehicle_vin,
        tool_used=data.tool_used,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    log = AuditLog(user_id=current_user.id, action="CREATE_PROJECT", resource_type="project", resource_id=project.id)
    db.add(log)
    db.commit()

    return ProjectResponse.model_validate(project)


@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/upload")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format non supporté: {ext}. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50MB)")

    file_info = save_uploaded_file(content, file.filename, project_id)

    project.ecu_filename = file.filename
    project.ecu_file_path = file_info["file_path"]
    project.ecu_file_size = file_info["file_size"]
    project.ecu_file_hash = file_info["file_hash"]
    project.ecu_original_backup = file_info["backup_path"]
    project.status = ProjectStatus.ANALYZING
    db.commit()

    log = AuditLog(
        user_id=current_user.id, action="UPLOAD_FILE", resource_type="project",
        resource_id=project.id, details=f"File: {file.filename}, Size: {file_info['file_size']}"
    )
    db.add(log)
    db.commit()

    analysis = await analyze_ecu_file(file_info["file_path"], content, db=db)

    project.ai_detected_ecu = analysis["ecu_type"]
    project.ai_detected_hw = analysis["hw_version"]
    project.ai_detected_sw = analysis["sw_version"]
    project.ai_checksum_valid = analysis["checksum_valid"]
    project.ai_confidence = analysis["confidence"]
    project.ai_analysis_json = json.dumps(analysis)
    project.vehicle_ecu_type = analysis["ecu_type"]

    if "REVIEW_REQUIRED" in analysis["recommendation"]:
        project.status = ProjectStatus.NEEDS_REVIEW
    else:
        project.status = ProjectStatus.ANALYZED

    version = save_version(file_info["file_path"], project_id, 1, "Original")
    fv = FileVersion(
        project_id=project_id,
        version_number=1,
        file_path=version["file_path"],
        file_hash=version["file_hash"],
        label="Original",
    )
    db.add(fv)
    db.commit()

    return {
        "message": "Fichier uploadé et analysé avec succès",
        "analysis": analysis,
        "status": project.status.value,
    }


@router.post("/{project_id}/modifications")
def select_modifications(
    project_id: int,
    data: ModificationSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status not in [ProjectStatus.ANALYZED, ProjectStatus.NEEDS_REVIEW]:
        raise HTTPException(status_code=400, detail="Le fichier doit d'abord être analysé")

    project.modifications = json.dumps(data.modifications)
    project.client_notes = data.client_notes
    project.status = ProjectStatus.PROCESSING
    db.commit()

    return {"message": "Modifications enregistrées", "modifications": data.modifications}


@router.post("/{project_id}/process")
async def process_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status == ProjectStatus.NEEDS_REVIEW:
        raise HTTPException(
            status_code=400,
            detail="Ce fichier nécessite la validation d'un expert avant traitement. "
                   "L'analyse a détecté des risques qui empêchent le traitement automatique."
        )

    if project.status != ProjectStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="Le projet n'est pas prêt pour le traitement")

    if not project.ecu_file_path:
        raise HTTPException(status_code=400, detail="Aucun fichier ECU trouvé")

    with open(project.ecu_file_path, "rb") as f:
        original_content = f.read()

    analysis = json.loads(project.ai_analysis_json) if project.ai_analysis_json else {}
    modifications = json.loads(project.modifications) if project.modifications else []

    modified_content = await generate_modified_file(original_content, analysis, modifications)

    import hashlib
    result_hash = hashlib.sha256(modified_content).hexdigest()
    result_filename = f"modified_{project.ecu_filename}"
    result_path = settings.UPLOAD_DIR / str(project_id) / result_filename

    with open(result_path, "wb") as f:
        f.write(modified_content)

    version = save_version(str(result_path), project_id, 2, "Modifié")
    fv = FileVersion(
        project_id=project_id,
        version_number=2,
        file_path=version["file_path"],
        file_hash=version["file_hash"],
        label="Modifié",
    )
    db.add(fv)

    project.result_file_path = str(result_path)
    project.result_checksum = result_hash
    project.status = ProjectStatus.COMPLETED
    db.commit()

    log = AuditLog(
        user_id=current_user.id, action="PROCESS_COMPLETE", resource_type="project",
        resource_id=project.id, details=f"Mods: {project.modifications}"
    )
    db.add(log)
    db.commit()

    return {
        "message": "Traitement terminé avec succès",
        "checksum": result_hash,
        "status": "completed",
    }


@router.get("/{project_id}/download")
def download_result(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status != ProjectStatus.COMPLETED or not project.result_file_path:
        raise HTTPException(status_code=400, detail="Aucun fichier résultat disponible")

    import os
    if not os.path.exists(project.result_file_path):
        raise HTTPException(status_code=404, detail="Fichier résultat introuvable")

    from fastapi.responses import FileResponse
    return FileResponse(
        project.result_file_path,
        filename=f"ECU_Modified_{project.ecu_filename}",
        media_type="application/octet-stream",
    )


@router.get("/{project_id}/versions")
def list_versions(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    versions = db.query(FileVersion).filter(FileVersion.project_id == project_id).order_by(FileVersion.version_number).all()
    return [{"id": v.id, "version": v.version_number, "label": v.label, "hash": v.file_hash, "created_at": v.created_at} for v in versions]
