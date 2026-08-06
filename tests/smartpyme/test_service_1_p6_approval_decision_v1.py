from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_AMBIGUOUS,
    STATUS_APPROVED,
    STATUS_BLOCKED,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    Service1P6ApprovalDecisionV1,
    build_service_1_p6_approval_decision_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)


def _candidate(
    *,
    roles=("sales_amount",),
    variables=("sales",),
    owner_confirmation_required=False,
    primary_role="sales_amount",
) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name="venta_total",
        normalized_column_name="venta_total",
        sheet_name="Ventas",
        observed_data_type="number",
        sample_values=(100, 200),
        candidate_semantic_roles=roles,
        candidate_variable_names=variables,
        confidence=0.95,
        ambiguity_reason=None,
        owner_confirmation_required=owner_confirmation_required,
        metadata={"column_ref_id": "Ventas::venta_total", "primary_semantic_role": primary_role},
    )


def test_unambiguous_hypothesis_requires_explicit_owner_confirmation_on_first_contact() -> None:
    out = build_service_1_p6_approval_decision_v1(case_id="case_p6", candidate=_candidate())
    assert out.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert out.reason == "FIRST_CONTACT_OWNER_CONFIRMATION_REQUIRED"
    assert out.approved_role is None
    assert out.approved_variable is None
    payload = out.to_dict()
    for field in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    ):
        assert payload[field] is False
    assert "formula_id" not in payload
    assert "pathology_code" not in payload
    assert "requested_capability" not in payload


def test_owner_confirmation_requirement_stays_fail_closed() -> None:
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_p6",
        candidate=_candidate(owner_confirmation_required=True),
    )
    assert out.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert out.approved_role is None
    assert out.approved_variable is None


def test_owner_event_can_approve_only_role_inside_hypothesis() -> None:
    candidate = _candidate(
        roles=("sales_amount", "collected_amount"),
        variables=("sales", "collected"),
        owner_confirmation_required=True,
        primary_role="sales_amount",
    )
    event = {
        "confirmed_by_owner": True,
        "question_ref": "Ventas::venta_total",
        "sheet_ref": "Ventas",
        "column_ref": "venta_total",
        "confirmation_scope": "SEMANTIC_ROLE",
        "confirmed_role": "collected_amount",
    }
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_p6",
        candidate=candidate,
        owner_confirmation_events=[event],
    )
    assert out.status == STATUS_APPROVED
    assert out.approved_role == "collected_amount"
    assert out.approved_variable == "collected"
    assert out.owner_confirmation_question_ref == "Ventas::venta_total"


def test_owner_role_outside_hypothesis_is_blocked() -> None:
    event = {
        "confirmed_by_owner": True,
        "question_ref": "Ventas::venta_total",
        "sheet_ref": "Ventas",
        "column_ref": "venta_total",
        "confirmation_scope": "SEMANTIC_ROLE",
        "confirmed_role": "inventory_quantity",
    }
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_p6",
        candidate=_candidate(owner_confirmation_required=True),
        owner_confirmation_events=[event],
    )
    assert out.status == STATUS_BLOCKED
    assert out.reason == "OWNER_CONFIRMED_ROLE_OUTSIDE_HYPOTHESIS"


def test_free_text_owner_evidence_does_not_become_approved_semantics() -> None:
    event = {
        "confirmed_by_owner": True,
        "question_ref": "Ventas::venta_total",
        "sheet_ref": "Ventas",
        "column_ref": "venta_total",
        "confirmation_scope": "FREE_TEXT_MEANING",
        "corrected_meaning": "es un valor interno",
    }
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_p6",
        candidate=_candidate(owner_confirmation_required=True),
        owner_confirmation_events=[event],
    )
    assert out.status == STATUS_AMBIGUOUS
    assert out.approved_role is None


def test_multiple_owner_events_for_same_column_block() -> None:
    event = {
        "confirmed_by_owner": True,
        "question_ref": "Ventas::venta_total",
        "sheet_ref": "Ventas",
        "column_ref": "venta_total",
        "confirmation_scope": "SEMANTIC_ROLE",
        "confirmed_role": "sales_amount",
    }
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_p6",
        candidate=_candidate(),
        owner_confirmation_events=[event, dict(event)],
    )
    assert out.status == STATUS_BLOCKED
    assert out.reason == "MULTIPLE_OWNER_CONFIRMATION_EVENTS_FOR_COLUMN"


def test_non_approved_decision_cannot_smuggle_approved_meaning() -> None:
    with pytest.raises(ValueError):
        Service1P6ApprovalDecisionV1(
            case_id="case",
            sheet_ref="Ventas",
            column_ref="venta_total",
            status=STATUS_AMBIGUOUS,
            approved_role="sales_amount",
            approved_variable=None,
            reason="invalid",
        )


@pytest.mark.parametrize(
    ("role", "variable"),
    (
        ("period_sales_total", "sale_price"),
        ("period_costs_total", "costs"),
        ("period_taxes_total", "taxes"),
    ),
)
def test_period_net_margin_semantic_roles_require_owner_confirmation_on_first_contact(
    role: str, variable: str
) -> None:
    out = build_service_1_p6_approval_decision_v1(
        case_id="case_period_net_margin",
        candidate=_candidate(
            roles=(role,),
            variables=(variable,),
            primary_role=role,
        ),
    )

    assert out.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert out.reason == "FIRST_CONTACT_OWNER_CONFIRMATION_REQUIRED"
    assert out.approved_role is None
    assert out.approved_variable is None
    assert out.to_dict()["runtime_authorized"] is False
