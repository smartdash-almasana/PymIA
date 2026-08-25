from __future__ import annotations

from pathlib import Path
import inspect

import pytest

import pymia.smartpyme.service_1_ui_v1 as ui
import pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 as semantic_web

from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    STATUS_PREPARED,
    build_service_1_analysis_evidence_preparation_v1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    STATUS_EVALUATED,
    execute_service_1_analysis_math_v1,
)
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_READY as F9_STATUS_READY,
    build_service_1_analysis_result_projection_v1,
)
from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    run_service_1_governed_analysis_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    ANALYSIS_DISCOVERY_CATALOG_V1,
    TECHNICALLY_AVAILABLE,
    TECHNICALLY_NEEDS_EVIDENCE,
    build_service_1_dynamic_analysis_discovery_v1,
)
from pymia.smartpyme.service_1_workbook_logical_model_v1 import (
    STATUS_READY as WORKBOOK_LOGICAL_MODEL_READY,
    build_service_1_workbook_logical_model_v1,
)


F12_AVAILABLE_ON_CAFETERIA = {
    "sales_by_category",
    "sales_by_employee",
    "sales_by_channel",
    "sales_by_payment_method",
    "units_by_product",
    "rows_by_product",
    "top_products_by_sales",
    "top_products_by_units",
    "discounted_rows",
    "discounted_rows_by_product",
    "transaction_id_multiplicity",
    "sales_by_product_branch",
    "sales_by_category_branch",
    "sales_series_hour",
}


def _p6(case_id: str, sheet: str, column: str, role: str) -> dict:
    return {
        "schema_version": "SERVICE_1_P6_APPROVAL_DECISION_V1",
        "case_id": case_id,
        "sheet_ref": sheet,
        "column_ref": column,
        "status": "APPROVED",
        "approved_role": role,
        "approved_variable": role,
        "reason": "OWNER_CONFIRMED_SEMANTIC_ROLE",
        "owner_confirmation_question_ref": f"q:{sheet}.{column}",
        "confidence": 0.99,
        "provenance": {"source": "f12_test"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _confirmed(approvals: list[dict], *, case_id: str, relationships: list[dict] | None = None) -> dict:
    return {
        "schema_version": "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1",
        "service_name": "SERVICE_1",
        "status": "CONFIRMED_BINDINGS",
        "bridge_packet": {"case_id": case_id},
        "reentry_packet": {"case_id": case_id, "p6_decisions": approvals},
        "confirmed_relationships": relationships or [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _relationship(case_id: str, left_sheet: str, left_column: str, right_sheet: str, right_column: str) -> dict:
    return {
        "case_id": case_id,
        "relationship_ref": f"{left_sheet}.{left_column}->{right_sheet}.{right_column}",
        "left_sheet_ref": left_sheet,
        "left_column_ref": left_column,
        "right_sheet_ref": right_sheet,
        "right_column_ref": right_column,
        "relationship_kind": "MANY_TO_ONE",
        "confirmed_by_owner": True,
        "question_ref": "q:relationship",
        "provenance": {"source": "f12_test"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


@pytest.fixture(scope="module")
def f12_cafeteria(tmp_path_factory: pytest.TempPathFactory) -> dict:
    workbook_path = Path(__file__).resolve().parents[2] / "prueba_excels" / "cafeteria_abc.xlsx"
    assert workbook_path.is_file()
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path_factory.mktemp("f12-cafeteria"),
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
    )
    status, menu_page = app.receive_xlsx(
        session_id="f12-cafeteria",
        filename=workbook_path.name,
        content=workbook_path.read_bytes(),
        selected_launch_review=None,
    )
    assert status == 200
    state = app.session("f12-cafeteria")
    steps = 0
    while state.semantic_questions:
        steps += 1
        assert steps <= 30
        question = state.semantic_questions[0]
        status, menu_page = app.confirm_meanings(
            session_id="f12-cafeteria",
            fields={f"action_{question['decision_id']}": "ACCEPT"},
        )
        assert status == 200
    assert state.semantic_assistance_state is not None
    semantic_run = state.semantic_assistance_state["semantic_run"]
    assert semantic_run["status"] == "CONFIRMED_BINDINGS"
    assert state.ingestion_output is not None
    workbook_logical_model = build_service_1_workbook_logical_model_v1(
        ingestion_output=state.ingestion_output,
    )
    assert workbook_logical_model["status"] == WORKBOOK_LOGICAL_MODEL_READY
    discovery = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=semantic_run,
        d7_workbook_logical_model=workbook_logical_model,
    )
    assert discovery.status == "DISCOVERY_READY"
    return {
        "app": app,
        "session_id": "f12-cafeteria",
        "menu_page": menu_page,
        "ingestion": state.ingestion_output,
        "semantic_run": semantic_run,
        "workbook_logical_model": workbook_logical_model,
        "discovery": discovery,
        "by_id": {item.analysis_id: item for item in discovery.analyses},
        "executions": {},
    }


def _run_to_f9(context: dict, analysis_id: str):
    cache = context["executions"]
    if analysis_id in cache:
        return cache[analysis_id]
    item = context["by_id"][analysis_id]
    assert item.technical_status == TECHNICALLY_AVAILABLE
    governed = item.governed_analysis_input
    assert governed is not None
    prep = build_service_1_analysis_evidence_preparation_v1(
        case_id=governed.case_id,
        governed_analysis_input=governed,
        ingestion_output=context["ingestion"],
        d7_workbook_logical_model=context["workbook_logical_model"],
    )
    assert prep.status == STATUS_PREPARED, prep.to_dict()
    assert prep.prepared_evidence is not None
    math = execute_service_1_analysis_math_v1(
        case_id=governed.case_id,
        governed_analysis_input=governed,
        prepared_evidence=prep.prepared_evidence,
    )
    assert math.status == STATUS_EVALUATED, math.to_dict()
    assert math.result is not None
    projection = build_service_1_analysis_result_projection_v1(
        math_result=math.result,
        prepared_evidence=prep.prepared_evidence,
        currency_code=None,
    )
    assert projection.status == F9_STATUS_READY, projection.to_dict()
    assert projection.projection is not None
    cache[analysis_id] = (prep.prepared_evidence, math.result, projection.projection)
    return cache[analysis_id]


def _table(context: dict, sheet_name: str) -> dict:
    return next(
        table for table in context["ingestion"]["normalized_tables"]
        if table["sheet_name"] == sheet_name
    )


def test_f12_catalog_contains_systematic_expansion() -> None:
    ids = {item.analysis_id for item in ANALYSIS_DISCOVERY_CATALOG_V1}
    assert F12_AVAILABLE_ON_CAFETERIA.issubset(ids)
    assert "catalog_price_variance_by_product" in ids
    assert "sales_series_day" in ids
    assert "sales_series_month" in ids


def test_real_cafeteria_exposes_new_dimensions_and_keeps_catalog_price_fail_closed(f12_cafeteria: dict) -> None:
    by_id = f12_cafeteria["by_id"]
    assert all(by_id[analysis_id].technical_status == TECHNICALLY_AVAILABLE for analysis_id in F12_AVAILABLE_ON_CAFETERIA)
    price_item = by_id["catalog_price_variance_by_product"]
    assert price_item.technical_status == TECHNICALLY_NEEDS_EVIDENCE
    assert ("list_price",) in price_item.missing_role_groups

    p6 = f12_cafeteria["semantic_run"]["reentry_packet"]["p6_decisions"]
    role_by_column = {(item["sheet_ref"], item["column_ref"]): item["approved_role"] for item in p6}
    assert role_by_column[("Ventas", "MetodoPago")] == "payment_method"
    assert role_by_column[("Productos", "Precio")] == "unit_sale_price"


def test_category_employee_channel_payment_and_hour_reach_f9(f12_cafeteria: dict) -> None:
    _prepared, total_result, _projection = _run_to_f9(f12_cafeteria, "sales_total")
    total_sales = total_result.groups[0].measures["sales"].value

    expected_group_values = {
        "sales_by_category": {str(row["categoria"]) for row in _table(f12_cafeteria, "Productos")["rows"]},
        "sales_by_employee": {str(row["empleado"]) for row in _table(f12_cafeteria, "Ventas")["rows"]},
        "sales_by_channel": {str(row["canalventa"]) for row in _table(f12_cafeteria, "Ventas")["rows"]},
        "sales_by_payment_method": {str(row["metodopago"]) for row in _table(f12_cafeteria, "Ventas")["rows"]},
    }
    dimension_by_analysis = {
        "sales_by_category": "category",
        "sales_by_employee": "employee",
        "sales_by_channel": "channel",
        "sales_by_payment_method": "payment_method",
    }
    for analysis_id, expected in expected_group_values.items():
        _prepared, result, _projection = _run_to_f9(f12_cafeteria, analysis_id)
        dimension = dimension_by_analysis[analysis_id]
        assert {group.key[dimension] for group in result.groups} == expected
        assert sum(group.measures["sales"].value for group in result.groups) == pytest.approx(total_sales)

    _prepared, hour_result, _projection = _run_to_f9(f12_cafeteria, "sales_series_hour")
    assert all(group.key["time"].endswith(":00") for group in hour_result.groups)
    assert sum(group.measures["sales"].value for group in hour_result.groups) == pytest.approx(total_sales)


def test_observed_demand_and_rankings_use_generic_math(f12_cafeteria: dict) -> None:
    _prepared, units_result, _projection = _run_to_f9(f12_cafeteria, "units_by_product")
    assert all(group.measures["units"].unit == "units" for group in units_result.groups)
    assert all(group.measures["units"].math_trace[0]["operation"] == "SUM" for group in units_result.groups)

    _prepared, transaction_result, _projection = _run_to_f9(f12_cafeteria, "rows_by_product")
    assert all(group.measures["row_count"].math_trace[0]["operation"] == "COUNT" for group in transaction_result.groups)
    assert sum(group.measures["row_count"].value for group in transaction_result.groups) == 5000

    _prepared, ranked_sales, _projection = _run_to_f9(f12_cafeteria, "top_products_by_sales")
    sales_values = [group.measures["sales"].value for group in ranked_sales.groups]
    assert sales_values == sorted(sales_values, reverse=True)
    assert [group.rank for group in ranked_sales.groups] == list(range(1, len(ranked_sales.groups) + 1))
    assert len(ranked_sales.groups) == 10

    _prepared, ranked_units, _projection = _run_to_f9(f12_cafeteria, "top_products_by_units")
    unit_values = [group.measures["units"].value for group in ranked_units.groups]
    assert unit_values == sorted(unit_values, reverse=True)
    assert len(ranked_units.groups) == 10


def test_discount_analysis_is_incidence_only_and_does_not_interpret_unit(f12_cafeteria: dict) -> None:
    ventas = _table(f12_cafeteria, "Ventas")
    expected_rows = sum(1 for row in ventas["rows"] if float(row["descuento"]) > 0)

    prepared, result, _projection = _run_to_f9(f12_cafeteria, "discounted_rows")
    assert len(prepared.prepared_rows) == expected_rows
    assert result.groups[0].measures["row_count"].value == expected_rows
    assert result.groups[0].measures["row_count"].formula_ref is None

    _prepared, ranked, _projection = _run_to_f9(f12_cafeteria, "discounted_rows_by_product")
    assert sum(group.measures["row_count"].value for group in ranked.groups) <= expected_rows
    assert all(group.measures["row_count"].formula_ref is None for group in ranked.groups)


def test_data_quality_multiplicity_is_factual_not_diagnostic(f12_cafeteria: dict) -> None:
    _prepared, result, projection = _run_to_f9(f12_cafeteria, "transaction_id_multiplicity")
    assert result.groups
    assert all(group.measures["row_count"].value == 1 for group in result.groups)
    assert all(finding.classification is None for finding in projection.findings)
    assert all(finding.severity is None for finding in projection.findings)


def test_cross_dimensions_materialize_governed_relationships_and_reconcile(f12_cafeteria: dict) -> None:
    _prepared, total_result, _projection = _run_to_f9(f12_cafeteria, "sales_total")
    total_sales = total_result.groups[0].measures["sales"].value

    prepared_product_branch, product_branch, _projection = _run_to_f9(f12_cafeteria, "sales_by_product_branch")
    assert {item.relationship_ref for item in prepared_product_branch.materialized_relationships} == {
        "Ventas.SucursalID->Sucursales.SucursalID"
    }
    assert sum(group.measures["sales"].value for group in product_branch.groups) == pytest.approx(total_sales)

    prepared_category_branch, category_branch, _projection = _run_to_f9(f12_cafeteria, "sales_by_category_branch")
    assert {item.relationship_ref for item in prepared_category_branch.materialized_relationships} == {
        "Ventas.ProductoID->Productos.ProductoID",
        "Ventas.SucursalID->Sucursales.SucursalID",
    }
    assert sum(group.measures["sales"].value for group in category_branch.groups) == pytest.approx(total_sales)


def test_catalog_price_variance_becomes_computable_only_with_explicit_list_price() -> None:
    case_id = "case-f12-price"
    approvals = [
        _p6(case_id, "Ventas", "ProductoID", "product_identifier"),
        _p6(case_id, "Ventas", "Cantidad", "quantity"),
        _p6(case_id, "Ventas", "PrecioUnitario", "unit_sale_price"),
        _p6(case_id, "Productos", "PrecioLista", "list_price"),
    ]
    relationship = _relationship(case_id, "Ventas", "ProductoID", "Productos", "ProductoID")
    confirmed = _confirmed(approvals, case_id=case_id, relationships=[relationship])
    discovery = build_service_1_dynamic_analysis_discovery_v1(confirmed_bindings=confirmed)
    item = {entry.analysis_id: entry for entry in discovery.analyses}["catalog_price_variance_by_product"]
    assert item.technical_status == TECHNICALLY_AVAILABLE
    assert item.governed_analysis_input is not None
    assert item.plan.relationship_refs == ("Ventas.ProductoID->Productos.ProductoID",)

    ingestion = {
        "case_id": case_id,
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["ProductoID", "Cantidad", "PrecioUnitario"],
                "normalized_headers": ["productoid", "cantidad", "preciounitario"],
                "rows": [
                    {"productoid": "P1", "cantidad": "1", "preciounitario": "90"},
                    {"productoid": "P1", "cantidad": "1", "preciounitario": "110"},
                    {"productoid": "P2", "cantidad": "2", "preciounitario": "60"},
                ],
                "source_row_numbers": [2, 3, 4],
            },
            {
                "status": "OK",
                "sheet_name": "Productos",
                "headers": ["ProductoID", "PrecioLista"],
                "normalized_headers": ["productoid", "preciolista"],
                "rows": [
                    {"productoid": "P1", "preciolista": "100"},
                    {"productoid": "P2", "preciolista": "50"},
                ],
                "source_row_numbers": [2, 3],
            },
        ],
        "runtime_authorized": False,
    }
    prep = build_service_1_analysis_evidence_preparation_v1(
        case_id=case_id,
        governed_analysis_input=item.governed_analysis_input,
        ingestion_output=ingestion,
    )
    assert prep.status == STATUS_PREPARED, prep.to_dict()
    assert prep.prepared_evidence is not None
    math = execute_service_1_analysis_math_v1(
        case_id=case_id,
        governed_analysis_input=item.governed_analysis_input,
        prepared_evidence=prep.prepared_evidence,
    )
    assert math.status == STATUS_EVALUATED, math.to_dict()
    assert math.result is not None
    values = {group.key["product"]: group.measures["catalog_price_variance_pct"].value for group in math.result.groups}
    assert values["P1"] == pytest.approx(0.0)
    assert values["P2"] == pytest.approx(20.0)
    assert all(group.measures["catalog_price_variance_pct"].formula_ref == "precio_catalogo_variacion_pct" for group in math.result.groups)


def test_f12_workbook_first_menu_exposes_canonical_analyses_without_legacy_launch_projection(f12_cafeteria: dict) -> None:
    page = f12_cafeteria["menu_page"]
    assert 'name="review_sales_by_category"' in page
    assert 'name="review_sales_by_payment_method"' in page
    assert 'name="review_top_products_by_units"' in page
    assert "Precio observado contra precio de catálogo" in page
    assert 'name="review_catalog_price_variance_by_product"' not in page
    assert "Ventas y cobranzas" not in page
    assert "Margen real" not in page
    assert "Flujo de caja" not in page
    assert 'name="review_sold_vs_collected_gap"' not in page
    assert 'name="review_net_margin_real"' not in page
    assert 'name="review_working_capital"' not in page


def test_f12_web_executes_single_analysis_id_through_f7_f8_f9(f12_cafeteria: dict) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]
    status, page = app.run_review(
        session_id=session_id,
        requested_capability="sales_by_category",
    )
    assert status == 200
    assert "Ventas por categoría" in page
    assert "Resumen del archivo" in page
    assert ">Ventas<" in page
    assert ">Sales<" not in page
    assert "$" in page
    assert "¿Querés seguir analizando tu planilla Excel?" in page
    menu_status, menu_page = app.analysis_menu(session_id=session_id)
    assert menu_status == 200
    assert "Elegí qué querés revisar" in menu_page
    state = app.session(session_id)
    packet = state.last_review_result
    assert packet["status"] == "READY"
    assert packet["analysis_id"] == "sales_by_category"
    assert packet["result_set"]["analysis_id"] == "sales_by_category"
    assert packet["diagnosis_generated"] is False


def test_f12_web_executes_multiple_analysis_ids_with_generic_result_renderer(f12_cafeteria: dict) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]
    status, page = app.run_selected_reviews(
        session_id=session_id,
        requested_capabilities=("sales_by_category", "sales_by_channel"),
    )
    assert status == 200
    assert "Ventas por categoría" in page
    assert "Ventas por canal" in page
    state = app.session(session_id)
    bundle = state.last_review_result
    assert bundle["status"] == "READY"
    assert bundle["analysis_ids"] == ["sales_by_category", "sales_by_channel"]
    assert len(bundle["results"]) == 2


def test_f12_direct_request_for_missing_evidence_fails_closed_to_menu(f12_cafeteria: dict) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]
    status, page = app.run_review(
        session_id=session_id,
        requested_capability="catalog_price_variance_by_product",
    )
    assert status == 200
    assert "Precio observado contra precio de catálogo" in page
    assert 'name="review_catalog_price_variance_by_product"' not in page


def test_f12_blocked_request_clears_previous_ready_result(f12_cafeteria: dict) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]

    ready_status, ready_page = app.run_review(
        session_id=session_id,
        requested_capability="sales_series_hour",
    )
    assert ready_status == 200
    assert "Resumen del archivo" in ready_page
    previous = app.session(session_id).last_review_result
    assert previous is not None
    assert previous["status"] == "READY"
    assert previous["analysis_id"] == "sales_series_hour"

    blocked_status, blocked_page = app.run_review(
        session_id=session_id,
        requested_capability="catalog_price_variance_by_product",
    )
    assert blocked_status == 200
    assert "Resultado listo" not in blocked_page
    assert app.session(session_id).last_review_result is None


def test_f12_blocked_bundle_clears_previous_ready_result(f12_cafeteria: dict) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]

    ready_status, _ready_page = app.run_review(
        session_id=session_id,
        requested_capability="sales_by_category",
    )
    assert ready_status == 200
    previous = app.session(session_id).last_review_result
    assert previous is not None
    assert previous["status"] == "READY"

    blocked_status, blocked_page = app.run_selected_reviews(
        session_id=session_id,
        requested_capabilities=(
            "sales_by_category",
            "catalog_price_variance_by_product",
        ),
    )
    assert blocked_status == 200
    assert "Resultado listo" not in blocked_page
    assert app.session(session_id).last_review_result is None


@pytest.mark.parametrize(
    "analysis_id",
    (
        "sales_total",
        "sales_by_product",
        "gross_margin_by_product",
        "sales_by_branch",
        "product_sales_concentration",
        "sales_series_day",
    ),
)
def test_f12_canonical_product_root_preserves_f9_resultset(
    f12_cafeteria: dict,
    analysis_id: str,
) -> None:
    _prepared, _math_result, expected_projection = _run_to_f9(f12_cafeteria, analysis_id)
    packet = run_service_1_governed_analysis_v1(
        ingestion_output=f12_cafeteria["ingestion"],
        confirmed_bindings=f12_cafeteria["semantic_run"],
        analysis_id=analysis_id,
        workbook_logical_model=f12_cafeteria["workbook_logical_model"],
    )
    assert packet["status"] == "READY"
    assert packet["result_set"] == expected_projection.result_set.to_dict()
    assert packet["findings"] == [finding.to_dict() for finding in expected_projection.findings]
    assert packet["outcome"] == expected_projection.outcome.to_dict()


def test_f12_web_has_no_direct_productive_f7_f8_f9_imports() -> None:
    source = inspect.getsource(semantic_web)
    assert "service_1_analysis_evidence_preparation_v1" not in source
    assert "build_service_1_analysis_evidence_preparation_v1" not in source
    assert "service_1_analysis_math_execution_v1" not in source
    assert "execute_service_1_analysis_math_v1" not in source
    assert "service_1_analysis_result_projection_v1" not in source
    assert "build_service_1_analysis_result_projection_v1" not in source
    assert "run_service_1_governed_analysis_v1" not in source
    assert "run_service_1_product_pipeline_v1" in source


def test_f12_web_cannot_execute_when_canonical_product_root_is_blocked(
    f12_cafeteria: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = f12_cafeteria["app"]
    session_id = f12_cafeteria["session_id"]
    calls: list[dict] = []

    def blocked_product_root(request, *, dependencies):
        calls.append({"request": request, "dependencies": dependencies})
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": request.analysis_id,
            "blocked_reason": "RC1_CANONICAL_ROOT_BLOCKED_TEST",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    monkeypatch.setattr(
        semantic_web,
        "run_service_1_product_pipeline_v1",
        blocked_product_root,
    )
    status, page = app.run_review(
        session_id=session_id,
        requested_capability="sales_by_category",
    )
    assert status == 200
    assert len(calls) == 1
    assert calls[0]["request"].analysis_id == "sales_by_category"
    assert "Resultado listo" not in page
    assert 'name="review_sales_by_category"' in page


def test_f12_generic_result_renderer_has_no_analysis_specific_math() -> None:
    source = inspect.getsource(ui.render_analysis_result_sets_v1).lower()
    assert "formulaengine" not in source
    assert "sales_by_" not in source
    assert "gross_margin" not in source
    assert "cafeteria" not in source
    assert "cafetería" not in source
