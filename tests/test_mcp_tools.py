"""Tests for the clinical-kb MCP tools (deterministic, no LLM or network)."""

from mcp_server.server import (
    _match_complaint,
    assess_vital_signs,
    get_esi_criteria,
    lookup_red_flags,
)

# --- complaint matching ----------------------------------------------------


def test_matches_known_complaint_via_alias():
    assert _match_complaint("can't breathe") == "shortness of breath"
    assert _match_complaint("facial droop") == "stroke symptoms"
    assert _match_complaint("throwing up") == "vomiting and diarrhea"


def test_unknown_complaint_falls_back_to_general():
    assert _match_complaint("ingrown toenail") == "general"


def test_lookup_red_flags_returns_flags_for_complaint():
    result = lookup_red_flags("chest pain")
    assert result["matched_complaint"] == "chest pain"
    assert len(result["red_flags"]) >= 1


def test_get_esi_criteria_returns_five_levels():
    result = get_esi_criteria("fever")
    assert sorted(result["esi_levels"].keys()) == ["1", "2", "3", "4", "5"]


# --- deterministic vital-sign assessment -----------------------------------


def test_normal_vitals_have_no_flags():
    result = assess_vital_signs(heart_rate=78, spo2=98, systolic_bp=120, respiratory_rate=16)
    assert result["dangerous_vitals"] == []
    assert result["suggested_min_acuity"] is None


def test_low_spo2_is_flagged_and_floors_acuity():
    result = assess_vital_signs(spo2=90)
    assert any("SpO2" in f for f in result["dangerous_vitals"])
    assert result["suggested_min_acuity"] == 2


def test_critical_spo2_floors_acuity_at_one():
    result = assess_vital_signs(spo2=82)
    assert result["suggested_min_acuity"] == 1


def test_multiple_dangerous_vitals_floor_at_one():
    result = assess_vital_signs(heart_rate=140, systolic_bp=85)
    assert len(result["dangerous_vitals"]) >= 2
    assert result["suggested_min_acuity"] == 1


def test_unreported_vitals_are_ignored():
    # 0 means "not reported" — must not be treated as a dangerous value.
    result = assess_vital_signs(heart_rate=0, spo2=0, systolic_bp=0)
    assert result["dangerous_vitals"] == []
