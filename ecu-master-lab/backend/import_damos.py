"""
Fast DAMOS/A2L importer - optimized for large files.

Uses streaming line-by-line parsing instead of splitting on blocks.
Processes all 126 DAMOS folders and imports map definitions.

Usage:
    cd ecu-master-lab/backend
    python import_damos.py
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.database import SessionLocal
from app.models.new.ecu_models import (
    ECUModel,
    Manufacturer,
    KnownMap,
    KnownString,
    MapCategory,
    MapUnit,
    MapAxis,
    KnownSignature,
)


# ===========================================================================
# Configuration
# ===========================================================================

DAMOS_ROOT = r"C:\Users\HOME\Desktop\Damos\DAMOS data\DAMOS"

UNIT_MAPPING = {
    "rpm": "rpm", "deg": "deg", "degC": "degC", "mg/stk": "mg/stk",
    "mg_hub": "mg/stk", "bar": "bar", "mbar": "mbar", "kg/h": "kg/h",
    "km/h": "km/h", "kmh": "km/h", "Nm": "Nm", "ms": "ms", "s": "ms",
    "V": "V", "%": "%", "kPa": "kPa", "l/h": "l/h", "g/s": "g/s",
    "hPa": "kPa", "Temp_Cels": "degC", "Pres_hPa": "kPa", "Vel": "km/h",
    "Acc": "%", "Fact": "%", "Fact1": "%", "Press": "bar",
    "InjQty": "mg/stk", "InjTime": "ms", "IgnAngle": "deg",
    "ThrPos": "%", "Lam": "%", "Pwm": "%", "Curr": "A", "Res": "Ohm",
    "Grad": "deg", "Tques": "Nm", "Pow": "kW", "VolFlow": "l/h",
    "MassFlow": "g/s", "Time": "ms", "Angle": "deg",
}

ECU_NAME_PATTERNS = [
    (r"EDC17[_\s]*CP04", "EDC17 CP04"),
    (r"EDC17[_\s]*CP14", "EDC17 CP14"),
    (r"EDC17[_\s]*CP20", "EDC17 CP14"),
    (r"EDC17[_\s]*CP54", "EDC17 CP54"),
    (r"EDC17[_\s]*C46", "EDC17 C46"),
    (r"EDC17[_\s]*CP02", "EDC17 CP04"),
    (r"EDC17[_\s]*CP09", "EDC17 CP04"),
    (r"EDC16[_\s]*C31", "EDC16"),
    (r"EDC16[_\s]*C35", "EDC16"),
    (r"EDC16[_\s]*CP34", "EDC16"),
    (r"EDC16[_\s]*CP31", "EDC16"),
    (r"EDC16[U\+]", "EDC16"),
    (r"EDC16", "EDC16"),
    (r"EDC15C4", "EDC15"),
    (r"EDC15C6", "EDC15"),
    (r"EDC15C7", "EDC15"),
    (r"EDC15[PVM]", "EDC15"),
    (r"EDC15", "EDC15"),
    (r"EDG15C", "EDC15"),
    (r"MED17[_\s]*4\.2", "MED17.1"),
    (r"MED17[_\s]*1", "MED17.1"),
    (r"MED17", "MED17.1"),
    (r"MED9[_\s]*51", "ME9"),
    (r"MED9[_\s]*1", "ME9"),
    (r"MED9", "ME9"),
    (r"ME9[_\s]*2", "ME9"),
    (r"ME9[_\s]*6", "ME9"),
    (r"ME9", "ME9"),
    (r"ME7[_\s]*5", "ME7"),
    (r"ME7[_\s]*6", "ME7"),
    (r"ME7[_\s]*2", "ME7"),
    (r"ME7[_\s]*1\.1", "ME7"),
    (r"ME7[_\s]*1", "ME7"),
    (r"ME7", "ME7"),
    (r"ME2[_\s]*1", "ME7"),
    (r"ME1[_\s]*5", "ME7"),
    (r"MSD8[05]", "ME7"),
    (r"MS4[35]", "ME7"),
    (r"MSS5[24]", "ME7"),
    (r"M5[_\s]*2", "ME7"),
    (r"M3[_\s]*8", "ME7"),
    (r"M4[_\s]*4", "ME7"),
    (r"SIMOS[_\s]*8", "SIMOS 8"),
    (r"SIMOS[_\s]*3", "SIMOS 3"),
    (r"SID803[A]?", "SID801"),
    (r"SID807", "SID801"),
    (r"SID801", "SID801"),
    (r"SID201", "SID201"),
    (r"PPD1", "SIMOS 8"),
    (r"DCM3", "Multec S"),
    (r"DCM", "Multec S"),
    (r"Multec", "Multec"),
    (r"MJD", "MJD 6JF"),
    (r"IAW", "IAW 4AV"),
    (r"DENSO", "Denso Diesel"),
]


# ===========================================================================
# Fast streaming A2L parser
# ===========================================================================

def parse_a2l_fast(filepath: str) -> List[Dict[str, Any]]:
    """Fast streaming parser - extracts only MAP and CURVE CHARACTERISTICs.
    
    Instead of splitting the entire file (which is slow for 700K lines),
    we stream line-by-line and only collect what we need.
    """
    results = []
    
    with open(filepath, 'r', encoding='latin-1', errors='replace') as f:
        in_characteristic = False
        in_axis = False
        depth = 0
        
        name = desc = ctype = addr = conv = unit = ""
        resolution = 0.0
        lo = hi = 0.0
        axes = []
        
        # Axis temp vars
        ax_type = ax_name = ax_unit = ""
        ax_pts = 0
        ax_lo = ax_hi = 0.0
        
        for line in f:
            line = line.strip()
            
            if not line or line.startswith('//'):
                continue
            
            if '/begin CHARACTERISTIC' in line:
                in_characteristic = True
                depth = 1
                name = desc = ctype = addr = conv = unit = ""
                resolution = 0.0
                lo = hi = 0.0
                axes = []
                field_idx = 0
                continue
            
            if in_characteristic:
                if '/begin AXIS_DESCR' in line:
                    in_axis = True
                    ax_type = ax_name = ax_unit = ""
                    ax_pts = 0
                    ax_lo = ax_hi = 0.0
                    ax_field = 0
                    continue
                
                if in_axis:
                    if '/end AXIS_DESCR' in line:
                        in_axis = False
                        if ax_type and ax_name:
                            axes.append({
                                'axis_type': ax_type,
                                'axis_name': ax_name,
                                'axis_unit': ax_unit,
                                'num_points': ax_pts,
                                'min_value': ax_lo,
                                'max_value': ax_hi,
                            })
                        continue
                    
                    if line.startswith('FORMAT') or line.startswith('EXTENDED_LIMITS') or line.startswith('DEPOSIT'):
                        continue
                    
                    parts = line.split()
                    if ax_field == 0:
                        ax_type = parts[0] if parts else ""
                    elif ax_field == 1:
                        ax_name = parts[0] if parts else ""
                    elif ax_field == 2:
                        ax_unit = parts[0] if parts else ""
                    elif ax_field == 3:
                        try:
                            ax_pts = int(parts[0])
                        except (ValueError, IndexError):
                            pass
                    elif ax_field == 4:
                        try:
                            ax_lo = float(parts[0])
                        except (ValueError, IndexError):
                            pass
                    elif ax_field == 5:
                        try:
                            ax_hi = float(parts[0])
                        except (ValueError, IndexError):
                            pass
                    ax_field += 1
                    continue
                
                if '/end CHARACTERISTIC' in line:
                    in_characteristic = False
                    if ctype in ("MAP", "CURVE") and addr:
                        addr_int = 0
                        try:
                            addr_int = int(addr, 16) if addr.lower().startswith("0x") else int(addr, 16)
                        except (ValueError, TypeError):
                            pass
                        
                        # Calculate rows/cols from axes
                        rows = cols = 0
                        data_type = "uint16"
                        if ctype == "MAP" and len(axes) >= 2:
                            cols = axes[0].get('num_points', 0)
                            rows = axes[1].get('num_points', 0)
                        elif ctype == "CURVE" and len(axes) >= 1:
                            cols = axes[0].get('num_points', 0)
                            rows = 1
                        
                        c = conv.lower()
                        if "s16" in c or "ws16" in c:
                            data_type = "int16"
                        elif "u16" in c or "wu16" in c:
                            data_type = "uint16"
                        elif "s32" in c or "ws32" in c:
                            data_type = "int32"
                        elif "u32" in c or "wu32" in c:
                            data_type = "uint32"
                        elif "f32" in c or "float" in c:
                            data_type = "float32"
                        
                        results.append({
                            'name': name,
                            'description': desc,
                            'char_type': ctype,
                            'address': addr,
                            'address_int': addr_int,
                            'conversion': conv,
                            'unit': unit,
                            'lower_limit': lo,
                            'upper_limit': hi,
                            'rows': rows,
                            'cols': cols,
                            'data_type': data_type,
                            'axes': axes,
                        })
                    continue
            
            # Not in characteristic - skip
            if not in_characteristic:
                continue
            
            # Parse characteristic fields by position
            # Remove inline comments
            if '//' in line:
                line = line[:line.index('//')].strip()
            if '/*' in line:
                line = line[:line.index('/*')].strip()
            if not line:
                continue
            
            if field_idx == 0:
                name = line
            elif field_idx == 1:
                desc = line.strip('"')
            elif field_idx == 2:
                ctype = line
            elif field_idx == 3:
                addr = line
            elif field_idx == 4:
                conv = line
            elif field_idx == 5:
                try:
                    resolution = float(line)
                except ValueError:
                    pass
            elif field_idx == 6:
                unit = line
            elif field_idx == 7:
                try:
                    lo = float(line)
                except ValueError:
                    pass
            elif field_idx == 8:
                try:
                    hi = float(line)
                except ValueError:
                    pass
            
            field_idx += 1
    
    return results


# ===========================================================================
# Helpers
# ===========================================================================

def identify_ecu_model(folder_name: str) -> Optional[str]:
    for pattern, model_name in ECU_NAME_PATTERNS:
        if re.search(pattern, folder_name, re.IGNORECASE):
            return model_name
    return None


def categorize_map(name: str, desc: str) -> str:
    n = name.upper()
    d = desc.upper() if desc else ""
    
    rules = [
        (["INJ", "EINSP", "FUEL", "KRAFT"], "Injection Quantity"),
        (["INJTIME", "EINSZP", "INJ_TIM"], "Injection Timing"),
        (["BOOST", "LAD", "TURBO", "VTG", "WG", "WASTEGATE"], "Boost Pressure"),
        (["RAIL", "RDFP", "COMMON", "DRUCKREG"], "Rail Pressure"),
        (["EGR", "AGR", "ABGAS"], "EGR Control"),
        (["DPF", "FILTR", "PARTIKEL", "SAI"], "DPF Regeneration"),
        (["VMAX", "V_MAX", "SPEED", "GESCHW"], "Speed Limiter"),
        (["TORQUE", "MOMENT", "MOM", "TRQ"], "Torque Limiter"),
        (["IDLE", "LAUF", "LEERGANG", "LL"], "Idle Speed"),
        (["GLOW", "GK", "GLUEH", "VORG"], "Glow Plug"),
        (["FAN", "LUEFTER", "VENT"], "Fan Control"),
        (["SMOKE", "RAUCH", "AIRMASS", "LUFT"], "Smoke Limitation"),
        (["LAMBDA", "LSU", "LAM", "O2"], "Lambda Control"),
        (["THROTTLE", "DRKL", "DROSSEL", "PEDAL"], "Throttle Control"),
        (["SWIRL", "SWI"], "Swirl Flap"),
        (["COLD", "KALT", "KLSTART"], "Cold Start Enrichment"),
        (["ALTITUDE", "HOEHE", "PRESS"], "Altitude Compensation"),
        (["ADBLUE", "SCR", "NOX", "UREA"], "AdBlue Injection"),
        (["CAT", "KAT", "CATALYST"], "Catalyst Heating"),
    ]
    
    for keywords, category in rules:
        if any(kw in n for kw in keywords):
            return category
    
    return "Injection Quantity"


def normalize_unit(a2l_unit: str) -> str:
    if a2l_unit in UNIT_MAPPING:
        return UNIT_MAPPING[a2l_unit]
    for key, val in UNIT_MAPPING.items():
        if key.lower() == a2l_unit.lower():
            return val
    return a2l_unit


# ===========================================================================
# Import logic
# ===========================================================================

def scan_damos_folders(damos_root: str) -> List[Tuple[str, str]]:
    results = []
    for folder_name in sorted(os.listdir(damos_root)):
        folder_path = os.path.join(damos_root, folder_name)
        if not os.path.isdir(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if fname.lower().endswith('.a2l'):
                results.append((folder_name, os.path.join(folder_path, fname)))
                break
    return results


def run_import(damos_root: str = DAMOS_ROOT) -> None:
    session = SessionLocal()
    
    try:
        print("Building caches...")
        ecu_model_cache = {}
        for m in session.query(ECUModel).all():
            ecu_model_cache[m.model_name] = m.id
        
        unit_cache = {}
        for u in session.query(MapUnit).all():
            unit_cache[u.symbol] = u.id
        
        folders = scan_damos_folders(damos_root)
        print(f"Found {len(folders)} A2L files")
        
        total_maps = 0
        total_axes = 0
        total_strings = 0
        matched = 0
        unmatched = []
        
        for i, (folder_name, a2l_path) in enumerate(folders, 1):
            model_name = identify_ecu_model(folder_name)
            ecu_model_id = ecu_model_cache.get(model_name) if model_name else None
            if model_name:
                matched += 1
            else:
                unmatched.append(folder_name)
            
            # Parse A2L
            try:
                chars = parse_a2l_fast(a2l_path)
            except Exception as e:
                print(f"  ERROR: {folder_name}: {e}")
                continue
            
            n_maps = sum(1 for c in chars if c['char_type'] == 'MAP')
            n_curves = sum(1 for c in chars if c['char_type'] == 'CURVE')
            print(f"[{i:3d}/{len(folders)}] {folder_name[:55]:<55s} -> {model_name or '???':<15s} ({n_maps} maps, {n_curves} curves)")
            
            file_maps = 0
            file_axes = 0
            
            for char in chars:
                # Check duplicate
                existing = session.query(KnownMap.id).filter(
                    KnownMap.ecu_model_name == (model_name or folder_name),
                    KnownMap.map_name == char['name'],
                ).first()
                if existing is not None:
                    continue
                
                category = categorize_map(char['name'], char['description'])
                unit_sym = normalize_unit(char['unit'])
                
                row = KnownMap(
                    ecu_model_id=ecu_model_id,
                    ecu_model_name=model_name or folder_name,
                    map_name=char['name'],
                    offset_hex=char['address'],
                    offset_dec=char['address_int'],
                    size_bytes=0,
                    rows=char['rows'],
                    cols=char['cols'],
                    data_type=char['data_type'],
                    category=category,
                    occurrence_count=1,
                    total_known_files=1,
                    confidence=0.90,
                )
                session.add(row)
                file_maps += 1
                
                for j, ax in enumerate(char['axes']):
                    ax_unit_sym = normalize_unit(ax.get('axis_unit', ''))
                    axis_row = MapAxis(
                        name=f"{char['name']}_{'X' if j == 0 else 'Y'}",
                        axis_type="x" if j == 0 else "y",
                        unit_id=unit_cache.get(ax_unit_sym),
                        min_value=ax.get('min_value', 0),
                        max_value=ax.get('max_value', 0),
                        num_points=ax.get('num_points', 0),
                        description=f"{ax.get('axis_type', '')}: {ax.get('axis_name', '')} [{ax.get('axis_unit', '')}]",
                    )
                    session.add(axis_row)
                    file_axes += 1
            
            total_maps += file_maps
            total_axes += file_axes
            
            # Insert top map names as known_strings
            map_names = [c['name'] for c in chars[:15]]
            for mn in map_names:
                existing = session.query(KnownString.id).filter(
                    KnownString.ecu_model_name == (model_name or folder_name),
                    KnownString.string_value == mn,
                ).first()
                if existing is None:
                    session.add(KnownString(
                        ecu_model_id=ecu_model_id,
                        ecu_model_name=model_name or folder_name,
                        string_value=mn,
                        category="calibration_map",
                        occurrence_count=1,
                        total_known_files=1,
                        confidence=0.85,
                    ))
                    total_strings += 1
            
            # Flush every 5 files
            if i % 5 == 0:
                session.flush()
                print(f"  ... flushed ({total_maps} maps, {total_axes} axes so far)")
        
        session.commit()
        
        print("\n" + "=" * 70)
        print("  DAMOS Import Summary")
        print("=" * 70)
        print(f"  A2L files processed:    {len(folders):>5d}")
        print(f"  ECU models matched:     {matched:>5d}")
        print(f"  ECU models unmatched:   {len(unmatched):>5d}")
        if unmatched:
            print(f"  Unmatched folders:")
            for u in unmatched:
                print(f"    - {u}")
        print("-" * 70)
        print(f"  {'Known Maps':<30s}: {total_maps:>6d} inserted")
        print(f"  {'Map Axes':<30s}: {total_axes:>6d} inserted")
        print(f"  {'Known Strings':<30s}: {total_strings:>6d} inserted")
        total = total_maps + total_axes + total_strings
        print(f"  {'TOTAL':<30s}: {total:>6d} new rows")
        print("=" * 70)
        
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Importing DAMOS/A2L data into ECU Master Lab V2 ...")
    run_import()
    print("Done.")
