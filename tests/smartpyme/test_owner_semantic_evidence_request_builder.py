from __future__ import annotations

import pytest
from pydantic import ValidationError

from pymia.smartpyme.owner_semantic_evidence_request_builder import (
    build_owner_semantic_evidence_request,
)


def test_builds_own_price_request_from_input_cost_narrative() -> None:
    request = build_owner_semantic_evidence_request(
        missing_key="own_price",
        owner_answer_text="Los precios los fui cambiando porque subió la tela.",
        source_ref="owner_answer://case-001/answer-001",
    )

    assert request.semantic_signal == "PRICE_VARIABILITY_DUE_TO_INPUT_COST"
    assert request.confidence == 0.82
    assert "última semana" in request.refined_request_text
    assert request.required_fields == [
        "producto/SKU",
        "precio de venta",
        "fecha o semana de vigencia",
    ]
    assert request.does_resolve_structural_input is False


def test_builds_average_stock_request_from_informal_stock_narrative() -> None:
    request = build_owner_semantic_evidence_request(
        missing_key="average_stock",
        owner_answer_text="El stock lo llevo a ojo.",
        source_ref="owner_answer://case-001/answer-002",
    )

    assert request.semantic_signal == "STOCK_ESTIMATED_OR_INFORMAL"
    assert "stock inicial" in request.refined_request_text
    assert "stock final" in request.refined_request_text
    assert "si es estimado o exacto" in request.required_fields
    assert request.does_resolve_structural_input is False


def test_builds_dso_request_from_collection_delay_narrative() -> None:
    request = build_owner_semantic_evidence_request(
        missing_key="dso",
        owner_answer_text="Algunos clientes pagan tarde y se atrasan.",
        source_ref="owner_answer://case-001/answer-003",
    )

    assert request.semantic_signal == "COLLECTION_DELAY_CONTEXT"
    assert "fecha real de cobro" in request.refined_request_text
    assert request.required_fields == [
        "cliente",
        "importe",
        "fecha de factura o venta",
        "fecha real de cobro o plazo",
        "estado pendiente si aplica",
    ]
    assert request.does_resolve_structural_input is False


def test_supported_missing_key_without_specific_terms_stays_actionable_with_lower_confidence() -> None:
    request = build_owner_semantic_evidence_request(
        missing_key="own_price",
        owner_answer_text="Tengo esa información en otro archivo.",
        source_ref="owner_answer://case-001/answer-004",
    )

    assert request.semantic_signal == "PRICE_REQUIRED_FOR_MARGIN"
    assert request.confidence == 0.64
    assert "precios de venta" in request.refined_request_text
    assert request.required_fields
    assert request.accepted_formats
    assert request.does_resolve_structural_input is False


def test_unsupported_missing_key_fails_closed() -> None:
    with pytest.raises(ValueError) as exc:
        build_owner_semantic_evidence_request(
            missing_key="unsupported_key",
            owner_answer_text="Tengo ese dato.",
            source_ref="owner_answer://case-001/answer-005",
        )

    assert "unsupported missing_key" in str(exc.value)


def test_request_id_is_deterministic_for_same_input() -> None:
    kwargs = {
        "missing_key": "own_price",
        "owner_answer_text": "Los precios los fui cambiando porque subió la tela.",
        "source_ref": "owner_answer://case-001/answer-006",
    }

    first = build_owner_semantic_evidence_request(**kwargs)
    second = build_owner_semantic_evidence_request(**kwargs)

    assert first.request_id == second.request_id


def test_preserves_metadata() -> None:
    request = build_owner_semantic_evidence_request(
        missing_key="average_stock",
        owner_answer_text="El stock lo llevo a ojo.",
        source_ref="owner_answer://case-001/answer-007",
        metadata={"tenant_id": "tenant-1"},
    )

    assert request.metadata["tenant_id"] == "tenant-1"


@pytest.mark.parametrize(
    ("owner_answer_text", "source_ref"),
    [
        ("", "owner_answer://case-001/answer-008"),
        ("Los precios cambiaron.", ""),
    ],
)
def test_empty_required_text_fields_fail_validation(
    owner_answer_text: str,
    source_ref: str,
) -> None:
    with pytest.raises(ValidationError):
        build_owner_semantic_evidence_request(
            missing_key="own_price",
            owner_answer_text=owner_answer_text,
            source_ref=source_ref,
        )
