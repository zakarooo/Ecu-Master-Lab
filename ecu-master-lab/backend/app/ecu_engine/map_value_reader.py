"""
Map value reader — reads calibrated values from binary ECU files.

Supports reading individual values, 1D curves, and 2D maps from any
offset with any data type (uint8/16/32, int8/16/32, float32).

Stdlib Python 3.8 only.
"""

import logging
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .models import MapDataType

log = logging.getLogger("ecu_engine.map_reader")


@dataclass
class ReadValue:
    raw: int = 0
    physical: float = 0.0
    offset: int = 0
    data_type: str = "uint16"
    byte_order: str = "little_endian"
    bytes_read: int = 0


@dataclass
class ReadAxis:
    name: str = ""
    unit: str = ""
    values: List[float] = field(default_factory=list)
    offsets: List[int] = field(default_factory=list)
    data_type: str = "uint16"
    byte_order: str = "little_endian"


@dataclass
class ReadMapResult:
    name: str = ""
    rows: int = 0
    cols: int = 0
    data_type: str = "uint16"
    byte_order: str = "little_endian"
    offset: int = 0
    size_bytes: int = 0
    values: List[List[float]] = field(default_factory=list)
    flat_values: List[float] = field(default_factory=list)
    x_axis: Optional[ReadAxis] = None
    y_axis: Optional[ReadAxis] = None
    min_value: float = 0.0
    max_value: float = 0.0
    avg_value: float = 0.0
    warnings: List[str] = field(default_factory=list)


# ── Data type parsing ──────────────────────────────────────────

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


def _read_value_at(
    data: bytes, offset: int, data_type: str, byte_order: str
) -> Optional[float]:
    """Read a single value from binary data."""
    if data_type not in _DT_SIZES:
        return None
    sz = _DT_SIZES[data_type]
    if offset + sz > len(data):
        return None
    if byte_order == "big_endian":
        fmt = _DT_STRUCT_BE.get(data_type, ">H")
    else:
        fmt = _DT_STRUCT_LE.get(data_type, "<H")
    return struct.unpack_from(fmt, data, offset)[0]


def _write_value_at(
    buf: bytearray, offset: int, value: float, data_type: str, byte_order: str
) -> bool:
    """Write a single value into a bytearray."""
    if data_type not in _DT_SIZES:
        return False
    sz = _DT_SIZES[data_type]
    if offset + sz > len(buf):
        return False
    if byte_order == "big_endian":
        fmt = _DT_STRUCT_BE.get(data_type, ">H")
    else:
        fmt = _DT_STRUCT_LE.get(data_type, "<H")
    if data_type in ("uint8", "int8"):
        struct.pack_into(fmt, buf, offset, int(value))
    elif "float" in data_type:
        struct.pack_into(fmt, buf, offset, float(value))
    else:
        struct.pack_into(fmt, buf, offset, int(value))
    return True


def _data_type_str(dt) -> str:
    return dt.value if isinstance(dt, MapDataType) else str(dt)


# ── Public API ──────────────────────────────────────────────────

def read_single_value(
    data: bytes,
    offset: int,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
) -> Optional[ReadValue]:
    """Read a single calibrated value from a binary file."""
    val = _read_value_at(data, offset, data_type, byte_order)
    if val is None:
        return None
    sz = _DT_SIZES.get(data_type, 2)
    return ReadValue(
        raw=int(val) if "float" not in data_type else 0,
        physical=float(val),
        offset=offset,
        data_type=data_type,
        byte_order=byte_order,
        bytes_read=sz,
    )


def read_curve(
    data: bytes,
    offset: int,
    num_points: int,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
) -> Optional[ReadAxis]:
    """Read a 1D curve (axis) from binary data."""
    if data_type not in _DT_SIZES:
        return None
    sz = _DT_SIZES[data_type]
    total = num_points * sz
    if offset + total > len(data):
        return None
    values = []
    offsets = []
    for i in range(num_points):
        v = _read_value_at(data, offset + i * sz, data_type, byte_order)
        values.append(float(v) if v is not None else 0.0)
        offsets.append(offset + i * sz)
    return ReadAxis(
        name="",
        values=values,
        offsets=offsets,
        data_type=data_type,
        byte_order=byte_order,
    )


def read_map(
    data: bytes,
    offset: int,
    rows: int,
    cols: int,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    x_axis_offset: int = -1,
    x_axis_points: int = 0,
    y_axis_offset: int = -1,
    y_axis_points: int = 0,
    name: str = "",
    row_major: bool = True,
) -> Optional[ReadMapResult]:
    """Read a 2D calibration map from binary data.

    Args:
        data: Binary file content
        offset: Start offset of map data
        rows: Number of rows (Y axis dimension)
        cols: Number of columns (X axis dimension)
        data_type: Data type string (uint8, uint16, int16, float32, etc.)
        byte_order: 'little_endian' or 'big_endian'
        x_axis_offset: Offset of X axis data (-1 = none)
        x_axis_points: Number of X axis points
        y_axis_offset: Offset of Y axis data (-1 = none)
        y_axis_points: Number of Y axis points
        name: Map name for identification
        row_major: True if data is stored row-by-row (default), False for col-by-col

    Returns:
        ReadMapResult with full map data, or None on error
    """
    if data_type not in _DT_SIZES:
        return None
    sz = _DT_SIZES[data_type]
    map_bytes = rows * cols * sz
    if offset + map_bytes > len(data):
        return None

    flat_values = []
    values_2d = []
    for r in range(rows):
        row_vals = []
        for c in range(cols):
            if row_major:
                v_off = offset + (r * cols + c) * sz
            else:
                v_off = offset + (c * rows + r) * sz
            v = _read_value_at(data, v_off, data_type, byte_order)
            val = float(v) if v is not None else 0.0
            row_vals.append(val)
            flat_values.append(val)
        values_2d.append(row_vals)

    x_axis = None
    if x_axis_offset >= 0 and x_axis_points > 0:
        x_axis = read_curve(data, x_axis_offset, x_axis_points, data_type, byte_order)

    y_axis = None
    if y_axis_offset >= 0 and y_axis_points > 0:
        y_axis = read_curve(data, y_axis_offset, y_axis_points, data_type, byte_order)

    vmin = min(flat_values) if flat_values else 0.0
    vmax = max(flat_values) if flat_values else 0.0
    avg = sum(flat_values) / len(flat_values) if flat_values else 0.0

    return ReadMapResult(
        name=name,
        rows=rows,
        cols=cols,
        data_type=data_type,
        byte_order=byte_order,
        offset=offset,
        size_bytes=map_bytes,
        values=values_2d,
        flat_values=flat_values,
        x_axis=x_axis,
        y_axis=y_axis,
        min_value=vmin,
        max_value=vmax,
        avg_value=avg,
    )


def read_map_from_detected(
    data: bytes,
    offset: int,
    size: int,
    rows: int,
    cols: int,
    data_type: MapDataType,
    name: str = "",
) -> Optional[ReadMapResult]:
    """Read a map using a DetectedMap's parameters (uses MapDataType enum)."""
    dt_str = data_type.value if isinstance(data_type, MapDataType) else str(data_type)
    return read_map(data, offset, rows, cols, dt_str, name=name)


def scan_map_value(
    data: bytes,
    offset: int,
    data_type: str = "uint16",
    byte_order: str = "little_endian",
    context_bytes: int = 16,
) -> Optional[Dict]:
    """Read a value with surrounding context for display/debugging."""
    val = read_single_value(data, offset, data_type, byte_order)
    if val is None:
        return None
    start = max(0, offset - context_bytes)
    end = min(len(data), offset + context_bytes)
    return {
        "value": val.physical,
        "offset": offset,
        "data_type": data_type,
        "hex_before": data[start:offset].hex(),
        "hex_after": data[offset + val.bytes_read:end].hex(),
        "context_start": start,
        "context_end": end,
    }
