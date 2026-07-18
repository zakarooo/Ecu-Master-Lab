from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.new.ecu_models import (
    Manufacturer,
    ECUModel,
    ECUVariant,
    Processor,
    Protocol,
    ChecksumAlgorithm,
    VehicleBrand,
    VehicleModel,
    VehicleEngine,
    SoftwareVersion,
    HardwareVersion,
    MemoryLayout,
    MemorySegment,
    ECUSignature,
    BinaryPattern,
    MapCategory,
    MapUnit,
    MapAxis,
    Map,
    ECUFile,
    Analysis,
    AnalysisResult,
    AnalysisHypothesis,
    AnalysisScore,
    DetectedMap,
    DetectedSegment,
    ChecksumResult,
    AIModel,
    AIPrediction,
    LearningDataset,
    Heuristic,
    Report,
    Export,
    ActivityLog,
)


# =============================================================================
# REFERENTIEL
# =============================================================================


class ManufacturerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, manufacturer_id: int) -> Optional[Manufacturer]:
        return self.db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()

    def get_by_name(self, name: str) -> Optional[Manufacturer]:
        return self.db.query(Manufacturer).filter(Manufacturer.name == name).first()

    def create(self, **kwargs) -> Manufacturer:
        manufacturer = Manufacturer(**kwargs)
        self.db.add(manufacturer)
        self.db.commit()
        self.db.refresh(manufacturer)
        return manufacturer

    def update(self, manufacturer: Manufacturer, **kwargs) -> Manufacturer:
        for key, value in kwargs.items():
            setattr(manufacturer, key, value)
        self.db.commit()
        self.db.refresh(manufacturer)
        return manufacturer

    def list_all(self) -> List[Manufacturer]:
        return self.db.query(Manufacturer).order_by(Manufacturer.created_at.desc()).all()

    def count(self) -> int:
        return self.db.query(Manufacturer).count()

    def search(self, query: str) -> List[Manufacturer]:
        return self.db.query(Manufacturer).filter(
            Manufacturer.name.ilike(f"%{query}%")
        ).all()


class ECUModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ecu_model_id: int) -> Optional[ECUModel]:
        return self.db.query(ECUModel).filter(ECUModel.id == ecu_model_id).first()

    def create(self, **kwargs) -> ECUModel:
        ecu_model = ECUModel(**kwargs)
        self.db.add(ecu_model)
        self.db.commit()
        self.db.refresh(ecu_model)
        return ecu_model

    def update(self, ecu_model: ECUModel, **kwargs) -> ECUModel:
        for key, value in kwargs.items():
            setattr(ecu_model, key, value)
        self.db.commit()
        self.db.refresh(ecu_model)
        return ecu_model

    def list_all(self) -> List[ECUModel]:
        return self.db.query(ECUModel).order_by(ECUModel.created_at.desc()).all()

    def count(self) -> int:
        return self.db.query(ECUModel).count()

    def list_by_manufacturer(self, manufacturer_id: int) -> List[ECUModel]:
        return self.db.query(ECUModel).filter(
            ECUModel.manufacturer_id == manufacturer_id
        ).all()

    def search(self, query: str) -> List[ECUModel]:
        return self.db.query(ECUModel).filter(
            (ECUModel.model_name.ilike(f"%{query}%"))
            | (ECUModel.family.ilike(f"%{query}%"))
        ).all()


class ECUVariantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ecu_variant_id: int) -> Optional[ECUVariant]:
        return self.db.query(ECUVariant).filter(ECUVariant.id == ecu_variant_id).first()

    def create(self, **kwargs) -> ECUVariant:
        ecu_variant = ECUVariant(**kwargs)
        self.db.add(ecu_variant)
        self.db.commit()
        self.db.refresh(ecu_variant)
        return ecu_variant

    def update(self, ecu_variant: ECUVariant, **kwargs) -> ECUVariant:
        for key, value in kwargs.items():
            setattr(ecu_variant, key, value)
        self.db.commit()
        self.db.refresh(ecu_variant)
        return ecu_variant

    def list_all(self) -> List[ECUVariant]:
        return self.db.query(ECUVariant).order_by(ECUVariant.created_at.desc()).all()

    def list_by_model(self, ecu_model_id: int) -> List[ECUVariant]:
        return self.db.query(ECUVariant).filter(
            ECUVariant.ecu_model_id == ecu_model_id
        ).all()


class ProcessorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, processor_id: int) -> Optional[Processor]:
        return self.db.query(Processor).filter(Processor.id == processor_id).first()

    def get_by_name(self, name: str) -> Optional[Processor]:
        return self.db.query(Processor).filter(Processor.name == name).first()

    def create(self, **kwargs) -> Processor:
        processor = Processor(**kwargs)
        self.db.add(processor)
        self.db.commit()
        self.db.refresh(processor)
        return processor

    def update(self, processor: Processor, **kwargs) -> Processor:
        for key, value in kwargs.items():
            setattr(processor, key, value)
        self.db.commit()
        self.db.refresh(processor)
        return processor

    def list_all(self) -> List[Processor]:
        return self.db.query(Processor).order_by(Processor.created_at.desc()).all()

    def count(self) -> int:
        return self.db.query(Processor).count()


class ProtocolRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, protocol_id: int) -> Optional[Protocol]:
        return self.db.query(Protocol).filter(Protocol.id == protocol_id).first()

    def get_by_name(self, name: str) -> Optional[Protocol]:
        return self.db.query(Protocol).filter(Protocol.name == name).first()

    def create(self, **kwargs) -> Protocol:
        protocol = Protocol(**kwargs)
        self.db.add(protocol)
        self.db.commit()
        self.db.refresh(protocol)
        return protocol

    def update(self, protocol: Protocol, **kwargs) -> Protocol:
        for key, value in kwargs.items():
            setattr(protocol, key, value)
        self.db.commit()
        self.db.refresh(protocol)
        return protocol

    def list_all(self) -> List[Protocol]:
        return self.db.query(Protocol).order_by(Protocol.created_at.desc()).all()


class ChecksumAlgorithmRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, checksum_algorithm_id: int) -> Optional[ChecksumAlgorithm]:
        return self.db.query(ChecksumAlgorithm).filter(
            ChecksumAlgorithm.id == checksum_algorithm_id
        ).first()

    def get_by_name(self, name: str) -> Optional[ChecksumAlgorithm]:
        return self.db.query(ChecksumAlgorithm).filter(
            ChecksumAlgorithm.name == name
        ).first()

    def create(self, **kwargs) -> ChecksumAlgorithm:
        checksum_algorithm = ChecksumAlgorithm(**kwargs)
        self.db.add(checksum_algorithm)
        self.db.commit()
        self.db.refresh(checksum_algorithm)
        return checksum_algorithm

    def update(self, checksum_algorithm: ChecksumAlgorithm, **kwargs) -> ChecksumAlgorithm:
        for key, value in kwargs.items():
            setattr(checksum_algorithm, key, value)
        self.db.commit()
        self.db.refresh(checksum_algorithm)
        return checksum_algorithm

    def list_all(self) -> List[ChecksumAlgorithm]:
        return self.db.query(ChecksumAlgorithm).order_by(
            ChecksumAlgorithm.created_at.desc()
        ).all()


# =============================================================================
# VEHICULES
# =============================================================================


class VehicleBrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_brand_id: int) -> Optional[VehicleBrand]:
        return self.db.query(VehicleBrand).filter(
            VehicleBrand.id == vehicle_brand_id
        ).first()

    def get_by_name(self, name: str) -> Optional[VehicleBrand]:
        return self.db.query(VehicleBrand).filter(VehicleBrand.name == name).first()

    def create(self, **kwargs) -> VehicleBrand:
        vehicle_brand = VehicleBrand(**kwargs)
        self.db.add(vehicle_brand)
        self.db.commit()
        self.db.refresh(vehicle_brand)
        return vehicle_brand

    def update(self, vehicle_brand: VehicleBrand, **kwargs) -> VehicleBrand:
        for key, value in kwargs.items():
            setattr(vehicle_brand, key, value)
        self.db.commit()
        self.db.refresh(vehicle_brand)
        return vehicle_brand

    def list_all(self) -> List[VehicleBrand]:
        return self.db.query(VehicleBrand).order_by(VehicleBrand.created_at.desc()).all()


class VehicleModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_model_id: int) -> Optional[VehicleModel]:
        return self.db.query(VehicleModel).filter(
            VehicleModel.id == vehicle_model_id
        ).first()

    def create(self, **kwargs) -> VehicleModel:
        vehicle_model = VehicleModel(**kwargs)
        self.db.add(vehicle_model)
        self.db.commit()
        self.db.refresh(vehicle_model)
        return vehicle_model

    def update(self, vehicle_model: VehicleModel, **kwargs) -> VehicleModel:
        for key, value in kwargs.items():
            setattr(vehicle_model, key, value)
        self.db.commit()
        self.db.refresh(vehicle_model)
        return vehicle_model

    def list_all(self) -> List[VehicleModel]:
        return self.db.query(VehicleModel).order_by(VehicleModel.created_at.desc()).all()

    def list_by_brand(self, brand_id: int) -> List[VehicleModel]:
        return self.db.query(VehicleModel).filter(
            VehicleModel.brand_id == brand_id
        ).all()


class VehicleEngineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_engine_id: int) -> Optional[VehicleEngine]:
        return self.db.query(VehicleEngine).filter(
            VehicleEngine.id == vehicle_engine_id
        ).first()

    def create(self, **kwargs) -> VehicleEngine:
        vehicle_engine = VehicleEngine(**kwargs)
        self.db.add(vehicle_engine)
        self.db.commit()
        self.db.refresh(vehicle_engine)
        return vehicle_engine

    def update(self, vehicle_engine: VehicleEngine, **kwargs) -> VehicleEngine:
        for key, value in kwargs.items():
            setattr(vehicle_engine, key, value)
        self.db.commit()
        self.db.refresh(vehicle_engine)
        return vehicle_engine

    def list_all(self) -> List[VehicleEngine]:
        return self.db.query(VehicleEngine).order_by(
            VehicleEngine.created_at.desc()
        ).all()

    def list_by_model(self, model_id: int) -> List[VehicleEngine]:
        return self.db.query(VehicleEngine).filter(
            VehicleEngine.model_id == model_id
        ).all()


# =============================================================================
# VERSIONS
# =============================================================================


class SoftwareVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, software_version_id: int) -> Optional[SoftwareVersion]:
        return self.db.query(SoftwareVersion).filter(
            SoftwareVersion.id == software_version_id
        ).first()

    def create(self, **kwargs) -> SoftwareVersion:
        software_version = SoftwareVersion(**kwargs)
        self.db.add(software_version)
        self.db.commit()
        self.db.refresh(software_version)
        return software_version

    def update(self, software_version: SoftwareVersion, **kwargs) -> SoftwareVersion:
        for key, value in kwargs.items():
            setattr(software_version, key, value)
        self.db.commit()
        self.db.refresh(software_version)
        return software_version

    def list_all(self) -> List[SoftwareVersion]:
        return self.db.query(SoftwareVersion).order_by(
            SoftwareVersion.created_at.desc()
        ).all()

    def list_by_model(self, ecu_model_id: int) -> List[SoftwareVersion]:
        return self.db.query(SoftwareVersion).filter(
            SoftwareVersion.ecu_model_id == ecu_model_id
        ).all()

    def find_by_sw_number(self, sw_number: str) -> Optional[SoftwareVersion]:
        return self.db.query(SoftwareVersion).filter(
            SoftwareVersion.sw_number == sw_number
        ).first()

    def find_by_calibration_id(self, cal_id: str) -> Optional[SoftwareVersion]:
        return self.db.query(SoftwareVersion).filter(
            SoftwareVersion.calibration_id == cal_id
        ).first()


class HardwareVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, hardware_version_id: int) -> Optional[HardwareVersion]:
        return self.db.query(HardwareVersion).filter(
            HardwareVersion.id == hardware_version_id
        ).first()

    def create(self, **kwargs) -> HardwareVersion:
        hardware_version = HardwareVersion(**kwargs)
        self.db.add(hardware_version)
        self.db.commit()
        self.db.refresh(hardware_version)
        return hardware_version

    def update(self, hardware_version: HardwareVersion, **kwargs) -> HardwareVersion:
        for key, value in kwargs.items():
            setattr(hardware_version, key, value)
        self.db.commit()
        self.db.refresh(hardware_version)
        return hardware_version

    def list_all(self) -> List[HardwareVersion]:
        return self.db.query(HardwareVersion).order_by(
            HardwareVersion.created_at.desc()
        ).all()

    def list_by_model(self, ecu_model_id: int) -> List[HardwareVersion]:
        return self.db.query(HardwareVersion).filter(
            HardwareVersion.ecu_model_id == ecu_model_id
        ).all()


# =============================================================================
# MEMOIRE
# =============================================================================


class MemoryLayoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, memory_layout_id: int) -> Optional[MemoryLayout]:
        return self.db.query(MemoryLayout).filter(
            MemoryLayout.id == memory_layout_id
        ).first()

    def create(self, **kwargs) -> MemoryLayout:
        memory_layout = MemoryLayout(**kwargs)
        self.db.add(memory_layout)
        self.db.commit()
        self.db.refresh(memory_layout)
        return memory_layout

    def update(self, memory_layout: MemoryLayout, **kwargs) -> MemoryLayout:
        for key, value in kwargs.items():
            setattr(memory_layout, key, value)
        self.db.commit()
        self.db.refresh(memory_layout)
        return memory_layout

    def list_all(self) -> List[MemoryLayout]:
        return self.db.query(MemoryLayout).order_by(
            MemoryLayout.created_at.desc()
        ).all()

    def list_by_model(self, ecu_model_id: int) -> List[MemoryLayout]:
        return self.db.query(MemoryLayout).filter(
            MemoryLayout.ecu_model_id == ecu_model_id
        ).all()


class MemorySegmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, memory_segment_id: int) -> Optional[MemorySegment]:
        return self.db.query(MemorySegment).filter(
            MemorySegment.id == memory_segment_id
        ).first()

    def create(self, **kwargs) -> MemorySegment:
        memory_segment = MemorySegment(**kwargs)
        self.db.add(memory_segment)
        self.db.commit()
        self.db.refresh(memory_segment)
        return memory_segment

    def update(self, memory_segment: MemorySegment, **kwargs) -> MemorySegment:
        for key, value in kwargs.items():
            setattr(memory_segment, key, value)
        self.db.commit()
        self.db.refresh(memory_segment)
        return memory_segment

    def list_all(self) -> List[MemorySegment]:
        return self.db.query(MemorySegment).all()

    def list_by_layout(self, layout_id: int) -> List[MemorySegment]:
        return self.db.query(MemorySegment).filter(
            MemorySegment.layout_id == layout_id
        ).all()


# =============================================================================
# SIGNATURES
# =============================================================================


class ECUSignatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ecu_signature_id: int) -> Optional[ECUSignature]:
        return self.db.query(ECUSignature).filter(
            ECUSignature.id == ecu_signature_id
        ).first()

    def create(self, **kwargs) -> ECUSignature:
        ecu_signature = ECUSignature(**kwargs)
        self.db.add(ecu_signature)
        self.db.commit()
        self.db.refresh(ecu_signature)
        return ecu_signature

    def update(self, ecu_signature: ECUSignature, **kwargs) -> ECUSignature:
        for key, value in kwargs.items():
            setattr(ecu_signature, key, value)
        self.db.commit()
        self.db.refresh(ecu_signature)
        return ecu_signature

    def list_all(self) -> List[ECUSignature]:
        return self.db.query(ECUSignature).order_by(
            ECUSignature.created_at.desc()
        ).all()

    def list_by_model(self, ecu_model_id: int) -> List[ECUSignature]:
        return self.db.query(ECUSignature).filter(
            ECUSignature.ecu_model_id == ecu_model_id
        ).all()


class BinaryPatternRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, binary_pattern_id: int) -> Optional[BinaryPattern]:
        return self.db.query(BinaryPattern).filter(
            BinaryPattern.id == binary_pattern_id
        ).first()

    def create(self, **kwargs) -> BinaryPattern:
        binary_pattern = BinaryPattern(**kwargs)
        self.db.add(binary_pattern)
        self.db.commit()
        self.db.refresh(binary_pattern)
        return binary_pattern

    def update(self, binary_pattern: BinaryPattern, **kwargs) -> BinaryPattern:
        for key, value in kwargs.items():
            setattr(binary_pattern, key, value)
        self.db.commit()
        self.db.refresh(binary_pattern)
        return binary_pattern

    def list_all(self) -> List[BinaryPattern]:
        return self.db.query(BinaryPattern).order_by(
            BinaryPattern.created_at.desc()
        ).all()

    def list_by_model(self, ecu_model_id: int) -> List[BinaryPattern]:
        return self.db.query(BinaryPattern).filter(
            BinaryPattern.ecu_model_id == ecu_model_id
        ).all()


# =============================================================================
# CARTOGRAPHIES
# =============================================================================


class MapCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, map_category_id: int) -> Optional[MapCategory]:
        return self.db.query(MapCategory).filter(
            MapCategory.id == map_category_id
        ).first()

    def get_by_name(self, name: str) -> Optional[MapCategory]:
        return self.db.query(MapCategory).filter(MapCategory.name == name).first()

    def create(self, **kwargs) -> MapCategory:
        map_category = MapCategory(**kwargs)
        self.db.add(map_category)
        self.db.commit()
        self.db.refresh(map_category)
        return map_category

    def update(self, map_category: MapCategory, **kwargs) -> MapCategory:
        for key, value in kwargs.items():
            setattr(map_category, key, value)
        self.db.commit()
        self.db.refresh(map_category)
        return map_category

    def list_all(self) -> List[MapCategory]:
        return self.db.query(MapCategory).order_by(MapCategory.sort_order).all()

    def list_root_categories(self) -> List[MapCategory]:
        return self.db.query(MapCategory).filter(
            MapCategory.parent_id.is_(None)
        ).order_by(MapCategory.sort_order).all()


class MapUnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, map_unit_id: int) -> Optional[MapUnit]:
        return self.db.query(MapUnit).filter(MapUnit.id == map_unit_id).first()

    def get_by_symbol(self, symbol: str) -> Optional[MapUnit]:
        return self.db.query(MapUnit).filter(MapUnit.symbol == symbol).first()

    def create(self, **kwargs) -> MapUnit:
        map_unit = MapUnit(**kwargs)
        self.db.add(map_unit)
        self.db.commit()
        self.db.refresh(map_unit)
        return map_unit

    def update(self, map_unit: MapUnit, **kwargs) -> MapUnit:
        for key, value in kwargs.items():
            setattr(map_unit, key, value)
        self.db.commit()
        self.db.refresh(map_unit)
        return map_unit

    def list_all(self) -> List[MapUnit]:
        return self.db.query(MapUnit).order_by(MapUnit.symbol).all()


class MapAxisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, map_axis_id: int) -> Optional[MapAxis]:
        return self.db.query(MapAxis).filter(MapAxis.id == map_axis_id).first()

    def create(self, **kwargs) -> MapAxis:
        map_axis = MapAxis(**kwargs)
        self.db.add(map_axis)
        self.db.commit()
        self.db.refresh(map_axis)
        return map_axis

    def update(self, map_axis: MapAxis, **kwargs) -> MapAxis:
        for key, value in kwargs.items():
            setattr(map_axis, key, value)
        self.db.commit()
        self.db.refresh(map_axis)
        return map_axis

    def list_all(self) -> List[MapAxis]:
        return self.db.query(MapAxis).all()


class MapRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, map_id: int) -> Optional[Map]:
        return self.db.query(Map).filter(Map.id == map_id).first()

    def create(self, **kwargs) -> Map:
        map_obj = Map(**kwargs)
        self.db.add(map_obj)
        self.db.commit()
        self.db.refresh(map_obj)
        return map_obj

    def update(self, map_obj: Map, **kwargs) -> Map:
        for key, value in kwargs.items():
            setattr(map_obj, key, value)
        self.db.commit()
        self.db.refresh(map_obj)
        return map_obj

    def list_all(self) -> List[Map]:
        return self.db.query(Map).order_by(Map.created_at.desc()).all()

    def list_by_model(self, ecu_model_id: int) -> List[Map]:
        return self.db.query(Map).filter(
            Map.ecu_model_id == ecu_model_id
        ).all()

    def list_by_category(self, category_id: int) -> List[Map]:
        return self.db.query(Map).filter(
            Map.category_id == category_id
        ).all()

    def search(self, query: str) -> List[Map]:
        return self.db.query(Map).filter(
            Map.name.ilike(f"%{query}%")
        ).all()


# =============================================================================
# ANALYSE ECU
# =============================================================================


class ECUFileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ecu_file_id: int) -> Optional[ECUFile]:
        return self.db.query(ECUFile).filter(ECUFile.id == ecu_file_id).first()

    def get_by_sha256(self, sha256: str) -> Optional[ECUFile]:
        return self.db.query(ECUFile).filter(ECUFile.sha256 == sha256).first()

    def create(self, **kwargs) -> ECUFile:
        ecu_file = ECUFile(**kwargs)
        self.db.add(ecu_file)
        self.db.commit()
        self.db.refresh(ecu_file)
        return ecu_file

    def update(self, ecu_file: ECUFile, **kwargs) -> ECUFile:
        for key, value in kwargs.items():
            setattr(ecu_file, key, value)
        self.db.commit()
        self.db.refresh(ecu_file)
        return ecu_file

    def list_all(self) -> List[ECUFile]:
        return self.db.query(ECUFile).order_by(ECUFile.uploaded_at.desc()).all()

    def list_by_project(self, project_id: int) -> List[ECUFile]:
        return self.db.query(ECUFile).filter(
            ECUFile.project_id == project_id
        ).all()

    def count(self) -> int:
        return self.db.query(ECUFile).count()


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analysis_id: int) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def create(self, **kwargs) -> Analysis:
        analysis = Analysis(**kwargs)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def update(self, analysis: Analysis, **kwargs) -> Analysis:
        for key, value in kwargs.items():
            setattr(analysis, key, value)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def list_all(self) -> List[Analysis]:
        return self.db.query(Analysis).order_by(Analysis.created_at.desc()).all()

    def list_by_file(self, ecu_file_id: int) -> List[Analysis]:
        return self.db.query(Analysis).filter(
            Analysis.ecu_file_id == ecu_file_id
        ).order_by(Analysis.created_at.desc()).all()

    def get_latest_by_file(self, ecu_file_id: int) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(
            Analysis.ecu_file_id == ecu_file_id
        ).order_by(Analysis.created_at.desc()).first()

    def count(self) -> int:
        return self.db.query(Analysis).count()


class AnalysisResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analysis_result_id: int) -> Optional[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_result_id
        ).first()

    def create(self, **kwargs) -> AnalysisResult:
        analysis_result = AnalysisResult(**kwargs)
        self.db.add(analysis_result)
        self.db.commit()
        self.db.refresh(analysis_result)
        return analysis_result

    def list_by_analysis(self, analysis_id: int) -> List[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.analysis_id == analysis_id
        ).all()

    def list_by_type(self, analysis_id: int, result_type: str) -> List[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.analysis_id == analysis_id,
            AnalysisResult.result_type == result_type,
        ).all()


class AnalysisHypothesisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analysis_hypothesis_id: int) -> Optional[AnalysisHypothesis]:
        return self.db.query(AnalysisHypothesis).filter(
            AnalysisHypothesis.id == analysis_hypothesis_id
        ).first()

    def create(self, **kwargs) -> AnalysisHypothesis:
        analysis_hypothesis = AnalysisHypothesis(**kwargs)
        self.db.add(analysis_hypothesis)
        self.db.commit()
        self.db.refresh(analysis_hypothesis)
        return analysis_hypothesis

    def update(self, analysis_hypothesis: AnalysisHypothesis, **kwargs) -> AnalysisHypothesis:
        for key, value in kwargs.items():
            setattr(analysis_hypothesis, key, value)
        self.db.commit()
        self.db.refresh(analysis_hypothesis)
        return analysis_hypothesis

    def list_by_analysis(self, analysis_id: int) -> List[AnalysisHypothesis]:
        return self.db.query(AnalysisHypothesis).filter(
            AnalysisHypothesis.analysis_id == analysis_id
        ).order_by(AnalysisHypothesis.rank).all()


class AnalysisScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analysis_score_id: int) -> Optional[AnalysisScore]:
        return self.db.query(AnalysisScore).filter(
            AnalysisScore.id == analysis_score_id
        ).first()

    def create(self, **kwargs) -> AnalysisScore:
        analysis_score = AnalysisScore(**kwargs)
        self.db.add(analysis_score)
        self.db.commit()
        self.db.refresh(analysis_score)
        return analysis_score

    def list_by_analysis(self, analysis_id: int) -> List[AnalysisScore]:
        return self.db.query(AnalysisScore).filter(
            AnalysisScore.analysis_id == analysis_id
        ).all()


class DetectedMapRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, detected_map_id: int) -> Optional[DetectedMap]:
        return self.db.query(DetectedMap).filter(
            DetectedMap.id == detected_map_id
        ).first()

    def create(self, **kwargs) -> DetectedMap:
        detected_map = DetectedMap(**kwargs)
        self.db.add(detected_map)
        self.db.commit()
        self.db.refresh(detected_map)
        return detected_map

    def list_by_analysis(self, analysis_id: int) -> List[DetectedMap]:
        return self.db.query(DetectedMap).filter(
            DetectedMap.analysis_id == analysis_id
        ).all()


class DetectedSegmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, detected_segment_id: int) -> Optional[DetectedSegment]:
        return self.db.query(DetectedSegment).filter(
            DetectedSegment.id == detected_segment_id
        ).first()

    def create(self, **kwargs) -> DetectedSegment:
        detected_segment = DetectedSegment(**kwargs)
        self.db.add(detected_segment)
        self.db.commit()
        self.db.refresh(detected_segment)
        return detected_segment

    def list_by_analysis(self, analysis_id: int) -> List[DetectedSegment]:
        return self.db.query(DetectedSegment).filter(
            DetectedSegment.analysis_id == analysis_id
        ).all()


class ChecksumResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, checksum_result_id: int) -> Optional[ChecksumResult]:
        return self.db.query(ChecksumResult).filter(
            ChecksumResult.id == checksum_result_id
        ).first()

    def create(self, **kwargs) -> ChecksumResult:
        checksum_result = ChecksumResult(**kwargs)
        self.db.add(checksum_result)
        self.db.commit()
        self.db.refresh(checksum_result)
        return checksum_result

    def list_by_analysis(self, analysis_id: int) -> List[ChecksumResult]:
        return self.db.query(ChecksumResult).filter(
            ChecksumResult.analysis_id == analysis_id
        ).all()

    def count_invalid(self, analysis_id: int) -> int:
        return self.db.query(ChecksumResult).filter(
            ChecksumResult.analysis_id == analysis_id,
            ChecksumResult.is_valid == False,
        ).count()


# =============================================================================
# INTELLIGENCE ARTIFICIELLE
# =============================================================================


class AIModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ai_model_id: int) -> Optional[AIModel]:
        return self.db.query(AIModel).filter(AIModel.id == ai_model_id).first()

    def get_active_models(self) -> List[AIModel]:
        return self.db.query(AIModel).filter(AIModel.is_active == True).all()

    def create(self, **kwargs) -> AIModel:
        ai_model = AIModel(**kwargs)
        self.db.add(ai_model)
        self.db.commit()
        self.db.refresh(ai_model)
        return ai_model

    def update(self, ai_model: AIModel, **kwargs) -> AIModel:
        for key, value in kwargs.items():
            setattr(ai_model, key, value)
        self.db.commit()
        self.db.refresh(ai_model)
        return ai_model

    def list_all(self) -> List[AIModel]:
        return self.db.query(AIModel).order_by(AIModel.created_at.desc()).all()

    def get_latest_active(self) -> Optional[AIModel]:
        return self.db.query(AIModel).filter(
            AIModel.is_active == True
        ).order_by(AIModel.created_at.desc()).first()


class AIPredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ai_prediction_id: int) -> Optional[AIPrediction]:
        return self.db.query(AIPrediction).filter(
            AIPrediction.id == ai_prediction_id
        ).first()

    def create(self, **kwargs) -> AIPrediction:
        ai_prediction = AIPrediction(**kwargs)
        self.db.add(ai_prediction)
        self.db.commit()
        self.db.refresh(ai_prediction)
        return ai_prediction

    def list_by_analysis(self, analysis_id: int) -> List[AIPrediction]:
        return self.db.query(AIPrediction).filter(
            AIPrediction.analysis_id == analysis_id
        ).all()

    def list_by_model(self, model_id: int) -> List[AIPrediction]:
        return self.db.query(AIPrediction).filter(
            AIPrediction.model_id == model_id
        ).all()


class LearningDatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, learning_dataset_id: int) -> Optional[LearningDataset]:
        return self.db.query(LearningDataset).filter(
            LearningDataset.id == learning_dataset_id
        ).first()

    def create(self, **kwargs) -> LearningDataset:
        learning_dataset = LearningDataset(**kwargs)
        self.db.add(learning_dataset)
        self.db.commit()
        self.db.refresh(learning_dataset)
        return learning_dataset

    def update(self, learning_dataset: LearningDataset, **kwargs) -> LearningDataset:
        for key, value in kwargs.items():
            setattr(learning_dataset, key, value)
        self.db.commit()
        self.db.refresh(learning_dataset)
        return learning_dataset

    def list_all(self) -> List[LearningDataset]:
        return self.db.query(LearningDataset).order_by(
            LearningDataset.created_at.desc()
        ).all()

    def list_validated(self) -> List[LearningDataset]:
        return self.db.query(LearningDataset).filter(
            LearningDataset.is_validated == True
        ).all()

    def count_validated(self) -> int:
        return self.db.query(LearningDataset).filter(
            LearningDataset.is_validated == True
        ).count()

    def list_unvalidated(self) -> List[LearningDataset]:
        return self.db.query(LearningDataset).filter(
            LearningDataset.is_validated == False
        ).all()


class HeuristicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, heuristic_id: int) -> Optional[Heuristic]:
        return self.db.query(Heuristic).filter(Heuristic.id == heuristic_id).first()

    def get_by_name(self, name: str) -> Optional[Heuristic]:
        return self.db.query(Heuristic).filter(Heuristic.name == name).first()

    def create(self, **kwargs) -> Heuristic:
        heuristic = Heuristic(**kwargs)
        self.db.add(heuristic)
        self.db.commit()
        self.db.refresh(heuristic)
        return heuristic

    def update(self, heuristic: Heuristic, **kwargs) -> Heuristic:
        for key, value in kwargs.items():
            setattr(heuristic, key, value)
        self.db.commit()
        self.db.refresh(heuristic)
        return heuristic

    def list_all(self) -> List[Heuristic]:
        return self.db.query(Heuristic).order_by(Heuristic.priority.desc()).all()

    def list_active(self) -> List[Heuristic]:
        return self.db.query(Heuristic).filter(
            Heuristic.is_active == True
        ).order_by(Heuristic.priority.desc()).all()

    def increment_hit_count(self, heuristic_id: int) -> Optional[Heuristic]:
        heuristic = self.db.query(Heuristic).filter(
            Heuristic.id == heuristic_id
        ).first()
        if heuristic:
            heuristic.hit_count = Heuristic.hit_count + 1
            self.db.commit()
            self.db.refresh(heuristic)
        return heuristic


# =============================================================================
# RAPPORTS
# =============================================================================


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, report_id: int) -> Optional[Report]:
        return self.db.query(Report).filter(Report.id == report_id).first()

    def create(self, **kwargs) -> Report:
        report = Report(**kwargs)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_by_analysis(self, analysis_id: int) -> List[Report]:
        return self.db.query(Report).filter(
            Report.analysis_id == analysis_id
        ).all()

    def list_all(self) -> List[Report]:
        return self.db.query(Report).order_by(
            Report.generated_at.desc()
        ).all()


class ExportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, export_id: int) -> Optional[Export]:
        return self.db.query(Export).filter(Export.id == export_id).first()

    def create(self, **kwargs) -> Export:
        export = Export(**kwargs)
        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)
        return export

    def list_by_report(self, report_id: int) -> List[Export]:
        return self.db.query(Export).filter(
            Export.report_id == report_id
        ).all()

    def list_all(self) -> List[Export]:
        return self.db.query(Export).order_by(
            Export.created_at.desc()
        ).all()


# =============================================================================
# HISTORIQUE
# =============================================================================


class ActivityLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, activity_log_id: int) -> Optional[ActivityLog]:
        return self.db.query(ActivityLog).filter(
            ActivityLog.id == activity_log_id
        ).first()

    def create(self, **kwargs) -> ActivityLog:
        activity_log = ActivityLog(**kwargs)
        self.db.add(activity_log)
        self.db.commit()
        self.db.refresh(activity_log)
        return activity_log

    def list_all(self) -> List[ActivityLog]:
        return self.db.query(ActivityLog).order_by(
            ActivityLog.created_at.desc()
        ).all()

    def list_by_user(self, user_id: int) -> List[ActivityLog]:
        return self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(ActivityLog.created_at.desc()).all()

    def list_by_resource(self, resource_type: str, resource_id: int) -> List[ActivityLog]:
        return self.db.query(ActivityLog).filter(
            ActivityLog.resource_type == resource_type,
            ActivityLog.resource_id == resource_id,
        ).order_by(ActivityLog.created_at.desc()).all()

    def count(self) -> int:
        return self.db.query(ActivityLog).count()
