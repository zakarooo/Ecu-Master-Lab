"""
Modeles de donnees centraux du moteur ECU.

Toutes les dataclasses partagees entre les couches du pipeline.
Aucune dependance externe - uniquement stdlib Python 3.8.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any


# ==============================================================
#  ENUMERATIONS
# ==============================================================

class FileFormat(Enum):
    BINARY = "binary"
    INTEL_HEX = "intel_hex"
    MOTOROLA_S19 = "motorola_s19"
    S_RECORD = "s_record"
    COMPRESSED = "compressed"
    EMPTY = "empty"
    UNKNOWN = "unknown"


class ProcessorFamily(Enum):
    TRICORE = "Tricore"
    MPC5xx = "MPC5xx"
    MPC5xxx = "MPC5xxx"
    ST10 = "ST10"
    SH705x = "SH705x"
    SH725xx = "SH725xx"
    RH850 = "RH850"
    RENESAS = "Renesas"
    ARM_CORTEX = "ARM Cortex"
    INFINEON_166 = "Infineon C166"
    NEC_V850 = "NEC V850"
    MICROCHIP = "Microchip"
    UNKNOWN = "unknown"


class MemoryType(Enum):
    FLASH = "Flash"
    EEPROM = "EEPROM"
    OTP = "OTP"
    RAM = "RAM"
    UNKNOWN = "unknown"


class ECUManufacturer(Enum):
    BOSCH = "Bosch"
    DELPHI = "Delphi"
    CONTINENTAL = "Continental"
    SIEMENS = "Siemens"
    DENSO = "Denso"
    MAGNETI_MARELLI = "Magneti Marelli"
    VALEO = "Valeo"
    HITACHI = "Hitachi"
    KEIHIN = "Keihin"
    MITSUBISHI = "Mitsubishi"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class SegmentType(Enum):
    BOOT = "Boot"
    CODE = "Code"
    CALIBRATION = "Calibration"
    EEPROM = "EEPROM"
    OTP = "OTP"
    DATA = "Data"
    UNKNOWN = "Unknown"


class MapDataType(Enum):
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    FLOAT32 = "float32"
    UNKNOWN = "unknown"


# ==============================================================
#  COUCHE 1 : FORMAT
# ==============================================================

@dataclass
class FormatResult:
    format_type: FileFormat = FileFormat.UNKNOWN
    file_size: int = 0
    encoding: str = "unknown"
    ascii_ratio: float = 0.0
    null_ratio: float = 0.0
    ff_ratio: float = 0.0
    entropy: float = 0.0
    explanation: str = ""
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)


# ==============================================================
#  COUCHE 2 : PROCESSEUR
# ==============================================================

@dataclass
class ProcessorProfile:
    family: ProcessorFamily = ProcessorFamily.UNKNOWN
    core: str = ""
    manufacturer: str = ""
    word_size: int = 0
    endianness: str = "unknown"
    clock_mhz: int = 0
    flash_size: int = 0
    ram_size: int = 0
    extensions: List[str] = field(default_factory=list)
    known_ecus: List[str] = field(default_factory=list)


@dataclass
class ProcessorResult:
    detected: bool = False
    primary: Optional[ProcessorProfile] = None
    alternatives: List[ProcessorProfile] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""


# ==============================================================
#  COUCHE 3 : MEMOIRE
# ==============================================================

@dataclass
class MemoryRegion:
    mem_type: MemoryType = MemoryType.UNKNOWN
    start_address: int = 0
    end_address: int = 0
    size: int = 0
    description: str = ""


@dataclass
class MemoryLayout:
    regions: List[MemoryRegion] = field(default_factory=list)
    total_size: int = 0
    address_bus_width: int = 0
    data_bus_width: int = 0
    explanation: str = ""
    confidence: float = 0.0


# ==============================================================
#  COUCHE 4 : EXTRACTION INFOS
# ==============================================================

@dataclass
class TechnicalInfo:
    hw_number: str = ""
    sw_number: str = ""
    calibration_id: str = ""
    vin: str = ""
    software_version: str = ""
    cvn: str = ""
    engine_type: str = ""
    emission_standard: str = ""
    manufacturer_refs: List[str] = field(default_factory=list)
    serial_number: str = ""
    production_date: str = ""
    asam_id: str = ""
    raw_strings: Dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)


# ==============================================================
#  COUCHE 5 : SIGNATURES INTERNES
# ==============================================================

@dataclass
class FoundSignature:
    name: str = ""
    category: str = ""
    offset: int = 0
    size: int = 0
    description: str = ""
    severity: str = "info"
    matched_pattern: bytes = b""


@dataclass
class SignatureScanResult:
    signatures: List[FoundSignature] = field(default_factory=list)
    interrupt_vector_address: int = -1
    bootloader_present: bool = False
    crc_tables_found: int = 0
    scheduler_detected: bool = False
    diagnostics_present: bool = False
    can_ids_found: List[int] = field(default_factory=list)
    rsa_detected: bool = False
    confidence: float = 0.0
    explanation: str = ""


# ==============================================================
#  COUCHE 6 : SEGMENTS
# ==============================================================

@dataclass
class SegmentAnalysis:
    seg_type: SegmentType = SegmentType.UNKNOWN
    start_offset: int = 0
    end_offset: int = 0
    size: int = 0
    entropy: float = 0.0
    non_empty_ratio: float = 0.0
    unique_byte_count: int = 0
    data_patterns: List[str] = field(default_factory=list)
    is_valid: bool = False
    explanation: str = ""


@dataclass
class SegmentAnalysisResult:
    segments: List[SegmentAnalysis] = field(default_factory=list)
    total_code_bytes: int = 0
    total_calibration_bytes: int = 0
    coherence_score: float = 0.0
    explanation: str = ""


# ==============================================================
#  COUCHE 7 : CARTOGRAPHIES
# ==============================================================

@dataclass
class DetectedMap:
    name: str = ""
    category: str = ""
    offset: int = 0
    size: int = 0
    rows: int = 0
    cols: int = 0
    data_type: MapDataType = MapDataType.UNKNOWN
    min_value: float = 0.0
    max_value: float = 0.0
    avg_value: float = 0.0
    entropy: float = 0.0
    non_empty_ratio: float = 0.0
    status: str = "active"
    detection_method: str = ""
    explanation: str = ""
    damos_map_id: int = 0


@dataclass
class MapDetectionResult:
    maps: List[DetectedMap] = field(default_factory=list)
    total_map_bytes: int = 0
    total_maps_found: int = 0
    confidence: float = 0.0
    explanation: str = ""


# ==============================================================
#  COUCHE 8 : CHECKSUM
# ==============================================================

@dataclass
class ChecksumResult:
    algorithm: str = ""
    stored_value: str = ""
    computed_value: str = ""
    is_valid: Optional[bool] = None
    data_range: Tuple[int, int] = (0, 0)
    offset: int = 0
    size: int = 0
    explanation: str = ""
    needs_recalculation: bool = False


# ==============================================================
#  COUCHE 9 : VALIDATION CROISEE
# ==============================================================

@dataclass
class ECUCandidate:
    ecu_id: str = ""
    manufacturer: str = ""
    ecu_family: str = ""
    ecu_model: str = ""
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    match_scores: Dict[str, float] = field(default_factory=dict)
    rejected: bool = False
    rejection_reasons: List[str] = field(default_factory=list)


@dataclass
class CrossValidationResult:
    hypotheses: List[ECUCandidate] = field(default_factory=list)
    best_hypothesis: Optional[ECUCandidate] = None
    consensus_reached: bool = False
    explanation: str = ""


# ==============================================================
#  COUCHE 10 : RAPPORT
# ==============================================================

@dataclass
class ReportRisk:
    category: str = ""
    severity: str = ""
    message: str = ""
    evidence: str = ""


@dataclass
class ReviewReason:
    reason: str = ""
    severity: str = ""
    evidence: str = ""


@dataclass
class PipelineStep:
    step: int = 0
    name: str = ""
    status: str = "pending"
    duration_ms: float = 0.0
    confidence_contribution: float = 0.0
    result_summary: str = ""
    details: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ECUReport:
    file_name: str = ""
    file_size: int = 0
    file_hash_sha256: str = ""
    file_hash_md5: str = ""

    detected_ecu: str = "Inconnu"
    detected_manufacturer: str = "Inconnu"
    detected_ecu_family: str = "Inconnu"
    detected_ecu_model: str = "Inconnu"
    detected_hw_version: str = "Inconnu"
    detected_sw_version: str = "Inconnu"
    detected_brand: str = "Inconnu"
    detected_engine: str = "Inconnu"
    detected_protocol: str = "Inconnu"

    confidence: float = 0.0
    consistency_score: float = 0.0
    hypotheses: List[dict] = field(default_factory=list)

    checksum: Optional[ChecksumResult] = None
    format_result: Optional[FormatResult] = None
    processor_result: Optional[ProcessorResult] = None
    memory_layout: Optional[MemoryLayout] = None
    tech_info: Optional[TechnicalInfo] = None
    signatures: Optional[SignatureScanResult] = None
    segments: Optional[SegmentAnalysisResult] = None
    maps: Optional[MapDetectionResult] = None
    cross_validation: Optional[CrossValidationResult] = None

    compatible_modifications: List[str] = field(default_factory=list)
    risks: List[ReportRisk] = field(default_factory=list)
    review_reasons: List[ReviewReason] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    needs_review: bool = False
    is_auto_processable: bool = False

    pipeline_steps: List[PipelineStep] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    total_pipeline_time_ms: float = 0.0
