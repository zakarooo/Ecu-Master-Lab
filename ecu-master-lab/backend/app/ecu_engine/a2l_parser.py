"""
A2L (ASAP2) parser for ECU calibration data.

Parses ASAM MCD-2MC format A2L files to extract:
  - CHARACTERISTICs (MAP, CURVE, VALUE, VAL_BLK, ASCII)
  - AXIS_DESCR (axis type, name, unit, points, min/max)
  - Conversion methods and units

Source: ASAP2 standard v1.4+
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AxisDescription:
    axis_type: str          # STD_AXIS, FIX_AXIS, COM_AXIS, RES_AXIS
    axis_name: str          # e.g., Eng_nAv, VehV_v
    axis_unit: str          # e.g., rpm, km/h, Temp_Cels
    num_points: int = 0
    min_value: float = 0.0
    max_value: float = 0.0


@dataclass
class Characteristic:
    name: str
    description: str
    char_type: str          # MAP, CURVE, VALUE, VAL_BLK, ASCII, CUBOID
    address: str            # hex string e.g., "0x801ABFD0"
    address_int: int = 0    # numeric address
    conversion: str = ""    # conversion method name
    resolution: float = 0.0
    unit: str = ""          # unit name (e.g., rpm, mg/stk, deg)
    lower_limit: float = 0.0
    upper_limit: float = 0.0
    axes: List[AxisDescription] = field(default_factory=list)

    @property
    def num_rows(self) -> Optional[int]:
        if self.char_type == "MAP" and len(self.axes) >= 2:
            return self.axes[1].num_points  # Y axis = rows
        if self.char_type == "CURVE" and len(self.axes) >= 1:
            return 1
        return None

    @property
    def num_cols(self) -> Optional[int]:
        if self.char_type == "MAP" and len(self.axes) >= 2:
            return self.axes[0].num_points  # X axis = cols
        if self.char_type == "CURVE" and len(self.axes) >= 1:
            return self.axes[0].num_points
        return None

    @property
    def data_type(self) -> str:
        c = self.conversion.lower()
        if "s16" in c or "ws16" in c:
            return "int16"
        if "u16" in c or "wu16" in c:
            return "uint16"
        if "s32" in c or "ws32" in c:
            return "int32"
        if "u32" in c or "wu32" in c:
            return "uint32"
        if "f32" in c or "float" in c:
            return "float32"
        if "s8" in c or "ws8" in c:
            return "int8"
        if "u8" in c or "wu8" in c:
            return "uint8"
        return "uint16"  # default


def parse_hex_address(addr_str: str) -> int:
    """Parse hex address string like '0x801ABFD0' to int."""
    addr_str = addr_str.strip()
    if addr_str.lower().startswith("0x"):
        return int(addr_str, 16)
    try:
        return int(addr_str, 16)
    except ValueError:
        return 0


def parse_a2l(content: str) -> List[Characteristic]:
    """Parse A2L content and return list of CHARACTERISTICs.
    
    Handles the ASAP2 v1.4 format used by DAMOS++ and similar tools.
    """
    characteristics = []
    
    # Split on CHARACTERISTIC blocks
    blocks = content.split("/begin CHARACTERISTIC")
    
    for block_raw in blocks[1:]:
        end = block_raw.find("/end CHARACTERISTIC")
        if end == -1:
            continue
        block = block_raw[:end]
        
        # Remove comments
        block = re.sub(r'/\*.*?\*/', '', block, flags=re.DOTALL)
        
        # Split into lines, filter empties and comments
        lines = []
        for line in block.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            lines.append(line)
        
        if len(lines) < 4:
            continue
        
        # Parse header fields
        name = lines[0]
        description = lines[1].strip('"') if len(lines) > 1 else ""
        char_type = lines[2] if len(lines) > 2 else ""
        
        if char_type not in ("MAP", "CURVE", "VALUE", "VAL_BLK", "ASCII", "CUBOID", "VAL_CPP_16", "VAL_CPP_32", "VAL_CPP_8"):
            continue
        
        address = lines[3] if len(lines) > 3 else "0x0"
        conversion = lines[4] if len(lines) > 4 else ""
        
        # Parse resolution and unit (positions vary)
        resolution = 0.0
        unit = ""
        lower_limit = 0.0
        upper_limit = 0.0
        
        # After conversion: resolution, unit, lower, upper
        if len(lines) > 5:
            try:
                resolution = float(lines[5])
            except (ValueError, IndexError):
                pass
        if len(lines) > 6:
            unit = lines[6]
        if len(lines) > 7:
            try:
                lower_limit = float(lines[7])
            except (ValueError, IndexError):
                pass
        if len(lines) > 8:
            try:
                upper_limit = float(lines[8])
            except (ValueError, IndexError):
                pass
        
        # Parse AXIS_DESCR blocks
        axes = []
        axis_blocks = block.split("/begin AXIS_DESCR")
        for ab in axis_blocks[1:]:
            ab_end = ab.find("/end AXIS_DESCR")
            if ab_end == -1:
                continue
            ab = ab[:ab_end]
            al = []
            for line in ab.split('\n'):
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('FORMAT') or line.startswith('EXTENDED_LIMITS') or line.startswith('DEPOSIT'):
                    continue
                al.append(line)
            
            if len(al) >= 4:
                axis_type = al[0]
                axis_name = al[1]
                axis_unit = al[2]
                try:
                    num_pts = int(al[3])
                except (ValueError, IndexError):
                    num_pts = 0
                ax_lo = 0.0
                ax_hi = 0.0
                if len(al) > 4:
                    try:
                        ax_lo = float(al[4])
                    except (ValueError, IndexError):
                        pass
                if len(al) > 5:
                    try:
                        ax_hi = float(al[5])
                    except (ValueError, IndexError):
                        pass
                
                axes.append(AxisDescription(
                    axis_type=axis_type,
                    axis_name=axis_name,
                    axis_unit=axis_unit,
                    num_points=num_pts,
                    min_value=ax_lo,
                    max_value=ax_hi,
                ))
        
        addr_int = parse_hex_address(address)
        
        char = Characteristic(
            name=name,
            description=description,
            char_type=char_type,
            address=address,
            address_int=addr_int,
            conversion=conversion,
            resolution=resolution,
            unit=unit,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            axes=axes,
        )
        characteristics.append(char)
    
    return characteristics


def parse_a2l_file(filepath: str) -> List[Characteristic]:
    """Parse an A2L file and return list of CHARACTERISTICs."""
    with open(filepath, 'r', encoding='latin-1', errors='replace') as f:
        content = f.read()
    return parse_a2l(content)


def extract_units(chars: List[Characteristic]) -> Dict[str, str]:
    """Extract unique unit names from characteristics.
    
    Returns dict of {unit_name: description}.
    """
    units = {}
    for c in chars:
        if c.unit and c.unit not in units:
            units[c.unit] = c.description[:100] if c.description else c.unit
    
    # Also extract from axes
    for c in chars:
        for ax in c.axes:
            if ax.axis_unit and ax.axis_unit not in units:
                units[ax.axis_unit] = f"Axis unit from {c.name}"
    
    return units
