from __future__ import annotations

from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_CAPABILITY,
    Service1GovernedComputationInputV1,
    build_service_1_computability_decision_v1,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understanding_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    build_service_1_p6_approval_decision_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_PERIOD_NET_MARGIN,
    P7_STATUS_MATCHED,
    build_service_1_requirement_matches_v1,
)


def _p6() -> list[dict]:
    return [
        {"status": "APPROVED", "approved_variable": "sold_amount", "column_ref": "venta_total", "reason": "UNAMBIGUOUS_SEMANTIC_HYPOTHESIS"},
        {"status": "APPROVED", "approved_variable": "collected_amount", "column_ref": "cobrado", "reason": "OWNER_CONFIRMED_SEMANTIC_ROLE"},
    ]


def _p7(*, status: str = "REQUIREMENT_MATCHED") -> list[dict]:
    return [{
        "family_id": "CASH_COLLECTIONS",
        "status": status,
        "missing_role_groups": [] if status == "REQUIREMENT_MATCHED" else [["collected_amount"]],
        "target_capabilities": ["sold_vs_collected_gap"],
        "grain": {
            "structural_scope": "REGION",
            "business_entity_grain": "NONE",
            "temporal_grain": "NONE",
            "aggregation_grain": "ATOMIC",
        },
    }]


def _period_net_margin_p6() -> list[dict]:
    return [
        {"status": "APPROVED", "approved_role": "period_sales_total", "approved_variable": "sale_price", "column_ref": "ventas_periodo"},
        {"status": "APPROVED", "approved_role": "period_costs_total", "approved_variable": "costs", "column_ref": "cmv_total"},
        {"status": "APPROVED", "approved_role": "period_taxes_total", "approved_variable": "taxes", "column_ref": "impuestos_periodo"},
    ]


def _period_net_margin_p7(*, status: str = "REQUIREMENT_MATCHED") -> list[dict]:
    return [{
        "family_id": "PERIOD_NET_MARGIN",
        "status": status,
        "missing_role_groups": [] if status == "REQUIREMENT_MATCHED" else [["period_taxes_total"]],
        "target_capabilities": ["net_margin_real"],
        "grain": {
            "structural_scope": "SHEET",
            "business_entity_grain": "NONE",
            "temporal_grain": "PERIOD",
            "aggregation_grain": "AGGREGATED",
        },
    }]


def test_p8_emits_governed_computation_input_without_runtime_authority() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8",
        requested_capability="sold_vs_collected_gap",
        p6_decisions=_p6(),
        requirement_matches=_p7(),
    )
    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_computation_input
    assert isinstance(governed, Service1GovernedComputationInputV1)
    assert governed.formula_id == "LIQ_001_vendido_cobrado"
    assert dict(governed.source_bindings) == {"sold_amount": "venta_total", "collected_amount": "cobrado"}
    payload = governed.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["delivery_authorized"] is False


def test_p8_rejects_nonapproved_p6_input() -> None:
    p6 = _p6()
    p6[1]["status"] = "AMBIGUOUS"
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="sold_vs_collected_gap", p6_decisions=p6, requirement_matches=_p7()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P6_APPROVAL_REQUIRED"


def test_p8_reports_missing_p7_requirements() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="sold_vs_collected_gap", p6_decisions=_p6(), requirement_matches=_p7(status="MISSING_REQUIREMENTS")
    )
    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.reason == "REQUIREMENTS_NOT_MATCHED"
    assert decision.missing_role_groups == (("collected_amount",),)


def test_p8_does_not_infer_unknown_capability() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_p8", requested_capability="invented_magic", p6_decisions=_p6(), requirement_matches=_p7()
    )
    assert decision.status == STATUS_UNSUPPORTED_CAPABILITY
    assert decision.reason == "CAPABILITY_NOT_GOVERNED"


def test_governed_input_requires_exact_source_binding_coverage() -> None:
    try:
        Service1GovernedComputationInputV1(
            case_id="case_p8",
            requested_capability="sold_vs_collected_gap",
            family_id="CASH_COLLECTIONS",
            pathology_code="LIQ_001",
            formula_id="LIQ_001_vendido_cobrado",
            formula_expression="sold_amount - collected_amount",
            required_variables=("sold_amount", "collected_amount"),
            required_evidence=(),
            source_bindings={"sold_amount": "venta_total"},
            grain={}, catalog_versions={}, provenance={},
        )
    except ValueError as exc:
        assert "source_bindings" in str(exc)
    else:
        raise AssertionError("incomplete governed source bindings must fail closed")


def test_p8_makes_net_margin_real_computable_from_exact_period_bindings() -> None:
    decision = build_service_1_computability_decision_v1(
        case_id="case_period_net_margin",
        requested_capability="net_margin_real",
        p6_decisions=_period_net_margin_p6(),
        requirement_matches=_period_net_margin_p7(),
    )

    assert decision.status == STATUS_COMPUTABLE
    assert decision.family_id == "PERIOD_NET_MARGIN"
    assert decision.governed_computation_input is not None
    assert dict(decision.governed_computation_input.source_bindings) == {
        "sale_price": "ventas_periodo",
        "costs": "cmv_total",
        "taxes": "impuestos_periodo",
    }
    assert decision.governed_computation_input.grain == {
        "structural_scope": "SHEET",
        "business_entity_grain": "NONE",
        "temporal_grain": "PERIOD",
        "aggregation_grain": "AGGREGATED",
    }


def test_p8_needs_evidence_when_period_net_margin_taxes_are_missing() -> None:
    p6 = _period_net_margin_p6()[:-1]
    decision = build_service_1_computability_decision_v1(
        case_id="case_period_net_margin",
        requested_capability="net_margin_real",
        p6_decisions=p6,
        requirement_matches=_period_net_margin_p7(status="MISSING_REQUIREMENTS"),
    )

    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.reason == "REQUIREMENTS_NOT_MATCHED"
    assert decision.missing_role_groups == (("period_taxes_total",),)


def test_ren_001_traverses_p6_p7_p8_from_column_understanding_without_monkeypatch() -> None:
    headers = ("ventas_periodo", "cmv_total", "impuestos_periodo")
    p6 = []
    for header in headers:
        understanding = build_column_understanding_v1(
            column_name=header,
            sheet_name="Resumen_periodo",
            sample_values=[1000, 2000],
            inferred_data_type="number",
            co_column_names=headers,
        )
        primary = understanding.primary_hypothesis
        assert primary is not None
        candidate = Service1ColumnSemanticCandidateV1(
            source_column_name=understanding.column_name,
            normalized_column_name=understanding.normalized_header,
            sheet_name=understanding.sheet_name,
            observed_data_type=understanding.inferred_data_type,
            sample_values=understanding.sample_values,
            candidate_semantic_roles=tuple(
                item.semantic_role for item in understanding.candidate_meanings
            ),
            candidate_variable_names=tuple(
                item.variable_name for item in understanding.candidate_meanings
            ),
            confidence=understanding.confidence,
            ambiguity_reason=None,
            owner_confirmation_required=understanding.owner_question_needed,
            metadata={
                "column_ref_id": f"{understanding.sheet_name}::{understanding.column_name}",
                "primary_semantic_role": primary.semantic_role,
            },
        )
        p6.append(
            build_service_1_p6_approval_decision_v1(
                case_id="case_period_net_margin",
                candidate=candidate,
            )
        )

    assert all(decision.status == STATUS_APPROVED for decision in p6)
    assert [(decision.approved_role, decision.approved_variable) for decision in p6] == [
        ("period_sales_total", "sale_price"),
        ("period_costs_total", "costs"),
        ("period_taxes_total", "taxes"),
    ]

    p7 = build_service_1_requirement_matches_v1(p6)
    period_net_margin = next(
        match for match in p7 if match.family_id == FAMILY_PERIOD_NET_MARGIN
    )
    assert period_net_margin.status == P7_STATUS_MATCHED

    decision = build_service_1_computability_decision_v1(
        case_id="case_period_net_margin",
        requested_capability="net_margin_real",
        p6_decisions=[item.to_dict() for item in p6],
        requirement_matches=[item.to_dict() for item in p7],
    )
    assert decision.status == STATUS_COMPUTABLE
    assert decision.governed_computation_input is not None
    assert dict(decision.governed_computation_input.source_bindings) == {
        "sale_price": "ventas_periodo",
        "costs": "cmv_total",
        "taxes": "impuestos_periodo",
    }
