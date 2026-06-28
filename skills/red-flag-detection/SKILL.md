---
name: red-flag-detection
description: Procedure for screening a presentation against emergency red flags and mapping to ESI acuity.
---

# Red-Flag Detection

Apply this procedure on every triage:

1. Always query the clinical-kb for **both** `lookup_red_flags` and
   `get_esi_criteria` using the chief complaint — never rely on memory alone.
2. Match each red flag against the presentation **conservatively**: if the
   presentation plausibly fits a red flag, treat it as present.
3. A matched red flag's `suggested_esi` is a **ceiling** for urgency (a lower
   number = more urgent). Choose the most urgent applicable level.
4. **Dangerous vital signs escalate regardless of complaint**: SpO2 < 92%,
   SBP < 90 mmHg, HR > 130, RR > 30, or altered mental status → ESI 1-2.
5. **Anchor to the matched red flag's `suggested_esi`.** Reserve **ESI 1** for an
   immediate life-threat or a dangerous vital sign. Missing data alone is not a
   reason to jump to ESI 1 — note the gap and reason from what is known.
6. When genuinely uncertain between two **adjacent** levels, choose the more
   urgent of the two — under-triage is more dangerous than mild over-triage.
