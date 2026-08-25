from __future__ import annotations

from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE,
    build_service_1_computability_decision_v1,
)
from pymia.smartpyme.service_1_derived_evidence_v1 import (
    NEED_DISCOUNT_UNIT,
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY,
    build_service_1_derived_evidence_v1,
)
from pymia.smartpyme.service_1_owner_unit_confirmation_event_v1 import (
    UNIT_DISCOUNT_FRACTION,
    build_service_1_owner_unit_confirmation_event_v1,
)
from pymia.smartpyme.service_1_ren_001_normalized_evidence_v1 import (
    evaluate_ren_001_from_normalized_tables_v1,
)


def _column_ref(sheet: str, column: str) -> dict:
    return {
        "field_id": f"{sheet}.{column}",
        "question_id": f"q:{sheet}.{column}",
        "sheet_name": sheet,
        "column_name": column,
        "normalized_column_name": column,
    }


def _p6(sheet: str, column: str, role: str, variable: str) -> dict:
    return {
        "schema_version": "SERVICE_1_P6_APPROVAL_DECISION_V1",
        "case_id": "case-derived-ren001",
        "sheet_ref": sheet,
        "column_ref": column,
        "status": "APPROVED",
        "approved_role": role,
        "approved_variable": variable,
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


def _requirement_match() -> dict:
    return {
        "schema_version": "SERVICE_1_VARIABLE_FAMILY_BINDINGS_V1",
        "service_name": "SERVICE_1",
        "family_id": "PERIOD_NET_MARGIN",
        "status": "MISSING_REQUIREMENTS",
        "required_role_groups": [
            ["period_sales_total"],
            ["period_costs_total"],
            ["period_taxes_total"],
        ],
        "satisfied_role_groups": [["period_taxes_total"]],
        "missing_role_groups": [["period_sales_total"], ["period_costs_total"]],
        "approved_roles": ["period_taxes_total"],
        "source_columns": ["ImpuestosPeriodo"],
        "target_variable_names": ["sale_price", "costs", "taxes"],
        "target_capabilities": ["net_margin_real"],
        "grain": {
            "structural_scope": "SHEET",
            "business_entity_grain": "NONE",
            "temporal_grain": "PERIOD",
            "aggregation_grain": "AGGREGATED",
        },
        "provenance": {"source": "test"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _fixture(*, with_discount: bool = False, relationship: bool = True) -> tuple[dict, dict, list[dict]]:
    ventas_columns = ["ProductoID", "Cantidad", "PrecioUnitario"]
    ventas_rows = [
        {"ProductoID": "P1", "Cantidad": 2, "PrecioUnitario": 100},
        {"ProductoID": "P2", "Cantidad": 1, "PrecioUnitario": 50},
    ]
    p6 = [
        _p6("Ventas", "ProductoID", "product_identifier", "product_id"),
        _p6("Ventas", "Cantidad", "quantity", "volume_sold"),
        _p6("Ventas", "PrecioUnitario", "unit_sale_price", "sale_price"),
        _p6("Productos", "ProductoID", "product_identifier", "product_id"),
        _p6("Productos", "Costo", "unit_cost_candidate", "cost"),
        _p6("Resumen", "ImpuestosPeriodo", "period_taxes_total", "taxes"),
    ]
    if with_discount:
        ventas_columns.append("Descuento")
        ventas_rows[0]["Descuento"] = 0.10
        ventas_rows[1]["Descuento"] = 0.0
        p6.append(_p6("Ventas", "Descuento", "discount_candidate", "discount"))

    ingestion = {
        "case_id": "case-derived-ren001",
        "workbook_context": {
            "case_id": "case-derived-ren001",
            "source_artifact_ref": "artifact:derived-ren001",
            "workbook_ref": "workbook:derived-ren001",
            "ingestion_scope": "all_sheets",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        },
        "provenance": {
            "source_kind": "XLSX",
            "source_artifact_ref": "artifact:derived-ren001",
            "source_file_ref": "workbook:derived-ren001",
            "workbook_ref": "workbook:derived-ren001",
            "filename": "cafeteria.xlsx",
            "sheet_names": ["Ventas", "Productos", "Resumen"],
            "sheet_refs": [],
        },
        "source_kind": "XLSX",
        "filename": "cafeteria.xlsx",
        "column_refs": [
            *[_column_ref("Ventas", column) for column in ventas_columns],
            _column_ref("Productos", "ProductoID"),
            _column_ref("Productos", "Costo"),
            _column_ref("Resumen", "ImpuestosPeriodo"),
        ],
        "normalized_tables": [
            {"sheet_name": "Ventas", "rows": ventas_rows},
            {
                "sheet_name": "Productos",
                "rows": [
                    {"ProductoID": "P1", "Costo": 60},
                    {"ProductoID": "P2", "Costo": 20},
                ],
            },
            {"sheet_name": "Resumen", "rows": [{"ImpuestosPeriodo": 20}]},
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    relationship_events = []
    if relationship:
        relationship_events.append(
            {
                "case_id": "case-derived-ren001",
                "left_sheet_ref": "Ventas",
                "left_column_ref": "ProductoID",
                "right_sheet_ref": "Productos",
                "right_column_ref": "ProductoID",
                "relationship_kind": "MANY_TO_ONE",
                "confirmed_by_owner": True,
                "question_ref": "dialogue:relationship:producto",
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "product_ready": False,
                "delivery_authorized": False,
                "diagnosis_generated": False,
            }
        )
    semantic_run = {
        "schema_version": "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1",
        "status": "CONFIRMED_BINDINGS",
        "bridge_packet": {"case_id": "case-derived-ren001"},
        "reentry_packet": {
            "case_id": "case-derived-ren001",
            "p6_decisions": p6,
            "requirement_matches": [_requirement_match()],
        },
        "confirmed_relationships": relationship_events,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return ingestion, semantic_run, p6


def test_derives_period_sales_and_costs_without_creating_fake_columns() -> None:
    ingestion, semantic_run, _p6_values = _fixture()

    packet = build_service_1_derived_evidence_v1(
        ingestion_output=ingestion,
        semantic_run=semantic_run,
        requested_capability="net_margin_real",
    )

    assert packet["status"] == STATUS_READY
    assert packet["derived_variables"]["sale_price"]["value"] == 250.0
    assert packet["derived_variables"]["costs"]["value"] == 140.0
    assert packet["derived_variables"]["sale_price"]["semantic_role"] == "period_sales_total"
    assert packet["derived_variables"]["costs"]["semantic_role"] == "period_costs_total"
    assert packet["derived_variables"]["costs"]["relationship_refs"]
    assert set(packet["derived_variables"]) == {"sale_price", "costs"}
    assert packet["runtime_authorized"] is False
    assert packet["delivery_authorized"] is False


def test_nonzero_discount_is_not_guessed_as_rate_or_amount() -> None:
    ingestion, semantic_run, _p6_values = _fixture(with_discount=True)

    packet = build_service_1_derived_evidence_v1(
        ingestion_output=ingestion,
        semantic_run=semantic_run,
        requested_capability="net_margin_real",
    )

    assert packet["status"] == STATUS_NEEDS_EVIDENCE
    assert packet["evidence_requirements"] == [NEED_DISCOUNT_UNIT]
    assert packet["derived_variables"] == {}
    assert len(packet["owner_questions"]) == 1
    assert packet["owner_questions"][0]["question_kind"] == "UNIT_MEANING"


def test_confirmed_fraction_discount_is_applied_before_period_sales_derivation() -> None:
    ingestion, semantic_run, _p6_values = _fixture(with_discount=True)
    event = build_service_1_owner_unit_confirmation_event_v1(
        case_id="case-derived-ren001",
        file_ref="cafeteria.xlsx",
        sheet_ref="Ventas",
        column_ref="Descuento",
        semantic_role="discount_candidate",
        unit_kind=UNIT_DISCOUNT_FRACTION,
        owner_answer=UNIT_DISCOUNT_FRACTION,
        question_ref="derived-unit:Ventas.Descuento",
        provenance={"owner_actor_id": "owner-1", "owner_actor_role": "OWNER"},
    )

    packet = build_service_1_derived_evidence_v1(
        ingestion_output=ingestion,
        semantic_run=semantic_run,
        requested_capability="net_margin_real",
        owner_unit_confirmation_events=[event.to_dict()],
    )

    assert packet["status"] == STATUS_READY
    assert packet["owner_questions"] == []
    assert packet["derived_variables"]["sale_price"]["value"] == 230.0
    assert packet["derived_variables"]["costs"]["value"] == 140.0
    assert packet["derived_variables"]["sale_price"]["governed_parameters"] == {
        "discount_unit_kind": UNIT_DISCOUNT_FRACTION
    }
    assert packet["derived_variables"]["sale_price"]["owner_unit_question_refs"] == [
        "derived-unit:Ventas.Descuento"
    ]


def test_missing_owner_confirmed_product_relationship_blocks_cross_sheet_cost_derivation() -> None:
    ingestion, semantic_run, _p6_values = _fixture(relationship=False)

    packet = build_service_1_derived_evidence_v1(
        ingestion_output=ingestion,
        semantic_run=semantic_run,
        requested_capability="net_margin_real",
    )

    assert packet["status"] == "BLOCKED"
    assert packet["blocked_reason"] == "BLOCK_DERIVED_EVIDENCE_RELATIONSHIP_NOT_CONFIRMED"


def test_p8_combines_direct_tax_total_with_derived_sales_and_costs_then_kernel_executes() -> None:
    ingestion, semantic_run, p6_values = _fixture()
    derived = build_service_1_derived_evidence_v1(
        ingestion_output=ingestion,
        semantic_run=semantic_run,
        requested_capability="net_margin_real",
    )
    assert derived["status"] == STATUS_READY

    decision = build_service_1_computability_decision_v1(
        case_id="case-derived-ren001",
        requested_capability="net_margin_real",
        p6_decisions=p6_values,
        requirement_matches=[_requirement_match()],
        derived_evidence_packet=derived,
    )

    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_computation_input
    assert governed is not None
    bindings = governed.to_dict()["source_bindings"]
    assert bindings["sale_price"]["source_kind"] == "DERIVED_EVIDENCE"
    assert bindings["costs"]["source_kind"] == "DERIVED_EVIDENCE"
    assert bindings["taxes"] == "ImpuestosPeriodo"

    result = evaluate_ren_001_from_normalized_tables_v1(
        computation_plan=governed.to_dict(),
        normalized_tables=ingestion["normalized_tables"],
        column_refs=ingestion["column_refs"],
        derived_evidence_packet=derived,
    )

    assert result["status"] == "EVALUATED"
    assert result["inputs"] == {"sale_price": 250.0, "costs": 140.0, "taxes": 20.0}
    assert result["computed"]["net_margin_amount"] == 90.0
    assert result["computed"]["net_margin_percentage"] == 36.0
    assert result["computed"]["total_outflows"] == 160.0
    assert result["aggregation"]["sources"]["sale_price"]["source_kind"] == "DERIVED_EVIDENCE"
    assert result["aggregation"]["sources"]["taxes"]["source_kind"] == "DIRECT_COLUMN_EVIDENCE"
