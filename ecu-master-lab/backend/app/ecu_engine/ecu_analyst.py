"""
PHASE 6 — ECU Analyst Agent.

Combines all knowledge base layers for comprehensive ECU analysis:
  - Layer 1: ECU identification (ecu_matcher)
  - Layer 2: DAMOS map detection (map_detector with DAMOS)
  - Layer 3: Semantic search (semantic_search)
  - Layer 4: Normalization (map_normalizer)
  - Layer 5: Quality scoring (damos_quality_report)
  - Layer 6: LLM enhancement (llm_enhancer)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from .ecu_matcher import ECUMatcher, ECUIdentification
from .map_detector import detect_maps
from .map_normalizer import MapNormalizer
from .semantic_search import SemanticSearchEngine
from .damos_quality_report import generate_quality_report, QualityReport
from .knowledge_extractor import extract_and_store
from .models import DetectedMap, MapDetectionResult

logger = logging.getLogger("ecu_engine.analyst")


@dataclass
class AnalysisResult:
    ecu_identification: Optional[ECUIdentification] = None
    damos_maps: List[dict] = field(default_factory=list)
    map_detection: Optional[MapDetectionResult] = None
    semantic_matches: List[dict] = field(default_factory=list)
    normalized_names: List[dict] = field(default_factory=list)
    quality_report: Optional[dict] = None
    llm_insights: str = ""
    recommendations: List[str] = field(default_factory=list)
    total_processing_time_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "ecu_identification": {
                "name": self.ecu_identification.ecu_name,
                "family": self.ecu_identification.ecu_family,
                "confidence": self.ecu_identification.confidence,
                "match_method": self.ecu_identification.match_method,
                "db_match": self.ecu_identification.db_model_match,
                "damos_match": self.ecu_identification.damos_match,
                "warnings": self.ecu_identification.warnings,
                "candidates": [
                    {
                        "model": c.model_name,
                        "vendor": c.vendor_id,
                        "confidence": c.confidence,
                        "method": c.match_method,
                    }
                    for c in self.ecu_identification.candidates
                ],
            } if self.ecu_identification else None,
            "damos_map_count": len(self.damos_maps),
            "detected_maps": {
                "total": self.map_detection.total_maps_found if self.map_detection else 0,
                "confidence": self.map_detection.confidence if self.map_detection else 0,
                "maps": [
                    {
                        "name": m.name,
                        "category": m.category,
                        "offset": hex(m.offset),
                        "size": m.size,
                        "dimensions": "%dx%d" % (m.rows, m.cols),
                        "status": m.status,
                        "method": m.detection_method,
                        "damos_id": m.damos_map_id,
                    }
                    for m in (self.map_detection.maps[:50] if self.map_detection else [])
                ],
            },
            "semantic_matches_count": len(self.semantic_matches),
            "normalized_names_count": len(self.normalized_names),
            "quality_report": self.quality_report,
            "llm_insights": self.llm_insights,
            "recommendations": self.recommendations,
            "processing_time_ms": self.total_processing_time_ms,
        }


class ECUAnalystAgent:
    """Comprehensive ECU analysis agent using all KB layers."""

    def __init__(self, session: Session):
        self.session = session
        self.ecu_matcher = ECUMatcher(session)
        self.normalizer = MapNormalizer(session)
        self.semantic = SemanticSearchEngine(session)

    def analyze_binary(
        self,
        binary_data: bytes,
        filename: str = "",
        use_damos: bool = True,
        use_llm: bool = False,
        run_quality: bool = False,
    ) -> AnalysisResult:
        """Run comprehensive ECU analysis."""
        import time
        start_ms = int(time.time() * 1000)
        result = AnalysisResult()

        # Step 1: ECU Identification
        logger.info("Step 1: ECU Identification")
        try:
            result.ecu_identification = self.ecu_matcher.identify_ecu(
                binary_data, filename
            )
        except Exception as exc:
            logger.error("ECU identification failed: %s", exc)

        # Step 2: Load DAMOS maps if ECU identified
        damos_maps = []
        if use_damos and result.ecu_identification:
            ecu_name = result.ecu_identification.ecu_name
            damos_maps = self._load_damos_maps(ecu_name)
            result.damos_maps = damos_maps
            logger.info("Loaded %d DAMOS maps for %s", len(damos_maps), ecu_name)

        # Step 3: Map Detection (with DAMOS)
        logger.info("Step 3: Map Detection")
        try:
            known_strings = self._load_known_strings()
            result.map_detection = detect_maps(
                binary_data,
                damos_maps=damos_maps,
                known_strings=known_strings,
            )
        except Exception as exc:
            logger.error("Map detection failed: %s", exc)

        # Step 4: Semantic search for detected maps
        if result.map_detection and result.map_detection.maps:
            logger.info("Step 4: Semantic Search")
            try:
                top_maps = result.map_detection.maps[:20]
                for dm in top_maps:
                    matches = self.semantic.search(
                        dm.name,
                        ecu_filter=result.ecu_identification.ecu_name if result.ecu_identification else None,
                        limit=3,
                    )
                    if matches:
                        result.semantic_matches.extend(matches)
            except Exception as exc:
                logger.error("Semantic search failed: %s", exc)

        # Step 5: Normalize map names
        if result.map_detection and result.map_detection.maps:
            logger.info("Step 5: Name Normalization")
            try:
                names = [m.name for m in result.map_detection.maps[:50]]
                normalized = self.normalizer.normalize_batch(names)
                result.normalized_names = [
                    {
                        "original": n.name_de,
                        "normalized": n.name_en,
                        "category": n.category,
                        "confidence": n.confidence,
                    }
                    for n in normalized
                ]
            except Exception as exc:
                logger.error("Normalization failed: %s", exc)

        # Step 6: Quality report
        if run_quality:
            logger.info("Step 6: Quality Report")
            try:
                report = generate_quality_report(self.session)
                result.quality_report = report.to_dict()
            except Exception as exc:
                logger.error("Quality report failed: %s", exc)

        # Step 7: LLM insights
        if use_llm:
            logger.info("Step 7: LLM Enhancement")
            try:
                from .llm_enhancer import enhance_report
                llm_result = enhance_report(
                    self._build_llm_context(result),
                    filename=filename,
                )
                result.llm_insights = llm_result.get("text", "")
            except Exception as exc:
                logger.error("LLM enhancement failed: %s", exc)

        # Step 8: Recommendations
        result.recommendations = self._generate_recommendations(result)

        elapsed = int(time.time() * 1000) - start_ms
        result.total_processing_time_ms = elapsed
        logger.info("Analysis complete in %dms", elapsed)

        return result

    def _load_damos_maps(self, ecu_name: str) -> List[dict]:
        """Load DAMOS maps for an ECU from DB."""
        try:
            rows = self.session.execute(text("""
                SELECT id, map_name, category, offset_hex, offset_dec,
                       size_bytes, unit, ecu_model_name
                FROM known_maps
                WHERE ecu_model_name LIKE :ecu
                ORDER BY offset_dec ASC
            """), {"ecu": "%" + ecu_name + "%"}).fetchall()

            return [
                {
                    "id": r[0], "map_name": r[1], "category": r[2],
                    "offset_hex": r[3], "offset_dec": r[4] or 0,
                    "size_bytes": r[5] or 256, "unit": r[6],
                    "ecu_model_name": r[7],
                }
                for r in rows
            ]
        except Exception:
            return []

    def _load_known_strings(self) -> List[str]:
        """Load known strings for signature detection."""
        try:
            rows = self.session.execute(text("""
                SELECT DISTINCT string_content FROM known_strings
                WHERE LENGTH(string_content) >= 4
                LIMIT 200
            """)).fetchall()
            return [r[0] for r in rows if r[0]]
        except Exception:
            return []

    def _build_llm_context(self, result: AnalysisResult) -> str:
        """Build context string for LLM analysis."""
        parts = []
        if result.ecu_identification:
            parts.append("ECU: %s (confidence: %.1f%%)" % (
                result.ecu_identification.ecu_name,
                result.ecu_identification.confidence * 100,
            ))
        if result.damos_maps:
            parts.append("DAMOS maps available: %d" % len(result.damos_maps))
        if result.map_detection:
            parts.append("Maps detected: %d (confidence: %.1f%%)" % (
                result.map_detection.total_maps_found,
                result.map_detection.confidence * 100,
            ))
        if result.semantic_matches:
            parts.append("Semantic matches: %d" % len(result.semantic_matches))
        return "\n".join(parts)

    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if result.ecu_identification:
            conf = result.ecu_identification.confidence
            if conf < 0.5:
                recs.append("Low ECU identification confidence. Consider manual verification.")
            if not result.ecu_identification.damos_match:
                recs.append("No DAMOS data found for this ECU. Map detection may be less accurate.")

        if result.map_detection:
            detected = result.map_detection.total_maps_found
            if detected == 0:
                recs.append("No maps detected. File may be encrypted or use unknown format.")
            elif detected < 10:
                recs.append("Few maps detected. Consider checking calibration region boundaries.")

        if not result.damos_maps:
            recs.append("Upload DAMOS/A2L data for this ECU to improve detection accuracy.")

        if result.quality_report and result.quality_report.get("overall_score", 100) < 70:
            recs.append("Knowledge base quality is below 70%. Run seed_data.py to enrich.")

        return recs
