"""
Systeme de scoring pondere et explicable.

Chaque evidence recoit un poids configurable. Le score final est la somme
des poids multiplies par la confiance de chaque evidence, normalisee a 100.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ScoreEvidence:
    factor: str
    raw_score: float
    weight: float
    weighted_score: float = 0.0
    explanation: str = ""

    def __post_init__(self):
        self.weighted_score = self.raw_score * self.weight


@dataclass
class ScoringEngine:
    total_weight: float = 0.0
    total_weighted: float = 0.0
    evidence_list: List[ScoreEvidence] = field(default_factory=list)
    explanations: List[str] = field(default_factory=list)

    # Poids par defaut - extensible
    DEFAULT_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "file_size_match": 20.0,
        "binary_pattern": 15.0,
        "manufacturer_ascii": 12.0,
        "hw_version_found": 15.0,
        "sw_version_found": 15.0,
        "processor_match": 10.0,
        "checksum_valid": 8.0,
        "maps_detected": 5.0,
        "consistency": 5.0,
        "brand_match": 3.0,
        "engine_match": 2.0,
    })

    def reset(self):
        self.total_weight = 0.0
        self.total_weighted = 0.0
        self.evidence_list.clear()
        self.explanations.clear()

    def add_evidence(self, factor: str, raw_score: float, explanation: str = ""):
        weight = self.DEFAULT_WEIGHTS.get(factor, 5.0)
        ev = ScoreEvidence(
            factor=factor,
            raw_score=max(0.0, min(100.0, raw_score)),
            weight=weight,
            explanation=explanation,
        )
        self.evidence_list.append(ev)
        self.total_weight += weight
        self.total_weighted += ev.weighted_score
        if explanation:
            self.explanations.append(f"[{factor}] {explanation}")

    def set_custom_weight(self, factor: str, weight: float):
        self.DEFAULT_WEIGHTS[factor] = weight

    def get_final_score(self) -> float:
        if self.total_weight <= 0:
            return 0.0
        raw = self.total_weighted / self.total_weight
        return max(0.0, min(99.9, raw))

    def get_score_breakdown(self) -> List[dict]:
        result = []
        for ev in self.evidence_list:
            result.append({
                "factor": ev.factor,
                "raw_score": round(ev.raw_score, 1),
                "weight": ev.weight,
                "weighted_score": round(ev.weighted_score, 2),
                "explanation": ev.explanation,
            })
        return result

    def get_explanations(self) -> List[str]:
        return list(self.explanations)


def combine_hypothesis_scores(
    size_score: float,
    pattern_score: float,
    manufacturer_score: float,
    hw_score: float,
    sw_score: float,
    processor_score: float,
    checksum_score: float,
    maps_score: float,
    consistency_score: float,
    brand_score: float = 0.0,
    engine_score: float = 0.0,
) -> Tuple[float, List[str]]:
    """
    Calcule un score composite a partir de sous-scores.
    Retourne (score_final, liste_explanations).
    """
    engine = ScoringEngine()

    if size_score > 0:
        engine.add_evidence("file_size_match", size_score, f"Taille compatible ({size_score:.0f}%)")
    if pattern_score > 0:
        engine.add_evidence("binary_pattern", pattern_score, f"Patterns binaires ({pattern_score:.0f}%)")
    if manufacturer_score > 0:
        engine.add_evidence("manufacturer_ascii", manufacturer_score, f"Constructeur ASCII ({manufacturer_score:.0f}%)")
    if hw_score > 0:
        engine.add_evidence("hw_version_found", hw_score, f"HW version ({hw_score:.0f}%)")
    if sw_score > 0:
        engine.add_evidence("sw_version_found", sw_score, f"SW version ({sw_score:.0f}%)")
    if processor_score > 0:
        engine.add_evidence("processor_match", processor_score, f"Processeur ({processor_score:.0f}%)")
    if checksum_score > 0:
        engine.add_evidence("checksum_valid", checksum_score, f"Checksum ({checksum_score:.0f}%)")
    if maps_score > 0:
        engine.add_evidence("maps_detected", maps_score, f"Cartographies ({maps_score:.0f}%)")
    if consistency_score > 0:
        engine.add_evidence("consistency", consistency_score, f"Coherence ({consistency_score:.0f}%)")
    if brand_score > 0:
        engine.add_evidence("brand_match", brand_score, f"Marque ({brand_score:.0f}%)")
    if engine_score > 0:
        engine.add_evidence("engine_match", engine_score, f"Moteur ({engine_score:.0f}%)")

    return engine.get_final_score(), engine.get_explanations()


def confidence_level(score: float) -> str:
    if score >= 90:
        return "very_high"
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "low"
    return "very_low"


def should_need_review(score: float, checksum_valid: Optional[bool], consistency: float) -> Tuple[bool, List[str]]:
    reasons = []
    if score < 30:
        reasons.append(f"Confiance trop faible ({score:.1f}%)")
    if checksum_valid is False:
        reasons.append("Checksum invalide")
    if consistency < 40:
        reasons.append("Cohérence interne insuffisante")
    return len(reasons) > 0, reasons
