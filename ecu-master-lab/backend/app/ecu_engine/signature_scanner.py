"""
Layer 5: Signature scanner for ECU binary analysis.

Scans binary data for known ECU signatures: interrupt vectors,
bootloaders, CRC tables, schedulers, CAN IDs, RSA/crypto markers,
and UDS diagnostic service IDs.
"""

import logging
from typing import Dict, List, Tuple, Any

from .models import SignatureScanResult, FoundSignature
from .utils import (
    find_binary_pattern,
    find_ascii_strings,
    read_uint32_be,
    read_uint16_be,
)

logger = logging.getLogger(__name__)


# ==============================================================
#  KNOWN SIGNATURES
# ==============================================================

KNOWN_SIGNATURES: List[Dict[str, Any]] = [
    # ----------------------------------------------------------
    #  Interrupt vector patterns
    # ----------------------------------------------------------
    {
        "category": "interrupt_vector",
        "name": "Tricore_BTV",
        "patterns": [b"\x00\x00\x0F\xFF"],
        "description": "Tricore BTV range 0x80000000-0x80000FFF",
        "severity": "high",
    },
    {
        "category": "interrupt_vector",
        "name": "MPC_VLE",
        "patterns": [b"\x00\x00\x04\x00"],
        "description": "MPC5xx vector table base 0x00000000-0x00000400",
        "severity": "high",
    },
    {
        "category": "interrupt_vector",
        "name": "SH_IVT",
        "patterns": [b"\x00\x00\x03\x00"],
        "description": "SH705x vector table base 0x00000000-0x00000300",
        "severity": "high",
    },
    # ----------------------------------------------------------
    #  Bootloader patterns
    # ----------------------------------------------------------
    {
        "category": "bootloader",
        "name": "Bosch_ME17",
        "patterns": [
            b"\x02\x01\x00\x00",
            b"\xFF\xFF\x00\x00",
            b"\x55\xAA\x55\xAA",
        ],
        "description": "Bosch ME(D)17 bootloader magic bytes",
        "severity": "high",
    },
    {
        "category": "bootloader",
        "name": "Bosch_EDC16",
        "patterns": [
            b"\x7F\x00\x00\x00",
            b"\x00\x7F\x00\x00",
        ],
        "description": "Bosch EDC16 bootloader pattern",
        "severity": "high",
    },
    {
        "category": "bootloader",
        "name": "Delphi_DCM",
        "patterns": [
            b"\xDE\x1C\x00\x00",
            b"\xDE\x1C\x01\x00",
            b"\xAA\x55\xAA\x55",
        ],
        "description": "Delphi DCM boot patterns",
        "severity": "high",
    },
    {
        "category": "bootloader",
        "name": "Bosch_ECU_Boot",
        "patterns": [
            b"\x10\x10\x10\x10",
            b"\x11\x22\x33\x44",
        ],
        "description": "Bosch ECU bootloader common markers",
        "severity": "medium",
    },
    # ----------------------------------------------------------
    #  CRC table signatures
    # ----------------------------------------------------------
    {
        "category": "crc_table",
        "name": "CRC32_04C11DB7",
        "patterns": [
            bytes([
                0x00, 0x00, 0x00, 0x00, 0x04, 0xC1, 0x1D, 0xB7,
            ]),
        ],
        "description": "CRC32 polynomial 0x04C11DB7 table start",
        "severity": "medium",
    },
    {
        "category": "crc_table",
        "name": "CRC32_EDB88320",
        "patterns": [
            bytes([
                0x00, 0x00, 0x00, 0x00, 0x77, 0x07, 0x30, 0x96,
            ]),
        ],
        "description": "CRC32 reflected polynomial 0xEDB88320 table",
        "severity": "medium",
    },
    {
        "category": "crc_table",
        "name": "CRC16_1021",
        "patterns": [
            bytes([
                0x00, 0x00, 0x10, 0x21,
            ]),
        ],
        "description": "CRC16 polynomial 0x1021 table start",
        "severity": "medium",
    },
    {
        "category": "crc_table",
        "name": "CRC16_8005",
        "patterns": [
            bytes([
                0x00, 0x00, 0x80, 0x05,
            ]),
        ],
        "description": "CRC16 polynomial 0x8005 table start",
        "severity": "medium",
    },
    {
        "category": "crc_table",
        "name": "CRC32_Table_256",
        "patterns": [
            bytes(range(256)),        # unlikely but a naive marker
        ],
        "description": "CRC32 256-entry table (raw bytes)",
        "severity": "low",
    },
    # ----------------------------------------------------------
    #  Scheduler patterns
    # ----------------------------------------------------------
    {
        "category": "scheduler",
        "name": "Periodic_Timer_1ms",
        "patterns": [
            b"\x00\x00\x03\xE8",     # 1000 decimal = 1ms @ 1MHz
            b"\x00\x00\x00\x64",     # 100 decimal
            b"\x00\x00\x00\x01",
        ],
        "description": "Periodic timer interrupt (1ms/10ms timers)",
        "severity": "low",
    },
    {
        "category": "scheduler",
        "name": "OS_Tick_Pattern",
        "patterns": [
            b"\x00\x00\x00\x0A",     # 10 tick
            b"\x00\x00\x00\x14",     # 20 tick
            b"\x00\x00\x00\x32",     # 50 tick
        ],
        "description": "Common OS tick values in scheduler tables",
        "severity": "low",
    },
    # ----------------------------------------------------------
    #  CAN ID patterns
    # ----------------------------------------------------------
    {
        "category": "can_id",
        "name": "CAN_Diag_Request",
        "patterns": [
            b"\x00\x00\x07\xE0",     # 0x7E0
            b"\x00\x00\x07\xE1",     # 0x7E1
            b"\x00\x00\x07\xE2",     # 0x7E2
        ],
        "description": "CAN diagnostic request IDs (0x7E0-0x7E2)",
        "severity": "medium",
    },
    {
        "category": "can_id",
        "name": "CAN_Diag_Response",
        "patterns": [
            b"\x00\x00\x07\xE8",     # 0x7E8
            b"\x00\x00\x07\xE9",     # 0x7E9
            b"\x00\x00\x07\xEA",     # 0x7EA
        ],
        "description": "CAN diagnostic response IDs (0x7E8-0x7EA)",
        "severity": "medium",
    },
    {
        "category": "can_id",
        "name": "CAN_CCP",
        "patterns": [
            b"\x00\x00\x0C\xC0",     # 0xCC0
            b"\x00\x00\x0C\xC1",     # 0xCC1
            b"\x00\x00\x0C\xE0",     # 0xCE0
        ],
        "description": "CAN CCP/XCP calibration IDs",
        "severity": "medium",
    },
    {
        "category": "can_id",
        "name": "CAN_OBD",
        "patterns": [
            b"\x00\x18\xFE\xF1\x00",  # 0x18FEF100
            b"\x00\x18\xFE\xF0\x00",  # 0x18FEF000
            b"\x00\x00\x07\xDF",     # 0x7DF
            b"\x00\x00\x07\xE0",
        ],
        "description": "Common OBD/CAN arbitration IDs",
        "severity": "low",
    },
    # ----------------------------------------------------------
    #  RSA / crypto patterns
    # ----------------------------------------------------------
    {
        "category": "rsa_crypto",
        "name": "RSA_PKCS1_Public",
        "patterns": [
            b"\x30\x82\x01\x0A\x02\x82\x01\x01\x00",  # PKCS#1 public key header
            b"\x30\x82\x01\x22\x30\x0D\x06\x09\x2A\x86\x48\x86\xF7\x0D\x01\x01\x01",
            b"\x30\x82\x01\x0D\x02\x82\x01\x01\x00",
        ],
        "description": "RSA PKCS#1 public key marker (2048-bit)",
        "severity": "high",
    },
    {
        "category": "rsa_crypto",
        "name": "RSA_Public_Key_Short",
        "patterns": [
            b"\x02\x82\x01\x01\x00",  # RSA modulus tag
            b"\x02\x03\x01\x00\x01",  # RSA public exponent 65537
        ],
        "description": "RSA public key modulus/exponent markers",
        "severity": "medium",
    },
    {
        "category": "rsa_crypto",
        "name": "AES_SBox",
        "patterns": [
            bytes([
                0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,
            ]),
        ],
        "description": "AES S-box lookup table start",
        "severity": "medium",
    },
    {
        "category": "rsa_crypto",
        "name": "Hash_Constant_IV",
        "patterns": [
            # SHA-256 initial hash values
            bytes([
                0x6A, 0x09, 0xE6, 0x67, 0xBB, 0x67, 0xAE, 0x85,
                0x3C, 0x6E, 0xF3, 0x72,
            ]),
        ],
        "description": "SHA-256 initial hash constant (first 12 bytes)",
        "severity": "low",
    },
    # ----------------------------------------------------------
    #  Diagnostic patterns (UDS service IDs in bytecode)
    #  NOTE: Only 3+ byte patterns to avoid false positives.
    #        2-byte patterns like \x27\x01 match too broadly.
    # ----------------------------------------------------------
    {
        "category": "diagnostic",
        "name": "UDS_ReadDataByIdentifier",
        "patterns": [
            b"\x22\xF1\x80",     # Active diagnostic session
            b"\x22\xF1\x90",     # VIN
            b"\x22\xF1\xA0",     # System supplier ID
            b"\x22\xF1\x86",     # Active diagnostic session
            b"\x22\xF1\x87",     # Vehicle manufacturer ECU software number
            b"\x22\xF1\x88",     # Vehicle manufacturer ECU hardware number
            b"\x22\xF1\x89",     # System supplier ECU hardware number
            b"\x22\xF1\x8A",     # System supplier ECU hardware version
            b"\x22\xF1\x8B",     # System supplier ECU software version
            b"\x22\xF1\x8C",     # System supplier ECU software version number
            b"\x22\xF1\x90",     # VIN
            b"\x22\xF1\x91",     # ECU installation date
            b"\x22\xF1\x92",     # ECU serial number
            b"\x22\xF1\x93",     # Vehicle manufacturer ECU hardware number
            b"\x22\xF1\x94",     # Vehicle manufacturer ECU hardware version
            b"\x22\xF1\x95",     # System supplier ECU hardware number
            b"\x22\xF1\x96",     # System supplier ECU hardware version
            b"\x22\xF1\x97",     # System supplier ECU software number
            b"\x22\xF1\x98",     # System supplier ECU software version
        ],
        "description": "UDS ReadDataByIdentifier (0x22) with specific DIDs",
        "severity": "medium",
    },
    {
        "category": "diagnostic",
        "name": "UDS_WriteDataByIdentifier",
        "patterns": [
            b"\x2E\xF1\x80",
            b"\x2E\xF1\x90",
            b"\x2E\xF1\xA0",
            b"\x2E\xF1\x86",
            b"\x2E\xF1\x87",
        ],
        "description": "UDS WriteDataByIdentifier (0x2E) with specific DIDs",
        "severity": "medium",
    },
    {
        "category": "diagnostic",
        "name": "UDS_RequestDownload",
        "patterns": [
            b"\x34\x00\x44",
            b"\x34\x00\x00",
        ],
        "description": "UDS RequestDownload service (0x34) - 3 bytes",
        "severity": "medium",
    },
    {
        "category": "diagnostic",
        "name": "UDS_TesterPresent",
        "patterns": [
            b"\x3E\x00\x80",     # TesterPresent with suppress positive response
        ],
        "description": "UDS TesterPresent (0x3E) with suppress flag",
        "severity": "medium",
    },
    {
        "category": "diagnostic",
        "name": "UDS_NegativeResponse",
        "patterns": [
            b"\x7F\x10\x12",     # NegativeResponse to SessionControl
            b"\x7F\x27\x35",     # NegativeResponse to SecurityAccess (invalidKey)
            b"\x7F\x27\x36",     # NegativeResponse to SecurityAccess (exceededNumberOfAttempts)
            b"\x7F\x27\x37",     # NegativeResponse to SecurityAccess (requiredTimeDelayNotExpired)
        ],
        "description": "UDS Negative Response codes (0x7F)",
        "severity": "medium",
    },
]

# Maximum offset to scan for certain patterns (first 64 KB)
_INTERRUPT_SCAN_LIMIT = 65536
_BOOTLOADER_SCAN_LIMIT = 131072
_CRC_SCAN_BLOCK_SIZE = 1024


def _compute_confidence(sig_count: int, categories: Dict[str, int],
                        total_boot: int, total_crc: int,
                        total_can: int, total_diag: int,
                        total_crypto: int) -> float:
    raw = 0.0

    # Interrupt vectors
    raw += min(categories.get("interrupt_vector", 0) * 15.0, 30.0)

    # Bootloader
    raw += min(total_boot * 10.0, 25.0)

    # CRC tables (higher weight for multiple tables)
    raw += min(total_crc * 5.0, 15.0)

    # Scheduler (low weight — universal values)
    raw += min(categories.get("scheduler", 0) * 2.0, 5.0)

    # Diagnostics
    raw += min(total_diag * 3.0, 15.0)

    # CAN IDs
    raw += min(total_can * 2.0, 10.0)

    # RSA / crypto
    raw += min(total_crypto * 8.0, 20.0)

    # Bonus for signature diversity
    hit_categories = sum(1 for v in categories.values() if v > 0)
    raw += hit_categories * 5.0

    score = min(raw, 99.9)

    logger.debug(
        "Confidence scoring: sig_count=%d categories=%d raw=%.1f score=%.1f",
        sig_count, hit_categories, raw, score,
    )
    return score


def _build_explanation(categories: Dict[str, int],
                       total_boot: int,
                       total_crc: int,
                       total_can: int,
                       total_diag: int,
                       total_crypto: int,
                       score: float) -> str:
    parts = []
    if categories.get("interrupt_vector", 0) > 0:
        parts.append(
            "interrupt vectors detected (%d)"
            % categories["interrupt_vector"]
        )
    if total_boot > 0:
        parts.append("bootloader found (%d hits)" % total_boot)
    if total_crc > 0:
        parts.append("CRC tables found (%d)" % total_crc)
    if categories.get("scheduler", 0) > 0:
        parts.append("scheduler detected")
    if total_diag > 0:
        parts.append("UDS diagnostics present (%d hits)" % total_diag)
    if total_can > 0:
        parts.append("CAN IDs found (%d)" % total_can)
    if total_crypto > 0:
        parts.append("RSA/crypto detected (%d hits)" % total_crypto)
    if not parts:
        return "No signatures detected (confidence=%.1f%%)" % score
    summary = "; ".join(parts)
    return "Signatures: %s (confidence=%.1f%%)" % (summary, score)


def scan_signatures(data: bytes) -> SignatureScanResult:
    logger.info("Starting signature scan (%d bytes)", len(data))

    result = SignatureScanResult()
    if not data:
        logger.warning("Empty data -- no signatures to scan")
        result.explanation = "Empty data, no signatures found"
        return result

    cat_count: Dict[str, int] = {}
    total_boot = 0
    total_crc = 0
    total_can = 0
    total_diag = 0
    total_crypto = 0

    for sig in KNOWN_SIGNATURES:
        cat = sig["category"]
        name = sig["name"]
        patterns = sig["patterns"]
        desc = sig["description"]
        sev = sig["severity"]
        for pattern in patterns:
            offsets = find_binary_pattern(data, pattern)
            if not offsets:
                continue
            for off in offsets[:5]:  # cap evidence per pattern
                fs = FoundSignature(
                    name=name,
                    category=cat,
                    offset=off,
                    size=len(pattern),
                    description=desc,
                    severity=sev,
                    matched_pattern=pattern,
                )
                result.signatures.append(fs)

            cat_count[cat] = cat_count.get(cat, 0) + len(offsets)
            if cat == "bootloader":
                total_boot += len(offsets)
            elif cat == "crc_table":
                total_crc += len(offsets)
            elif cat == "can_id":
                total_can += len(offsets)
            elif cat == "diagnostic":
                total_diag += len(offsets)
            elif cat == "rsa_crypto":
                total_crypto += len(offsets)

    # ----------------------------------------------------------
    #  Interrupt vector base address detection (heuristic)
    # ----------------------------------------------------------
    iv_count = cat_count.get("interrupt_vector", 0)
    if iv_count > 0:
        scan_end = min(_INTERRUPT_SCAN_LIMIT, len(data))
        # Look for the first aligned 32-bit value that looks like a
        # valid vector table base (common ranges).
        for offset in range(0, scan_end - 4, 4):
            val = read_uint32_be(data, offset)
            if 0x80000000 <= val <= 0x800FFFFF:
                result.interrupt_vector_address = val
                logger.info(
                    "Tricore-style interrupt vector base: 0x%08X at "
                    "offset 0x%X",
                    val, offset,
                )
                break
            if 0x00000000 <= val <= 0x00000400 and offset < 0x100:
                result.interrupt_vector_address = val
                logger.info(
                    "MPC-style interrupt vector base: 0x%08X at "
                    "offset 0x%X",
                    val, offset,
                )
                break
            if 0xFFFFFF00 <= val <= 0xFFFFFFFF and offset < 0x200:
                # Some SH/Renesas use high vectors
                result.interrupt_vector_address = val
                break

    # ----------------------------------------------------------
    #  Bootloader presence
    # ----------------------------------------------------------
    result.bootloader_present = total_boot > 0

    # ----------------------------------------------------------
    #  CRC table count (count unique CRC-type signatures)
    # ----------------------------------------------------------
    result.crc_tables_found = cat_count.get("crc_table", 0)

    # ----------------------------------------------------------
    #  Scheduler detection
    # ----------------------------------------------------------
    result.scheduler_detected = cat_count.get("scheduler", 0) > 0

    # ----------------------------------------------------------
    #  Diagnostics (UDS) detection
    # ----------------------------------------------------------
    result.diagnostics_present = total_diag > 0

    # ----------------------------------------------------------
    #  CAN IDs found
    # ----------------------------------------------------------
    can_ids_raw: List[int] = []
    for sig in KNOWN_SIGNATURES:
        if sig["category"] != "can_id":
            continue
        for pattern in sig["patterns"]:
            offsets = find_binary_pattern(data, pattern)
            for off in offsets[:3]:
                # Attempt to interpret the 4 bytes as a CAN ID
                if len(pattern) >= 4:
                    can_val = read_uint32_be(data, off)
                    if can_val > 0:
                        can_ids_raw.append(can_val)
    # Deduplicate and sort
    result.can_ids_found = sorted(set(can_ids_raw))[:20]

    # ----------------------------------------------------------
    #  RSA / crypto detection
    # ----------------------------------------------------------
    result.rsa_detected = total_crypto > 0

    # ----------------------------------------------------------
    #  Confidence scoring
    # ----------------------------------------------------------
    score = _compute_confidence(
        len(result.signatures),
        cat_count,
        total_boot,
        total_crc,
        total_can,
        total_diag,
        total_crypto,
    )
    result.confidence = score
    result.explanation = _build_explanation(
        cat_count,
        total_boot,
        total_crc,
        total_can,
        total_diag,
        total_crypto,
        score,
    )

    logger.info(
        "Signature scan complete: %d sigs, %.1f%% confidence",
        len(result.signatures),
        score,
    )
    return result
