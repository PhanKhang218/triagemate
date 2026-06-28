"""Deterministic safety guardrails — pure, unit-testable functions that run outside
the LLM: PHI redaction, prompt-injection detection, and output validation."""

from __future__ import annotations

import re

from .config import ESI_MAX, ESI_MIN

# Direct patient identifiers to strip before anything is logged.
_PHI_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("PHONE", re.compile(r"\b(?:\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")),
    ("MRN", re.compile(r"(?i)\b(?:mrn|record(?:\s*no)?)[:\s#]*\d{4,}\b")),
    ("DOB", re.compile(r"(?i)\b(?:dob|date of birth)[:\s]*\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b")),
]


def redact_phi(text: str) -> tuple[str, list[str]]:
    """Redact identifiers and return (redacted_text, categories_found)."""
    redacted = text or ""
    found: list[str] = []
    for label, pattern in _PHI_PATTERNS:
        if pattern.search(redacted):
            redacted = pattern.sub(f"[REDACTED {label}]", redacted)
            found.append(label)
    return redacted, found


# Patterns that try to steer the triage decision instead of describing symptoms.
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(ignore|disregard|forget)\b.*\b(instructions?|rules?|protocol|red flags?|guardrails?)\b"),
    re.compile(r"(?i)\b(override|bypass)\b.*\b(triage|protocol|safety|review|rules?)\b"),
    re.compile(r"(?i)\b(mark|set|classify|rate)\b.*\b(esi|level|priority|acuity)\b.*\b([45]|low(est)?|non-?urgent)\b"),
    re.compile(r"(?i)\bsend\b.*\bhome\b"),
    re.compile(r"(?i)\b(you are now|act as|new instructions?)\b"),
    re.compile(r"(?i)^\s*(system|assistant)\s*:"),
]


def detect_prompt_injection(text: str) -> bool:
    """Return True if the free text tries to steer the triage decision."""
    return any(pattern.search(text or "") for pattern in _INJECTION_PATTERNS)


# Phrases that cross from triage routing into diagnosis or treatment.
_OVERREACH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(diagnosis is|you have|the patient has)\b"),
    re.compile(r"(?i)\b(prescribe|prescription|administer|take)\b.*\b(\d+\s?mg|tablet|dose|medication)\b"),
    re.compile(r"(?i)\b(start|give)\b.*\b(antibiotics?|insulin|morphine|aspirin)\b"),
]


def contains_clinical_overreach(text: str) -> bool:
    """Return True if text gives a diagnosis or treatment (outside the mandate)."""
    return any(pattern.search(text or "") for pattern in _OVERREACH_PATTERNS)


def validate_triage_result(result: dict) -> list[str]:
    """Validate a TriageResult dict; return a list of issues (empty == valid)."""
    issues: list[str] = []

    esi = result.get("esi_level")
    if not isinstance(esi, int) or not (ESI_MIN <= esi <= ESI_MAX):
        issues.append(f"esi_level {esi!r} is outside the valid range {ESI_MIN}-{ESI_MAX}")

    if not result.get("rationale"):
        issues.append("rationale is missing")

    if not result.get("disclaimer"):
        issues.append("mandatory disclaimer is missing")

    if result.get("requires_nurse_confirmation") is not True:
        issues.append("requires_nurse_confirmation must be True (human-in-the-loop)")

    disposition = result.get("recommended_disposition", "")
    if contains_clinical_overreach(disposition):
        issues.append("recommended_disposition contains diagnosis/treatment language")

    return issues
