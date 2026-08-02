from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    Service1P6ApprovalDecisionV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_PERIOD_NET_MARGIN,
    FAMILY_SALES_MARGIN,
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    P7_STATUS_NOT_OBSERVED,
    Service1GrainV1,
    Service1RequirementMatchV1,
    build_service_1_requirement_matches_v1,
    project_service_1_requirement_matches_to_variable_family_bindings_v1,
)


def _p6(column: str, role: str, *, status: str = STATUS_APPROVED) -> Service1P6ApprovalDecisionV1:
    return Service1P6ApprovalDecisionV1(
        case_id="case_p7",
        sheet_ref="Ventas",
        column_ref=column,
        status=status,
        approved_role=(role if status == STATUS_APPROVED else None),
        approved_variable=(role if status == STATUS_APPROVED else None),
        reason="test",
        confidence=0.95,
        provenance={"candidate_ref": column},
    )


def _by_family(matches: tuple[Service1RequirementMatchV1, ...]) -> dict[str, Service1RequirementMatchV1]:
    return {match.family_id: match for match in matches}


def test_grain_contract_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="structural_scope"):
        Service1GrainV1("FILE", "NONE", "NONE", "ATOMIC")


def test_sales_margin_requirement_match_consumes_only_p6_approved_roles() -> None:
    matches = build_service_1_requirement_matches_v1(
        [
            _p6("Producto", "product_name"),
            _p6("Cantidad", "quantity"),
            _p6("Precio", "unit_sale_price"),
            _p6("Costo", "unit_cost_candidate"),
        ]
    )
    margin = _by_family(matches)[FAMILY_SALES_MARGIN]

    assert margin.status == P7_STATUS_MATCHED
    assert margin.missing_role_groups == ()
    assert set(margin.approved_roles) >= {
        "product_name",
        "quantity",
        "unit_sale_price",
        "unit_cost_candidate",
    }
    assert margin.grain.structural_scope == "REGION"
    assert margin.grain.aggregation_grain == "ATOMIC"
    assert margin.provenance["source"] == "P6_APPROVAL_DECISIONS"
    assert margin.runtime_authorized is False
    assert margin.tool_execution_authorized is False


def test_partial_p6_approved_roles_report_missing_requirements_without_computability() -> None:
    matches = build_service_1_requirement_matches_v1([_p6("Precio", "unit_sale_price")])
    margin = _by_family(matches)[FAMILY_SALES_MARGIN]

    assert margin.status == P7_STATUS_MISSING_REQUIREMENTS
    assert ("quantity",) in margin.missing_role_groups
    assert ("unit_cost_candidate",) in margin.missing_role_groups
    payload = margin.to_dict()
    assert "formula_id" not in payload
    assert "computation_candidate_ready" not in payload


def test_p7_rejects_non_approved_p6_decision() -> None:
    with pytest.raises(ValueError, match="APPROVED P6"):
        build_service_1_requirement_matches_v1(
            [_p6("Precio", "unit_sale_price", status=STATUS_NEEDS_OWNER_CONFIRMATION)]
        )


def test_legacy_variable_family_binding_is_projection_of_requirement_match() -> None:
    matches = build_service_1_requirement_matches_v1(
        [
            _p6("Producto", "product_name"),
            _p6("Cantidad", "quantity"),
            _p6("Precio", "unit_sale_price"),
            _p6("Costo", "unit_cost_candidate"),
        ]
    )
    projected = project_service_1_requirement_matches_to_variable_family_bindings_v1(matches)
    margin = next(binding for binding in projected if binding.family_id == FAMILY_SALES_MARGIN)

    assert margin.metadata["compatibility_projection"] is True
    assert margin.metadata["canonical_source"] == "Service1RequirementMatchV1"
    assert margin.runtime_authorized is False


def test_requirement_matching_is_deterministic() -> None:
    decisions = [
        _p6("Producto", "product_name"),
        _p6("Cantidad", "quantity"),
        _p6("Precio", "unit_sale_price"),
        _p6("Costo", "unit_cost_candidate"),
    ]
    assert build_service_1_requirement_matches_v1(decisions) == build_service_1_requirement_matches_v1(decisions)


def test_period_net_margin_requirement_match_uses_declared_period_aggregate_grain() -> None:
    matches = build_service_1_requirement_matches_v1(
        [
            _p6("ventas_periodo", "period_sales_total"),
            _p6("cmv_total", "period_costs_total"),
            _p6("impuestos_periodo", "period_taxes_total"),
        ]
    )
    margin = _by_family(matches)[FAMILY_PERIOD_NET_MARGIN]

    assert margin.status == P7_STATUS_MATCHED
    assert margin.target_capabilities == ("net_margin_real",)
    assert margin.grain == Service1GrainV1("SHEET", "NONE", "PERIOD", "AGGREGATED")
    assert margin.runtime_authorized is False
    assert margin.tool_execution_authorized is False
    assert margin.delivery_authorized is False
    assert margin.diagnosis_generated is False


def test_period_net_margin_reports_missing_taxes_without_changing_sales_margin() -> None:
    matches = build_service_1_requirement_matches_v1(
        [
            _p6("ventas_periodo", "period_sales_total"),
            _p6("cmv_total", "period_costs_total"),
        ]
    )
    by_family = _by_family(matches)

    assert by_family[FAMILY_PERIOD_NET_MARGIN].status == P7_STATUS_MISSING_REQUIREMENTS
    assert by_family[FAMILY_PERIOD_NET_MARGIN].missing_role_groups == (("period_taxes_total",),)
    assert by_family[FAMILY_SALES_MARGIN].status == P7_STATUS_NOT_OBSERVED
