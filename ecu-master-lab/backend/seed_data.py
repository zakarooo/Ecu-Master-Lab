from __future__ import annotations

"""
Seed script for ECU Master Lab V2 — PostgreSQL reference data.

Idempotent: safe to run multiple times (skips duplicates by name/unique key).

Usage:
    cd ecu-master-lab/backend
    python seed_data.py
"""

import sys
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Bootstrap: make sure ``app`` package is importable when run as standalone
# ---------------------------------------------------------------------------
import os

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.database import engine, SessionLocal  # noqa: E402
from app.models.new.ecu_models import (  # noqa: E402
    ChecksumAlgorithm,
    ECUModel,
    Manufacturer,
    Processor,
    Protocol,
    SoftwareVersion,
    MapCategory,
    MapUnit,
    VehicleBrand,
)


# ===========================================================================
# Helper — generic upsert (ON CONFLICT … DO NOTHING)
# ===========================================================================

def _upsert_one(
    session: Session,
    model: Any,
    unique_col: str,
    data: Dict[str, Any],
) -> int:
    """Insert *data* into *model*; skip if *unique_col* already exists.

    Returns 1 if inserted, 0 if skipped.
    """
    existing = session.query(model.id).filter(
        getattr(model, unique_col) == data[unique_col]
    ).first()
    if existing is not None:
        return 0
    row = model(**data)
    session.add(row)
    session.flush()
    return 1


def _upsert_many(
    session: Session,
    model: Any,
    unique_col: str,
    rows: List[Dict[str, Any]],
) -> int:
    """Batch upsert — returns count of newly inserted rows."""
    count = 0
    for data in rows:
        count += _upsert_one(session, model, unique_col, data)
    return count


# ===========================================================================
# 1. PROCESSORS (15 profiles)
# ===========================================================================

PROCESSORS: List[Dict[str, Any]] = [
    {
        "name": "Tricore TC1796",
        "family": "Tricore",
        "manufacturer": "Infineon",
        "architecture": "Tricore",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 300,
        "flash_kb": 4032,
        "ram_kb": 344,
        "extensions": "MCUSafe, HSM",
        "known_ecus": "Bosch EDC17, Siemens SID20x, Continental SID80x",
    },
    {
        "name": "Tricore TC1766",
        "family": "Tricore",
        "manufacturer": "Infineon",
        "architecture": "Tricore",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 200,
        "flash_kb": 3072,
        "ram_kb": 256,
        "known_ecus": "Bosch EDC16, Delphi DCM",
    },
    {
        "name": "Tricore TC1767",
        "family": "Tricore",
        "manufacturer": "Infineon",
        "architecture": "Tricore",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 200,
        "flash_kb": 4032,
        "ram_kb": 344,
        "known_ecus": "Bosch EDC17 CP04/CP14",
    },
    {
        "name": "Tricore TC1797",
        "family": "Tricore",
        "manufacturer": "Infineon",
        "architecture": "Tricore",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 300,
        "flash_kb": 6144,
        "ram_kb": 512,
        "known_ecus": "Bosch MED17, CPCR",
    },
    {
        "name": "MPC555",
        "family": "MPC5xx",
        "manufacturer": "NXP/Freescale",
        "architecture": "PowerPC",
        "word_size": 32,
        "endianness": "big",
        "clock_mhz": 40,
        "flash_kb": 448,
        "ram_kb": 36,
        "known_ecus": "Bosch EDC15, Siemens MS42",
    },
    {
        "name": "MPC563",
        "family": "MPC5xx",
        "manufacturer": "NXP/Freescale",
        "architecture": "PowerPC",
        "word_size": 32,
        "endianness": "big",
        "clock_mhz": 56,
        "flash_kb": 1024,
        "ram_kb": 48,
        "known_ecus": "Bosch EDC15 C3",
    },
    {
        "name": "MPC5604P",
        "family": "MPC5xx",
        "manufacturer": "NXP/Freescale",
        "architecture": "PowerPC",
        "word_size": 32,
        "endianness": "big",
        "clock_mhz": 150,
        "flash_kb": 1536,
        "ram_kb": 96,
        "known_ecus": "Continental SID201, Bosch EDC17C46",
    },
    {
        "name": "ST10F275",
        "family": "ST10",
        "manufacturer": "STMicroelectronics",
        "architecture": "C166",
        "word_size": 16,
        "endianness": "little",
        "clock_mhz": 64,
        "flash_kb": 672,
        "ram_kb": 56,
        "known_ecus": "Bosch EDC15, Siemens SIM2K",
    },
    {
        "name": "ST10F280",
        "family": "ST10",
        "manufacturer": "STMicroelectronics",
        "architecture": "C166",
        "word_size": 16,
        "endianness": "little",
        "clock_mhz": 80,
        "flash_kb": 832,
        "ram_kb": 64,
        "known_ecus": "Bosch ME7, Motronic ME7.x",
    },
    {
        "name": "SH7058",
        "family": "SH-2A",
        "manufacturer": "Renesas",
        "architecture": "SuperH",
        "word_size": 32,
        "endianness": "big",
        "clock_mhz": 160,
        "flash_kb": 1024,
        "ram_kb": 64,
        "known_ecus": "Hitachi ASTEC, Bosch EDC16U1",
    },
    {
        "name": "RH850 D1M",
        "family": "RH850",
        "manufacturer": "Renesas",
        "architecture": "RH850",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 320,
        "flash_kb": 4096,
        "ram_kb": 512,
        "known_ecus": "Continental, Bosch MED17.5, Denso",
    },
    {
        "name": "C167CS",
        "family": "C166",
        "manufacturer": "Infineon",
        "architecture": "C166",
        "word_size": 16,
        "endianness": "little",
        "clock_mhz": 20,
        "flash_kb": 0,
        "ram_kb": 16,
        "known_ecus": "Bosch EDC15 V6, older diesel ECUs",
    },
    {
        "name": "V850E1",
        "family": "V850",
        "manufacturer": "NEC/Renesas",
        "architecture": "V850",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 120,
        "flash_kb": 768,
        "ram_kb": 48,
        "known_ecus": "Hitachi, Denso diesel ECUs",
    },
    {
        "name": "ARM Cortex-M4",
        "family": "ARM",
        "manufacturer": "STMicroelectronics",
        "architecture": "ARM",
        "word_size": 32,
        "endianness": "little",
        "clock_mhz": 168,
        "flash_kb": 1024,
        "ram_kb": 128,
        "known_ecus": "Newer ECUs, GPEC, aftermarket",
    },
    {
        "name": "H8/3003",
        "family": "H8/300",
        "manufacturer": "Renesas",
        "architecture": "H8/300",
        "word_size": 16,
        "endianness": "big",
        "clock_mhz": 20,
        "flash_kb": 128,
        "ram_kb": 8,
        "known_ecus": "Older Denso, Toyota EFI",
    },
]


# ===========================================================================
# 2. PROTOCOLS (8)
# ===========================================================================

PROTOCOLS: List[Dict[str, Any]] = [
    {
        "name": "UDS",
        "description": "Unified Diagnostic Services (ISO 14229)",
        "requires_bootloader": True,
        "typical_tools": "OpenDiag, DiagRA, WinOLS",
    },
    {
        "name": "KWP2000",
        "description": "Keyword Protocol 2000 (ISO 14230)",
        "requires_bootloader": False,
        "typical_tools": "VAG KKL, ELM327",
    },
    {
        "name": "CAN",
        "description": "Controller Area Network (ISO 11898)",
        "requires_bootloader": False,
        "typical_tools": "CANtact, PCAN",
    },
    {
        "name": "J1850",
        "description": "SAE J1850 VPW/PWM (OBD-II)",
        "requires_bootloader": False,
        "typical_tools": "OBD-II scanner",
    },
    {
        "name": "ISO-9141",
        "description": "ISO 9141-2 diagnostic",
        "requires_bootloader": False,
        "typical_tools": "OBD-II adapter",
    },
    {
        "name": "BDM",
        "description": "Background Debug Mode (Freescale/MPC)",
        "requires_bootloader": True,
        "typical_tools": "BDM Pod, USBTAP, Codemaster",
    },
    {
        "name": "JTAG",
        "description": "Joint Test Action Group (ARM/Tricore)",
        "requires_bootloader": True,
        "typical_tools": "J-Link, OpenOCD",
    },
    {
        "name": "BOOTLOADER",
        "description": "Flash bootloader (OEM specific)",
        "requires_bootloader": True,
        "typical_tools": "OEM flash tools, KTag, PCMFlash",
    },
]


# ===========================================================================
# 3. CHECKSUM ALGORITHMS (8)
# ===========================================================================

CHECKSUM_ALGORITHMS: List[Dict[str, Any]] = [
    {
        "name": "CRC16-CCITT",
        "manufacturer": "Generic",
        "polynomial": "0x1021",
        "init_value": "0xFFFF",
        "xor_out": "0x0000",
    },
    {
        "name": "CRC16-BOSCH",
        "manufacturer": "Bosch",
        "polynomial": "0x8005",
        "init_value": "0x0000",
        "xor_out": "0x0000",
    },
    {
        "name": "CRC32",
        "manufacturer": "Generic",
        "polynomial": "0x04C11DB7",
        "init_value": "0xFFFFFFFF",
        "xor_out": "0xFFFFFFFF",
    },
    {
        "name": "CRC32-BOSCH",
        "manufacturer": "Bosch",
        "polynomial": "0x1EDC6F41",
        "init_value": "0xFFFFFFFF",
        "xor_out": "0xFFFFFFFF",
    },
    {
        "name": "SUM8",
        "manufacturer": "Generic",
        "polynomial": "0x07",
        "init_value": "0x00",
        "xor_out": "0x00",
    },
    {
        "name": "SUM16",
        "manufacturer": "Generic",
        "polynomial": "0x0707",
        "init_value": "0x0000",
        "xor_out": "0x0000",
    },
    {
        "name": "XOR16",
        "manufacturer": "Generic",
        "polynomial": "0x0000",
        "init_value": "0x0000",
        "xor_out": "0x0000",
    },
    {
        "name": "CRC8",
        "manufacturer": "Generic",
        "polynomial": "0x07",
        "init_value": "0x00",
        "xor_out": "0x00",
    },
]


# ===========================================================================
# 4. MANUFACTURERS (10)
# ===========================================================================

MANUFACTURERS: List[Dict[str, Any]] = [
    {
        "name": "Bosch",
        "country": "Germany",
        "website": "https://www.bosch.com",
        "description": "Robert Bosch GmbH - Leader in ECU manufacturing",
    },
    {
        "name": "Continental",
        "country": "Germany",
        "website": "https://www.continental.com",
        "description": "Continental AG - Major automotive supplier",
    },
    {
        "name": "Siemens VDO",
        "country": "Germany",
        "description": "Siemens VDO Automotive (now Continental)",
    },
    {
        "name": "Delphi",
        "country": "USA",
        "website": "https://www.delphi.com",
        "description": "Delphi Technologies (now BorgWarner)",
    },
    {
        "name": "Denso",
        "country": "Japan",
        "website": "https://www.denso.com",
        "description": "DENSO Corporation - Japanese ECU manufacturer",
    },
    {
        "name": "Hitachi",
        "country": "Japan",
        "description": "Hitachi Astemo - ECUs for Japanese vehicles",
    },
    {
        "name": "Magneti Marelli",
        "country": "Italy",
        "description": "Magneti Marelli - Italian automotive electronics",
    },
    {
        "name": "Valeo",
        "country": "France",
        "website": "https://www.valeo.com",
        "description": "Valeo SA - French automotive supplier",
    },
    {
        "name": "MAHLE",
        "country": "Germany",
        "description": "MAHLE GmbH - Powertrain electronics",
    },
    {
        "name": "Gefran",
        "country": "Italy",
        "description": "Gefran - Industrial and automotive electronics",
    },
]


# ===========================================================================
# 5. MAP CATEGORIES (12)
# ===========================================================================

MAP_CATEGORIES: List[Dict[str, Any]] = [
    {"name": "Injection Timing", "description": "Main injection timing maps", "sort_order": 1},
    {"name": "Injection Quantity", "description": "Fuel injection quantity maps", "sort_order": 2},
    {"name": "Boost Pressure", "description": "Turbo boost pressure control", "sort_order": 3},
    {"name": "Smoke Limitation", "description": "Smoke limitation / air mass limit maps", "sort_order": 4},
    {"name": "Speed Limiter", "description": "Vehicle speed limitation maps", "sort_order": 5},
    {"name": "Torque Limiter", "description": "Engine torque limitation maps", "sort_order": 6},
    {"name": "Rail Pressure", "description": "Common rail pressure control", "sort_order": 7},
    {"name": "EGR Control", "description": "Exhaust Gas Recirculation maps", "sort_order": 8},
    {"name": "Glow Plug", "description": "Glow plug timing maps", "sort_order": 9},
    {"name": "Fan Control", "description": "Cooling fan control maps", "sort_order": 10},
    {"name": "Idle Speed", "description": "Idle speed control maps", "sort_order": 11},
    {"name": "Turbo Vane", "description": "Variable turbine geometry maps", "sort_order": 12},
]


# ===========================================================================
# 6. MAP UNITS (10)
# ===========================================================================

MAP_UNITS: List[Dict[str, Any]] = [
    {"symbol": "rpm", "name": "Revolutions per minute", "unit_type": "angular_speed"},
    {"symbol": "deg", "name": "Degrees", "unit_type": "angle"},
    {"symbol": "mg/stk", "name": "Milligrams per stroke", "unit_type": "mass_flow"},
    {"symbol": "bar", "name": "Bar", "unit_type": "pressure"},
    {"symbol": "mbar", "name": "Millibar", "unit_type": "pressure"},
    {"symbol": "kg/h", "name": "Kilograms per hour", "unit_type": "mass_flow"},
    {"symbol": "km/h", "name": "Kilometers per hour", "unit_type": "speed"},
    {"symbol": "Nm", "name": "Newton-meters", "unit_type": "torque"},
    {"symbol": "ms", "name": "Milliseconds", "unit_type": "time"},
    {"symbol": "degC", "name": "Degrees Celsius", "unit_type": "temperature"},
]


# ===========================================================================
# 7. VEHICLE BRANDS (8)
# ===========================================================================

VEHICLE_BRANDS: List[Dict[str, Any]] = [
    {"name": "Volkswagen", "country": "Germany"},
    {"name": "Audi", "country": "Germany"},
    {"name": "BMW", "country": "Germany"},
    {"name": "Mercedes-Benz", "country": "Germany"},
    {"name": "Peugeot", "country": "France"},
    {"name": "Renault", "country": "France"},
    {"name": "Toyota", "country": "Japan"},
    {"name": "Ford", "country": "USA"},
]


# ===========================================================================
# 8. ECU MODELS (8 — all linked to Bosch = manufacturer_id 1)
# ===========================================================================

ECU_MODELS: List[Dict[str, Any]] = [
    {
        "manufacturer_id": 1,
        "model_name": "EDC15",
        "family": "EDC",
        "processor_type": "MPC555",
        "flash_size_kb": 512,
        "protocol": "KWP2000",
    },
    {
        "manufacturer_id": 1,
        "model_name": "EDC16",
        "family": "EDC",
        "processor_type": "SH7058",
        "flash_size_kb": 1024,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "EDC17 CP04",
        "family": "EDC",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 3072,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "EDC17 CP14",
        "family": "EDC",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 4032,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "EDC17 C46",
        "family": "EDC",
        "processor_type": "Tricore TC1796",
        "flash_size_kb": 4032,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "MED17.1",
        "family": "MED",
        "processor_type": "Tricore TC1797",
        "flash_size_kb": 4096,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "MED17.5",
        "family": "MED",
        "processor_type": "RH850 D1M",
        "flash_size_kb": 4096,
        "protocol": "UDS",
    },
    {
        "manufacturer_id": 1,
        "model_name": "ME7",
        "family": "ME",
        "processor_type": "ST10F280",
        "flash_size_kb": 672,
        "protocol": "KWP2000",
    },
]


# ===========================================================================
# 9. SOFTWARE VERSIONS (4 — unique on (ecu_model_id, sw_number))
# ===========================================================================

SOFTWARE_VERSIONS: List[Dict[str, Any]] = [
    {
        "ecu_model_id": 3,
        "sw_number": "0281012803",
        "hw_number": "0281012278",
        "calibration_id": "EDC17CP04",
    },
    {
        "ecu_model_id": 5,
        "sw_number": "0281014673",
        "hw_number": "0281015164",
        "calibration_id": "EDC17C46",
    },
    {
        "ecu_model_id": 6,
        "sw_number": "0281020540",
        "hw_number": "0281020658",
        "calibration_id": "MED17.1",
    },
    {
        "ecu_model_id": 7,
        "sw_number": "0281030097",
        "hw_number": "0281030200",
        "calibration_id": "MED17.5",
    },
]


# ===========================================================================
# Seeding functions (one per table, respecting FK order)
# ===========================================================================

def seed_manufacturers(session: Session) -> int:
    return _upsert_many(session, Manufacturer, "name", MANUFACTURERS)


def seed_processors(session: Session) -> int:
    return _upsert_many(session, Processor, "name", PROCESSORS)


def seed_protocols(session: Session) -> int:
    return _upsert_many(session, Protocol, "name", PROTOCOLS)


def seed_checksum_algorithms(session: Session) -> int:
    return _upsert_many(session, ChecksumAlgorithm, "name", CHECKSUM_ALGORITHMS)


def seed_map_categories(session: Session) -> int:
    return _upsert_many(session, MapCategory, "name", MAP_CATEGORIES)


def seed_map_units(session: Session) -> int:
    return _upsert_many(session, MapUnit, "symbol", MAP_UNITS)


def seed_vehicle_brands(session: Session) -> int:
    return _upsert_many(session, VehicleBrand, "name", VEHICLE_BRANDS)


def seed_ecu_models(session: Session) -> int:
    """ECU models use model_name as the unique key (no name column)."""
    count = 0
    for data in ECU_MODELS:
        existing = session.query(ECUModel.id).filter(
            ECUModel.model_name == data["model_name"],
            ECUModel.manufacturer_id == data["manufacturer_id"],
        ).first()
        if existing is not None:
            continue
        row = ECUModel(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_software_versions(session: Session) -> int:
    """Software versions have unique constraint on (ecu_model_id, sw_number)."""
    count = 0
    for data in SOFTWARE_VERSIONS:
        existing = session.query(SoftwareVersion.id).filter(
            SoftwareVersion.ecu_model_id == data["ecu_model_id"],
            SoftwareVersion.sw_number == data["sw_number"],
        ).first()
        if existing is not None:
            continue
        row = SoftwareVersion(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


# ===========================================================================
# Main entry point
# ===========================================================================

def run_seed() -> None:
    """Seed all reference tables and print a summary."""

    session: Session = SessionLocal()
    try:
        counts: Dict[str, int] = {}

        # Order matters — FKs first.
        counts["manufacturers"] = seed_manufacturers(session)
        counts["processors"] = seed_processors(session)
        counts["protocols"] = seed_protocols(session)
        counts["checksum_algorithms"] = seed_checksum_algorithms(session)
        counts["map_categories"] = seed_map_categories(session)
        counts["map_units"] = seed_map_units(session)
        counts["vehicle_brands"] = seed_vehicle_brands(session)

        # Depends on manufacturers.
        counts["ecu_models"] = seed_ecu_models(session)

        # Depends on ecu_models.
        counts["software_versions"] = seed_software_versions(session)

        session.commit()

        print("=" * 60)
        print("  ECU Master Lab V2 — Seed Summary")
        print("=" * 60)
        total = 0
        for table, n in counts.items():
            label = table.replace("_", " ").title()
            print(f"  {label:<30s} : {n:>3d} inserted")
            total += n
        print("-" * 60)
        print(f"  {'TOTAL':<30s} : {total:>3d} new rows inserted")
        print("=" * 60)

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Seeding ECU Master Lab V2 reference data …")
    run_seed()
    print("Done.")
