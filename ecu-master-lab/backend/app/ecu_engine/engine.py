"""
ECU Engine — Main orchestrator tying all 10 pipeline layers together.

Runs each layer sequentially, records timing and confidence per step,
assembles a full ECUReport via the report generator, and returns a
JSON-serializable dict.
"""

import logging
import time
from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .format_detector import detect_format
from .processor_identifier import identify_processor
from .memory_identifier import identify_memory
from .info_extractor import extract_technical_info
from .signature_scanner import scan_signatures
from .segment_analyzer import analyze_segments
from .map_detector import detect_maps
from .checksum_engine import auto_detect_checksum, verify_checksum
from .cross_validator import cross_validate
from .report_generator import generate_report
from .models import PipelineStep, ECUReport
from .utils import compute_hashes

logger = logging.getLogger("ecu_engine")


# ==============================================================
#  SERIALIZATION HELPERS
# ==============================================================

def _to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses, enums and bytes to
    JSON-safe primitives."""
    if obj is None or isinstance(obj, (int, float, str, bool)):
        return obj
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, tuple):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, list):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        return {
            f.name: _to_jsonable(getattr(obj, f.name))
            for f in fields(obj)
        }
    return str(obj)


# ==============================================================
#  PIPELINE HELPERS
# ==============================================================

def _calibration_region(
    memory_layout: Optional[Any],
) -> Tuple[int, int]:
    """Extract calibration offset and size from the memory layout.
    Falls back to (0, 0) when no suitable region is found."""
    if memory_layout and memory_layout.regions:
        for region in memory_layout.regions:
            rtype = getattr(region.mem_type, "value", str(region.mem_type))
            if rtype in ("Flash", "Calibration"):
                return (region.start_address, region.size)
    return (0, 0)


def _best_checksum(results: Optional[List[Any]]) -> Optional[Any]:
    """Pick the most informative single ChecksumResult from a list.
    Prefers a valid result, then an invalid one, then the first."""
    if not results:
        return None
    for r in results:
        if r.is_valid is True:
            return r
    for r in results:
        if r.is_valid is False:
            return r
    return results[0]


def _add_compat_keys(serialized: dict, report: "ECUReport") -> dict:
    """Add backward-compatible top-level keys that the old API expected."""
    serialized["ecu_type"] = report.detected_ecu or "Inconnu"
    serialized["ecu_brand"] = report.detected_manufacturer or "Inconnu"
    serialized["detected_brand"] = report.detected_brand or report.detected_manufacturer or "Inconnu"
    serialized["detected_engine"] = report.detected_engine or "Inconnu"
    serialized["hw_version"] = report.detected_hw_version or "Inconnu"
    serialized["sw_version"] = report.detected_sw_version or "Inconnu"
    serialized["file_size"] = report.file_size
    serialized["file_hash"] = report.file_hash_sha256
    serialized["file_format"] = report.format_result.format_type.value if report.format_result else "unknown"
    serialized["checksum_valid"] = report.checksum.is_valid if report.checksum else None
    serialized["checksum_algorithm"] = report.checksum.algorithm if report.checksum else "Inconnu"
    serialized["confidence"] = report.confidence
    serialized["has_encryption"] = False
    serialized["has_proprietary_format"] = False
    serialized["compatible_modifications"] = report.compatible_modifications
    serialized["map_regions"] = _to_jsonable(report.maps.maps) if report.maps else []
    serialized["total_map_bytes"] = report.maps.total_map_bytes if report.maps else 0
    serialized["risks"] = [r.message for r in report.risks]
    serialized["review_reasons"] = [r.reason for r in report.review_reasons]
    serialized["recommendation"] = report.recommendations[0] if report.recommendations else ""
    serialized["consistency_score"] = report.consistency_score
    serialized["needs_review"] = report.needs_review
    serialized["recommended_protocol"] = report.detected_protocol or "Inconnu"
    serialized["processing_time_seconds"] = report.processing_time_seconds
    serialized["analysis_steps"] = _to_jsonable(report.pipeline_steps)
    return serialized


# ==============================================================
#  ECUEngine CLASS
# ==============================================================

class ECUEngine:
    """Main ECU analysis engine orchestrating the 10-layer pipeline."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("ecu_engine")

    # ----------------------------------------------------------
    #  PUBLIC API
    # ----------------------------------------------------------

    async def analyze(self, file_path: str, data: bytes, db=None) -> dict:
        """Run the full 10-layer analysis pipeline and return a
        JSON-serializable report dict.

        If ``db`` is provided, Layer 9 will query the knowledge database
        for identification matching before falling back to hardcoded profiles.
        """
        start_time = time.time()
        steps: List[PipelineStep] = []
        all_results: Dict[str, Any] = {}

        file_name = file_path.replace("\\", "/").rsplit("/", 1)[-1]
        hashes = compute_hashes(data)
        all_results["hashes"] = hashes

        # Layer 1: Format detection
        fmt = self._run(1, "format_detection", steps,
                        lambda: detect_format(data, file_name))
        all_results["format"] = fmt

        # Layer 2: Processor identification
        proc = self._run(2, "processor_identification", steps,
                         lambda: identify_processor(data))
        all_results["processor"] = proc

        # Layer 3: Memory layout identification
        profile = proc.primary if proc and proc.detected else None
        mem = self._run(3, "memory_identification", steps,
                        lambda: identify_memory(data, profile))
        all_results["memory"] = mem

        # Layer 4: Technical info extraction
        tech = self._run(4, "info_extraction", steps,
                         lambda: extract_technical_info(data))
        all_results["tech_info"] = tech

        # Layer 5: Signature scanning
        sigs = self._run(5, "signature_scanning", steps,
                         lambda: scan_signatures(data))
        all_results["signatures"] = sigs

        # Layer 6: Segment analysis
        segs = self._run(6, "segment_analysis", steps,
                         lambda: analyze_segments(data, mem))
        all_results["segments"] = segs

        # Layer 7: Map detection (uses calibration region from memory)
        cal_off, cal_sz = _calibration_region(mem)
        maps = self._run(7, "map_detection", steps,
                         lambda: detect_maps(data, cal_off, cal_sz))
        all_results["maps"] = maps

        # Layer 8: Checksum verification
        model_hint = ""
        if tech and tech.hw_number:
            model_hint = tech.hw_number
        elif proc and proc.primary:
            model_hint = proc.primary.core
        chk_list = self._run(8, "checksum_verification", steps,
                             lambda: auto_detect_checksum(data, model_hint))
        all_results["checksums"] = chk_list
        chk = _best_checksum(
            chk_list if isinstance(chk_list, list) else None)

        # Layer 9: Cross validation
        xval = self._run(9, "cross_validation", steps,
                         lambda: cross_validate(
                             data, fmt, proc, tech, sigs,
                             mem, maps, chk, db=db))
        all_results["cross_validation"] = xval

        # Layer 10: Report generation
        elapsed = time.time() - start_time
        report = self._run(
            10, "report_generation", steps,
            lambda: generate_report(
                file_name, data, fmt, proc, mem, tech,
                sigs, segs, maps, chk_list if isinstance(
                    chk_list, list) else [],
                xval, steps, elapsed))

        # Layer 11 (optional): LLM enhancement via Mistral
        llm_result = None
        if isinstance(report, ECUReport):
            try:
                from .llm_enhancer import enhance_report
                analysis_id = hashes.get("sha256", file_name)
                llm_result = enhance_report(report, analysis_id)
            except Exception as exc:
                self.logger.info("LLM enhancement skipped: %s", exc)
        else:
            try:
                from .llm_enhancer import enhance_report
                analysis_id = hashes.get("sha256", file_name)
                # For dict reports, create a lightweight shim
                class _ReportShim:
                    pass
                shim = _ReportShim()
                for k in ("file_name","file_size","file_type","file_entropy",
                          "brand_guess","file_type_detailed","confidence",
                          "processor_info","checksum_info","maps_summary",
                          "db_match_info","referentiel_info","segments","anomalies",
                          "knowledge_stats"):
                    setattr(shim, k, report.get(k) if isinstance(report, dict) else None)
                shim.file_name = report.get("file_name", file_name) if isinstance(report, dict) else file_name
                shim.file_size = report.get("file_size", 0) if isinstance(report, dict) else 0
                shim.file_type = report.get("file_type", "unknown") if isinstance(report, dict) else "unknown"
                shim.file_entropy = report.get("file_entropy", 0.0) if isinstance(report, dict) else 0.0
                llm_result = enhance_report(shim, analysis_id)
            except Exception as exc:
                self.logger.info("LLM enhancement skipped: %s", exc)

        # Finalize: attach metadata and serialize
        total_ms = sum(s.duration_ms for s in steps)

        if isinstance(report, ECUReport):
            report.file_hash_sha256 = hashes.get("sha256", "")
            report.file_hash_md5 = hashes.get("md5", "")
            report.pipeline_steps = steps
            report.processing_time_seconds = elapsed
            report.total_pipeline_time_ms = total_ms
            serialized = self._serialize_report(report)
            if llm_result:
                serialized["llm_analysis"] = llm_result
            return _add_compat_keys(serialized, report)

        if isinstance(report, dict):
            report.setdefault("file_hash_sha256",
                              hashes.get("sha256", ""))
            report.setdefault("file_hash_md5",
                              hashes.get("md5", ""))
            report["pipeline_steps"] = _to_jsonable(steps)
            report["processing_time_seconds"] = elapsed
            report["total_pipeline_time_ms"] = total_ms
            if llm_result:
                report["llm_analysis"] = llm_result
            return report

        return {
            "results": all_results,
            "hashes": hashes,
            "pipeline_steps": _to_jsonable(steps),
            "processing_time_seconds": elapsed,
            "total_pipeline_time_ms": total_ms,
        }

    # ----------------------------------------------------------
    #  INTERNAL HELPERS
    # ----------------------------------------------------------

    def _run(
        self,
        num: int,
        name: str,
        steps: List[PipelineStep],
        fn: Callable,
    ) -> Any:
        """Execute a single pipeline layer inside a try/except,
        record timing and confidence as a PipelineStep."""
        step = PipelineStep(step=num, name=name, status="running")
        t0 = time.time()
        try:
            result = fn()
            step.status = "success"
            step.duration_ms = (time.time() - t0) * 1000.0
            if result is not None:
                if hasattr(result, "confidence"):
                    step.confidence_contribution = result.confidence
                if hasattr(result, "explanation"):
                    step.result_summary = str(result.explanation)[:200]
                if hasattr(result, "warnings"):
                    step.warnings = list(result.warnings)
            self.logger.info(
                "Layer %d (%s): OK in %.1f ms",
                num, name, step.duration_ms)
            steps.append(step)
            return result
        except Exception as exc:
            step.status = "error"
            step.duration_ms = (time.time() - t0) * 1000.0
            step.result_summary = str(exc)[:200]
            step.details.append(type(exc).__name__)
            self.logger.exception(
                "Layer %d (%s) failed", num, name)
            steps.append(step)
            return None

    def _serialize_report(self, report: ECUReport) -> dict:
        """Convert an ECUReport dataclass to a JSON-safe dict."""
        return _to_jsonable(report)


# ==============================================================
#  MODULE-LEVEL COMPATIBILITY API
# ==============================================================

async def analyze_ecu_file(
    file_path: str, file_content: bytes, db=None
) -> dict:
    """Existing API called by projects.py. Creates an ECUEngine
    instance and delegates to its analyze method.

    If ``db`` is provided, it is passed to Layer 9 for knowledge DB matching.
    """
    engine = ECUEngine()
    return await engine.analyze(file_path, file_content, db=db)


async def generate_modified_file(
    original_content: bytes,
    analysis: dict,
    modifications: list,
) -> bytes:
    """Simulation: copy original bytes, apply modifications to
    map regions identified by the analysis, return the result."""
    result = bytearray(original_content)
    mod_hashes = []
    for mod in modifications:
        if isinstance(mod, str):
            mod_hashes.append(hash(mod) & 0xFFFF)
        elif isinstance(mod, dict):
            offset = mod.get("offset", 0)
            values = mod.get("values", [])
            for i, val in enumerate(values):
                pos = offset + i
                if 0 <= pos < len(result):
                    result[pos] = val & 0xFF
        else:
            mod_hashes.append(hash(str(mod)) & 0xFFFF)

    if mod_hashes:
        import struct
        maps = analysis.get("map_regions", [])
        for map_info in maps:
            if isinstance(map_info, dict) and map_info.get("status") == "active":
                off = int(map_info.get("offset", "0x0"), 16) if isinstance(map_info.get("offset"), str) else map_info.get("offset", 0)
                sz = int(map_info.get("size", "0x0"), 16) if isinstance(map_info.get("size"), str) else map_info.get("size", 0)
                for idx, mh in enumerate(mod_hashes):
                    for i in range(0, min(sz, 32), 2):
                        pos = off + i
                        if pos + 1 < len(result):
                            old_val = struct.unpack_from("<H", result, pos)[0]
                            delta = (mh + i) % 20 - 10
                            new_val = max(0, min(65535, old_val + delta))
                            struct.pack_into("<H", result, pos, new_val)
    return bytes(result)
