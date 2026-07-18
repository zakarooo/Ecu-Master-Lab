"""Layer 2 - Processor identification for ECU binary analysis."""

import logging
import re
import struct
from typing import Dict, List, Optional, Tuple

from .models import ProcessorFamily, ProcessorProfile, ProcessorResult
from .utils import (
    compute_entropy,
    find_ascii_strings,
    find_binary_pattern,
    read_uint32_be,
)

logger = logging.getLogger("ecu_engine.processor")

# ==============================================================
#  PROCESSOR DATABASE
# ==============================================================

PROCESSOR_DATABASE: Dict[str, ProcessorProfile] = {
    "TC1766": ProcessorProfile(
        family=ProcessorFamily.TRICORE, core="TC1766", manufacturer="Infineon",
        word_size=32, endianness="big", clock_mhz=150, flash_size=1_032_192,
        ram_size=68_096, known_ecus=["Bosch MED9.1", "Bosch EDC16", "Siemens Simos 7"]),
    "TC1767": ProcessorProfile(
        family=ProcessorFamily.TRICORE, core="TC1767", manufacturer="Infineon",
        word_size=32, endianness="big", clock_mhz=150, flash_size=1_032_192,
        ram_size=68_096, known_ecus=["Bosch MED9.1", "Bosch ME7", "Continental SIM2K"]),
    "TC1797": ProcessorProfile(
        family=ProcessorFamily.TRICORE, core="TC1797", manufacturer="Infineon",
        word_size=32, endianness="big", clock_mhz=200, flash_size=2_097_152,
        ram_size=124_928, known_ecus=["Bosch MED17", "Bosch EDC17", "Continental SIMOS 18"]),
    "TC377": ProcessorProfile(
        family=ProcessorFamily.TRICORE, core="TC377", manufacturer="Infineon",
        word_size=32, endianness="big", clock_mhz=300, flash_size=8_388_608,
        ram_size=688_128, known_ecus=["Bosch MED17.7", "Bosch EDC17C64"]),
    "MPC563": ProcessorProfile(
        family=ProcessorFamily.MPC5xx, core="MPC563", manufacturer="NXP",
        word_size=32, endianness="big", clock_mhz=56, flash_size=448_000,
        ram_size=36_000, known_ecus=["Delphi DCM3.7"]),
    "MPC5634": ProcessorProfile(
        family=ProcessorFamily.MPC5xxx, core="MPC5634", manufacturer="NXP",
        word_size=32, endianness="big", clock_mhz=150, flash_size=1_536_000,
        ram_size=96_000, known_ecus=["Bosch EDC17CP44", "Magneti Marelli IAW"]),
    "MPC5567": ProcessorProfile(
        family=ProcessorFamily.MPC5xxx, core="MPC5567", manufacturer="NXP",
        word_size=32, endianness="big", clock_mhz=132, flash_size=1_024_000,
        ram_size=48_000, known_ecus=["Bosch MED9", "Delphi DCM"]),
    "ST10F275": ProcessorProfile(
        family=ProcessorFamily.ST10, core="ST10F275", manufacturer="STMicroelectronics",
        word_size=16, endianness="big", clock_mhz=64, flash_size=832_000,
        ram_size=48_000, known_ecus=["Bosch ME7.5", "Siemens Simos 6"]),
    "SH7058": ProcessorProfile(
        family=ProcessorFamily.SH705x, core="SH7058", manufacturer="Renesas",
        word_size=32, endianness="big", clock_mhz=80, flash_size=1_024_000,
        ram_size=48_000, known_ecus=["Denso", "Hitachi"]),
    "SH72531": ProcessorProfile(
        family=ProcessorFamily.SH725xx, core="SH72531", manufacturer="Renesas",
        word_size=32, endianness="big", clock_mhz=120, flash_size=1_536_000,
        ram_size=96_000, known_ecus=["Denso 275000"]),
    "RH850": ProcessorProfile(
        family=ProcessorFamily.RH850, core="RH850C1M", manufacturer="Renesas",
        word_size=32, endianness="big", clock_mhz=120, flash_size=4_096_000,
        ram_size=256_000, known_ecus=["Continental", "Bosch", "Hitachi"]),
    "Cortex-R5": ProcessorProfile(
        family=ProcessorFamily.ARM_CORTEX, core="Cortex-R5", manufacturer="ARM / Various",
        word_size=32, endianness="little", clock_mhz=400, flash_size=2_048_000,
        ram_size=256_000, known_ecus=["Bosch MED17.5", "Bosch EDC17"]),
    "Cortex-M7": ProcessorProfile(
        family=ProcessorFamily.ARM_CORTEX, core="Cortex-M7", manufacturer="ARM / Various",
        word_size=32, endianness="little", clock_mhz=480, flash_size=2_048_000,
        ram_size=512_000, known_ecus=["Various modern ECU platforms"]),
    "C166": ProcessorProfile(
        family=ProcessorFamily.INFINEON_166, core="C166", manufacturer="Infineon",
        word_size=16, endianness="big", clock_mhz=40, flash_size=256_000,
        ram_size=16_000, known_ecus=["Bosch ME5", "Bosch ME7.1"]),
    "V850": ProcessorProfile(
        family=ProcessorFamily.NEC_V850, core="V850ES", manufacturer="NEC / Renesas",
        word_size=32, endianness="big", clock_mhz=133, flash_size=1_024_000,
        ram_size=48_000, known_ecus=["Bosch EDC15", "Bosch ME7"]),
}

# ==============================================================
#  DETECTION HEURISTICS
# ==============================================================

_NAME_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"TC\s*176[67]", re.I), "TC1766"),
    (re.compile(r"TC\s*1797", re.I),    "TC1797"),
    (re.compile(r"TC\s*37[7Xx]", re.I), "TC377"),
    (re.compile(r"MPC\s*5634", re.I),   "MPC5634"),
    (re.compile(r"MPC\s*563\b", re.I),  "MPC563"),
    (re.compile(r"MPC\s*5567", re.I),   "MPC5567"),
    (re.compile(r"ST\s*10\s*F?\s*275", re.I), "ST10F275"),
    (re.compile(r"SH\s*7058", re.I),    "SH7058"),
    (re.compile(r"SH\s*72531", re.I),   "SH72531"),
    (re.compile(r"RH[\-\s]*850", re.I), "RH850"),
    (re.compile(r"CORTEX[\-\s]*R5", re.I), "Cortex-R5"),
    (re.compile(r"CORTEX[\-\s]*M7", re.I), "Cortex-M7"),
    (re.compile(r"(?:SAK\s*)?C\s*166", re.I), "C166"),
    (re.compile(r"V[\-\s]*850", re.I),  "V850"),
]

_VECTOR_BASES: Dict[str, List[int]] = {
    "TC1766": [0x80000000], "TC1767": [0x80000000],
    "TC1797": [0x80000000], "TC377":  [0x80000000],
    "MPC5634": [0x00000000], "MPC563":  [0x00000000],
    "MPC5567": [0x00000000],
    "ST10F275": [0x00000000],
    "SH7058":  [0x00000000], "SH72531": [0x00000000],
    "RH850":   [0x00000000, 0x00100000],
    "Cortex-R5": [0x00000000, 0xFFFF0000],
    "Cortex-M7": [0x00000000, 0x08000000],
    "C166":    [0x00000000, 0x00200000],
    "V850":    [0x00000000, 0x00100000],
}

_MEM_REG_ADDRS: Dict[str, List[int]] = {
    "TC1766":  [0xF0200000], "TC1767":  [0xF0200000],
    "TC1797":  [0xF0200000], "TC377":   [0xF0200000],
    "MPC5634": [0xFFF40000], "MPC563":  [0xFFF40000],
    "MPC5567": [0xFFF40000],
    "SH7058":  [0xFFFFF000], "SH72531": [0xFFFFF000],
    "RH850":   [0xFFF00000],
    "C166":    [0xFF0000],
    "V850":    [0xFFF80000],
}


def _score_names(data: bytes, limit: int) -> Dict[str, Tuple[float, List[str]]]:
    out: Dict[str, Tuple[float, List[str]]] = {}
    for offset, text in find_ascii_strings(data, min_length=3, max_offset=limit):
        for regex, key in _NAME_PATTERNS:
            if regex.search(text):
                ev = "Name '%s' at 0x%X" % (text.strip(), offset)
                old = out.get(key)
                if old:
                    out[key] = (old[0] + 0.35, old[1] + [ev])
                else:
                    out[key] = (0.35, [ev])
                break
    return out


def _score_vectors(data: bytes) -> Dict[str, Tuple[float, List[str]]]:
    out: Dict[str, Tuple[float, List[str]]] = {}
    for key, bases in _VECTOR_BASES.items():
        for base in bases:
            if base + 64 > len(data):
                continue
            first = read_uint32_be(data, base)
            if first == 0:
                continue
            upper = (first >> 24) & 0xFF
            if not (0x20 <= upper <= 0xFF):
                continue
            non_null = sum(
                1 for i in range(0, 64, 4)
                if base + i + 4 <= len(data) and read_uint32_be(data, base + i) != 0
            )
            ratio = non_null / 16.0
            if ratio < 0.3:
                continue
            score = 0.20 + 0.15 * min(ratio, 1.0)
            ev = "Vector table at 0x%08X (%d/16 non-null)" % (base, non_null)
            old = out.get(key)
            if old:
                out[key] = (old[0] + score, old[1] + [ev])
            else:
                out[key] = (score, [ev])
    return out


def _score_memmap(data: bytes, limit: int) -> Dict[str, Tuple[float, List[str]]]:
    out: Dict[str, Tuple[float, List[str]]] = {}
    for key, addrs in _MEM_REG_ADDRS.items():
        for addr in addrs:
            pattern = struct.pack(">I", addr)
            hits = find_binary_pattern(data, pattern, start=0, end=limit)
            if not hits:
                continue
            score = 0.10 * min(len(hits), 5)
            ev = "Reg 0x%08X found %d time(s)" % (addr, len(hits))
            old = out.get(key)
            if old:
                out[key] = (old[0] + score, old[1] + [ev])
            else:
                out[key] = (score, [ev])
    return out


def _merge(
    *dicts: Dict[str, Tuple[float, List[str]]]
) -> Dict[str, Tuple[float, List[str]]]:
    merged: Dict[str, Tuple[float, List[str]]] = {}
    for d in dicts:
        for k, (sc, ev) in d.items():
            old = merged.get(k)
            if old:
                merged[k] = (old[0] + sc, old[1] + ev)
            else:
                merged[k] = (sc, list(ev))
    return merged


# ==============================================================
#  PUBLIC API
# ==============================================================

def identify_processor(data: bytes) -> ProcessorResult:
    """Identify the target processor from a raw binary dump."""
    logger.info("Starting processor identification (%d bytes)", len(data))

    if not data:
        return ProcessorResult(detected=False, explanation="Empty data buffer")

    limit = min(len(data), 1024 * 1024)

    merged = _merge(
        _score_names(data, limit),
        _score_vectors(data),
        _score_memmap(data, limit),
    )

    if not merged:
        return ProcessorResult(
            detected=False, explanation="No recognizable processor signature found")

    ranked = sorted(merged.items(), key=lambda kv: kv[1][0], reverse=True)
    best_key, (best_score, best_ev) = ranked[0]
    best = PROCESSOR_DATABASE[best_key]
    confidence = min(best_score / 1.5, 1.0)

    alts = [
        PROCESSOR_DATABASE[k] for k, (s, _) in ranked[1:4] if s >= 0.10
    ]

    explanation = "Identified %s (%s), score %.2f" % (
        best.core, best.manufacturer, best_score)
    if alts:
        explanation += ", alts: %s" % ", ".join(a.core for a in alts)

    logger.info("Identified %s (confidence=%.2f)", best.core, confidence)

    return ProcessorResult(
        detected=True, primary=best, alternatives=alts,
        evidence=best_ev, confidence=confidence, explanation=explanation,
    )
