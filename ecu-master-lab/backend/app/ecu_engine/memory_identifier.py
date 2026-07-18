"""
Couche 3 - Identification de la disposition memoire ECU.

Analyse la structure physique de la memoire: regions Flash, EEPROM,
OTP, RAM, et estime les largeurs de bus adresse/donnee.
"""

import logging
from typing import List, Optional

from .models import MemoryType, MemoryRegion, MemoryLayout, ProcessorProfile
from .utils import detect_null_fill, detect_ff_fill, block_entropy

logger = logging.getLogger(__name__)

_BLOCK_SIZE = 256
_MAX_BLOCKS = 512
_EEPROM_MAX_SIZE = 65536
_EEPROM_MIN_SIZE = 16
_EEPROM_MAX_ENTROPY = 0.40
_EEPROM_SEARCH_END_RATIO = 0.10
_OTP_FF_THRESHOLD = 0.85
_OTP_NULL_THRESHOLD = 0.85
_OTP_MAX_ENTROPY = 0.15
_RAM_MIN_ENTROPY = 0.60
_RAM_MIN_UNIQUE = 40
_RAM_MIN_NON_EMPTY = 0.40
_FLASH_MIN_NON_EMPTY = 0.30
_FLASH_MIN_ENTROPY = 0.25
_MIN_REGION_SIZE = 64


def _estimate_address_bus(file_size: int) -> int:
    if file_size < 0x10000:
        return 16
    if file_size < 0x100000:
        return 20
    if file_size < 0x1000000:
        return 24
    return 32

def _estimate_data_bus(processor: Optional[ProcessorProfile]) -> int:
    if processor is None:
        return 0
    if processor.word_size in (8, 16, 32):
        return processor.word_size
    if processor.family is not None:
        name = processor.family.value
        if "166" in name or "V850" in name:
            return 16
        if "Tricore" in name or "ARM" in name or "RH850" in name:
            return 32
    return 0

def _non_empty_ratio(data: bytes, start: int, end: int) -> float:
    total = end - start
    if total <= 0:
        return 0.0
    count = 0
    for i in range(start, end):
        if data[i] not in (0x00, 0xFF):
            count += 1
    return count / total


def _unique_byte_count(data: bytes, start: int, end: int) -> int:
    unique = set()
    limit = min(end, start + 8192)
    for i in range(start, limit):
        unique.add(data[i])
    return len(unique)

def _is_otp(data: bytes, s: int, e: int, ent: float) -> bool:
    if e - s < _MIN_REGION_SIZE:
        return False
    if ent >= _OTP_MAX_ENTROPY:
        return False
    if detect_ff_fill(data, s, e - s) >= _OTP_FF_THRESHOLD:
        return True
    if detect_null_fill(data, s, e - s) >= _OTP_NULL_THRESHOLD:
        return True
    return False


def _is_eeprom(data: bytes, s: int, e: int, fsz: int, ent: float) -> bool:
    sz = e - s
    if sz < _EEPROM_MIN_SIZE or sz > _EEPROM_MAX_SIZE:
        return False
    if ent > _EEPROM_MAX_ENTROPY:
        return False
    return s >= int(fsz * (1.0 - _EEPROM_SEARCH_END_RATIO))


def _is_flash(data: bytes, s: int, e: int, ent: float) -> bool:
    if e - s < _MIN_REGION_SIZE:
        return False
    if ent < _FLASH_MIN_ENTROPY:
        return False
    return _non_empty_ratio(data, s, e) >= _FLASH_MIN_NON_EMPTY


def _is_ram(data: bytes, s: int, e: int, ent: float) -> bool:
    if e - s < _MIN_REGION_SIZE:
        return False
    if ent < _RAM_MIN_ENTROPY:
        return False
    if _unique_byte_count(data, s, e) < _RAM_MIN_UNIQUE:
        return False
    return _non_empty_ratio(data, s, e) >= _RAM_MIN_NON_EMPTY


def _scan_blocks(data: bytes) -> List[dict]:
    entropies = block_entropy(data, _BLOCK_SIZE, _MAX_BLOCKS)
    results = []
    for idx, ent in enumerate(entropies):
        start = idx * _BLOCK_SIZE
        end = min(start + _BLOCK_SIZE, len(data))
        results.append({
            "start": start, "end": end,
            "entropy": ent, "type": MemoryType.UNKNOWN,
        })
    return results


def _merge_adjacent(blocks: List[dict]) -> List[dict]:
    if not blocks:
        return []
    merged = [dict(blocks[0])]
    for b in blocks[1:]:
        last = merged[-1]
        if b["type"] == last["type"] and b["start"] == last["end"]:
            prev_sz = last["end"] - last["start"]
            cur_sz = b["end"] - b["start"]
            new_sz = prev_sz + cur_sz
            if new_sz > 0:
                last["entropy"] = (
                    last["entropy"] * prev_sz + b["entropy"] * cur_sz
                ) / new_sz
            last["end"] = b["end"]
        else:
            merged.append(dict(b))
    return merged


def _classify(data: bytes, blocks: List[dict], fsz: int) -> List[dict]:
    for b in blocks:
        s, e, ent = b["start"], b["end"], b["entropy"]
        if _is_otp(data, s, e, ent):
            b["type"] = MemoryType.OTP
        elif _is_eeprom(data, s, e, fsz, ent):
            b["type"] = MemoryType.EEPROM
        elif _is_flash(data, s, e, ent):
            b["type"] = MemoryType.FLASH
        elif _is_ram(data, s, e, ent):
            b["type"] = MemoryType.RAM
    return blocks


def _region_desc(mt: MemoryType, s: int, e: int, ent: float) -> str:
    kb = (e - s) / 1024.0
    if mt == MemoryType.FLASH:
        return "Flash: code/calibration, entropie %.2f, %.1f Ko" % (ent, kb)
    if mt == MemoryType.EEPROM:
        return "EEPROM: parametrage, %d octets" % (e - s,)
    if mt == MemoryType.OTP:
        return "OTP: programmation unique, %.1f Ko" % (kb,)
    if mt == MemoryType.RAM:
        return "RAM: donnees volatiles, %.1f Ko" % (kb,)
    return "Region inconnue"


def _build_regions(blocks: List[dict]) -> List[MemoryRegion]:
    merged = _merge_adjacent(blocks)
    regions: List[MemoryRegion] = []
    for b in merged:
        if b["type"] == MemoryType.UNKNOWN:
            continue
        sz = b["end"] - b["start"]
        if sz < _MIN_REGION_SIZE:
            continue
        regions.append(MemoryRegion(
            mem_type=b["type"],
            start_address=b["start"],
            end_address=b["end"],
            size=sz,
            description=_region_desc(b["type"], b["start"], b["end"], b["entropy"]),
        ))
    return regions


def _confidence(regions: List[MemoryRegion], fsz: int) -> float:
    if not regions:
        return 0.0
    score = 0.3
    types = {r.mem_type for r in regions}
    if MemoryType.FLASH in types:
        score += 0.3
    if MemoryType.EEPROM in types:
        score += 0.15
    if MemoryType.OTP in types:
        score += 0.1
    covered = sum(r.size for r in regions)
    coverage = covered / fsz if fsz > 0 else 0.0
    score += min(coverage, 1.0) * 0.15
    return min(score, 1.0)


def _build_explanation(
    regions: List[MemoryRegion], addr: int, data_bus: int, conf: float,
) -> str:
    lines = ["Memoire: %d region(s) detectee(s)." % len(regions)]
    counts: dict = {}
    for r in regions:
        counts[r.mem_type] = counts.get(r.mem_type, 0) + 1
    for mt, cnt in counts.items():
        lines.append("  - %s: %d" % (mt.value, cnt))
    lines.append("Bus adresse: %d bits" % addr)
    if data_bus > 0:
        lines.append("Bus donnees: %d bits" % data_bus)
    else:
        lines.append("Bus donnees: indisponible")
    lines.append("Confiance: %.2f" % conf)
    return "\n".join(lines)


def identify_memory(
    data: bytes,
    processor: Optional[ProcessorProfile] = None,
) -> MemoryLayout:
    logger.info("Debut identification memoire (%d octets)", len(data))
    fsz = len(data)
    addr_bus = _estimate_address_bus(fsz)
    data_bus = _estimate_data_bus(processor)
    blocks = _scan_blocks(data)
    blocks = _classify(data, blocks, fsz)
    regions = _build_regions(blocks)
    conf = _confidence(regions, fsz)
    explanation = _build_explanation(regions, addr_bus, data_bus, conf)
    logger.info(
        "Identification terminee: %d regions, confiance=%.2f",
        len(regions), conf,
    )
    return MemoryLayout(
        regions=regions,
        total_size=fsz,
        address_bus_width=addr_bus,
        data_bus_width=data_bus,
        explanation=explanation,
        confidence=conf,
    )
