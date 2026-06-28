"""Central configuration for TriageMate."""

from __future__ import annotations

import os

# Model used by every sub-agent (free-tier friendly, no GCP billing needed).
MODEL = "gemini-2.5-flash"

# Valid Emergency Severity Index range.
ESI_MIN = 1
ESI_MAX = 5

# Audit trail location (one JSON event per line).
AUDIT_LOG_PATH = os.environ.get(
    "TRIAGEMATE_AUDIT_LOG",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "audit_log.jsonl"),
)
