from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_tenant_schema_family_memory_v1 import (
    REVALIDATION_KNOWN_COMPATIBLE_DELTA,
    REVALIDATION_KNOWN_IDENTICAL,
    REVALIDATION_KNOWN_MATERIAL_DELTA,
    REVALIDATION_UNKNOWN_FAMILY,
    REVALIDATION_UNRESOLVED,
    Service1TenantSchemaFamilyMemoryErrorV1,
    build_service_1_scoped_semantic_mapping_refs_v1,
    build_service_1_tenant_schema_family_memory_v1,
    plan_service_1_schema_delta_revalidation_v1,
)
from pymia.smartpyme.service_1_tenant_schema_family_memory_store_v1 import (
    append_service_1_tenant_schema_family_memory_v1,
    list_service_1_tenant_schema_family_memory_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_store_v1 import (
    append_service_1_tenant_semantic_contract_v1,
    list_service_1_tenant_semantic_contracts_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    build_service_1_tenant_semantic_contract_v1,
)
from pymia.smartpyme.service_1_workbook_schema_identity_v1 import (
    build_service_1_workbook_schema_identity_v1,
)


def _candidate(
    columns: list[tuple[str, str]],
    *,
    table_key: str = "table:ventas",
    grain_kind: str = "ROW",
    key_column: str = "id",
) -> dict:
    return {
        "logical_table_id": table_key,
        "source_sheet_refs": ["Datos"],
        "source_region_refs": ["region:1"],
        "grain_state": "RESOLVED",
        "grain_candidate": {"kind": grain_kind, "key_refs": [key_column]},
        "primary_key_candidates": [
            {
                "key_kind": "PRIMARY",
                "column_refs": [key_column],
                "candidate_primary_key": True,
            }
        ],
        "unique_key_candidates": [],
        "provenance": {
            "structural_payload": {
                "columns": [
                    {
                        "normalized_header": name,
                        "inferred_type": dtype,
                        "nullability_class": "NONE",
                        "uniqueness_class": "UNIQUE" if name == key_column else "MATERIAL",
                        "candidate_primary_key": name == key_column,
                    }
                    for name, dtype in columns
                ]
            }
        },
    }


def _identity(
    columns: list[tuple[str, str]],
    *,
    table_key: str = "table:ventas",
    grain_kind: str = "ROW",
    key_column: str = "id",
) -> dict:
    result = build_service_1_workbook_schema_identity_v1(
        logical_table_candidates=[
            _candidate(columns, table_key=table_key, grain_kind=grain_kind, key_column=key_column)
        ],
        workbook_ref="renamed-file.xlsx",
    )
    assert result["status"] == "WORKBOOK_SCHEMA_READY"
    return result


def _semantic_contract(*, tenant_id: str = "tenant-a"):
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case-1",
        file_ref="sha256:book",
        region_ref="region:1",
        sheet_ref="Datos",
        column_ref="importe",
        question_ref="q-importe",
        owner_answer="OWNER_CONFIRMED",
        proposed_role="sales_amount",
        proposed_variable="sold_amount",
        confirmed_role="sales_amount",
        confirmation_scope="SEMANTIC_ROLE",
        timestamp="2026-08-21T18:00:00+00:00",
        provenance={"producer": "d6-test"},
    )
    return build_service_1_tenant_semantic_contract_v1(
        tenant_id=tenant_id,
        cliente_id=None,
        owner_actor_id="owner-1",
        owner_actor_role="OWNER",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        workbook_ref="sha256:book",
        expected_case_id="case-1",
        expected_sheet_ref="Datos",
        expected_question_ref="q-importe",
        source_column_name="importe",
        normalized_column_ref="importe",
        owner_confirmation_event=event,
    )


def test_d6_initial_family_record_is_tenant_scoped_and_never_authorizes_reuse() -> None:
    record = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("importe", "number")]),
    )

    assert record.schema_family_ref != "UNKNOWN"
    assert record.family_revision == 1
    assert record.automatic_reuse_authorized is False
    assert record.semantic_rebind_authorized is False
    assert record.runtime_authorized is False
    assert "renamed-file.xlsx" not in record.record_id


def test_d6_same_tenant_artifact_stores_semantic_and_schema_memory_without_parallel_store(tmp_path: Path) -> None:
    semantic = _semantic_contract()
    schema = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("importe", "number")]),
    )

    semantic_result = append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant-a", contract=semantic
    )
    schema_result = append_service_1_tenant_schema_family_memory_v1(
        base_dir=tmp_path, tenant_id="tenant-a", record=schema
    )

    assert semantic_result.path == schema_result.path
    assert semantic_result.path.name == "tenant_semantic_contracts.jsonl"
    assert list_service_1_tenant_semantic_contracts_v1(base_dir=tmp_path, tenant_id="tenant-a") == (semantic,)
    assert list_service_1_tenant_schema_family_memory_v1(base_dir=tmp_path, tenant_id="tenant-a") == (schema,)
    assert len(semantic_result.path.read_text(encoding="utf-8").splitlines()) == 2


def test_d6_owner_confirmed_semantics_are_projected_as_hints_only() -> None:
    contract = _semantic_contract()
    refs = build_service_1_scoped_semantic_mapping_refs_v1(
        tenant_id="tenant-a",
        semantic_contracts=[contract],
        semantic_scope_packet={
            "column_scopes": [
                {
                    "sheet_ref": "Datos",
                    "normalized_header": "importe",
                    "logical_table_ref": "table:ventas",
                }
            ]
        },
    )

    assert refs[0]["contract_id"] == contract.contract_id
    assert refs[0]["logical_table_ref"] == "table:ventas"
    assert refs[0]["historical_evidence_only"] is True
    assert refs[0]["automatic_reuse_authorized"] is False
    assert refs[0]["semantic_rebind_authorized"] is False


def test_d6_known_identical_schema_requires_no_revalidation_but_only_returns_hints() -> None:
    identity = _identity([("id", "text"), ("importe", "number")])
    record = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=identity,
        semantic_mapping_refs=[{"contract_id": "c1", "normalized_column_ref": "importe"}],
    )

    plan = plan_service_1_schema_delta_revalidation_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        current_schema_identity=identity,
        memory_records=[record],
    )

    assert plan["revalidation_state"] == REVALIDATION_KNOWN_IDENTICAL
    assert plan["revalidation_scope"] == []
    assert plan["historical_semantic_hints"][0]["contract_id"] == "c1"
    assert plan["automatic_reuse_authorized"] is False
    assert plan["semantic_rebind_authorized"] is False


def test_d6_compatible_column_delta_revalidates_only_d3_affected_scope() -> None:
    prior_identity = _identity([("id", "text"), ("importe", "number")])
    prior = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=prior_identity,
    )
    current = _identity([("id", "text"), ("importe", "number"), ("descuento", "number")])

    plan = plan_service_1_schema_delta_revalidation_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        current_schema_identity=current,
        memory_records=[prior],
    )

    assert plan["revalidation_state"] == REVALIDATION_KNOWN_COMPATIBLE_DELTA
    assert plan["revalidation_scope"] == plan["schema_delta"]["affected_scope"]
    assert any(item.endswith(".descuento") for item in plan["revalidation_scope"])
    assert not any(item.endswith(".importe") for item in plan["revalidation_scope"])
    assert plan["full_semantic_process_required"] is False


def test_d6_material_grain_delta_revalidates_d3_scope_and_not_whole_workbook() -> None:
    prior_identity = _identity([("id", "text"), ("importe", "number")], grain_kind="ROW")
    prior = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=prior_identity,
    )
    current = _identity([("id", "text"), ("importe", "number")], grain_kind="MONTH")

    plan = plan_service_1_schema_delta_revalidation_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        current_schema_identity=current,
        memory_records=[prior],
    )

    assert plan["revalidation_state"] == REVALIDATION_KNOWN_MATERIAL_DELTA
    assert plan["revalidation_scope"] == plan["schema_delta"]["affected_scope"]
    assert any(item.startswith("grain:") for item in plan["revalidation_scope"])
    assert plan["full_semantic_process_required"] is False


def test_d6_unknown_family_uses_normal_semantic_process_without_hints() -> None:
    prior = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("importe", "number")]),
    )
    unrelated = _identity([("codigo", "text"), ("descripcion", "text")], table_key="table:other", key_column="codigo")

    plan = plan_service_1_schema_delta_revalidation_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        current_schema_identity=unrelated,
        memory_records=[prior],
    )

    assert plan["revalidation_state"] == REVALIDATION_UNKNOWN_FAMILY
    assert plan["full_semantic_process_required"] is True
    assert plan["historical_semantic_hints"] == []


def test_d6_ambiguous_family_match_fails_closed() -> None:
    family_a = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("a", "number")]),
    )
    family_b = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("b", "number")]),
    )
    current = _identity([("id", "text"), ("a", "number"), ("b", "number")])

    plan = plan_service_1_schema_delta_revalidation_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        current_schema_identity=current,
        memory_records=[family_a, family_b],
    )

    assert plan["revalidation_state"] == REVALIDATION_UNRESOLVED
    assert plan["status"] == "BLOCKED"
    assert plan["automatic_reuse_authorized"] is False


def test_d6_schema_family_lineage_is_append_only_and_cross_tenant_safe(tmp_path: Path) -> None:
    first = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("importe", "number")]),
    )
    second = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=_identity([("id", "text"), ("importe", "number"), ("descuento", "number")]),
        prior_record=first,
    )

    append_service_1_tenant_schema_family_memory_v1(base_dir=tmp_path, tenant_id="tenant-a", record=first)
    append_service_1_tenant_schema_family_memory_v1(base_dir=tmp_path, tenant_id="tenant-a", record=second)
    records = list_service_1_tenant_schema_family_memory_v1(base_dir=tmp_path, tenant_id="tenant-a")

    assert [item.family_revision for item in records] == [1, 2]
    assert records[1].prior_record_id == records[0].record_id
    assert records[1].delta_affected_scope
    with pytest.raises(Service1TenantSchemaFamilyMemoryErrorV1):
        append_service_1_tenant_schema_family_memory_v1(base_dir=tmp_path, tenant_id="tenant-b", record=first)
