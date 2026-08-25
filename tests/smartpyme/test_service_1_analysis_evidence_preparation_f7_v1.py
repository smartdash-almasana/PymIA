from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisFilterV1,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    Service1GovernedAnalysisInputV1,
    build_service_1_governed_relationship_binding_v1,
)
from pymia.smartpyme.service_1_logical_relationship_graph_v1 import (
    CARDINALITY_MANY_TO_ONE,
    build_service_1_logical_relationship_graph_v1,
)
from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_confirmed_relationship_bindings_v1,
    build_service_1_owner_relationship_confirmation_event_v1,
)
import pymia.smartpyme.service_1_analysis_evidence_preparation_v1 as f7
from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    STATUS_BLOCKED,
    STATUS_NEEDS_EVIDENCE,
    STATUS_PREPARED,
    STATUS_UNSUPPORTED,
    build_service_1_analysis_evidence_preparation_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1


def _plan(
    *,
    analysis_id: str,
    kind: AnalysisKind,
    dimensions: tuple[str, ...],
    business: str,
    temporal: str,
    aggregation: str,
    filters: tuple[Service1AnalysisFilterV1, ...] = (),
    order_by: tuple[Service1AnalysisOrderByV1, ...] = (),
    limit: int | None = None,
    relationship_refs: tuple[str, ...] = (),
    measures: tuple[str, ...] = ("sales",),
) -> Service1AnalysisPlanV1:
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
        filters=filters,
        order_by=order_by,
        limit=limit,
    )


def _governed(
    plan: Service1AnalysisPlanV1,
    *,
    source_bindings: dict[str, str],
    relationship_bindings: dict | None = None,
    formula_refs: tuple[str, ...] = (),
) -> Service1GovernedAnalysisInputV1:
    return Service1GovernedAnalysisInputV1(
        case_id="case-f7",
        analysis_plan=plan,
        source_bindings=source_bindings,
        relationship_bindings=relationship_bindings or {},
        grain=Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain=plan.requested_grain.business_entity_grain,
            temporal_grain=plan.requested_grain.temporal_grain,
            aggregation_grain=plan.requested_grain.aggregation_grain,
        ),
        formula_refs=formula_refs,
        provenance={"source": "test_f7"},
    )


def _sales_ingestion() -> dict:
    return {
        "case_id": "case-f7",
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["VentaID", "Fecha", "Hora", "ProductoID", "SucursalID", "VentaTotal"],
                "normalized_headers": ["ventaid", "fecha", "hora", "productoid", "sucursalid", "ventatotal"],
                "rows": [
                    {"ventaid": "V1", "fecha": "2026-08-01", "hora": "08:10", "productoid": "P1", "sucursalid": "S1", "ventatotal": "100"},
                    {"ventaid": "V2", "fecha": "2026-08-01", "hora": "09:20", "productoid": "P2", "sucursalid": "S1", "ventatotal": "200"},
                    {"ventaid": "V3", "fecha": "2026-08-02", "hora": "08:40", "productoid": "P1", "sucursalid": "S2", "ventatotal": "150"},
                ],
                "source_row_numbers": [2, 3, 4],
            }
        ],
        "runtime_authorized": False,
    }


def _margin_ingestion(*, duplicate_product_key: bool = False, unmatched: bool = False) -> dict:
    sales_product = "P9" if unmatched else "P1"
    product_rows = [
        {"productoid": "P1", "costounitario": "60"},
        {"productoid": "P2", "costounitario": "100"},
    ]
    if duplicate_product_key:
        product_rows.append({"productoid": "P1", "costounitario": "61"})
    return {
        "case_id": "case-f7",
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["ProductoID", "Cantidad", "VentaTotal"],
                "normalized_headers": ["productoid", "cantidad", "ventatotal"],
                "rows": [
                    {"productoid": sales_product, "cantidad": "2", "ventatotal": "200"},
                    {"productoid": "P2", "cantidad": "1", "ventatotal": "150"},
                ],
                "source_row_numbers": [2, 3],
            },
            {
                "status": "OK",
                "sheet_name": "Productos",
                "headers": ["ProductoID", "CostoUnitario"],
                "normalized_headers": ["productoid", "costounitario"],
                "rows": product_rows,
                "source_row_numbers": list(range(2, 2 + len(product_rows))),
            },
        ],
        "runtime_authorized": False,
    }


def _product_relationship_bindings() -> dict[str, dict]:
    event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-f7",
        file_ref="ventas.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="ProductoID",
        right_sheet_ref="Productos",
        right_column_ref="ProductoID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="Sí",
        question_ref="rel-product",
        timestamp="2026-08-18T13:00:00-03:00",
    )
    return build_service_1_confirmed_relationship_bindings_v1((event,), case_id="case-f7")


def _d4_d7_relationship_context() -> tuple[dict, dict, object]:
    event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-f7",
        file_ref="workbook:f7",
        left_sheet_ref="Ventas",
        left_column_ref="ProductoID",
        right_sheet_ref="Productos",
        right_column_ref="ProductoID",
        relationship_kind=CARDINALITY_MANY_TO_ONE,
        owner_answer="Sí",
        question_ref="rel-product-f7",
        timestamp="2026-08-18T13:00:00-03:00",
        provenance={"owner_actor_ref": "owner:f7"},
    )
    candidates = [
        {
            "candidate_id": "table:ventas",
            "logical_table_id": "table:ventas",
            "workbook_ref": "workbook:f7",
            "source_sheet_refs": ["Ventas"],
            "source_region_refs": ["Ventas:region:1"],
            "structural_signature": "sig:ventas",
            "provenance": {
                "sheet_ref": "Ventas",
                "region_ref": "Ventas:region:1",
                "structural_payload": {"columns": [{"normalized_header": "productoid"}, {"normalized_header": "cantidad"}, {"normalized_header": "ventatotal"}]},
            },
        },
        {
            "candidate_id": "table:productos",
            "logical_table_id": "table:productos",
            "workbook_ref": "workbook:f7",
            "source_sheet_refs": ["Productos"],
            "source_region_refs": ["Productos:region:1"],
            "structural_signature": "sig:productos",
            "provenance": {
                "sheet_ref": "Productos",
                "region_ref": "Productos:region:1",
                "structural_payload": {"columns": [{"normalized_header": "productoid"}, {"normalized_header": "costounitario"}]},
            },
        },
    ]
    evidence = [{
        "relationship_ref": event.relationship_ref,
        "left_column_ref": "Ventas.ProductoID",
        "right_column_ref": "Productos.ProductoID",
        "relationship_kind": CARDINALITY_MANY_TO_ONE,
        "evidence_refs": ["ev:f7:relationship"],
        "left_value_coverage": 1.0,
        "right_value_coverage": 1.0,
        "intersection_cardinality": 2,
        "candidate_foreign_key": True,
        "candidate_primary_key_ref": "Productos.ProductoID",
    }]
    schema_identity = {
        "schema_fingerprint": "schema:f7",
        "provenance": {
            "source_artifact_ref": "xlsx:sha256:f7",
            "workbook_ref": "workbook:f7",
        },
    }
    graph = build_service_1_logical_relationship_graph_v1(
        logical_table_candidates=candidates,
        relationship_evidence=evidence,
        owner_confirmation_events=(event,),
        schema_identity=schema_identity,
    )
    model = {
        "source_artifact_ref": "xlsx:sha256:f7",
        "workbook_ref": "workbook:f7",
        "schema_identity": schema_identity,
        "relationship_graph": graph,
    }
    binding = build_service_1_governed_relationship_binding_v1(
        d7_workbook_logical_model=model,
        owner_confirmation_event=event,
    )
    return model, binding, event


def test_grouped_sales_by_product_prepares_membership_without_aggregation() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"},
    )

    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7",
        governed_analysis_input=governed,
        ingestion_output=_sales_ingestion(),
    )

    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    assert [row.row_ref for row in prepared.prepared_rows] == ["Ventas!row:2", "Ventas!row:3", "Ventas!row:4"]
    groups = {group.key["product"]: group.member_row_refs for group in prepared.groups}
    assert groups == {
        "P1": ("Ventas!row:2", "Ventas!row:4"),
        "P2": ("Ventas!row:3",),
    }
    payload = prepared.to_dict()
    assert payload["aggregation_execution_authorized"] is False
    assert payload["formula_execution_authorized"] is False
    assert payload["ranking_execution_authorized"] is False


def test_single_value_prepares_one_all_group_without_calculating_total() -> None:
    plan = _plan(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
    )
    governed = _governed(plan, source_bindings={"sales_amount": "VentaTotal"})
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    assert len(prepared.groups) == 1
    assert prepared.groups[0].group_ref == "group:ALL"
    assert prepared.groups[0].key == {}
    assert "result" not in prepared.to_dict()


def test_filter_selects_rows_before_group_membership() -> None:
    plan = _plan(
        analysis_id="sales_by_product_branch_s1",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        filters=(Service1AnalysisFilterV1(field_ref="branch", operator="EQ", value="S1"),),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "product_identifier": "ProductoID",
            "branch_identifier": "SucursalID",
        },
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    assert [row.row_ref for row in prepared.prepared_rows] == ["Ventas!row:2", "Ventas!row:3"]
    assert prepared.applied_filters[0]["field_ref"] == "branch"


def test_series_day_builds_temporal_bucket_membership_only() -> None:
    plan = _plan(
        analysis_id="sales_series_by_day",
        kind=AnalysisKind.SERIES,
        dimensions=("time",),
        business="NONE",
        temporal="DAY",
        aggregation="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),),
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "operation_date": "Fecha"},
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    groups = {group.key["time"]: group.member_row_refs for group in prepared.groups}
    assert groups["2026-08-01"] == ("Ventas!row:2", "Ventas!row:3")
    assert groups["2026-08-02"] == ("Ventas!row:4",)
    assert prepared.provenance["order_by_deferred"] is True


def test_series_hour_uses_operation_time_bucket() -> None:
    plan = _plan(
        analysis_id="sales_series_by_hour",
        kind=AnalysisKind.SERIES,
        dimensions=("time",),
        business="NONE",
        temporal="HOUR",
        aggregation="GROUPED",
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "operation_time": "Hora"},
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    groups = {group.key["time"]: group.member_row_refs for group in prepared.groups}
    assert groups["08:00"] == ("Ventas!row:2", "Ventas!row:4")
    assert groups["09:00"] == ("Ventas!row:3",)


def test_ranked_plan_prepares_groups_but_defers_order_and_limit() -> None:
    plan = _plan(
        analysis_id="top_products",
        kind=AnalysisKind.RANKED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales", direction="DESC"),),
        limit=2,
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"},
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    assert len(prepared.groups) == 2
    assert prepared.provenance["ranking_performed"] is False
    assert prepared.provenance["order_by_deferred"] is True
    assert prepared.provenance["limit_deferred"] is True


def test_confirmed_many_to_one_relationship_materializes_row_evidence_without_formula() -> None:
    relationships = _product_relationship_bindings()
    relationship_ref = next(iter(relationships))
    plan = _plan(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=(relationship_ref,),
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "quantity": "Cantidad",
            "unit_cost_candidate": "CostoUnitario",
            "product_identifier": "ProductoID",
        },
        relationship_bindings=relationships,
        formula_refs=("margen_bruto",),
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_margin_ingestion()
    )
    assert decision.status == STATUS_PREPARED
    prepared = decision.prepared_evidence
    assert prepared is not None
    assert len(prepared.materialized_relationships) == 1
    relation = prepared.materialized_relationships[0]
    assert relation.relationship_kind == "MANY_TO_ONE"
    assert relation.materialized_pairs == (
        ("Ventas!row:2", "Productos!row:2"),
        ("Ventas!row:3", "Productos!row:3"),
    )
    first = prepared.prepared_rows[0]
    assert first.role_values["unit_cost_candidate"] == "60"
    assert first.role_source_refs["unit_cost_candidate"] == "Productos.CostoUnitario"
    assert first.to_dict()["relationship_refs"] == [relationship_ref]
    assert prepared.provenance["formula_execution_performed"] is False


def test_r6_d4_d7_p8_f7_provenance_chain_is_required_before_materialization() -> None:
    model, binding, _event = _d4_d7_relationship_context()
    relationship_ref = str(binding["relationship_ref"])
    plan = _plan(
        analysis_id="gross_margin_by_product_r6",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=(relationship_ref,),
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "quantity": "Cantidad",
            "unit_cost_candidate": "CostoUnitario",
            "product_identifier": "ProductoID",
        },
        relationship_bindings={relationship_ref: binding},
        formula_refs=("margen_bruto",),
    )
    ingestion = _margin_ingestion()
    ingestion["workbook_context"] = {
        "source_artifact_ref": "xlsx:sha256:f7",
        "workbook_ref": "workbook:f7",
        "schema_fingerprint": "schema:f7",
    }
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7",
        governed_analysis_input=governed,
        ingestion_output=ingestion,
        d7_workbook_logical_model=model,
    )
    assert decision.status == STATUS_PREPARED
    assert decision.prepared_evidence is not None
    assert decision.prepared_evidence.provenance["d4_provenance_validated"] is True
    assert decision.prepared_evidence.materialized_relationships[0].materialized_pairs


def test_r6_f7_rejects_binding_without_d4_graph_reference() -> None:
    model, binding, _event = _d4_d7_relationship_context()
    binding = dict(binding)
    binding.pop("d4_graph_ref")
    plan = _plan(
        analysis_id="gross_margin_by_product_r6_missing_graph",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=(str(binding["relationship_ref"]),),
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "quantity": "Cantidad", "unit_cost_candidate": "CostoUnitario", "product_identifier": "ProductoID"},
        relationship_bindings={str(binding["relationship_ref"]): binding},
        formula_refs=("margen_bruto",),
    )
    ingestion = _margin_ingestion()
    ingestion["workbook_context"] = {"source_artifact_ref": "xlsx:sha256:f7", "workbook_ref": "workbook:f7", "schema_fingerprint": "schema:f7"}
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=ingestion, d7_workbook_logical_model=model
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "D4_RELATIONSHIP_PROVENANCE_REQUIRED"


def test_many_to_one_duplicate_lookup_key_blocks_cardinality_drift() -> None:
    relationships = _product_relationship_bindings()
    ref = next(iter(relationships))
    plan = _plan(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=(ref,),
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "quantity": "Cantidad",
            "unit_cost_candidate": "CostoUnitario",
            "product_identifier": "ProductoID",
        },
        relationship_bindings=relationships,
        formula_refs=("margen_bruto",),
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7",
        governed_analysis_input=governed,
        ingestion_output=_margin_ingestion(duplicate_product_key=True),
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason is not None and decision.reason.startswith("RELATIONSHIP_CARDINALITY_VIOLATION")
    assert decision.prepared_evidence is None


def test_unmatched_required_relationship_needs_evidence() -> None:
    relationships = _product_relationship_bindings()
    ref = next(iter(relationships))
    plan = _plan(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        relationship_refs=(ref,),
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "quantity": "Cantidad",
            "unit_cost_candidate": "CostoUnitario",
            "product_identifier": "ProductoID",
        },
        relationship_bindings=relationships,
        formula_refs=("margen_bruto",),
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_margin_ingestion(unmatched=True)
    )
    assert decision.status == STATUS_NEEDS_EVIDENCE
    assert decision.reason is not None and decision.reason.startswith("RELATIONSHIP_MATCH_MISSING")


def test_cross_sheet_sources_without_governed_relationship_fail_closed() -> None:
    plan = _plan(
        analysis_id="gross_margin_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        measures=("gross_margin",),
    )
    governed = _governed(
        plan,
        source_bindings={
            "sales_amount": "VentaTotal",
            "quantity": "Cantidad",
            "unit_cost_candidate": "CostoUnitario",
            "product_identifier": "ProductoID",
        },
        formula_refs=("margen_bruto",),
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_margin_ingestion()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason == "CROSS_SHEET_SOURCE_REQUIRES_RELATIONSHIP"


def test_unsupported_filter_operator_does_not_execute_selection() -> None:
    plan = _plan(
        analysis_id="sales_filtered",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        filters=(Service1AnalysisFilterV1(field_ref="product", operator="REGEX", value="P.*"),),
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"},
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_UNSUPPORTED
    assert decision.reason == "FILTER_OPERATOR_UNSUPPORTED:REGEX"


def test_incompatible_filter_comparison_fails_closed() -> None:
    plan = _plan(
        analysis_id="sales_filtered_bad_type",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
        filters=(Service1AnalysisFilterV1(field_ref="product", operator="GT", value=10),),
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"},
    )
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    assert decision.status == STATUS_BLOCKED
    assert decision.reason is not None and decision.reason.startswith("FILTER_VALUE_INVALID:product:")


def test_ingestion_input_is_not_mutated() -> None:
    plan = _plan(
        analysis_id="sales_by_product",
        kind=AnalysisKind.GROUPED,
        dimensions=("product",),
        business="PRODUCT",
        temporal="PERIOD",
        aggregation="GROUPED",
    )
    governed = _governed(
        plan,
        source_bindings={"sales_amount": "VentaTotal", "product_identifier": "ProductoID"},
    )
    ingestion = _sales_ingestion()
    before = copy.deepcopy(ingestion)
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=ingestion
    )
    assert decision.status == STATUS_PREPARED
    assert ingestion == before


def test_f7_has_no_math_product_or_execution_authority() -> None:
    source = inspect.getsource(f7)
    assert "FormulaEngineService" not in source
    assert "service_1_product_pipeline_v1" not in source
    assert "GenericCapabilityEngine" not in source
    assert "build_service_1_computability_decision_v1" not in source

    plan = _plan(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        dimensions=(),
        business="NONE",
        temporal="PERIOD",
        aggregation="AGGREGATED",
    )
    governed = _governed(plan, source_bindings={"sales_amount": "VentaTotal"})
    decision = build_service_1_analysis_evidence_preparation_v1(
        case_id="case-f7", governed_analysis_input=governed, ingestion_output=_sales_ingestion()
    )
    payload = decision.to_dict()
    assert payload["runtime_authorized"] is False
    assert payload["analysis_execution_authorized"] is False
    assert payload["aggregation_execution_authorized"] is False
    assert payload["formula_execution_authorized"] is False
    assert payload["ranking_execution_authorized"] is False
