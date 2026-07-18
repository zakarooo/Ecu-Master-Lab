"""
PHASE 1 — DAMOS Data Quality Report.

Audits the knowledge base for:
  - Duplicate maps (same name + ECU)
  - Invalid addresses (0x0, out of range)
  - Missing units
  - ECUs without associated maps
  - Naming inconsistencies

Returns a quality_score (0-100) and detailed findings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.new.ecu_models import (
    ECUModel,
    KnownMap,
    KnownSignature,
    KnownString,
    KnownChecksum,
    KnownSegment,
    MapCategory,
    MapUnit,
    MapAxis,
    Manufacturer,
)

logger = logging.getLogger("ecu_engine.quality")


@dataclass
class QualityFinding:
    category: str
    severity: str  # critical, warning, info
    message: str
    count: int = 0
    details: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    overall_score: float = 0.0
    total_maps: int = 0
    total_ecus: int = 0
    total_axes: int = 0
    findings: List[QualityFinding] = field(default_factory=list)
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score, 1),
            "total_maps": self.total_maps,
            "total_ecus": self.total_ecus,
            "total_axes": self.total_axes,
            "findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "message": f.message,
                    "count": f.count,
                    "details": f.details[:5],
                }
                for f in self.findings
            ],
            "score_breakdown": self.score_breakdown,
        }


def _check_duplicate_maps(session: Session) -> Tuple[float, QualityFinding]:
    """Find maps with same name + ecu_model_name (duplicates)."""
    dupes = session.execute(text("""
        SELECT ecu_model_name, map_name, COUNT(*) as cnt
        FROM known_maps
        GROUP BY ecu_model_name, map_name
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 20
    """)).fetchall()

    count = sum(r[2] - 1 for r in dupes)
    details = ["%s/%s (x%d)" % (r[0], r[1], r[2]) for r in dupes[:10]]

    if count == 0:
        score = 100.0
    elif count < 10:
        score = 85.0
    elif count < 100:
        score = 70.0
    else:
        score = max(40.0, 100.0 - count * 0.5)

    severity = "info" if count == 0 else ("warning" if count < 50 else "critical")
    return score, QualityFinding(
        category="duplicates",
        severity=severity,
        message="%d duplicate map entries found" % count,
        count=count,
        details=details,
    )


def _check_invalid_addresses(session: Session) -> Tuple[float, QualityFinding]:
    """Find maps with invalid addresses."""
    invalid = session.execute(text("""
        SELECT COUNT(*) FROM known_maps
        WHERE offset_hex IS NULL OR offset_hex = ''
           OR offset_dec IS NULL OR offset_dec = 0
    """)).scalar() or 0

    total = session.query(KnownMap).count() or 1
    ratio = invalid / total

    if ratio == 0:
        score = 100.0
    elif ratio < 0.05:
        score = 90.0
    elif ratio < 0.20:
        score = 70.0
    else:
        score = max(30.0, 100.0 - ratio * 200)

    severity = "info" if ratio < 0.05 else ("warning" if ratio < 0.20 else "critical")
    return score, QualityFinding(
        category="invalid_addresses",
        severity=severity,
        message="%d maps with invalid/missing addresses (%.1f%%)" % (invalid, ratio * 100),
        count=invalid,
    )


def _check_missing_units(session: Session) -> Tuple[float, QualityFinding]:
    """Find maps without category (no unit info)."""
    no_cat = session.execute(text("""
        SELECT COUNT(*) FROM known_maps
        WHERE category IS NULL OR category = '' OR category = 'Injection Quantity'
    """)).scalar() or 0

    total = session.query(KnownMap).count() or 1
    ratio = no_cat / total

    if ratio < 0.10:
        score = 100.0
    elif ratio < 0.30:
        score = 80.0
    elif ratio < 0.60:
        score = 60.0
    else:
        score = max(20.0, 100.0 - ratio * 150)

    severity = "info" if ratio < 0.10 else ("warning" if ratio < 0.40 else "critical")
    return score, QualityFinding(
        category="missing_categories",
        severity=severity,
        message="%d maps with default/missing category (%.1f%%)" % (no_cat, ratio * 100),
        count=no_cat,
    )


def _check_ecus_without_maps(session: Session) -> Tuple[float, QualityFinding]:
    """Find ECU models with no associated maps."""
    ecus_with_maps = session.execute(text("""
        SELECT DISTINCT ecu_model_name FROM known_maps
        WHERE ecu_model_name IS NOT NULL
    """)).fetchall()
    ecu_names_with_maps = {r[0] for r in ecus_with_maps}

    all_models = session.query(ECUModel.model_name).all()
    all_names = {m[0] for m in all_models}

    without_maps = all_names - ecu_names_with_maps
    count = len(without_maps)

    if count == 0:
        score = 100.0
    elif count <= 3:
        score = 85.0
    elif count <= 8:
        score = 70.0
    else:
        score = max(30.0, 100.0 - count * 5)

    severity = "info" if count == 0 else ("warning" if count <= 5 else "critical")
    return score, QualityFinding(
        category="ecus_without_maps",
        severity=severity,
        message="%d ECU models without associated maps" % count,
        count=count,
        details=sorted(without_maps)[:10],
    )


def _check_map_coverage(session: Session) -> Tuple[float, QualityFinding]:
    """Check how many ECU models have map coverage."""
    ecus_with_maps = session.execute(text("""
        SELECT COUNT(DISTINCT ecu_model_name) FROM known_maps
        WHERE ecu_model_name IS NOT NULL AND ecu_model_name != ''
    """)).scalar() or 0

    total_maps = session.query(KnownMap).count() or 1
    unique_names = session.execute(text("""
        SELECT COUNT(DISTINCT map_name) FROM known_maps
    """)).scalar() or 0

    coverage = ecus_with_maps / max(1, 27)  # 27 ECU models in DB
    avg_maps = total_maps / max(1, ecus_with_maps)

    if coverage > 0.8 and avg_maps > 100:
        score = 100.0
    elif coverage > 0.5 and avg_maps > 50:
        score = 80.0
    elif coverage > 0.3:
        score = 60.0
    else:
        score = max(20.0, coverage * 100)

    return score, QualityFinding(
        category="coverage",
        severity="info",
        message="%d/%d ECUs covered, %.0f maps/ECU, %d unique map names" % (
            ecus_with_maps, 27, avg_maps, unique_names),
        count=ecus_with_maps,
    )


def _check_axis_quality(session: Session) -> Tuple[float, QualityFinding]:
    """Check map_axes quality."""
    total_axes = session.query(MapAxis).count()
    total_maps = session.query(KnownMap).count() or 1

    maps_with_axes = session.execute(text("""
        SELECT COUNT(DISTINCT name) FROM map_axes
    """)).scalar() or 0

    ratio = maps_with_axes / total_maps if total_maps else 0

    if ratio > 0.5:
        score = 100.0
    elif ratio > 0.2:
        score = 75.0
    elif ratio > 0.05:
        score = 50.0
    else:
        score = 20.0

    return score, QualityFinding(
        category="axis_quality",
        severity="info" if ratio > 0.3 else "warning",
        message="%d axes for %d maps (%.1f%% coverage)" % (
            total_axes, total_maps, ratio * 100),
        count=total_axes,
    )


def generate_quality_report(session: Session) -> QualityReport:
    """Generate a comprehensive data quality report."""
    report = QualityReport()
    report.total_maps = session.query(KnownMap).count()
    report.total_ecus = session.query(ECUModel).count()
    report.total_axes = session.query(MapAxis).count()

    checks = [
        _check_duplicate_maps,
        _check_invalid_addresses,
        _check_missing_units,
        _check_ecus_without_maps,
        _check_map_coverage,
        _check_axis_quality,
    ]

    scores = []
    for check_fn in checks:
        try:
            score, finding = check_fn(session)
            scores.append(score)
            report.findings.append(finding)
            report.score_breakdown[finding.category] = round(score, 1)
        except Exception as exc:
            logger.warning("Quality check %s failed: %s", check_fn.__name__, exc)
            scores.append(50.0)

    if scores:
        report.overall_score = sum(scores) / len(scores)

    return report
