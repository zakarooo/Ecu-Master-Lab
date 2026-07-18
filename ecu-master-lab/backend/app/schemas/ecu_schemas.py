from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Referentiel
# ---------------------------------------------------------------------------

class ManufacturerCreate(BaseModel):
    name: str
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class ManufacturerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class ManufacturerUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class ECUModelCreate(BaseModel):
    manufacturer_id: int
    model_name: str
    family: Optional[str] = None
    processor_type: Optional[str] = None
    flash_size_kb: Optional[int] = None
    typical_brands: Optional[str] = None
    typical_engines: Optional[str] = None
    protocol: Optional[str] = None
    notes: Optional[str] = None


class ECUModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manufacturer_id: int
    model_name: str
    family: Optional[str] = None
    processor_type: Optional[str] = None
    flash_size_kb: Optional[int] = None
    typical_brands: Optional[str] = None
    typical_engines: Optional[str] = None
    protocol: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class ECUModelUpdate(BaseModel):
    manufacturer_id: Optional[int] = None
    model_name: Optional[str] = None
    family: Optional[str] = None
    processor_type: Optional[str] = None
    flash_size_kb: Optional[int] = None
    typical_brands: Optional[str] = None
    typical_engines: Optional[str] = None
    protocol: Optional[str] = None
    notes: Optional[str] = None


class ECUVariantCreate(BaseModel):
    ecu_model_id: int
    variant_name: str
    hw_revision: Optional[str] = None
    sw_revision: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum_type: Optional[str] = None
    is_encrypted: Optional[bool] = None
    notes: Optional[str] = None


class ECUVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    variant_name: str
    hw_revision: Optional[str] = None
    sw_revision: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum_type: Optional[str] = None
    is_encrypted: Optional[bool] = None
    notes: Optional[str] = None
    created_at: datetime


class ECUVariantUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    variant_name: Optional[str] = None
    hw_revision: Optional[str] = None
    sw_revision: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum_type: Optional[str] = None
    is_encrypted: Optional[bool] = None
    notes: Optional[str] = None


class ProcessorCreate(BaseModel):
    name: str
    family: str
    manufacturer: str
    architecture: str
    word_size: int
    endianness: str
    clock_mhz: Optional[float] = None
    flash_kb: Optional[int] = None
    ram_kb: Optional[int] = None
    extensions: Optional[str] = None
    known_ecus: Optional[str] = None


class ProcessorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    family: str
    manufacturer: str
    architecture: str
    word_size: int
    endianness: str
    clock_mhz: Optional[float] = None
    flash_kb: Optional[int] = None
    ram_kb: Optional[int] = None
    extensions: Optional[str] = None
    known_ecus: Optional[str] = None
    created_at: datetime


class ProcessorUpdate(BaseModel):
    name: Optional[str] = None
    family: Optional[str] = None
    manufacturer: Optional[str] = None
    architecture: Optional[str] = None
    word_size: Optional[int] = None
    endianness: Optional[str] = None
    clock_mhz: Optional[float] = None
    flash_kb: Optional[int] = None
    ram_kb: Optional[int] = None
    extensions: Optional[str] = None
    known_ecus: Optional[str] = None


class ProtocolCreate(BaseModel):
    name: str
    description: Optional[str] = None
    requires_bootloader: Optional[bool] = None
    typical_tools: Optional[str] = None


class ProtocolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    requires_bootloader: Optional[bool] = None
    typical_tools: Optional[str] = None
    created_at: datetime


class ProtocolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    requires_bootloader: Optional[bool] = None
    typical_tools: Optional[str] = None


class ChecksumAlgorithmCreate(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    polynomial: Optional[str] = None
    init_value: Optional[str] = None
    xor_out: Optional[str] = None
    description: Optional[str] = None


class ChecksumAlgorithmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: Optional[str] = None
    polynomial: Optional[str] = None
    init_value: Optional[str] = None
    xor_out: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class ChecksumAlgorithmUpdate(BaseModel):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    polynomial: Optional[str] = None
    init_value: Optional[str] = None
    xor_out: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

class VehicleBrandCreate(BaseModel):
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None


class VehicleBrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime


class VehicleBrandUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None


class VehicleModelCreate(BaseModel):
    brand_id: int
    name: str
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    body_type: Optional[str] = None


class VehicleModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    name: str
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    body_type: Optional[str] = None
    created_at: datetime


class VehicleModelUpdate(BaseModel):
    brand_id: Optional[int] = None
    name: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    body_type: Optional[str] = None


class VehicleEngineCreate(BaseModel):
    model_id: int
    engine_code: Optional[str] = None
    displacement_cc: Optional[float] = None
    fuel_type: Optional[str] = None
    power_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    emission_standard: Optional[str] = None
    ecu_model_id: Optional[int] = None


class VehicleEngineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    engine_code: Optional[str] = None
    displacement_cc: Optional[float] = None
    fuel_type: Optional[str] = None
    power_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    emission_standard: Optional[str] = None
    ecu_model_id: Optional[int] = None
    created_at: datetime


class VehicleEngineUpdate(BaseModel):
    model_id: Optional[int] = None
    engine_code: Optional[str] = None
    displacement_cc: Optional[float] = None
    fuel_type: Optional[str] = None
    power_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    emission_standard: Optional[str] = None
    ecu_model_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

class SoftwareVersionCreate(BaseModel):
    ecu_model_id: int
    sw_number: str
    hw_number: Optional[str] = None
    calibration_id: Optional[str] = None
    cvn: Optional[str] = None
    version_label: Optional[str] = None
    file_size: Optional[int] = None
    checksum_value: Optional[str] = None
    notes: Optional[str] = None


class SoftwareVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    sw_number: str
    hw_number: Optional[str] = None
    calibration_id: Optional[str] = None
    cvn: Optional[str] = None
    version_label: Optional[str] = None
    file_size: Optional[int] = None
    checksum_value: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class SoftwareVersionUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    sw_number: Optional[str] = None
    hw_number: Optional[str] = None
    calibration_id: Optional[str] = None
    cvn: Optional[str] = None
    version_label: Optional[str] = None
    file_size: Optional[int] = None
    checksum_value: Optional[str] = None
    notes: Optional[str] = None


class HardwareVersionCreate(BaseModel):
    ecu_model_id: int
    hw_number: str
    revision: Optional[str] = None
    board_type: Optional[str] = None
    processor_id: Optional[int] = None
    flash_size_kb: Optional[int] = None
    eeprom_size_kb: Optional[int] = None
    notes: Optional[str] = None


class HardwareVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    hw_number: str
    revision: Optional[str] = None
    board_type: Optional[str] = None
    processor_id: Optional[int] = None
    flash_size_kb: Optional[int] = None
    eeprom_size_kb: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


class HardwareVersionUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    hw_number: Optional[str] = None
    revision: Optional[str] = None
    board_type: Optional[str] = None
    processor_id: Optional[int] = None
    flash_size_kb: Optional[int] = None
    eeprom_size_kb: Optional[int] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class MemoryLayoutCreate(BaseModel):
    ecu_model_id: int
    total_size_bytes: int
    address_bus_width: Optional[int] = None
    data_bus_width: Optional[int] = None
    endianness: Optional[str] = None
    notes: Optional[str] = None


class MemoryLayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    total_size_bytes: int
    address_bus_width: Optional[int] = None
    data_bus_width: Optional[int] = None
    endianness: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class MemoryLayoutUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    total_size_bytes: Optional[int] = None
    address_bus_width: Optional[int] = None
    data_bus_width: Optional[int] = None
    endianness: Optional[str] = None
    notes: Optional[str] = None


class MemorySegmentCreate(BaseModel):
    layout_id: int
    name: str
    segment_type: str
    start_address: int
    end_address: int
    size_bytes: int
    permissions: Optional[str] = None
    description: Optional[str] = None


class MemorySegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    layout_id: int
    name: str
    segment_type: str
    start_address: int
    end_address: int
    size_bytes: int
    permissions: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class MemorySegmentUpdate(BaseModel):
    layout_id: Optional[int] = None
    name: Optional[str] = None
    segment_type: Optional[str] = None
    start_address: Optional[int] = None
    end_address: Optional[int] = None
    size_bytes: Optional[int] = None
    permissions: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Signatures
# ---------------------------------------------------------------------------

class ECUSignatureCreate(BaseModel):
    ecu_model_id: int
    signature_name: str
    pattern_hex: str
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    confidence_weight: Optional[float] = None
    description: Optional[str] = None


class ECUSignatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    signature_name: str
    pattern_hex: str
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    confidence_weight: Optional[float] = None
    description: Optional[str] = None
    created_at: datetime


class ECUSignatureUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    signature_name: Optional[str] = None
    pattern_hex: Optional[str] = None
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    confidence_weight: Optional[float] = None
    description: Optional[str] = None


class BinaryPatternCreate(BaseModel):
    ecu_model_id: int
    pattern_name: str
    pattern_hex: str
    offset_start: Optional[int] = None
    offset_end: Optional[int] = None
    byte_length: Optional[int] = None
    description: Optional[str] = None


class BinaryPatternResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    pattern_name: str
    pattern_hex: str
    offset_start: Optional[int] = None
    offset_end: Optional[int] = None
    byte_length: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime


class BinaryPatternUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    pattern_name: Optional[str] = None
    pattern_hex: Optional[str] = None
    offset_start: Optional[int] = None
    offset_end: Optional[int] = None
    byte_length: Optional[int] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Maps
# ---------------------------------------------------------------------------

class MapCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class MapCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    created_at: datetime


class MapCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class MapUnitCreate(BaseModel):
    symbol: str
    name: str
    unit_type: Optional[str] = None


class MapUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    unit_type: Optional[str] = None
    created_at: datetime


class MapUnitUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    unit_type: Optional[str] = None


class MapAxisCreate(BaseModel):
    name: str
    axis_type: str
    unit_id: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    num_points: Optional[int] = None
    description: Optional[str] = None


class MapAxisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    axis_type: str
    unit_id: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    num_points: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime


class MapAxisUpdate(BaseModel):
    name: Optional[str] = None
    axis_type: Optional[str] = None
    unit_id: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    num_points: Optional[int] = None
    description: Optional[str] = None


class MapCreate(BaseModel):
    ecu_model_id: int
    category_id: Optional[int] = None
    name: str
    address_hex: Optional[str] = None
    address_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    unit_id: Optional[int] = None
    axis_x_id: Optional[int] = None
    axis_y_id: Optional[int] = None
    description: Optional[str] = None


class MapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_model_id: int
    category_id: Optional[int] = None
    name: str
    address_hex: Optional[str] = None
    address_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    unit_id: Optional[int] = None
    axis_x_id: Optional[int] = None
    axis_y_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime


class MapUpdate(BaseModel):
    ecu_model_id: Optional[int] = None
    category_id: Optional[int] = None
    name: Optional[str] = None
    address_hex: Optional[str] = None
    address_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    unit_id: Optional[int] = None
    axis_x_id: Optional[int] = None
    axis_y_id: Optional[int] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

class ECUFileCreate(BaseModel):
    project_id: Optional[int] = None
    filename: str
    file_path: str
    file_size: int
    sha256: str
    md5: Optional[str] = None
    file_format: Optional[str] = None
    uploaded_by: Optional[int] = None


class ECUFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: Optional[int] = None
    filename: str
    file_path: str
    file_size: int
    sha256: str
    md5: Optional[str] = None
    file_format: Optional[str] = None
    uploaded_by: Optional[int] = None
    uploaded_at: Optional[datetime] = None


class ECUFileUpdate(BaseModel):
    project_id: Optional[int] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    sha256: Optional[str] = None
    md5: Optional[str] = None
    file_format: Optional[str] = None
    uploaded_by: Optional[int] = None


class AnalysisCreate(BaseModel):
    ecu_file_id: int
    detected_manufacturer: Optional[str] = None
    detected_ecu_model: Optional[str] = None
    detected_processor: Optional[str] = None
    confidence: Optional[float] = None
    needs_review: Optional[bool] = None
    processing_time_ms: Optional[int] = None
    engine_version: Optional[str] = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_file_id: int
    detected_manufacturer: Optional[str] = None
    detected_ecu_model: Optional[str] = None
    detected_ecu_family: Optional[str] = None
    detected_processor: Optional[str] = None
    detected_protocol: Optional[str] = None
    detected_hw_version: Optional[str] = None
    detected_sw_version: Optional[str] = None
    detected_brand: Optional[str] = None
    detected_engine: Optional[str] = None
    confidence: Optional[float] = None
    consistency_score: Optional[float] = None
    needs_review: Optional[bool] = None
    review_reasons: Optional[str] = None
    processing_time_ms: Optional[int] = None
    engine_version: Optional[str] = None
    created_at: datetime


class AnalysisUpdate(BaseModel):
    ecu_file_id: Optional[int] = None
    detected_manufacturer: Optional[str] = None
    detected_ecu_model: Optional[str] = None
    detected_ecu_family: Optional[str] = None
    detected_processor: Optional[str] = None
    detected_protocol: Optional[str] = None
    detected_hw_version: Optional[str] = None
    detected_sw_version: Optional[str] = None
    detected_brand: Optional[str] = None
    detected_engine: Optional[str] = None
    confidence: Optional[float] = None
    consistency_score: Optional[float] = None
    needs_review: Optional[bool] = None
    review_reasons: Optional[str] = None
    processing_time_ms: Optional[int] = None
    engine_version: Optional[str] = None


class AnalysisResultCreate(BaseModel):
    analysis_id: int
    result_type: str
    result_data: Any
    confidence: Optional[float] = None
    explanation: Optional[str] = None


class AnalysisResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    result_type: str
    result_data: Any
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    created_at: datetime


class AnalysisResultUpdate(BaseModel):
    analysis_id: Optional[int] = None
    result_type: Optional[str] = None
    result_data: Optional[Any] = None
    confidence: Optional[float] = None
    explanation: Optional[str] = None


class AnalysisHypothesisCreate(BaseModel):
    analysis_id: int
    rank: int
    ecu_model_id: Optional[int] = None
    ecu_name: str
    probability: float
    evidence: Optional[str] = None
    is_rejected: Optional[bool] = None
    rejection_reasons: Optional[str] = None


class AnalysisHypothesisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    rank: int
    ecu_model_id: Optional[int] = None
    ecu_name: str
    probability: float
    evidence: Optional[str] = None
    is_rejected: Optional[bool] = None
    rejection_reasons: Optional[str] = None
    created_at: datetime


class AnalysisHypothesisUpdate(BaseModel):
    analysis_id: Optional[int] = None
    rank: Optional[int] = None
    ecu_model_id: Optional[int] = None
    ecu_name: Optional[str] = None
    probability: Optional[float] = None
    evidence: Optional[str] = None
    is_rejected: Optional[bool] = None
    rejection_reasons: Optional[str] = None


class AnalysisScoreCreate(BaseModel):
    analysis_id: int
    factor: str
    raw_score: float
    weight: float
    weighted_score: float
    explanation: Optional[str] = None


class AnalysisScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    factor: str
    raw_score: float
    weight: float
    weighted_score: float
    explanation: Optional[str] = None
    created_at: datetime


class AnalysisScoreUpdate(BaseModel):
    analysis_id: Optional[int] = None
    factor: Optional[str] = None
    raw_score: Optional[float] = None
    weight: Optional[float] = None
    weighted_score: Optional[float] = None
    explanation: Optional[str] = None


class DetectedMapCreate(BaseModel):
    analysis_id: int
    map_id: Optional[int] = None
    map_name: str
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    status: Optional[str] = None
    detection_method: Optional[str] = None
    confidence: Optional[float] = None


class DetectedMapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    map_id: Optional[int] = None
    map_name: str
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    status: Optional[str] = None
    detection_method: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None


class DetectedMapUpdate(BaseModel):
    map_id: Optional[int] = None
    map_name: Optional[str] = None
    offset_hex: Optional[str] = None
    offset_dec: Optional[int] = None
    size_bytes: Optional[int] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    data_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    status: Optional[str] = None
    detection_method: Optional[str] = None
    confidence: Optional[float] = None


class DetectedSegmentCreate(BaseModel):
    analysis_id: int
    segment_type: str
    start_offset: int
    end_offset: int
    size_bytes: int
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    is_valid: Optional[bool] = None
    explanation: Optional[str] = None


class DetectedSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    segment_type: str
    start_offset: int
    end_offset: int
    size_bytes: int
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    is_valid: Optional[bool] = None
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None


class DetectedSegmentUpdate(BaseModel):
    segment_type: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    size_bytes: Optional[int] = None
    entropy: Optional[float] = None
    non_empty_ratio: Optional[float] = None
    is_valid: Optional[bool] = None
    explanation: Optional[str] = None


class ChecksumResultCreate(BaseModel):
    analysis_id: int
    algorithm: str
    offset: Optional[int] = None
    size: Optional[int] = None
    stored_value: Optional[str] = None
    computed_value: Optional[str] = None
    is_valid: Optional[bool] = None
    data_start: Optional[int] = None
    data_end: Optional[int] = None
    explanation: Optional[str] = None


class ChecksumResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    algorithm: str
    offset: Optional[int] = None
    size: Optional[int] = None
    stored_value: Optional[str] = None
    computed_value: Optional[str] = None
    is_valid: Optional[bool] = None
    data_start: Optional[int] = None
    data_end: Optional[int] = None
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None


class ChecksumResultUpdate(BaseModel):
    algorithm: Optional[str] = None
    offset: Optional[int] = None
    size: Optional[int] = None
    stored_value: Optional[str] = None
    computed_value: Optional[str] = None
    is_valid: Optional[bool] = None
    data_start: Optional[int] = None
    data_end: Optional[int] = None
    explanation: Optional[str] = None


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

class AIModelCreate(BaseModel):
    name: str
    version: str
    model_type: str
    accuracy: Optional[float] = None
    training_samples: Optional[int] = None
    config_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AIModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    model_type: str
    accuracy: Optional[float] = None
    training_samples: Optional[int] = None
    config_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    created_at: datetime


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    model_type: Optional[str] = None
    accuracy: Optional[float] = None
    training_samples: Optional[int] = None
    config_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AIPredictionCreate(BaseModel):
    analysis_id: int
    model_id: int
    prediction_type: str
    predicted_value: str
    confidence: Optional[float] = None
    features_used: Optional[str] = None


class AIPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    model_id: int
    prediction_type: str
    predicted_value: str
    confidence: Optional[float] = None
    features_used: Optional[str] = None
    created_at: datetime


class AIPredictionUpdate(BaseModel):
    analysis_id: Optional[int] = None
    model_id: Optional[int] = None
    prediction_type: Optional[str] = None
    predicted_value: Optional[str] = None
    confidence: Optional[float] = None
    features_used: Optional[str] = None


class LearningDatasetCreate(BaseModel):
    ecu_file_id: int
    label_manufacturer: Optional[str] = None
    label_ecu_model: Optional[str] = None
    label_processor: Optional[str] = None
    is_validated: Optional[bool] = None
    validated_by: Optional[str] = None


class LearningDatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ecu_file_id: int
    label_manufacturer: Optional[str] = None
    label_ecu_model: Optional[str] = None
    label_processor: Optional[str] = None
    is_validated: Optional[bool] = None
    validated_by: Optional[str] = None
    created_at: datetime


class LearningDatasetUpdate(BaseModel):
    label_manufacturer: Optional[str] = None
    label_ecu_model: Optional[str] = None
    label_processor: Optional[str] = None
    is_validated: Optional[bool] = None
    validated_by: Optional[str] = None


class HeuristicCreate(BaseModel):
    name: str
    category: str
    rule_json: Dict[str, Any]
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class HeuristicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    rule_json: Dict[str, Any]
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: datetime


class HeuristicUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    rule_json: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

class ReportCreate(BaseModel):
    analysis_id: int
    title: str
    format: str
    content_json: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    generated_by: Optional[str] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    title: str
    format: str
    content_json: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    generated_by: Optional[str] = None
    created_at: datetime


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    format: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    generated_by: Optional[str] = None


class ExportCreate(BaseModel):
    report_id: int
    export_format: str
    file_path: str
    file_size: Optional[int] = None


class ExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: int
    export_format: str
    file_path: str
    file_size: Optional[int] = None
    created_at: datetime


class ExportUpdate(BaseModel):
    report_id: Optional[int] = None
    export_format: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------

class ActivityLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class ActivityLogUpdate(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
