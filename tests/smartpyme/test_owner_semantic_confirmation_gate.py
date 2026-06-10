from __future__ import annotations

import pytest
from pydantic import ValidationError

from pymia.contracts.owner_semantic_confirmation import OwnerSemanticConfirmationGate


def _base_payload() -> dict:
    return {
        "gate_id": "semantic_confirmation_gate_001",
        "target_type": "SEMANTIC_INTERPRETATION",
        "proposed_interpretation": (
            "Estoy entendiendo que el eje a revisar es variación de precios por suba de tela."
        ),
        "confirmation_question": "¿Confirmás que este es el eje correcto para avanzar?",
        "related_missing_keys": ["own_price"],
        "related_pathology_candidates": ["REN_001"],
        "related_formula_candidates": ["PYME_017_pricing_drift"],
        "source_ref": "owner_semantic_request://case-001/request-001",
        "metadata": {"tenant_id": "tenant-1"},
    }


def test_pending_gate_is_valid_without_owner_response_or_correction() -> None:
    gate = OwnerSemanticConfirmationGate(**_base_payload())

    assert gate.status == "PENDING_OWNER_CONFIRMATION"
    assert gate.owner_response_text is None
    assert gate.corrected_interpretation is None
    assert gate.is_owner_confirmed is False
    assert gate.is_terminal is False


def test_confirmed_gate_requires_owner_response_and_is_terminal() -> None:
    payload = _base_payload()
    payload["status"] = "CONFIRMED_BY_OWNER"
    payload["owner_response_text"] = "Sí, ese es el problema principal."

    gate = OwnerSemanticConfirmationGate(**payload)

    assert gate.status == "CONFIRMED_BY_OWNER"
    assert gate.owner_response_text == "Sí, ese es el problema principal."
    assert gate.corrected_interpretation is None
    assert gate.is_owner_confirmed is True
    assert gate.is_terminal is True


def test_rejected_gate_requires_owner_response_and_is_terminal() -> None:
    payload = _base_payload()
    payload["status"] = "REJECTED_BY_OWNER"
    payload["owner_response_text"] = "No, no es por la tela."

    gate = OwnerSemanticConfirmationGate(**payload)

    assert gate.status == "REJECTED_BY_OWNER"
    assert gate.owner_response_text == "No, no es por la tela."
    assert gate.is_owner_confirmed is False
    assert gate.is_terminal is True


def test_corrected_gate_requires_owner_response_and_corrected_interpretation() -> None:
    payload = _base_payload()
    payload["status"] = "CORRECTED_BY_OWNER"
    payload["owner_response_text"] = "No, el problema principal es que me pagan tarde."
    payload["corrected_interpretation"] = (
        "El eje confirmado por el dueño es atraso de cobranzas."
    )

    gate = OwnerSemanticConfirmationGate(**payload)

    assert gate.status == "CORRECTED_BY_OWNER"
    assert gate.owner_response_text == "No, el problema principal es que me pagan tarde."
    assert gate.corrected_interpretation == (
        "El eje confirmado por el dueño es atraso de cobranzas."
    )
    assert gate.is_owner_confirmed is False
    assert gate.is_terminal is True


def test_rejects_pending_gate_with_owner_response() -> None:
    payload = _base_payload()
    payload["owner_response_text"] = "Sí."

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticConfirmationGate(**payload)

    assert "pending gate cannot include owner response or correction" in str(exc.value)


@pytest.mark.parametrize("status", ["CONFIRMED_BY_OWNER", "REJECTED_BY_OWNER"])
def test_rejects_confirmed_or_rejected_gate_without_owner_response(status: str) -> None:
    payload = _base_payload()
    payload["status"] = status

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticConfirmationGate(**payload)

    assert "confirmed or rejected gate requires owner_response_text" in str(exc.value)


def test_rejects_corrected_gate_without_corrected_interpretation() -> None:
    payload = _base_payload()
    payload["status"] = "CORRECTED_BY_OWNER"
    payload["owner_response_text"] = "No, es otra cosa."

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticConfirmationGate(**payload)

    assert "corrected gate requires owner_response_text and corrected_interpretation" in str(
        exc.value
    )


@pytest.mark.parametrize(
    "field_name",
    ["gate_id", "proposed_interpretation", "confirmation_question", "source_ref"],
)
def test_rejects_empty_required_strings(field_name: str) -> None:
    payload = _base_payload()
    payload[field_name] = ""

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticConfirmationGate(**payload)

    assert "field must be non-empty" in str(exc.value)


def test_model_dump_preserves_traceable_confirmation_fields() -> None:
    gate = OwnerSemanticConfirmationGate(**_base_payload())

    payload = gate.model_dump(mode="json")

    assert payload["gate_id"] == "semantic_confirmation_gate_001"
    assert payload["target_type"] == "SEMANTIC_INTERPRETATION"
    assert payload["proposed_interpretation"] == (
        "Estoy entendiendo que el eje a revisar es variación de precios por suba de tela."
    )
    assert payload["confirmation_question"] == (
        "¿Confirmás que este es el eje correcto para avanzar?"
    )
    assert payload["related_missing_keys"] == ["own_price"]
    assert payload["related_pathology_candidates"] == ["REN_001"]
    assert payload["related_formula_candidates"] == ["PYME_017_pricing_drift"]
    assert payload["source_ref"] == "owner_semantic_request://case-001/request-001"
