from __future__ import annotations

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understanding_v1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE,
    build_service_1_analysis_computability_decision_v1,
)
from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_confirmed_relationship_bindings_v1,
    build_service_1_owner_relationship_confirmation_event_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_MATCHED,
    build_service_1_analysis_requirement_match_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    STATUS_READY,
    build_service_1_workbook_profile_v1,
)


def _understanding(column: str, values: list[object], inferred: str, co_columns: list[str]):
    return build_column_understanding_v1(
        column_name=column,
        sheet_name="Ventas",
        sample_values=values,
        inferred_data_type=inferred,
        co_column_names=co_columns,
    )


def test_dimensional_roles_are_first_class_and_branch_is_not_sales_channel() -> None:
    cases = (
        ("SucursalID", ["S01", "S02"], "text", "branch_identifier"),
        ("Sucursal", ["Centro", "Norte"], "text", "branch_name"),
        ("Hora", ["08:30", "14:15"], "text", "operation_time"),
        ("VentaID", [1001, 1002], "number", "transaction_identifier"),
        ("Ciudad", ["Córdoba", "Rosario"], "text", "city"),
        ("CanalVenta", ["Mostrador", "Ecommerce"], "text", "sales_channel"),
    )
    co_columns = ["VentaTotal", "Fecha", "ProductoID", "SucursalID", "CanalVenta"]
    for column, values, inferred, expected_role in cases:
        result = _understanding(column, values, inferred, co_columns)
        assert result.primary_hypothesis is not None, column
        assert result.primary_hypothesis.semantic_role == expected_role, column

    branch = _understanding("Sucursal", ["Centro", "Norte"], "text", co_columns)
    branch_roles = {item.semantic_role for item in branch.candidate_meanings}
    assert "branch_name" in branch_roles
    assert "sales_channel" not in branch_roles

    channel = _understanding("CanalVenta", ["Mostrador", "Ecommerce"], "text", co_columns)
    channel_roles = {item.semantic_role for item in channel.candidate_meanings}
    assert "sales_channel" in channel_roles
    assert "branch_name" not in channel_roles
    assert "branch_identifier" not in channel_roles


def _branch_ingestion_output() -> dict:
    return {
        "case_id": "case-f6-branch",
        "filename": "branches.xlsx",
        "source_file_ref": "branches.xlsx",
        "workbook_context": {
            "case_id": "case-f6-branch",
            "source_artifact_ref": "artifact:case-f6-branch",
            "workbook_ref": "workbook:case-f6-branch",
            "ingestion_scope": "all_sheets",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        },
        "provenance": {
            "source_kind": "xlsx",
            "source_artifact_ref": "artifact:case-f6-branch",
            "source_file_ref": "workbook:case-f6-branch",
            "workbook_ref": "workbook:case-f6-branch",
            "filename": "branches.xlsx",
            "sheet_names": ["Ventas", "Sucursales"],
            "sheet_refs": [],
        },
        "column_refs": [
            {"sheet_name": "Ventas", "column_name": "SucursalID", "normalized_column_name": "sucursalid"},
            {"sheet_name": "Ventas", "column_name": "VentaTotal", "normalized_column_name": "ventatotal"},
            {"sheet_name": "Sucursales", "column_name": "SucursalID", "normalized_column_name": "sucursalid"},
            {"sheet_name": "Sucursales", "column_name": "Sucursal", "normalized_column_name": "sucursal"},
        ],
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["SucursalID", "VentaTotal"],
                "normalized_headers": ["sucursalid", "ventatotal"],
                "rows": [
                    {"sucursalid": "S01", "ventatotal": "100"},
                    {"sucursalid": "S02", "ventatotal": "200"},
                    {"sucursalid": "S01", "ventatotal": "150"},
                ],
                "row_count": 3,
                "column_count": 2,
                "runtime_authorized": False,
            },
            {
                "status": "OK",
                "sheet_name": "Sucursales",
                "headers": ["SucursalID", "Sucursal"],
                "normalized_headers": ["sucursalid", "sucursal"],
                "rows": [
                    {"sucursalid": "S01", "sucursal": "Centro"},
                    {"sucursalid": "S02", "sucursal": "Norte"},
                ],
                "row_count": 2,
                "column_count": 2,
                "runtime_authorized": False,
            },
        ],
        "runtime_authorized": False,
    }


def test_workbook_profiler_relationship_detection_is_not_product_specific() -> None:
    profile = build_service_1_workbook_profile_v1(ingestion_output=_branch_ingestion_output())
    assert profile["status"] == STATUS_READY
    relationships = {
        item["relationship_ref"]: item
        for item in profile["relationships"]
    }
    ref = "Ventas.SucursalID->Sucursales.SucursalID"
    assert ref in relationships
    relation = relationships[ref]
    assert relation["relationship_kind"] == "MANY_TO_ONE"
    assert relation["candidate_foreign_key"] is True


def test_owner_confirmed_relationship_projection_is_generic_and_non_executing() -> None:
    branch_event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-f6",
        file_ref="branches.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="SucursalID",
        right_sheet_ref="Sucursales",
        right_column_ref="SucursalID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="Sí",
        question_ref="q-branch",
        timestamp="2026-08-18T12:00:00+00:00",
    )
    product_event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-f6",
        file_ref="branches.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="ProductoID",
        right_sheet_ref="Productos",
        right_column_ref="ProductoID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="Sí",
        question_ref="q-product",
        timestamp="2026-08-18T12:00:00+00:00",
    )

    bindings = build_service_1_confirmed_relationship_bindings_v1(
        (branch_event, product_event),
        case_id="case-f6",
    )
    assert set(bindings) == {
        "Ventas.SucursalID->Sucursales.SucursalID",
        "Ventas.ProductoID->Productos.ProductoID",
    }
    for binding in bindings.values():
        assert binding["confirmed_by_owner"] is True
        assert binding["relationship_resolution_authorized"] is False
        assert binding["join_execution_authorized"] is False
        assert binding["runtime_authorized"] is False
        assert binding["delivery_authorized"] is False


def _p6(role: str, column: str) -> Service1P6ApprovalDecisionV1:
    return Service1P6ApprovalDecisionV1(
        case_id="case-f6",
        sheet_ref="Ventas",
        column_ref=column,
        status=STATUS_APPROVED,
        approved_role=role,
        approved_variable=role,
        reason="F6_TEST_APPROVED",
        provenance={"source": "f6_test"},
    )


def test_branch_relationship_evidence_flows_to_existing_p8_without_join_execution() -> None:
    relationship_ref = "Ventas.SucursalID->Sucursales.SucursalID"
    plan = Service1AnalysisPlanV1(
        analysis_id="sales_by_branch_relationship",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("branch",),
        relationship_refs=(relationship_ref,),
        requested_grain=Service1RequestedAnalysisGrainV1(
            business_entity_grain="BRANCH",
            temporal_grain="PERIOD",
            aggregation_grain="GROUPED",
        ),
    )
    p6 = (
        _p6("sales_amount", "VentaTotal"),
        _p6("branch_identifier", "SucursalID"),
    )
    match = build_service_1_analysis_requirement_match_v1(plan, p6)
    assert match.status == P7_STATUS_MATCHED

    event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-f6",
        file_ref="branches.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="SucursalID",
        right_sheet_ref="Sucursales",
        right_column_ref="SucursalID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="Sí",
        question_ref="q-branch",
        timestamp="2026-08-18T12:00:00+00:00",
    )
    bindings = build_service_1_confirmed_relationship_bindings_v1((event,), case_id="case-f6")
    decision = build_service_1_analysis_computability_decision_v1(
        case_id="case-f6",
        analysis_plan=plan,
        p6_decisions=p6,
        analysis_requirement_match=match,
        relationship_bindings=bindings,
    )
    assert decision.status == STATUS_COMPUTABLE
    governed = decision.governed_analysis_input
    assert governed is not None
    assert relationship_ref in governed.relationship_bindings
    assert governed.relationship_bindings[relationship_ref]["join_execution_authorized"] is False
    assert governed.to_dict()["analysis_execution_authorized"] is False
