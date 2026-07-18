"""
DB Matcher — Identifie un fichier ECU inconnu en interrogeant
la base de connaissances (known_signatures, known_strings, etc.).

Retourne une liste de candidats scored avec des preuves.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.new.ecu_models import (
    KnownChecksum,
    KnownEcuFile,
    KnownMap,
    KnownSegment,
    KnownSignature,
    KnownString,
)

log = logging.getLogger("ecu_engine.db_matcher")


def _extract_file_strings(data: bytes, min_length: int = 6, max_count: int = 200) -> List[str]:
    """Extract ASCII strings from binary for matching."""
    strings = []
    current = []
    for byte in data:
        if 32 <= byte < 127:
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                text = "".join(current).strip()
                if text:
                    strings.append(text)
            current = []
    if len(current) >= min_length:
        text = "".join(current).strip()
        if text:
            strings.append(text)
    return strings[:max_count]


def _extract_file_patterns(data: bytes) -> List[str]:
    """Extract 4+ byte patterns from binary for matching."""
    patterns = []
    # Sample at key offsets to avoid scanning entire file
    offsets_to_check = list(range(0, min(len(data), 65536), 4))
    if len(data) > 65536:
        # Also sample middle and end
        mid = len(data) // 2
        end = len(data) - 65536
        offsets_to_check.extend(range(mid, mid + 32768, 4))
        offsets_to_check.extend(range(end, end + 32768, 4))

    seen = set()
    for off in offsets_to_check:
        if off + 4 <= len(data):
            p = data[off:off + 4].hex()
            if p not in seen:
                seen.add(p)
                patterns.append(p)
    return patterns


def match_from_db(
    db: Session,
    data: bytes,
    file_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Query the knowledge database to identify an unknown ECU file.

    Returns a list of candidate dicts sorted by score:
    [
        {
            "ecu_model_name": "Bosch EDC16C60",
            "manufacturer_name": "Bosch",
            "score": 0.85,
            "evidence": ["12 string matches", "3 pattern matches", "2 segment matches"],
            "match_details": {
                "strings_matched": 12,
                "patterns_matched": 3,
                "segments_matched": 2,
                "total_known_files": 5,
            }
        },
        ...
    ]
    """
    candidates: Dict[str, Dict[str, Any]] = {}

    def _ensure_candidate(name: str, manufacturer: str = None):
        if name not in candidates:
            candidates[name] = {
                "ecu_model_name": name,
                "manufacturer_name": manufacturer or "",
                "score": 0.0,
                "evidence": [],
                "match_details": {
                    "strings_matched": 0,
                    "patterns_matched": 0,
                    "segments_matched": 0,
                    "checksums_matched": 0,
                    "total_known_files": 0,
                },
            }

    # --- 1. String matching ---
    file_strings = _extract_file_strings(data)
    if file_strings:
        # Query known strings that match file strings (batch query)
        # Truncate string values for LIKE query
        string_upper = [s.upper()[:100] for s in file_strings if len(s) >= 6]

        if string_upper:
            # Use ILIKE for case-insensitive matching
            for s_upper in string_upper[:100]:  # Limit to avoid slow queries
                matches = db.query(KnownString).filter(
                    func.upper(KnownString.string_value).like("%" + s_upper[:50] + "%")
                ).all()
                for m in matches:
                    name = m.ecu_model_name or "Unknown"
                    _ensure_candidate(name, m.manufacturer_name if hasattr(m, 'manufacturer_name') else "")
                    c = candidates[name]
                    c["match_details"]["strings_matched"] += 1
                    c["score"] += 0.15 * (m.confidence or 0.5)
                    if len(c["evidence"]) < 5:
                        c["evidence"].append("String match: '%s'" % s_upper[:30])

    # --- 2. Pattern matching ---
    file_patterns = _extract_file_patterns(data)
    if file_patterns:
        for p_hex in file_patterns[:50]:
            matches = db.query(KnownSignature).filter(
                KnownSignature.pattern_hex == p_hex
            ).all()
            for m in matches:
                name = m.ecu_model_name or "Unknown"
                _ensure_candidate(name)
                c = candidates[name]
                c["match_details"]["patterns_matched"] += 1
                c["score"] += 0.25 * (m.confidence or 0.5)
                if len(c["evidence"]) < 5:
                    c["evidence"].append("Pattern match: %s" % p_hex[:16])

    # --- 3. Segment matching ---
    if file_size:
        # Rough size-based matching
        size_matches = db.query(
            KnownSegment.ecu_model_name,
            func.count(KnownSegment.id).label("cnt"),
        ).filter(
            func.abs(KnownSegment.end_offset - file_size) < file_size * 0.1
        ).group_by(
            KnownSegment.ecu_model_name
        ).all()
        for name, cnt in size_matches:
            if name:
                _ensure_candidate(name)
                c = candidates[name]
                c["match_details"]["segments_matched"] += cnt
                c["score"] += 0.10 * min(cnt, 5)

    # --- 4. Compute final scores ---
    results = list(candidates.values())

    # Normalize scores
    if results:
        max_score = max(c["score"] for c in results)
        if max_score > 0:
            for c in results:
                c["score"] = min(c["score"] / max_score * 100, 99.9)

    # Sort by score descending
    results.sort(key=lambda c: c["score"], reverse=True)

    # Count total known files per model
    for c in results:
        count = db.query(KnownEcuFile).filter(
            KnownEcuFile.ecu_model_name == c["ecu_model_name"]
        ).count()
        c["match_details"]["total_known_files"] = count

    log.info(
        "DB match: %d candidates found, best=%.1f%% (%s)",
        len(results),
        results[0]["score"] if results else 0,
        results[0]["ecu_model_name"] if results else "none",
    )

    return results[:10]


def match_referentiel(db: Session, data: bytes) -> List[Dict[str, Any]]:
    """
    Match against the referentiel tables (ecu_models + software_versions).
    Used as fallback when knowledge tables are empty.
    Returns candidates scored against referentiel data.
    """
    candidates: Dict[str, Dict[str, Any]] = {}

    def _ensure(name, manufacturer=""):
        if name not in candidates:
            candidates[name] = {
                "ecu_model_name": name,
                "manufacturer_name": manufacturer,
                "score": 0.0,
                "evidence": [],
                "match_details": {"referentiel_score": 0, "total_known_files": 0},
            }

    try:
        from app.models.new.ecu_models import (
            ECUModel as _DBECUModel,
            SoftwareVersion as _DBSWVersion,
            Manufacturer as _DBMfr,
        )
        from sqlalchemy.orm import joinedload
    except ImportError:
        return []

    ecu_models = db.query(_DBECUModel).options(
        joinedload(_DBECUModel.manufacturer)
    ).all()

    if not ecu_models:
        return []

    # Extract strings from binary for matching
    strings = []
    current = []
    for byte in data:
        if 32 <= byte < 127:
            current.append(chr(byte))
        else:
            if len(current) >= 6:
                strings.append("".join(current).strip())
            current = []
    if len(current) >= 6:
        strings.append("".join(current).strip())
    text_blob = " ".join(strings).lower()

    for model in ecu_models:
        mfr_name = model.manufacturer.name if model.manufacturer else ""
        model_lower = (model.model_name or "").lower()
        family_lower = (model.family or "").lower()

        score = 0.0
        evidence = []

        if model_lower and model_lower in text_blob:
            score += 30
            evidence.append("Model name found in strings: %s" % model.model_name)

        if family_lower and family_lower in text_blob:
            score += 20
            evidence.append("Family found in strings: %s" % model.family)

        typical_brands = (model.typical_brands or "").lower()
        if typical_brands:
            for tb in typical_brands.split(","):
                tb = tb.strip()
                if tb and tb in text_blob:
                    score += 10
                    evidence.append("Typical brand match: %s" % tb)
                    break

        if score < 5:
            continue

        name = model.model_name
        _ensure(name, mfr_name)
        candidates[name]["score"] = score
        candidates[name]["evidence"] = evidence
        candidates[name]["match_details"]["referentiel_score"] = score

    results = list(candidates.values())
    if results:
        max_s = max(c["score"] for c in results)
        if max_s > 0:
            for c in results:
                c["score"] = min(c["score"] / max_s * 100, 99.9)
    results.sort(key=lambda c: c["score"], reverse=True)
    return results[:10]
