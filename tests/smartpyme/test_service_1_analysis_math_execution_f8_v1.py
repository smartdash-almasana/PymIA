from __future__ import annotations

import inspect

from pymia.contracts.formula_contract import (
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    Service1PreparedAnalysisEvidenceV1,
    Service1PreparedGroupV1,
    Service1PreparedRowV1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    STATUS_NEEDS_EVIDENCE,
    execute_service_1_analysis_math_v1,
)
from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedAnalysisInputV1
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1


def _plan(
    *,
    analysis_id: str,
    measures: tuple[str, ...],
    kind: AnalysisKind = AnalysisKind.SINGLE_VALUE,
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


def _row(ref: str, values: dict[str, object], sources: dict[str, str] | None = None) -> Service1PreparedRowV1:
    source_map = sources or {role: f"Ventas.{role}" for role in values}
    return Service1PreparedRowV1(
        row_ref=ref,
        base_sheet_ref="Ventas",
        role_values=values,
        role_source_refs=source_map,
        source_row_refs=(ref,),
        provenance={"source": "test"},
    )


def _prepared(
    plan: Service1AnalysisPlanV1,
    rows: tuple[Service1PreparedRowV1, ...],
    groups: tuple[Service1PreparedGroupV1, ...],
) -> Service1PreparedAnalysisEvidenceV1:
    return Service1PreparedAnalysisEvidenceV1(
        case_id="case-f8",
        analysis_id=plan.analysis_id,
        analysis_plan=plan,
        grain=Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain=plan.requested_grain.business_entity_grain,
            temporal_grain=plan.requested_grain.temporal_grain,
            aggregation_grain=plan.requested_grain.aggregation_grain,
        ),
        source_sheet_refs=("Ventas",),
        prepared_rows=rows,
        groups=groups,
        provenance={"source": "test_f7"},
    )


def _governed(
    plan: Service1AnalysisPlanV1,
    *,
    source_bindings: dict[str, str],
    formula_refs: tuple[str, ...] = (),
) -> Service1GovernedAnalysisInputV1:
    return Service1GovernedAnalysisInputV1(
        case_id="case-f8",
        analysis_plan=plan,
        source_bindings=source_bindings,
        relationship_bindings={},
        grain=Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain=plan.requested_grain.business_entity_grain,
            temporal_grain=plan.requested_grain.temporal_grain,
            aggregation_grain=plan.requested_grain.aggregation_grain,
        ),
        formula_refs=formula_refs,
        provenance={"source": "test_p8"},
    )


def _all_group(rows: tuple[Service1PreparedRowV1, ...]) -> tuple[Service1PreparedGroupV1, ...]:
    return (
        Service1PreparedGroupV1(
            group_ref="group:ALL",
            key={},
            member_row_refs=tuple(row.row_ref for row in rows),
        ),
    )


def test_formula_engine_owns_generic_math_primitives() -> None:
    engine = FormulaEngineService()
    cases = (
        (MathPrimitiveOperation.SUM, [1, 2, 3], [], 6.0),
        (MathPrimitiveOperation.COUNT, [1, 2, 3], [], 3.0),
        (MathPrimitiveOperation.AVG, [2, 4], [], 3.0),
        (MathPrimitiveOperation.MIN, [2, 4], [], 2.0),
        (MathPrimitiveOperation.MAX, [2, 4], [], 4.0),
        (MathPrimitiveOperation.SUM_PRODUCT, [2, 1], [60, 100], 220.0),
        (MathPrimitiveOperation.MULTIPLY, [2, 60], [], 120.0),
        (MathPrimitiveOperation.SUBTRACT, [200, 20], [], 180.0),
        (MathPrimitiveOperation.PERCENT_OF, [200, 10], [], 20.0),
        (MathPrimitiveOperation.SINGLE_VALUE, [30, 30], [], 30.0),
    )
    for operation, values, paired, expected in cases:
        result = engine.calculate_math_primitive(
            MathPrimitiveInput(operation=operation, values=values, paired_values=paired, source_refs=["src"])
        )
        assert result.status == FormulaStatus.OK
        assert result.value == expected


def test_single_sales_total_uses_sum_math_authority() -> None:
    plan = _plan(analysis_id="sales_total", measures=("sales",))
    rows = (
        _row("Ventas!row:2", {"sales_amount": "100"}),
        _row("Ventas!row:3", {"sales_amount": "200"}),
        _row("Ventas!row:4", {"sales_amount": "150"}),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(plan, source_bindings={"sales_amount": "VentaTotal"}),
        prepared_evidence=_prepared(plan, rows, _all_group(rows)),
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    measure = decision.result.groups[0].measures["sales"]
    assert measure.value == 450.0
    assert measure.formula_ref is None
    assert measure.math_trace[0]["operation"] == "SUM"


def test_grouped_sales_by_product_aggregates_each_f7_group() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        measures=("sales",),
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        aggregation="GROUPED",
    )
    rows = (
        _row("Ventas!row:2", {"sales_amount": "100", "product_identifier": "P1"}),
        _row("Ventas!row:3", {"sales_amount": "200", "product_identifier": "P2"}),
        _row("Ventas!row:4", {"sales_amount": "150", "product_identifier": "P1"}),
    )
    groups = (
        Service1PreparedGroupV1("group:product=P1", {"product": "P1"}, ("Ventas!row:2", "Ventas!row:4")),
        Service1PreparedGroupV1("group:product=P2", {"product": "P2"}, ("Ventas!row:3",)),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(
            plan, source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"}
        ),
        prepared_evidence=_prepared(plan, rows, groups),
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    values = {group.key["product"]: group.measures["sales"].value for group in decision.result.groups}
    assert values == {"P1": 250.0, "P2": 200.0}


def test_gross_margin_uses_sum_product_then_canonical_formula() -> None:
    plan = _plan(
        analysis_id="gross_margin_by_product",
        measures=("gross_margin",),
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        aggregation="GROUPED",
    )
    rows = (
        _row(
            "Ventas!row:2",
            {"sales_amount": "200", "quantity": "2", "unit_cost_candidate": "60", "product_identifier": "P1"},
            {
                "sales_amount": "Ventas.VentaTotal",
                "quantity": "Ventas.Cantidad",
                "unit_cost_candidate": "Productos.CostoUnitario",
                "product_identifier": "Ventas.ProductoID",
            },
        ),
        _row(
            "Ventas!row:3",
            {"sales_amount": "150", "quantity": "1", "unit_cost_candidate": "100", "product_identifier": "P2"},
            {
                "sales_amount": "Ventas.VentaTotal",
                "quantity": "Ventas.Cantidad",
                "unit_cost_candidate": "Productos.CostoUnitario",
                "product_identifier": "Ventas.ProductoID",
            },
        ),
    )
    groups = (
        Service1PreparedGroupV1("group:product=P1", {"product": "P1"}, ("Ventas!row:2",)),
        Service1PreparedGroupV1("group:product=P2", {"product": "P2"}, ("Ventas!row:3",)),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(
            plan,
            source_bindings={
                "sales_amount": "VentaTotal",
                "quantity": "Cantidad",
                "unit_cost_candidate": "CostoUnitario",
                "product_identifier": "ProductoID",
            },
            formula_refs=("margen_bruto",),
        ),
        prepared_evidence=_prepared(plan, rows, groups),
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    by_product = {group.key["product"]: group.measures["gross_margin"] for group in decision.result.groups}
    assert by_product["P1"].formula_inputs == {"ventas": 200.0, "costos": 120.0}
    assert by_product["P1"].value == 0.4
    assert by_product["P1"].formula_ref == "margen_bruto"
    assert [item["operation"] for item in by_product["P1"].math_trace] == ["SUM", "SUM_PRODUCT", "FORMULA"]


def test_dso_aggregates_inputs_and_calls_canonical_formula() -> None:
    plan = _plan(analysis_id="dso", measures=("dso",))
    rows = (
        _row("Ventas!row:2", {"accounts_receivable_amount": "100", "sales_amount": "1000", "period_days": "30"}),
        _row("Ventas!row:3", {"accounts_receivable_amount": "200", "sales_amount": "500", "period_days": "30"}),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(
            plan,
            source_bindings={
                "accounts_receivable_amount": "CxC",
                "sales_amount": "Ventas",
                "period_days": "Dias",
            },
            formula_refs=("PYME_011_dso",),
        ),
        prepared_evidence=_prepared(plan, rows, _all_group(rows)),
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    assert decision.result.groups[0].measures["dso"].value == 6.0


def test_projected_cash_balance_uses_single_and_sum_primitives() -> None:
    plan = _plan(analysis_id="cash", measures=("projected_cash_balance",))
    rows = (
        _row("Caja!row:2", {"initial_balance": "1000", "expected_collections": "200", "expected_payments": "100"}),
        _row("Caja!row:3", {"initial_balance": "1000", "expected_collections": "300", "expected_payments": "50"}),
    )
    prepared = _prepared(plan, rows, _all_group(rows))
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(
            plan,
            source_bindings={
                "initial_balance": "SaldoInicial",
                "expected_collections": "Cobros",
                "expected_payments": "Pagos",
            },
            formula_refs=("LIQ_002_saldo_final_proyectado",),
        ),
        prepared_evidence=prepared,
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    assert decision.result.groups[0].measures["projected_cash_balance"].value == 1350.0


def test_ranked_plan_orders_by_computed_measure_and_applies_limit() -> None:
    plan = _plan(
        analysis_id="top_products",
        measures=("sales",),
        kind=AnalysisKind.RANKED,
        dimensions=("product",),
        business="PRODUCT",
        aggregation="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales", direction="DESC"),),
        limit=1,
    )
    rows = (
        _row("Ventas!row:2", {"sales_amount": "100", "product_identifier": "P1"}),
        _row("Ventas!row:3", {"sales_amount": "300", "product_identifier": "P2"}),
    )
    groups = (
        Service1PreparedGroupV1("group:product=P1", {"product": "P1"}, ("Ventas!row:2",)),
        Service1PreparedGroupV1("group:product=P2", {"product": "P2"}, ("Ventas!row:3",)),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(
            plan, source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"}
        ),
        prepared_evidence=_prepared(plan, rows, groups),
    )
    assert decision.status == STATUS_EVALUATED
    assert decision.result is not None
    assert len(decision.result.groups) == 1
    assert decision.result.groups[0].key == {"product": "P2"}
    assert decision.result.groups[0].rank == 1


def test_invalid_numeric_evidence_never_becomes_zero() -> None:
    plan = _plan(analysis_id="sales_total", measures=("sales",))
    rows = (_row("Ventas!row:2", {"sales_amount": "not-a-number"}),)
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=_governed(plan, source_bindings={"sales_amount": "VentaTotal"}),
        prepared_evidence=_prepared(plan, rows, _all_group(rows)),
    )
    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.result is None
    assert "INVALID_NUMERIC_EVIDENCE" in str(decision.reason)


def test_multiple_distinct_single_values_block_math_primitive() -> None:
    engine = FormulaEngineService()
    result = engine.calculate_math_primitive(
        MathPrimitiveInput(operation=MathPrimitiveOperation.SINGLE_VALUE, values=[30, 31])
    )
    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MULTIPLE_DISTINCT_VALUES"


def test_empty_sum_and_unexpected_paired_values_fail_closed() -> None:
    engine = FormulaEngineService()
    empty_sum = engine.calculate_math_primitive(
        MathPrimitiveInput(operation=MathPrimitiveOperation.SUM, values=[])
    )
    assert empty_sum.status == FormulaStatus.BLOCKED
    assert empty_sum.blocking_reason == "EMPTY_INPUT"

    injected_pair = engine.calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.SUM,
            values=[1, 2],
            paired_values=[3, 4],
        )
    )
    assert injected_pair.status == FormulaStatus.BLOCKED
    assert injected_pair.blocking_reason == "UNEXPECTED_PAIRED_VALUES"


def test_p8_formula_ref_drift_blocks_before_execution() -> None:
    plan = _plan(analysis_id="gross_margin", measures=("gross_margin",))
    rows = (_row("Ventas!row:2", {"sales_amount": "200", "quantity": "2", "unit_cost_candidate": "60"}),)
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "quantity": "Cantidad", "unit_cost_candidate": "Costo"},
        formula_refs=(),
    )
    decision = execute_service_1_analysis_math_v1(
        case_id="case-f8",
        governed_analysis_input=governed,
        prepared_evidence=_prepared(plan, rows, _all_group(rows)),
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "P8_FORMULA_REF_DRIFT"


def test_f8_module_does_not_import_product_root_ui_or_derived_evidence() -> None:
    import pymia.smartpyme.service_1_analysis_math_execution_v1 as f8

    source = inspect.getsource(f8)
    assert "service_1_product_pipeline_v1" not in source
    assert "service_1_assisted_web_v1" not in source
    assert "service_1_derived_evidence_v1" not in source
    assert "finding_projection" not in source
    assert "FormulaEngineService" in source


def test_f8_converges_known_math_debt_outside_formula_engine() -> None:
    import pymia.smartpyme.service_1_derived_evidence_v1 as derived
    import pymia.smartpyme.service_1_generic_capability_engine_v1 as generic

    derived_source = inspect.getsource(derived)
    generic_source = inspect.getsource(generic)
    for forbidden in (
        "qty * unit_price",
        "qty * unit_cost",
        "sales_total +=",
        "costs_total +=",
        "gross_sale * (",
        "gross_sale - discount",
    ):
        assert forbidden not in derived_source
    assert "FormulaEngineService" in derived_source
    assert 'sum(values, Decimal("0"))' not in generic_source
    assert "calculate_math_primitive" in generic_source
