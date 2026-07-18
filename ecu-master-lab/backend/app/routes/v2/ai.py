from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import AIPrediction, AIModel, Heuristic, LearningDataset
from app.schemas.ecu_schemas import (
    AIModelCreate,
    AIModelResponse,
    AIPredictionCreate,
    AIPredictionResponse,
    LearningDatasetCreate,
    LearningDatasetResponse,
    HeuristicCreate,
    HeuristicResponse,
)
from app.services.v2.ecu_services import AIModelService, AIPredictionService, LearningDatasetService, HeuristicService
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/ai", tags=["V2 - AI"])


# ─── AI Models ──────────────────────────────────────────────────────────────

@router.get("/models", response_model=PaginatedResponse)
def list_ai_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AIModel)
    if search:
        q = q.filter(AIModel.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(AIModel.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/models/active", response_model=PaginatedResponse)
def list_active_ai_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AIModel).filter(AIModel.is_active.is_(True))
    items, total = paginate_query(q.order_by(AIModel.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/models/{model_id}", response_model=AIModelResponse)
def get_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    m = AIModelService(db).get_by_id(model_id)
    if not m:
        raise HTTPException(404, "AI model not found")
    return m


@router.post("/models", response_model=AIModelResponse, status_code=201)
def create_ai_model(
    data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return AIModelService(db).create(data)


@router.put("/models/{model_id}", response_model=AIModelResponse)
def update_ai_model(
    model_id: int,
    data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    m = AIModelService(db).update(model_id, data)
    if not m:
        raise HTTPException(404, "AI model not found")
    return m


# ─── AI Predictions ─────────────────────────────────────────────────────────

@router.get("/predictions/analysis/{analysis_id}", response_model=PaginatedResponse)
def list_predictions_by_analysis(
    analysis_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(AIPrediction).filter(AIPrediction.analysis_id == analysis_id)
    items, total = paginate_query(q.order_by(AIPrediction.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/predictions", response_model=AIPredictionResponse, status_code=201)
def create_prediction(
    data: AIPredictionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return AIPredictionService(db).create(data)


# ─── Learning Datasets ──────────────────────────────────────────────────────

@router.get("/datasets", response_model=PaginatedResponse)
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(LearningDataset)
    if search:
        q = q.filter(LearningDataset.label_manufacturer.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(LearningDataset.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/datasets/unvalidated", response_model=PaginatedResponse)
def list_unvalidated_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(LearningDataset).filter(LearningDataset.is_validated.is_(False))
    items, total = paginate_query(q.order_by(LearningDataset.id.desc()), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/datasets/{dataset_id}", response_model=LearningDatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    d = LearningDatasetService(db).get_by_id(dataset_id)
    if not d:
        raise HTTPException(404, "Learning dataset not found")
    return d


@router.post("/datasets", response_model=LearningDatasetResponse, status_code=201)
def create_dataset(
    data: LearningDatasetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return LearningDatasetService(db).create(data)


@router.put("/datasets/{dataset_id}", response_model=LearningDatasetResponse)
def validate_dataset(
    dataset_id: int,
    data: LearningDatasetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    d = LearningDatasetService(db).update(dataset_id, data)
    if not d:
        raise HTTPException(404, "Learning dataset not found")
    return d


# ─── Heuristics ─────────────────────────────────────────────────────────────

@router.get("/heuristics", response_model=PaginatedResponse)
def list_heuristics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Heuristic)
    if search:
        q = q.filter(Heuristic.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Heuristic.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/heuristics/active", response_model=PaginatedResponse)
def list_active_heuristics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Heuristic).filter(Heuristic.is_active.is_(True))
    items, total = paginate_query(q.order_by(Heuristic.priority.desc(), Heuristic.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/heuristics/{heuristic_id}", response_model=HeuristicResponse)
def get_heuristic(
    heuristic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    h = HeuristicService(db).get_by_id(heuristic_id)
    if not h:
        raise HTTPException(404, "Heuristic not found")
    return h


@router.post("/heuristics", response_model=HeuristicResponse, status_code=201)
def create_heuristic(
    data: HeuristicCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return HeuristicService(db).create(data)


@router.put("/heuristics/{heuristic_id}", response_model=HeuristicResponse)
def update_heuristic(
    heuristic_id: int,
    data: HeuristicCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    h = HeuristicService(db).update(heuristic_id, data)
    if not h:
        raise HTTPException(404, "Heuristic not found")
    return h


@router.post("/heuristics/{heuristic_id}/hit", response_model=HeuristicResponse)
def hit_heuristic(
    heuristic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    h = HeuristicService(db).increment_hit_count(heuristic_id)
    if not h:
        raise HTTPException(404, "Heuristic not found")
    return h
