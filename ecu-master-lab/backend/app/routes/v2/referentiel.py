from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.new.ecu_models import (
    ChecksumAlgorithm,
    ECUModel,
    ECUVariant,
    Manufacturer,
    Processor,
    Protocol,
)
from app.schemas.ecu_schemas import (
    ManufacturerCreate,
    ManufacturerResponse,
    ECUModelCreate,
    ECUModelResponse,
    ECUVariantCreate,
    ECUVariantResponse,
    ProcessorCreate,
    ProcessorResponse,
    ProtocolCreate,
    ProtocolResponse,
    ChecksumAlgorithmCreate,
    ChecksumAlgorithmResponse,
)
from app.services.v2.ecu_services import (
    ManufacturerService,
    ECUModelService,
    ECUVariantService,
    ProcessorService,
    ProtocolService,
    ChecksumAlgorithmService,
)
from .pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/v2/referentiel", tags=["V2 - Referentiel"])


# ─── Manufacturers ───────────────────────────────────────────────────────────

@router.get("/manufacturers", response_model=PaginatedResponse)
def list_manufacturers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Manufacturer)
    if search:
        q = q.filter(Manufacturer.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Manufacturer.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/manufacturers/{manufacturer_id}", response_model=ManufacturerResponse)
def get_manufacturer(
    manufacturer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    m = ManufacturerService(db).get_by_id(manufacturer_id)
    if not m:
        raise HTTPException(404, "Manufacturer not found")
    return m


@router.post("/manufacturers", response_model=ManufacturerResponse, status_code=201)
def create_manufacturer(
    data: ManufacturerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ManufacturerService(db).create(data)


@router.put("/manufacturers/{manufacturer_id}", response_model=ManufacturerResponse)
def update_manufacturer(
    manufacturer_id: int,
    data: ManufacturerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    m = ManufacturerService(db).update(manufacturer_id, data)
    if not m:
        raise HTTPException(404, "Manufacturer not found")
    return m


# ─── ECU Models ──────────────────────────────────────────────────────────────

@router.get("/ecu-models", response_model=PaginatedResponse)
def list_ecu_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUModel)
    if search:
        q = q.filter(ECUModel.model_name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ECUModel.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/ecu-models/{ecu_model_id}", response_model=ECUModelResponse)
def get_ecu_model(
    ecu_model_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    m = ECUModelService(db).get_by_id(ecu_model_id)
    if not m:
        raise HTTPException(404, "ECU model not found")
    return m


@router.get("/ecu-models/manufacturer/{manufacturer_id}", response_model=PaginatedResponse)
def list_ecu_models_by_manufacturer(
    manufacturer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUModel).filter(ECUModel.manufacturer_id == manufacturer_id)
    items, total = paginate_query(q.order_by(ECUModel.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/ecu-models", response_model=ECUModelResponse, status_code=201)
def create_ecu_model(
    data: ECUModelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ECUModelService(db).create(data)


@router.put("/ecu-models/{ecu_model_id}", response_model=ECUModelResponse)
def update_ecu_model(
    ecu_model_id: int,
    data: ECUModelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    m = ECUModelService(db).update(ecu_model_id, data)
    if not m:
        raise HTTPException(404, "ECU model not found")
    return m


# ─── ECU Variants ────────────────────────────────────────────────────────────

@router.get("/ecu-variants", response_model=PaginatedResponse)
def list_ecu_variants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUVariant)
    if search:
        q = q.filter(ECUVariant.variant_name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ECUVariant.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/ecu-variants/{ecu_variant_id}", response_model=ECUVariantResponse)
def get_ecu_variant(
    ecu_variant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    v = ECUVariantService(db).get_by_id(ecu_variant_id)
    if not v:
        raise HTTPException(404, "ECU variant not found")
    return v


@router.get("/ecu-variants/model/{ecu_model_id}", response_model=PaginatedResponse)
def list_ecu_variants_by_model(
    ecu_model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ECUVariant).filter(ECUVariant.ecu_model_id == ecu_model_id)
    items, total = paginate_query(q.order_by(ECUVariant.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/ecu-variants", response_model=ECUVariantResponse, status_code=201)
def create_ecu_variant(
    data: ECUVariantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ECUVariantService(db).create(data)


# ─── Processors ──────────────────────────────────────────────────────────────

@router.get("/processors", response_model=PaginatedResponse)
def list_processors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Processor)
    if search:
        q = q.filter(Processor.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Processor.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/processors/{processor_id}", response_model=ProcessorResponse)
def get_processor(
    processor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = ProcessorService(db).get_by_id(processor_id)
    if not p:
        raise HTTPException(404, "Processor not found")
    return p


@router.post("/processors", response_model=ProcessorResponse, status_code=201)
def create_processor(
    data: ProcessorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ProcessorService(db).create(data)


# ─── Protocols ───────────────────────────────────────────────────────────────

@router.get("/protocols", response_model=PaginatedResponse)
def list_protocols(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Protocol)
    if search:
        q = q.filter(Protocol.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(Protocol.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/protocols/{protocol_id}", response_model=ProtocolResponse)
def get_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = ProtocolService(db).get_by_id(protocol_id)
    if not p:
        raise HTTPException(404, "Protocol not found")
    return p


@router.post("/protocols", response_model=ProtocolResponse, status_code=201)
def create_protocol(
    data: ProtocolCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ProtocolService(db).create(data)


# ─── Checksum Algorithms ────────────────────────────────────────────────────

@router.get("/checksum-algorithms", response_model=PaginatedResponse)
def list_checksum_algorithms(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(ChecksumAlgorithm)
    if search:
        q = q.filter(ChecksumAlgorithm.name.ilike(f"%{search}%"))
    items, total = paginate_query(q.order_by(ChecksumAlgorithm.id), skip, limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/checksum-algorithms/{algo_id}", response_model=ChecksumAlgorithmResponse)
def get_checksum_algorithm(
    algo_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    a = ChecksumAlgorithmService(db).get_by_id(algo_id)
    if not a:
        raise HTTPException(404, "Checksum algorithm not found")
    return a


@router.post("/checksum-algorithms", response_model=ChecksumAlgorithmResponse, status_code=201)
def create_checksum_algorithm(
    data: ChecksumAlgorithmCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ChecksumAlgorithmService(db).create(data)
