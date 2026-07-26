from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    Service1OwnerConfirmationEventV1,
    build_service_1_owner_confirmation_event_v1,
)


def test_owner_confirmation_event_is_evidence_only() -> None:
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case_1",
        file_ref="ventas.xlsx",
        region_ref="region_1",
        sheet_ref="Ventas",
        column_ref="importe",
        question_ref="q_1",
        owner_answer="OPT_VENTA",
        proposed_role="sales_amount",
        confirmed_role="sales_amount",
        confirmation_scope="SEMANTIC_ROLE",
        timestamp="2026-07-26T17:00:00+00:00",
        provenance={"producer": "test"},
    )
    payload = event.to_dict()
    assert isinstance(event, Service1OwnerConfirmationEventV1)
    assert payload["confirmed_by_owner"] is True
    assert payload["confirmed_role"] == "sales_amount"
    assert payload["runtime_authorized"] is False
    assert payload["tool_execution_authorized"] is False
    assert payload["product_ready"] is False
    assert payload["delivery_authorized"] is False
    assert payload["diagnosis_generated"] is False


def test_owner_confirmation_event_rejects_permission_in_provenance() -> None:
    with pytest.raises(ValueError):
        build_service_1_owner_confirmation_event_v1(
            case_id="case_1",
            file_ref="ventas.xlsx",
            region_ref=None,
            sheet_ref="Ventas",
            column_ref="importe",
            question_ref="q_1",
            owner_answer="OPT_VENTA",
            confirmed_role="sales_amount",
            confirmation_scope="SEMANTIC_ROLE",
            timestamp="2026-07-26T17:00:00+00:00",
            provenance={"runtime_authorized": True},
        )


def test_owner_confirmation_event_free_text_is_not_semantic_approval() -> None:
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case_1",
        file_ref="ventas.xlsx",
        region_ref=None,
        sheet_ref="Ventas",
        column_ref="otro",
        question_ref="q_2",
        owner_answer="OTHER",
        corrected_meaning="importe reservado internamente",
        confirmation_scope="FREE_TEXT_MEANING",
        timestamp="2026-07-26T17:00:00+00:00",
        provenance={"normalization_required": True},
    )
    assert event.confirmed_role is None
    assert event.corrected_meaning == "importe reservado internamente"
