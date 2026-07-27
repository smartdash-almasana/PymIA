from __future__ import annotations

import pytest

from pymia.smartpyme.owner_semantic_gate_builder import (
    build_pending_owner_semantic_confirmation_gate_from_translation,
)


def _valid_payload() -> dict:
    return {
        "proposed_interpretation": "margin price deviation due to fabric price increase",
        "target_type": "SEMANTIC_INTERPRETATION",
        "source_ref": "owner_narrative://case-123",
        "related_missing_keys": ["own_price", "fabric_cost"],
        "related_pathology_candidates": ["REN_001"],
        "related_formula_candidates": ["PYME_017_pricing_drift"],
        "metadata": {"tenant_id": "tenant-1"},
    }


def test_valid_payload_creates_pending_gate() -> None:
    payload = _valid_payload()
    # Ensure input is not mutated
    payload_copy = dict(payload)
    
    gate = build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    assert gate.status == "PENDING_OWNER_CONFIRMATION"
    assert gate.proposed_interpretation == "margin price deviation due to fabric price increase"
    assert gate.source_ref == "owner_narrative://case-123"
    assert gate.target_type == "SEMANTIC_INTERPRETATION"
    assert gate.related_missing_keys == ["own_price", "fabric_cost"]
    assert gate.related_pathology_candidates == ["REN_001"]
    assert gate.related_formula_candidates == ["PYME_017_pricing_drift"]
    assert gate.metadata == {"tenant_id": "tenant-1"}
    assert gate.is_terminal is False
    assert gate.is_owner_confirmed is False

    # Check input payload is not mutated
    assert payload == payload_copy


def test_missing_proposed_interpretation_fails_closed() -> None:
    payload = _valid_payload()
    del payload["proposed_interpretation"]
    with pytest.raises(ValueError, match="proposed_interpretation is required"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    payload["proposed_interpretation"] = "   "
    with pytest.raises(ValueError, match="proposed_interpretation must be non-empty"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_missing_source_ref_fails_closed() -> None:
    payload = _valid_payload()
    del payload["source_ref"]
    with pytest.raises(ValueError, match="source_ref is required"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    payload["source_ref"] = ""
    with pytest.raises(ValueError, match="source_ref must be non-empty"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_invalid_target_type_fails_closed() -> None:
    payload = _valid_payload()
    payload["target_type"] = "INVALID_TYPE"
    with pytest.raises(ValueError, match="invalid target_type"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_terminal_status_in_payload_fails_closed() -> None:
    payload = _valid_payload()
    payload["status"] = "CONFIRMED_BY_OWNER"
    payload["owner_response_text"] = "Yes"
    with pytest.raises(ValueError, match="Cannot create a gate in a terminal status"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_terminal_fields_in_payload_fails_closed() -> None:
    payload = _valid_payload()
    payload["owner_response_text"] = "Yes"
    with pytest.raises(ValueError, match="Cannot build a pending gate with owner response text"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    payload = _valid_payload()
    payload["corrected_interpretation"] = "Correction"
    with pytest.raises(ValueError, match="Cannot build a pending gate with corrected interpretation"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_lists_are_normalized() -> None:
    payload = _valid_payload()
    payload["related_missing_keys"] = ["  key_1 ", "", "key_2"]
    payload["related_pathology_candidates"] = ["REN_001", "  ", "REN_002"]
    payload["related_formula_candidates"] = ["FORM_1", None, "FORM_2"]

    gate = build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    assert gate.related_missing_keys == ["key_1", "key_2"]
    assert gate.related_pathology_candidates == ["REN_001", "REN_002"]
    assert gate.related_formula_candidates == ["FORM_1", "None", "FORM_2"]


def test_evidence_and_computed_variables_in_metadata_fails_closed() -> None:
    payload = _valid_payload()
    payload["metadata"] = {"evidence_candidate": "something"}
    with pytest.raises(ValueError, match="Payload must not contain evidence_candidate or computed_variables"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)

    payload = _valid_payload()
    payload["metadata"] = {"computed_variables": "something"}
    with pytest.raises(ValueError, match="Payload must not contain evidence_candidate or computed_variables"):
        build_pending_owner_semantic_confirmation_gate_from_translation(payload)


def test_gate_projects_to_question_metadata_correctly() -> None:
    payload = _valid_payload()
    gate = build_pending_owner_semantic_confirmation_gate_from_translation(payload)
    
    metadata = gate.to_owner_question_metadata()
    
    assert metadata["expects_semantic_confirmation"] is True
    assert metadata["semantic_confirmation_gate_id"] == gate.gate_id
    assert metadata["semantic_confirmation_target_type"] == "SEMANTIC_INTERPRETATION"
    assert metadata["proposed_interpretation"] == "margin price deviation due to fabric price increase"
    assert metadata["related_missing_keys"] == ["own_price", "fabric_cost"]
    assert metadata["semantic_confirmation_source_ref"] == "owner_narrative://case-123"
    assert "semantic_confirmation_status" not in metadata
