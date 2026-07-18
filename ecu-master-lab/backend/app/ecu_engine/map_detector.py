"""
Layer 7 — Détection de cartographies (calibration maps) dans un dump ECU.
Scan des régions de calibration pour blocs tabulaires (1D/2D).
Aucune dépendance externe — stdlib Python 3.8 uniquement.
"""

import logging
import struct
from typing import Dict, List, Optional, Tuple

from .models import DetectedMap, MapDataType, MapDetectionResult
from .utils import (
    compute_entropy,
    is_likely_data_region,
    read_uint16_be,
    read_uint16_le,
    read_uint8,
)

log = logging.getLogger("ecu_engine.maps")

MAP_HEURISTICS: List[Dict[str, object]] = [
    {"name": "Couple moteur", "category": "couple",
     "typical_sizes": [(16, 16), (32, 32), (8, 16), (16, 8)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "torque,couple,Nm,rpm"},
    {"name": "Carte turbo", "category": "turbo",
     "typical_sizes": [(16, 16), (8, 16), (16, 8)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "turbo,boost,pressure"},
    {"name": "Injection durée", "category": "injection",
     "typical_sizes": [(16, 16), (32, 16), (16, 32)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "injection,duration,temps"},
    {"name": "Pression rail", "category": "rail",
     "typical_sizes": [(16, 8), (8, 16), (16, 16)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "rail,pressure,common"},
    {"name": "Lambda / Sonde O2", "category": "lambda",
     "typical_sizes": [(16, 16), (8, 8), (16, 8)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.FLOAT32],
     "search_hints": "lambda,o2,stoich,afr"},
    {"name": "Position pédale", "category": "pedale",
     "typical_sizes": [(16, 8), (8, 16)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "pedal,pedale,throttle"},
    {"name": "Fumées / EGR", "category": "fumee",
     "typical_sizes": [(16, 16), (8, 16)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "smoke,fumee,egr"},
    {"name": "Température", "category": "temperature",
     "typical_sizes": [(16, 8), (8, 8), (16, 16)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.INT16],
     "search_hints": "temperature,coolant,air,egt"},
    {"name": "Avance allumage", "category": "avance",
     "typical_sizes": [(16, 16), (32, 16)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.INT16],
     "search_hints": "timing,avance,ignition"},
    {"name": "Pression admission", "category": "pression",
     "typical_sizes": [(16, 16), (8, 16), (16, 8)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "map,manifold,boost"},
    {"name": "Vitesse véhicule", "category": "vitesse",
     "typical_sizes": [(8, 8), (16, 8)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "speed,vitesse,kph"},
    {"name": "Régime moteur", "category": "regime",
     "typical_sizes": [(16, 8), (32, 1)],
     "typical_data_types": [MapDataType.UINT16, MapDataType.UINT8],
     "search_hints": "rpm,régime,idle"},
]

BLOCK_SIZES = [256, 512, 1024, 2048, 4096]
KNOWN_OFFSETS: Dict[str, List[int]] = {
    "bosch_edc17": [0x10000, 0x18000, 0x20000, 0x28000, 0x30000],
    "bosch_edc16": [0x08000, 0x10000, 0x18000],
    "bosch_me7":   [0x08000, 0x10000, 0x18000, 0x20000],
    "siemens_sid": [0x08000, 0x10000, 0x18000],
    "delphi_dcm":  [0x10000, 0x20000, 0x30000],
    "denso":       [0x08000, 0x10000, 0x18000],
}


# ── Helpers ────────────────────────────────────────────────────

def _read_values(data: bytes, off: int, count: int, dt: MapDataType) -> List[float]:
    out: List[float] = []
    for i in range(count):
        if dt == MapDataType.UINT8:
            out.append(float(read_uint8(data, off + i)))
        elif dt == MapDataType.UINT16:
            b = off + i * 2
            out.append(float(read_uint16_le(data, b)) if b + 2 <= len(data) else 0.0)
        elif dt == MapDataType.INT16:
            b = off + i * 2
            out.append(float(struct.unpack_from("<h", data, b)[0]) if b + 2 <= len(data) else 0.0)
        else:
            out.append(float(read_uint8(data, off + i)))
    return out


def _stats(vals: List[float]) -> Tuple[float, float, float]:
    if not vals:
        return 0.0, 0.0, 0.0
    return min(vals), max(vals), sum(vals) / len(vals)


def _ne_ratio(vals: List[float]) -> float:
    return sum(1 for v in vals if v != 0.0) / len(vals) if vals else 0.0


def _variance(v: List[float]) -> float:
    if len(v) < 2:
        return 0.0
    m = sum(v) / len(v)
    return sum((x - m) ** 2 for x in v) / len(v)


def _classify(ent: float, ne: float) -> str:
    if ne >= 0.10 and ent >= 0.02:
        return "active"
    return "sparse" if ne >= 0.01 else "empty"


def _pick_dt(size: int) -> MapDataType:
    return MapDataType.UINT16 if size % 2 == 0 else MapDataType.UINT8


def _match_heuristic(rows: int, cols: int, dt: MapDataType) -> Optional[Dict[str, object]]:
    for h in MAP_HEURISTICS:
        for r, c in h["typical_sizes"]:  # type: ignore
            if (rows == r and cols == c) or (rows == c and cols == r):
                if dt in h["typical_data_types"]:
                    return h
    for h in MAP_HEURISTICS:
        for r, c in h["typical_sizes"]:  # type: ignore
            if (rows == r and cols == c) or (rows == c and cols == r):
                return h
    return None


def _best_dims(data: bytes, off: int, bsz: int, dt: MapDataType) -> Tuple[int, int]:
    best_r, best_c, best_s = 1, bsz, -1.0
    candidates = [r for r in range(2, min(bsz, 32) + 1) if bsz % r == 0]
    for rows in candidates[:20]:
        cols = bsz // rows
        if cols < 1 or cols > 64:
            continue
        if cols < 1 or cols > 64:
            continue
        stride = cols if dt == MapDataType.UINT8 else cols * 2
        if rows * stride > bsz:
            continue
        totals = []
        for r in range(rows):
            rv = _read_values(data, off + r * stride, cols, dt)
            totals.append(sum(rv))
        nv = _variance(totals)
        mv = sum(totals) / len(totals) if totals else 1.0
        sc = nv / (abs(mv) + 1e-9)
        if sc > best_s and rows <= 32:
            best_s, best_r, best_c = sc, rows, cols
    return best_r, best_c


def _make_map(
    data: bytes, off: int, bsz: int, rows: int, cols: int,
    dt: MapDataType, method: str, family: str = "",
) -> DetectedMap:
    tv = rows * cols
    bc = tv * 2 if dt == MapDataType.UINT16 else tv
    bc = min(bc, bsz)
    vals = _read_values(data, off, tv, dt)
    vmin, vmax, avg = _stats(vals)
    ne = _ne_ratio(vals)
    ent = compute_entropy(data[off:off + bc])
    status = _classify(ent, ne)
    h = _match_heuristic(rows, cols, dt)
    name = (str(h["name"]) if h else ("Carte %s" % family)) if family else (str(h["name"]) if h else "Bloc données")
    cat = str(h["category"]) if h else "unknown"
    return DetectedMap(
        name=name, category=cat, offset=off, size=bc,
        rows=rows, cols=cols, data_type=dt,
        min_value=vmin, max_value=vmax, avg_value=avg,
        entropy=ent, non_empty_ratio=ne, status=status,
        detection_method=method,
        explanation="%s %dx%d, %s, %.0f%% non-vide" % (method, rows, cols, dt.value, ne * 100),
    )


# ── Méthode 1 : Scan blocs taille fixe ────────────────────────

def _scan_fixed(data: bytes, start: int, size: int) -> List[DetectedMap]:
    found: List[DetectedMap] = []
    seen: set = set()
    end_lim = min(start + size, len(data))
    scan_limit = min(end_lim, start + 262144)

    for bsz in BLOCK_SIZES:
        step = max(bsz, 2048)
        off = start
        while off + bsz <= scan_limit:
            if off in seen:
                off += step
                continue
            blk = data[off:off + bsz]
            ne = _ne_ratio(list(blk[:64]))
            if ne < 0.01:
                off += step
                continue
            ent = compute_entropy(blk)
            if ent < 0.01:
                off += step
                continue

            for dt in (MapDataType.UINT8, MapDataType.UINT16):
                rows, cols = _best_dims(data, off, bsz, dt)
                bc = rows * cols * (2 if dt == MapDataType.UINT16 else 1)
                if bc > bsz:
                    off += step
                    continue
                dm = _make_map(data, off, bsz, rows, cols, dt, "fixed_block_scan")
                if dm.non_empty_ratio >= 0.01:
                    found.append(dm)
                    seen.add(off)
                break
            off += step
    return found


# ── Méthode 2 : Détection 1D (séquences monotones) ───────────

def _scan_1d(data: bytes, start: int, size: int) -> List[DetectedMap]:
    found: List[DetectedMap] = []
    end_lim = min(start + size, len(data))
    scan_limit = min(end_lim, start + 65536)

    for dt in (MapDataType.UINT8, MapDataType.UINT16):
        esz = 1 if dt == MapDataType.UINT8 else 2
        off = start
        while off + 4 * esz <= scan_limit:
            window_end = min(off + 4096, scan_limit)
            si, sd, seq_s = 0, 0, off
            idx = off
            while idx + 2 * esz <= window_end:
                v = read_uint8(data, idx) if dt == MapDataType.UINT8 else read_uint16_le(data, idx)
                ni = idx + esz
                nv = read_uint8(data, ni) if dt == MapDataType.UINT8 else read_uint16_le(data, ni)
                if v < nv:
                    si += 1
                    sd = 0
                elif v > nv:
                    sd += 1
                    si = 0
                else:
                    si = sd = 0
                if si >= 4 or sd >= 4:
                    seq_e = ni + esz
                    seq_len = seq_e - seq_s
                    if 8 <= seq_len <= 2048:
                        tv = seq_len // esz
                        vals = _read_values(data, seq_s, tv, dt)
                        vmin, vmax, avg = _stats(vals)
                        ne = _ne_ratio(vals)
                        ent = compute_entropy(data[seq_s:seq_e])
                        dm = DetectedMap(
                            name="Carte 1D (sequence monotone)", category="unknown",
                            offset=seq_s, size=seq_len, rows=1, cols=tv, data_type=dt,
                            min_value=vmin, max_value=vmax, avg_value=avg,
                            entropy=ent, non_empty_ratio=ne, status=_classify(ent, ne),
                            detection_method="heuristic_1d",
                            explanation="Sequence monotone %d elements (%s)" % (tv, dt.value),
                        )
                        found.append(dm)
                    si = sd = 0
                    off = seq_e
                    break
                idx += esz
            else:
                off = window_end
                continue
            if si < 4 and sd < 4:
                off = max(off + 2048, off + esz)
    return found


# ── Méthode 3 : Scan offsets connus ───────────────────────────

def _scan_known(data: bytes, region_size: int) -> List[DetectedMap]:
    found: List[DetectedMap] = []
    seen: set = set()

    for family, offsets in KNOWN_OFFSETS.items():
        for base in offsets:
            if base + 256 > len(data) or base in seen:
                continue
            for bsz in (256, 512, 1024):
                if base + bsz > len(data) or base in seen:
                    continue
                blk = data[base:base + bsz]
                ent = compute_entropy(blk)
                ne = _ne_ratio(list(blk))
                if ent < 0.01 or ne < 0.01:
                    continue
                dt = _pick_dt(bsz)
                rows, cols = _best_dims(data, base, bsz, dt)
                bc = rows * cols * (2 if dt == MapDataType.UINT16 else 1)
                if bc > bsz:
                    continue
                dm = _make_map(data, base, bsz, rows, cols, dt, "known_offset_%s" % family, family)
                if dm.non_empty_ratio >= 0.01:
                    found.append(dm)
                    seen.add(base)
                break
    return found


# ── Déduplication & Scoring ───────────────────────────────────

def _dedup(maps: List[DetectedMap]) -> List[DetectedMap]:
    if not maps:
        return []
    sm = sorted(maps, key=lambda m: (m.offset, -m.size))
    res: List[DetectedMap] = []
    for dm in sm:
        ov = False
        for ex in res:
            if dm.offset < ex.offset + ex.size and ex.offset < dm.offset + dm.size:
                ov = True
                if dm.entropy > ex.entropy:
                    res.remove(ex)
                    res.append(dm)
                break
        if not ov:
            res.append(dm)
    res.sort(key=lambda m: m.offset)
    return res


def _confidence(maps: List[DetectedMap]) -> float:
    if not maps:
        return 0.0
    sc = min(len(maps) / 5.0, 1.0) * 0.3
    act = sum(1 for m in maps if m.status == "active")
    if maps:
        sc += (act / len(maps)) * 0.25
    ents = [m.entropy for m in maps if m.status == "active"]
    if ents:
        sc += min((sum(ents) / len(ents)) * 2.0, 0.25)
    for dm in maps:
        if dm.non_empty_ratio > 0.5:
            sc += 0.05
        if dm.rows >= 4 and dm.cols >= 4:
            sc += 0.05
    return round(min(sc, 1.0), 3)


# ── API principale ────────────────────────────────────────────

def detect_maps(
    data: bytes, calibration_offset: int = 0, calibration_size: int = 0
) -> MapDetectionResult:
    """Détecte les cartographies de calibration dans un dump ECU."""
    log.info("Début détection cartographies, taille=%d, offset_cal=0x%X",
             len(data), calibration_offset)

    if not data:
        return MapDetectionResult(
            maps=[], total_map_bytes=0, total_maps_found=0,
            confidence=0.0, explanation="Données vides")

    start = calibration_offset
    sz = calibration_size if calibration_size > 0 else len(data) - start
    sz = min(sz, len(data) - start)

    all_maps: List[DetectedMap] = []

    log.info("Méthode 1 — blocs taille fixe")
    all_maps.extend(_scan_fixed(data, start, sz))
    log.info("Méthode 2 — heuristique 1D")
    all_maps.extend(_scan_1d(data, start, sz))
    log.info("Méthode 3 — offsets connus")
    all_maps.extend(_scan_known(data, sz))

    all_maps = _dedup(all_maps)
    total_bytes = sum(m.size for m in all_maps)
    conf = _confidence(all_maps)
    active = sum(1 for m in all_maps if m.status == "active")
    sparse = sum(1 for m in all_maps if m.status == "sparse")
    empty = sum(1 for m in all_maps if m.status == "empty")

    expl = "%d cartes | %d octets | %.1f%% confiance | act=%d sp=%d vides=%d" % (
        len(all_maps), total_bytes, conf * 100, active, sparse, empty)
    log.info(expl)

    return MapDetectionResult(
        maps=all_maps, total_map_bytes=total_bytes,
        total_maps_found=len(all_maps), confidence=conf, explanation=expl)
