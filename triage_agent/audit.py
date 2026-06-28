"""Append-only audit trail: one PHI-redacted JSON event per triage decision."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from .config import AUDIT_LOG_PATH
from .guardrails import redact_phi


def record_triage_event(
    presentation: dict,
    result: dict,
    extra_security_flags: list[str] | None = None,
) -> dict:
    """Redact the narrative, write one audit event, and return it."""
    redacted_narrative, phi_categories = redact_phi(presentation.get("narrative", ""))

    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "chief_complaint": presentation.get("chief_complaint", "unknown"),
        "redacted_narrative": redacted_narrative,
        "phi_categories_detected": phi_categories,
        "esi_level": result.get("esi_level"),
        "esi_label": result.get("esi_label"),
        "matched_red_flags": result.get("matched_red_flags", []),
        "safety_flags": (result.get("safety_flags", []) or []) + (extra_security_flags or []),
        "requires_nurse_confirmation": result.get("requires_nurse_confirmation", True),
    }

    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event
