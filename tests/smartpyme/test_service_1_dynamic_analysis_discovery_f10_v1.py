from __future__ import annotations

import inspect

import pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 as f10
from pymia.smartpyme.service_1_analysis_plan_v1 import AnalysisKind
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    STATUS_BLOCKED,
    STATUS_READY,
    TECHNICALLY_AVAILABLE,
    TECHNICALLY_NEEDS_EVIDENCE,
    Service1AnalysisDiscoveryTemplateV1,
    build_service_1_dynamic_analysis_discovery_v1,
    project_service_1_dynamic_discovery_menu_v1,
)
from pymia.smartpyme.service_1_ui_v1 import render_analysis_menu_v1


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
        "provenance": {"source": "test"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _confirmed(
    approvals: list[dict],
    *,
    case_id: str = "case-f10",
    relationships: list[dict] | None = None,
) -> dict:
    return {
        "schema_version": "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1",
        "service_name": "SERVICE_1",
        "status": "CONFIRMED_BINDINGS",
        "bridge_packet": {"case_id": case_id},
        "reentry_packet": {
            "case_id": case_id,
            "p6_decisions": approvals,
        },
        "confirmed_relationships": relationships or [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _by_id(result) -> dict:
    return {item.analysis_id: item for item in result.analyses}


def test_sales_only_discovers_total_and_blocks_dimensions_from_actual_p7_p8() -> None:
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed([
            _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        ])
    )
    assert result.status == STATUS_READY
    items = _by_id(result)
    assert items["sales_total"].technical_status == TECHNICALLY_AVAILABLE
    assert items["sales_total"].p7_status == "REQUIREMENT_MATCHED"
    assert items["sales_total"].p8_status == "COMPUTABLE"
    assert items["sales_by_product"].technical_status == TECHNICALLY_NEEDS_EVIDENCE
    assert ("product_identifier", "product_name") in items["sales_by_product"].missing_role_groups
    assert items["sales_by_branch"].technical_status == TECHNICALLY_NEEDS_EVIDENCE
    assert items["sales_series_day"].technical_status == TECHNICALLY_NEEDS_EVIDENCE


def test_product_and_date_semantics_expand_discovery_without_ui_rules() -> None:
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed([
            _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
            _p6("case-f10", "Ventas", "ProductoID", "product_identifier"),
            _p6("case-f10", "Ventas", "Fecha", "operation_date"),
        ])
    )
    items = _by_id(result)
    assert items["sales_total"].technically_available is True
    assert items["sales_by_product"].technically_available is True
    assert items["sales_series_day"].technically_available is True
    assert items["sales_series_month"].technically_available is True
    assert items["sales_by_branch"].technically_available is False


def test_gross_margin_cross_sheet_needs_confirmed_relationship_evidence() -> None:
    approvals = [
        _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        _p6("case-f10", "Ventas", "Cantidad", "quantity"),
        _p6("case-f10", "Ventas", "ProductoID", "product_identifier"),
        _p6("case-f10", "Productos", "CostoUnitario", "unit_cost_candidate"),
    ]
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed(approvals)
    )
    item = _by_id(result)["gross_margin_by_product"]
    assert item.technical_status == TECHNICALLY_NEEDS_EVIDENCE
    assert item.technically_available is False
    assert item.required_relationship_refs == ()
    assert item.missing_relationship_evidence
    assert item.p8_reason == "CROSS_SHEET_RELATIONSHIP_EVIDENCE_REQUIRED"


def test_owner_confirmed_relationship_is_added_to_plan_then_validated_by_p8() -> None:
    approvals = [
        _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        _p6("case-f10", "Ventas", "Cantidad", "quantity"),
        _p6("case-f10", "Ventas", "ProductoID", "product_identifier"),
        _p6("case-f10", "Productos", "CostoUnitario", "unit_cost_candidate"),
    ]
    relationship = {
        "case_id": "case-f10",
        "left_sheet_ref": "Ventas",
        "left_column_ref": "ProductoID",
        "right_sheet_ref": "Productos",
        "right_column_ref": "ProductoID",
        "relationship_kind": "MANY_TO_ONE",
        "confirmed_by_owner": True,
        "question_ref": "rel-product",
        "provenance": {"source": "test"},
    }
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed(approvals, relationships=[relationship])
    )
    item = _by_id(result)["gross_margin_by_product"]
    ref = "Ventas.ProductoID->Productos.ProductoID"
    assert item.technical_status == TECHNICALLY_AVAILABLE
    assert item.required_relationship_refs == (ref,)
    assert item.plan.relationship_refs == (ref,)
    assert item.p8_status == "COMPUTABLE"
    assert item.missing_relationship_evidence == ()


def test_ambiguous_confirmed_relationship_paths_block_discovery() -> None:
    approvals = [
        _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        _p6("case-f10", "Ventas", "Cantidad", "quantity"),
        _p6("case-f10", "Ventas", "ProductoID", "product_identifier"),
        _p6("case-f10", "Productos", "CostoUnitario", "unit_cost_candidate"),
    ]
    relationships = [
        {
            "case_id": "case-f10",
            "left_sheet_ref": "Ventas",
            "left_column_ref": "ProductoID",
            "right_sheet_ref": "Productos",
            "right_column_ref": "ProductoID",
            "relationship_kind": "MANY_TO_ONE",
            "confirmed_by_owner": True,
            "question_ref": "rel-product",
            "provenance": {"source": "test"},
        },
        {
            "case_id": "case-f10",
            "left_sheet_ref": "Ventas",
            "left_column_ref": "ProductoAlt",
            "right_sheet_ref": "Productos",
            "right_column_ref": "ProductoAlt",
            "relationship_kind": "MANY_TO_ONE",
            "confirmed_by_owner": True,
            "question_ref": "rel-product-alt",
            "provenance": {"source": "test"},
        },
    ]
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed(approvals, relationships=relationships)
    )
    item = _by_id(result)["gross_margin_by_product"]
    assert item.technically_available is False
    assert item.technical_status == "TECHNICALLY_BLOCKED"
    assert item.p8_reason == "DISCOVERY_AMBIGUOUS_RELATIONSHIP_PATH"
    assert item.required_relationship_refs == ()


def test_cash_projection_is_discovered_from_confirmed_roles() -> None:
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed([
            _p6("case-f10", "Caja", "SaldoInicial", "initial_balance"),
            _p6("case-f10", "Caja", "Cobros", "expected_collections"),
            _p6("case-f10", "Caja", "Pagos", "expected_payments"),
        ])
    )
    item = _by_id(result)["projected_cash_balance"]
    assert item.technically_available is True
    assert item.p8_status == "COMPUTABLE"
    assert item.plan.measures == ("projected_cash_balance",)


def test_commercial_exposure_is_separate_from_technical_availability() -> None:
    confirmed = _confirmed([
        _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        _p6("case-f10", "Ventas", "ProductoID", "product_identifier"),
    ])
    technical_only = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=confirmed
    )
    technical_ids = {item.analysis_id for item in technical_only.technically_available}
    assert {"sales_total", "sales_by_product"}.issubset(technical_ids)
    assert technical_only.commercially_exposed == ()

    exposed = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=confirmed,
        commercially_exposed_analysis_ids=("sales_by_product",),
    )
    exposed_technical_ids = {item.analysis_id for item in exposed.technically_available}
    assert {"sales_total", "sales_by_product"}.issubset(exposed_technical_ids)
    assert [item.analysis_id for item in exposed.commercially_exposed] == ["sales_by_product"]
    assert _by_id(exposed)["sales_total"].commercially_exposed is False


def test_new_analysis_template_requires_no_ui_change() -> None:
    custom = Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_total_second_view",
        title="Segunda vista de ventas",
        question="¿Cuál es el total de ventas en esta vista?",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("sales",),
        dimensions=(),
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    )
    result = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=_confirmed([
            _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
        ]),
        templates=(custom,),
        commercially_exposed_analysis_ids=(custom.analysis_id,),
    )
    assert result.status == STATUS_READY
    assert len(result.analyses) == 1
    assert result.analyses[0].analysis_id == "sales_total_second_view"
    assert result.analyses[0].technically_available is True
    assert result.analyses[0].commercially_requested is True
    assert result.analyses[0].commercially_exposed is True

    menu = project_service_1_dynamic_discovery_menu_v1(result)
    assert menu["available"] == [
        ("sales_total_second_view", "Segunda vista de ventas", "¿Cuál es el total de ventas en esta vista?")
    ]
    html = render_analysis_menu_v1(menu["available"], blocked_options=menu["blocked"])
    assert 'name="review_sales_total_second_view"' in html


def test_unknown_commercial_exposure_policy_fails_closed_at_configuration_boundary() -> None:
    try:
        build_service_1_dynamic_analysis_discovery_v1(
            confirmed_bindings=_confirmed([
                _p6("case-f10", "Ventas", "VentaTotal", "sales_amount"),
            ]),
            commercially_exposed_analysis_ids=("does_not_exist",),
        )
    except ValueError as exc:
        assert "unknown commercial exposure" in str(exc)
    else:
        raise AssertionError("unknown exposure id must fail")


def test_discovery_fails_closed_without_confirmed_bindings() -> None:
    result = build_service_1_dynamic_analysis_discovery_v1(confirmed_bindings={})
    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == "CONFIRMED_BINDINGS_REQUIRED"
    assert result.analyses == ()
    payload = result.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["analysis_execution_authorized"] is False


def test_f10_has_no_ui_menu_or_execution_dependencies() -> None:
    source = inspect.getsource(f10)
    assert "service_1_assisted_web" not in source
    assert "_REVIEW_OPTIONS" not in source
    assert "_LAUNCH_REVIEW_OPTIONS" not in source
    assert "FormulaEngineService" not in source
    assert "service_1_analysis_math_execution" not in source
    assert "service_1_analysis_result_projection" not in source
    assert "cafeteria" not in source.lower()
    assert "retail" not in source.lower()
    assert "consorcio" not in source.lower()
