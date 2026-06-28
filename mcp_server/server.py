"""clinical-kb MCP server: read-only red-flag and ESI-criteria lookups over stdio,
backed by a curated JSON file (no network calls, no patient data).

Run standalone for debugging: python mcp_server/server.py
"""

from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

with open(KB_PATH, encoding="utf-8") as f:
    KB = json.load(f)

mcp = FastMCP("clinical-kb")


def _match_complaint(complaint: str) -> str:
    """Resolve free-text complaint to a KB key by alias matching; fall back to 'general'."""
    query = (complaint or "").strip().lower()
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
