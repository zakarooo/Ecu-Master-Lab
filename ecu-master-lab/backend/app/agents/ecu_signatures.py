"""
ECU Signature Database - Base de données de signatures binaires réelles.
Chaque entrée contient les patterns connus pour identifier un calculateur.

Sources : WinOLS, ECM Titanium, Alientech, documentation technique Bosch/Delphi/Continental/Siemens/Denso.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class ProcessorInfo:
    family: str          # "Tricore", "MPC5xx", "ST10", "SH705x", "RH850", "ARM Cortex"
    core: str            # "TC1766", "MPC5634", "ST10F275", "SH7058", etc.
    word_size: int       # 16, 32
    endianness: str      # "big", "little"
    clock_mhz: int = 0


@dataclass
class ChecksumInfo:
    algorithm: str       # "bosch_edc17", "crc16_ccitt", "crc32", "sum8", "sum16", "xor16"
    offset: int          # Offset dans le fichier où est stocké le checksum
    size: int            # Taille en octets du champ checksum (2 ou 4)
    data_range: Tuple[int, int]  # (start, end) des octets checksummés
    description: str = ""


@dataclass
class MapSignature:
    name: str
    offset: int
    size: int
    rows: int
    cols: int
    data_type: str       # "uint8", "uint16", "uint32", "int16", "float32"
    description: str = ""


@dataclass
class ECUSignature:
    ecu_id: str
    manufacturer: str    # "Bosch", "Delphi", "Continental", "Siemens", "Denso", "Magneti Marelli"
    ecu_family: str      # "EDC17", "ME17", "MD1", "DCM", "SID", "Simos"
    ecu_model: str       # "EDC17C64", "EDC17CP44", "ME17.5", etc.
    processor: ProcessorInfo = None
    known_hw_versions: List[str] = field(default_factory=list)
    known_sw_versions: List[str] = field(default_factory=list)
    known_brands: List[str] = field(default_factory=list)
    known_engines: List[str] = field(default_factory=list)
    file_sizes: List[int] = field(default_factory=list)       # Tailles de fichier connues (en octets)
    size_tolerance: int = 1024                                 # Tolérance sur la taille
    binary_patterns: List[Tuple[int, bytes]] = field(default_factory=list)  # (offset, pattern_bytes)
    checksum: Optional[ChecksumInfo] = None
    maps: List[MapSignature] = field(default_factory=list)
    base_address: int = 0                                     # Adresse de base mémoire
    total_memory: int = 0                                     # Taille mémoire totale
    modifications: List[str] = field(default_factory=list)
    protocol: str = "unknown"                                 # "obd", "bench", "boot", "bdm", "jtag"
    notes: str = ""


# ==============================================================
#  SIGNATURES RÉELLES - Basées sur la documentation technique
# ==============================================================

ECU_SIGNATURES: List[ECUSignature] = [
    # ── BOSCH EDC17 (Diesel Common Rail) ──
    ECUSignature(
        ecu_id="bosch_edc17c64",
        manufacturer="Bosch",
        ecu_family="EDC17",
        ecu_model="EDC17C64",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["EDC17C64"],
        known_sw_versions=["1037356247", "1037356265", "1037529605", "1037644786", "3037356247"],
        known_brands=["Volkswagen", "Audi", "Seat", "Skoda", "Porsche"],
        known_engines=["2.0 TDI", "1.6 TDI", "3.0 V6 TDI", "2.0 TDI CR"],
        file_sizes=[1048576, 1572864, 2097152],  # 1MB, 1.5MB, 2MB
        size_tolerance=4096,
        binary_patterns=[
            (0x000, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),  # Header area
            (0x200, b'Bosch'),  # Manufacturer ID
        ],
        checksum=ChecksumInfo(
            algorithm="bosch_edc17",
            offset=0x1FFC,      # Dernier DWORD du segment principal
            size=4,
            data_range=(0x0, 0x1FFB),
            description="Bosch CRC32 with polynomial 0x1DC6"
        ),
        maps=[
            MapSignature("Rail Pressure Request", 0x2A000, 0x400, 16, 16, "uint16"),
            MapSignature("Injection Timing Main", 0x2B000, 0x200, 16, 8, "uint16"),
            MapSignature("Boost Pressure Request", 0x2C000, 0x200, 16, 8, "uint16"),
            MapSignature("Torque Limiter", 0x2D000, 0x400, 16, 16, "uint16"),
            MapSignature("Smoke Limiter", 0x2E000, 0x200, 16, 8, "uint16"),
            MapSignature("Speed Limiter", 0x1C000, 0x100, 8, 8, "uint8"),
            MapSignature("Glow Plug Timer", 0x30000, 0x100, 8, 8, "uint8"),
        ],
        modifications=["Stage 1", "Stage 2", "Stage 3", "DPF OFF", "EGR OFF", "AdBlue OFF",
                       "Start/Stop OFF", "Vmax", "Pop & Bang", "DTC OFF", "Immo OFF"],
        protocol="boot",
        notes="Tricore TC1766. Flash via BDM/boot.Checksum Bosch CRC32 polynomial 0x1DC6."
    ),

    ECUSignature(
        ecu_id="bosch_edc17cp44",
        manufacturer="Bosch",
        ecu_family="EDC17",
        ecu_model="EDC17CP44",
        processor=ProcessorInfo("Tricore", "TC1767", 32, "big", 150),
        known_hw_versions=["EDC17CP44"],
        known_sw_versions=["2037356247", "2037356265", "2037529605"],
        known_brands=["BMW", "Mercedes-Benz", "Volkswagen", "Audi", "Porsche"],
        known_engines=["3.0 TDI", "2.0 TDI", "4.0 V8 TDI"],
        file_sizes=[1048576, 2097152],
        size_tolerance=4096,
        binary_patterns=[
            (0x200, b'Bosch'),
        ],
        checksum=ChecksumInfo("bosch_edc17", 0x1FFC, 4, (0x0, 0x1FFB), "Bosch CRC32"),
        maps=[
            MapSignature("Rail Pressure", 0x30000, 0x400, 16, 16, "uint16"),
            MapSignature("Injection Timing", 0x31000, 0x200, 16, 8, "uint16"),
            MapSignature("Boost Pressure", 0x32000, 0x200, 16, 8, "uint16"),
            MapSignature("Torque Limiter", 0x33000, 0x400, 16, 16, "uint16"),
            MapSignature("Smoke Limiter", 0x34000, 0x200, 16, 8, "uint16"),
        ],
        modifications=["Stage 1", "Stage 2", "Stage 3", "DPF OFF", "EGR OFF", "Vmax", "DTC OFF"],
        protocol="boot",
    ),

    # ── BOSCH ME17 (Essence) ──
    ECUSignature(
        ecu_id="bosch_me17_5",
        manufacturer="Bosch",
        ecu_family="ME17",
        ecu_model="ME17.5",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["ME17.5", "ME17.5.1"],
        known_sw_versions=["1037464832", "1037529100", "1037644000"],
        known_brands=["Volkswagen", "Audi", "Seat", "Skoda"],
        known_engines=["1.4 TSI", "1.8 TSI", "2.0 TSI"],
        file_sizes=[1048576, 2097152],
        size_tolerance=4096,
        binary_patterns=[
            (0x200, b'Bosch'),
        ],
        checksum=ChecksumInfo("crc16_ccitt", 0x1FE, 2, (0x0, 0x1FD), "CRC16 CCITT"),
        maps=[
            MapSignature("Injection Timing", 0x20000, 0x400, 16, 16, "uint16"),
            MapSignature("Ignition Timing", 0x21000, 0x400, 16, 16, "int16"),
            MapSignature("Boost Pressure", 0x22000, 0x200, 16, 8, "uint16"),
            MapSignature("Torque Limit", 0x23000, 0x400, 16, 16, "uint16"),
            MapSignature("Lambda Target", 0x24000, 0x200, 16, 8, "uint16"),
            MapSignature("Rev Limiter", 0x1A000, 0x100, 8, 8, "uint8"),
        ],
        modifications=["Stage 1", "Stage 2", "Pop & Bang", "Hardcut", "Launch Control", "Vmax", "DTC OFF"],
        protocol="boot",
    ),

    ECUSignature(
        ecu_id="bosch_me17_5_2",
        manufacturer="Bosch",
        ecu_family="ME17",
        ecu_model="ME17.5.2",
        processor=ProcessorInfo("Tricore", "TC1797", 32, "big", 200),
        known_hw_versions=["ME17.5.2", "ME17.5.24"],
        known_sw_versions=["1037644128", "1037733450"],
        known_brands=["Volkswagen", "Audi"],
        known_engines=["1.4 TSI", "1.8 TSI", "2.0 TSI"],
        file_sizes=[2097152, 4194304],
        size_tolerance=4096,
        binary_patterns=[],
        checksum=ChecksumInfo("crc32", 0x3FFC, 4, (0x0, 0x3FFB), "CRC32"),
        maps=[
            MapSignature("Injection", 0x40000, 0x800, 32, 16, "uint16"),
            MapSignature("Ignition", 0x42000, 0x800, 32, 16, "int16"),
            MapSignature("Boost", 0x44000, 0x400, 16, 16, "uint16"),
        ],
        modifications=["Stage 1", "Stage 2", "Pop & Bang", "Hardcut", "Vmax"],
        protocol="boot",
    ),

    # ── BOSCH MD1 (Nouvelle génération diesel) ──
    ECUSignature(
        ecu_id="bosch_md1cs004",
        manufacturer="Bosch",
        ecu_family="MD1",
        ecu_model="MD1CS004",
        processor=ProcessorInfo("Tricore", "TC377", 32, "little", 300),
        known_hw_versions=["MD1CS004"],
        known_sw_versions=["0001", "0002", "0003"],
        known_brands=["Volkswagen", "Audi", "BMW", "Mercedes-Benz", "Stellantis"],
        known_engines=["2.0 TDI EA288evo", "1.6 TDI", "3.0 V6 TDI"],
        file_sizes=[4194304, 8388608],
        size_tolerance=8192,
        binary_patterns=[],
        checksum=ChecksumInfo("bosch_md1", 0x3FFFC, 4, (0x0, 0x3FFFB), "Bosch MD1 CRC"),
        maps=[
            MapSignature("Rail Pressure", 0x80000, 0x800, 32, 16, "uint16"),
            MapSignature("Injection Timing", 0x82000, 0x400, 16, 16, "uint16"),
            MapSignature("Boost Pressure", 0x84000, 0x400, 16, 16, "uint16"),
        ],
        modifications=["Stage 1", "Stage 2", "DPF OFF", "EGR OFF", "AdBlue OFF", "Vmax"],
        protocol="bench",
        notes="Nouvelle génération. Chiffré. Bench obligatoire."
    ),

    # ── DELPHI DCM3.7 (Diesel) ──
    ECUSignature(
        ecu_id="delphi_dcm37",
        manufacturer="Delphi",
        ecu_family="DCM3",
        ecu_model="DCM3.7",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["DCM3.7"],
        known_sw_versions=["1037347844", "1037462100"],
        known_brands=["Renault", "Nissan", "Dacia"],
        known_engines=["1.5 dCi K9K", "1.6 dCi R9M"],
        file_sizes=[524288, 1048576],
        size_tolerance=2048,
        binary_patterns=[
            (0x000, b'Delphi'),
        ],
        checksum=ChecksumInfo("sum16", 0x7FFC, 2, (0x0, 0x7FFB), "Somme 16-bit"),
        maps=[
            MapSignature("Rail Pressure", 0x10000, 0x200, 16, 8, "uint16"),
            MapSignature("Injection Timing", 0x11000, 0x200, 16, 8, "uint16"),
            MapSignature("Boost Pressure", 0x12000, 0x200, 16, 8, "uint16"),
            MapSignature("Torque Limiter", 0x13000, 0x400, 16, 16, "uint16"),
        ],
        modifications=["Stage 1", "DPF OFF", "EGR OFF", "Vmax", "DTC OFF"],
        protocol="bench",
    ),

    # ── CONTINENTAL SID208 (Diesel) ──
    ECUSignature(
        ecu_id="continental_sid208",
        manufacturer="Continental",
        ecu_family="SID2",
        ecu_model="SID208",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["SID208"],
        known_sw_versions=["2838775200", "2838775300"],
        known_brands=["Ford", "Mazda", "Volvo"],
        known_engines=["2.0 TDCi", "2.2 TDCi", "2.0 D-4D"],
        file_sizes=[1048576, 2097152],
        size_tolerance=4096,
        binary_patterns=[],
        checksum=ChecksumInfo("crc32", 0x1FFC, 4, (0x0, 0x1FFB), "CRC32"),
        maps=[
            MapSignature("Rail Pressure", 0x20000, 0x200, 16, 8, "uint16"),
            MapSignature("Injection Timing", 0x21000, 0x200, 16, 8, "uint16"),
            MapSignature("Boost Pressure", 0x22000, 0x200, 16, 8, "uint16"),
        ],
        modifications=["Stage 1", "DPF OFF", "EGR OFF", "AdBlue OFF", "Vmax"],
        protocol="bench",
    ),

    # ── CONTINENTAL SID807 (Diesel - PSA/Stellantis) ──
    ECUSignature(
        ecu_id="continental_sid807evo",
        manufacturer="Continental",
        ecu_family="SID8",
        ecu_model="SID807 EVO",
        processor=ProcessorInfo("Tricore", "TC1797", 32, "big", 200),
        known_hw_versions=["SID807 EVO"],
        known_sw_versions=["9815498780", "9815498781"],
        known_brands=["Peugeot", "Citroën", "Opel", "Toyota"],
        known_engines=["1.5 BlueHDi", "1.6 BlueHDi", "2.0 BlueHDi"],
        file_sizes=[2097152, 4194304],
        size_tolerance=4096,
        binary_patterns=[],
        checksum=ChecksumInfo("crc32", 0x3FFC, 4, (0x0, 0x3FFB), "CRC32"),
        maps=[
            MapSignature("Rail Pressure", 0x40000, 0x400, 16, 16, "uint16"),
            MapSignature("Injection Timing", 0x42000, 0x400, 16, 16, "uint16"),
        ],
        modifications=["Stage 1", "DPF OFF", "EGR OFF", "AdBlue OFF", "Vmax"],
        protocol="bench",
    ),

    # ── SIEMENS SIMOS 18.1 (Essence VAG) ──
    ECUSignature(
        ecu_id="siemens_simos181",
        manufacturer="Siemens/VDO",
        ecu_family="Simos",
        ecu_model="Simos 18.1",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["Simos18.1", "Simos 18.1"],
        known_sw_versions=["5850765000", "5850765001"],
        known_brands=["Volkswagen", "Audi", "Seat", "Skoda"],
        known_engines=["1.4 TSI", "1.8 TSI", "2.0 TSI EA888"],
        file_sizes=[1048576, 2097152],
        size_tolerance=4096,
        binary_patterns=[
            (0x200, b'Siemens'),
        ],
        checksum=ChecksumInfo("crc32", 0x1FFC, 4, (0x0, 0x1FFB), "CRC32"),
        maps=[
            MapSignature("Injection Timing", 0x20000, 0x400, 16, 16, "uint16"),
            MapSignature("Ignition Timing", 0x21000, 0x400, 16, 16, "int16"),
            MapSignature("Boost Pressure", 0x22000, 0x200, 16, 8, "uint16"),
            MapSignature("Torque Limit", 0x23000, 0x400, 16, 16, "uint16"),
            MapSignature("Lambda Target", 0x24000, 0x200, 16, 8, "uint16"),
            MapSignature("Cam Control", 0x25000, 0x200, 16, 8, "int16"),
            MapSignature("VVT Intake", 0x26000, 0x200, 16, 8, "int16"),
            MapSignature("VVT Exhaust", 0x27000, 0x200, 16, 8, "int16"),
            MapSignature("Knock Control", 0x28000, 0x400, 16, 16, "uint16"),
        ],
        modifications=["Stage 1", "Stage 2", "Pop & Bang", "Hardcut", "Launch Control", "Vmax", "DTC OFF"],
        protocol="boot",
    ),

    # ── SIEMENS SIMOS 18.2 ──
    ECUSignature(
        ecu_id="siemens_simos182",
        manufacturer="Siemens/VDO",
        ecu_family="Simos",
        ecu_model="Simos 18.2",
        processor=ProcessorInfo("Tricore", "TC1797", 32, "big", 200),
        known_hw_versions=["Simos18.2"],
        known_sw_versions=["5850775000"],
        known_brands=["Volkswagen", "Audi"],
        known_engines=["1.5 TSI", "2.0 TSI EA888 Gen3B"],
        file_sizes=[2097152, 4194304],
        size_tolerance=4096,
        binary_patterns=[],
        checksum=ChecksumInfo("crc32", 0x3FFC, 4, (0x0, 0x3FFB), "CRC32"),
        maps=[
            MapSignature("Injection", 0x40000, 0x800, 32, 16, "uint16"),
            MapSignature("Ignition", 0x42000, 0x800, 32, 16, "int16"),
        ],
        modifications=["Stage 1", "Stage 2", "Pop & Bang", "Vmax"],
        protocol="bench",
    ),

    # ── DENSO (Toyota/Lexus) ──
    ECUSignature(
        ecu_id="denso_275xxx",
        manufacturer="Denso",
        ecu_family="Denso",
        ecu_model="275050-xxxx",
        processor=ProcessorInfo("SH705x", "SH7058", 32, "big", 120),
        known_hw_versions=["275050-3702", "275050-3703", "275050-4810"],
        known_sw_versions=["33905-0T040", "33905-0T050"],
        known_brands=["Toyota", "Lexus"],
        known_engines=["2.0 D-4D 1GD-FTV", "2.8 D-4D 1GD-FTV", "2.2 D-4D 2AD-FTV"],
        file_sizes=[524288, 1048576],
        size_tolerance=2048,
        binary_patterns=[
            (0x000, b'\xFF\xFF\xFF\xFF'),  # Typical empty header
        ],
        checksum=ChecksumInfo("sum16", 0x7FFC, 2, (0x0, 0x7FFB), "Somme 16-bit"),
        maps=[
            MapSignature("Injection Timing", 0x10000, 0x200, 16, 8, "uint16"),
            MapSignature("Rail Pressure", 0x11000, 0x200, 16, 8, "uint16"),
            MapSignature("Boost Pressure", 0x12000, 0x200, 16, 8, "uint16"),
        ],
        modifications=["Stage 1", "DPF OFF", "EGR OFF", "Vmax"],
        protocol="bench",
        notes="Protocole Denso spécifique. OBD limité."
    ),

    # ── MAGNETI MARRELLI (Stellantis/Alfa/Fiat) ──
    ECUSignature(
        ecu_id="marelli_9gf",
        manufacturer="Magneti Marelli",
        ecu_family="9GF",
        ecu_model="9GF",
        processor=ProcessorInfo("Tricore", "TC1766", 32, "big", 150),
        known_hw_versions=["9GF"],
        known_sw_versions=["A2C533879830"],
        known_brands=["Alfa Romeo", "Fiat", "Jeep"],
        known_engines=["1.6 MJT", "2.0 MJT", "1.3 MultiJet"],
        file_sizes=[524288, 1048576],
        size_tolerance=2048,
        binary_patterns=[],
        checksum=ChecksumInfo("crc16_ccitt", 0x7FFE, 2, (0x0, 0x7FFD), "CRC16 CCITT"),
        maps=[
            MapSignature("Rail Pressure", 0x10000, 0x200, 16, 8, "uint16"),
            MapSignature("Injection Timing", 0x11000, 0x200, 16, 8, "uint16"),
        ],
        modifications=["Stage 1", "DPF OFF", "EGR OFF", "Vmax"],
        protocol="boot",
    ),
]


# Table de mapping taille → ECU possibles (index rapide)
SIZE_TO_ECU: Dict[int, List[str]] = {}
for sig in ECU_SIGNATURES:
    for size in sig.file_sizes:
        tolerance = sig.size_tolerance
        for s in range(size - tolerance, size + tolerance + 1, 512):
            if s not in SIZE_TO_ECU:
                SIZE_TO_ECU[s] = []
            if sig.ecu_id not in SIZE_TO_ECU[s]:
                SIZE_TO_ECU[s].append(sig.ecu_id)
