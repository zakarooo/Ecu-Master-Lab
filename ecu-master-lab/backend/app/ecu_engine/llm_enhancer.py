"""
LLM Enhancement Layer for ECU Analysis Reports.

Uses Mistral API (OpenAI-compatible) to generate enriched,
human-readable analysis summaries from engine results.
"""

import httpx
import logging
import json
from typing import Optional
from .config import settings

logger = logging.getLogger(__name__)

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def _build_prompt(report, analysis_id: str) -> str:
    """Build the prompt from ECUReport dataclass fields."""
    parts = []
    parts.append(f"ECU Analysis ID: {analysis_id}")
    parts.append(f"File: {report.file_name} ({report.file_size:,} bytes)")
    parts.append(f"File Type: {report.file_type}")
    parts.append(f"File Entropy: {report.file_entropy:.2f}")

    if report.brand_guess:
        parts.append(f"Detected Brand: {report.brand_guess}")
    if report.file_type_detailed:
        parts.append(f"File Type Detail: {report.file_type_detailed}")
    if report.confidence:
        parts.append(f"Confidence: {report.confidence:.0%}")

    if report.processor_info:
        pi = report.processor_info
        parts.append(f"Processor: {pi.get('processor', 'unknown')} (family: {pi.get('family', 'unknown')}, arch: {pi.get('architecture', 'unknown')})")

    if report.checksum_info:
        ci = report.checksum_info
        parts.append(f"Checksum: {ci.get('algorithm', 'unknown')}, valid={ci.get('is_valid', False)}, confidence={ci.get('confidence', 0):.0%}")

    if report.maps_summary:
        ms = report.maps_summary
        parts.append(f"Maps: {ms.get('maps_count', 0)} maps, total size {ms.get('total_size', 0)} bytes, confidence {ms.get('overall_confidence', 0):.0%}")
        if ms.get('map_details'):
            for md in ms['map_details'][:8]:
                parts.append(f"  - {md.get('name','?')} @ 0x{md.get('offset',0):08X} ({md.get('type','?')}, rows={md.get('rows','?')}, cols={md.get('cols','?')})")

    if report.db_match_info:
        dmi = report.db_match_info
        parts.append(f"DB Match: {dmi.get('ecu_model', 'N/A')}, score {dmi.get('match_score', 0):.0f}/100")
        if dmi.get('confidence_factors'):
            for cf in dmi['confidence_factors'][:5]:
                parts.append(f"  - {cf}")

    if report.referentiel_info:
        ri = report.referentiel_info
        parts.append(f"Referentiel match: score={ri.get('score', 0):.0f}, matched={ri.get('matched', False)}")
        if ri.get('matched_fields'):
            parts.append(f"  Matched fields: {', '.join(ri['matched_fields'][:8])}")
        if ri.get('missing_fields'):
            parts.append(f"  Missing fields: {', '.join(ri['missing_fields'][:8])}")

    if report.segments:
        parts.append(f"Segments: {len(report.segments)} detected")
        for seg in report.segments[:6]:
            parts.append(f"  - {seg.get('type','?')} @ 0x{seg.get('offset',0):08X} size={seg.get('size',0)}")

    if report.anomalies:
        parts.append(f"Anomalies: {len(report.anomalies)}")
        for a in report.anomalies[:5]:
            parts.append(f"  - {a.get('type','?')}: {a.get('message', a.get('description',''))}")

    if report.knowledge_stats:
        ks = report.knowledge_stats
        parts.append(f"Knowledge base: {ks.get('signature_count',0)} signatures, {ks.get('string_count',0)} strings, {ks.get('segment_count',0)} segments, {ks.get('checksum_count',0)} checksums, {ks.get('map_count',0)} maps")

    return "\n".join(parts)


def enhance_report(report, analysis_id: str) -> Optional[dict]:
    """
    Call Mistral API to generate an enriched analysis report.

    Returns a dict with keys:
      - executive_summary: high-level 1-2 sentence summary
      - technical_analysis: detailed paragraph about what was found
      - recommendations: list of actionable recommendations
      - risk_assessment: "low" / "medium" / "high"
      - next_steps: list of concrete next steps

    Returns None if LLM call fails (analysis still works without it).
    """
    api_key = settings.MISTRAL_API_KEY
    if not api_key:
        logger.info("No MISTRAL_API_KEY configured, skipping LLM enhancement")
        return None

    prompt_body = _build_prompt(report, analysis_id)

    system_msg = (
        "You are an automotive ECU diagnostic expert. "
        "Analyze the following ECU file analysis results and provide:\n"
        "1. A 1-2 sentence executive summary of what the ECU file is.\n"
        "2. A detailed technical analysis paragraph.\n"
        "3. A list of actionable recommendations.\n"
        "4. A risk assessment (low/medium/high) for modification safety.\n"
        "5. A list of concrete next steps for the user.\n\n"
        "Respond in valid JSON with keys: executive_summary, technical_analysis, "
        "recommendations (array), risk_assessment (string), next_steps (array).\n"
        "Keep the total response under 1500 tokens."
    )

    payload = {
        "model": settings.MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt_body},
        ],
        "temperature": 0.3,
        "max_tokens": 1200,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(MISTRAL_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)
        logger.info("LLM enhancement completed for %s", analysis_id)
        return result

    except json.JSONDecodeError as e:
        logger.warning("LLM response was not valid JSON, returning raw text: %s", e)
        return {"executive_summary": content if 'content' in dir() else "LLM analysis available but not parseable.",
                "technical_analysis": "",
                "recommendations": [],
                "risk_assessment": "unknown",
                "next_steps": []}
    except Exception as e:
        logger.warning("LLM enhancement failed: %s", e)
        return None
