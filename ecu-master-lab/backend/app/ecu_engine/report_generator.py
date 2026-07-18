"""
Couche 10 : Generation du rapport ECU final.

Assemble les resultats de toutes les couches du pipeline en un
ECUReport complet avec scores de confiance, risques et recommandations.
"""

import logging
from typing import Dict, List

from .models import (
    ECUReport, PipelineStep, ReportRisk, ReviewReason,
    FormatResult, ProcessorResult, MemoryLayout, TechnicalInfo,
    SignatureScanResult, SegmentAnalysisResult, MapDetectionResult,
    ChecksumResult, CrossValidationResult, ConfidenceLevel,
)
from .cross_validator import ECU_SIGNATURES_DB

logger = logging.getLogger("ecu_engine.report")

_LEVEL_THRESHOLDS = [
    (85.0, ConfidenceLevel.VERY_HIGH),
    (65.0, ConfidenceLevel.HIGH),
    (45.0, ConfidenceLevel.MEDIUM),
    (25.0, ConfidenceLevel.LOW),
    (0.0, ConfidenceLevel.VERY_LOW),
]


def _confidence_level(score: float) -> ConfidenceLevel:
    for threshold, level in _LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return ConfidenceLevel.VERY_LOW


def _to100(value: float, scale_max: float) -> float:
    if scale_max <= 0:
        return 0.0
    return min(100.0, max(0.0, (value / scale_max) * 100.0))


def _checksum_score(results: List[ChecksumResult]) -> float:
    if not results:
        return 0.0
    ok = sum(1 for c in results if c.is_valid is True)
    bad = sum(1 for c in results if c.is_valid is False)
    algo = any(c.algorithm for c in results)
    if ok > 0 and bad == 0:
        return 90.0
    if ok > 0:
        return 50.0
    if bad > 0:
        return 15.0
    return 40.0 if algo else 20.0


def _compute_confidence(
    cv: CrossValidationResult, proc: ProcessorResult,
    sig: SignatureScanResult, mp: MapDetectionResult,
    chks: List[ChecksumResult], seg: SegmentAnalysisResult,
) -> float:
    cv_s = cv.best_hypothesis.confidence if cv.best_hypothesis else 0.0
    proc_s = _to100(proc.confidence, 1.0)
    sig_s = _to100(sig.confidence, 99.9)
    map_s = _to100(mp.confidence, 1.0)
    chk_s = _checksum_score(chks)
    coh_s = seg.coherence_score
    raw = (cv_s * 0.40 + proc_s * 0.15 + sig_s * 0.10
           + map_s * 0.15 + chk_s * 0.10 + coh_s * 0.10)
    return round(min(100.0, max(0.0, raw)), 2)


def _build_risks(
    chks: List[ChecksumResult], conf: float,
    coh: float, sig: SignatureScanResult, fmt: FormatResult,
) -> List[ReportRisk]:
    r: List[ReportRisk] = []
    for c in chks:
        if c.is_valid is False:
            r.append(ReportRisk(
                category="Checksum", severity="high",
                message="Checksum invalide: %s" % c.algorithm,
                evidence="Stocke: %s, Calcule: %s" % (
                    c.stored_value, c.computed_value)))
    if conf < 30.0:
        r.append(ReportRisk(
            category="Confiance", severity="high",
            message="Confiance tres faible: %.1f%%" % conf,
            evidence="Niveau: %s" % _confidence_level(conf).value))
    elif conf < 50.0:
        r.append(ReportRisk(
            category="Confiance", severity="medium",
            message="Confiance moderee: %.1f%%" % conf,
            evidence="Niveau: %s" % _confidence_level(conf).value))
    if coh < 40.0:
        r.append(ReportRisk(
            category="Segment", severity="medium",
            message="Coherence structurelle faible: %.1f%%" % coh,
            evidence="Segments memoire incoherents"))
    if sig.rsa_detected:
        r.append(ReportRisk(
            category="Securite", severity="high",
            message="Chiffrement / RSA detecte",
            evidence="RSA/crypto markers dans les signatures"))
    if fmt.format_type.value == "unknown":
        r.append(ReportRisk(
            category="Format", severity="medium",
            message="Format fichier non reconnu",
            evidence=fmt.explanation))
    return r


def _build_reviews(
    conf: float, chks: List[ChecksumResult],
    coh: float, sig: SignatureScanResult,
) -> List[ReviewReason]:
    revs: List[ReviewReason] = []
    if conf < 30.0:
        revs.append(ReviewReason(
            reason="Confiance trop faible pour traitement auto",
            severity="high",
            evidence="Score: %.1f%%, niveau: %s" % (
                conf, _confidence_level(conf).value)))
    bad = [c for c in chks if c.is_valid is False]
    if bad:
        algos = ", ".join(c.algorithm for c in bad if c.algorithm)
        revs.append(ReviewReason(
            reason="Checksum(s) invalide(s)",
            severity="high",
            evidence="Algorithmes: %s" % algos))
    if coh < 40.0:
        revs.append(ReviewReason(
            reason="Coherence structurelle insuffisante",
            severity="medium",
            evidence="Score: %.1f%%" % coh))
    if sig.rsa_detected:
        revs.append(ReviewReason(
            reason="Chiffrement necessitant analyse manuelle",
            severity="high",
            evidence="RSA/crypto present"))
    return revs


def _build_recommendations(
    risks: List[ReportRisk], conf: float,
    chks: List[ChecksumResult], cv: CrossValidationResult,
    sig: SignatureScanResult,
) -> List[str]:
    recs: List[str] = []
    if conf >= 70.0:
        recs.append("Confiance elevee — identification fiable.")
    elif conf >= 45.0:
        recs.append("Confiance moderee — valider avec infos complementaires.")
    else:
        recs.append("Confiance faible — analyse manuelle recommandee.")
    if any(c.is_valid is False for c in chks):
        recs.append("Recalculer les checksums avant modification.")
    if any(c.is_valid is True for c in chks):
        recs.append("Checksums valides — sauvegarder valeurs originales.")
    if cv.consensus_reached:
        recs.append("Consensus atteint — identification renforcee.")
    elif cv.best_hypothesis:
        recs.append("Aucun consensus — considerer hypotheses secondaires.")
    if sig.rsa_detected:
        recs.append("RSA/crypto detecte — precautions speciales requises.")
    if sig.diagnostics_present:
        recs.append("Diagnostics UDS presents — lecture DIDs possible.")
    if any(r.category == "Securite" for r in risks):
        recs.append("Risques securite — pas d'ecriture sans verification.")
    return recs or ["Aucune recommandation specifique."]


def _hypotheses_to_dicts(cv: CrossValidationResult) -> List[Dict]:
    if not cv.hypotheses:
        return []
    top = sorted(cv.hypotheses, key=lambda h: h.confidence, reverse=True)[:5]
    return [{
        "ecu_id": h.ecu_id, "manufacturer": h.manufacturer,
        "ecu_family": h.ecu_family, "ecu_model": h.ecu_model,
        "confidence": h.confidence, "evidence": h.evidence,
        "match_scores": h.match_scores,
    } for h in top]


def _lookup_modifications(ecu_id: str) -> List[str]:
    # Normalize ecu_id: strip prefixes like "REF_", "DB_", "BOSCH_"
    normalized = ecu_id.upper().replace(" ", "_")
    for prefix in ("REF_", "DB_"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    # Try exact match first
    for e in ECU_SIGNATURES_DB:
        if e.get("ecu_id", "").upper() == normalized:
            return list(e.get("modifications", []))
    # Fuzzy match: check if any signature ecu_model is contained in the normalized id
    for e in ECU_SIGNATURES_DB:
        model = e.get("ecu_model", "").upper().replace(" ", "")
        if model and model in normalized:
            return list(e.get("modifications", []))
    # Reverse fuzzy: check if normalized id is contained in any signature ecu_model
    for e in ECU_SIGNATURES_DB:
        ecu_model_upper = e.get("ecu_model", "").upper().replace(" ", "")
        if normalized and ecu_model_upper and normalized in ecu_model_upper:
            return list(e.get("modifications", []))
    # Match by ecu_family
    for e in ECU_SIGNATURES_DB:
        family = e.get("ecu_family", "").upper()
        if family and family in normalized:
            return list(e.get("modifications", []))
    return []


def generate_report(
    file_name: str,
    data: bytes,
    format_result: FormatResult,
    processor_result: ProcessorResult,
    memory_layout: MemoryLayout,
    tech_info: TechnicalInfo,
    signature_result: SignatureScanResult,
    segment_result: SegmentAnalysisResult,
    map_result: MapDetectionResult,
    checksum_results: List[ChecksumResult],
    cross_validation: CrossValidationResult,
    pipeline_steps: List[PipelineStep],
    processing_time: float,
) -> ECUReport:
    logger.info("Generating report for %s (%d bytes)", file_name, len(data))
    sz = len(data)
    best = cross_validation.best_hypothesis

    report = ECUReport(
        file_name=file_name, file_size=sz,
        file_hash_sha256=getattr(format_result, "hash_sha256", ""),
        file_hash_md5=getattr(format_result, "hash_md5", ""),
    )

    # Best hypothesis fields
    if best:
        report.detected_ecu = best.ecu_id or "Inconnu"
        report.detected_manufacturer = best.manufacturer or "Inconnu"
        report.detected_ecu_family = best.ecu_family or "Inconnu"
        report.detected_ecu_model = best.ecu_model or "Inconnu"
    if tech_info:
        if tech_info.hw_number:
            report.detected_hw_version = tech_info.hw_number
        if tech_info.sw_number:
            report.detected_sw_version = tech_info.sw_number
        if tech_info.engine_type:
            report.detected_engine = tech_info.engine_type
    if best and best.evidence:
        for ev in best.evidence:
            if "marque" in ev.lower() or "brand" in ev.lower():
                parts = ev.split(":", 1)
                if len(parts) > 1:
                    report.detected_brand = parts[1].strip()
                break
    if best:
        proto = best.match_scores.get("protocol", "")
        if not proto:
            for e in ECU_SIGNATURES_DB:
                if e.get("ecu_id") == best.ecu_id:
                    proto = e.get("protocol", "")
                    break
        report.detected_protocol = proto or "Inconnu"

    # Confidence
    conf = _compute_confidence(
        cross_validation, processor_result, signature_result,
        map_result, checksum_results, segment_result)
    report.confidence = conf
    report.consistency_score = segment_result.coherence_score

    # Risks & reviews
    report.risks = _build_risks(
        checksum_results, conf, segment_result.coherence_score,
        signature_result, format_result)
    report.review_reasons = _build_reviews(
        conf, checksum_results, segment_result.coherence_score,
        signature_result)

    # Flags
    report.needs_review = (
        conf < 30.0
        or any(c.is_valid is False for c in checksum_results)
        or segment_result.coherence_score < 40.0
        or signature_result.rsa_detected)
    report.is_auto_processable = (
        not report.needs_review
        and conf >= 50.0
        and segment_result.coherence_score >= 40.0)

    # Recommendations & hypotheses
    report.recommendations = _build_recommendations(
        report.risks, conf, checksum_results,
        cross_validation, signature_result)
    report.hypotheses = _hypotheses_to_dicts(cross_validation)
    if best:
        report.compatible_modifications = _lookup_modifications(best.ecu_id)

    # Attach layer results
    report.checksum = checksum_results[0] if checksum_results else None
    report.format_result = format_result
    report.processor_result = processor_result
    report.memory_layout = memory_layout
    report.tech_info = tech_info
    report.signatures = signature_result
    report.segments = segment_result
    report.maps = map_result
    report.cross_validation = cross_validation

    # Pipeline metadata
    report.pipeline_steps = pipeline_steps
    report.processing_time_seconds = processing_time
    report.total_pipeline_time_ms = sum(s.duration_ms for s in pipeline_steps)

    logger.info(
        "Report: %s, conf=%.1f%%, risks=%d, review=%s",
        report.detected_ecu, conf, len(report.risks),
        report.needs_review)
    return report
