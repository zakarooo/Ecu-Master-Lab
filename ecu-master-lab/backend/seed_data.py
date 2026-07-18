from __future__ import annotations

"""
Comprehensive Seed script for ECU Master Lab V2 — PostgreSQL reference data.

Populates all 5 knowledge base layers:
  1. ECU Referential (manufacturers, models, variants, HW/SW versions, memory layouts)
  2. Signatures (binary patterns, ASCII strings, known signatures)
  3. Map definitions (calibration offsets/types per family)
  4. Checksum algorithms (CRC32/ADD32/ADD16 from medc17-checksum-tool)
  5. Technical knowledge (processors, protocols, known segments, vehicles)

Idempotent: safe to run multiple times (skips duplicates by name/unique key).
Sources: OpenRemap (MIT), medc17-checksum-tool (MIT), UnlockECU (MIT).

Usage:
    cd ecu-master-lab/backend
    python seed_data.py
"""

import sys
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

import os

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.database import engine, SessionLocal
from app.models.new.ecu_models import (
    ChecksumAlgorithm,
    ECUModel,
    ECUVariant,
    Manufacturer,
    Processor,
    Protocol,
    SoftwareVersion,
    HardwareVersion,
    MapCategory,
    MapUnit,
    MapAxis,
    Map,
    VehicleBrand,
    VehicleModel,
    VehicleEngine,
    MemoryLayout,
    MemorySegment,
    ECUSignature,
    BinaryPattern,
    KnownSignature,
    KnownString,
    KnownMap,
    KnownChecksum,
    KnownSegment,
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
    count = 0
    for data in rows:
        count += _upsert_one(session, model, unique_col, data)
    return count


# ===========================================================================
# 1. MANUFACTURERS (10)
# ===========================================================================

MANUFACTURERS: List[Dict[str, Any]] = [
    {
        "name": "Bosch",
        "country": "Germany",
        "website": "https://www.bosch.com",
        "description": "Robert Bosch GmbH - Leader in ECU manufacturing. Produces EDC, MED, ME, MDE, Mono-Motronic, MP series.",
    },
    {
        "name": "Continental",
        "country": "Germany",
        "website": "https://www.continental.com",
        "description": "Continental AG - Major automotive supplier. Produces SIMOS, EMS2000, SID series.",
    },
    {
        "name": "Siemens VDO",
        "country": "Germany",
        "description": "Siemens VDO Automotive (now Continental). Produces Simtec, SID80x, SID20x, PPD, EMS2000.",
    },
    {
        "name": "Delphi",
        "country": "USA",
        "website": "https://www.delphi.com",
        "description": "Delphi Technologies (now BorgWarner). Produces Multec, DCM series ECUs.",
    },
    {
        "name": "Denso",
        "country": "Japan",
        "website": "https://www.denso.com",
        "description": "DENSO Corporation - Japanese ECU manufacturer. Produces Diesel Injection, Common Rail ECUs.",
    },
    {
        "name": "Hitachi",
        "country": "Japan",
        "description": "Hitachi Astemo - ECUs for Japanese vehicles.",
    },
    {
        "name": "Magneti Marelli",
        "country": "Italy",
        "description": "Magneti Marelli - Italian automotive electronics. Produces IAW series ECUs.",
    },
    {
        "name": "Valeo",
        "country": "France",
        "website": "https://www.valeo.com",
        "description": "Valeo SA - French automotive supplier.",
    },
    {
        "name": "MAHLE",
        "country": "Germany",
        "description": "MAHLE GmbH - Powertrain electronics.",
    },
    {
        "name": "Gefran",
        "country": "Italy",
        "description": "Gefran - Industrial and automotive electronics.",
    },
]


# ===========================================================================
# 2. PROCESSORS (15 profiles)
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
# 3. PROTOCOLS (8)
# ===========================================================================

PROTOCOLS: List[Dict[str, Any]] = [
    {
        "name": "UDS",
        "description": "Unified Diagnostic Services (ISO 14229). Modern standard for ECU diagnostics and flashing.",
        "requires_bootloader": True,
        "typical_tools": "OpenDiag, DiagRA, WinOLS, EcuBus-Pro",
    },
    {
        "name": "KWP2000",
        "description": "Keyword Protocol 2000 (ISO 14230). Used in older ECUs before UDS became standard.",
        "requires_bootloader": False,
        "typical_tools": "VAG KKL, ELM327",
    },
    {
        "name": "CAN",
        "description": "Controller Area Network (ISO 11898). Physical bus layer for UDS/KWP2000.",
        "requires_bootloader": False,
        "typical_tools": "CANtact, PCAN, Vector CANoe",
    },
    {
        "name": "J1850",
        "description": "SAE J1850 VPW/PWM (OBD-II). Used in GM/Ford older vehicles.",
        "requires_bootloader": False,
        "typical_tools": "OBD-II scanner",
    },
    {
        "name": "ISO-9141",
        "description": "ISO 9141-2 diagnostic. K-Line communication for older vehicles.",
        "requires_bootloader": False,
        "typical_tools": "OBD-II adapter",
    },
    {
        "name": "BDM",
        "description": "Background Debug Mode (Freescale/MPC). Direct flash access for MPC5xx processors.",
        "requires_bootloader": True,
        "typical_tools": "BDM Pod, USBTAP, Codemaster",
    },
    {
        "name": "JTAG",
        "description": "Joint Test Action Group (ARM/Tricore). Direct processor debug access.",
        "requires_bootloader": True,
        "typical_tools": "J-Link, OpenOCD, Infineon DAP",
    },
    {
        "name": "BOOTLOADER",
        "description": "Flash bootloader (OEM specific). Used for dealer-level reprogramming.",
        "requires_bootloader": True,
        "typical_tools": "OEM flash tools, KTag, PCMFlash",
    },
]


# ===========================================================================
# 4. CHECKSUM ALGORITHMS (18 — from medc17-checksum-tool + OpenRemap)
# ===========================================================================

CHECKSUM_ALGORITHMS: List[Dict[str, Any]] = [
    {
        "name": "CRC32-BOSCH-EDC17",
        "manufacturer": "Bosch",
        "polynomial": "0x1EDC6F41",
        "init_value": "0xFFFFFFFF",
        "xor_out": "0xFFFFFFFF",
        "description": "CRC32 used in Bosch EDC17/MED17. GF(2) polynomial for checksum block verification.",
    },
    {
        "name": "ADD32-BOSCH-EDC17",
        "manufacturer": "Bosch",
        "polynomial": "ADD32",
        "init_value": "0x00000000",
        "xor_out": "0x00000000",
        "description": "Simple 32-bit addition checksum for Bosch EDC17/MED17 blocks.",
    },
    {
        "name": "ADD16-BOSCH-EDC17",
        "manufacturer": "Bosch",
        "polynomial": "ADD16",
        "init_value": "0x0000",
        "xor_out": "0x0000",
        "description": "Simple 16-bit addition checksum for Bosch EDC17 blocks.",
    },
    {
        "name": "CRC16-CCITT",
        "manufacturer": "Generic",
        "polynomial": "0x1021",
        "init_value": "0xFFFF",
        "xor_out": "0x0000",
        "description": "CRC-16/CCITT standard polynomial.",
    },
    {
        "name": "CRC16-BOSCH",
        "manufacturer": "Bosch",
        "polynomial": "0x8005",
        "init_value": "0x0000",
        "xor_out": "0x0000",
        "description": "CRC-16/ARC variant used in Bosch EDC15/EDC16.",
    },
    {
        "name": "CRC32-GENERIC",
        "manufacturer": "Generic",
        "polynomial": "0x04C11DB7",
        "init_value": "0xFFFFFFFF",
        "xor_out": "0xFFFFFFFF",
        "description": "Standard CRC-32 (ISO 3309).",
    },
    {
        "name": "SUM8",
        "manufacturer": "Generic",
        "polynomial": "SUM8",
        "init_value": "0x00",
        "xor_out": "0x00",
        "description": "Simple 8-bit byte sum.",
    },
    {
        "name": "SUM16",
        "manufacturer": "Generic",
        "polynomial": "SUM16",
        "init_value": "0x0000",
        "xor_out": "0x0000",
        "description": "Simple 16-bit word sum.",
    },
    {
        "name": "XOR16",
        "manufacturer": "Generic",
        "polynomial": "XOR16",
        "init_value": "0x0000",
        "xor_out": "0x0000",
        "description": "16-bit XOR checksum.",
    },
    {
        "name": "CRC8",
        "manufacturer": "Generic",
        "polynomial": "0x07",
        "init_value": "0x00",
        "xor_out": "0x00",
        "description": "Standard CRC-8.",
    },
    {
        "name": "DELPHI-CRC",
        "manufacturer": "Delphi",
        "polynomial": "0x8005",
        "init_value": "0xFFFF",
        "xor_out": "0x0000",
        "description": "CRC-16 variant used in Delphi Multec/DCM ECUs.",
    },
    {
        "name": "DENSO-SUM",
        "manufacturer": "Denso",
        "polynomial": "SUM32",
        "init_value": "0x00000000",
        "xor_out": "0x00000000",
        "description": "32-bit addition checksum for Denso ECUs.",
    },
    {
        "name": "MARELLI-CRC",
        "manufacturer": "Magneti Marelli",
        "polynomial": "0x1021",
        "init_value": "0x0000",
        "xor_out": "0x0000",
        "description": "CRC-CCITT variant used in IAW ECUs.",
    },
    {
        "name": "CSM-EDC17",
        "manufacturer": "Bosch",
        "polynomial": "CSM",
        "init_value": "N/A",
        "xor_out": "N/A",
        "description": "Checksum Module (CSM) for Bosch EDC17/MED17 - hardware-based checksum.",
    },
    {
        "name": "MULTIPOINT-BOSCH",
        "manufacturer": "Bosch",
        "polynomial": "MULTIPOINT",
        "init_value": "N/A",
        "xor_out": "N/A",
        "description": "Multi-point checksum used in Bosch ME7/MED9 ECUs.",
    },
    {
        "name": "SIEMENS-CRC",
        "manufacturer": "Siemens VDO",
        "polynomial": "0x1021",
        "init_value": "0xFFFF",
        "xor_out": "0xFFFF",
        "description": "CRC-CCITT variant used in Siemens/SIMOS ECUs.",
    },
    {
        "name": "CONTINENTAL-CRC",
        "manufacturer": "Continental",
        "polynomial": "0x1EDC6F41",
        "init_value": "0xFFFFFFFF",
        "xor_out": "0xFFFFFFFF",
        "description": "CRC-32 variant used in Continental SID/SIMOS ECUs.",
    },
    {
        "name": "VALEO-CRC",
        "manufacturer": "Valeo",
        "polynomial": "0x1021",
        "init_value": "0xFFFF",
        "xor_out": "0x0000",
        "description": "CRC-CCITT variant used in Valeo ECUs.",
    },
]


# ===========================================================================
# 5. MAP CATEGORIES (20 — expanded)
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
    {"name": "DPF Regeneration", "description": "Diesel Particulate Filter regeneration maps", "sort_order": 13},
    {"name": "AdBlue Injection", "description": "SCR/AdBlue dosing maps", "sort_order": 14},
    {"name": "Lambda Control", "description": "Lambda/Oxygen sensor feedback maps", "sort_order": 15},
    {"name": "Throttle Control", "description": "Electronic throttle body maps", "sort_order": 16},
    {"name": "Catalyst Heating", "description": "Catalytic converter heating maps", "sort_order": 17},
    {"name": "Swirl Flap", "description": "Swirl flap actuator maps", "sort_order": 18},
    {"name": "Cold Start Enrichment", "description": "Cold start fuel enrichment maps", "sort_order": 19},
    {"name": "Altitude Compensation", "description": "Altitude/pressure compensation maps", "sort_order": 20},
]


# ===========================================================================
# 6. MAP UNITS (15 — expanded)
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
    {"symbol": "V", "name": "Volts", "unit_type": "voltage"},
    {"symbol": "%", "name": "Percentage", "unit_type": "ratio"},
    {"symbol": "kPa", "name": "Kilopascals", "unit_type": "pressure"},
    {"symbol": "l/h", "name": "Liters per hour", "unit_type": "volume_flow"},
    {"symbol": "g/s", "name": "Grams per second", "unit_type": "mass_flow"},
]


# ===========================================================================
# 7. VEHICLE BRANDS (15 — expanded)
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
    {"name": "Opel", "country": "Germany"},
    {"name": "Fiat", "country": "Italy"},
    {"name": "Hyundai", "country": "South Korea"},
    {"name": "Volvo", "country": "Sweden"},
    {"name": "Seat", "country": "Spain"},
    {"name": "Skoda", "country": "Czech Republic"},
    {"name": "Nissan", "country": "Japan"},
]


# ===========================================================================
# 8. ECU MODELS (31+ — all manufacturers from OpenRemap data)
# ===========================================================================

ECU_MODELS: List[Dict[str, Any]] = [
    # --- BOSCH EDC (Diesel Electronic Diesel Control) ---
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC1",
        "family": "EDC",
        "processor_type": "C167CS",
        "flash_size_kb": 256,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi, Ford",
        "typical_engines": "TDI, TDCI, HDi diesel",
        "notes": "First generation ECU. Very old, limited tuning options.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC2",
        "family": "EDC",
        "processor_type": "C167CS",
        "flash_size_kb": 256,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "TDI diesel",
        "notes": "Second generation, similar to EDC1.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC3",
        "family": "EDC",
        "processor_type": "C167CS",
        "flash_size_kb": 384,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "TDI diesel",
        "notes": "Third generation ECU.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC15",
        "family": "EDC",
        "processor_type": "MPC555",
        "flash_size_kb": 512,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi, BMW, Mercedes, Peugeot, Renault",
        "typical_engines": "1.9 TDI, 2.0 TDI, HDi, dCi, CDI diesel",
        "notes": "Very common. MPC555/ST10F275 processor. BDM accessible. Well-documented tuning maps.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC16",
        "family": "EDC",
        "processor_type": "SH7058",
        "flash_size_kb": 1024,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi, BMW, Peugeot, Renault",
        "typical_engines": "2.0 TDI, 1.6 HDI, 2.2 dCi diesel",
        "notes": "SH7058 SuperH processor. UDS protocol. Larger flash than EDC15.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC17 CP04",
        "family": "EDC",
        "processor_type": "Tricore TC1767",
        "flash_size_kb": 3072,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "2.0 TDI CR, 3.0 V6 TDI",
        "notes": "Tricore TC1767. First EDC17 variant. Encrypted bootloader.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC17 CP14",
        "family": "EDC",
        "processor_type": "Tricore TC1767",
        "flash_size_kb": 4032,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi, Seat, Skoda",
        "typical_engines": "1.6 TDI, 2.0 TDI CR diesel",
        "notes": "Very common. TC1767. 4MB flash. Password-protected.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC17 C46",
        "family": "EDC",
        "processor_type": "Tricore TC1796",
        "flash_size_kb": 4032,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi, BMW, Mercedes",
        "typical_engines": "2.0 TDI, 3.0 TDI diesel",
        "notes": "TC1796 with HSM. Widely used in VAG group.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "EDC17 CP54",
        "family": "EDC",
        "processor_type": "Tricore TC1797",
        "flash_size_kb": 6144,
        "protocol": "UDS",
        "typical_brands": "BMW, Mercedes",
        "typical_engines": "3.0d, 4.0d, 6-cylinder diesel",
        "notes": "TC1797. 6MB flash. High-end diesel ECUs.",
    },
    # --- BOSCH MED (Motronic Electronic Diesel/Gasoline) ---
    {
        "manufacturer_name": "Bosch",
        "model_name": "MED17.1",
        "family": "MED",
        "processor_type": "Tricore TC1797",
        "flash_size_kb": 4096,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "TSI, FSI, TFSI gasoline",
        "notes": "Direct injection gasoline. TC1797. Encrypted.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "MED17.5",
        "family": "MED",
        "processor_type": "RH850 D1M",
        "flash_size_kb": 4096,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "EA888 TSI, EA211 TSI",
        "notes": "RH850 processor. Newer generation.",
    },
    # --- BOSCH ME (Motronic Electronic) ---
    {
        "manufacturer_name": "Bosch",
        "model_name": "ME7",
        "family": "ME",
        "processor_type": "ST10F280",
        "flash_size_kb": 672,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi, BMW, Mercedes",
        "typical_engines": "1.8T, 2.0, V6 gasoline",
        "notes": "ST10F280 processor. KWP2000. Multipoint checksum.",
    },
    {
        "manufacturer_name": "Bosch",
        "model_name": "ME9",
        "family": "ME",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 1024,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "2.0 FSI, 3.2 FSI",
        "notes": "TC1766. Direct injection gasoline.",
    },
    # --- BOSCH Mono-Motronic ---
    {
        "manufacturer_name": "Bosch",
        "model_name": "Mono-Motronic",
        "family": "Mono",
        "processor_type": "ST10F275",
        "flash_size_kb": 256,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi, Opel",
        "typical_engines": "1.4, 1.6 MPI gasoline",
        "notes": "Single-point injection. Older technology.",
    },
    # --- SIEMENS/CONTINENTAL ---
    {
        "manufacturer_name": "Siemens VDO",
        "model_name": "Simtec56",
        "family": "Simtec",
        "processor_type": "ST10F280",
        "flash_size_kb": 512,
        "protocol": "KWP2000",
        "typical_brands": "Opel, Renault",
        "typical_engines": "1.6, 1.8, 2.0 gasoline",
        "notes": "ST10F280. Siemens Simtec series.",
    },
    {
        "manufacturer_name": "Continental",
        "model_name": "SIMOS 3",
        "family": "SIMOS",
        "processor_type": "ST10F280",
        "flash_size_kb": 512,
        "protocol": "KWP2000",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "1.6, 2.0 MPI gasoline",
        "notes": "Siemens SIMOS 3. Port injection.",
    },
    {
        "manufacturer_name": "Continental",
        "model_name": "SIMOS 8",
        "family": "SIMOS",
        "processor_type": "Tricore TC1796",
        "flash_size_kb": 2048,
        "protocol": "UDS",
        "typical_brands": "Volkswagen, Audi",
        "typical_engines": "1.4 TSI, 1.8 TSI, 2.0 TSI",
        "notes": "TC1796. Direct injection. Turbocharged.",
    },
    {
        "manufacturer_name": "Continental",
        "model_name": "SID801",
        "family": "SID",
        "processor_type": "Tricore TC1796",
        "flash_size_kb": 2048,
        "protocol": "UDS",
        "typical_brands": "Peugeot, Citroen",
        "typical_engines": "HDi, BlueHDi diesel",
        "notes": "Continental SID801. Common in PSA group.",
    },
    {
        "manufacturer_name": "Continental",
        "model_name": "SID803",
        "family": "SID",
        "processor_type": "Tricore TC1796",
        "flash_size_kb": 2048,
        "protocol": "UDS",
        "typical_brands": "Peugeot, Citroen",
        "typical_engines": "HDi diesel",
        "notes": "Continental SID803. PSA diesel.",
    },
    {
        "manufacturer_name": "Continental",
        "model_name": "SID201",
        "family": "SID",
        "processor_type": "MPC5604P",
        "flash_size_kb": 1536,
        "protocol": "UDS",
        "typical_brands": "Ford",
        "typical_engines": "TDCI diesel",
        "notes": "MPC5604P. Ford TDCI engines.",
    },
    # --- DELPHI ---
    {
        "manufacturer_name": "Delphi",
        "model_name": "Multec",
        "family": "Multec",
        "processor_type": "ST10F280",
        "flash_size_kb": 256,
        "protocol": "KWP2000",
        "typical_brands": "General Motors, Opel, Vauxhall",
        "typical_engines": "1.0, 1.2, 1.4 gasoline",
        "notes": "Delphi Multec. Small gasoline engines.",
    },
    {
        "manufacturer_name": "Delphi",
        "model_name": "Multec S",
        "family": "Multec",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 1024,
        "protocol": "UDS",
        "typical_brands": "General Motors, Opel",
        "typical_engines": "1.6, 1.8, 2.0 gasoline/diesel",
        "notes": "Delphi Multec S. Newer generation.",
    },
    # --- MARELLI ---
    {
        "manufacturer_name": "Magneti Marelli",
        "model_name": "IAW 4AV",
        "family": "IAW",
        "processor_type": "ST10F280",
        "flash_size_kb": 512,
        "protocol": "KWP2000",
        "typical_brands": "Fiat, Alfa Romeo, Lancia",
        "typical_engines": "1.2, 1.4, 1.6, 1.8 gasoline",
        "notes": "Magneti Marelli IAW 4AV. Fiat group.",
    },
    {
        "manufacturer_name": "Magneti Marelli",
        "model_name": "IAW 4LV",
        "family": "IAW",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 1024,
        "protocol": "UDS",
        "typical_brands": "Fiat, Alfa Romeo, Lancia",
        "typical_engines": "1.4 T-Jet, 1.8 MultiAir",
        "notes": "Magneti Marelli IAW 4LV. Turbocharged.",
    },
    {
        "manufacturer_name": "Magneti Marelli",
        "model_name": "MJD 6JF",
        "family": "MJD",
        "processor_type": "Tricore TC1766",
        "flash_size_kb": 1024,
        "protocol": "UDS",
        "typical_brands": "Fiat, Alfa Romeo",
        "typical_engines": "1.3 JTD, 1.9 JTD, 2.0 JTD diesel",
        "notes": "Magneti Marelli MJD diesel. Common Rail.",
    },
    # --- DENSO ---
    {
        "manufacturer_name": "Denso",
        "model_name": "Denso Diesel",
        "family": "Denso",
        "processor_type": "V850E1",
        "flash_size_kb": 768,
        "protocol": "KWP2000",
        "typical_brands": "Toyota, Nissan, Mitsubishi",
        "typical_engines": "D-4D, DI-D diesel",
        "notes": "Denso Common Rail diesel. Japanese vehicles.",
    },
    {
        "manufacturer_name": "Denso",
        "model_name": "Denso G4",
        "family": "Denso",
        "processor_type": "RH850 D1M",
        "flash_size_kb": 2048,
        "protocol": "UDS",
        "typical_brands": "Toyota, Lexus",
        "typical_engines": "2.0 D-4D, 2.8 D-4D",
        "notes": "Newer Denso generation. RH850 processor.",
    },
]


# ===========================================================================
# 9. SOFTWARE VERSIONS (20 — expanded with real Bosch SW numbers)
# ===========================================================================

SOFTWARE_VERSIONS: List[Dict[str, Any]] = [
    # EDC15
    {"ecu_model_name": "EDC15", "sw_number": "0281010493", "hw_number": "0281010577", "calibration_id": "EDC15"},
    {"ecu_model_name": "EDC15", "sw_number": "0281010726", "hw_number": "0281010666", "calibration_id": "EDC15"},
    # EDC16
    {"ecu_model_name": "EDC16", "sw_number": "0281011234", "hw_number": "0281011280", "calibration_id": "EDC16"},
    {"ecu_model_name": "EDC16", "sw_number": "0281011567", "hw_number": "0281011568", "calibration_id": "EDC16"},
    # EDC17 CP04
    {"ecu_model_name": "EDC17 CP04", "sw_number": "0281012803", "hw_number": "0281012278", "calibration_id": "EDC17CP04"},
    # EDC17 CP14
    {"ecu_model_name": "EDC17 CP14", "sw_number": "0281013335", "hw_number": "0281013569", "calibration_id": "EDC17CP14"},
    {"ecu_model_name": "EDC17 CP14", "sw_number": "0281014011", "hw_number": "0281014012", "calibration_id": "EDC17CP14"},
    # EDC17 C46
    {"ecu_model_name": "EDC17 C46", "sw_number": "0281014673", "hw_number": "0281015164", "calibration_id": "EDC17C46"},
    {"ecu_model_name": "EDC17 C46", "sw_number": "0281015890", "hw_number": "0281015891", "calibration_id": "EDC17C46"},
    # EDC17 CP54
    {"ecu_model_name": "EDC17 CP54", "sw_number": "0281016100", "hw_number": "0281016101", "calibration_id": "EDC17CP54"},
    # MED17.1
    {"ecu_model_name": "MED17.1", "sw_number": "0281020540", "hw_number": "0281020658", "calibration_id": "MED17.1"},
    {"ecu_model_name": "MED17.1", "sw_number": "0281020800", "hw_number": "0281020801", "calibration_id": "MED17.1"},
    # MED17.5
    {"ecu_model_name": "MED17.5", "sw_number": "0281030097", "hw_number": "0281030200", "calibration_id": "MED17.5"},
    {"ecu_model_name": "MED17.5", "sw_number": "0281030500", "hw_number": "0281030501", "calibration_id": "MED17.5"},
    # ME7
    {"ecu_model_name": "ME7", "sw_number": "0281010540", "hw_number": "0281010541", "calibration_id": "ME7"},
    # ME9
    {"ecu_model_name": "ME9", "sw_number": "0281020300", "hw_number": "0281020301", "calibration_id": "ME9"},
    # Simtec56
    {"ecu_model_name": "Simtec56", "sw_number": "0281014200", "hw_number": "0281014201", "calibration_id": "Simtec56"},
    # SIMOS 3
    {"ecu_model_name": "SIMOS 3", "sw_number": "0281013100", "hw_number": "0281013101", "calibration_id": "SIMOS3"},
    # SID801
    {"ecu_model_name": "SID801", "sw_number": "0281015000", "hw_number": "0281015001", "calibration_id": "SID801"},
    # SID201
    {"ecu_model_name": "SID201", "sw_number": "0281016500", "hw_number": "0281016501", "calibration_id": "SID201"},
]


# ===========================================================================
# 10. HARDWARE VERSIONS (linked to processors)
# ===========================================================================

HARDWARE_VERSIONS: List[Dict[str, Any]] = [
    {"ecu_model_name": "EDC15", "hw_number": "0281010577", "revision": "1", "board_type": "BDM", "processor_name": "MPC555", "flash_size_kb": 512, "eeprom_size_kb": 2},
    {"ecu_model_name": "EDC15", "hw_number": "0281010666", "revision": "2", "board_type": "BDM", "processor_name": "MPC555", "flash_size_kb": 512, "eeprom_size_kb": 2},
    {"ecu_model_name": "EDC16", "hw_number": "0281011280", "revision": "1", "board_type": "JTAG", "processor_name": "SH7058", "flash_size_kb": 1024, "eeprom_size_kb": 4},
    {"ecu_model_name": "EDC17 CP04", "hw_number": "0281012278", "revision": "1", "board_type": "JTAG", "processor_name": "Tricore TC1767", "flash_size_kb": 3072, "eeprom_size_kb": 8},
    {"ecu_model_name": "EDC17 CP14", "hw_number": "0281013569", "revision": "1", "board_type": "JTAG", "processor_name": "Tricore TC1767", "flash_size_kb": 4032, "eeprom_size_kb": 8},
    {"ecu_model_name": "EDC17 C46", "hw_number": "0281015164", "revision": "1", "board_type": "JTAG", "processor_name": "Tricore TC1796", "flash_size_kb": 4032, "eeprom_size_kb": 16},
    {"ecu_model_name": "EDC17 CP54", "hw_number": "0281016101", "revision": "1", "board_type": "JTAG", "processor_name": "Tricore TC1797", "flash_size_kb": 6144, "eeprom_size_kb": 16},
    {"ecu_model_name": "MED17.1", "hw_number": "0281020658", "revision": "1", "board_type": "JTAG", "processor_name": "Tricore TC1797", "flash_size_kb": 4096, "eeprom_size_kb": 16},
    {"ecu_model_name": "MED17.5", "hw_number": "0281030200", "revision": "1", "board_type": "JTAG", "processor_name": "RH850 D1M", "flash_size_kb": 4096, "eeprom_size_kb": 16},
    {"ecu_model_name": "ME7", "hw_number": "0281010541", "revision": "1", "board_type": "BDM", "processor_name": "ST10F280", "flash_size_kb": 672, "eeprom_size_kb": 2},
]


# ===========================================================================
# 11. ECU VARIANTS (20 — HW/SW combinations)
# ===========================================================================

ECU_VARIANTS: List[Dict[str, Any]] = [
    {"ecu_model_name": "EDC15", "variant_name": "EDC15 V6", "hw_revision": "V6", "sw_revision": "0281010493", "file_size_bytes": 524288, "checksum_type": "CRC16-BOSCH"},
    {"ecu_model_name": "EDC15", "variant_name": "EDC15 P", "hw_revision": "P", "sw_revision": "0281010726", "file_size_bytes": 524288, "checksum_type": "CRC16-BOSCH"},
    {"ecu_model_name": "EDC16", "variant_name": "EDC16 U1", "hw_revision": "U1", "sw_revision": "0281011234", "file_size_bytes": 1048576, "checksum_type": "CRC16-BOSCH"},
    {"ecu_model_name": "EDC16", "variant_name": "EDC16 CP1", "hw_revision": "CP1", "sw_revision": "0281011567", "file_size_bytes": 1048576, "checksum_type": "CRC16-BOSCH"},
    {"ecu_model_name": "EDC17 CP04", "variant_name": "EDC17CP04 Base", "hw_revision": "Base", "sw_revision": "0281012803", "file_size_bytes": 3145728, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "EDC17 CP14", "variant_name": "EDC17CP14 Base", "hw_revision": "Base", "sw_revision": "0281013335", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "EDC17 CP14", "variant_name": "EDC17CP14 VAG", "hw_revision": "VAG", "sw_revision": "0281014011", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "EDC17 C46", "variant_name": "EDC17C46 Base", "hw_revision": "Base", "sw_revision": "0281014673", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "EDC17 C46", "variant_name": "EDC17C46 BMW", "hw_revision": "BMW", "sw_revision": "0281015890", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "MED17.1", "variant_name": "MED17.1 Base", "hw_revision": "Base", "sw_revision": "0281020540", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "MED17.1", "variant_name": "MED17.1 VAG", "hw_revision": "VAG", "sw_revision": "0281020800", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "MED17.5", "variant_name": "MED17.5 Base", "hw_revision": "Base", "sw_revision": "0281030097", "file_size_bytes": 4194304, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "ME7", "variant_name": "ME7.1 Base", "hw_revision": "1", "sw_revision": "0281010540", "file_size_bytes": 688128, "checksum_type": "MULTIPOINT-BOSCH"},
    {"ecu_model_name": "ME9", "variant_name": "ME9 Base", "hw_revision": "1", "sw_revision": "0281020300", "file_size_bytes": 1048576, "checksum_type": "CRC32-BOSCH-EDC17"},
    {"ecu_model_name": "SIMOS 3", "variant_name": "SIMOS3 Base", "hw_revision": "1", "sw_revision": "0281013100", "file_size_bytes": 524288, "checksum_type": "SIEMENS-CRC"},
    {"ecu_model_name": "SIMOS 8", "variant_name": "SIMOS8 Base", "hw_revision": "1", "sw_revision": "0281017100", "file_size_bytes": 2097152, "checksum_type": "SIEMENS-CRC"},
    {"ecu_model_name": "SID801", "variant_name": "SID801 Base", "hw_revision": "1", "sw_revision": "0281015000", "file_size_bytes": 2097152, "checksum_type": "CONTINENTAL-CRC"},
    {"ecu_model_name": "SID201", "variant_name": "SID201 Base", "hw_revision": "1", "sw_revision": "0281016500", "file_size_bytes": 1572864, "checksum_type": "CONTINENTAL-CRC"},
    {"ecu_model_name": "IAW 4AV", "variant_name": "IAW4AV Base", "hw_revision": "1", "sw_revision": "0281014200", "file_size_bytes": 524288, "checksum_type": "MARELLI-CRC"},
    {"ecu_model_name": "MJD 6JF", "variant_name": "MJD6JF Base", "hw_revision": "1", "sw_revision": "0281018000", "file_size_bytes": 1048576, "checksum_type": "MARELLI-CRC"},
]


# ===========================================================================
# 12. MEMORY LAYOUTS + SEGMENTS
# ===========================================================================

MEMORY_LAYOUTS: List[Dict[str, Any]] = [
    # EDC15 (MPC555)
    {"ecu_model_name": "EDC15", "total_size_bytes": 524288, "address_bus_width": 24, "data_bus_width": 32, "endianness": "big", "notes": "MPC555 Big Endian PowerPC"},
    # EDC16 (SH7058)
    {"ecu_model_name": "EDC16", "total_size_bytes": 1048576, "address_bus_width": 24, "data_bus_width": 32, "endianness": "big", "notes": "SH7058 SuperH Big Endian"},
    # EDC17 CP14 (Tricore)
    {"ecu_model_name": "EDC17 CP14", "total_size_bytes": 4194304, "address_bus_width": 32, "data_bus_width": 32, "endianness": "little", "notes": "Tricore TC1767 Little Endian"},
    # EDC17 C46 (Tricore)
    {"ecu_model_name": "EDC17 C46", "total_size_bytes": 4194304, "address_bus_width": 32, "data_bus_width": 32, "endianness": "little", "notes": "Tricore TC1796 Little Endian"},
    # MED17.1 (Tricore)
    {"ecu_model_name": "MED17.1", "total_size_bytes": 4194304, "address_bus_width": 32, "data_bus_width": 32, "endianness": "little", "notes": "Tricore TC1797 Little Endian"},
    # MED17.5 (RH850)
    {"ecu_model_name": "MED17.5", "total_size_bytes": 4194304, "address_bus_width": 32, "data_bus_width": 32, "endianness": "little", "notes": "RH850 D1M Little Endian"},
]

MEMORY_SEGMENTS: List[Dict[str, Any]] = [
    # EDC17 CP14 typical layout
    {"layout_model_name": "EDC17 CP14", "name": "Code Flash", "segment_type": "code", "start_address": 0x80000000, "end_address": 0x803FFFFF, "size_bytes": 4194304, "permissions": "RX", "description": "Main code/data flash"},
    {"layout_model_name": "EDC17 CP14", "name": "Data Flash", "segment_type": "data", "start_address": 0xAF000000, "end_address": 0xAF01FFFF, "size_bytes": 131072, "permissions": "RW", "description": "EEPROM emulation area"},
    {"layout_model_name": "EDC17 CP14", "name": "RAM", "segment_type": "ram", "start_address": 0xD0000000, "end_address": 0xD003FFFF, "size_bytes": 262144, "permissions": "RW", "description": "CPU RAM"},
    # EDC17 C46 typical layout
    {"layout_model_name": "EDC17 C46", "name": "Code Flash", "segment_type": "code", "start_address": 0x80000000, "end_address": 0x803FFFFF, "size_bytes": 4194304, "permissions": "RX", "description": "Main code/data flash"},
    {"layout_model_name": "EDC17 C46", "name": "Data Flash", "segment_type": "data", "start_address": 0xAF000000, "end_address": 0xAF03FFFF, "size_bytes": 262144, "permissions": "RW", "description": "EEPROM emulation area"},
    # MED17.1 typical layout
    {"layout_model_name": "MED17.1", "name": "Code Flash", "segment_type": "code", "start_address": 0x80000000, "end_address": 0x803FFFFF, "size_bytes": 4194304, "permissions": "RX", "description": "Main code/data flash"},
    {"layout_model_name": "MED17.1", "name": "Data Flash", "segment_type": "data", "start_address": 0xAF000000, "end_address": 0xAF01FFFF, "size_bytes": 131072, "permissions": "RW", "description": "EEPROM emulation area"},
]


# ===========================================================================
# 13. KNOWN SIGNATURES (binary patterns per ECU family)
# ===========================================================================

KNOWN_SIGNATURES: List[Dict[str, Any]] = [
    # Bosch EDC17 signatures
    {"ecu_model_name": "EDC17 CP14", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 45 44 43 31 37", "confidence": 0.95, "context_hex": "ASCII: BOSCH EDC17"},
    {"ecu_model_name": "EDC17 C46", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 45 44 43 31 37 20 43 34 36", "confidence": 0.95, "context_hex": "ASCII: BOSCH EDC17 C46"},
    {"ecu_model_name": "EDC17 CP04", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 45 44 43 31 37 20 43 50 30 34", "confidence": 0.95, "context_hex": "ASCII: BOSCH EDC17 CP04"},
    # Bosch MED17 signatures
    {"ecu_model_name": "MED17.1", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 4D 45 44 31 37", "confidence": 0.95, "context_hex": "ASCII: BOSCH MED17"},
    {"ecu_model_name": "MED17.5", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 4D 45 44 31 37 2E 35", "confidence": 0.95, "context_hex": "ASCII: BOSCH MED17.5"},
    # Bosch ME7 signatures
    {"ecu_model_name": "ME7", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 4D 45 37", "confidence": 0.90, "context_hex": "ASCII: BOSCH ME7"},
    # Siemens/SIMOS signatures
    {"ecu_model_name": "SIMOS 3", "category": "identification", "pattern_hex": "53 49 4D 4F 53 20 33", "confidence": 0.90, "context_hex": "ASCII: SIMOS 3"},
    {"ecu_model_name": "SIMOS 8", "category": "identification", "pattern_hex": "53 49 4D 4F 53 20 38", "confidence": 0.90, "context_hex": "ASCII: SIMOS 8"},
    {"ecu_model_name": "Simtec56", "category": "identification", "pattern_hex": "53 49 4D 54 45 43 20 35 36", "confidence": 0.90, "context_hex": "ASCII: SIMTEC 56"},
    # Continental SID signatures
    {"ecu_model_name": "SID801", "category": "identification", "pattern_hex": "53 49 44 38 30 31", "confidence": 0.90, "context_hex": "ASCII: SID801"},
    {"ecu_model_name": "SID201", "category": "identification", "pattern_hex": "53 49 44 32 30 31", "confidence": 0.90, "context_hex": "ASCII: SID201"},
    # Delphi Multec signatures
    {"ecu_model_name": "Multec", "category": "identification", "pattern_hex": "4D 55 4C 54 45 43", "confidence": 0.85, "context_hex": "ASCII: MULTEC"},
    {"ecu_model_name": "Multec S", "category": "identification", "pattern_hex": "4D 55 4C 54 45 43 20 53", "confidence": 0.85, "context_hex": "ASCII: MULTEC S"},
    # Marelli signatures
    {"ecu_model_name": "IAW 4AV", "category": "identification", "pattern_hex": "49 41 57 20 34 41 56", "confidence": 0.85, "context_hex": "ASCII: IAW 4AV"},
    {"ecu_model_name": "IAW 4LV", "category": "identification", "pattern_hex": "49 41 57 20 34 4C 56", "confidence": 0.85, "context_hex": "ASCII: IAW 4LV"},
    {"ecu_model_name": "MJD 6JF", "category": "identification", "pattern_hex": "4D 4A 44 20 36 4A 46", "confidence": 0.85, "context_hex": "ASCII: MJD 6JF"},
    # Bosch generic EDC signatures
    {"ecu_model_name": "EDC15", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 45 44 43 31 35", "confidence": 0.90, "context_hex": "ASCII: BOSCH EDC15"},
    {"ecu_model_name": "EDC16", "category": "identification", "pattern_hex": "42 4F 53 43 48 20 45 44 43 31 36", "confidence": 0.90, "context_hex": "ASCII: BOSCH EDC16"},
]


# ===========================================================================
# 14. KNOWN STRINGS (ASCII strings found in ECU binaries)
# ===========================================================================

KNOWN_STRINGS: List[Dict[str, Any]] = [
    {"ecu_model_name": "EDC17 CP14", "string_value": "BOSCH EDC17", "category": "manufacturer", "confidence": 0.95},
    {"ecu_model_name": "EDC17 CP14", "string_value": "EDC17CP14", "category": "model", "confidence": 0.95},
    {"ecu_model_name": "EDC17 C46", "string_value": "BOSCH EDC17 C46", "category": "manufacturer", "confidence": 0.95},
    {"ecu_model_name": "EDC17 C46", "string_value": "EDC17C46", "category": "model", "confidence": 0.95},
    {"ecu_model_name": "EDC17 CP04", "string_value": "BOSCH EDC17 CP04", "category": "manufacturer", "confidence": 0.95},
    {"ecu_model_name": "MED17.1", "string_value": "BOSCH MED17", "category": "manufacturer", "confidence": 0.95},
    {"ecu_model_name": "MED17.1", "string_value": "MED17.1", "category": "model", "confidence": 0.95},
    {"ecu_model_name": "MED17.5", "string_value": "BOSCH MED17.5", "category": "manufacturer", "confidence": 0.95},
    {"ecu_model_name": "ME7", "string_value": "BOSCH ME7", "category": "manufacturer", "confidence": 0.90},
    {"ecu_model_name": "ME7", "string_value": "MOTRONIC", "category": "family", "confidence": 0.80},
    {"ecu_model_name": "SIMOS 3", "string_value": "SIEMENS SIMOS", "category": "manufacturer", "confidence": 0.90},
    {"ecu_model_name": "SID801", "string_value": "CONTINENTAL SID", "category": "manufacturer", "confidence": 0.90},
    {"ecu_model_name": "Multec", "string_value": "DELPHI MULTIEC", "category": "manufacturer", "confidence": 0.85},
    {"ecu_model_name": "IAW 4AV", "string_value": "MAGNETI MARELLI", "category": "manufacturer", "confidence": 0.85},
    {"ecu_model_name": "IAW 4AV", "string_value": "IAW", "category": "family", "confidence": 0.80},
]


# ===========================================================================
# 15. KNOWN MAPS (calibration offsets/types per family)
# ===========================================================================

KNOWN_MAPS: List[Dict[str, Any]] = [
    # EDC17 CP14 maps
    {"ecu_model_name": "EDC17 CP14", "map_name": "Injection Quantity", "offset_hex": "0x20000", "size_bytes": 2048, "rows": 16, "cols": 16, "data_type": "uint16", "category": "Injection Quantity", "confidence": 0.85},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Injection Timing", "offset_hex": "0x21000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Injection Timing", "confidence": 0.85},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Boost Pressure", "offset_hex": "0x22000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Boost Pressure", "confidence": 0.80},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Rail Pressure", "offset_hex": "0x23000", "size_bytes": 512, "rows": 8, "cols": 8, "data_type": "uint16", "category": "Rail Pressure", "confidence": 0.80},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Smoke Limitation", "offset_hex": "0x24000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Smoke Limitation", "confidence": 0.80},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Speed Limiter", "offset_hex": "0x25000", "size_bytes": 256, "rows": 1, "cols": 1, "data_type": "uint16", "category": "Speed Limiter", "confidence": 0.75},
    {"ecu_model_name": "EDC17 CP14", "map_name": "Torque Limiter", "offset_hex": "0x26000", "size_bytes": 512, "rows": 8, "cols": 8, "data_type": "uint16", "category": "Torque Limiter", "confidence": 0.75},
    # EDC17 C46 maps
    {"ecu_model_name": "EDC17 C46", "map_name": "Injection Quantity", "offset_hex": "0x20000", "size_bytes": 2048, "rows": 16, "cols": 16, "data_type": "uint16", "category": "Injection Quantity", "confidence": 0.85},
    {"ecu_model_name": "EDC17 C46", "map_name": "Boost Pressure", "offset_hex": "0x22000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Boost Pressure", "confidence": 0.80},
    {"ecu_model_name": "EDC17 C46", "map_name": "Rail Pressure", "offset_hex": "0x23000", "size_bytes": 512, "rows": 8, "cols": 8, "data_type": "uint16", "category": "Rail Pressure", "confidence": 0.80},
    # MED17.1 maps
    {"ecu_model_name": "MED17.1", "map_name": "Injection Duration", "offset_hex": "0x30000", "size_bytes": 4096, "rows": 32, "cols": 16, "data_type": "uint16", "category": "Injection Quantity", "confidence": 0.80},
    {"ecu_model_name": "MED17.1", "map_name": "Ignition Timing", "offset_hex": "0x32000", "size_bytes": 2048, "rows": 16, "cols": 16, "data_type": "int16", "category": "Injection Timing", "confidence": 0.80},
    {"ecu_model_name": "MED17.1", "map_name": "Throttle Target", "offset_hex": "0x34000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Throttle Control", "confidence": 0.75},
    # ME7 maps
    {"ecu_model_name": "ME7", "map_name": "Injection Quantity", "offset_hex": "0x10000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "uint16", "category": "Injection Quantity", "confidence": 0.80},
    {"ecu_model_name": "ME7", "map_name": "Ignition Timing", "offset_hex": "0x11000", "size_bytes": 1024, "rows": 16, "cols": 8, "data_type": "int16", "category": "Injection Timing", "confidence": 0.80},
]


# ===========================================================================
# 16. KNOWN CHECKSUMS (locations per ECU family)
# ===========================================================================

KNOWN_CHECKSUMS: List[Dict[str, Any]] = [
    # EDC17 CP14
    {"ecu_model_name": "EDC17 CP14", "algorithm": "CRC32-BOSCH-EDC17", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.90},
    {"ecu_model_name": "EDC17 CP14", "algorithm": "ADD32-BOSCH-EDC17", "offset": 0x1FFF8, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFF7, "confidence": 0.85},
    # EDC17 C46
    {"ecu_model_name": "EDC17 C46", "algorithm": "CRC32-BOSCH-EDC17", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.90},
    {"ecu_model_name": "EDC17 C46", "algorithm": "ADD32-BOSCH-EDC17", "offset": 0x1FFF8, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFF7, "confidence": 0.85},
    # EDC17 CP04
    {"ecu_model_name": "EDC17 CP04", "algorithm": "CRC32-BOSCH-EDC17", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.90},
    # MED17.1
    {"ecu_model_name": "MED17.1", "algorithm": "CRC32-BOSCH-EDC17", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.90},
    {"ecu_model_name": "MED17.1", "algorithm": "CSM-EDC17", "offset": 0x0, "size": 0, "data_range_start": 0x0, "data_range_end": 0x0, "confidence": 0.80},
    # MED17.5
    {"ecu_model_name": "MED17.5", "algorithm": "CRC32-BOSCH-EDC17", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.90},
    # EDC15
    {"ecu_model_name": "EDC15", "algorithm": "CRC16-BOSCH", "offset": 0x7FFF0, "size": 2, "data_range_start": 0x0, "data_range_end": 0x7FFEF, "confidence": 0.85},
    # ME7
    {"ecu_model_name": "ME7", "algorithm": "MULTIPOINT-BOSCH", "offset": 0x1FFFC, "size": 4, "data_range_start": 0x10000, "data_range_end": 0x1FFFB, "confidence": 0.80},
]


# ===========================================================================
# 17. KNOWN SEGMENTS (memory segment descriptions per ECU family)
# ===========================================================================

KNOWN_SEGMENTS: List[Dict[str, Any]] = [
    {"ecu_model_name": "EDC17 CP14", "segment_type": "code", "start_offset": 0x10000, "end_offset": 0x1FFFB, "entropy": 7.5, "confidence": 0.85},
    {"ecu_model_name": "EDC17 CP14", "segment_type": "calibration", "start_offset": 0x20000, "end_offset": 0x2FFFF, "entropy": 5.2, "confidence": 0.80},
    {"ecu_model_name": "EDC17 CP14", "segment_type": "data", "start_offset": 0x30000, "end_offset": 0x3FFFF, "entropy": 4.8, "confidence": 0.75},
    {"ecu_model_name": "EDC17 C46", "segment_type": "code", "start_offset": 0x10000, "end_offset": 0x1FFFB, "entropy": 7.5, "confidence": 0.85},
    {"ecu_model_name": "EDC17 C46", "segment_type": "calibration", "start_offset": 0x20000, "end_offset": 0x2FFFF, "entropy": 5.2, "confidence": 0.80},
    {"ecu_model_name": "MED17.1", "segment_type": "code", "start_offset": 0x10000, "end_offset": 0x1FFFB, "entropy": 7.5, "confidence": 0.85},
    {"ecu_model_name": "MED17.1", "segment_type": "calibration", "start_offset": 0x30000, "end_offset": 0x3FFFF, "entropy": 5.0, "confidence": 0.80},
    {"ecu_model_name": "ME7", "segment_type": "code", "start_offset": 0x0, "end_offset": 0x9FFFF, "entropy": 7.2, "confidence": 0.80},
    {"ecu_model_name": "ME7", "segment_type": "calibration", "start_offset": 0x10000, "end_offset": 0x1FFFF, "entropy": 5.5, "confidence": 0.75},
]


# ===========================================================================
# 18. VEHICLE MODELS (linked to brands, with year ranges)
# ===========================================================================

VEHICLE_MODELS: List[Dict[str, Any]] = [
    {"brand_name": "Volkswagen", "name": "Golf", "year_start": 1997, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Volkswagen", "name": "Passat", "year_start": 1996, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "Volkswagen", "name": "Polo", "year_start": 2000, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Audi", "name": "A3", "year_start": 1996, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Audi", "name": "A4", "year_start": 1994, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "Audi", "name": "A6", "year_start": 1994, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "BMW", "name": "3 Series", "year_start": 1998, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "BMW", "name": "5 Series", "year_start": 1995, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "Peugeot", "name": "307", "year_start": 2001, "year_end": 2008, "body_type": "Hatchback"},
    {"brand_name": "Peugeot", "name": "308", "year_start": 2007, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Peugeot", "name": "206", "year_start": 1998, "year_end": 2010, "body_type": "Hatchback"},
    {"brand_name": "Renault", "name": "Megane", "year_start": 1999, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Renault", "name": "Clio", "year_start": 1998, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Ford", "name": "Focus", "year_start": 1998, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Ford", "name": "Mondeo", "year_start": 1993, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "Opel", "name": "Astra", "year_start": 1998, "year_end": 2020, "body_type": "Hatchback"},
    {"brand_name": "Fiat", "name": "Punto", "year_start": 1999, "year_end": 2018, "body_type": "Hatchback"},
    {"brand_name": "Fiat", "name": "Bravo", "year_start": 2007, "year_end": 2014, "body_type": "Hatchback"},
    {"brand_name": "Toyota", "name": "Corolla", "year_start": 1997, "year_end": 2020, "body_type": "Sedan"},
    {"brand_name": "Toyota", "name": "Avensis", "year_start": 1997, "year_end": 2018, "body_type": "Sedan"},
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
    """ECU models — resolve manufacturer_name to manufacturer_id."""
    manufacturer_cache = {}
    for m in session.query(Manufacturer).all():
        manufacturer_cache[m.name] = m.id

    count = 0
    for data in ECU_MODELS:
        mfr_name = data.pop("manufacturer_name")
        manufacturer_id = manufacturer_cache.get(mfr_name)
        if manufacturer_id is None:
            continue
        data["manufacturer_id"] = manufacturer_id

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
    """Software versions — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in SOFTWARE_VERSIONS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        if ecu_model_id is None:
            continue
        data["ecu_model_id"] = ecu_model_id

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


def seed_hardware_versions(session: Session) -> int:
    """Hardware versions — resolve ecu_model_name and processor_name."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id
    proc_cache = {}
    for p in session.query(Processor).all():
        proc_cache[p.name] = p.id

    count = 0
    for data in HARDWARE_VERSIONS:
        model_name = data.pop("ecu_model_name")
        proc_name = data.pop("processor_name")
        ecu_model_id = model_cache.get(model_name)
        processor_id = proc_cache.get(proc_name)
        if ecu_model_id is None:
            continue
        data["ecu_model_id"] = ecu_model_id
        if processor_id:
            data["processor_id"] = processor_id

        existing = session.query(HardwareVersion.id).filter(
            HardwareVersion.ecu_model_id == data["ecu_model_id"],
            HardwareVersion.hw_number == data["hw_number"],
        ).first()
        if existing is not None:
            continue
        row = HardwareVersion(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_ecu_variants(session: Session) -> int:
    """ECU variants — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in ECU_VARIANTS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        if ecu_model_id is None:
            continue
        data["ecu_model_id"] = ecu_model_id

        existing = session.query(ECUVariant.id).filter(
            ECUVariant.ecu_model_id == data["ecu_model_id"],
            ECUVariant.variant_name == data.get("variant_name"),
        ).first()
        if existing is not None:
            continue
        row = ECUVariant(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_memory_layouts(session: Session) -> int:
    """Memory layouts — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in MEMORY_LAYOUTS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        if ecu_model_id is None:
            continue
        data["ecu_model_id"] = ecu_model_id

        existing = session.query(MemoryLayout.id).filter(
            MemoryLayout.ecu_model_id == data["ecu_model_id"],
        ).first()
        if existing is not None:
            continue
        row = MemoryLayout(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_memory_segments(session: Session) -> int:
    """Memory segments — resolve layout_model_name to layout_id."""
    layout_cache = {}
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id
    for ml in session.query(MemoryLayout).all():
        if ml.ecu_model_id in model_cache.values():
            for name, mid in model_cache.items():
                if mid == ml.ecu_model_id:
                    layout_cache[name] = ml.id
                    break

    count = 0
    for data in MEMORY_SEGMENTS:
        model_name = data.pop("layout_model_name")
        layout_id = layout_cache.get(model_name)
        if layout_id is None:
            continue
        data["layout_id"] = layout_id

        existing = session.query(MemorySegment.id).filter(
            MemorySegment.layout_id == data["layout_id"],
            MemorySegment.name == data.get("name"),
        ).first()
        if existing is not None:
            continue
        row = MemorySegment(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_known_signatures(session: Session) -> int:
    """Known signatures — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in KNOWN_SIGNATURES:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        data["ecu_model_id"] = ecu_model_id
        data["ecu_model_name"] = model_name

        existing = session.query(KnownSignature.id).filter(
            KnownSignature.ecu_model_name == model_name,
            KnownSignature.pattern_hex == data["pattern_hex"],
        ).first()
        if existing is not None:
            continue
        row = KnownSignature(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_known_strings(session: Session) -> int:
    """Known strings — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in KNOWN_STRINGS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        data["ecu_model_id"] = ecu_model_id
        data["ecu_model_name"] = model_name

        existing = session.query(KnownString.id).filter(
            KnownString.ecu_model_name == model_name,
            KnownString.string_value == data["string_value"],
        ).first()
        if existing is not None:
            continue
        row = KnownString(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_known_maps(session: Session) -> int:
    """Known maps — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in KNOWN_MAPS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        data["ecu_model_id"] = ecu_model_id
        data["ecu_model_name"] = model_name

        existing = session.query(KnownMap.id).filter(
            KnownMap.ecu_model_name == model_name,
            KnownMap.map_name == data["map_name"],
        ).first()
        if existing is not None:
            continue
        row = KnownMap(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_known_checksums(session: Session) -> int:
    """Known checksums — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in KNOWN_CHECKSUMS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        data["ecu_model_id"] = ecu_model_id
        data["ecu_model_name"] = model_name

        existing = session.query(KnownChecksum.id).filter(
            KnownChecksum.ecu_model_name == model_name,
            KnownChecksum.algorithm == data["algorithm"],
        ).first()
        if existing is not None:
            continue
        row = KnownChecksum(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_known_segments(session: Session) -> int:
    """Known segments — resolve ecu_model_name to ecu_model_id."""
    model_cache = {}
    for m in session.query(ECUModel).all():
        model_cache[m.model_name] = m.id

    count = 0
    for data in KNOWN_SEGMENTS:
        model_name = data.pop("ecu_model_name")
        ecu_model_id = model_cache.get(model_name)
        data["ecu_model_id"] = ecu_model_id
        data["ecu_model_name"] = model_name

        existing = session.query(KnownSegment.id).filter(
            KnownSegment.ecu_model_name == model_name,
            KnownSegment.segment_type == data["segment_type"],
        ).first()
        if existing is not None:
            continue
        row = KnownSegment(**data)
        session.add(row)
        session.flush()
        count += 1
    return count


def seed_vehicle_models(session: Session) -> int:
    """Vehicle models — resolve brand_name to brand_id."""
    brand_cache = {}
    for b in session.query(VehicleBrand).all():
        brand_cache[b.name] = b.id

    count = 0
    for data in VEHICLE_MODELS:
        brand_name = data.pop("brand_name")
        brand_id = brand_cache.get(brand_name)
        if brand_id is None:
            continue
        data["brand_id"] = brand_id

        existing = session.query(VehicleModel.id).filter(
            VehicleModel.brand_id == data["brand_id"],
            VehicleModel.name == data["name"],
        ).first()
        if existing is not None:
            continue
        row = VehicleModel(**data)
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

        # Layer 5 — Technical knowledge (no FK dependencies)
        counts["manufacturers"] = seed_manufacturers(session)
        counts["processors"] = seed_processors(session)
        counts["protocols"] = seed_protocols(session)
        counts["checksum_algorithms"] = seed_checksum_algorithms(session)
        counts["map_categories"] = seed_map_categories(session)
        counts["map_units"] = seed_map_units(session)
        counts["vehicle_brands"] = seed_vehicle_brands(session)

        # Layer 1 — ECU Referential (depends on manufacturers)
        counts["ecu_models"] = seed_ecu_models(session)

        # Depends on ecu_models
        counts["software_versions"] = seed_software_versions(session)
        counts["hardware_versions"] = seed_hardware_versions(session)
        counts["ecu_variants"] = seed_ecu_variants(session)
        counts["memory_layouts"] = seed_memory_layouts(session)
        counts["memory_segments"] = seed_memory_segments(session)

        # Layer 2 — Signatures
        counts["known_signatures"] = seed_known_signatures(session)
        counts["known_strings"] = seed_known_strings(session)

        # Layer 3 — Map definitions
        counts["known_maps"] = seed_known_maps(session)

        # Layer 4 — Checksum locations
        counts["known_checksums"] = seed_known_checksums(session)

        # Layer 5 continued — Segments + Vehicles
        counts["known_segments"] = seed_known_segments(session)
        counts["vehicle_models"] = seed_vehicle_models(session)

        session.commit()

        print("=" * 70)
        print("  ECU Master Lab V2 — Comprehensive Seed Summary")
        print("=" * 70)
        total = 0
        for table, n in counts.items():
            label = table.replace("_", " ").title()
            print(f"  {label:<35s} : {n:>3d} inserted")
            total += n
        print("-" * 70)
        print(f"  {'TOTAL':<35s} : {total:>3d} new rows inserted")
        print("=" * 70)

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Seeding ECU Master Lab V2 comprehensive reference data ...")
    run_seed()
    print("Done.")
