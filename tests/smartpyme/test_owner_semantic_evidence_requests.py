from __future__ import annotations

import pytest
from pydantic import ValidationError

from pymia.contracts.owner_semantic_evidence_requests import (
    OwnerSemanticEvidenceRequest,
)


def _valid_request_payload() -> dict:
    return {
        "request_id": "semantic_request_own_price_001",
        "missing_key": "own_price",
        "missing_input_type": "STRUCTURAL_INPUT",
        "owner_answer_text": "Los precios los fui cambiando porque subió la tela.",
        "semantic_signal": "PRICE_VARIABILITY_DUE_TO_INPUT_COST",
        "interpreted_meaning": (
            "El dueño indica variación de precios por aumento de insumos."
        ),
        "refined_request_text": (
            "Para calcular margen necesito precios de venta por producto/SKU de la "
            "última semana y, si cambiaron durante el período, desde qué fecha "
            "rigió cada precio."
        ),
        "required_fields": [
            "producto/SKU",
            "precio de venta",
            "fecha o semana de vigencia",
        ],
        "accepted_formats": ["Excel", "lista de precios", "texto estructurado"],
        "does_resolve_structural_input": False,
        "confidence": 0.72,
        "source_ref": "owner_answer://case-001/answer-001",
        "metadata": {"scenario": "owner_semantic_evidence_requests_contract"},
    }


def test_own_price_owner_answer_refines_evidence_request_without_unblocking() -> None:
    request = OwnerSemanticEvidenceRequest(**_valid_request_payload())

    assert request.missing_key == "own_price"
    assert request.missing_input_type == "STRUCTURAL_INPUT"
    assert request.semantic_signal == "PRICE_VARIABILITY_DUE_TO_INPUT_COST"
    assert "precios de venta" in request.refined_request_text
    assert request.required_fields == [
        "producto/SKU",
        "precio de venta",
        "fecha o semana de vigencia",
    ]
    assert request.accepted_formats == ["Excel", "lista de precios", "texto estructurado"]
    assert request.does_resolve_structural_input is False


def test_rejects_structural_resolution_by_owner_narrative() -> None:
    payload = _valid_request_payload()
    payload["does_resolve_structural_input"] = True

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticEvidenceRequest(**payload)

    assert "owner narrative cannot resolve structural input" in str(exc.value)


def test_rejects_empty_required_fields() -> None:
    payload = _valid_request_payload()
    payload["required_fields"] = []

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticEvidenceRequest(**payload)

    assert "list must contain at least one non-empty item" in str(exc.value)


def test_rejects_empty_accepted_formats() -> None:
    payload = _valid_request_payload()
    payload["accepted_formats"] = []

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticEvidenceRequest(**payload)

    assert "list must contain at least one non-empty item" in str(exc.value)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_rejects_confidence_outside_probability_range(confidence: float) -> None:
    payload = _valid_request_payload()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError) as exc:
        OwnerSemanticEvidenceRequest(**payload)

    assert "confidence must be between 0 and 1" in str(exc.value)


def test_model_dump_preserves_trace_and_owner_facing_request() -> None:
    request = OwnerSemanticEvidenceRequest(**_valid_request_payload())

    payload = request.model_dump(mode="json")

    assert payload["missing_key"] == "own_price"
    assert payload["semantic_signal"] == "PRICE_VARIABILITY_DUE_TO_INPUT_COST"
    assert "precios de venta" in payload["refined_request_text"]
    assert payload["does_resolve_structural_input"] is False
