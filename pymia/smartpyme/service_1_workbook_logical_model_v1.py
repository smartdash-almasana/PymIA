"""Canonical Workbook Logical Model evidence coordinator for Servicio 1 (D7).

Composes D1-D6 evidence before the existing semantic/P7/P8/F7/F8/F9 chain.
This is not a second product pipeline and grants no downstream authority.
"""
from __future__ import annotations

from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_logical_relationship_graph_v1 import build_service_1_logical_relationship_graph_v1
from pymia.smartpyme.service_1_logical_table_candidate_v1 import STATUS_READY as LOGICAL_TABLES_READY, build_service_1_logical_table_candidates_v1
from pymia.smartpyme.service_1_region_evidence_v1 import STATUS_READY as REGION_EVIDENCE_READY, build_service_1_region_evidence_from_canonical_ingestion_v1
from pymia.smartpyme.service_1_table_scoped_semantic_context_v1 import STATUS_READY as TABLE_SCOPE_READY, build_service_1_table_scoped_semantic_context_v1
from pymia.smartpyme.service_1_tenant_schema_family_memory_v1 import REVALIDATION_UNKNOWN_FAMILY, plan_service_1_schema_delta_revalidation_v1
from pymia.smartpyme.service_1_workbook_profiler_v1 import STATUS_READY as WORKBOOK_PROFILE_READY, build_service_1_workbook_profile_v1
from pymia.smartpyme.service_1_workbook_schema_identity_v1 import STATUS_READY as SCHEMA_IDENTITY_READY, build_service_1_workbook_schema_identity_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_WORKBOOK_LOGICAL_MODEL_V1"
STATUS_READY: Final[str] = "WORKBOOK_LOGICAL_MODEL_READY"
STATUS_UNRESOLVED: Final[str] = "UNRESOLVED"
STATUS_BLOCKED: Final[str] = "BLOCKED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized", "tool_execution_authorized", "product_ready",
    "delivery_authorized", "diagnosis_generated", "join_execution_authorized",
    "computability_authorized", "automatic_reuse_authorized", "semantic_rebind_authorized",
)


def build_service_1_workbook_logical_model_v1(
    *,
    ingestion_output: Mapping[str, Any],
    tenant_id: str | None = None,
    source_system_ref: str | None = None,
    source_context_ref: str | None = None,
    schema_family_memory_records: Sequence[Mapping[str, Any] | Any] = (),
    owner_relationship_confirmation_events: Sequence[Any] = (),
) -> dict[str, Any]:
    if not isinstance(ingestion_output, Mapping) or not ingestion_output:
        return _blocked("INGESTION_OUTPUT_REQUIRED")
    if any(bool(ingestion_output.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked("INGESTION_OUTPUT_AUTHORITY_FORBIDDEN")
    case_id = str(ingestion_output.get("case_id") or "").strip()
    workbook_ref = str(ingestion_output.get("source_file_ref") or ingestion_output.get("filename") or "").strip()
    if not case_id or not workbook_ref:
        return _blocked("CASE_AND_WORKBOOK_REF_REQUIRED")
    if not isinstance(ingestion_output.get("normalized_tables"), list) or not ingestion_output.get("normalized_tables"):
        return _blocked("NORMALIZED_TABLES_REQUIRED")
    if not isinstance(ingestion_output.get("column_refs"), list) or not ingestion_output.get("column_refs"):
        return _blocked("COLUMN_REFS_REQUIRED")

    canonical_packet = _canonical_packet(ingestion_output)
    workbook_profile = build_service_1_workbook_profile_v1(ingestion_output=dict(ingestion_output))
    if workbook_profile.get("status") != WORKBOOK_PROFILE_READY:
        return _unresolved("WORKBOOK_PROFILE_UNAVAILABLE", workbook_profile=workbook_profile)

    region_evidence = build_service_1_region_evidence_from_canonical_ingestion_v1(canonical_packet=canonical_packet)
    if region_evidence.get("status") != REGION_EVIDENCE_READY:
        return _unresolved(
            str(region_evidence.get("blocked_reason") or "REGION_EVIDENCE_UNRESOLVED"),
            workbook_profile=workbook_profile,
            region_evidence=region_evidence,
        )

    logical_tables = build_service_1_logical_table_candidates_v1(
        canonical_packet=canonical_packet,
        region_evidence=region_evidence,
        workbook_profile=workbook_profile,
    )
    if logical_tables.get("status") != LOGICAL_TABLES_READY:
        return _unresolved(
            str(logical_tables.get("blocked_reason") or "LOGICAL_TABLES_UNRESOLVED"),
            workbook_profile=workbook_profile,
            region_evidence=region_evidence,
            logical_tables=logical_tables,
        )

    schema_identity = build_service_1_workbook_schema_identity_v1(
        logical_table_candidates=logical_tables,
        workbook_profile=workbook_profile,
        workbook_ref=workbook_ref,
    )
    if schema_identity.get("status") != SCHEMA_IDENTITY_READY:
        return _unresolved(
            str(schema_identity.get("blocked_reason") or "SCHEMA_IDENTITY_UNRESOLVED"),
            workbook_profile=workbook_profile,
            region_evidence=region_evidence,
            logical_tables=logical_tables,
            schema_identity=schema_identity,
        )

    relationship_graph = build_service_1_logical_relationship_graph_v1(
        logical_table_candidates=logical_tables,
        workbook_profile=workbook_profile,
        schema_identity=schema_identity,
        owner_confirmation_events=owner_relationship_confirmation_events,
    )

    table_scoped_semantics = build_service_1_table_scoped_semantic_context_v1(
        column_refs=tuple(
            item for item in ingestion_output.get("column_refs") or () if isinstance(item, Mapping)
        ),
        logical_table_candidates=logical_tables,
        logical_relationship_graph=relationship_graph,
    )
    if table_scoped_semantics.get("status") != TABLE_SCOPE_READY:
        return _unresolved(
            "TABLE_SCOPED_SEMANTICS_UNRESOLVED",
            workbook_profile=workbook_profile,
            region_evidence=region_evidence,
            logical_tables=logical_tables,
            schema_identity=schema_identity,
            relationship_graph=relationship_graph,
            table_scoped_semantics=table_scoped_semantics,
        )

    schema_revalidation = _schema_revalidation(
        tenant_id=tenant_id,
        source_system_ref=source_system_ref,
        source_context_ref=source_context_ref,
        schema_identity=schema_identity,
        memory_records=schema_family_memory_records,
    )
    if schema_revalidation.get("status") == STATUS_BLOCKED:
        return _unresolved(
            str(schema_revalidation.get("blocked_reason") or "SCHEMA_REVALIDATION_UNRESOLVED"),
            workbook_profile=workbook_profile,
            region_evidence=region_evidence,
            logical_tables=logical_tables,
            schema_identity=schema_identity,
            relationship_graph=relationship_graph,
            table_scoped_semantics=table_scoped_semantics,
            schema_revalidation=schema_revalidation,
        )

    projection = _p7_p8_projection(
        logical_tables=logical_tables,
        schema_identity=schema_identity,
        relationship_graph=relationship_graph,
        table_scoped_semantics=table_scoped_semantics,
        schema_revalidation=schema_revalidation,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "workbook_ref": workbook_ref,
        "workbook_profile": workbook_profile,
        "region_evidence": region_evidence,
        "logical_tables": logical_tables,
        "schema_identity": schema_identity,
        "relationship_graph": relationship_graph,
        "table_scoped_semantics": table_scoped_semantics,
        "schema_revalidation": schema_revalidation,
        "p7_p8_evidence_projection": projection,
        **_false_authority(),
    }


def _canonical_packet(ingestion_output: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "INGESTION_OUTPUT_READY",
        "case_id": ingestion_output.get("case_id"),
        "filename": ingestion_output.get("filename"),
        "ingestion_output": dict(ingestion_output),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _schema_revalidation(
    *,
    tenant_id: str | None,
    source_system_ref: str | None,
    source_context_ref: str | None,
    schema_identity: Mapping[str, Any],
    memory_records: Sequence[Mapping[str, Any] | Any],
) -> dict[str, Any]:
    tenant = str(tenant_id or "").strip()
    system_ref = str(source_system_ref or "").strip()
    context_ref = str(source_context_ref or "").strip()
    if not (tenant and system_ref and context_ref):
        return {
            "schema_version": SCHEMA_VERSION,
            "status": STATUS_READY,
            "blocked_reason": None,
            "revalidation_state": REVALIDATION_UNKNOWN_FAMILY,
            "schema_family_ref": None,
            "matched_memory_record_id": None,
            "schema_delta": None,
            "affected_scope": [],
            "revalidation_scope": [],
            "historical_semantic_hints": [],
            "historical_relationship_evidence_refs": [],
            "historical_evidence_only": True,
            "full_semantic_process_required": True,
            "tenant_context_available": False,
            **_false_authority(),
        }
    result = dict(plan_service_1_schema_delta_revalidation_v1(
        tenant_id=tenant,
        source_system_ref=system_ref,
        source_context_ref=context_ref,
        current_schema_identity=schema_identity,
        memory_records=memory_records,
    ))
    result["tenant_context_available"] = True
    return result


def _p7_p8_projection(
    *,
    logical_tables: Mapping[str, Any],
    schema_identity: Mapping[str, Any],
    relationship_graph: Mapping[str, Any],
    table_scoped_semantics: Mapping[str, Any],
    schema_revalidation: Mapping[str, Any],
) -> dict[str, Any]:
    candidates = [dict(item) for item in logical_tables.get("candidates") or () if isinstance(item, Mapping)]
    scopes = [dict(item) for item in table_scoped_semantics.get("column_scopes") or () if isinstance(item, Mapping)]
    historical_semantic_hints = [
        dict(item)
        for item in schema_revalidation.get("historical_semantic_hints") or ()
        if isinstance(item, Mapping)
    ]
    owner_evidence_refs = [
        str(item.get("contract_id") or "").strip()
        for item in historical_semantic_hints
        if str(item.get("contract_id") or "").strip()
    ]
    return {
        "logical_table_ids": [str(item.get("logical_table_id") or "") for item in candidates],
        "source_grains": [
            {
                "logical_table_id": item.get("logical_table_id"),
                "grain_state": item.get("grain_state"),
                "grain_candidate": item.get("grain_candidate"),
            }
            for item in candidates
        ],
        "selected_source_bindings": [
            {
                "column_ref": item.get("column_ref"),
                "logical_table_ref": item.get("logical_table_ref"),
                "region_refs": list(item.get("region_refs") or ()),
                "grain_ref": item.get("grain_ref"),
            }
            for item in scopes
        ],
        "relationship_graph_ref": relationship_graph.get("graph_ref"),
        "relationship_path_evidence": [
            str(item.get("relationship_ref") or "")
            for item in relationship_graph.get("relationships") or ()
            if isinstance(item, Mapping) and str(item.get("relationship_ref") or "").strip()
        ],
        "fanout_certificate": dict(relationship_graph.get("fanout_certificate") or {}),
        "schema_fingerprint": schema_identity.get("schema_fingerprint"),
        "schema_delta_state": schema_revalidation.get("revalidation_state"),
        "affected_scope": list(schema_revalidation.get("affected_scope") or ()),
        "owner_evidence_refs": owner_evidence_refs,
        "historical_semantic_hints": historical_semantic_hints,
        "historical_relationship_evidence_refs": list(
            schema_revalidation.get("historical_relationship_evidence_refs") or ()
        ),
        "historical_evidence_only": True,
        **_false_authority(),
    }


def _false_authority() -> dict[str, bool]:
    return {flag: False for flag in _AUTHORITY_FLAGS}


def _unresolved(reason: str, **parts: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_UNRESOLVED,
        "blocked_reason": reason,
        **parts,
        **_false_authority(),
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        **_false_authority(),
    }


__all__ = [
    "SCHEMA_VERSION", "STATUS_READY", "STATUS_UNRESOLVED", "STATUS_BLOCKED",
    "build_service_1_workbook_logical_model_v1",
]
