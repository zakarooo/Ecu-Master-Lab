from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# =============================================================================
# 1. REFERENTIEL (6 tables)
# =============================================================================


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    ecu_models: Mapped[List["ECUModel"]] = relationship(
        "ECUModel", back_populates="manufacturer"
    )


class ECUModel(Base):
    __tablename__ = "ecu_models"
    __table_args__ = (
        Index("ix_ecu_models_manufacturer_id", "manufacturer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    family: Mapped[Optional[str]] = mapped_column(String(50))
    processor_type: Mapped[Optional[str]] = mapped_column(String(100))
    flash_size_kb: Mapped[Optional[int]] = mapped_column(Integer)
    eeprom_size_kb: Mapped[Optional[int]] = mapped_column(Integer)
    ram_size_kb: Mapped[Optional[int]] = mapped_column(Integer)
    typical_brands: Mapped[Optional[str]] = mapped_column(Text)
    typical_engines: Mapped[Optional[str]] = mapped_column(Text)
    protocol: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    manufacturer: Mapped["Manufacturer"] = relationship(
        "Manufacturer", back_populates="ecu_models"
    )
    ecu_variants: Mapped[List["ECUVariant"]] = relationship(
        "ECUVariant", back_populates="ecu_model"
    )
    software_versions: Mapped[List["SoftwareVersion"]] = relationship(
        "SoftwareVersion", back_populates="ecu_model"
    )
    hardware_versions: Mapped[List["HardwareVersion"]] = relationship(
        "HardwareVersion", back_populates="ecu_model"
    )
    memory_layouts: Mapped[List["MemoryLayout"]] = relationship(
        "MemoryLayout", back_populates="ecu_model"
    )
    ecu_signatures: Mapped[List["ECUSignature"]] = relationship(
        "ECUSignature", back_populates="ecu_model"
    )
    binary_patterns: Mapped[List["BinaryPattern"]] = relationship(
        "BinaryPattern", back_populates="ecu_model"
    )
    maps: Mapped[List["Map"]] = relationship("Map", back_populates="ecu_model")
    analysis_hypotheses: Mapped[List["AnalysisHypothesis"]] = relationship(
        "AnalysisHypothesis", back_populates="ecu_model"
    )


class ECUVariant(Base):
    __tablename__ = "ecu_variants"
    __table_args__ = (
        Index("ix_ecu_variants_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    variant_name: Mapped[Optional[str]] = mapped_column(String(100))
    hw_revision: Mapped[Optional[str]] = mapped_column(String(50))
    sw_revision: Mapped[Optional[str]] = mapped_column(String(50))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    checksum_type: Mapped[Optional[str]] = mapped_column(String(50))
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="ecu_variants"
    )


class Processor(Base):
    __tablename__ = "processors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    family: Mapped[Optional[str]] = mapped_column(String(50))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    architecture: Mapped[Optional[str]] = mapped_column(String(50))
    word_size: Mapped[Optional[int]] = mapped_column(Integer)
    endianness: Mapped[Optional[str]] = mapped_column(String(10))
    clock_mhz: Mapped[Optional[int]] = mapped_column(Integer)
    flash_kb: Mapped[Optional[int]] = mapped_column(Integer)
    ram_kb: Mapped[Optional[int]] = mapped_column(Integer)
    extensions: Mapped[Optional[str]] = mapped_column(Text)
    known_ecus: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    hardware_versions: Mapped[List["HardwareVersion"]] = relationship(
        "HardwareVersion", back_populates="processor"
    )


class Protocol(Base):
    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    requires_bootloader: Mapped[bool] = mapped_column(Boolean, default=False)
    typical_tools: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ChecksumAlgorithm(Base):
    __tablename__ = "checksum_algorithms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    polynomial: Mapped[Optional[str]] = mapped_column(String(50))
    init_value: Mapped[Optional[str]] = mapped_column(String(50))
    xor_out: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# =============================================================================
# 2. VEHICULES (3 tables)
# =============================================================================


class VehicleBrand(Base):
    __tablename__ = "vehicle_brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    vehicle_models: Mapped[List["VehicleModel"]] = relationship(
        "VehicleModel", back_populates="brand"
    )


class VehicleModel(Base):
    __tablename__ = "vehicle_models"
    __table_args__ = (
        Index("ix_vehicle_models_brand_id", "brand_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_brands.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    year_start: Mapped[Optional[int]] = mapped_column(Integer)
    year_end: Mapped[Optional[int]] = mapped_column(Integer)
    body_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    brand: Mapped["VehicleBrand"] = relationship(
        "VehicleBrand", back_populates="vehicle_models"
    )
    vehicle_engines: Mapped[List["VehicleEngine"]] = relationship(
        "VehicleEngine", back_populates="vehicle_model"
    )


class VehicleEngine(Base):
    __tablename__ = "vehicle_engines"
    __table_args__ = (
        Index("ix_vehicle_engines_model_id", "model_id"),
        Index("ix_vehicle_engines_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_models.id"), nullable=False
    )
    engine_code: Mapped[Optional[str]] = mapped_column(String(50))
    displacement_cc: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(30))
    power_hp: Mapped[Optional[int]] = mapped_column(Integer)
    torque_nm: Mapped[Optional[int]] = mapped_column(Integer)
    emission_standard: Mapped[Optional[str]] = mapped_column(String(30))
    ecu_model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    vehicle_model: Mapped["VehicleModel"] = relationship(
        "VehicleModel", back_populates="vehicle_engines"
    )
    ecu_model: Mapped[Optional["ECUModel"]] = relationship("ECUModel")


# =============================================================================
# 3. VERSIONS (2 tables)
# =============================================================================


class SoftwareVersion(Base):
    __tablename__ = "software_versions"
    __table_args__ = (
        UniqueConstraint("ecu_model_id", "sw_number", name="uq_sw_version_model_sw"),
        Index("ix_software_versions_ecu_model_id", "ecu_model_id"),
        Index("ix_software_versions_sw_number", "sw_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    sw_number: Mapped[Optional[str]] = mapped_column(String(100))
    hw_number: Mapped[Optional[str]] = mapped_column(String(100))
    calibration_id: Mapped[Optional[str]] = mapped_column(String(100))
    cvn: Mapped[Optional[str]] = mapped_column(String(100))
    version_label: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    checksum_value: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="software_versions"
    )


class HardwareVersion(Base):
    __tablename__ = "hardware_versions"
    __table_args__ = (
        Index("ix_hardware_versions_ecu_model_id", "ecu_model_id"),
        Index("ix_hardware_versions_hw_number", "hw_number"),
        Index("ix_hardware_versions_processor_id", "processor_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    hw_number: Mapped[Optional[str]] = mapped_column(String(100))
    revision: Mapped[Optional[str]] = mapped_column(String(50))
    board_type: Mapped[Optional[str]] = mapped_column(String(50))
    processor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("processors.id"), nullable=True
    )
    flash_size_kb: Mapped[Optional[int]] = mapped_column(Integer)
    eeprom_size_kb: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="hardware_versions"
    )
    processor: Mapped[Optional["Processor"]] = relationship(
        "Processor", back_populates="hardware_versions"
    )


# =============================================================================
# 4. MEMOIRE (2 tables)
# =============================================================================


class MemoryLayout(Base):
    __tablename__ = "memory_layouts"
    __table_args__ = (
        Index("ix_memory_layouts_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    total_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    address_bus_width: Mapped[Optional[int]] = mapped_column(Integer)
    data_bus_width: Mapped[Optional[int]] = mapped_column(Integer)
    endianness: Mapped[Optional[str]] = mapped_column(String(10))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="memory_layouts"
    )
    memory_segments: Mapped[List["MemorySegment"]] = relationship(
        "MemorySegment", back_populates="layout"
    )


class MemorySegment(Base):
    __tablename__ = "memory_segments"
    __table_args__ = (
        Index("ix_memory_segments_layout_id", "layout_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    layout_id: Mapped[int] = mapped_column(
        ForeignKey("memory_layouts.id"), nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(String(100))
    segment_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_address: Mapped[Optional[int]] = mapped_column(BigInteger)
    end_address: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    permissions: Mapped[Optional[str]] = mapped_column(String(10))
    description: Mapped[Optional[str]] = mapped_column(Text)

    layout: Mapped["MemoryLayout"] = relationship(
        "MemoryLayout", back_populates="memory_segments"
    )


# =============================================================================
# 5. SIGNATURES (2 tables)
# =============================================================================


class ECUSignature(Base):
    __tablename__ = "ecu_signatures"
    __table_args__ = (
        Index("ix_ecu_signatures_ecu_model_id", "ecu_model_id"),
        Index("ix_ecu_signatures_confidence", "confidence_weight"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    signature_name: Mapped[Optional[str]] = mapped_column(String(200))
    pattern_hex: Mapped[Optional[str]] = mapped_column(Text)
    offset_hex: Mapped[Optional[str]] = mapped_column(String(50))
    offset_dec: Mapped[Optional[int]] = mapped_column(BigInteger)
    confidence_weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="ecu_signatures"
    )


class BinaryPattern(Base):
    __tablename__ = "binary_patterns"
    __table_args__ = (
        Index("ix_binary_patterns_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    pattern_name: Mapped[Optional[str]] = mapped_column(String(100))
    pattern_hex: Mapped[Optional[str]] = mapped_column(Text)
    offset_start: Mapped[Optional[int]] = mapped_column(BigInteger)
    offset_end: Mapped[Optional[int]] = mapped_column(BigInteger)
    byte_length: Mapped[Optional[int]] = mapped_column(Integer)
    match_count: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="binary_patterns"
    )


# =============================================================================
# 6. CARTOGRAPHIES (4 tables)
# =============================================================================


class MapCategory(Base):
    __tablename__ = "map_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_categories.id"), nullable=True
    )
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    parent: Mapped[Optional["MapCategory"]] = relationship(
        "MapCategory", remote_side="MapCategory.id", back_populates="children"
    )
    children: Mapped[List["MapCategory"]] = relationship(
        "MapCategory", back_populates="parent"
    )
    maps: Mapped[List["Map"]] = relationship("Map", back_populates="category")


class MapUnit(Base):
    __tablename__ = "map_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    unit_type: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    maps: Mapped[List["Map"]] = relationship("Map", back_populates="unit")
    axes: Mapped[List["MapAxis"]] = relationship(
        "MapAxis", back_populates="unit"
    )


class MapAxis(Base):
    __tablename__ = "map_axes"
    __table_args__ = (
        Index("ix_map_axes_unit_id", "unit_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    axis_type: Mapped[Optional[str]] = mapped_column(String(20))
    unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_units.id"), nullable=True
    )
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    num_points: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)

    unit: Mapped[Optional["MapUnit"]] = relationship(
        "MapUnit", back_populates="axes"
    )
    maps_as_x: Mapped[List["Map"]] = relationship(
        "Map", foreign_keys="Map.axis_x_id", back_populates="axis_x"
    )
    maps_as_y: Mapped[List["Map"]] = relationship(
        "Map", foreign_keys="Map.axis_y_id", back_populates="axis_y"
    )


class Map(Base):
    __tablename__ = "maps"
    __table_args__ = (
        Index("ix_maps_ecu_model_id", "ecu_model_id"),
        Index("ix_maps_category_id", "category_id"),
        Index("ix_maps_unit_id", "unit_id"),
        Index("ix_maps_axis_x_id", "axis_x_id"),
        Index("ix_maps_axis_y_id", "axis_y_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_categories.id"), nullable=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(100))
    address_hex: Mapped[Optional[str]] = mapped_column(String(50))
    address_dec: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    rows: Mapped[Optional[int]] = mapped_column(Integer)
    cols: Mapped[Optional[int]] = mapped_column(Integer)
    data_type: Mapped[Optional[str]] = mapped_column(String(20))
    unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_units.id"), nullable=True
    )
    axis_x_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_axes.id"), nullable=True
    )
    axis_y_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("map_axes.id"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_model: Mapped["ECUModel"] = relationship(
        "ECUModel", back_populates="maps"
    )
    category: Mapped[Optional["MapCategory"]] = relationship(
        "MapCategory", back_populates="maps"
    )
    unit: Mapped[Optional["MapUnit"]] = relationship(
        "MapUnit", back_populates="maps"
    )
    axis_x: Mapped[Optional["MapAxis"]] = relationship(
        "MapAxis", foreign_keys=[axis_x_id], back_populates="maps_as_x"
    )
    axis_y: Mapped[Optional["MapAxis"]] = relationship(
        "MapAxis", foreign_keys=[axis_y_id], back_populates="maps_as_y"
    )
    detected_maps: Mapped[List["DetectedMap"]] = relationship(
        "DetectedMap", back_populates="known_map"
    )


# =============================================================================
# 7. ANALYSE ECU (8 tables)
# =============================================================================


class ECUFile(Base):
    __tablename__ = "ecu_files"
    __table_args__ = (
        Index("ix_ecu_files_sha256", "sha256"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    sha256: Mapped[Optional[str]] = mapped_column(String(64))
    md5: Mapped[Optional[str]] = mapped_column(String(32))
    file_format: Mapped[Optional[str]] = mapped_column(String(20))
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis", back_populates="ecu_file"
    )
    learning_datasets: Mapped[List["LearningDataset"]] = relationship(
        "LearningDataset", back_populates="ecu_file"
    )
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="ecu_files", foreign_keys=[project_id]
    )


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        Index("ix_analyses_ecu_file_id", "ecu_file_id"),
        Index("ix_analyses_confidence", "confidence"),
        Index("ix_analyses_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_file_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_files.id", ondelete="CASCADE"), nullable=False
    )
    detected_manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    detected_ecu_model: Mapped[Optional[str]] = mapped_column(String(100))
    detected_ecu_family: Mapped[Optional[str]] = mapped_column(String(50))
    detected_processor: Mapped[Optional[str]] = mapped_column(String(100))
    detected_protocol: Mapped[Optional[str]] = mapped_column(String(50))
    detected_hw_version: Mapped[Optional[str]] = mapped_column(String(100))
    detected_sw_version: Mapped[Optional[str]] = mapped_column(String(100))
    detected_brand: Mapped[Optional[str]] = mapped_column(String(100))
    detected_engine: Mapped[Optional[str]] = mapped_column(String(100))
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    consistency_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    review_reasons: Mapped[Optional[str]] = mapped_column(Text)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    engine_version: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_file: Mapped["ECUFile"] = relationship(
        "ECUFile", back_populates="analyses"
    )
    analysis_results: Mapped[List["AnalysisResult"]] = relationship(
        "AnalysisResult", back_populates="analysis"
    )
    analysis_hypotheses: Mapped[List["AnalysisHypothesis"]] = relationship(
        "AnalysisHypothesis", back_populates="analysis"
    )
    analysis_scores: Mapped[List["AnalysisScore"]] = relationship(
        "AnalysisScore", back_populates="analysis"
    )
    detected_maps: Mapped[List["DetectedMap"]] = relationship(
        "DetectedMap", back_populates="analysis"
    )
    detected_segments: Mapped[List["DetectedSegment"]] = relationship(
        "DetectedSegment", back_populates="analysis"
    )
    checksum_results: Mapped[List["ChecksumResult"]] = relationship(
        "ChecksumResult", back_populates="analysis"
    )
    ai_predictions: Mapped[List["AIPrediction"]] = relationship(
        "AIPrediction", back_populates="analysis"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="analysis"
    )


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = (
        Index("ix_analysis_results_analysis_id", "analysis_id"),
        Index(
            "ix_analysis_results_analysis_type",
            "analysis_id",
            "result_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    result_type: Mapped[Optional[str]] = mapped_column(String(50))
    result_data: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="analysis_results"
    )


class AnalysisHypothesis(Base):
    __tablename__ = "analysis_hypotheses"
    __table_args__ = (
        Index("ix_analysis_hypotheses_analysis_id", "analysis_id"),
        Index("ix_analysis_hypotheses_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    rank: Mapped[Optional[int]] = mapped_column(Integer)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ecu_models.id"), nullable=True
    )
    ecu_name: Mapped[Optional[str]] = mapped_column(String(100))
    probability: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    is_rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reasons: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="analysis_hypotheses"
    )
    ecu_model: Mapped[Optional["ECUModel"]] = relationship(
        "ECUModel", back_populates="analysis_hypotheses"
    )


class AnalysisScore(Base):
    __tablename__ = "analysis_scores"
    __table_args__ = (
        Index("ix_analysis_scores_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    factor: Mapped[Optional[str]] = mapped_column(String(100))
    raw_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    weighted_score: Mapped[Optional[float]] = mapped_column(Numeric(7, 2))
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="analysis_scores"
    )


class DetectedMap(Base):
    __tablename__ = "detected_maps"
    __table_args__ = (
        Index("ix_detected_maps_analysis_id", "analysis_id"),
        Index("ix_detected_maps_map_id", "map_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    map_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("maps.id"), nullable=True
    )
    map_name: Mapped[Optional[str]] = mapped_column(String(100))
    offset_hex: Mapped[Optional[str]] = mapped_column(String(50))
    offset_dec: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    rows: Mapped[Optional[int]] = mapped_column(Integer)
    cols: Mapped[Optional[int]] = mapped_column(Integer)
    data_type: Mapped[Optional[str]] = mapped_column(String(20))
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    avg_value: Mapped[Optional[float]] = mapped_column(Float)
    entropy: Mapped[Optional[float]] = mapped_column(Float)
    non_empty_ratio: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[Optional[str]] = mapped_column(String(20))
    detection_method: Mapped[Optional[str]] = mapped_column(String(50))
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="detected_maps"
    )
    known_map: Mapped[Optional["Map"]] = relationship(
        "Map", back_populates="detected_maps"
    )


class DetectedSegment(Base):
    __tablename__ = "detected_segments"
    __table_args__ = (
        Index("ix_detected_segments_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    segment_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    end_offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    entropy: Mapped[Optional[float]] = mapped_column(Float)
    non_empty_ratio: Mapped[Optional[float]] = mapped_column(Float)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="detected_segments"
    )


class ChecksumResult(Base):
    __tablename__ = "checksum_results"
    __table_args__ = (
        Index("ix_checksum_results_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    algorithm: Mapped[Optional[str]] = mapped_column(String(100))
    offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    size: Mapped[Optional[int]] = mapped_column(Integer)
    stored_value: Mapped[Optional[str]] = mapped_column(String(100))
    computed_value: Mapped[Optional[str]] = mapped_column(String(100))
    is_valid: Mapped[Optional[bool]] = mapped_column(Boolean)
    data_start: Mapped[Optional[int]] = mapped_column(BigInteger)
    data_end: Mapped[Optional[int]] = mapped_column(BigInteger)
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="checksum_results"
    )


# =============================================================================
# 8. INTELLIGENCE ARTIFICIELLE (4 tables)
# =============================================================================


class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    version: Mapped[Optional[str]] = mapped_column(String(50))
    model_type: Mapped[Optional[str]] = mapped_column(String(50))
    accuracy: Mapped[Optional[float]] = mapped_column(Float)
    training_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    training_samples: Mapped[Optional[int]] = mapped_column(Integer)
    config_json: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    predictions: Mapped[List["AIPrediction"]] = relationship(
        "AIPrediction", back_populates="model"
    )


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (
        Index("ix_ai_predictions_analysis_id", "analysis_id"),
        Index("ix_ai_predictions_model_id", "model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ai_models.id"), nullable=False
    )
    prediction_type: Mapped[Optional[str]] = mapped_column(String(50))
    predicted_value: Mapped[Optional[str]] = mapped_column(String(200))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    features_used: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="ai_predictions"
    )
    model: Mapped["AIModel"] = relationship(
        "AIModel", back_populates="predictions"
    )


class LearningDataset(Base):
    __tablename__ = "learning_datasets"
    __table_args__ = (
        Index("ix_learning_datasets_ecu_file_id", "ecu_file_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_file_id: Mapped[int] = mapped_column(
        ForeignKey("ecu_files.id"), nullable=False
    )
    label_manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    label_ecu_model: Mapped[Optional[str]] = mapped_column(String(100))
    label_processor: Mapped[Optional[str]] = mapped_column(String(100))
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ecu_file: Mapped["ECUFile"] = relationship(
        "ECUFile", back_populates="learning_datasets"
    )


class Heuristic(Base):
    __tablename__ = "heuristics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    rule_json: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


# =============================================================================
# 9. RAPPORTS (2 tables)
# =============================================================================


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(200))
    format: Mapped[Optional[str]] = mapped_column(String(20))
    content_json: Mapped[Optional[str]] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    generated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="reports"
    )
    exports: Mapped[List["Export"]] = relationship(
        "Export", back_populates="report"
    )


class Export(Base):
    __tablename__ = "exports"
    __table_args__ = (
        Index("ix_exports_report_id", "report_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    export_format: Mapped[Optional[str]] = mapped_column(String(20))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    report: Mapped["Report"] = relationship("Report", back_populates="exports")


# =============================================================================
# 10. HISTORIQUE (1 table)
# =============================================================================


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_action", "action"),
        Index("ix_activity_logs_resource_type", "resource_type"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# =============================================================================
# 11. BASE DE CONNAISSANCES (7 tables)
# =============================================================================


class KnownEcuFile(Base):
    __tablename__ = "known_ecu_files"
    __table_args__ = (
        Index("ix_known_ecu_files_sha256", "sha256"),
        Index("ix_known_ecu_files_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    manufacturer_name: Mapped[Optional[str]] = mapped_column(String(100))
    confirmed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnownSignature(Base):
    __tablename__ = "known_signatures"
    __table_args__ = (
        Index("ix_known_signatures_pattern_hex", "pattern_hex"),
        Index("ix_known_signatures_ecu_model_id", "ecu_model_id"),
        Index("ix_known_signatures_category", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    pattern_hex: Mapped[str] = mapped_column(String(200), nullable=False)
    pattern_bytes: Mapped[Optional[bytes]] = mapped_column(nullable=True)
    offset_relative: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    context_hex: Mapped[Optional[str]] = mapped_column(String(200))
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    total_known_files: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    source_file_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnownString(Base):
    __tablename__ = "known_strings"
    __table_args__ = (
        Index("ix_known_strings_string_value", "string_value"),
        Index("ix_known_strings_ecu_model_id", "ecu_model_id"),
        Index("ix_known_strings_category", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    string_value: Mapped[str] = mapped_column(String(500), nullable=False)
    offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    total_known_files: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    source_file_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnownMap(Base):
    __tablename__ = "known_maps"
    __table_args__ = (
        Index("ix_known_maps_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    map_name: Mapped[Optional[str]] = mapped_column(String(200))
    offset_hex: Mapped[Optional[str]] = mapped_column(String(20))
    offset_dec: Mapped[Optional[int]] = mapped_column(BigInteger)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    rows: Mapped[Optional[int]] = mapped_column(Integer)
    cols: Mapped[Optional[int]] = mapped_column(Integer)
    data_type: Mapped[Optional[str]] = mapped_column(String(20))
    category: Mapped[Optional[str]] = mapped_column(String(50))
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    total_known_files: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    source_file_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnownChecksum(Base):
    __tablename__ = "known_checksums"
    __table_args__ = (
        Index("ix_known_checksums_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    size: Mapped[Optional[int]] = mapped_column(Integer)
    data_range_start: Mapped[Optional[int]] = mapped_column(BigInteger)
    data_range_end: Mapped[Optional[int]] = mapped_column(BigInteger)
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    total_known_files: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    source_file_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnownSegment(Base):
    __tablename__ = "known_segments"
    __table_args__ = (
        Index("ix_known_segments_ecu_model_id", "ecu_model_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ecu_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ecu_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    segment_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    end_offset: Mapped[Optional[int]] = mapped_column(BigInteger)
    entropy: Mapped[Optional[float]] = mapped_column(Float)
    occurrence_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    total_known_files: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    source_file_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AnalysisCorrection(Base):
    __tablename__ = "analysis_corrections"
    __table_args__ = (
        Index("ix_analysis_corrections_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    original_prediction: Mapped[Optional[str]] = mapped_column(String(200))
    corrected_model_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    corrected_model_name: Mapped[Optional[str]] = mapped_column(String(200))
    corrected_manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    corrected_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
