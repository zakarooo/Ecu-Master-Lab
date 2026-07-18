"""
Couche 6 : Analyse des segments memoire.

Divise le binaire ECU en segments logiques (Boot, Code, Calibration, EEPROM)
et valide leur coherence structurelle.
"""

import logging
from typing import List, Optional, Tuple

from .models import (
    MemoryLayout,
    SegmentAnalysis,
    SegmentAnalysisResult,
    SegmentType,
)
from .utils import (
    compute_entropy,
    detect_ff_fill,
    detect_null_fill,
    find_ascii_strings,
)

logger = logging.getLogger("ecu_engine.segment")

_BOOT_SIZE_MIN = 4096
_BOOT_SIZE_MAX = 65536
_EEPROM_MAX_SIZE = 65536
_EEPROM_PATTERN_WINDOW = 64
_CAL_MAP_WINDOW = 1024


def _count_unique(data: bytes) -> int:
    return len(set(data))


def _non_empty_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(1 for b in data if b not in (0x00, 0xFF)) / len(data)


def _detect_patterns(data: bytes) -> List[str]:
    patterns: List[str] = []
    if not data:
        return patterns
    null_r = detect_null_fill(data, 0, len(data))
    ff_r = detect_ff_fill(data, 0, len(data))
    if null_r > 0.8:
        patterns.append("null_fill_over_80pct")
    elif null_r > 0.5:
        patterns.append("null_fill_over_50pct")
    if ff_r > 0.8:
        patterns.append("ff_fill_over_80pct")
    elif ff_r > 0.5:
        patterns.append("ff_fill_over_50pct")
    ascii_strs = find_ascii_strings(data, min_length=6, max_offset=min(len(data), 8192))
    if ascii_strs:
        patterns.append("ascii_strings_%d" % len(ascii_strs))
    unique = _count_unique(data)
    if unique < 10:
        patterns.append("low_unique_bytes_%d" % unique)
    elif unique > 200:
        patterns.append("high_byte_diversity_%d" % unique)
    ent = compute_entropy(data)
    if ent < 0.3:
        patterns.append("very_low_entropy")
    elif ent > 0.85:
        patterns.append("high_entropy")
    return patterns


def _make_segment(
    seg_type: SegmentType, start: int, end: int,
    data: bytes, explanation: str, is_valid: bool,
) -> SegmentAnalysis:
    chunk = data[start:end]
    return SegmentAnalysis(
        seg_type=seg_type, start_offset=start, end_offset=end,
        size=end - start, entropy=compute_entropy(chunk),
        non_empty_ratio=_non_empty_ratio(chunk),
        unique_byte_count=_count_unique(chunk),
        data_patterns=_detect_patterns(chunk),
        is_valid=is_valid, explanation=explanation,
    )


def _detect_boot(data: bytes) -> Optional[Tuple[int, int]]:
    size = len(data)
    if size < _BOOT_SIZE_MIN:
        return None
    boot_end = min(_BOOT_SIZE_MAX, size)
    chunk = data[:boot_end]
    ent = compute_entropy(chunk)
    ascii_strs = find_ascii_strings(chunk, min_length=4, max_offset=2048)
    has_vectors = False
    for i in range(0, min(len(chunk), 256), 4):
        if len(chunk) < i + 4:
            break
        val = int.from_bytes(chunk[i:i + 4], "big")
        if 0x00000100 <= val <= 0x00FFFFFF:
            has_vectors = True
            break
    null_r = detect_null_fill(data, 0, min(256, size))
    ff_r = detect_ff_fill(data, 0, min(256, size))
    score = 0.0
    if has_vectors:
        score += 0.4
    if ent > 0.4:
        score += 0.2
    if null_r < 0.5:
        score += 0.15
    if ascii_strs:
        score += 0.15
    if ff_r < 0.5:
        score += 0.1
    if score >= 0.3:
        return (0, boot_end)
    return None


def _detect_eeprom(data: bytes, offset: int) -> Optional[Tuple[int, int]]:
    remaining = data[offset:]
    window = min(len(remaining), _EEPROM_MAX_SIZE)
    if window < 64:
        return None
    seg = remaining[:window]
    ent = compute_entropy(seg)
    ff_r = detect_ff_fill(remaining, 0, window)
    null_r = detect_null_fill(remaining, 0, window)
    has_pattern = False
    for i in range(0, min(len(seg) - _EEPROM_PATTERN_WINDOW, 4096), _EEPROM_PATTERN_WINDOW):
        block_ff = detect_ff_fill(seg, i, _EEPROM_PATTERN_WINDOW)
        block_null = detect_null_fill(seg, i, _EEPROM_PATTERN_WINDOW)
        if block_ff > 0.6 or block_null > 0.6:
            has_pattern = True
            break
    if ff_r > 0.7 and ent < 0.3 and has_pattern:
        return (offset, offset + window)
    if null_r > 0.7 and ent < 0.25:
        return (offset, offset + window)
    return None


def _detect_calibration(data: bytes, start: int, end: int) -> bool:
    size = end - start
    if size <= 0:
        return False
    chunk = data[start:end]
    ent = compute_entropy(chunk)
    if ent > 0.80 or ent < 0.10:
        return False
    structured = 0
    window = max(min(_CAL_MAP_WINDOW, size // 4), 16)
    step = max(window, 256)
    for i in range(0, size, step):
        block = chunk[i:i + window]
        if not block:
            continue
        b_ent = compute_entropy(block)
        if 0.15 < b_ent < 0.75:
            structured += 1
    if structured >= max(1, size // step) * 0.5:
        return True
    ff_ratio = detect_ff_fill(data, start, size)
    if 0.1 < ff_ratio < 0.7 and ent < 0.65:
        return True
    if ent < 0.55 and _non_empty_ratio(chunk) > 0.15:
        return True
    return False


def analyze_segments(
    data: bytes,
    memory_layout: Optional[MemoryLayout] = None,
) -> SegmentAnalysisResult:
    segments: List[SegmentAnalysis] = []
    explanations: List[str] = []
    size = len(data)
    if size == 0:
        return SegmentAnalysisResult(
            coherence_score=0.0,
            explanation="Empty binary, no segments to analyze.",
        )

    # Phase 1: boot detection
    boot = _detect_boot(data)
    if boot:
        seg = _make_segment(
            SegmentType.BOOT, boot[0], boot[1], data,
            "Boot segment: interrupt vectors or bootloader code.", True,
        )
        segments.append(seg)
        explanations.append(
            "Boot [0x%X-0x%X] (%d bytes, entropy %.3f)"
            % (boot[0], boot[1], boot[1] - boot[0], seg.entropy)
        )
    else:
        explanations.append("No boot segment detected at file start.")

    # Phase 2: EEPROM detection
    eeprom = _detect_eeprom(data, 0)
    if eeprom:
        seg = _make_segment(
            SegmentType.EEPROM, eeprom[0], eeprom[1], data,
            "EEPROM segment: high fill patterns, low entropy.", True,
        )
        segments.append(seg)
        explanations.append(
            "EEPROM [0x%X-0x%X] (%d bytes)"
            % (eeprom[0], eeprom[1], eeprom[1] - eeprom[0])
        )

    # Phase 3: code / calibration split
    code_start = boot[1] if boot else 0
    code_end = eeprom[0] if eeprom else size
    remaining = code_end - code_start
    if remaining > 0:
        candidates = [
            (code_start, code_start + remaining // 2),
            (code_start + remaining // 2, code_end),
        ]
        if remaining > 65536:
            third = remaining // 3
            candidates = [
                (code_start, code_start + third),
                (code_start + third, code_start + 2 * third),
                (code_start + 2 * third, code_end),
            ]
        for cs, ce in candidates:
            if ce <= cs:
                continue
            is_cal = _detect_calibration(data, cs, ce)
            if is_cal:
                stype, expl = (SegmentType.CALIBRATION,
                               "Calibration: structured map data, moderate entropy.")
            else:
                stype, expl = (SegmentType.CODE,
                               "Code: high entropy, executable content.")
            seg = _make_segment(stype, cs, ce, data, expl, True)
            segments.append(seg)
            explanations.append(
                "%s [0x%X-0x%X] (%d bytes, entropy %.3f)"
                % (stype.value, cs, ce, ce - cs, seg.entropy)
            )

    # Phase 4: coherence validation
    score = 100.0
    warnings: List[str] = []
    boot_segs = [s for s in segments if s.seg_type == SegmentType.BOOT]
    code_segs = [s for s in segments if s.seg_type == SegmentType.CODE]
    cal_segs = [s for s in segments if s.seg_type == SegmentType.CALIBRATION]

    if boot_segs:
        bs = boot_segs[0]
        if bs.start_offset != 0:
            score -= 10
            warnings.append("Boot does not start at offset 0.")
        if bs.entropy < 0.2:
            score -= 10
            warnings.append("Boot entropy very low.")
    else:
        score -= 5
        warnings.append("No boot segment found.")

    if code_segs:
        cs = code_segs[0]
        if boot_segs and cs.start_offset < boot_segs[0].end_offset:
            score -= 15
            warnings.append("Code overlaps boot.")
        if cs.entropy < 0.5:
            score -= 10
            warnings.append("Code entropy unexpectedly low.")

    for cs in cal_segs:
        for cds in code_segs:
            if cs.start_offset < cds.start_offset:
                score -= 10
                warnings.append(
                    "Calibration at 0x%X precedes code at 0x%X."
                    % (cs.start_offset, cds.start_offset)
                )
                break

    ep_segs = [s for s in segments if s.seg_type == SegmentType.EEPROM]
    if ep_segs and boot_segs and ep_segs[0].start_offset < boot_segs[0].end_offset:
        score -= 10
        warnings.append("EEPROM overlaps boot region.")

    total_bytes = sum(s.size for s in segments)
    if total_bytes > 0 and total_bytes < size * 0.3:
        score -= 10
        warnings.append(
            "Segments cover only %.1f%% of binary." % (total_bytes / size * 100)
        )

    score = max(0.0, min(100.0, score))
    if warnings:
        explanations.append("Warnings: " + "; ".join(warnings))

    total_code = sum(s.size for s in code_segs)
    total_cal = sum(s.size for s in cal_segs)

    logger.info("Segment analysis done: %d segments, coherence %.1f", len(segments), score)

    return SegmentAnalysisResult(
        segments=segments,
        total_code_bytes=total_code,
        total_calibration_bytes=total_cal,
        coherence_score=score,
        explanation=" | ".join(explanations),
    )
