"""
PHASE 2 — Map Name Normalizer.

Normalizes German/technical DAMOS map names to human-readable English.
Uses a synonym table + built-in rules.

Usage:
    normalizer = MapNormalizer(session)
    result = normalizer.normalize_map_name("Kraftstoffmenge_Fahrerwunsch")
    # → "Driver Demand Injection Quantity"
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("ecu_engine.normalizer")

# ── Built-in German→English rules ──────────────────────────────────────────
GERMAN_TO_ENGLISH: Dict[str, str] = {
    # Fuel / Injection
    "kraftstoff": "fuel", "kraftstoffmenge": "injection quantity",
    "einspritzmenge": "injection quantity", "einspritzzeit": "injection timing",
    "einspritzwinkel": "injection angle", "einspritzdruck": "injection pressure",
    "vor einspritz": "pilot injection", "nach einspritz": "post injection",
    "haupt einspritz": "main injection", "saugrohr": "intake manifold",
    "luftmasse": "air mass", "luftmenge": "air quantity",
    "fuel demand": "driver demand injection",

    # Boost / Turbo
    "ladedruck": "boost pressure", "ladedruckbegrenzer": "boost pressure limiter",
    "turbolader": "turbocharger", "vtg": "variable turbine geometry",
    "wastegate": "wastegate",

    # EGR / Exhaust
    "agr": "EGR", "abgasrückführung": "EGR", "abgas": "exhaust",
    "ruß": "soot", "rußfilter": "DPF", "partikelfilter": "DPF",
    "adblue": "AdBlue", "harnstofflösung": "urea solution",
    "nox": "NOx", "katalysator": "catalyst",

    # Temperature
    "temperatur": "temperature", "temp": "temp",
    "motor": "engine", "kühlmittel": "coolant",
    "kühlmitteltemperatur": "coolant temperature",
    "öltemperatur": "oil temperature", "sauglufttemperatur": "intake air temperature",
    "abgastemperatur": "exhaust gas temperature",
    "umgebungstemperatur": "ambient temperature",

    # RPM / Speed
    "drehzahl": "RPM", "n_drehzahl": "engine RPM",
    "fahrzeuggeschwindigkeit": "vehicle speed",
    "geschwindigkeit": "speed",

    # Torque / Power
    "drehmoment": "torque", "moment": "torque",
    "leistung": "power", "maximale": "maximum",
    "nominal": "nominal", "pedal": "pedal",

    # Driver request
    "fahrerwunsch": "driver demand", "fahrpedal": "accelerator pedal",
    "gaspedal": "accelerator pedal", "pedalwert": "pedal value",
    "pedalstellung": "pedal position",

    # Limits / Constraints
    "begrenzer": "limiter", "begrenzung": "limitation",
    "schutz": "protection", "grenzwert": "limit value",
    "maximalwert": "maximum value", "minimalwert": "minimum value",

    # Timing / Angles
    "verstellwinkel": "adjustment angle", "steuerwinkel": "control angle",
    "zündung": "ignition", "zündzeitpunkt": "ignition timing",
    "ventil": "valve", "ventilsteuerzeiten": "valve timing",
    "nockenwellen": "camshaft",

    # Corrections
    "korrektur": "correction", "nachlauf": "post-run",
    "voreil": "lead", "anreicherung": "enrichment",
    "verdünnung": "dilution",

    # Lambda
    "lambda": "lambda", "sauerstoff": "oxygen",
    "sonde": "sensor",

    # Common full words
    "tabelle": "table", "kennlinie": "curve", "kennfeld": "map",
    "kurve": "curve", "charakteristik": "characteristic",
    "funktion": "function", "wert": "value", "werte": "values",
    "grenze": "limit", "bereich": "range",
    "steuerung": "control", "regelung": "regulation",
    "überwachung": "monitoring", "diagnose": "diagnosis",
    "fehler": "fault", "speicher": "memory",
    "anzeige": "display", "ausgang": "output", "eingang": "input",
    "simulation": "simulation", "test": "test",
    "bedingung": "condition", "schwelle": "threshold",
    "filter": "filter", "zeitspez": "time-specific",
}


@dataclass
class NormalizedMap:
    name_de: str
    name_en: str
    category: str
    subcategory: str
    unit_hint: str
    confidence: float
    changes: List[str]


class MapNormalizer:
    """Normalizes DAMOS map names to human-readable English."""

    def __init__(self, session: Session):
        self.session = session
        self._synonym_cache: Dict[str, str] = {}
        self._load_synonyms()

    def _load_synonyms(self):
        """Load map_synonyms from DB if table exists."""
        try:
            rows = self.session.execute(text(
                "SELECT german_term, english_term FROM map_synonyms"
            )).fetchall()
            for row in rows:
                self._synonym_cache[row[0].lower()] = row[1]
            logger.info("Loaded %d DB synonyms", len(self._synonym_cache))
        except Exception:
            pass

    def normalize_map_name(self, raw_name: str) -> NormalizedMap:
        """Normalize a single map name."""
        changes: List[str] = []
        working = raw_name.strip()

        # Step 1: Replace underscores with spaces
        if "_" in working:
            working = re.sub(r"_+", " ", working)
            changes.append("replaced underscores")

        # Step 2: Split into tokens
        tokens = working.split()
        en_tokens: List[str] = []
        matched_terms: List[str] = []

        for token in tokens:
            low = token.lower()

            # Check DB synonyms first
            if low in self._synonym_cache:
                en_tokens.append(self._synonym_cache[low])
                matched_terms.append(low)
                continue

            # Check built-in rules
            replaced = False
            for de, en in sorted(GERMAN_TO_ENGLISH.items(), key=lambda x: -len(x[0])):
                if de in low:
                    en_tokens.append(en)
                    matched_terms.append(de)
                    replaced = True
                    break

            if not replaced:
                en_tokens.append(token)

        name_en = " ".join(en_tokens)
        name_en = re.sub(r"\s+", " ", name_en).strip()

        # Capitalize first letter
        if name_en:
            name_en = name_en[0].upper() + name_en[1:]

        # Infer category from matched terms
        category = self._infer_category(matched_terms, raw_name)
        subcategory = self._infer_subcategory(matched_terms, raw_name)
        unit_hint = self._infer_unit(matched_terms, raw_name)

        confidence = min(1.0, len(matched_terms) / max(1, len(tokens))) if tokens else 0

        return NormalizedMap(
            name_de=raw_name,
            name_en=name_en,
            category=category,
            subcategory=subcategory,
            unit_hint=unit_hint,
            confidence=round(confidence, 2),
            changes=changes,
        )

    def _infer_category(self, matched_terms: List[str], raw: str) -> str:
        """Infer map category from matched German terms."""
        term_str = " ".join(matched_terms) + " " + raw.lower()

        categories = {
            "Injection": ["kraftstoff", "einspritz", "injection", "fuel"],
            "Boost Pressure": ["ladedruck", "boost", "turbo", "vtg"],
            "EGR": ["agr", "abgasrückführung", "egr"],
            "DPF": ["rußfilter", "partikelfilter", "dpf", "soot"],
            "AdBlue": ["adblue", "harnstoff", "nox"],
            "Lambda": ["lambda", "sauerstoff", "sonde"],
            "Temperature": ["temperatur", "temp"],
            "Torque": ["drehmoment", "moment", "torque"],
            "RPM Limiter": ["drehzahl", "rpm"],
            "Ignition": ["zünd", "ignition"],
            "Valve Timing": ["ventil", "nockenwellen", "camshaft"],
            "Pedal": ["pedal", "fahrerwunsch", "gaspedal"],
        }

        for cat, keywords in categories.items():
            for kw in keywords:
                if kw in term_str:
                    return cat
        return "Other"

    def _infer_subcategory(self, matched_terms: List[str], raw: str) -> str:
        term_str = " ".join(matched_terms) + " " + raw.lower()

        subcats = {
            "Maximum Limit": ["maximal", "maximum", "begrenzer", "limiter"],
            "Minimum Limit": ["minimal", "minimum"],
            "Driver Demand": ["fahrerwunsch", "pedal", "demand"],
            "Cold Start": ["kalt", "cold", "start"],
            "Warm Up": ["warm", "warming"],
            "Altitude": ["höhe", "altitude", "luftdruck"],
            "Altitude Compensation": ["höhen", "altitude"],
        }

        for sub, keywords in subcats.items():
            for kw in keywords:
                if kw in term_str:
                    return sub
        return ""

    def _infer_unit(self, matched_terms: List[str], raw: str) -> str:
        term_str = " ".join(matched_terms) + " " + raw.lower()
        unit_map = {
            "rpm": ["drehzahl", "rpm"],
            "°C": ["temperatur", "temp"],
            "bar": ["druck", "pressure"],
            "mg/stroke": ["kraftstoff", "einspritz", "injection"],
            "°": ["winkel", "angle"],
            "V": ["spannung", "voltage"],
            "%": ["%", "prozent"],
            "ms": ["millisek", "ms"],
            "kg/h": ["luftmasse", "air mass"],
            "km/h": ["geschwindigkeit", "speed"],
            "Nm": ["drehmoment", "torque"],
        }

        for unit, keywords in unit_map.items():
            for kw in keywords:
                if kw in term_str:
                    return unit
        return ""

    def normalize_batch(self, names: List[str]) -> List[NormalizedMap]:
        """Normalize a batch of map names."""
        return [self.normalize_map_name(n) for n in names]

    def get_stats(self) -> dict:
        """Get normalization statistics."""
        try:
            result = self.session.execute(text("""
                SELECT
                    COUNT(DISTINCT map_name) as unique_names,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT ecu_model_name) as ecus
                FROM known_maps
            """)).fetchone()
            return {
                "unique_names": result[0] if result else 0,
                "total_rows": result[1] if result else 0,
                "ecus_covered": result[2] if result else 0,
                "synonyms_loaded": len(self._synonym_cache),
            }
        except Exception:
            return {"error": "database unavailable"}
