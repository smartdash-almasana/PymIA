from __future__ import annotations

from pathlib import Path
import inspect

import pytest

from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    STATUS_PREPARED,
    build_service_1_analysis_evidence_preparation_v1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    STATUS_EVALUATED,
    execute_service_1_analysis_math_v1,
)
from pymia.smartpyme.service_1_analysis_plan_v1 import AnalysisKind, Service1AnalysisOrderByV1
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_READY as F9_STATUS_READY,
    build_service_1_analysis_result_projection_v1,
)
from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    ANALYSIS_DISCOVERY_CATALOG_V1,
    TECHNICALLY_AVAILABLE,
    Service1AnalysisDiscoveryTemplateV1,
    build_service_1_dynamic_analysis_discovery_v1,
)
import pymia.smartpyme.service_1_analysis_evidence_preparation_v1 as f7
import pymia.smartpyme.service_1_analysis_math_execution_v1 as f8
import pymia.smartpyme.service_1_analysis_result_projection_v1 as f9
import pymia.smartpyme.service_1_computability_v1 as p8
import pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 as f10
import pymia.smartpyme.service_1_variable_family_bindings_v1 as p7


F11_ANALYSIS_IDS = (
    "sales_total",
    "sales_by_product",
    "gross_margin_by_product",
    "sales_by_branch",
    "product_sales_concentration",
    "sales_series_month",
)


def _concentration_template() -> Service1AnalysisDiscoveryTemplateV1:
    return Service1AnalysisDiscoveryTemplateV1(
        analysis_id="product_sales_concentration",
        title="Concentración de ventas por producto",
        question="¿Qué participación tiene cada producto sobre las ventas totales?",
        kind=AnalysisKind.RANKED,
        measures=("sales_concentration",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales_concentration", direction="DESC"),),
        preferred_roles=("product_identifier",),
    )


def _f11_templates() -> tuple[Service1AnalysisDiscoveryTemplateV1, ...]:
    by_id = {item.analysis_id: item for item in ANALYSIS_DISCOVERY_CATALOG_V1}
    return (
        by_id["sales_total"],
        by_id["sales_by_product"],
        by_id["gross_margin_by_product"],
        by_id["sales_by_branch"],
        _concentration_template(),
        by_id["sales_series_month"],
    )


@pytest.fixture(scope="module")
def cafeteria_case(tmp_path_factory: pytest.TempPathFactory) -> dict:
    workbook_path = Path(__file__).resolve().parents[2] / "prueba_excels" / "cafeteria_abc.xlsx"
    assert workbook_path.is_file()
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path_factory.mktemp("f11-cafeteria"),
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
    )
    status, _page = app.receive_xlsx(
        session_id="f11-cafeteria",
        filename=workbook_path.name,
        content=workbook_path.read_bytes(),
        selected_launch_review=None,
    )
    assert status == 200
    state = app.session("f11-cafeteria")
    steps = 0
    while state.semantic_questions:
        steps += 1
        assert steps <= 20
        question = state.semantic_questions[0]
        status, _page = app.confirm_meanings(
            session_id="f11-cafeteria",
            fields={f"action_{question['decision_id']}": "ACCEPT"},
        )
        assert status == 200
    assert state.semantic_assistance_state is not None
    assert state.semantic_assistance_state["status"] == "CONFIRMED_BINDINGS"
    semantic_run = state.semantic_assistance_state["semantic_run"]
    assert semantic_run["status"] == "CONFIRMED_BINDINGS"
    assert state.ingestion_output is not None

    discovery = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=semantic_run,
        commercially_exposed_analysis_ids=F11_ANALYSIS_IDS,
        templates=_f11_templates(),
    )
    assert discovery.status == "DISCOVERY_READY"
    by_id = {item.analysis_id: item for item in discovery.analyses}
    assert set(by_id) == set(F11_ANALYSIS_IDS)
    assert all(item.technical_status == TECHNICALLY_AVAILABLE for item in by_id.values())
    assert all(item.governed_analysis_input is not None for item in by_id.values())
    return {
        "ingestion": state.ingestion_output,
        "semantic_run": semantic_run,
        "discovery": discovery,
        "by_id": by_id,
        "owner_steps": steps,
        "executions": {},
    }


def _run_to_f9(cafeteria_case: dict, analysis_id: str):
    cache = cafeteria_case["executions"]
    if analysis_id in cache:
        return cache[analysis_id]
    item = cafeteria_case["by_id"][analysis_id]
    governed = item.governed_analysis_input
    assert governed is not None
    case_id = governed.case_id
    prepared_decision = build_service_1_analysis_evidence_preparation_v1(
        case_id=case_id,
        governed_analysis_input=governed,
        ingestion_output=cafeteria_case["ingestion"],
    )
    assert prepared_decision.status == STATUS_PREPARED, prepared_decision.to_dict()
    prepared = prepared_decision.prepared_evidence
    assert prepared is not None

    math_decision = execute_service_1_analysis_math_v1(
        case_id=case_id,
        governed_analysis_input=governed,
        prepared_evidence=prepared,
    )
    assert math_decision.status == STATUS_EVALUATED, math_decision.to_dict()
    assert math_decision.result is not None

    f9_decision = build_service_1_analysis_result_projection_v1(
        math_result=math_decision.result,
        prepared_evidence=prepared,
        currency_code=None,
    )
    assert f9_decision.status == F9_STATUS_READY, f9_decision.to_dict()
    assert f9_decision.projection is not None
    cache[analysis_id] = (prepared, math_decision.result, f9_decision.projection)
    return cache[analysis_id]


def test_real_cafeteria_semantics_and_relationships_are_general(cafeteria_case: dict) -> None:
    semantic_run = cafeteria_case["semantic_run"]
    reentry = semantic_run["reentry_packet"]
    roles = {
        (str(item["sheet_ref"]), str(item["column_ref"])): str(item["approved_role"])
        for item in reentry["p6_decisions"]
    }
    assert roles[("Ventas", "Cantidad")] == "quantity"
    assert roles[("Ventas", "PrecioUnitario")] == "unit_sale_price"
    assert roles[("Ventas", "ProductoID")] == "product_identifier"
    assert roles[("Ventas", "SucursalID")] == "branch_identifier"
    assert roles[("Productos", "Costo")] == "unit_cost_candidate"
    assert roles[("Sucursales", "Sucursal")] == "branch_name"
    relationship_refs = {
        item["relationship_ref"] for item in semantic_run["confirmed_relationships"]
    }
    assert relationship_refs == {
        "Ventas.ProductoID->Productos.ProductoID",
        "Ventas.SucursalID->Sucursales.SucursalID",
    }
    assert cafeteria_case["owner_steps"] == 3


def test_f11_sales_total_atomic_evidence_reaches_f9(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "sales_total")
    assert len(prepared.prepared_rows) == 5000
    assert set(prepared.prepared_rows[0].role_values) == {"quantity", "unit_sale_price"}
    measure = result.groups[0].measures["sales"]
    assert measure.value > 0
    assert measure.formula_ref is None
    assert measure.math_trace[0]["operation"] == "SUM_PRODUCT"
    assert measure.math_trace[0]["primary_role"] == "quantity"
    assert measure.math_trace[0]["paired_role"] == "unit_sale_price"
    assert projection.result_set.groups[0].measures["sales"].value == measure.value


def test_f11_sales_by_product_uses_same_pipeline(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "sales_by_product")
    assert len(prepared.groups) == 15
    assert len(result.groups) == 15
    assert len(projection.result_set.groups) == 15
    assert all(group.measures["sales"].math_trace[0]["operation"] == "SUM_PRODUCT" for group in result.groups)
    assert not prepared.materialized_relationships


def test_f11_gross_margin_by_product_uses_confirmed_product_relationship_and_formula(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "gross_margin_by_product")
    assert len(prepared.groups) == 15
    assert [item.relationship_ref for item in prepared.materialized_relationships] == [
        "Ventas.ProductoID->Productos.ProductoID"
    ]
    for group in result.groups:
        measure = group.measures["gross_margin"]
        assert measure.formula_ref == "margen_bruto"
        operations = [item["operation"] for item in measure.math_trace]
        assert operations == ["SUM_PRODUCT", "SUM_PRODUCT", "FORMULA"]
        assert -1 <= measure.value <= 1
    assert projection.result_set.relationship_refs == ("Ventas.ProductoID->Productos.ProductoID",)


def test_f11_sales_by_branch_uses_confirmed_branch_relationship(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "sales_by_branch")
    assert len(prepared.groups) == 5
    assert [item.relationship_ref for item in prepared.materialized_relationships] == [
        "Ventas.SucursalID->Sucursales.SucursalID"
    ]
    branch_names = {group.key["branch"] for group in result.groups}
    sucursales = next(
        table
        for table in cafeteria_case["ingestion"]["normalized_tables"]
        if table["sheet_name"] == "Sucursales"
    )
    expected_branch_names = {str(row["sucursal"]) for row in sucursales["rows"]}
    assert branch_names == expected_branch_names
    assert projection.result_set.relationship_refs == ("Ventas.SucursalID->Sucursales.SucursalID",)


def test_f11_product_concentration_is_cross_group_canonical_formula(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "product_sales_concentration")
    assert len(prepared.groups) == 15
    assert len(result.groups) == 15
    assert [group.rank for group in result.groups] == list(range(1, 16))
    values = [group.measures["sales_concentration"].value for group in result.groups]
    assert values == sorted(values, reverse=True)
    assert sum(values) == pytest.approx(100.0, abs=1e-8)
    for group in result.groups:
        measure = group.measures["sales_concentration"]
        assert measure.formula_ref == "PYME_033_concentracion_sku"
        assert any(item.get("scope") == "ALL_GROUPS" for item in measure.math_trace)
    assert projection.result_set.groups[0].rank == 1


def test_f11_sales_series_month_uses_same_atomic_sales_basis(cafeteria_case: dict) -> None:
    prepared, result, projection = _run_to_f9(cafeteria_case, "sales_series_month")
    assert len(prepared.groups) == 5
    months = [group.key["time"] for group in result.groups]
    assert months == ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]
    assert all(group.measures["sales"].math_trace[0]["operation"] == "SUM_PRODUCT" for group in result.groups)
    assert [group.key["time"] for group in projection.result_set.groups] == months


def test_f11_sales_shapes_reconcile_to_one_transactional_total(cafeteria_case: dict) -> None:
    _prepared, total_result, _projection = _run_to_f9(cafeteria_case, "sales_total")
    total_sales = total_result.groups[0].measures["sales"].value

    _prepared, product_result, _projection = _run_to_f9(cafeteria_case, "sales_by_product")
    _prepared, branch_result, _projection = _run_to_f9(cafeteria_case, "sales_by_branch")
    _prepared, month_result, _projection = _run_to_f9(cafeteria_case, "sales_series_month")
    _prepared, concentration_result, _projection = _run_to_f9(cafeteria_case, "product_sales_concentration")

    assert sum(group.measures["sales"].value for group in product_result.groups) == pytest.approx(total_sales)
    assert sum(group.measures["sales"].value for group in branch_result.groups) == pytest.approx(total_sales)
    assert sum(group.measures["sales"].value for group in month_result.groups) == pytest.approx(total_sales)
    assert all(
        group.measures["sales_concentration"].formula_inputs["total_sales"] == pytest.approx(total_sales)
        for group in concentration_result.groups
    )


def test_f11_no_cafeteria_or_analysis_id_runtime_branches() -> None:
    modules = (p7, p8, f7, f8, f9, f10)
    for module in modules:
        source = inspect.getsource(module).lower()
        assert "cafeteria" not in source
        assert "cafetería" not in source
        assert "if analysis_id ==" not in source
        assert "if plan.analysis_id ==" not in source
