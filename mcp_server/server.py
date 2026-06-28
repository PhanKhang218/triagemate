"""clinical-kb MCP server: read-only red-flag and ESI-criteria lookups over stdio,
backed by a curated JSON file (no network calls, no patient data).

Run standalone for debugging: python mcp_server/server.py
"""

from __future__ import annotations

import json
import os
import re

from mcp.server.fastmcp import FastMCP

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

with open(KB_PATH, encoding="utf-8") as f:
    KB = json.load(f)

mcp = FastMCP("clinical-kb")


def _match_complaint(complaint: str) -> str:
    """Resolve free-text complaint to a KB key by alias matching; fall back to 'general'."""
    # Normalize: lowercase and drop punctuation so "can't breathe" matches "cant breathe".
    query = re.sub(r"[^a-z0-9\s]+", "", (complaint or "").strip().lower())
    complaints = KB["chief_complaints"]
    if query in complaints:
        return query
    for key, data in complaints.items():
        if key == "general":
            continue
        if key in query or query in key:
            return key
        for alias in data.get("aliases", []):
            if alias in query or query in alias:
                return key
    return "general"


@mcp.tool()
def lookup_red_flags(complaint: str) -> dict:
    """Return emergency danger signs (red flags) for a chief complaint.

    Each red flag includes the clinical concern it points to and a suggested ESI
    level. Use this to check whether a patient's presentation contains any
    emergency indicators that should raise the acuity.

    Args:
        complaint: The patient's chief complaint in plain language (e.g. "chest pain").
    """
    key = _match_complaint(complaint)
    data = KB["chief_complaints"][key]
    return {
        "matched_complaint": key,
        "red_flags": data["red_flags"],
        "disclaimer": KB["_disclaimer"],
    }


@mcp.tool()
def assess_vital_signs(
    heart_rate: int = 0,
    spo2: int = 0,
    systolic_bp: int = 0,
    respiratory_rate: int = 0,
    temperature_c: float = 0.0,
) -> dict:
    """Flag dangerous adult vital signs using fixed clinical thresholds.

    This is a deterministic check (no judgment) that gives the Triage Agent an
    objective acuity floor. Pass 0 for any vital that was not reported.

    Args:
        heart_rate: Beats per minute (0 if not reported).
        spo2: Oxygen saturation percentage (0 if not reported).
        systolic_bp: Systolic blood pressure in mmHg (0 if not reported).
        respiratory_rate: Breaths per minute (0 if not reported).
        temperature_c: Body temperature in Celsius (0 if not reported).
    """
    flags: list[str] = []
    if spo2 and spo2 < 92:
        flags.append(f"Low SpO2 ({spo2}%) — hypoxemia")
    if heart_rate and heart_rate > 130:
        flags.append(f"Tachycardia (HR {heart_rate})")
    if heart_rate and 0 < heart_rate < 40:
        flags.append(f"Bradycardia (HR {heart_rate})")
    if systolic_bp and systolic_bp < 90:
        flags.append(f"Hypotension (SBP {systolic_bp})")
    if respiratory_rate and respiratory_rate > 30:
        flags.append(f"Tachypnea (RR {respiratory_rate})")
    if respiratory_rate and 0 < respiratory_rate < 8:
        flags.append(f"Bradypnea (RR {respiratory_rate})")
    if temperature_c and temperature_c >= 40:
        flags.append(f"High fever ({temperature_c}C)")
    if temperature_c and 0 < temperature_c <= 35:
        flags.append(f"Hypothermia ({temperature_c}C)")

    # Any dangerous vital floors acuity at ESI 2; a critical one or several at ESI 1.
    suggested_min_acuity = None
    if flags:
        suggested_min_acuity = 2
    if (spo2 and spo2 < 85) or (systolic_bp and systolic_bp < 80) or len(flags) >= 2:
        suggested_min_acuity = 1

    return {
        "dangerous_vitals": flags,
        "suggested_min_acuity": suggested_min_acuity,
        "note": "Deterministic threshold check; the agent still reasons over the full presentation.",
        "disclaimer": KB["_disclaimer"],
    }


@mcp.tool()
def get_esi_criteria(complaint: str) -> dict:
    """Return the Emergency Severity Index (ESI 1-5) reference plus the triage
    criteria for a chief complaint. Use this to decide which ESI level best fits
    the patient's presentation.

    Args:
        complaint: The patient's chief complaint in plain language (e.g. "fever").
    """
    key = _match_complaint(complaint)
    data = KB["chief_complaints"][key]
    return {
        "matched_complaint": key,
        "esi_criteria": data["esi_criteria"],
        "esi_levels": KB["esi_levels"],
        "disclaimer": KB["_disclaimer"],
    }


if __name__ == "__main__":
    mcp.run()  # stdio transport
