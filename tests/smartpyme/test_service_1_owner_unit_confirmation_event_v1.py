from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_owner_unit_confirmation_event_v1 import (
    UNIT_DISCOUNT_FRACTION,
    build_service_1_owner_unit_confirmation_event_v1,
)


def test_owner_unit_confirmation_event_is_explicit_evidence_without_authority() -> None:
    event = build_service_1_owner_unit_confirmation_event_v1(
        case_id="case-unit",
        file_ref="cafeteria.xlsx",
        sheet_ref="Ventas",
        column_ref="Descuento",
        semantic_role="discount_candidate",
        unit_kind=UNIT_DISCOUNT_FRACTION,
        owner_answer=UNIT_DISCOUNT_FRACTION,
        question_ref="derived-unit:Ventas.Descuento",
        provenance={"owner_actor_id": "owner-1", "owner_actor_role": "OWNER"},
    )

    payload = event.to_dict()
    assert payload["confirmed_by_owner"] is True
    assert payload["unit_kind"] == UNIT_DISCOUNT_FRACTION
    assert payload["runtime_authorized"] is False
    assert payload["tool_execution_authorized"] is False
    assert payload["product_ready"] is False
    assert payload["delivery_authorized"] is False
    assert payload["diagnosis_generated"] is False


def test_owner_unit_confirmation_event_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError, match="unsupported unit_kind"):
        build_service_1_owner_unit_confirmation_event_v1(
            case_id="case-unit",
            sheet_ref="Ventas",
            column_ref="Descuento",
            semantic_role="discount_candidate",
            unit_kind="GUESS_PERCENT",
            owner_answer="GUESS_PERCENT",
            question_ref="derived-unit:Ventas.Descuento",
        )


def test_owner_unit_confirmation_event_rejects_authority_in_provenance() -> None:
    with pytest.raises(ValueError, match="provenance cannot carry authority fields"):
        build_service_1_owner_unit_confirmation_event_v1(
            case_id="case-unit",
            sheet_ref="Ventas",
            column_ref="Descuento",
            semantic_role="discount_candidate",
            unit_kind=UNIT_DISCOUNT_FRACTION,
            owner_answer=UNIT_DISCOUNT_FRACTION,
            question_ref="derived-unit:Ventas.Descuento",
            provenance={"runtime_authorized": False},
        )
