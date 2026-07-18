from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.repositories.v2.ecu_repositories import (
    ActivityLogRepository,
    AIModelRepository,
    AIPredictionRepository,
    AnalysisHypothesisRepository,
    AnalysisRepository,
    AnalysisResultRepository,
    AnalysisScoreRepository,
    BinaryPatternRepository,
    ChecksumAlgorithmRepository,
    ChecksumResultRepository,
    DetectedMapRepository,
    DetectedSegmentRepository,
    ECUFileRepository,
    ECUModelRepository,
    ECUSignatureRepository,
    ECUVariantRepository,
    ExportRepository,
    HardwareVersionRepository,
    HeuristicRepository,
    LearningDatasetRepository,
    ManufacturerRepository,
    MapAxisRepository,
    MapCategoryRepository,
    MapRepository,
    MapUnitRepository,
    MemoryLayoutRepository,
    MemorySegmentRepository,
    ProcessorRepository,
    ProtocolRepository,
    ReportRepository,
    SoftwareVersionRepository,
    VehicleBrandRepository,
    VehicleEngineRepository,
    VehicleModelRepository,
)
from app.schemas.ecu_schemas import (
    ActivityLogCreate,
    ActivityLogUpdate,
    AIModelCreate,
    AIModelUpdate,
    AIPredictionCreate,
    AnalysisCreate,
    AnalysisHypothesisCreate,
    AnalysisHypothesisUpdate,
    AnalysisResultCreate,
    AnalysisResultUpdate,
    AnalysisScoreCreate,
    AnalysisScoreUpdate,
    AnalysisUpdate,
    BinaryPatternCreate,
    BinaryPatternUpdate,
    ChecksumAlgorithmCreate,
    ChecksumAlgorithmUpdate,
    ChecksumResultCreate,
    DetectedMapCreate,
    DetectedSegmentCreate,
    ECUFileCreate,
    ECUFileUpdate,
    ECUModelCreate,
    ECUModelUpdate,
    ECUSignatureCreate,
    ECUSignatureUpdate,
    ECUVariantCreate,
    ECUVariantUpdate,
    ExportCreate,
    HardwareVersionCreate,
    HardwareVersionUpdate,
    HeuristicCreate,
    HeuristicUpdate,
    LearningDatasetCreate,
    LearningDatasetUpdate,
    ManufacturerCreate,
    ManufacturerUpdate,
    MapAxisCreate,
    MapAxisUpdate,
    MapCategoryCreate,
    MapCategoryUpdate,
    MapCreate,
    MapUnitCreate,
    MapUnitUpdate,
    MapUpdate,
    MemoryLayoutCreate,
    MemoryLayoutUpdate,
    MemorySegmentCreate,
    MemorySegmentUpdate,
    ProcessorCreate,
    ProcessorUpdate,
    ProtocolCreate,
    ProtocolUpdate,
    ReportCreate,
    SoftwareVersionCreate,
    SoftwareVersionUpdate,
    VehicleBrandCreate,
    VehicleBrandUpdate,
    VehicleEngineCreate,
    VehicleEngineUpdate,
    VehicleModelCreate,
    VehicleModelUpdate,
)

logger = logging.getLogger(__name__)


# =============================================================================
# REFERENTIEL SERVICES
# =============================================================================


class ManufacturerService:
    def __init__(self, db: Session) -> None:
        self.repo = ManufacturerRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ManufacturerCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ManufacturerUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def search(self, query: str) -> List[Any]:
        return self.repo.search(query)


class ECUModelService:
    def __init__(self, db: Session) -> None:
        self.repo = ECUModelRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ECUModelCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ECUModelUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_manufacturer(self, manufacturer_id: int) -> List[Any]:
        return self.repo.list_by_manufacturer(manufacturer_id)

    def search(self, query: str) -> List[Any]:
        return self.repo.search(query)


class ECUVariantService:
    def __init__(self, db: Session) -> None:
        self.repo = ECUVariantRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ECUVariantCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ECUVariantUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)


class ProcessorService:
    def __init__(self, db: Session) -> None:
        self.repo = ProcessorRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def create(self, data: ProcessorCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ProcessorUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class ProtocolService:
    def __init__(self, db: Session) -> None:
        self.repo = ProtocolRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def create(self, data: ProtocolCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ProtocolUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class ChecksumAlgorithmService:
    def __init__(self, db: Session) -> None:
        self.repo = ChecksumAlgorithmRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def create(self, data: ChecksumAlgorithmCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ChecksumAlgorithmUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


# =============================================================================
# VEHICLE SERVICES
# =============================================================================


class VehicleBrandService:
    def __init__(self, db: Session) -> None:
        self.repo = VehicleBrandRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def create(self, data: VehicleBrandCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: VehicleBrandUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class VehicleModelService:
    def __init__(self, db: Session) -> None:
        self.repo = VehicleModelRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: VehicleModelCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: VehicleModelUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_brand(self, brand_id: int) -> List[Any]:
        return self.repo.list_by_brand(brand_id)


class VehicleEngineService:
    def __init__(self, db: Session) -> None:
        self.repo = VehicleEngineRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: VehicleEngineCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: VehicleEngineUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, model_id: int) -> List[Any]:
        return self.repo.list_by_model(model_id)


# =============================================================================
# VERSION SERVICES
# =============================================================================


class SoftwareVersionService:
    def __init__(self, db: Session) -> None:
        self.repo = SoftwareVersionRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: SoftwareVersionCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: SoftwareVersionUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)

    def find_by_sw_number(self, sw_number: str) -> Optional[Any]:
        return self.repo.find_by_sw_number(sw_number)

    def find_by_calibration_id(self, calibration_id: str) -> Optional[Any]:
        return self.repo.find_by_calibration_id(calibration_id)


class HardwareVersionService:
    def __init__(self, db: Session) -> None:
        self.repo = HardwareVersionRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: HardwareVersionCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: HardwareVersionUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)


# =============================================================================
# MEMORY SERVICES
# =============================================================================


class MemoryLayoutService:
    def __init__(self, db: Session) -> None:
        self.repo = MemoryLayoutRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: MemoryLayoutCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MemoryLayoutUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)


class MemorySegmentService:
    def __init__(self, db: Session) -> None:
        self.repo = MemorySegmentRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: MemorySegmentCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MemorySegmentUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_layout(self, layout_id: int) -> List[Any]:
        return self.repo.list_by_layout(layout_id)


# =============================================================================
# SIGNATURE SERVICES
# =============================================================================


class ECUSignatureService:
    def __init__(self, db: Session) -> None:
        self.repo = ECUSignatureRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ECUSignatureCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ECUSignatureUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)


class BinaryPatternService:
    def __init__(self, db: Session) -> None:
        self.repo = BinaryPatternRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: BinaryPatternCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: BinaryPatternUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)


# =============================================================================
# MAP SERVICES
# =============================================================================


class MapCategoryService:
    def __init__(self, db: Session) -> None:
        self.repo = MapCategoryRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def create(self, data: MapCategoryCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MapCategoryUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_root_categories(self) -> List[Any]:
        return self.repo.list_root_categories()


class MapUnitService:
    def __init__(self, db: Session) -> None:
        self.repo = MapUnitRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_symbol(self, symbol: str) -> Optional[Any]:
        return self.repo.get_by_symbol(symbol)

    def create(self, data: MapUnitCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MapUnitUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class MapAxisService:
    def __init__(self, db: Session) -> None:
        self.repo = MapAxisRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: MapAxisCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MapAxisUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class MapService:
    def __init__(self, db: Session) -> None:
        self.repo = MapRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: MapCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: MapUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_model(self, ecu_model_id: int) -> List[Any]:
        return self.repo.list_by_model(ecu_model_id)

    def list_by_category(self, category_id: int) -> List[Any]:
        return self.repo.list_by_category(category_id)

    def search(self, query: str) -> List[Any]:
        return self.repo.search(query)


# =============================================================================
# ECU FILE SERVICE
# =============================================================================


class ECUFileService:
    def __init__(self, db: Session) -> None:
        self.repo = ECUFileRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_sha256(self, sha256: str) -> Optional[Any]:
        return self.repo.get_by_sha256(sha256)

    def create(self, data: ECUFileCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: ECUFileUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_project(self, project_id: int) -> List[Any]:
        return self.repo.list_by_project(project_id)

    def count(self) -> int:
        return self.repo.count()

    def register_upload(
        self,
        filename: str,
        file_path: str,
        file_size: int,
        sha256: str,
        md5: Optional[str],
        file_format: Optional[str],
        project_id: Optional[int],
        user_id: Optional[int],
    ) -> Any:
        return self.repo.create(
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            sha256=sha256,
            md5=md5,
            file_format=file_format,
            project_id=project_id,
            uploaded_by=user_id,
        )


# =============================================================================
# ANALYSIS SERVICE
# =============================================================================


class AnalysisService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AnalysisRepository(db)
        self.hypothesis_repo = AnalysisHypothesisRepository(db)
        self.score_repo = AnalysisScoreRepository(db)
        self.detected_map_repo = DetectedMapRepository(db)
        self.detected_segment_repo = DetectedSegmentRepository(db)
        self.checksum_repo = ChecksumResultRepository(db)
        self.result_repo = AnalysisResultRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: AnalysisCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: AnalysisUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_by_file(self, ecu_file_id: int) -> List[Any]:
        return self.repo.list_by_file(ecu_file_id)

    def get_latest_by_file(self, ecu_file_id: int) -> Optional[Any]:
        return self.repo.get_latest_by_file(ecu_file_id)

    def count(self) -> int:
        return self.repo.count()

    def save_analysis(self, ecu_file_id: int, engine_result: dict) -> Any:
        analysis = self.repo.create(
            ecu_file_id=ecu_file_id,
            detected_manufacturer=engine_result.get("detected_manufacturer"),
            detected_ecu_model=engine_result.get("detected_ecu_model"),
            detected_ecu_family=engine_result.get("detected_ecu_family"),
            detected_processor=engine_result.get("detected_processor"),
            detected_protocol=engine_result.get("detected_protocol"),
            detected_hw_version=engine_result.get(
                "detected_hw_version", engine_result.get("hw_version")
            ),
            detected_sw_version=engine_result.get(
                "detected_sw_version", engine_result.get("sw_version")
            ),
            detected_brand=engine_result.get(
                "detected_brand", engine_result.get("ecu_brand")
            ),
            detected_engine=engine_result.get("detected_engine"),
            confidence=engine_result.get("confidence"),
            consistency_score=engine_result.get("consistency_score"),
            needs_review=engine_result.get("needs_review", False),
            review_reasons=self._serialize_review_reasons(
                engine_result.get("review_reasons", [])
            ),
            processing_time_ms=int(
                engine_result.get("processing_time_seconds", 0) * 1000
            ),
            engine_version=None,
        )

        self._save_hypotheses(analysis.id, engine_result)
        self._save_scores(analysis.id, engine_result)
        self._save_detected_maps(analysis.id, engine_result)
        self._save_detected_segments(analysis.id, engine_result)
        self._save_checksums(analysis.id, engine_result)
        self._save_layer_results(analysis.id, engine_result)

        return self.repo.get_by_id(analysis.id)

    def _serialize_review_reasons(self, reasons: Any) -> Optional[str]:
        if not reasons:
            return None
        if isinstance(reasons, list):
            texts = []
            for r in reasons:
                if isinstance(r, dict):
                    texts.append(r.get("reason", str(r)))
                else:
                    texts.append(str(r))
            return "; ".join(texts)
        return str(reasons)

    def _save_hypotheses(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        hypotheses = engine_result.get("hypotheses", [])
        for idx, h in enumerate(hypotheses):
            evidence = h.get("evidence", [])
            if isinstance(evidence, list):
                evidence = "; ".join(str(e) for e in evidence)
            rejection_reasons = h.get("rejection_reasons", [])
            if isinstance(rejection_reasons, list):
                rejection_reasons = "; ".join(
                    str(r) for r in rejection_reasons
                )
            self.hypothesis_repo.create(
                analysis_id=analysis_id,
                rank=h.get("rank", idx + 1),
                ecu_model_id=h.get("ecu_model_id"),
                ecu_name=h.get(
                    "ecu_name",
                    h.get("ecu_model", h.get("ecu_id", "Unknown")),
                ),
                probability=h.get(
                    "probability", h.get("confidence", 0.0)
                ),
                evidence=evidence if evidence else None,
                is_rejected=h.get("rejected", h.get("is_rejected", False)),
                rejection_reasons=(
                    rejection_reasons if rejection_reasons else None
                ),
            )

    def _save_scores(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        scores = engine_result.get("scores", [])
        for s in scores:
            self.score_repo.create(
                analysis_id=analysis_id,
                factor=s.get("factor", ""),
                raw_score=s.get("raw_score", 0.0),
                weight=s.get("weight", 1.0),
                weighted_score=s.get("weighted_score", 0.0),
                explanation=s.get("explanation"),
            )

    def _save_detected_maps(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        maps_data = engine_result.get("maps")
        map_list: List[dict] = []
        if isinstance(maps_data, dict):
            map_list = maps_data.get("maps", [])
        elif isinstance(maps_data, list):
            map_list = maps_data

        if not map_list:
            map_list = engine_result.get("map_regions", [])

        for m in map_list:
            offset = m.get("offset", m.get("offset_dec", 0))
            offset_dec = offset if isinstance(offset, int) else 0
            offset_hex = m.get("offset_hex")
            if not offset_hex and offset_dec:
                offset_hex = hex(offset_dec)

            size = m.get("size", m.get("size_bytes", 0))
            data_type = m.get("data_type", "")
            if isinstance(data_type, dict):
                data_type = data_type.get("value", str(data_type))

            self.detected_map_repo.create(
                analysis_id=analysis_id,
                map_id=m.get("map_id"),
                map_name=m.get("name", m.get("map_name", "")),
                offset_hex=offset_hex,
                offset_dec=offset_dec,
                size_bytes=size if isinstance(size, int) else 0,
                rows=m.get("rows"),
                cols=m.get("cols"),
                data_type=str(data_type) if data_type else None,
                min_value=m.get("min_value"),
                max_value=m.get("max_value"),
                avg_value=m.get("avg_value"),
                entropy=m.get("entropy"),
                non_empty_ratio=m.get("non_empty_ratio"),
                status=m.get("status"),
                detection_method=m.get("detection_method"),
                confidence=m.get("confidence"),
            )

    def _save_detected_segments(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        seg_data = engine_result.get("segments")
        seg_list: List[dict] = []
        if isinstance(seg_data, dict):
            seg_list = seg_data.get("segments", [])
        elif isinstance(seg_data, list):
            seg_list = seg_data

        for s in seg_list:
            seg_type = s.get("segment_type", s.get("seg_type", ""))
            if isinstance(seg_type, dict):
                seg_type = seg_type.get("value", str(seg_type))

            self.detected_segment_repo.create(
                analysis_id=analysis_id,
                segment_type=str(seg_type) if seg_type else "Unknown",
                start_offset=s.get("start_offset", 0),
                end_offset=s.get("end_offset", 0),
                size_bytes=s.get("size", s.get("size_bytes", 0)),
                entropy=s.get("entropy"),
                non_empty_ratio=s.get("non_empty_ratio"),
                is_valid=s.get("is_valid", True),
                explanation=s.get("explanation"),
            )

    def _save_checksums(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        checksums = engine_result.get("checksums")
        if not checksums:
            single = engine_result.get("checksum")
            if single:
                checksums = [single]
            else:
                checksums = []

        if not isinstance(checksums, list):
            checksums = []

        for c in checksums:
            data_range = c.get("data_range", (0, 0))
            if isinstance(data_range, (list, tuple)) and len(data_range) >= 2:
                data_start = data_range[0]
                data_end = data_range[1]
            else:
                data_start = c.get("data_start")
                data_end = c.get("data_end")

            self.checksum_repo.create(
                analysis_id=analysis_id,
                algorithm=c.get("algorithm", ""),
                offset=c.get("offset"),
                size=c.get("size"),
                stored_value=c.get("stored_value"),
                computed_value=c.get("computed_value"),
                is_valid=c.get("is_valid"),
                data_start=data_start,
                data_end=data_end,
                explanation=c.get("explanation"),
            )

    def _save_layer_results(
        self, analysis_id: int, engine_result: dict
    ) -> None:
        layers = engine_result.get("layers")
        if not layers:
            layers = engine_result.get("pipeline_steps", [])
        if not layers:
            layers = engine_result.get("analysis_steps", [])

        for layer in layers:
            name = layer.get("name", "")
            details = layer.get("details", [])
            if isinstance(details, list):
                details = "; ".join(str(d) for d in details)

            self.result_repo.create(
                analysis_id=analysis_id,
                result_type=name,
                result_data=json.dumps(layer, default=str),
                confidence=layer.get("confidence_contribution"),
                explanation=layer.get(
                    "result_summary", layer.get("explanation")
                ),
            )


# =============================================================================
# ANALYSIS SUB-SERVICES
# =============================================================================


class AnalysisResultService:
    def __init__(self, db: Session) -> None:
        self.repo = AnalysisResultRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def list_by_type(self, analysis_id: int, result_type: str) -> List[Any]:
        return self.repo.list_by_type(analysis_id, result_type)

    def create(self, data: AnalysisResultCreate) -> Any:
        return self.repo.create(**data.model_dump())


class AnalysisHypothesisService:
    def __init__(self, db: Session) -> None:
        self.repo = AnalysisHypothesisRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def create(self, data: AnalysisHypothesisCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: AnalysisHypothesisUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class AnalysisScoreService:
    def __init__(self, db: Session) -> None:
        self.repo = AnalysisScoreRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def create(self, data: AnalysisScoreCreate) -> Any:
        return self.repo.create(**data.model_dump())


class DetectedMapService:
    def __init__(self, db: Session) -> None:
        self.repo = DetectedMapRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def create(self, data: DetectedMapCreate) -> Any:
        return self.repo.create(**data.model_dump())


class DetectedSegmentService:
    def __init__(self, db: Session) -> None:
        self.repo = DetectedSegmentRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def create(self, data: DetectedSegmentCreate) -> Any:
        return self.repo.create(**data.model_dump())


class ChecksumResultService:
    def __init__(self, db: Session) -> None:
        self.repo = ChecksumResultRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def create(self, data: ChecksumResultCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def count_invalid(self, analysis_id: int) -> int:
        return self.repo.count_invalid(analysis_id)


# =============================================================================
# AI SERVICES
# =============================================================================


class AIModelService:
    def __init__(self, db: Session) -> None:
        self.repo = AIModelRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_active_models(self) -> List[Any]:
        return self.repo.get_active_models()

    def get_latest_active(self) -> Optional[Any]:
        return self.repo.get_latest_active()

    def create(self, data: AIModelCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: AIModelUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))


class AIPredictionService:
    def __init__(self, db: Session) -> None:
        self.repo = AIPredictionRepository(db)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)

    def list_by_model(self, model_id: int) -> List[Any]:
        return self.repo.list_by_model(model_id)

    def create(self, data: AIPredictionCreate) -> Any:
        return self.repo.create(**data.model_dump())


class LearningDatasetService:
    def __init__(self, db: Session) -> None:
        self.repo = LearningDatasetRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: LearningDatasetCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def update(self, id: int, data: LearningDatasetUpdate) -> Optional[Any]:
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **data.model_dump(exclude_unset=True))

    def list_validated(self) -> List[Any]:
        return self.repo.list_validated()

    def list_unvalidated(self) -> List[Any]:
        return self.repo.list_unvalidated()

    def count_validated(self) -> int:
        return self.repo.count_validated()


class HeuristicService:
    def __init__(self, db: Session) -> None:
        self.repo = HeuristicRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def get_by_name(self, name: str) -> Optional[Any]:
        return self.repo.get_by_name(name)

    def get_active(self) -> List[Any]:
        return self.repo.get_active()

    def create(self, data: HeuristicCreate) -> Any:
        payload = data.model_dump()
        rule = payload.get("rule_json")
        if isinstance(rule, dict):
            payload["rule_json"] = json.dumps(rule)
        return self.repo.create(**payload)

    def update(self, id: int, data: HeuristicUpdate) -> Optional[Any]:
        payload = data.model_dump(exclude_unset=True)
        rule = payload.get("rule_json")
        if isinstance(rule, dict):
            payload["rule_json"] = json.dumps(rule)
        obj = self.repo.get_by_id(id)
        if not obj:
            return None
        return self.repo.update(obj, **payload)

    def increment_hit_count(self, id: int) -> Optional[Any]:
        return self.repo.increment_hit_count(id)


# =============================================================================
# REPORT SERVICES
# =============================================================================


class ReportService:
    def __init__(self, db: Session) -> None:
        self.repo = ReportRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ReportCreate) -> Any:
        payload = data.model_dump()
        content = payload.get("content_json")
        if isinstance(content, dict):
            payload["content_json"] = json.dumps(content)
        return self.repo.create(**payload)

    def list_by_analysis(self, analysis_id: int) -> List[Any]:
        return self.repo.list_by_analysis(analysis_id)


class ExportService:
    def __init__(self, db: Session) -> None:
        self.repo = ExportRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ExportCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def list_by_report(self, report_id: int) -> List[Any]:
        return self.repo.list_by_report(report_id)


# =============================================================================
# ACTIVITY LOG SERVICE
# =============================================================================


class ActivityLogService:
    def __init__(self, db: Session) -> None:
        self.repo = ActivityLogRepository(db)

    def list_all(self) -> List[Any]:
        return self.repo.list_all()

    def get_by_id(self, id: int) -> Optional[Any]:
        return self.repo.get_by_id(id)

    def create(self, data: ActivityLogCreate) -> Any:
        return self.repo.create(**data.model_dump())

    def list_by_user(self, user_id: int) -> List[Any]:
        return self.repo.list_by_user(user_id)

    def list_by_resource(
        self, resource_type: str, resource_id: Optional[int] = None
    ) -> List[Any]:
        return self.repo.list_by_resource(resource_type, resource_id)

    def count(self) -> int:
        return self.repo.count()
