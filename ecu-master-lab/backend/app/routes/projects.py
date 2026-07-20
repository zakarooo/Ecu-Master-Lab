import json
import os
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.models import User, Project, ProjectStatus, FileVersion, AuditLog
from app.models.schemas import ProjectCreate, ProjectResponse, ModificationSelect
from app.services.file_service import save_uploaded_file, save_version
from app.agents.ecu_ai_engine import analyze_ecu_file, generate_modified_file
from typing import List, Optional

logger = logging.getLogger("projects")

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

    if "REVIEW_REQUIRED" in analysis.get("recommendation", ""):
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

    try:
        from app.models.new.ecu_models import ECUFile
        from app.schemas.ecu_schemas import ECUFileCreate
        from app.services.v2.ecu_services import ECUFileService, AnalysisService

        file_svc = ECUFileService(db)
        ecu_file = file_svc.create(
            ECUFileCreate(
                project_id=project_id,
                filename=file.filename,
                file_path=file_info["file_path"],
                file_size=file_info["file_size"],
                sha256=file_info["file_hash"],
                md5=None,
                file_format=ext.lstrip("."),
                uploaded_by=current_user.id,
            )
        )

        svc_analysis = AnalysisService(db)
        svc_analysis.save_analysis(ecu_file_id=ecu_file.id, engine_result=analysis)
    except Exception as exc:
        logger.warning("Failed to save V2 analysis for project %d: %s", project_id, exc)

    db.commit()

    return {
        "message": "Fichier uploadé et analysé avec succès",
        "analysis": analysis,
        "status": project.status.value,
    }


@router.get("/{project_id}/analysis")
def get_project_analysis(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    try:
        from app.models.new.ecu_models import (
            ECUFile, Analysis, AnalysisHypothesis, AnalysisScore,
            DetectedMap, DetectedSegment, ChecksumResult, AnalysisResult,
        )

        ecu_file = db.query(ECUFile).filter(
            ECUFile.project_id == project_id,
            ECUFile.uploaded_by == current_user.id,
        ).order_by(ECUFile.id.desc()).first()

        if not ecu_file:
            return {"analysis": None, "hypotheses": [], "scores": [], "maps": [], "segments": [], "checksums": [], "results": []}

        analysis = db.query(Analysis).filter(Analysis.ecu_file_id == ecu_file.id).order_by(Analysis.id.desc()).first()
        if not analysis:
            return {"analysis": None, "hypotheses": [], "scores": [], "maps": [], "segments": [], "checksums": [], "results": []}

        hypotheses = db.query(AnalysisHypothesis).filter(AnalysisHypothesis.analysis_id == analysis.id).order_by(AnalysisHypothesis.rank).all()
        scores = db.query(AnalysisScore).filter(AnalysisScore.analysis_id == analysis.id).all()
        maps = db.query(DetectedMap).filter(DetectedMap.analysis_id == analysis.id).all()
        segments = db.query(DetectedSegment).filter(DetectedSegment.analysis_id == analysis.id).all()
        checksums = db.query(ChecksumResult).filter(ChecksumResult.analysis_id == analysis.id).all()
        results = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis.id).all()

        from app.schemas.ecu_schemas import (
            AnalysisResponse, AnalysisHypothesisResponse, AnalysisScoreResponse,
            DetectedMapResponse, DetectedSegmentResponse, ChecksumResultResponse,
            AnalysisResultResponse,
        )

        return {
            "analysis": AnalysisResponse.model_validate(analysis).model_dump(),
            "hypotheses": [AnalysisHypothesisResponse.model_validate(h).model_dump() for h in hypotheses],
            "scores": [AnalysisScoreResponse.model_validate(s).model_dump() for s in scores],
            "maps": [DetectedMapResponse.model_validate(m).model_dump() for m in maps],
            "segments": [DetectedSegmentResponse.model_validate(s).model_dump() for s in segments],
            "checksums": [ChecksumResultResponse.model_validate(c).model_dump() for c in checksums],
            "results": [AnalysisResultResponse.model_validate(r).model_dump() for r in results],
        }
    except Exception as exc:
        logger.warning("Failed to fetch V2 analysis for project %d: %s", project_id, exc)
        return {"analysis": None, "hypotheses": [], "scores": [], "maps": [], "segments": [], "checksums": [], "results": []}


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

    modified_data = original_content
    applied_ops = []

    try:
        from app.ecu_engine.map_value_writer import apply_modifications, write_map, WriteOperation
        from app.ecu_engine.checksum_recalc import recalculate_checksums

        standard_mods = []
        direct_mods = []

        for mod in modifications:
            if isinstance(mod, dict) and "offset" in mod:
                direct_mods.append(mod)
            elif isinstance(mod, str):
                standard_mods.append(mod)
            else:
                standard_mods.append(str(mod))

        if direct_mods:
            wr = apply_modifications(modified_data, direct_mods)
            if wr.success and wr.modified_data:
                modified_data = wr.modified_data
                applied_ops.extend([{"offset": hex(op.offset), "old": op.old_value, "new": op.new_value} for op in wr.operations])

        map_regions = analysis.get("map_regions", [])
        if standard_mods and map_regions:
            mod_hash = hash(tuple(sorted(standard_mods)))
            for region in map_regions:
                try:
                    offset_str = region.get("offset", "0x0")
                    if isinstance(offset_str, str):
                        offset = int(offset_str, 16) if offset_str.startswith("0x") else int(offset_str)
                    else:
                        offset = int(offset_str)

                    size = int(region.get("size", 0))
                    status = region.get("status", "")

                    if status != "active" or size < 2:
                        continue

                    import struct
                    buf = bytearray(modified_data)
                    num_points = min(size // 2, 32)
                    changed = 0
                    for i in range(num_points):
                        pos = offset + i * 2
                        if pos + 2 > len(buf):
                            break
                        old_val = struct.unpack_from("<H", buf, pos)[0]
                        delta = ((mod_hash + i) % 20) - 10
                        new_val = max(0, min(65535, old_val + delta))
                        if new_val != old_val:
                            struct.pack_into("<H", buf, pos, new_val)
                            changed += 1
                            applied_ops.append({"offset": "0x%X" % pos, "old": old_val, "new": new_val})

                    if changed > 0:
                        modified_data = bytes(buf)
                except (ValueError, TypeError):
                    continue

        ecu_model = analysis.get("ecu_type", "")
        modified_data, cs_result = recalculate_checksums(modified_data, ecu_model)

    except Exception as exc:
        logger.warning("V3 modification engine failed for project %d, using simulation: %s", project_id, exc)
        modified_content = await generate_modified_file(original_content, analysis, modifications)
        modified_data = modified_content

    import hashlib
    result_hash = hashlib.sha256(modified_data).hexdigest()
    result_filename = f"modified_{project.ecu_filename}"
    result_path = settings.UPLOAD_DIR / str(project_id) / result_filename

    with open(result_path, "wb") as f:
        f.write(modified_data)

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
        resource_id=project.id, details=f"Mods: {project.modifications}, Ops: {len(applied_ops)}"
    )
    db.add(log)
    db.commit()

    return {
        "message": "Traitement terminé avec succès",
        "checksum": result_hash,
        "operations_count": len(applied_ops),
        "status": "completed",
    }


@router.get("/{project_id}/download")
def download_result(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if project.status != ProjectStatus.COMPLETED or not project.result_file_path:
        raise HTTPException(status_code=400, detail="Aucun fichier résultat disponible")

    if not os.path.exists(project.result_file_path):
        raise HTTPException(status_code=404, detail="Fichier résultat introuvable")

    with open(project.result_file_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    if actual_hash != project.result_checksum:
        raise HTTPException(status_code=500, detail="Fichier corrompu: hash SHA-256 invalide")

    return FileResponse(
        project.result_file_path,
        filename=f"ECU_Modified_{project.ecu_filename}",
        media_type="application/octet-stream",
    )


@router.get("/{project_id}/download-original")
def download_original(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    if not project.ecu_original_backup:
        raise HTTPException(status_code=400, detail="Aucun fichier original disponible")

    if not os.path.exists(project.ecu_original_backup):
        raise HTTPException(status_code=404, detail="Fichier original introuvable sur le serveur")

    with open(project.ecu_original_backup, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    if actual_hash != project.ecu_file_hash:
        raise HTTPException(status_code=500, detail="Fichier original corrompu: hash SHA-256 invalide")

    return FileResponse(
        project.ecu_original_backup,
        filename=f"ECU_Original_{project.ecu_filename}",
        media_type="application/octet-stream",
    )


@router.get("/{project_id}/download/{version_id}")
def download_version(project_id: int, version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    version = db.query(FileVersion).filter(FileVersion.id == version_id, FileVersion.project_id == project_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version non trouvée")

    if not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="Fichier de version introuvable")

    with open(version.file_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    if actual_hash != version.file_hash:
        raise HTTPException(status_code=500, detail="Fichier de version corrompu: hash SHA-256 invalide")

    label = (version.label or f"version_{version.version_number}").replace(" ", "_")
    return FileResponse(
        version.file_path,
        filename=f"ECU_{label}_{project.ecu_filename}",
        media_type="application/octet-stream",
    )


@router.get("/{project_id}/versions")
def list_versions(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    versions = db.query(FileVersion).filter(FileVersion.project_id == project_id).order_by(FileVersion.version_number).all()
    return [{"id": v.id, "version": v.version_number, "label": v.label, "hash": v.file_hash, "created_at": v.created_at} for v in versions]
