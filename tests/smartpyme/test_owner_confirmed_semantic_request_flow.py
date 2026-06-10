from __future__ import annotations

import pytest

from pymia.contracts.owner_semantic_confirmation import OwnerSemanticConfirmationGate
from pymia.contracts.owner_semantic_evidence_requests import OwnerSemanticEvidenceRequest
from pymia.smartpyme.owner_confirmed_semantic_request_flow import (
    build_owner_confirmed_semantic_request_flow,
)


def _confirmation_gate_payload() -> dict:
    return {
        "gate_id": "semantic_gate_001",
        "target_type": "PATHOLOGY_AXIS",
        "proposed_interpretation": (
            "El eje a revisar es variación de precios por suba de tela."
        ),
        "confirmation_question": "¿Confirmás que este es el eje correcto?",
        "related_missing_keys": ["own_price"],
        "related_pathology_candidates": ["REN_001"],
        "related_formula_candidates": ["PYME_017_pricing_drift"],
        "source_ref": "owner_semantic_gate://case-001/gate-001",
    }


def _pending_gate() -> OwnerSemanticConfirmationGate:
    return OwnerSemanticConfirmationGate(**_confirmation_gate_payload())


def _confirmed_gate(owner_response_text: str | None = None) -> OwnerSemanticConfirmationGate:
    payload = _confirmation_gate_payload()
    payload["status"] = "CONFIRMED_BY_OWNER"
    payload["owner_response_text"] = owner_response_text or (
        "Sí, la tela subió y fui cambiando precios"
    )
    return OwnerSemanticConfirmationGate(**payload)


def _rejected_gate() -> OwnerSemanticConfirmationGate:
    payload = _confirmation_gate_payload()
    payload["status"] = "REJECTED_BY_OWNER"
    payload["owner_response_text"] = "No, no es ese el problema."
    return OwnerSemanticConfirmationGate(**payload)


def _corrected_gate() -> OwnerSemanticConfirmationGate:
    payload = _confirmation_gate_payload()
    payload["status"] = "CORRECTED_BY_OWNER"
    payload["owner_response_text"] = "No, el problema es otro."
    payload["corrected_interpretation"] = (
        "El problema principal es que los clientes pagan tarde"
    )
    return OwnerSemanticConfirmationGate(**payload)


def test_pending_gate_returns_pending_confirmation_without_requests() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_pending_gate(),
        missing_keys=["own_price"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "PENDING_OWNER_CONFIRMATION"
    assert result.semantic_evidence_requests == ()
    assert result.unsupported_missing_keys == ()
    assert result.is_blocked_actionable is False


def test_rejected_gate_needs_reinterpretation_without_requests() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_rejected_gate(),
        missing_keys=["own_price"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "NEEDS_REINTERPRETATION"
    assert result.semantic_evidence_requests == ()
    assert result.unsupported_missing_keys == ()
    assert result.is_blocked_actionable is False


def test_confirmed_gate_with_own_price_generates_blocked_actionable_request() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_confirmed_gate(),
        missing_keys=["own_price"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "BLOCKED_ACTIONABLE"
    assert len(result.semantic_evidence_requests) == 1
    request = result.semantic_evidence_requests[0]
    assert isinstance(request, OwnerSemanticEvidenceRequest)
    assert request.missing_key == "own_price"
    assert request.does_resolve_structural_input is False
    assert request.metadata["produces_findings"] is False
    assert request.metadata["does_resolve_structural_input"] is False


def test_corrected_gate_uses_corrected_interpretation_as_owner_answer_text() -> None:
    corrected_interpretation = "El problema principal es que los clientes pagan tarde"

    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_corrected_gate(),
        missing_keys=["dso"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "BLOCKED_ACTIONABLE"
    assert len(result.semantic_evidence_requests) == 1
    assert result.semantic_evidence_requests[0].missing_key == "dso"
    assert result.semantic_evidence_requests[0].owner_answer_text == corrected_interpretation


def test_deduplicates_missing_keys_preserving_first_supported_occurrence() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_confirmed_gate(),
        missing_keys=["own_price", "own_price", "dso"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "BLOCKED_ACTIONABLE"
    assert [request.missing_key for request in result.semantic_evidence_requests] == [
        "own_price",
        "dso",
    ]


def test_unsupported_missing_key_is_reported_without_blocking_supported_requests() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_confirmed_gate(),
        missing_keys=["own_price", "unsupported_key"],
        source_ref="owner_semantic_flow://case-001",
    )

    assert result.flow_status == "BLOCKED_ACTIONABLE"
    assert [request.missing_key for request in result.semantic_evidence_requests] == [
        "own_price"
    ]
    assert result.unsupported_missing_keys == ("unsupported_key",)


def test_empty_source_ref_fails_closed() -> None:
    with pytest.raises(ValueError) as exc:
        build_owner_confirmed_semantic_request_flow(
            confirmation_gate=_confirmed_gate(),
            missing_keys=["own_price"],
            source_ref="",
        )

    assert "source_ref must be non-empty" in str(exc.value)


def test_metadata_preserves_initial_values_and_adds_confirmation_trace() -> None:
    result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=_confirmed_gate(),
        missing_keys=["own_price"],
        source_ref="owner_semantic_flow://case-001",
        metadata={"tenant_id": "tenant-1"},
    )

    assert result.metadata["tenant_id"] == "tenant-1"
    assert result.metadata["confirmation_gate_id"] == "semantic_gate_001"
    assert result.metadata["confirmation_status"] == "CONFIRMED_BY_OWNER"
    assert result.metadata["confirmation_target_type"] == "PATHOLOGY_AXIS"
    assert result.metadata["does_resolve_structural_input"] is False
    assert result.metadata["produces_findings"] is False
    request = result.semantic_evidence_requests[0]
    assert request.metadata["tenant_id"] == "tenant-1"
    assert request.metadata["confirmation_gate_id"] == "semantic_gate_001"
    assert request.metadata["confirmation_status"] == "CONFIRMED_BY_OWNER"
    assert request.metadata["confirmation_target_type"] == "PATHOLOGY_AXIS"
    assert request.metadata["does_resolve_structural_input"] is False
    assert request.metadata["produces_findings"] is False
