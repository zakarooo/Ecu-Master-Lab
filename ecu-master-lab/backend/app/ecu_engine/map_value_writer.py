"""
Map value writer — writes calibrated values into binary ECU files.

Provides atomic read-modify-write for individual values, 1D curves,
and 2D maps. All writes produce a modified copy (immutable original).

Stdlib Python 3.8 only.
"""

import copy
import logging
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .models import MapDataType

log = logging.getLogger("ecu_engine.map_writer")


@dataclass
class WriteOperation:
    offset: int = 0
    old_value: float = 0.0
    new_value: float = 0.0
    data_type: str = "uint16"
    description: str = ""


@dataclass
class WriteResult:
    success: bool = False
    original_size: int = 0
    modified_size: int = 0
    modified_data: Optional[bytes] = None
    operations: List[WriteOperation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    description: str = ""


_DT_SIZES = {
    "uint8": 1, "int8": 1,
    "uint16": 2, "int16": 2,
    "uint32": 4, "int32": 4,
    "float32": 4,
}

_DT_STRUCT_LE = {
    "uint8": "B", "int8": "b",
    "uint16": "<H", "int16": "<h",
    "uint32": "<I", "int32": "<i",
    "float32": "<f",
}

_DT_STRUCT_BE = {
    "uint8": "B", "int8": "b",
    "uint16": ">H", "int16": ">h",
    "uint32": ">I", "int32": ">i",
    "float32": ">f",
}


def _clamp(value: float, data_type: str) -> float:
    """Clamp value to data type range."""
    ranges = {
        "uint8": (0, 255),
        "int8": (-128, 127),
        "uint16": (0, 65535),
        "int16": (-32768, 32767),
        "uint32": (0, 4294967295),
        "int32": (-2147483648, 2147483647),
    }
    if data_type not in ranges:
        return value
    lo, hi = ranges[data_type]
    return max(lo, min(hi, value))


def _get_fmt(data_type: str, byte_order: str) -> str:
    if byte_order == "big_endian":
        return _DT_STRUCT_BE.get(data_type, ">H")
    return _DT_STRUCT_LE.get(data_type, "<H")


# ── Public API ──────────────────────────────────────────────────

def write_single_value(
    data: bytes,
    offset: int,
    value: float,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    clamp: bool = True,
) -> WriteResult:
    """Write a single value to a specific offset.

    Returns a new bytes object with the value written.
    Original data is never modified.
    """
    if data_type not in _DT_SIZES:
        return WriteResult(success=False, warnings=["Unknown data type: " + data_type])
    sz = _DT_SIZES[data_type]
    if offset + sz > len(data):
        return WriteResult(success=False, warnings=["Offset out of bounds: 0x%X" % offset])

    if clamp:
        value = _clamp(value, data_type)

    buf = bytearray(data)
    old_val = struct.unpack_from(_get_fmt(data_type, byte_order), buf, offset)[0]
    struct.pack_into(_get_fmt(data_type, byte_order), buf, offset, int(value) if "float" not in data_type else float(value))

    ops = [WriteOperation(
        offset=offset,
        old_value=float(old_val),
        new_value=value,
        data_type=data_type,
        description="Single value at 0x%X" % offset,
    )]

    return WriteResult(
        success=True,
        original_size=len(data),
        modified_size=len(buf),
        modified_data=bytes(buf),
        operations=ops,
        description="Wrote %s value %s at 0x%X" % (data_type, str(value), offset),
    )


def write_curve(
    data: bytes,
    offset: int,
    values: List[float],
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    clamp: bool = True,
) -> WriteResult:
    """Write a 1D curve (axis) to binary data."""
    if data_type not in _DT_SIZES:
        return WriteResult(success=False, warnings=["Unknown data type: " + data_type])
    sz = _DT_SIZES[data_type]
    total = len(values) * sz
    if offset + total > len(data):
        return WriteResult(success=False, warnings=["Not enough space: need %d bytes at 0x%X" % (total, offset)])

    buf = bytearray(data)
    ops = []
    for i, v in enumerate(values):
        v_off = offset + i * sz
        if clamp:
            v = _clamp(v, data_type)
        old_val = struct.unpack_from(_get_fmt(data_type, byte_order), buf, v_off)[0]
        struct.pack_into(_get_fmt(data_type, byte_order), buf, v_off, int(v) if "float" not in data_type else float(v))
        if old_val != v:
            ops.append(WriteOperation(
                offset=v_off, old_value=float(old_val), new_value=v,
                data_type=data_type,
                description="Curve[%d]" % i,
            ))

    return WriteResult(
        success=True,
        original_size=len(data),
        modified_size=len(buf),
        modified_data=bytes(buf),
        operations=ops,
        description="Wrote %d curve values at 0x%X (%d changed)" % (len(values), offset, len(ops)),
    )


def write_map(
    data: bytes,
    offset: int,
    values: List[List[float]],
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    clamp: bool = True,
    row_major: bool = True,
) -> WriteResult:
    """Write a 2D calibration map to binary data.

    Args:
        data: Original binary data
        offset: Start offset for map data
        values: 2D list of values [rows][cols]
        data_type: Data type string
        byte_order: 'little_endian' or 'big_endian'
        clamp: Whether to clamp values to data type range
        row_major: True if written row-by-row (default)

    Returns:
        WriteResult with all operations performed
    """
    if data_type not in _DT_SIZES:
        return WriteResult(success=False, warnings=["Unknown data type: " + data_type])
    sz = _DT_SIZES[data_type]
    rows = len(values)
    if rows == 0:
        return WriteResult(success=False, warnings=["Empty values"])
    cols = len(values[0])
    total = rows * cols * sz
    if offset + total > len(data):
        return WriteResult(success=False, warnings=["Not enough space: need %d bytes at 0x%X" % (total, offset)])

    buf = bytearray(data)
    ops = []
    for r in range(rows):
        for c in range(cols):
            v = values[r][c]
            if clamp:
                v = _clamp(v, data_type)
            if row_major:
                v_off = offset + (r * cols + c) * sz
            else:
                v_off = offset + (c * rows + r) * sz
            if v_off + sz > len(buf):
                continue
            old_val = struct.unpack_from(_get_fmt(data_type, byte_order), buf, v_off)[0]
            struct.pack_into(_get_fmt(data_type, byte_order), buf, v_off, int(v) if "float" not in data_type else float(v))
            if old_val != v:
                ops.append(WriteOperation(
                    offset=v_off, old_value=float(old_val), new_value=v,
                    data_type=data_type,
                    description="Map[%d][%d]" % (r, c),
                ))

    return WriteResult(
        success=True,
        original_size=len(data),
        modified_size=len(buf),
        modified_data=bytes(buf),
        operations=ops,
        description="Wrote %dx%d map at 0x%X (%d values changed)" % (rows, cols, offset, len(ops)),
    )


def write_map_values_flat(
    data: bytes,
    offset: int,
    flat_values: List[float],
    rows: int,
    cols: int,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    clamp: bool = True,
    row_major: bool = True,
) -> WriteResult:
    """Write a map from flat (1D) values."""
    if len(flat_values) != rows * cols:
        return WriteResult(success=False, warnings=[
            "Expected %d values, got %d" % (rows * cols, len(flat_values))
        ])
    grid = []
    for r in range(rows):
        grid.append(flat_values[r * cols:(r + 1) * cols])
    return write_map(data, offset, grid, data_type, byte_order, clamp, row_major)


def apply_modifications(
    data: bytes,
    modifications: List[Dict],
) -> WriteResult:
    """Apply multiple modifications in one pass.

    Each modification dict should have:
        - offset: int
        - value: float (or values: List[float] for curves)
        - data_type: str (optional, default 'uint16')
        - byte_order: str (optional, default 'little_endian')
    """
    buf = bytearray(data)
    ops = []
    warnings = []
    for mod in modifications:
        offset = mod.get("offset", 0)
        data_type = mod.get("data_type", "uint16")
        byte_order = mod.get("byte_order", "little_endian")
        if data_type not in _DT_SIZES:
            warnings.append("Unknown data type at 0x%X" % offset)
            continue
        sz = _DT_SIZES[data_type]
        if offset + sz > len(buf):
            warnings.append("Offset 0x%X out of bounds" % offset)
            continue
        value = mod.get("value", 0.0)
        value = _clamp(value, data_type)
        old_val = struct.unpack_from(_get_fmt(data_type, byte_order), buf, offset)[0]
        struct.pack_into(_get_fmt(data_type, byte_order), buf, offset, int(value) if "float" not in data_type else float(value))
        if old_val != value:
            ops.append(WriteOperation(
                offset=offset, old_value=float(old_val), new_value=value,
                data_type=data_type,
                description="Bulk modification",
            ))

    return WriteResult(
        success=True,
        original_size=len(data),
        modified_size=len(buf),
        modified_data=bytes(buf),
        operations=ops,
        warnings=warnings,
        description="Applied %d modifications (%d changed)" % (len(modifications), len(ops)),
    )
