from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread

import pytest

import pymia.smartpyme.service_1_semantic_boundary_v1 as semantic_boundary_module
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
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_READY as RESULT_PROJECTION_READY,
    build_service_1_analysis_result_projection_v1,
    verify_service_1_result_set_integrity_v1,
)
from pymia.smartpyme.service_1_headless_adapter_v1 import (
    HEADLESS_ROUTE_V1,
    MAX_JSON_BODY_BYTES_V1 as HEADLESS_MAX_JSON_BODY_BYTES_V1,
    create_service_1_headless_server_v1,
)
from pymia.smartpyme.service_1_headless_contract_v1 import HEADLESS_REQUEST_SCHEMA_VERSION
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    _physical_lineage,
)
from pymia.smartpyme.service_1_semantic_boundary_http_v1 import (
    MAX_JSON_BODY_BYTES_V1 as SEMANTIC_MAX_JSON_BODY_BYTES_V1,
    SEMANTIC_INITIAL_ROUTE_V1,
    create_service_1_semantic_boundary_server_v1,
)
from pymia.smartpyme.service_1_semantic_boundary_v1 import (
    REENTRY_REQUEST_SCHEMA,
    Service1SemanticStateStoreV1,
    execute_service_1_semantic_reentry_json_v1,
)
from pymia.smartpyme.service_1_semantic_coordinate_model_v2 import (
    Service1SemanticCoordinateTaxonomyV2,
    load_service_1_semantic_coordinate_taxonomy_v2,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1
from pymia.smartpyme.service_1_workbook_business_understanding_v1 import (
    AUTHORITY as BUSINESS_AUTHORITY,
    SCHEMA_VERSION as BUSINESS_SCHEMA_VERSION,
    STATUS_BLOCKED as BUSINESS_BLOCKED,
    validate_service_1_workbook_business_understanding_v1,
)


def _serve(server):
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def _post_raw(server, path: str, body: bytes):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=30)
    conn.request("POST", path, body=body, headers={"Content-Type": "application/json"})
    response = conn.getresponse()
    data = response.read()
    return response.status, json.loads(data.decode("utf-8"))


def test_result_set_digest_uses_the_same_deduplicated_refs_as_result_set() -> None:
    plan = Service1AnalysisPlanV1(
        analysis_id="sales_total",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("sales",),
        dimensions=(),
        relationship_refs=("rel-1",),
        requested_grain=Service1RequestedAnalysisGrainV1(
            business_entity_grain="NONE",
            temporal_grain="PERIOD",
            aggregation_grain="AGGREGATED",
        ),
    )
    grain = Service1GrainV1(
        structural_scope="SHEET",
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    )
    prepared_row = Service1PreparedRowV1(
        row_ref="row-1",
        base_sheet_ref="sheet-1",
        role_values={"sales_amount": 10},
        role_source_refs={"sales_amount": "sheet-1.sales"},
        source_row_refs=("sheet-1:2",),
        relationship_refs=("rel-1",),
    )
    prepared_group = Service1PreparedGroupV1(
        group_ref="group-1",
        key={},
        member_row_refs=("row-1",),
    )
    relationship = Service1PreparedRelationshipV1(
        relationship_ref="rel-1",
        relationship_kind="MANY_TO_ONE",
        left_sheet_ref="sheet-1",
        right_sheet_ref="sheet-2",
        materialized_pairs=(("sheet-1:2", "sheet-2:2"),),
    )
    prepared = Service1PreparedAnalysisEvidenceV1(
        case_id="case-1",
        analysis_id="sales_total",
        analysis_plan=plan,
        grain=grain,
        source_sheet_refs=("sheet-1", "sheet-1"),
        prepared_rows=(prepared_row,),
        groups=(prepared_group,),
        materialized_relationships=(relationship, relationship),
    )
    measure = Service1ExecutedMeasureV1(
        measure_ref="sales",
        value=10.0,
        unit="currency",
        formula_ref=None,
        formula_inputs={},
        source_refs=("sheet-1.sales",),
        math_trace=(),
    )
    math_result = Service1AnalysisMathResultV1(
        case_id="case-1",
        analysis_id="sales_total",
        groups=(
            Service1ExecutedGroupV1(
                group_ref="group-1",
                key={},
                measures={"sales": measure},
                member_row_refs=("row-1",),
            ),
        ),
    )

    decision = build_service_1_analysis_result_projection_v1(
        math_result=math_result,
        prepared_evidence=prepared,
    )

    assert decision.status == RESULT_PROJECTION_READY
    assert decision.projection is not None
    result_set = decision.projection.result_set
    assert result_set.source_sheet_refs == ("sheet-1",)
    assert result_set.relationship_refs == ("rel-1",)
    assert verify_service_1_result_set_integrity_v1(result_set) is True


def test_headless_identity_coercion_failure_is_http_400() -> None:
    server = create_service_1_headless_server_v1(host="127.0.0.1", port=0)
    thread = _serve(server)
    payload = {
        "schema_version": HEADLESS_REQUEST_SCHEMA_VERSION,
        "analysis_id": "sales_total",
        "ingestion_output": {},
        "confirmed_bindings": {"status": "CONFIRMED_BINDINGS"},
        "tenant_identity_contract": {"tenant_id": "tenant-a"},
    }
    try:
        status, body = _post_raw(
            server,
            HEADLESS_ROUTE_V1,
            json.dumps(payload).encode("utf-8"),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 400
    assert body["blocked_reason"] == "HEADLESS_IDENTITY_COERCION_FAILED"


def test_headless_rejects_oversized_json_before_product_root() -> None:
    server = create_service_1_headless_server_v1(host="127.0.0.1", port=0)
    thread = _serve(server)
    try:
        status, body = _post_raw(
            server,
            HEADLESS_ROUTE_V1,
            b"x" * (HEADLESS_MAX_JSON_BODY_BYTES_V1 + 1),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 413
    assert body["blocked_reason"] == "HEADLESS_BODY_TOO_LARGE"


def test_semantic_http_rejects_oversized_json_before_reading_payload() -> None:
    server = create_service_1_semantic_boundary_server_v1(host="127.0.0.1", port=0)
    thread = _serve(server)
    try:
        status, body = _post_raw(
            server,
            SEMANTIC_INITIAL_ROUTE_V1,
            b"x" * (SEMANTIC_MAX_JSON_BODY_BYTES_V1 + 1),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 413
    assert body["blocked_reason"] == "C2_SEMANTIC_BODY_TOO_LARGE"


def test_semantic_reentry_persists_followup_packet_not_previous_state(monkeypatch) -> None:
    store = Service1SemanticStateStoreV1()
    previous = {"status": "OWNER_DIALOGUE_REQUIRED", "owner_questions": [{"decision_id": "d1"}]}
    ref = store.put(previous)
    followup = {
        "status": "OWNER_DIALOGUE_FOLLOWUP",
        "case_id": "case-1",
        "requested_capability": None,
        "owner_questions": [{"decision_id": "d2"}],
        "validated_packet": {"decisions": []},
    }
    monkeypatch.setattr(
        semantic_boundary_module,
        "run_service_1_assisted_semantic_reentry_v1",
        lambda **_kwargs: followup,
    )

    response = execute_service_1_semantic_reentry_json_v1(
        {
            "schema_version": REENTRY_REQUEST_SCHEMA,
            "semantic_state_ref": ref,
            "owner_responses": [{"decision_id": "d1", "action": "ACCEPT"}],
            "owner_actor_id": "owner-1",
            "owner_actor_role": "OWNER",
        },
        state_store=store,
    )

    assert response["status"] == "OWNER_DIALOGUE_FOLLOWUP"
    assert response["semantic_state_ref"] == ref
    assert store.get(ref) is followup


def test_physical_lineage_reuses_packet_sheet_ref() -> None:
    packet = {
        "workbook_ref": "workbook:1",
        "sheet_refs": [{"sheet_name": "Ventas", "sheet_ref": "sheet:canonical:ventas"}],
    }
    lineage = _physical_lineage(
        [{"sheet_name": "Ventas", "source_kind": "xlsx"}],
        packet=packet,
    )

    assert lineage[0]["sheet_ref"] == "sheet:canonical:ventas"


@pytest.mark.parametrize(
    "bad_field,bad_value",
    [
        ("confidence", float("nan")),
        ("business_objects", 5),
    ],
)
def test_business_understanding_malformed_fields_fail_closed(
    bad_field: str,
    bad_value: object,
) -> None:
    table = {
        "sheet_name": "Ventas",
        "table_meaning": "Ventas",
        "grain": "una fila por venta",
        "business_objects": [],
        "processes": [],
        "semantic_groups": [],
        "confidence": 0.8,
    }
    table[bad_field] = bad_value
    result = validate_service_1_workbook_business_understanding_v1(
        candidate={
            "schema_version": BUSINESS_SCHEMA_VERSION,
            "authority": BUSINESS_AUTHORITY,
            "workbook_summary": "Libro de ventas",
            "tables": [table],
            "material_ambiguities": [],
        },
        workbook_semantic_context={"tables": [{"sheet_name": "Ventas"}]},
    )

    assert result["status"] == BUSINESS_BLOCKED
    assert result["blocked_reason"] == "BUSINESS_UNDERSTANDING_FIELD_INVALID"


def test_taxonomy_aliases_use_the_same_canonical_normalizer_as_headers() -> None:
    base = load_service_1_semantic_coordinate_taxonomy_v2()
    aliases = {
        axis: {value: tuple(items) for value, items in base.aliases[axis].items()}
        for axis in base.aliases
    }
    aliases["measure"]["price"] = aliases["measure"]["price"] + (
        "precio-unitario",
        "precio/unitario",
    )

    taxonomy = Service1SemanticCoordinateTaxonomyV2(
        schema_version=base.schema_version,
        status=base.status,
        axes=base.axes,
        labels=base.labels,
        aliases=aliases,
        business_families=base.business_families,
        operating_archetypes=base.operating_archetypes,
    )

    assert taxonomy.aliases["measure"]["price"].count("precio_unitario") == 1
