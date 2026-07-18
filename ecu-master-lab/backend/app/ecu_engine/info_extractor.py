"""
Couche 4 : Extraction des informations techniques d'un ECU.

Scanne les chaines ASCII pour identifier HW/SW, VIN, calibration,
moteur, normes emission, references fabricant et identifiants ASAM/ODX.
"""

import re
import logging
from typing import List, Tuple, Dict, Optional

from .models import TechnicalInfo
from .utils import (
    find_ascii_strings,
    read_uint16_be,
    read_uint16_le,
    read_uint32_be,
    read_uint32_le,
)

logger = logging.getLogger(__name__)

HEADER_SCAN = 256 * 1024
TAIL_SCAN = 64 * 1024
MIN_STR_LEN = 4

# -- compiled patterns --------------------------------------------------

_PATTERNS_HW = [
    re.compile(r"HW[\s:]+([A-Za-z0-9 .\-/]{3,40})"),
    re.compile(r"Hardware[\s:]+([A-Za-z0-9 .\-/]{3,40})"),
    re.compile(r"Mat[\s]*No[\s.:]+([A-Za-z0-9 .\-/]{3,40})"),
    re.compile(r"Part[\s#]+([A-Za-z0-9 \-]{5,30})"),
]

_PATTERNS_SW = [
    re.compile(r"SW[\s:]+([A-Za-z0-9 .\-/]{3,40})"),
    re.compile(r"Software[\s:]+([A-Za-z0-9 .\-/]{3,40})"),
    re.compile(r"Version[\s:]+([A-Za-z0-9 .\-]{3,30})"),
]

_PATTERNS_CAL = [
    re.compile(r"CalID[\s:=]+([A-Za-z0-9]{4,32})"),
    re.compile(r"CVN[\s:=]+([A-Za-z0-9]{4,32})"),
    re.compile(r"Calibration[\s:=]+([A-Za-z0-9]{4,32})"),
]

_VIN_PATTERN = re.compile(
    r"[A-HJ-NPR-Z0-9]{17}"
)

_PATTERNS_ENGINE = [
    re.compile(r"\d\.\d\s*TDI", re.IGNORECASE),
    re.compile(r"\d\.\d\s*TSI", re.IGNORECASE),
    re.compile(r"\d\.\d\s*TFSI", re.IGNORECASE),
    re.compile(r"\d\.\d\s*dCi", re.IGNORECASE),
    re.compile(r"\d\.\d\s*HDi", re.IGNORECASE),
    re.compile(r"\d\.\d\s*JTD", re.IGNORECASE),
    re.compile(r"\d\.\d\s*CRDI", re.IGNORECASE),
    re.compile(r"\d\.\d\s*CDI", re.IGNORECASE),
    re.compile(r"\d\.\d\s*Ecoboost", re.IGNORECASE),
    re.compile(r"\d\.\d\s*DCR", re.IGNORECASE),
]

_PATTERNS_EMISSION = [
    re.compile(r"Euro\s*[56]", re.IGNORECASE),
    re.compile(r"EPA", re.IGNORECASE),
    re.compile(r"CARB", re.IGNORECASE),
    re.compile(r"Euro\s*[34]", re.IGNORECASE),
    re.compile(r"Tier\s*2", re.IGNORECASE),
    re.compile(r"OBD\s*II", re.IGNORECASE),
]

_PATTERNS_MANUFACTURER = [
    re.compile(r"0\s*281\s*0\d{6,10}"),
    re.compile(r"0\s*281\s*\d{7,10}"),
    re.compile(r"[0-9A-Z]{2,4}\s*\d{5,10}"),
    re.compile(r"Continental\s*[A-Z0-9\-]{5,25}"),
    re.compile(r"Delphi\s*[A-Z0-9\-]{5,25}"),
    re.compile(r"Denso\s*[A-Z0-9\-]{5,25}"),
]

_PATTERNS_ASAM = [
    re.compile(r"ASAM\s*[A-Z0-9_\-\.]{5,40}"),
    re.compile(r"ODX[\s:=]+[A-Za-z0-9_\-\.]{5,40}"),
    re.compile(r"ODXID[\s:=]+([A-Za-z0-9_\-\.]+)"),
]

_VIN_KNOWN_OFFSETS = [0x00, 0x10, 0x20, 0x40, 0x60, 0x100, 0x200, 0x400, 0x800]


# -- helper -----------------------------------------------------------

def _extract_value(text: str, pattern: re.Pattern) -> Optional[str]:
    """Return group(1) or the full match if no capture group."""
    m = pattern.search(text)
    if not m:
        return None
    if m.lastindex and m.lastindex >= 1:
        return m.group(1).strip()
    return m.group(0).strip()


def _collect_strings(data: bytes) -> List[Tuple[int, str]]:
    """Scan first 256 KB and last 64 KB for ASCII strings."""
    head_end = min(HEADER_SCAN, len(data))
    tail_start = max(0, len(data) - TAIL_SCAN)

    head = find_ascii_strings(data, MIN_STR_LEN, head_end)
    tail = find_ascii_strings(data, MIN_STR_LEN, len(data))
    tail = [(off, s) for off, s in tail if off >= tail_start]
    seen = set()
    merged = []
    for off, s in head:
        if s not in seen:
            seen.add(s)
            merged.append((off, s))
    for off, s in tail:
        if s not in seen:
            seen.add(s)
            merged.append((off, s))
    return merged


def _vin_from_known_offsets(data: bytes) -> Optional[str]:
    """Check common VIN offsets for 17-char alphanumeric patterns."""
    for offset in _VIN_KNOWN_OFFSETS:
        end = offset + 17
        if end <= len(data):
            chunk = data[offset:end].decode("ascii", errors="ignore")
            if _VIN_PATTERN.fullmatch(chunk):
                return chunk
    return None


def _vin_from_strings(strings: List[Tuple[int, str]]) -> Optional[str]:
    """Search among extracted strings for a 17-char VIN candidate."""
    for _off, s in strings:
        s_clean = s.replace(" ", "").replace("-", "")
        if len(s_clean) == 17 and _VIN_PATTERN.fullmatch(s_clean):
            return s_clean
    # allow substrings within longer strings
    joined = " ".join(s for _, s in strings)
    m = _VIN_PATTERN.search(joined)
    if m:
        candidate = m.group(0)
        if len(candidate) == 17:
            return candidate
    return None


def _search_patterns(
    text: str,
    patterns: List[re.Pattern],
    label: str,
    evidence: List[str],
) -> Optional[str]:
    """Try each pattern, record evidence on first match."""
    for pat in patterns:
        val = _extract_value(text, pat)
        if val:
            evidence.append(
                "{0}: matched pattern '{1}' -> '{2}'".format(label, pat.pattern[:40], val)
            )
            return val
    return None


def _extract_16bit_values(
    data: bytes, offset: int, count: int, little_endian: bool = True
) -> List[int]:
    """Read a sequence of uint16 values around an offset (±64 bytes)."""
    start = max(0, offset - 64)
    end = min(len(data), offset + count * 2 + 64)
    results = []
    i = start
    while i < end - 1:
        if little_endian:
            val = read_uint16_le(data, i)
        else:
            val = read_uint16_be(data, i)
        results.append(val)
        i += 2
    return results


def extract_technical_info(data: bytes) -> TechnicalInfo:
    """
    Scan the binary for human-readable metadata and heuristic numeric
    signatures.  Returns a ``TechnicalInfo`` populated with as many
    fields as could be extracted, a confidence score and an evidence
    trail.
    """
    info = TechnicalInfo()
    evidence = info.evidence  # alias for convenience

    if not data:
        evidence.append("Empty data, nothing to extract")
        return info

    logger.info("Collecting ASCII strings (first 256 KB + last 64 KB)")
    strings = _collect_strings(data)
    joined = "\n".join(s for _, s in strings)

    # -- HW Number ----------------------------------------------------
    hw = _search_patterns(joined, _PATTERNS_HW, "HW", evidence)
    if hw:
        info.hw_number = hw

    # heuristic: long numeric/dash string that looks like a part number
    if not info.hw_number:
        m = re.search(r"\b\d[\d ]{6,20}\b", joined)
        if m:
            info.hw_number = m.group(0).strip()
            evidence.append(
                "HW (numeric heuristic): '{0}'".format(info.hw_number)
            )

    # -- SW Number ----------------------------------------------------
    sw = _search_patterns(joined, _PATTERNS_SW, "SW", evidence)
    if sw:
        info.sw_number = sw

    # -- Calibration ID / CVN -----------------------------------------
    cal = _search_patterns(joined, _PATTERNS_CAL, "CAL", evidence)
    if cal:
        info.calibration_id = cal

    # separate CVN extraction if CalID matched but CVN didn't
    if info.calibration_id and not info.cvn:
        cvn_m = re.search(r"CVN[\s:=]+([A-Fa-f0-9]{4,32})", joined)
        if cvn_m:
            info.cvn = cvn_m.group(1).strip()
            evidence.append("CVN: '{0}'".format(info.cvn))

    # -- VIN ----------------------------------------------------------
    vin = _vin_from_known_offsets(data)
    if vin:
        info.vin = vin
        evidence.append("VIN (known offset): '{0}'".format(vin))
    else:
        vin = _vin_from_strings(strings)
        if vin:
            info.vin = vin
            evidence.append("VIN (string scan): '{0}'".format(vin))

    # -- Engine Type --------------------------------------------------
    engine = _search_patterns(joined, _PATTERNS_ENGINE, "ENGINE", evidence)
    if engine:
        info.engine_type = engine

    # -- Emission Standard --------------------------------------------
    em = _search_patterns(joined, _PATTERNS_EMISSION, "EMISSION", evidence)
    if em:
        info.emission_standard = em

    # -- Manufacturer References --------------------------------------
    seen_refs = set()  # type: Dict[str, str] used as set below
    for pat in _PATTERNS_MANUFACTURER:
        for m in pat.finditer(joined):
            ref = m.group(0).strip()
            if ref not in seen_refs and len(ref) >= 8:
                seen_refs.add(ref)
                info.manufacturer_refs.append(ref)
                evidence.append("MFR ref: '{0}'".format(ref))
    # limit to top 10 most distinctive
    info.manufacturer_refs = info.manufacturer_refs[:10]

    # -- ASAM / ODX ---------------------------------------------------
    asam = _search_patterns(joined, _PATTERNS_ASAM, "ASAM/ODX", evidence)
    if asam:
        info.asam_id = asam

    # -- Serial Number heuristic (digits after S/N or SN:) -----------
    sn_m = re.search(r"(?:S/?N|Serial)[\s:=]+([A-Za-z0-9]{4,30})", joined)
    if sn_m:
        info.serial_number = sn_m.group(1).strip()
        evidence.append("Serial: '{0}'".format(info.serial_number))

    # -- Production Date heuristic ------------------------------------
    date_m = re.search(
        r"(?:Date|Prod|Build)[\s:=]*(\d{4}[\-/\.]\d{2}[\-/\.]\d{2})", joined
    )
    if date_m:
        info.production_date = date_m.group(1).strip()
        evidence.append("Date: '{0}'".format(info.production_date))

    # -- 16-bit value heuristics at string boundaries -----------------
    # Some ECUs store the HW/SW version as uint16 pairs near the
    # firmware identifier string.  Check around first matched string
    # offset for version-like uint16 clusters.
    if strings:
        first_off = strings[0][0]
        le_vals = _extract_16bit_values(data, first_off, 8, little_endian=True)
        be_vals = _extract_16bit_values(data, first_off, 8, little_endian=False)
        version_candidates = set()
        for v in le_vals + be_vals:
            if 0x0001 <= v <= 0xFFFF:
                version_candidates.add(v)
        if version_candidates and not info.software_version:
            # pick the most common value as a guess
            most_common = max(version_candidates, key=lambda x: list(version_candidates).count(x))
            info.software_version = "0x{0:04X}".format(most_common)
            evidence.append(
                "SW version (uint16 heuristic): '{0}'".format(info.software_version)
            )

    # -- Confidence scoring -------------------------------------------
    fields_found = sum(
        1 for v in [
            info.hw_number,
            info.sw_number,
            info.calibration_id,
            info.vin,
            info.engine_type,
            info.emission_standard,
            info.serial_number,
            info.production_date,
            info.asam_id,
        ] if v
    )
    fields_found += min(len(info.manufacturer_refs), 3)
    fields_found += 1 if info.cvn else 0

    # Normalize to 0-1 range.  Finding 6+ fields is considered very
    # confident; each additional string found beyond that adds little.
    raw = fields_found / 10.0
    info.confidence = min(raw, 1.0)

    evidence.append(
        "Confidence: {0:.2f} ({1} key fields found)".format(
            info.confidence, fields_found
        )
    )

    # Store a sample of raw strings for downstream layers
    sample_limit = 200
    for off, s in strings[:sample_limit]:
        key = "0x{0:08X}".format(off)
        info.raw_strings[key] = s

    logger.info(
        "Extraction complete: HW=%s  SW=%s  VIN=%s  confidence=%.2f",
        info.hw_number or "?",
        info.sw_number or "?",
        info.vin or "?",
        info.confidence,
    )
    return info
