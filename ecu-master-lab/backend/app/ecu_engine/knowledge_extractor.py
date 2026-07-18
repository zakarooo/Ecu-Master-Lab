"""
Knowledge Extractor — Extrait les features d'un fichier ECU connu
et les stocke dans la base de connaissances pour enrichir le
matching futur.

Utilise les couches existantes du moteur ECU pour l'extraction,
puis enregistre les résultats dans les tables knowledge DB.
"""

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.new.ecu_models import (
    KnownChecksum,
    KnownEcuFile,
    KnownMap,
    KnownSegment,
    KnownSignature,
    KnownString,
)

log = logging.getLogger("ecu_engine.knowledge")

# Categories for classifying extracted strings
_STRING_CATEGORIES = {
    "hw": ["HW", "Hardware", "Mat", "Part"],
    "sw": ["SW", "Software", "Version"],
    "brand": ["Bosch", "Continental", "Siemens", "Delphi", "Denso", "Hitachi", "Valeo", "Marelli"],
    "model": ["EDC", "MED", "ME7", "ME9", "SID", "DCM", "SIMOS", "IAW"],
    "calibration": ["CalID", "CVN", "Calibration"],
    "vin": ["VIN"],
    "engine": ["TDI", "TSI", "TFSI", "dCi", "HDi", "JTD", "CRDI", "CDI"],
    "protocol": ["UDS", "KWP", "CAN", "ISO"],
    "other": [],
}

# Unique binary patterns to extract (byte sequences that distinguish ECU types)
_SIGNATURE_PATTERNS = [
    # Bootloader patterns
    (b"\x02\x01\x00\x00", "bootloader", "Bosch ME17 boot"),
    (b"\xFF\xFF\x00\x00", "bootloader", "Bosch boot marker"),
    (b"\x55\xAA\x55\xAA", "bootloader", "Universal boot sig"),
    (b"\xDE\x1C\x00\x00", "bootloader", "Delphi DCM boot"),
    (b"\xDE\x1C\x01\x00", "bootloader", "Delphi DCM boot v2"),
    (b"\xAA\x55\xAA\x55", "bootloader", "Delphi boot marker"),
    (b"\x10\x10\x10\x10", "bootloader", "Bosch ECU boot"),
    (b"\x11\x22\x33\x44", "bootloader", "Bosch ECU boot v2"),
    # CRC table patterns
    (bytes([0x00, 0x00, 0x00, 0x00, 0x04, 0xC1, 0x1D, 0xB7]), "crc_table", "CRC32 04C11DB7"),
    (bytes([0x00, 0x00, 0x00, 0x00, 0x77, 0x07, 0x30, 0x96]), "crc_table", "CRC32 EDB88320"),
    # Interrupt vectors
    (b"\x00\x00\x0F\xFF", "interrupt_vector", "Tricore BTV"),
    (b"\x00\x00\x04\x00", "interrupt_vector", "MPC VLE"),
    (b"\x00\x00\x03\x00", "interrupt_vector", "SH IVT"),
    # RSA / Crypto
    (b"\x63\x7C\x77\x7B\xF2\x6B\x6F\xC5", "crypto", "AES S-box"),
    (bytes([0x6A, 0x09, 0xE6, 0x67, 0xBB, 0x67, 0xAE, 0x85, 0x3C, 0x6E, 0xF3, 0x72]), "crypto", "SHA-256 IV"),
]


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _classify_string(text: str) -> str:
    """Classify an ASCII string into a category."""
    text_upper = text.upper().strip()
    for cat, keywords in _STRING_CATEGORIES.items():
        if cat == "other":
            continue
        for kw in keywords:
            if kw.upper() in text_upper:
                return cat
    return "other"


def _extract_unique_patterns(data: bytes) -> List[Dict[str, Any]]:
    """Extract unique binary patterns that appear in the file."""
    results = []
    for pattern, category, description in _SIGNATURE_PATTERNS:
        offsets = []
        start = 0
        while True:
            idx = data.find(pattern, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
            if len(offsets) >= 10:
                break
        if offsets:
            results.append({
                "pattern_hex": pattern.hex(),
                "pattern_bytes": pattern,
                "category": category,
                "description": description,
                "offsets": offsets,
                "occurrence_count": len(offsets),
            })
    return results


def _extract_strings(data: bytes, min_length: int = 6, max_count: int = 200) -> List[Dict[str, Any]]:
    """Extract significant ASCII strings from the binary."""
    strings = []
    current = []
    current_start = 0

    for i, byte in enumerate(data):
        if 32 <= byte < 127:
            if not current:
                current_start = i
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                text = "".join(current).strip()
                if text:
                    strings.append({
                        "string_value": text[:500],
                        "offset": current_start,
                        "category": _classify_string(text),
                    })
            current = []

    if len(current) >= min_length:
        text = "".join(current).strip()
        if text:
            strings.append({
                "string_value": text[:500],
                "offset": current_start,
                "category": _classify_string(text),
            })

    # Prioritize: hw, sw, brand, model first, then others
    priority_order = {"hw": 0, "sw": 1, "brand": 2, "model": 3, "calibration": 4, "vin": 5, "engine": 6, "protocol": 7, "other": 8}
    strings.sort(key=lambda s: (priority_order.get(s["category"], 9), s["offset"]))

    return strings[:max_count]


def _extract_segments(data: bytes) -> List[Dict[str, Any]]:
    """Extract memory segments from the binary using entropy analysis."""
    from app.ecu_engine.utils import compute_entropy

    segments = []
    block_size = 4096
    current_type = None
    current_start = 0

    for offset in range(0, len(data), block_size):
        block = data[offset:offset + block_size]
        if not block:
            break

        entropy = compute_entropy(block)
        non_empty = sum(1 for b in block if b != 0) / len(block)

        # Classify
        if entropy < 0.15 and non_empty < 0.15:
            seg_type = "empty"
        elif entropy < 0.3 and non_empty > 0.8:
            seg_type = "data"
        elif entropy > 0.7 and non_empty > 0.8:
            seg_type = "code"
        elif entropy > 0.4 and non_empty > 0.5:
            seg_type = "calibration"
        else:
            seg_type = "mixed"

        if seg_type != current_type:
            if current_type and current_type != "mixed":
                segments.append({
                    "segment_type": current_type,
                    "start_offset": current_start,
                    "end_offset": offset,
                    "entropy": compute_entropy(data[current_start:offset]),
                })
            current_type = seg_type
            current_start = offset

    # Last segment
    if current_type and current_type not in ("mixed", "empty"):
        segments.append({
            "segment_type": current_type,
            "start_offset": current_start,
            "end_offset": len(data),
            "entropy": compute_entropy(data[current_start:len(data)]),
        })

    return segments


def extract_and_store(
    db: Session,
    data: bytes,
    filename: str,
    file_path: str,
    ecu_model_name: str,
    manufacturer_name: str,
    ecu_model_id: Optional[int] = None,
    user_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract all features from a known ECU file and store them in the knowledge DB.

    Returns a summary dict with counts of extracted features.
    """
    sha256 = _compute_sha256(data)
    file_size = len(data)

    # Check if already registered
    existing = db.query(KnownEcuFile).filter(KnownEcuFile.sha256 == sha256).first()
    if existing:
        log.info("File already registered: %s (id=%d)", sha256[:16], existing.id)
        return {"status": "already_registered", "known_file_id": existing.id}

    # 1. Register the known file
    known_file = KnownEcuFile(
        sha256=sha256,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        ecu_model_id=ecu_model_id,
        ecu_model_name=ecu_model_name,
        manufacturer_name=manufacturer_name,
        confirmed_by=user_id,
        notes=notes,
    )
    db.add(known_file)
    db.flush()
    source_id = known_file.id

    stats = {"known_file_id": source_id, "signatures": 0, "strings": 0, "segments": 0}

    # 2. Extract and store binary patterns
    patterns = _extract_unique_patterns(data)
    for p in patterns:
        # Check if this pattern already exists for this ECU model
        existing_sig = db.query(KnownSignature).filter(
            KnownSignature.pattern_hex == p["pattern_hex"],
            KnownSignature.ecu_model_name == ecu_model_name,
        ).first()

        if existing_sig:
            existing_sig.occurrence_count += 1
            existing_sig.total_known_files += 1
        else:
            sig = KnownSignature(
                ecu_model_id=ecu_model_id,
                ecu_model_name=ecu_model_name,
                category=p["category"],
                pattern_hex=p["pattern_hex"],
                pattern_bytes=p["pattern_bytes"],
                context_hex=p["description"],
                occurrence_count=p["occurrence_count"],
                total_known_files=1,
                confidence=min(0.3 + len(patterns) * 0.05, 0.9),
                source_file_id=source_id,
            )
            db.add(sig)
            stats["signatures"] += 1

    # 3. Extract and store strings
    strings = _extract_strings(data)
    for s in strings:
        existing_str = db.query(KnownString).filter(
            KnownString.string_value == s["string_value"],
            KnownString.ecu_model_name == ecu_model_name,
        ).first()

        if existing_str:
            existing_str.occurrence_count += 1
            existing_str.total_known_files += 1
        else:
            kstr = KnownString(
                ecu_model_id=ecu_model_id,
                ecu_model_name=ecu_model_name,
                string_value=s["string_value"],
                offset=s["offset"],
                category=s["category"],
                occurrence_count=1,
                total_known_files=1,
                confidence=0.5 if s["category"] != "other" else 0.2,
                source_file_id=source_id,
            )
            db.add(kstr)
            stats["strings"] += 1

    # 4. Extract and store segments
    segments = _extract_segments(data)
    for seg in segments:
        kseg = KnownSegment(
            ecu_model_id=ecu_model_id,
            ecu_model_name=ecu_model_name,
            segment_type=seg["segment_type"],
            start_offset=seg["start_offset"],
            end_offset=seg["end_offset"],
            entropy=seg["entropy"],
            occurrence_count=1,
            total_known_files=1,
            confidence=0.4,
            source_file_id=source_id,
        )
        db.add(kseg)
        stats["segments"] += 1

    db.commit()
    log.info(
        "Knowledge extracted: %d signatures, %d strings, %d segments for %s",
        stats["signatures"], stats["strings"], stats["segments"], ecu_model_name,
    )
    return stats
