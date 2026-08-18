from __future__ import annotations

import inspect

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_ANALYSIS,
    Service1GovernedAnalysisInputV1,
    build_service_1_analysis_computability_decision_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_MATCHED,
    Service1AnalysisRequirementMatchV1,
    Service1GrainV1,
    build_service_1_analysis_requirement_match_v1,
)


def _p6(*roles: str, case_id: str = "case_f5") -> tuple[Service1P6ApprovalDecisionV1, ...]:
    return tuple(
        Service1P6ApprovalDecisionV1(
            case_id=case_id,
            sheet_ref="Ventas",
            column_ref=f"col_{index}_{role}",
            status=STATUS_APPROVED,
            approved_role=role,
            approved_variable=role,
            reason="TEST_APPROVED",
            provenance={"source": "f5_test"},
        )
        for index, role in enumerate(roles)
    )


def _plan(
    *,
    analysis_id: str,
    kind: AnalysisKind,
    dimensions: tuple[str, ...],
    business: str,
    temporal: str,
    aggregation: str,
    measures: tuple[str, ...] = ("sales",),
    relationship_refs: tuple[str, ...] = (),
) -> Service1AnalysisPlanV1:
    order_by: tuple[Service1AnalysisOrderByV1, ...] = ()
    if kind is AnalysisKind.SERIES:
        order_by = (Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),)
    elif kind is AnalysisKind.RANKED:
        order_by = (Service1AnalysisOrderByV1(field_ref="sales", direction="DESC"),)
    return Service1AnalysisPlanV1(
        analysis_id=analysis_id,
        kind=kind,
        measures=measures,
        dimensions=dimensions,
        relationship_refs=relationship_refs,
        requested_grain=Service1RequestedAnalysisGrainV1(
            business_entity_grain=business,
            temporal_grain=temporal,
            aggregation_grain=aggregation,
        ),
        order_by=order_by,
    )


def _p7(plan: Service1AnalysisPlanV1, p6: tuple[Service1P6ApprovalDecisionV1, ...]) -> Service1AnalysisRequirementMatchV1:
    return build_service_1_analysis_requirement_match_v1(plan, p6)


def _decide(
    plan: Service1AnalysisPlanV1,
    p6: tuple[Service1P6ApprovalDecisionV1, ...],
    *,
    relationships: dict | None = None,
):
    return build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=_p7(plan, p6),
        relationship_bindings=relationships,
    )


def test_sales_total_is_computable_without_execution_authority() -> None:
    plan = _plan(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
    )
    decision = _decide(plan, _p6("sales_amount"))

    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_analysis_input
    assert isinstance(governed, Service1GovernedAnalysisInputV1)
    assert dict(governed.source_bindings) == {"sales_amount": "col_0_sales_amount"}
    assert governed.grain == Service1GrainV1("REGION", "NONE", "PERIOD", "AGGREGATED")
    assert governed.formula_refs == ()
    payload = governed.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["analysis_execution_authorized"] is False
    assert "AGGREGATION_RUNTIME_DEFERRED_TO_F8" in payload["safety_flags"]


def test_grouped_product_and_branch_are_computable_from_p7_resolved_grain() -> None:
    product = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    product_decision = _decide(product, _p6("sales_amount", "product_identifier"))
    assert product_decision.status == STATUS_COMPUTABLE
    assert product_decision.governed_analysis_input is not None
    assert product_decision.governed_analysis_input.grain.business_entity_grain == "PRODUCT"

    branch = _plan(
        analysis_id="sales_by_branch",
        kind=AnalysisKind.GROUPED,
        dimensions=("branch",),
        business="BRANCH",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    branch_decision = _decide(branch, _p6("sales_amount", "branch_identifier"))
    assert branch_decision.status == STATUS_COMPUTABLE
    assert branch_decision.governed_analysis_input is not None
    assert branch_decision.governed_analysis_input.grain.business_entity_grain == "BRANCH"


def test_series_and_ranked_kinds_can_be_declared_computable_without_execution() -> None:
    series = _plan(
        analysis_id="sales_series_by_day",
        kind=AnalysisKind.SERIES,
        dimensions=("time",),
        business="NONE",
        temporal="DAY",
        aggregation="GROUPED",
    )
    series_decision = _decide(series, _p6("sales_amount", "operation_date"))
    assert series_decision.status == STATUS_COMPUTABLE
    assert series_decision.governed_analysis_input is not None
    assert series_decision.governed_analysis_input.grain.temporal_grain == "DAY"

    ranked = _plan(
        analysis_id="sales_ranked_by_product",
        kind=AnalysisKind.RANKED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    ranked_decision = _decide(ranked, _p6("sales_amount", "product_identifier"))
    assert ranked_decision.status == STATUS_COMPUTABLE
    assert ranked_decision.governed_analysis_input is not None
    assert ranked_decision.governed_analysis_input.analysis_plan.kind is AnalysisKind.RANKED


def test_missing_p7_requirements_becomes_needs_evidence() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    decision = _decide(plan, _p6("sales_amount"))

    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.governed_analysis_input is None
    assert decision.missing_role_groups == (("product_identifier", "product_name"),)


def test_unsupported_measure_is_classified_unsupported_not_executed() -> None:
    plan = _plan(
        analysis_id="magic_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        measures=("magic_measure",),
    )
    p6 = _p6("sales_amount", "product_identifier")
    p7_match = _p7(plan, p6)
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=p7_match,
    )

    assert decision.status == STATUS_UNSUPPORTED_ANALYSIS
    assert decision.governed_analysis_input is None
    assert decision.reason is not None and decision.reason.startswith("UNSUPPORTED_ANALYSIS_")


def test_required_relationship_without_confirmed_binding_needs_evidence() -> None:
    plan = _plan(
        analysis_id="sales_by_product_joined",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=("sales_to_products",),
    )
    p6 = _p6("sales_amount", "product_identifier")
    decision = _decide(plan, p6)

    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.missing_relationship_refs == ("sales_to_products",)
    assert decision.governed_analysis_input is None


def test_confirmed_relationship_is_carried_as_evidence_not_resolved_join() -> None:
    plan = _plan(
        analysis_id="sales_by_product_joined",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=("sales_to_products",),
    )
    p6 = _p6("sales_amount", "product_identifier")
    decision = _decide(
        plan,
        p6,
        relationships={
            "sales_to_products": {
                "relationship_ref": "sales_to_products",
                "confirmed_by_owner": True,
                "left_ref": "Ventas.ProductoID",
                "right_ref": "Productos.ProductoID",
            }
        },
    )

    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_analysis_input
    assert governed is not None
    assert governed.relationship_bindings["sales_to_products"]["confirmed_by_owner"] is True
    assert governed.provenance["relationship_resolution_performed"] is False
    assert governed.to_dict()["analysis_execution_authorized"] is False


def test_unconfirmed_or_undeclared_relationship_fails_closed() -> None:
    plan = _plan(
        analysis_id="sales_by_product_joined",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=("sales_to_products",),
    )
    p6 = _p6("sales_amount", "product_identifier")
    unconfirmed = _decide(
        plan,
        p6,
        relationships={"sales_to_products": {"confirmed_by_owner": False}},
    )
    assert unconfirmed.status == STATUS_NEEDS_EVIDENCE
    assert unconfirmed.reason == "RELATIONSHIP_OWNER_CONFIRMATION_REQUIRED"

    no_relationship_plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    extra = _decide(
        no_relationship_plan,
        p6,
        relationships={"undeclared": {"confirmed_by_owner": True}},
    )
    assert extra.status == STATUS_BLOCKED
    assert extra.reason == "UNDECLARED_RELATIONSHIP_BINDING"


def test_p7_grain_drift_is_blocked_by_p8() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    p6 = _p6("sales_amount", "product_identifier")
    match = _p7(plan, p6)
    assert match.status == P7_STATUS_MATCHED
    drifted = Service1AnalysisRequirementMatchV1(
        analysis_id=match.analysis_id,
        status=match.status,
        reason=None,
        required_role_groups=match.required_role_groups,
        satisfied_role_groups=match.satisfied_role_groups,
        missing_role_groups=match.missing_role_groups,
        approved_roles=match.approved_roles,
        source_columns=match.source_columns,
        requested_grain=match.requested_grain,
        resolved_grain=Service1GrainV1("REGION", "BRANCH", "PERIOD", "GROUPED"),
        required_relationship_refs=match.required_relationship_refs,
        provenance={"source": "drift_test"},
    )
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=drifted,
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P7_RESOLVED_GRAIN_DRIFT"


def test_ambiguous_role_group_and_duplicate_role_sources_are_blocked() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    both_alternatives = _p6("sales_amount", "product_identifier", "product_name")
    alternative_decision = _decide(plan, both_alternatives)
    assert alternative_decision.status == STATUS_BLOCKED
    assert alternative_decision.reason == "AMBIGUOUS_ANALYSIS_ROLE_GROUP"

    duplicate_role_sources = (
        *_p6("sales_amount", "product_identifier"),
        Service1P6ApprovalDecisionV1(
            case_id="case_f5",
            sheet_ref="Otra",
            column_ref="second_sales_column",
            status=STATUS_APPROVED,
            approved_role="sales_amount",
            approved_variable="sales_amount",
            reason="TEST_APPROVED",
            provenance={"source": "f5_test"},
        ),
    )
    duplicate_decision = _decide(plan, duplicate_role_sources)
    assert duplicate_decision.status == STATUS_BLOCKED
    assert duplicate_decision.reason == "AMBIGUOUS_ANALYSIS_SOURCE_COLUMN"


def test_p6_case_mismatch_is_blocked() -> None:
    plan = _plan(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
    )
    p6 = _p6("sales_amount", case_id="other_case")
    p7_match = _p7(plan, p6)
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=p7_match,
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P6_CASE_MISMATCH"


def test_analysis_p8_builder_contains_no_execution_or_math_call() -> None:
    source = inspect.getsource(build_service_1_analysis_computability_decision_v1)
    assert "FormulaEngineService" not in source
    assert "calculate_formula" not in source
    assert "execute_generic_capability" not in source
    assert "service_1_product_pipeline_v1" not in source
    assert "SUM(" not in source
    assert "AVG(" not in source
    assert "RANK(" not in source


def test_gross_margin_by_product_is_computable_when_cost_and_relationship_evidence_exist() -> None:
    plan = _plan(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        measures=("gross_margin",),
        relationship_refs=("sales_to_products",),
    )
    p6 = _p6("sales_amount", "quantity", "unit_cost_candidate", "product_identifier")
    decision = _decide(
        plan,
        p6,
        relationships={
            "sales_to_products": {
                "relationship_ref": "sales_to_products",
                "confirmed_by_owner": True,
            }
        },
    )

    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_analysis_input
    assert governed is not None
    assert governed.formula_refs == ("margen_bruto",)
    assert set(governed.source_bindings) == {"sales_amount", "quantity", "unit_cost_candidate", "product_identifier"}
    assert governed.to_dict()["analysis_execution_authorized"] is False


def test_dso_analysis_needs_evidence_when_receivables_and_period_are_missing() -> None:
    plan = _plan(
        analysis_id="dso_analysis",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
        measures=("dso",),
    )
    decision = _decide(plan, _p6("sales_amount"))

    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.governed_analysis_input is None
    assert ("accounts_receivable_amount",) in decision.missing_role_groups
    assert ("period_days", "days") in decision.missing_role_groups


def test_projected_cash_balance_needs_evidence_when_cash_inputs_are_incomplete() -> None:
    plan = _plan(
        analysis_id="projected_cash_balance",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
        measures=("projected_cash_balance",),
    )
    decision = _decide(plan, _p6("initial_balance"))

    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.governed_analysis_input is None
    assert ("expected_collections",) in decision.missing_role_groups
    assert ("expected_payments",) in decision.missing_role_groups


def test_p7_structural_grain_drift_is_blocked() -> None:
    plan = _plan(
        analysis_id="sales_by_product_structural_drift",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    p6 = _p6("sales_amount", "product_identifier")
    match = _p7(plan, p6)
    drifted = Service1AnalysisRequirementMatchV1(
        analysis_id=match.analysis_id,
        status=match.status,
        reason=None,
        required_role_groups=match.required_role_groups,
        satisfied_role_groups=match.satisfied_role_groups,
        missing_role_groups=match.missing_role_groups,
        approved_roles=match.approved_roles,
        source_columns=match.source_columns,
        requested_grain=match.requested_grain,
        resolved_grain=Service1GrainV1("SHEET", "PRODUCT", "PERIOD", "GROUPED"),
        required_relationship_refs=match.required_relationship_refs,
        provenance={"source": "structural_drift_test"},
    )
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=drifted,
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P7_RESOLVED_GRAIN_DRIFT"


def test_relationship_evidence_cannot_inject_runtime_authority() -> None:
    plan = _plan(
        analysis_id="sales_by_product_relation_authority",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=("sales_to_products",),
    )
    p6 = _p6("sales_amount", "product_identifier")
    decision = _decide(
        plan,
        p6,
        relationships={
            "sales_to_products": {
                "relationship_ref": "sales_to_products",
                "confirmed_by_owner": True,
                "runtime_authorized": True,
            }
        },
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "RELATIONSHIP_BINDING_AUTHORITY_FORBIDDEN"


def test_p6_case_mismatch_blocks_before_needs_evidence_classification() -> None:
    plan = _plan(
        analysis_id="sales_by_product_wrong_case",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    p6 = _p6("sales_amount", case_id="other_case")
    p7_match = _p7(plan, p6)
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case_f5",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=p7_match,
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P6_CASE_MISMATCH"
