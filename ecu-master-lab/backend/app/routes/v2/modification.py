"""
Modification routes — API endpoints for reading, editing, and patching ECU maps.

Provides the bridge between the frontend modification UI and the
ecu_engine value reader/writer/checksum_recalc modules.

Part of P0 Phase: File Editing Foundations.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.ecu_engine.map_value_reader import read_map, read_curve, read_single_value
from app.ecu_engine.map_value_writer import write_map, write_curve, write_single_value
from app.ecu_engine.checksum_recalc import recalculate_checksums, get_checksum_info
from app.ecu_engine.unit_converter import (
    raw_to_physical, physical_to_raw, get_conversion, get_all_conversions,
)

log = logging.getLogger("routes.modification")

router = APIRouter(prefix="/api/v3/modification", tags=["modification"])


# ── Request/Response models ─────────────────────────────────────

class ReadMapRequest(BaseModel):
    file_path: str
    offset: int
    rows: int
    cols: int
    data_type: str = "uint16"
    byte_order: str = "little_endian"
    name: str = ""

class ReadMapResponse(BaseModel):
    success: bool
    name: str = ""
    rows: int = 0
    cols: int = 0
    values: List[List[float]] = []
    data_type: str = "uint16"
    min_value: float = 0.0
    max_value: float = 0.0
    avg_value: float = 0.0
    offset: int = 0
    size_bytes: int = 0
    warnings: List[str] = []

class WriteMapRequest(BaseModel):
    file_path: str
    offset: int
    values: List[List[float]]
    data_type: str = "uint16"
    byte_order: str = "little_endian"
    output_path: Optional[str] = None

class WriteMapResponse(BaseModel):
    success: bool
    operations_count: int = 0
    values_changed: int = 0
    output_path: str = ""
    checksum_info: Optional[Dict] = None
    warnings: List[str] = []
    description: str = ""

class ConvertRequest(BaseModel):
    raw_value: float
    conversion_name: str = "IDENTITY"
    factor: float = 1.0
    offset: float = 0.0

class ConvertResponse(BaseModel):
    raw_value: float
    physical_value: float
    unit: str = ""
    conversion_name: str = ""

class ChecksumRequest(BaseModel):
    file_path: str
    ecu_model: str = ""

class ChecksumResponse(BaseModel):
    total: int = 0
    valid: int = 0
    invalid: int = 0
    unknown: int = 0
    details: List[Dict] = []


# ── Helper ──────────────────────────────────────────────────────

def _resolve_path(file_path: str) -> str:
    """Resolve file path to absolute."""
    p = os.path.abspath(file_path)
    if not os.path.isfile(p):
        raise HTTPException(status_code=404, detail="File not found: " + file_path)
    return p


# ── Routes ──────────────────────────────────────────────────────

@router.post("/read-map", response_model=ReadMapResponse)
async def api_read_map(req: ReadMapRequest):
    """Read a 2D calibration map from a binary file."""
    path = _resolve_path(req.file_path)
    with open(path, "rb") as f:
        data = f.read()
    result = read_map(data, req.offset, req.rows, req.cols, req.data_type, req.byte_order, name=req.name)
    if result is None:
        return ReadMapResponse(success=False, warnings=["Failed to read map at 0x%X" % req.offset])
    return ReadMapResponse(
        success=True,
        name=result.name,
        rows=result.rows,
        cols=result.cols,
        values=result.values,
        data_type=result.data_type,
        min_value=result.min_value,
        max_value=result.max_value,
        avg_value=result.avg_value,
        offset=result.offset,
        size_bytes=result.size_bytes,
        warnings=result.warnings,
    )


@router.post("/write-map", response_model=WriteMapResponse)
async def api_write_map(req: WriteMapRequest):
    """Write modified map values to a new file with checksum recalculation."""
    path = _resolve_path(req.file_path)
    with open(path, "rb") as f:
        data = f.read()

    wr = write_map(data, req.offset, req.values, req.data_type, req.byte_order)
    if not wr.success:
        return WriteMapResponse(success=False, warnings=wr.warnings)

    ecu_model = ""
    for part in os.path.basename(path).upper().split():
        if any(kw in part for kw in ("EDC", "MED", "ME7", "SID", "DCM")):
            ecu_model = part
            break

    patched_data, cs_result = recalculate_checksums(wr.modified_data or bytes(data), ecu_model)

    output_path = req.output_path
    if not output_path:
        base, ext = os.path.splitext(path)
        output_path = base + "_modified" + ext

    with open(output_path, "wb") as f:
        f.write(patched_data)

    return WriteMapResponse(
        success=True,
        operations_count=len(wr.operations),
        values_changed=len(wr.operations),
        output_path=output_path,
        checksum_info={
            "recalculated": cs_result.checksums_recalculated,
            "valid_before": cs_result.checksums_valid_before,
            "valid_after": cs_result.checksums_valid_after,
        },
        warnings=wr.warnings,
        description=wr.description,
    )


@router.post("/read-value")
async def api_read_value(req: ReadMapRequest):
    """Read a single value from a binary file at a specific offset."""
    path = _resolve_path(req.file_path)
    with open(path, "rb") as f:
        data = f.read()
    result = read_single_value(data, req.offset, req.data_type, req.byte_order)
    if result is None:
        return {"success": False, "error": "Failed to read at 0x%X" % req.offset}
    return {
        "success": True,
        "value": result.physical,
        "offset": result.offset,
        "data_type": result.data_type,
    }


@router.post("/convert", response_model=ConvertResponse)
async def api_convert(req: ConvertRequest):
    """Convert between raw ECU values and physical values."""
    conv = get_conversion(req.conversion_name)
    unit = conv.unit if conv else ""
    phys = raw_to_physical(req.raw_value, req.conversion_name, req.factor, req.offset)
    return ConvertResponse(
        raw_value=req.raw_value,
        physical_value=round(phys, 6),
        unit=unit,
        conversion_name=req.conversion_name,
    )


@router.post("/checksum", response_model=ChecksumResponse)
async def api_checksum(req: ChecksumRequest):
    """Validate all checksums for a file."""
    path = _resolve_path(req.file_path)
    with open(path, "rb") as f:
        data = f.read()
    info = get_checksum_info(data, req.ecu_model)
    return ChecksumResponse(**info)


@router.get("/conversions")
async def api_list_conversions():
    """List all available unit conversions."""
    return {"conversions": get_all_conversions()}
