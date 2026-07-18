"""
Couche 8 — Moteur de verification des checksums ECU.

Algorithmes : CRC16, CRC32, Sum, XOR, variantes constructeurs.
Stdlib Python 3.8 uniquement.
"""

import logging
import struct
from typing import List, Tuple, Optional

from .models import ChecksumResult

logger = logging.getLogger("ecu_engine.checksum")

_READ_FMT = {1: ">B", 2: ">H", 4: ">I"}


# ==============================================================
#  FONCTIONS ALGORITHME
# ==============================================================

def _crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc


def _crc16_ibm(data: bytes) -> int:
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8005 if crc & 1 else crc >> 1
    return crc & 0xFFFF


def _crc32_standard(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if crc & 1 else crc >> 1
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _crc32_bosch(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xB71DC6 if crc & 1 else crc >> 1
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _crc32_continental(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _crc32_bosch_edc17(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x1EDC6F41 if crc & 1 else crc >> 1
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _crc32_bosch_md1(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x876E4B1B if crc & 1 else crc >> 1
    return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF


def _sum8(data: bytes) -> int:
    return sum(data) & 0xFF


def _sum16(data: bytes) -> int:
    total = 0
    for i in range(0, len(data) - 1, 2):
        total += (data[i] << 8) | data[i + 1]
    if len(data) % 2 == 1:
        total += data[-1] << 8
    return total & 0xFFFF


def _xor16(data: bytes) -> int:
    result = 0
    for i in range(0, len(data) - 1, 2):
        result ^= (data[i] << 8) | data[i + 1]
    if len(data) % 2 == 1:
        result ^= data[-1] << 8
    return result & 0xFFFF


def _delphi_checksum(data: bytes) -> int:
    s = _sum16(data)
    return s ^ 0xFFFF


_ALGORITHMS = {
    "crc16_ccitt": _crc16_ccitt,
    "crc16_ibm": _crc16_ibm,
    "crc32_standard": _crc32_standard,
    "crc32_bosch": _crc32_bosch,
    "crc32_continental": _crc32_continental,
    "crc32_bosch_edc17": _crc32_bosch_edc17,
    "crc32_bosch_md1": _crc32_bosch_md1,
    "sum8": _sum8,
    "sum16": _sum16,
    "xor16": _xor16,
    "delphi": _delphi_checksum,
}


# ==============================================================
#  CONFIGURATIONS CONNUES
# ==============================================================

KNOWN_CHECKSUM_CONFIGS = [
    {"ecu_pattern": "Bosch EDC16",     "algorithm": "crc16_ccitt",         "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "Bosch EDC17",     "algorithm": "crc32_bosch_edc17",   "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
    {"ecu_pattern": "Bosch MD1",       "algorithm": "crc32_bosch_md1",     "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
    {"ecu_pattern": "Bosch ME7",       "algorithm": "crc16_ccitt",         "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "Bosch",           "algorithm": "crc32_bosch",         "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
    {"ecu_pattern": "Continental",     "algorithm": "crc32_continental",   "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
    {"ecu_pattern": "Delphi",          "algorithm": "delphi",              "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "Siemens",         "algorithm": "crc32_standard",      "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
    {"ecu_pattern": "Denso",           "algorithm": "sum16",               "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "Magneti Marelli", "algorithm": "sum8",                "offset": 0x7FFF, "size": 1, "data_range_description": "0x0000..0x7FFE"},
    {"ecu_pattern": "Valeo",           "algorithm": "xor16",               "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "Hitachi",         "algorithm": "crc16_ibm",           "offset": 0x7FFE, "size": 2, "data_range_description": "0x0000..0x7FFD"},
    {"ecu_pattern": "",                "algorithm": "crc32_standard",      "offset": 0x7FFC, "size": 4, "data_range_description": "0x0000..0x7FFB"},
]


# ==============================================================
#  FONCTIONS PRINCIPALES
# ==============================================================

def _read_stored(data: bytes, offset: int, size: int) -> Optional[int]:
    if offset + size > len(data):
        return None
    fmt = _READ_FMT.get(size)
    if fmt is None:
        return int.from_bytes(data[offset: offset + size], byteorder="big")
    return struct.unpack(fmt, data[offset: offset + size])[0]


def _format_hex(value: int, size: int) -> str:
    return "0x" + format(value, "0" + str(size * 2) + "X").upper()


def verify_checksum(
    data: bytes,
    algorithm: str,
    offset: int,
    size: int,
    data_start: int,
    data_end: int,
) -> ChecksumResult:
    fn = _ALGORITHMS.get(algorithm)
    if fn is None:
        return ChecksumResult(
            algorithm=algorithm,
            explanation="Algorithme inconnu: " + algorithm,
        )
    if data_end > len(data):
        data_end = len(data)
    if data_start >= data_end:
        return ChecksumResult(
            algorithm=algorithm,
            explanation="Plage de donnees invalide",
        )
    stored = _read_stored(data, offset, size)
    if stored is None:
        return ChecksumResult(
            algorithm=algorithm, offset=offset, size=size,
            explanation="Impossible de lire le checksum a l'offset specifie",
        )
    computed = fn(data[data_start: data_end])
    valid = stored == computed
    result = ChecksumResult(
        algorithm=algorithm,
        stored_value=_format_hex(stored, size),
        computed_value=_format_hex(computed, size),
        is_valid=valid,
        data_range=(data_start, data_end),
        offset=offset,
        size=size,
        needs_recalculation=not valid,
    )
    if valid:
        result.explanation = (
            "Checksum " + algorithm + " valide ("
            + _format_hex(stored, size) + ")"
        )
    else:
        result.explanation = (
            "Checksum " + algorithm + " INVALIDE — stocke="
            + _format_hex(stored, size) + " attendu="
            + _format_hex(computed, size)
        )
    logger.debug(
        "verify %s offset=0x%X size=%d valid=%s",
        algorithm, offset, size, valid,
    )
    return result


def auto_detect_checksum(
    data: bytes,
    ecu_model: str = "",
) -> List[ChecksumResult]:
    results = []  # type: List[ChecksumResult]
    ecu_upper = ecu_model.upper()
    for cfg in KNOWN_CHECKSUM_CONFIGS:
        pattern = cfg["ecu_pattern"]
        if pattern and pattern.upper() not in ecu_upper:
            continue
        logger.info(
            "Essai config: %s / %s",
            pattern or "(defaut)", cfg["algorithm"],
        )
        vr = verify_checksum(
            data=data,
            algorithm=cfg["algorithm"],
            offset=cfg["offset"],
            size=cfg["size"],
            data_start=0,
            data_end=cfg["offset"],
        )
        results.append(vr)
    if not results:
        logger.warning(
            "Aucune configuration applicable pour '%s'", ecu_model
        )
    return results
