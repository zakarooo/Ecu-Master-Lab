"""
Layer 9 : Validation croisee contre la base de signatures ECU connues.

Compare les signaux extraits des couches precedentes avec un catalogue
de profils ECU pour proposer des candidats classes par score decroissant.
"""

import logging
from typing import List, Dict, Optional, Tuple

from .models import (
    ECUCandidate,
    CrossValidationResult,
    ProcessorProfile,
    FormatResult,
    TechnicalInfo,
    SignatureScanResult,
    MemoryLayout,
    MapDetectionResult,
    ChecksumResult,
)
from .scoring import combine_hypothesis_scores

try:
    from sqlalchemy.orm import Session as _Session
except ImportError:
    _Session = None

logger = logging.getLogger(__name__)


# ==============================================================
#  BASE DE SIGNATURES ECU CONNUES
# ==============================================================

ECU_SIGNATURES_DB: List[Dict] = [
    {"ecu_id": "BOSCH_EDC17C64", "manufacturer": "Bosch",
     "ecu_family": "EDC17", "ecu_model": "EDC17C64",
     "known_hw_versions": ["0 281 030 XXX", "0 281 030 963"],
     "known_sw_versions": ["1037343991", "1037556117"],
     "known_brands": ["Volkswagen", "Audi", "Seat", "Skoda"],
     "known_engines": ["1.9 TDI", "2.0 TDI", "1.6 TDI"],
     "file_sizes": [{"size": 524288, "tolerance": 0.1}, {"size": 1048576, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off", "AdBlue delete"],
     "protocol": "CAN"},
    {"ecu_id": "BOSCH_EDC17CP44", "manufacturer": "Bosch",
     "ecu_family": "EDC17", "ecu_model": "EDC17CP44",
     "known_hw_versions": ["0 281 030 536", "0 281 030 537"],
     "known_sw_versions": ["1037343991", "1037456007"],
     "known_brands": ["Volkswagen", "Audi", "BMW"],
     "known_engines": ["2.0 TDI", "3.0 TDI", "2.7 TDI"],
     "file_sizes": [{"size": 524288, "tolerance": 0.1}, {"size": 1048576, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off"],
     "protocol": "CAN"},
    {"ecu_id": "BOSCH_ME17_5", "manufacturer": "Bosch",
     "ecu_family": "ME17", "ecu_model": "ME17.5",
     "known_hw_versions": ["0 281 027 411", "0 281 027 412"],
     "known_sw_versions": ["1037462001"],
     "known_brands": ["Volkswagen", "Audi"],
     "known_engines": ["1.4 TSI", "1.8 TSI", "2.0 TSI"],
     "file_sizes": [{"size": 524288, "tolerance": 0.1}, {"size": 1048576, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "Popcorn map"],
     "protocol": "CAN"},
    {"ecu_id": "BOSCH_ME17_5_2", "manufacturer": "Bosch",
     "ecu_family": "ME17", "ecu_model": "ME17.5.2",
     "known_hw_versions": ["0 281 033 311", "0 281 033 312"],
     "known_sw_versions": ["1037565010", "1037565020"],
     "known_brands": ["Volkswagen", "Audi", "Porsche"],
     "known_engines": ["1.8 TSI", "2.0 TSI", "2.0 TFSI"],
     "file_sizes": [{"size": 1048576, "tolerance": 0.1}, {"size": 2097152, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "Popcorn map", "Flex fuel"],
     "protocol": "CAN"},
    {"ecu_id": "BOSCH_MD1CS004", "manufacturer": "Bosch",
     "ecu_family": "MD1", "ecu_model": "MD1CS004",
     "known_hw_versions": ["0 281 035 377", "0 281 035 378"],
     "known_sw_versions": ["1039316010"],
     "known_brands": ["Volkswagen", "Audi", "Skoda"],
     "known_engines": ["2.0 TDI EA288", "1.6 TDI"],
     "file_sizes": [{"size": 2097152, "tolerance": 0.1}, {"size": 4194304, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off", "AdBlue delete"],
     "protocol": "CAN"},
    {"ecu_id": "DELPHI_DCM3_7", "manufacturer": "Delphi",
     "ecu_family": "DCM3", "ecu_model": "DCM3.7",
     "known_hw_versions": ["DDC17C003", "DDC17C004"],
     "known_sw_versions": ["1037623001"],
     "known_brands": ["Renault", "Nissan", "Dacia"],
     "known_engines": ["1.5 dCi", "1.6 dCi", "2.0 dCi"],
     "file_sizes": [{"size": 524288, "tolerance": 0.1}, {"size": 1048576, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off"],
     "protocol": "CAN"},
    {"ecu_id": "CONTINENTAL_SID208", "manufacturer": "Continental",
     "ecu_family": "SID2xx", "ecu_model": "SID208",
     "known_hw_versions": ["A2C813916001", "A2C813916002"],
     "known_sw_versions": ["1039156001"],
     "known_brands": ["Ford", "Peugeot", "Citroen", "Mazda"],
     "known_engines": ["1.5 TDCi", "1.6 TDCi", "2.0 TDCi"],
     "file_sizes": [{"size": 2097152, "tolerance": 0.1}, {"size": 4194304, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off"],
     "protocol": "CAN"},
    {"ecu_id": "CONTINENTAL_SID807EVO", "manufacturer": "Continental",
     "ecu_family": "SID807", "ecu_model": "SID807 EVO",
     "known_hw_versions": ["A2C813978001", "A2C813978002"],
     "known_sw_versions": ["1039234001"],
     "known_brands": ["Peugeot", "Citroen", "DS"],
     "known_engines": ["1.5 BlueHDi", "1.6 BlueHDi", "2.0 BlueHDi"],
     "file_sizes": [{"size": 2097152, "tolerance": 0.1}, {"size": 4194304, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off", "AdBlue off"],
     "protocol": "CAN"},
    {"ecu_id": "SIEMENS_SIMOS18_1", "manufacturer": "Siemens",
     "ecu_family": "Simos", "ecu_model": "Simos 18.1",
     "known_hw_versions": ["5WP4 373 193-001", "5WP4 373 193-002"],
     "known_sw_versions": ["1037385201"],
     "known_brands": ["Volkswagen", "Audi", "Seat", "Skoda"],
     "known_engines": ["1.4 TSI", "1.8 TSI", "2.0 TSI"],
     "file_sizes": [{"size": 2097152, "tolerance": 0.1}, {"size": 4194304, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "Popcorn map", "Flex fuel"],
     "protocol": "CAN"},
    {"ecu_id": "SIEMENS_SIMOS18_2", "manufacturer": "Siemens",
     "ecu_family": "Simos", "ecu_model": "Simos 18.2",
     "known_hw_versions": ["5WP4 447 193-001", "5WP4 447 193-002"],
     "known_sw_versions": ["1039456001"],
     "known_brands": ["Volkswagen", "Audi", "Porsche"],
     "known_engines": ["2.0 TSI", "2.5 TFSI", "3.0 TFSI"],
     "file_sizes": [{"size": 4194304, "tolerance": 0.1}, {"size": 8388608, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "Popcorn map", "Flex fuel", "E85"],
     "protocol": "CAN"},
    {"ecu_id": "DENSO_275000", "manufacturer": "Denso",
     "ecu_family": "275xxx", "ecu_model": "275000",
     "known_hw_versions": ["89670-0C020", "89670-0C030"],
     "known_sw_versions": ["89670-0C020-000"],
     "known_brands": ["Toyota", "Lexus"],
     "known_engines": ["1.4 D-4D", "2.0 D-4D", "2.8 D-4D"],
     "file_sizes": [{"size": 524288, "tolerance": 0.1}, {"size": 1048576, "tolerance": 0.1}],
     "processor_family": "RH850",
     "modifications": ["Stage 1"],
     "protocol": "CAN"},
    {"ecu_id": "DENSO_275100", "manufacturer": "Denso",
     "ecu_family": "275xxx", "ecu_model": "275100",
     "known_hw_versions": ["89670-0C530", "89670-0C540"],
     "known_sw_versions": ["89670-0C530-000"],
     "known_brands": ["Toyota", "Lexus", "Hino"],
     "known_engines": ["2.5 D-4D", "3.0 D-4D"],
     "file_sizes": [{"size": 1048576, "tolerance": 0.1}, {"size": 2097152, "tolerance": 0.1}],
     "processor_family": "RH850",
     "modifications": ["Stage 1"],
     "protocol": "CAN"},
    {"ecu_id": "DENSO_275200", "manufacturer": "Denso",
     "ecu_family": "275xxx", "ecu_model": "275200",
     "known_hw_versions": ["89670-0E040", "89670-0E050"],
     "known_sw_versions": ["89670-0E040-000"],
     "known_brands": ["Toyota", "Lexus"],
     "known_engines": ["2.8 D-4D", "1.8 D-4D"],
     "file_sizes": [{"size": 1048576, "tolerance": 0.1}, {"size": 2097152, "tolerance": 0.1}],
     "processor_family": "RH850",
     "modifications": ["Stage 1"],
     "protocol": "CAN"},
    {"ecu_id": "MAGNETI_MARELLI_9GF", "manufacturer": "Magneti Marelli",
     "ecu_family": "9GF", "ecu_model": "9GF",
     "known_hw_versions": ["MF406000", "MF406100"],
     "known_sw_versions": ["1039500001"],
     "known_brands": ["Fiat", "Alfa Romeo", "Lancia"],
     "known_engines": ["1.3 JTD", "1.6 JTD", "2.0 JTD", "3.0 V6 JTD"],
     "file_sizes": [{"size": 1048576, "tolerance": 0.1}, {"size": 2097152, "tolerance": 0.1}],
     "processor_family": "Tricore",
     "modifications": ["Stage 1", "EGR off", "DPF off"],
     "protocol": "CAN"},
]


# ==============================================================
#  FONCTIONS DE SCORING PAR DIMENSION
# ==============================================================

def _score_file_size(data_size: int, known_sizes: List[Dict]) -> float:
    if not known_sizes or data_size <= 0:
        return 0.0
    for entry in known_sizes:
        target = entry["size"]
        tol = entry.get("tolerance", 0.1)
        if target * (1.0 - tol) <= data_size <= target * (1.0 + tol):
            return 100.0
    best = 0.0
    for entry in known_sizes:
        target = entry["size"]
        if target <= 0:
            continue
        ratio = data_size / target
        if 0.5 <= ratio <= 2.0:
            closeness = 1.0 - min(abs(ratio - 1.0), 1.0)
            best = max(best, closeness * 50.0)
    return best


def _score_binary_pattern(
    tech_info: Optional[TechnicalInfo], ecu: Dict
) -> float:
    if not tech_info:
        return 0.0
    parts = list(tech_info.raw_strings.values())
    parts.extend(tech_info.evidence)
    parts.append(tech_info.hw_number)
    parts.append(tech_info.sw_number)
    text = " ".join(p for p in parts if p).lower()
    if not text.strip():
        return 0.0
    score = 0.0
    model = ecu.get("ecu_model", "").lower()
    family = ecu.get("ecu_family", "").lower()
    if model and model in text:
        score += 60.0
    if family and family in text:
        score += 40.0
    return min(100.0, score)


def _score_manufacturer(
    tech_info: Optional[TechnicalInfo], ecu: Dict
) -> float:
    if not tech_info:
        return 0.0
    parts = list(tech_info.raw_strings.values())
    parts.extend(tech_info.evidence)
    text = " ".join(p for p in parts if p).lower()
    mfr = ecu.get("manufacturer", "").lower()
    if mfr and mfr in text:
        return 100.0
    return 0.0


def _score_version_match(detected: str, known_versions: List[str]) -> float:
    if not detected or not known_versions:
        return 0.0
    val = detected.lower().strip()
    for version in known_versions:
        v = version.lower().strip()
        if v in val or val in v:
            return 100.0
    digits = "".join(c for c in val if c.isdigit())
    for version in known_versions:
        v_digits = "".join(c for c in version if c.isdigit())
        if digits and v_digits and digits == v_digits:
            return 90.0
    return 0.0


def _score_processor(proc_result, expected_family: str) -> float:
    if not proc_result or not proc_result.detected or not proc_result.primary:
        return 0.0
    detected = proc_result.primary.family.value.lower()
    expected = expected_family.lower()
    if detected == expected:
        return 100.0
    if "tricore" in detected and "tricore" in expected:
        return 90.0
    if detected == "unknown":
        return 10.0
    return 0.0


def _score_checksum(checksum_result: Optional[ChecksumResult]) -> float:
    if not checksum_result:
        return 0.0
    if checksum_result.is_valid is True:
        return 80.0
    if checksum_result.is_valid is False:
        return 10.0
    if checksum_result.algorithm:
        return 40.0
    return 20.0


def _score_maps(map_result: Optional[MapDetectionResult]) -> float:
    if not map_result:
        return 0.0
    count = map_result.total_maps_found
    if count >= 20:
        return 100.0
    if count >= 10:
        return 80.0
    if count >= 5:
        return 60.0
    if count >= 1:
        return 40.0
    return 0.0


def _score_brand(
    tech_info: Optional[TechnicalInfo], known_brands: List[str]
) -> float:
    if not tech_info or not known_brands:
        return 0.0
    parts = list(tech_info.raw_strings.values())
    parts.extend(tech_info.evidence)
    parts.append(tech_info.vin)
    text = " ".join(p for p in parts if p).lower()
    if not text.strip():
        return 0.0
    for brand in known_brands:
        if brand.lower() in text:
            return 100.0
    return 0.0


def _score_engine(
    tech_info: Optional[TechnicalInfo], known_engines: List[str]
) -> float:
    if not tech_info or not tech_info.engine_type or not known_engines:
        return 0.0
    engine = tech_info.engine_type.lower().strip()
    if not engine:
        return 0.0
    for known in known_engines:
        k = known.lower().strip()
        if k in engine or engine in k:
            return 100.0
    engine_digits = "".join(c for c in engine if c.isdigit())
    for known in known_engines:
        k_digits = "".join(c for c in known.lower() if c.isdigit())
        if engine_digits and k_digits and engine_digits == k_digits:
            return 70.0
    return 0.0


# ==============================================================
#  VALIDATION CROISEE PRINCIPALE
# ==============================================================

def cross_validate(
    data: bytes,
    format_result: FormatResult,
    processor_result,
    tech_info: TechnicalInfo,
    signature_result: SignatureScanResult,
    memory_layout: MemoryLayout,
    map_result: MapDetectionResult,
    checksum_result: ChecksumResult,
    db=None,
) -> CrossValidationResult:
    """Valide les candidats ECU contre la base de signatures connues.

    Si ``db`` est fourni, le matching base de connaissances (DB) est
    exécuté en premier et ses résultats sont fusionnés avec les
    profils hardcodés — priorité au DB quand le score est suffisant.
    """
    logger.info("Layer 9: Debut validation croisee (%d octets)", len(data))

    data_size = len(data)
    candidates = []

    # --- Phase 3 : DB Knowledge matching (prioritaire) ---
    db_candidates = []
    if db is not None:
        try:
            from .db_matcher import match_from_db
            db_raw = match_from_db(db, data, file_size=data_size)
            for dc in db_raw:
                if dc["score"] < 10.0:
                    continue
                cand = ECUCandidate(
                    ecu_id="DB_%s" % dc["ecu_model_name"].replace(" ", "_"),
                    manufacturer=dc.get("manufacturer_name", ""),
                    ecu_family="DB",
                    ecu_model=dc["ecu_model_name"],
                    confidence=dc["score"],
                    evidence=dc.get("evidence", []),
                    match_scores=dc.get("match_details", {}),
                )
                db_candidates.append(cand)
            logger.info("Layer 9: DB matcher a retourne %d candidats", len(db_candidates))
        except Exception as exc:
            logger.warning("Layer 9: DB matcher failed: %s", exc)
            try:
                db.rollback()
            except Exception:
                pass

    for ecu in ECU_SIGNATURES_DB:
        size_score = _score_file_size(data_size, ecu["file_sizes"])
        pattern_score = _score_binary_pattern(tech_info, ecu)
        mfr_score = _score_manufacturer(tech_info, ecu)
        hw_score = _score_version_match(
            tech_info.hw_number if tech_info else "",
            ecu["known_hw_versions"],
        )
        sw_score = _score_version_match(
            tech_info.sw_number if tech_info else "",
            ecu["known_sw_versions"],
        )
        proc_score = _score_processor(processor_result, ecu["processor_family"])
        chk_score = _score_checksum(checksum_result)
        maps_score = _score_maps(map_result)
        brand_score = _score_brand(tech_info, ecu["known_brands"])
        engine_score = _score_engine(tech_info, ecu["known_engines"])

        nonzero = sum(1 for s in [
            size_score, pattern_score, mfr_score, hw_score, sw_score,
            proc_score, chk_score, maps_score, brand_score, engine_score,
        ] if s > 0)
        consistency = min(100.0, (nonzero / 10.0) * 120.0)

        score, explanations = combine_hypothesis_scores(
            size_score=size_score,
            pattern_score=pattern_score,
            manufacturer_score=mfr_score,
            hw_score=hw_score,
            sw_score=sw_score,
            processor_score=proc_score,
            checksum_score=chk_score,
            maps_score=maps_score,
            consistency_score=consistency,
            brand_score=brand_score,
            engine_score=engine_score,
        )

        evidence = [
            msg for ok, msg in [
                (size_score > 0, "Taille fichier compatible"),
                (pattern_score > 0, "Pattern binaire detecte"),
                (mfr_score > 0, "Constructeur identifie"),
                (hw_score > 0, "HW version: %s" % tech_info.hw_number),
                (sw_score > 0, "SW version: %s" % tech_info.sw_number),
                (proc_score > 0, "Processeur compatible"),
                (brand_score > 0, "Marque vehicule detectee"),
                (engine_score > 0, "Moteur compatible"),
            ] if ok
        ]
        evidence.extend(explanations)

        match_scores = {
            "file_size": size_score, "binary_pattern": pattern_score,
            "manufacturer": mfr_score, "hw_version": hw_score,
            "sw_version": sw_score, "processor": proc_score,
            "checksum": chk_score, "maps": maps_score,
            "brand": brand_score, "engine": engine_score,
            "consistency": consistency,
        }

        candidate = ECUCandidate(
            ecu_id=ecu["ecu_id"],
            manufacturer=ecu["manufacturer"],
            ecu_family=ecu["ecu_family"],
            ecu_model=ecu["ecu_model"],
            confidence=score,
            evidence=evidence,
            match_scores=match_scores,
        )

        if score < 20.0:
            candidate.rejected = True
            reasons = []
            if size_score == 0:
                reasons.append("Taille incompatible")
            if pattern_score == 0 and hw_score == 0:
                reasons.append("Aucun identifiant ECU detecte")
            if proc_score == 0:
                reasons.append("Processeur incompatible")
            if not reasons:
                reasons.append("Score trop faible")
            candidate.rejection_reasons = reasons

        candidates.append(candidate)

    candidates.sort(key=lambda c: c.confidence, reverse=True)

    # --- Merge DB candidates with hardcoded candidates ---
    # DB candidates get a 15% boost when they also match a hardcoded profile
    for db_cand in db_candidates:
        matched = False
        for hc in candidates:
            if (db_cand.ecu_model.lower() in hc.ecu_model.lower()
                    or hc.ecu_model.lower() in db_cand.ecu_model.lower()):
                # Boost existing hardcoded candidate with DB evidence
                hc.confidence = min(hc.confidence + 15.0, 99.9)
                hc.evidence.extend(db_cand.evidence)
                hc.match_scores["db_match"] = db_cand.confidence
                matched = True
                break
        if not matched and db_cand.confidence >= 25.0:
            # Add DB-only candidate (not in hardcoded profiles)
            candidates.append(db_cand)

    candidates.sort(key=lambda c: c.confidence, reverse=True)

    best = None
    if candidates and candidates[0].confidence > 30.0:
        best = candidates[0]

    consensus = False
    if len(candidates) >= 2:
        diff = candidates[0].confidence - candidates[1].confidence
        consensus = diff > 20.0

    explanation = "Aucun candidat significatif detecte"
    if best:
        explanation = (
            "Meilleur candidat: %s %s (%.1f%%) - %d candidats analyses"
            % (best.manufacturer, best.ecu_model, best.confidence,
               len(candidates))
        )
    if consensus:
        explanation += " [Consensus atteint]"

    logger.info(
        "Layer 9: Terminee - %d candidats, best=%s (%.1f%%)",
        len(candidates),
        best.ecu_id if best else "aucun",
        best.confidence if best else 0.0,
    )

    return CrossValidationResult(
        hypotheses=candidates,
        best_hypothesis=best,
        consensus_reached=consensus,
        explanation=explanation,
    )
