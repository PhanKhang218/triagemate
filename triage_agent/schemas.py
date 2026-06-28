"""Pydantic contracts validated at every hand-off between agents."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Vitals(BaseModel):
    """Reported vital signs (all optional)."""

    heart_rate: int | None = Field(None, description="Heart rate (beats/min), if reported")
    spo2: int | None = Field(None, description="Oxygen saturation (%), if reported")
    systolic_bp: int | None = Field(None, description="Systolic blood pressure (mmHg), if reported")
    respiratory_rate: int | None = Field(None, description="Respiratory rate (breaths/min), if reported")
    temperature_c: float | None = Field(None, description="Body temperature (Celsius), if reported")


class PatientPresentation(BaseModel):
    """Structured form of the nurse's free text, produced by the Intake Agent."""

    chief_complaint: str = Field(description="Main reason for the visit, in a few words")
    narrative: str = Field(description="Concise clinical-language summary of the presentation")
    onset: str = Field("unknown", description="When symptoms started, if stated")
    age: int | None = Field(None, description="Patient age in years, if stated")
    sex: str = Field("unknown", description="Patient sex, if stated")
    vitals: Vitals = Field(default_factory=Vitals, description="Reported vital signs")
    relevant_history: list[str] = Field(
        default_factory=list, description="Relevant history or medications mentioned"
    )
    missing_critical_info: list[str] = Field(
        default_factory=list,
        description="Important data not provided (e.g. 'vital signs', 'onset time')",
    )


class TriageResult(BaseModel):
    """Final triage recommendation from the Safety Reviewer Agent (decision support only)."""

    esi_level: int = Field(
        description="Emergency Severity Index from 1 (most urgent) to 5 (least urgent)",
        ge=1,
        le=5,
    )
    esi_label: str = Field(description="Human-readable ESI label, e.g. 'Emergent'")
    matched_red_flags: list[str] = Field(
        default_factory=list, description="Emergency red flags identified in the presentation"
    )
    rationale: str = Field(description="Plain-language explanation for the chosen ESI level")
    recommended_disposition: str = Field(
        description="Routing suggestion only (e.g. 'Immediate provider evaluation'). "
        "Never a diagnosis or treatment."
    )
    safety_flags: list[str] = Field(
        default_factory=list, description="Guardrail concerns raised during safety review"
    )
    disclaimer: str = Field(
        "Decision support only. A licensed clinician makes the final triage decision.",
        description="Mandatory non-diagnostic disclaimer",
    )
    requires_nurse_confirmation: bool = Field(
        True, description="Always True — a licensed nurse must confirm before any action"
    )
