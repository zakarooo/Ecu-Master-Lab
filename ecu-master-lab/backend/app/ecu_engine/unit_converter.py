"""
Unit converter — converts between ECU raw (integer) values and physical values.

ECU calibration maps store values as integers. To display meaningful physical
values (rpm, km/h, mg/stk, bar, °C, etc.), we need to apply a conversion formula.

Supports the most common ECU conversion types found in A2L files.

Stdlib Python 3.8 only.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

log = logging.getLogger("ecu_engine.unit_converter")


@dataclass
class ConversionFormula:
    name: str
    formula: str
    unit: str
    parameters: Dict[str, float] = field(default_factory=dict)


@dataclass
class UnitConversion:
    raw_to_physical: Optional[Callable] = None
    physical_to_raw: Optional[Callable] = None
    formula_name: str = ""
    unit: str = ""


# ── Common A2L conversion methods ──────────────────────────────

_KNOWN_CONVERSIONS: Dict[str, UnitConversion] = {
    "IDENTITY": UnitConversion(
        raw_to_physical=lambda x: float(x),
        physical_to_raw=lambda x: float(x),
        formula_name="IDENTITY", unit="",
    ),
    "RPM": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.375,
        physical_to_raw=lambda x: x / 0.375,
        formula_name="RPM", unit="rpm",
    ),
    "RPM_16": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.375,
        physical_to_raw=lambda x: x / 0.375,
        formula_name="RPM_16", unit="rpm",
    ),
    "SPEED_KMH": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.015625 * 3.6,
        physical_to_raw=lambda x: x / (0.015625 * 3.6),
        formula_name="SPEED_KMH", unit="km/h",
    ),
    "PRESSURE_BAR": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="PRESSURE_BAR", unit="bar",
    ),
    "TEMPERATURE_C": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1 - 40.0,
        physical_to_raw=lambda x: (x + 40.0) / 0.1,
        formula_name="TEMPERATURE_C", unit="°C",
    ),
    "TEMPERATURE_K": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1,
        physical_to_raw=lambda x: x / 0.1,
        formula_name="TEMPERATURE_K", unit="K",
    ),
    "INJECTION_MG": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="INJECTION_MG", unit="mg/stk",
    ),
    "ANGLE_DEG": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.01 - 30.0,
        physical_to_raw=lambda x: (x + 30.0) / 0.01,
        formula_name="ANGLE_DEG", unit="°",
    ),
    "LAMBDA": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="LAMBDA", unit="λ",
    ),
    "PERCENT": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1,
        physical_to_raw=lambda x: x / 0.1,
        formula_name="PERCENT", unit="%",
    ),
    "VOLTAGE_V": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="VOLTAGE_V", unit="V",
    ),
    "DURATION_MS": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="DURATION_MS", unit="ms",
    ),
    "FREQUENCY_HZ": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1,
        physical_to_raw=lambda x: x / 0.1,
        formula_name="FREQUENCY_HZ", unit="Hz",
    ),
    "TORQUE_NM": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1,
        physical_to_raw=lambda x: x / 0.1,
        formula_name="TORQUE_NM", unit="Nm",
    ),
    "MASSFLOW_GS": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.01,
        physical_to_raw=lambda x: x / 0.01,
        formula_name="MASSFLOW_GS", unit="g/s",
    ),
    "PRESSURE_KPA": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.1,
        physical_to_raw=lambda x: x / 0.1,
        formula_name="PRESSURE_KPA", unit="kPa",
    ),
    "TIME_S": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="TIME_S", unit="s",
    ),
    "VOLUME_MM3": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.001,
        physical_to_raw=lambda x: x / 0.001,
        formula_name="VOLUME_MM3", unit="mm³",
    ),
    "RESISTANCE_OHM": UnitConversion(
        raw_to_physical=lambda x: float(x) * 0.01,
        physical_to_raw=lambda x: x / 0.01,
        formula_name="RESISTANCE_OHM", unit="Ω",
    ),
}


# ── Linear conversion: physical = raw * factor + offset ────────

def _linear_conversion(factor: float, offset: float) -> UnitConversion:
    return UnitConversion(
        raw_to_physical=lambda x, f=factor, o=offset: float(x) * f + o,
        physical_to_raw=lambda x, f=factor, o=offset: (x - o) / f if f != 0 else 0.0,
        formula_name="LINEAR(%.6f, %.6f)" % (factor, offset),
        unit="",
    )


# ── A2L FORMULA parsing (simple forms) ────────────────────────

def parse_a2l_formula(formula_str: str) -> Optional[Callable]:
    """Parse simple A2L FORMULA strings.

    Supports common forms like:
      'AX/10 - 40'
      '(X * 0.1) - 40'
      'X * 0.001'
      'X / 256'
    """
    if not formula_str:
        return None
    s = formula_str.strip()
    s = s.replace("**", "**")
    try:
        test_val = 100.0
        result = eval(s, {"__builtins__": {}}, {"X": test_val, "x": test_val, "AX": test_val})
        if isinstance(result, (int, float)):
            return lambda x, _s=s: float(eval(_s, {"__builtins__": {}}, {"X": float(x), "x": float(x), "AX": float(x)}))
    except Exception:
        pass
    return None


# ── Unit name normalization ────────────────────────────────────

_UNIT_ALIASES: Dict[str, str] = {
    "rpm": "rpm", "tr/min": "rpm", "upm": "rpm",
    "km/h": "km/h", "kmh": "km/h", "kph": "km/h",
    "bar": "bar", "mbar": "mbar",
    "mg/stk": "mg/stk", "mg/str": "mg/stk", "mg/coup": "mg/stk",
    "mg/hub": "mg/stk",
    "deg": "°", "grad": "°", "°c": "°C", "°celsius": "°C",
    "k": "K", "kelvin": "K",
    "": "", "-": "",
    "%": "%", "prozent": "%", "pct": "%",
    "v": "V", "volt": "V",
    "ms": "ms", "millisecond": "ms",
    "nm": "Nm", "n.m": "Nm",
    "hz": "Hz", "hertz": "Hz",
    "g/s": "g/s", "g/s": "g/s",
    "kpa": "kPa", "kpascal": "kPa",
    "s": "s", "sec": "s", "sек": "s",
    "mm³": "mm³", "mm3": "mm³",
    "ohm": "Ω", "ω": "Ω",
    "lambda": "λ", "λ": "λ", "la": "λ",
}


def normalize_unit(unit_str: str) -> str:
    """Normalize a unit string to a canonical form."""
    if not unit_str:
        return ""
    return _UNIT_ALIASES.get(unit_str.lower().strip(), unit_str.strip())


# ── Public API ──────────────────────────────────────────────────

def get_conversion(unit_or_formula: str) -> Optional[UnitConversion]:
    """Look up a conversion by unit name or formula key."""
    key = unit_or_formula.upper().strip()
    if key in _KNOWN_CONVERSIONS:
        return _KNOWN_CONVERSIONS[key]
    normalized = normalize_unit(unit_or_formula)
    for k, v in _KNOWN_CONVERSIONS.items():
        if v.unit == normalized:
            return v
    return None


def raw_to_physical(
    raw_value: float,
    conversion_name: str = "IDENTITY",
    factor: float = 1.0,
    offset: float = 0.0,
) -> float:
    """Convert a raw ECU value to its physical equivalent.

    Uses the named conversion if found, otherwise falls back to
    linear: physical = raw * factor + offset.
    """
    conv = get_conversion(conversion_name)
    if conv and conv.raw_to_physical:
        return conv.raw_to_physical(raw_value)
    if factor != 1.0 or offset != 0.0:
        return raw_value * factor + offset
    return float(raw_value)


def physical_to_raw(
    physical_value: float,
    conversion_name: str = "IDENTITY",
    factor: float = 1.0,
    offset: float = 0.0,
) -> float:
    """Convert a physical value back to ECU raw integer."""
    conv = get_conversion(conversion_name)
    if conv and conv.physical_to_raw:
        return conv.physical_to_raw(physical_value)
    if factor != 1.0 or offset != 0.0:
        return (physical_value - offset) / factor if factor != 0 else 0.0
    return float(physical_value)


def convert_curve(
    raw_values: List[float],
    conversion_name: str = "IDENTITY",
    factor: float = 1.0,
    offset: float = 0.0,
) -> List[float]:
    """Convert a list of raw curve values to physical values."""
    return [raw_to_physical(v, conversion_name, factor, offset) for v in raw_values]


def convert_map(
    raw_values: List[List[float]],
    conversion_name: str = "IDENTITY",
    factor: float = 1.0,
    offset: float = 0.0,
) -> List[List[float]]:
    """Convert a 2D map of raw values to physical values."""
    return [
        [raw_to_physical(v, conversion_name, factor, offset) for v in row]
        for row in raw_values
    ]


def get_all_conversions() -> List[Dict]:
    """List all known conversions for UI display."""
    return [
        {"name": k, "unit": v.unit, "formula": v.formula_name}
        for k, v in sorted(_KNOWN_CONVERSIONS.items())
        if k != "IDENTITY"
    ]
