---
name: symptom-analysis
description: Methodology for converting a free-text patient description into a structured, triage-ready presentation.
---

# Symptom Analysis

Follow this procedure when structuring a patient's presentation:

1. Identify the single **chief complaint** — the dominant reason for the visit.
2. Capture **onset, duration, and severity** if stated; mark "unknown" otherwise.
3. Record any **vital signs verbatim**. Never infer a vital sign that was not stated.
4. Note pertinent **history and current medications** that affect acuity.
5. Explicitly list **missing critical data** (especially vital signs and onset) in
   `missing_critical_info` so the triage step can reason conservatively.

Keep the narrative concise and in clinical language. Do not diagnose or interpret —
your only job is faithful structuring.
