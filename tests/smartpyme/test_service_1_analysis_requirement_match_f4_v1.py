from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
)
import pymia.smartpyme.service_1_variable_family_bindings_v1 as p7
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_BLOCKED,
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    Service1GrainV1,
    build_service_1_analysis_requirement_match_v1,
)


def _p6(*roles: str) -> tuple[Service1P6ApprovalDecisionV1, ...]:
    return tuple(
        Service1P6ApprovalDecisionV1(
            case_id="case_f4",
            sheet_ref="Ventas",
            column_ref=f"col_{role}",
            status=STATUS_APPROVED,
            approved_role=role,
            approved_variable=role,
            reason="TEST_APPROVED",
            provenance={"source": "f4_test"},
        )
        for role in roles
    )


def _grain(*, business: str, temporal: str, aggregation: str) -> Service1RequestedAnalysisGrainV1:
    return Service1RequestedAnalysisGrainV1(
        business_entity_grain=business,
        temporal_grain=temporal,
        aggregation_grain=aggregation,
    )


def _plan(
    *,
    analysis_id: str,
    kind: AnalysisKind,
    dimensions: tuple[str, ...],
    business: str,
    temporal: str,
    aggregation: str,
    relationship_refs: tuple[str, ...] = (),
) -> Service1AnalysisPlanV1:
    order_by = (
        (Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),)
        if kind is AnalysisKind.SERIES
        else ()
    )
    return Service1AnalysisPlanV1(
        analysis_id=analysis_id,
        kind=kind,
        measures=("sales",),
        dimensions=dimensions,
        relationship_refs=relationship_refs,
        requested_grain=_grain(
            business=business,
            temporal=temporal,
            aggregation=aggregation,
        ),
        order_by=order_by,
    )


def test_sales_total_resolves_period_aggregated_grain() -> None:
    plan = _plan(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
    )
    result = build_service_1_analysis_requirement_match_v1(plan, _p6("sales_amount"))

    assert result.status == P7_STATUS_MATCHED
    assert result.required_role_groups == (("sales_amount",),)
    assert result.resolved_grain == Service1GrainV1(
        structural_scope="REGION",
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    )
    assert result.reason is None


def test_sales_by_product_resolves_product_grouped_grain() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "product_identifier"),
    )

    assert result.status == P7_STATUS_MATCHED
    assert ("product_identifier", "product_name") in result.required_role_groups
    assert result.resolved_grain is not None
    assert result.resolved_grain.business_entity_grain == "PRODUCT"


def test_sales_by_branch_resolves_branch_grouped_grain() -> None:
    plan = _plan(
        analysis_id="sales_by_branch",
        kind=AnalysisKind.GROUPED,
        dimensions=("branch",),
        business="BRANCH",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "branch_identifier"),
    )

    assert result.status == P7_STATUS_MATCHED
    assert result.resolved_grain is not None
    assert result.resolved_grain.business_entity_grain == "BRANCH"


def test_sales_by_hour_requires_operation_time() -> None:
    plan = _plan(
        analysis_id="sales_by_hour",
        kind=AnalysisKind.SERIES,
        dimensions=("time",),
        business="NONE",
        temporal="HOUR",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "operation_time"),
    )

    assert result.status == P7_STATUS_MATCHED
    assert ("operation_time",) in result.required_role_groups
    assert result.resolved_grain is not None
    assert result.resolved_grain.temporal_grain == "HOUR"


def test_sales_by_product_missing_product_role_has_no_resolved_grain() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(plan, _p6("sales_amount"))

    assert result.status == P7_STATUS_MISSING_REQUIREMENTS
    assert result.resolved_grain is None
    assert result.missing_role_groups == (("product_identifier", "product_name"),)


def test_sales_channel_never_satisfies_branch_dimension() -> None:
    plan = _plan(
        analysis_id="sales_by_branch",
        kind=AnalysisKind.GROUPED,
        dimensions=("branch",),
        business="BRANCH",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "sales_channel"),
    )

    assert result.status == P7_STATUS_MISSING_REQUIREMENTS
    assert result.resolved_grain is None
    assert ("branch_identifier", "branch_name") in result.missing_role_groups
    assert "sales_channel" not in result.approved_roles


def test_relationship_refs_are_requirements_only() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=("sales_to_products",),
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "product_identifier"),
    )

    assert result.status == P7_STATUS_MATCHED
    assert result.required_relationship_refs == ("sales_to_products",)
    assert result.provenance["relationship_resolution_authorized"] is False
    payload = result.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["tool_execution_authorized"] is False
    assert payload["delivery_authorized"] is False
    assert payload["diagnosis_generated"] is False


def test_cross_grain_product_branch_is_generic_and_resolved() -> None:
    plan = _plan(
        analysis_id="sales_by_product_branch",
        kind=AnalysisKind.GROUPED,
        dimensions=("product", "branch"),
        business="PRODUCT+BRANCH",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "product_identifier", "branch_identifier"),
    )

    assert result.status == P7_STATUS_MATCHED
    assert result.resolved_grain is not None
    assert result.resolved_grain.business_entity_grain == "PRODUCT+BRANCH"


def test_invalid_composite_grain_fails_closed() -> None:
    with pytest.raises(ValueError, match="invalid business_entity_grain"):
        Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain="PRODUCT+MAGIC",
            temporal_grain="PERIOD",
            aggregation_grain="GROUPED",
        )

    plan = _plan(
        analysis_id="bad_cross_grain",
        kind=AnalysisKind.GROUPED,
        dimensions=("product", "branch"),
        business="PRODUCT+MAGIC",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    result = build_service_1_analysis_requirement_match_v1(
        plan,
        _p6("sales_amount", "product_identifier", "branch_identifier"),
    )
    assert result.status == P7_STATUS_BLOCKED
    assert result.resolved_grain is None
    assert result.reason is not None and result.reason.startswith("INVALID_REQUESTED_GRAIN:")


def test_p7_analysis_match_adds_no_math_computability_or_execution_authority() -> None:
    source = inspect.getsource(p7)
    assert "FormulaEngineService" not in source
    assert "service_1_computability_v1" not in source
    assert "service_1_product_pipeline_v1" not in source
