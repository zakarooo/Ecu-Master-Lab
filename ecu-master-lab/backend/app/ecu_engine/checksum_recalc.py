"""
Checksum recalculation engine — recalculates all checksums after map edits.

Uses the existing checksum_engine algorithms but adds write-back capability
to patch checksums in the modified binary.

Stdlib Python 3.8 only.
"""

import logging
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .checksum_engine import (
    KNOWN_CHECKSUM_CONFIGS,
    _ALGORITHMS,
    _read_stored,
    auto_detect_checksum,
    verify_checksum,
)
from .models import ChecksumResult

log = logging.getLogger("ecu_engine.checksum_recalc")


@dataclass
class RecalcResult:
    success: bool = False
    checksums_recalculated: int = 0
    checksums_valid_before: int = 0
    checksums_valid_after: int = 0
    operations: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    description: str = ""


def _read_fmt(size: int, byte_order: str = "big") -> str:
    """Get struct format for reading checksum storage."""
    if byte_order == "little":
        fmts = {1: "<B", 2: "<H", 4: "<I"}
    else:
        fmts = {1: ">B", 2: ">H", 4: ">I"}
    return fmts.get(size, ">I")


def recalculate_checksums(
    data: bytes,
    ecu_model: str = "",
    modified_regions: Optional[List[Tuple[int, int]]] = None,
) -> Tuple[bytes, RecalcResult]:
    """Recalculate and write-back all applicable checksums.

    Args:
        data: Modified binary data (after map edits)
        ecu_model: ECU model hint for algorithm selection
        modified_regions: List of (start, end) regions that were modified.
                          If None, recalculates all detected checksums.

    Returns:
        Tuple of (patched_data, RecalcResult)
    """
    result = RecalcResult()
    buf = bytearray(data)

    configs_to_try = []
    ecu_upper = ecu_model.upper()
    for cfg in KNOWN_CHECKSUM_CONFIGS:
        pattern = cfg["ecu_pattern"]
        if pattern and pattern.upper() not in ecu_upper:
            continue
        configs_to_try.append(cfg)

    if not configs_to_try:
        configs_to_try = [cfg for cfg in KNOWN_CHECKSUM_CONFIGS if not cfg["ecu_pattern"]]

    for cfg in configs_to_try:
        algorithm = cfg["algorithm"]
        cs_offset = cfg["offset"]
        cs_size = cfg["size"]
        data_start = 0
        data_end = cfg["offset"]

        if cs_offset + cs_size > len(buf):
            continue

        fn = _ALGORITHMS.get(algorithm)
        if fn is None:
            continue

        if data_end > len(buf):
            data_end = len(buf)
        if data_start >= data_end:
            continue

        old_stored = _read_stored(bytes(buf), cs_offset, cs_size)
        old_valid = None
        if old_stored is not None:
            computed = fn(buf[data_start:data_end])
            old_valid = (old_stored == computed)

        if old_valid:
            result.checksums_valid_before += 1

        new_computed = fn(buf[data_start:data_end])

        if old_stored is not None and old_stored == new_computed:
            result.checksums_valid_after += 1
            result.checksums_recalculated += 1
            continue

        fmt = _read_fmt(cs_size)
        struct.pack_into(fmt, buf, cs_offset, new_computed)

        result.checksums_recalculated += 1
        result.checksums_valid_after += 1
        result.operations.append({
            "algorithm": algorithm,
            "offset": cs_offset,
            "size": cs_size,
            "old_value": "0x%X" % old_stored if old_stored is not None else "N/A",
            "new_value": "0x%X" % new_computed,
            "was_valid": old_valid,
        })
        log.info(
            "Recalculated %s at 0x%X: %s -> %s",
            algorithm, cs_offset,
            "0x%X" % old_stored if old_stored is not None else "N/A",
            "0x%X" % new_computed,
        )

    result.success = result.checksums_recalculated > 0 or len(result.operations) == 0
    result.description = (
        "%d checksums recalculated, %d/%d valid after patch" % (
            result.checksums_recalculated,
            result.checksums_valid_after,
            result.checksums_recalculated,
        )
    )

    return bytes(buf), result


def validate_checksums(
    data: bytes,
    ecu_model: str = "",
) -> List[ChecksumResult]:
    """Validate all applicable checksums without modification.

    Returns list of ChecksumResult for display/reporting.
    """
    return auto_detect_checksum(data, ecu_model)


def get_checksum_info(
    data: bytes,
    ecu_model: str = "",
) -> Dict:
    """Get a summary of all checksum info for the frontend."""
    results = validate_checksums(data, ecu_model)
    valid_count = sum(1 for r in results if r.is_valid is True)
    invalid_count = sum(1 for r in results if r.is_valid is False)
    unknown_count = sum(1 for r in results if r.is_valid is None)
    return {
        "total": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "unknown": unknown_count,
        "details": [
            {
                "algorithm": r.algorithm,
                "offset": "0x%X" % r.offset if r.offset else "N/A",
                "stored": r.stored_value,
                "computed": r.computed_value,
                "is_valid": r.is_valid,
                "explanation": r.explanation,
            }
            for r in results
        ],
    }
