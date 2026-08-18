from __future__ import annotations

from dataclasses import replace
import inspect

import pytest

from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    Service1PreparedAnalysisEvidenceV1,
    Service1PreparedGroupV1,
    Service1PreparedRelationshipV1,
    Service1PreparedRowV1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    Service1AnalysisMathResultV1,
    Service1ExecutedGroupV1,
    Service1ExecutedMeasureV1,
)
from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
import pymia.smartpyme.service_1_analysis_result_projection_v1 as f9
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_service_1_analysis_result_projection_v1,
    verify_service_1_finding_integrity_v1,
    verify_service_1_result_set_integrity_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1


def _plan(
    *,
    analysis_id: str = "sales_total",
    kind: AnalysisKind = AnalysisKind.SINGLE_VALUE,
    measures: tuple[str, ...] = ("sales",),
    dimensions: tuple[str, ...] = (),
    business: str = "NONE",
    temporal: str = "PERIOD",
    aggregation: str = "AGGREGATED",
    order_by: tuple[Service1AnalysisOrderByV1, ...] = (),
    limit: int | None = None,
) -> Service1AnalysisPlanV1:
    return Service1AnalysisPlanV1(
        analysis_id=analysis_id,
        kind=kind,
        measures=measures,
        dimensions=dimensions,
        relationship_refs=(),
        requested_grain=Service1RequestedAnalysisGrainV1(
            business_entity_grain=business,
            temporal_grain=temporal,
            aggregation_grain=aggregation,
        ),
        order_by=order_by,
        limit=limit,
    )


def _grain(plan: Service1AnalysisPlanV1) -> Service1GrainV1:
    return Service1GrainV1(
        structural_scope="REGION",
        business_entity_grain=plan.requested_grain.business_entity_grain,
        temporal_grain=plan.requested_grain.temporal_grain,
        aggregation_grain=plan.requested_grain.aggregation_grain,
    )


def _prepared_sales_total() -> Service1PreparedAnalysisEvidenceV1:
    plan = _plan()
    rows = (
        Service1PreparedRowV1(
            row_ref="Ventas!row:2",
            base_sheet_ref="Ventas",
            role_values={"sales_amount": "100"},
            role_source_refs={"sales_amount": "Ventas.VentaTotal"},
            source_row_refs=("Ventas!row:2",),
            provenance={"source": "test"},
        ),
        Service1PreparedRowV1(
            row_ref="Ventas!row:3",
            base_sheet_ref="Ventas",
            role_values={"sales_amount": "200"},
            role_source_refs={"sales_amount": "Ventas.VentaTotal"},
            source_row_refs=("Ventas!row:3",),
            provenance={"source": "test"},
        ),
    )
    return Service1PreparedAnalysisEvidenceV1(
        case_id="case-f9",
        analysis_id=plan.analysis_id,
        analysis_plan=plan,
        grain=_grain(plan),
        source_sheet_refs=("Ventas",),
        prepared_rows=rows,
        groups=(
            Service1PreparedGroupV1(
                group_ref="group:ALL",
                key={},
                member_row_refs=("Ventas!row:2", "Ventas!row:3"),
            ),
        ),
        provenance={"source": "test"},
    )


def _math_sales_total(*, value: float = 300.0) -> Service1AnalysisMathResultV1:
    measure = Service1ExecutedMeasureV1(
        measure_ref="sales",
        value=value,
        unit="currency",
        formula_ref=None,
        formula_inputs={"sales": value},
        source_refs=("Ventas.VentaTotal@Ventas!row:2", "Ventas.VentaTotal@Ventas!row:3"),
        math_trace=(
            {
                "input_name": "sales",
                "operation": "SUM",
                "primary_role": "sales_amount",
                "paired_role": None,
                "value": value,
                "source_refs": ["Ventas.VentaTotal@Ventas!row:2", "Ventas.VentaTotal@Ventas!row:3"],
            },
        ),
    )
    return Service1AnalysisMathResultV1(
        case_id="case-f9",
        analysis_id="sales_total",
        groups=(
            Service1ExecutedGroupV1(
                group_ref="group:ALL",
                key={},
                measures={"sales": measure},
                member_row_refs=("Ventas!row:2", "Ventas!row:3"),
            ),
        ),
        provenance={"source": "test"},
    )


def _prepared_grouped_margin() -> Service1PreparedAnalysisEvidenceV1:
    plan = Service1AnalysisPlanV1(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        measures=("gross_margin",),
        dimensions=("product",),
        relationship_refs=("Ventas.ProductoID->Productos.ProductoID",),
        requested_grain=Service1RequestedAnalysisGrainV1(
            business_entity_grain="PRODUCT",
            temporal_grain="PERIOD",
            aggregation_grain="GROUPED",
        ),
    )
    rows = (
        Service1PreparedRowV1(
            row_ref="Ventas!row:2",
            base_sheet_ref="Ventas",
            role_values={"sales_amount": "200", "quantity": "2", "unit_cost_candidate": "60", "product_identifier": "P1"},
            role_source_refs={
                "sales_amount": "Ventas.VentaTotal",
                "quantity": "Ventas.Cantidad",
                "unit_cost_candidate": "Productos.CostoUnitario",
                "product_identifier": "Ventas.ProductoID",
            },
            source_row_refs=("Ventas!row:2", "Productos!row:2"),
            relationship_refs=("Ventas.ProductoID->Productos.ProductoID",),
            provenance={"source": "test"},
        ),
        Service1PreparedRowV1(
            row_ref="Ventas!row:3",
            base_sheet_ref="Ventas",
            role_values={"sales_amount": "150", "quantity": "1", "unit_cost_candidate": "100", "product_identifier": "P2"},
            role_source_refs={
                "sales_amount": "Ventas.VentaTotal",
                "quantity": "Ventas.Cantidad",
                "unit_cost_candidate": "Productos.CostoUnitario",
                "product_identifier": "Ventas.ProductoID",
            },
            source_row_refs=("Ventas!row:3", "Productos!row:3"),
            relationship_refs=("Ventas.ProductoID->Productos.ProductoID",),
            provenance={"source": "test"},
        ),
    )
    return Service1PreparedAnalysisEvidenceV1(
        case_id="case-f9",
        analysis_id=plan.analysis_id,
        analysis_plan=plan,
        grain=_grain(plan),
        source_sheet_refs=("Ventas", "Productos"),
        prepared_rows=rows,
        groups=(
            Service1PreparedGroupV1(group_ref="group:product=P1", key={"product": "P1"}, member_row_refs=("Ventas!row:2",)),
            Service1PreparedGroupV1(group_ref="group:product=P2", key={"product": "P2"}, member_row_refs=("Ventas!row:3",)),
        ),
        materialized_relationships=(
            Service1PreparedRelationshipV1(
                relationship_ref="Ventas.ProductoID->Productos.ProductoID",
                relationship_kind="MANY_TO_ONE",
                left_sheet_ref="Ventas",
                right_sheet_ref="Productos",
                materialized_pairs=(("Ventas!row:2", "Productos!row:2"), ("Ventas!row:3", "Productos!row:3")),
            ),
        ),
        provenance={"source": "test"},
    )


def _margin_measure(value: float, sales_ref: str, quantity_ref: str, cost_ref: str) -> Service1ExecutedMeasureV1:
    return Service1ExecutedMeasureV1(
        measure_ref="gross_margin",
        value=value,
        unit="ratio",
        formula_ref="margen_bruto",
        formula_inputs={"ventas": 200.0, "costos": 120.0},
        source_refs=(sales_ref, quantity_ref, cost_ref),
        math_trace=(
            {"input_name": "ventas", "operation": "SUM", "value": 200.0, "source_refs": [sales_ref]},
            {"input_name": "costos", "operation": "SUM_PRODUCT", "value": 120.0, "source_refs": [quantity_ref, cost_ref]},
            {"operation": "FORMULA", "formula_ref": "margen_bruto", "value": value, "source_refs": [sales_ref, quantity_ref, cost_ref]},
        ),
    )


def _math_grouped_margin() -> Service1AnalysisMathResultV1:
    return Service1AnalysisMathResultV1(
        case_id="case-f9",
        analysis_id="gross_margin_by_product",
        groups=(
            Service1ExecutedGroupV1(
                group_ref="group:product=P1",
                key={"product": "P1"},
                measures={
                    "gross_margin": _margin_measure(
                        0.4,
                        "Ventas.VentaTotal@Ventas!row:2",
                        "Ventas.Cantidad@Ventas!row:2",
                        "Productos.CostoUnitario@Ventas!row:2",
                    )
                },
                member_row_refs=("Ventas!row:2",),
            ),
            Service1ExecutedGroupV1(
                group_ref="group:product=P2",
                key={"product": "P2"},
                measures={
                    "gross_margin": _margin_measure(
                        1 / 3,
                        "Ventas.VentaTotal@Ventas!row:3",
                        "Ventas.Cantidad@Ventas!row:3",
                        "Productos.CostoUnitario@Ventas!row:3",
                    )
                },
                member_row_refs=("Ventas!row:3",),
            ),
        ),
        provenance={"source": "test"},
    )


def _prepared_ranked() -> Service1PreparedAnalysisEvidenceV1:
    plan = _plan(
        analysis_id="top_products",
        kind=AnalysisKind.RANKED,
        measures=("sales",),
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales", direction="DESC"),),
        limit=2,
    )
    rows = (
        Service1PreparedRowV1(
            row_ref="Ventas!row:2", base_sheet_ref="Ventas",
            role_values={"sales_amount": "100", "product_identifier": "P1"},
            role_source_refs={"sales_amount": "Ventas.VentaTotal", "product_identifier": "Ventas.ProductoID"},
            source_row_refs=("Ventas!row:2",), provenance={"source": "test"},
        ),
        Service1PreparedRowV1(
            row_ref="Ventas!row:3", base_sheet_ref="Ventas",
            role_values={"sales_amount": "200", "product_identifier": "P2"},
            role_source_refs={"sales_amount": "Ventas.VentaTotal", "product_identifier": "Ventas.ProductoID"},
            source_row_refs=("Ventas!row:3",), provenance={"source": "test"},
        ),
    )
    return Service1PreparedAnalysisEvidenceV1(
        case_id="case-f9", analysis_id=plan.analysis_id, analysis_plan=plan,
        grain=_grain(plan), source_sheet_refs=("Ventas",), prepared_rows=rows,
        groups=(
            Service1PreparedGroupV1(group_ref="group:product=P1", key={"product": "P1"}, member_row_refs=("Ventas!row:2",)),
            Service1PreparedGroupV1(group_ref="group:product=P2", key={"product": "P2"}, member_row_refs=("Ventas!row:3",)),
        ), provenance={"source": "test"},
    )


def _math_ranked() -> Service1AnalysisMathResultV1:
    def measure(row: int, value: float) -> Service1ExecutedMeasureV1:
        ref = f"Ventas.VentaTotal@Ventas!row:{row}"
        return Service1ExecutedMeasureV1(
            measure_ref="sales", value=value, unit="currency", formula_ref=None,
            formula_inputs={"sales": value}, source_refs=(ref,),
            math_trace=({"input_name": "sales", "operation": "SUM", "value": value, "source_refs": [ref]},),
        )
    return Service1AnalysisMathResultV1(
        case_id="case-f9", analysis_id="top_products",
        groups=(
            Service1ExecutedGroupV1(
                group_ref="group:product=P2", key={"product": "P2"},
                measures={"sales": measure(3, 200)}, member_row_refs=("Ventas!row:3",), rank=1,
            ),
            Service1ExecutedGroupV1(
                group_ref="group:product=P1", key={"product": "P1"},
                measures={"sales": measure(2, 100)}, member_row_refs=("Ventas!row:2",), rank=2,
            ),
        ), provenance={"source": "test"},
    )


def test_single_value_projects_typed_result_set_and_finding() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total(), currency_code="ARS"
    )
    assert decision.status == STATUS_READY
    projection = decision.projection
    assert projection is not None
    result_set = projection.result_set
    assert result_set.analysis_id == "sales_total"
    assert result_set.groups[0].measures["sales"].value == 300.0
    assert result_set.groups[0].measures["sales"].currency_code == "ARS"
    finding = projection.findings[0]
    assert finding.finding_id.startswith("finding:")
    assert finding.category == "ANALYTICAL_RESULT"
    assert finding.entity_ref == "ALL"
    assert finding.metric_ref == "sales"
    assert finding.observed_value == 300.0
    assert finding.currency_code == "ARS"


def test_finding_does_not_invent_classification_severity_financial_impact_or_recommendation() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    finding = decision.projection.findings[0]  # type: ignore[union-attr]
    payload = finding.to_dict()
    assert finding.classification is None
    assert finding.severity is None
    assert finding.financial_impact is None
    assert payload["recommendation_generated"] is False
    assert payload["severity_assigned"] is False
    assert payload["financial_impact_inferred"] is False
    assert any("no currency code" in item.lower() for item in finding.limitations)


def test_grouped_margin_preserves_formula_and_relationship_evidence_chain() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_grouped_margin(), prepared_evidence=_prepared_grouped_margin()
    )
    assert decision.status == STATUS_READY
    findings = decision.projection.findings  # type: ignore[union-attr]
    first = findings[0]
    assert first.entity_ref == "product=P1"
    assert first.evidence_chain.formula_ref == "margen_bruto"
    assert first.evidence_chain.relationship_refs == ("Ventas.ProductoID->Productos.ProductoID",)
    assert "Ventas!row:2" in first.evidence_chain.member_row_refs
    assert any(item.get("operation") == "FORMULA" for item in first.evidence_chain.math_trace)
    result_set = decision.projection.result_set  # type: ignore[union-attr]
    assert result_set.relationship_refs == ("Ventas.ProductoID->Productos.ProductoID",)
    assert result_set.source_sheet_refs == ("Ventas", "Productos")


def test_ranked_result_preserves_rank_and_uses_ranked_category() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_ranked(), prepared_evidence=_prepared_ranked(), currency_code="ARS"
    )
    assert decision.status == STATUS_READY
    projection = decision.projection
    assert projection is not None
    assert [group.rank for group in projection.result_set.groups] == [1, 2]
    assert [finding.category for finding in projection.findings] == ["RANKED_ANALYTICAL_RESULT", "RANKED_ANALYTICAL_RESULT"]
    assert [finding.rank for finding in projection.findings] == [1, 2]


def test_finding_id_is_deterministic_for_same_governed_result() -> None:
    first = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    second = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    assert first.projection.findings[0].finding_id == second.projection.findings[0].finding_id  # type: ignore[union-attr]
    assert first.projection.outcome.outcome_id == second.projection.outcome.outcome_id  # type: ignore[union-attr]


def test_sha256_integrity_verifies_and_does_not_claim_authenticity() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    projection = decision.projection
    assert projection is not None
    finding = projection.findings[0]
    assert verify_service_1_finding_integrity_v1(finding) is True
    assert verify_service_1_result_set_integrity_v1(projection.result_set) is True
    assert finding.integrity.algorithm == "SHA-256"
    assert finding.integrity.authenticity_asserted is False
    assert finding.integrity.non_repudiation_asserted is False
    assert projection.result_set.integrity.authenticity_asserted is False


def test_tampered_finding_fails_integrity_without_recomputing_digest() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    finding = decision.projection.findings[0]  # type: ignore[union-attr]
    tampered = replace(finding, observed_value=finding.observed_value + 1)
    assert verify_service_1_finding_integrity_v1(tampered) is False


def test_tampered_result_set_fails_integrity_without_recomputing_digest() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    result_set = decision.projection.result_set  # type: ignore[union-attr]
    group = result_set.groups[0]
    measure = group.measures["sales"]
    changed_measure = replace(measure, value=999.0)
    changed_group = replace(group, measures={"sales": changed_measure})
    tampered = replace(result_set, groups=(changed_group,))
    assert verify_service_1_result_set_integrity_v1(tampered) is False


def test_invalid_currency_code_fails_closed() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total(), currency_code="PESO"
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "CURRENCY_CODE_INVALID"
    assert decision.projection is None


def test_case_and_analysis_drift_fail_closed() -> None:
    math_result = _math_sales_total()
    wrong_case = replace(math_result, case_id="other-case")
    case_decision = build_service_1_analysis_result_projection_v1(
        math_result=wrong_case, prepared_evidence=_prepared_sales_total()
    )
    assert case_decision.status == STATUS_BLOCKED
    assert case_decision.reason == "CASE_ID_DRIFT"

    wrong_analysis = replace(math_result, analysis_id="other-analysis")
    analysis_decision = build_service_1_analysis_result_projection_v1(
        math_result=wrong_analysis, prepared_evidence=_prepared_sales_total()
    )
    assert analysis_decision.status == STATUS_BLOCKED
    assert analysis_decision.reason == "ANALYSIS_ID_DRIFT"


def test_group_key_drift_fails_closed() -> None:
    math_result = _math_sales_total()
    wrong_group = replace(math_result.groups[0], key={"unexpected": "x"})
    decision = build_service_1_analysis_result_projection_v1(
        math_result=replace(math_result, groups=(wrong_group,)), prepared_evidence=_prepared_sales_total()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "RESULT_GROUP_KEY_DRIFT:group:ALL"


def test_group_membership_drift_fails_closed() -> None:
    math_result = _math_sales_total()
    wrong_group = replace(math_result.groups[0], member_row_refs=("Ventas!row:2",))
    decision = build_service_1_analysis_result_projection_v1(
        math_result=replace(math_result, groups=(wrong_group,)), prepared_evidence=_prepared_sales_total()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "RESULT_GROUP_MEMBERSHIP_DRIFT:group:ALL"


def test_measure_set_drift_fails_closed() -> None:
    math_result = _math_sales_total()
    original = math_result.groups[0].measures["sales"]
    wrong_measure = replace(original, measure_ref="gross_margin")
    wrong_group = replace(math_result.groups[0], measures={"gross_margin": wrong_measure})
    decision = build_service_1_analysis_result_projection_v1(
        math_result=replace(math_result, groups=(wrong_group,)), prepared_evidence=_prepared_sales_total()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "RESULT_MEASURE_SET_DRIFT:group:ALL"


def test_outcome_is_bounded_and_forbids_causal_claims() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    outcome = decision.projection.outcome  # type: ignore[union-attr]
    payload = outcome.to_dict()
    assert payload["causal_diagnosis_generated"] is False
    assert payload["recommendations_generated"] is False
    assert payload["severity_assigned"] is False
    assert payload["financial_impact_inferred"] is False
    assert any("causality" in item.lower() for item in outcome.limitations)
    assert any("fraud" in item.lower() for item in outcome.forbidden_claims)


def test_nested_evidence_and_provenance_are_immutable() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    projection = decision.projection
    assert projection is not None
    finding = projection.findings[0]
    trace = finding.evidence_chain.math_trace[0]
    assert isinstance(trace["source_refs"], tuple)
    with pytest.raises(TypeError):
        trace["operation"] = "AVG"  # type: ignore[index]
    with pytest.raises(TypeError):
        projection.result_set.provenance["source"] = "tampered"  # type: ignore[index]


def test_non_finite_values_are_rejected_by_f9_contracts() -> None:
    decision = build_service_1_analysis_result_projection_v1(
        math_result=_math_sales_total(), prepared_evidence=_prepared_sales_total()
    )
    finding = decision.projection.findings[0]  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="finite number"):
        replace(finding, observed_value=float("nan"))
    measure = decision.projection.result_set.groups[0].measures["sales"]  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="finite number"):
        replace(measure, value=float("inf"))


def test_f9_source_has_no_math_hmac_secret_or_legacy_actionable_finding_dependency() -> None:
    source = inspect.getsource(f9)
    lowered = source.lower()
    assert "import hmac" not in lowered
    assert "secret" not in lowered
    assert "actionablefinding" not in lowered
    assert "formulaengineservice" not in lowered
    assert "calculate_math_primitive" not in lowered
    assert "recommendation_generated\": true" not in lowered
    assert "severity_assigned\": true" not in lowered
    assert "financial_impact_inferred\": true" not in lowered
