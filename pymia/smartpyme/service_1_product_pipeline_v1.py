"""Single product application root for Servicio 1."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_derived_evidence_v1 import (
    STATUS_BLOCKED as DERIVED_EVIDENCE_BLOCKED,
    STATUS_NEEDS_EVIDENCE as DERIVED_EVIDENCE_NEEDS,
    STATUS_READY as DERIVED_EVIDENCE_READY,
    build_service_1_derived_evidence_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    STATUS_OWNER_FOLLOWUP,
    STATUS_OWNER_QUESTIONS,
    build_computability_decision_from_confirmed_bindings_v1,
    run_initial_pass,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_BLOCKED as ASSISTED_SEMANTIC_BLOCKED,
    STATUS_CONFIRMED as ASSISTED_SEMANTIC_CONFIRMED,
    STATUS_OWNER_DIALOGUE_FOLLOWUP as ASSISTED_SEMANTIC_FOLLOWUP,
    STATUS_OWNER_DIALOGUE_REQUIRED as ASSISTED_SEMANTIC_OWNER_REQUIRED,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)
from pymia.smartpyme.service_1_liq_001_evaluator_v1 import (
    CAPABILITY_REF as LIQ_001_CAPABILITY_REF,
    STATUS_EVALUATED as LIQ_001_STATUS_EVALUATED,
    evaluate_liq_001_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_liq_001_outcome_v1 import (
    STATUS_READY as LIQ_001_OUTCOME_READY,
    build_liq_001_outcome_v1,
    deliver_liq_001_outcome_xlsx_v1,
)
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_EVALUATED as GENERIC_STATUS_EVALUATED,
    execute_generic_capability_v1 as _execute_generic_capability_v1_raw,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_COMPUTABLE as P8_STATUS_COMPUTABLE,
    build_service_1_composite_governed_computation_input_v1,
)
from pymia.smartpyme.service_1_capability_registry_v1 import (
    get_capability_definition_v1,
)
from pymia.smartpyme.service_1_pipeline_v1 import (
    Service1PipelineToolRequestV1,
    run_service_1_pipeline_v1,
)
from pymia.smartpyme.service_1_ren_001_evaluator_v1 import (
    CAPABILITY_REF as REN_001_CAPABILITY_REF,
    STATUS_EVALUATED as REN_001_STATUS_EVALUATED,
)
from pymia.smartpyme.service_1_ren_001_normalized_evidence_v1 import (
    evaluate_ren_001_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_ren_001_outcome_v1 import (
    STATUS_READY as REN_001_OUTCOME_READY,
    build_ren_001_outcome_v1,
    deliver_ren_001_outcome_xlsx_v1,
)
from pymia.smartpyme.service_1_reconciliation_product_request_v1 import (
    STATUS_BLOCKED as RECONCILIATION_STATUS_BLOCKED,
    STATUS_NEEDS_EVIDENCE as RECONCILIATION_STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_OWNER as RECONCILIATION_STATUS_NEEDS_OWNER,
    STATUS_REVIEW_READY as RECONCILIATION_STATUS_REVIEW_READY,
    build_service_1_reconciliation_product_request_v1,
)
from pymia.smartpyme.service_1_consorcios_collection_aging_v1 import (
    build_collection_aging_product_request_v1,
)
from pymia.smartpyme.service_1_consorcios_expense_variance_v1 import (
    build_expense_variance_product_request_v1,
)
from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    STATUS_PREPARED as F7_STATUS_PREPARED,
    build_service_1_analysis_evidence_preparation_v1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    STATUS_EVALUATED as F8_STATUS_EVALUATED,
    execute_service_1_analysis_math_v1,
)
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_READY as F9_STATUS_READY,
    build_service_1_analysis_result_projection_v1,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    F12_COMMERCIAL_ANALYSIS_IDS,
    STATUS_READY as F10_STATUS_READY,
    build_service_1_dynamic_analysis_discovery_v1,
)
from pymia.smartpyme.service_1_result_memory_v1 import Service1ResultMemoryErrorV1
from pymia.smartpyme.service_1_workbook_logical_model_v1 import (
    STATUS_READY as WORKBOOK_LOGICAL_MODEL_READY,
    build_service_1_workbook_logical_model_v1,
)
from pymia.smartpyme.service_1_result_memory_wiring_v1 import (
    build_service_1_result_memory_from_execution_v1,
)

SCHEMA_VERSION = "SERVICE_1_PRODUCT_PIPELINE_V1"
STATUS_READY = "PRODUCT_PIPELINE_READY"
STATUS_COMPUTATION_PLAN_READY = "COMPUTATION_PLAN_READY"
STATUS_NEEDS_OWNER = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED = "BLOCKED"
STATUS_RECONCILIATION_REVIEW_READY = RECONCILIATION_STATUS_REVIEW_READY
STATUS_RECONCILIATION_NEEDS_OWNER = RECONCILIATION_STATUS_NEEDS_OWNER
STATUS_RECONCILIATION_NEEDS_EVIDENCE = RECONCILIATION_STATUS_NEEDS_EVIDENCE


def _persist_governed_analysis_result_memory_v1(
    *,
    tenant_identity_contract: Any,
    persist_result_memory: Any,
    governed_analysis_input: Any,
    result_projection: Any,
    confirmed_bindings: Mapping[str, Any],
    ingestion_output: Mapping[str, Any],
) -> dict[str, Any]:
    """Persist F9 output without making F13 an execution authority."""
    if tenant_identity_contract is None:
        return {
            "status": "NOT_PERSISTED",
            "reason": "TENANT_IDENTITY_REQUIRED",
            "persisted": False,
        }
    if persist_result_memory is None:
        return {
            "status": "NOT_PERSISTED",
            "reason": "RESULT_MEMORY_ADAPTER_UNAVAILABLE",
            "persisted": False,
        }
    try:
        record = build_service_1_result_memory_from_execution_v1(
            identity_contract=tenant_identity_contract,
            governed_analysis_input=governed_analysis_input,
            result_projection=result_projection,
            semantic_run=confirmed_bindings,
            ingestion_output=ingestion_output,
        )
    except (Service1ResultMemoryErrorV1, TypeError, ValueError) as exc:
        return {
            "status": "NEEDS_EVIDENCE",
            "reason": getattr(exc, "code", None) or "RESULT_MEMORY_CONTRACT_BLOCKED",
            "detail": getattr(exc, "detail", None) or str(exc),
            "persisted": False,
        }
    try:
        persisted = bool(persist_result_memory(record))
    except Exception:
        return {
            "status": "PERSISTENCE_ERROR",
            "reason": "RESULT_MEMORY_PERSISTENCE_FAILED",
            "persisted": False,
            "memory_record_id": record.memory_record_id,
        }
    if not persisted:
        return {
            "status": "PERSISTENCE_ERROR",
            "reason": "RESULT_MEMORY_PERSISTENCE_UNCONFIRMED",
            "persisted": False,
            "memory_record_id": record.memory_record_id,
        }
    return {
        "status": "PERSISTED",
        "reason": None,
        "persisted": True,
        "memory_record_id": record.memory_record_id,
        "period": record.period.to_dict(),
        "artifact_ref": record.artifact_ref,
        "result_set_integrity_digest": record.result_set_integrity_digest,
        "executed_at": record.executed_at,
    }


def run_service_1_governed_analysis_v1(
    *,
    ingestion_output: Mapping[str, Any],
    confirmed_bindings: Mapping[str, Any],
    analysis_id: str,
    tenant_identity_contract: Any = None,
    persist_result_memory: Any = None,
) -> dict[str, Any]:
    """Canonical F12 execution entry: F10/P7/P8 -> F7 -> F8 -> F9 -> F13.

    The caller supplies already-governed canonical ingestion and owner-confirmed
    semantics. This root re-runs discovery/computability and owns all productive
    analytical coordination. The web layer may request an ``analysis_id`` and
    render this packet, but it must not execute F7/F8/F9 itself.
    """
    requested_analysis_id = str(analysis_id or "").strip()
    if not requested_analysis_id:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "blocked_reason": "ANALYSIS_ID_REQUIRED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
    if (
        not isinstance(confirmed_bindings, Mapping)
        or confirmed_bindings.get("status") != STATUS_CONFIRMED_BINDINGS
    ):
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "blocked_reason": "CONFIRMED_BINDINGS_REQUIRED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
    if not isinstance(ingestion_output, Mapping):
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "blocked_reason": "CANONICAL_INGESTION_REQUIRED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    discovery = build_service_1_dynamic_analysis_discovery_v1(
        confirmed_bindings=confirmed_bindings,
        commercially_exposed_analysis_ids=F12_COMMERCIAL_ANALYSIS_IDS,
    )
    if discovery.status != F10_STATUS_READY:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "blocked_reason": discovery.blocked_reason or "F12_DISCOVERY_NOT_READY",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    item = next(
        (value for value in discovery.analyses if value.analysis_id == requested_analysis_id),
        None,
    )
    if item is None or not item.commercially_requested:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "blocked_reason": "ANALYSIS_NOT_COMMERCIALLY_REQUESTED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
    if not item.commercially_exposed or item.governed_analysis_input is None:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "title": item.title,
            "question": item.question,
            "blocked_reason": item.p8_reason or item.p7_reason or "ANALYSIS_NOT_COMPUTABLE",
            "missing_role_groups": [list(group) for group in item.missing_role_groups],
            "missing_relationship_evidence": list(item.missing_relationship_evidence),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    governed = item.governed_analysis_input
    prepared = build_service_1_analysis_evidence_preparation_v1(
        case_id=governed.case_id,
        governed_analysis_input=governed,
        ingestion_output=dict(ingestion_output),
    )
    if prepared.status != F7_STATUS_PREPARED or prepared.prepared_evidence is None:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "title": item.title,
            "question": item.question,
            "blocked_reason": prepared.reason or "F7_PREPARATION_BLOCKED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    math = execute_service_1_analysis_math_v1(
        case_id=governed.case_id,
        governed_analysis_input=governed,
        prepared_evidence=prepared.prepared_evidence,
    )
    if math.status != F8_STATUS_EVALUATED or math.result is None:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "title": item.title,
            "question": item.question,
            "blocked_reason": math.reason or "F8_EXECUTION_BLOCKED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    projection = build_service_1_analysis_result_projection_v1(
        math_result=math.result,
        prepared_evidence=prepared.prepared_evidence,
        currency_code=None,
    )
    if projection.status != F9_STATUS_READY or projection.projection is None:
        return {
            "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
            "status": "BLOCKED",
            "analysis_id": requested_analysis_id,
            "title": item.title,
            "question": item.question,
            "blocked_reason": projection.reason or "F9_PROJECTION_BLOCKED",
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    result_projection = projection.projection
    memory = _persist_governed_analysis_result_memory_v1(
        tenant_identity_contract=tenant_identity_contract,
        persist_result_memory=persist_result_memory,
        governed_analysis_input=governed,
        result_projection=result_projection,
        confirmed_bindings=confirmed_bindings,
        ingestion_output=ingestion_output,
    )
    return {
        "schema_version": "SERVICE_1_F12_ANALYSIS_EXECUTION_V1",
        "status": "READY",
        "analysis_id": requested_analysis_id,
        "title": item.title,
        "question": item.question,
        "result_set": result_projection.result_set.to_dict(),
        "findings": [finding.to_dict() for finding in result_projection.findings],
        "outcome": result_projection.outcome.to_dict(),
        "result_memory": memory,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def execute_generic_capability_v1(*, capability_ref: str, governed_computation_input: object, normalized_tables: object, column_refs: object, governed_results: object = None) -> dict[str, object]:
    """Product-root execution boundary: consume canonical P8 input directly."""
    return _execute_generic_capability_v1_raw(
        capability_ref=capability_ref,
        computation_plan=None,
        governed_computation_input=governed_computation_input,
        normalized_tables=normalized_tables,
        column_refs=column_refs,
        governed_results=governed_results,
    )


def run_service_1_product_pipeline_v1(
    *,
    ingestion_output: Any,
    tool_requests: Sequence[Service1PipelineToolRequestV1],
    output_dir: str | Path,
    sheet_name: str = "sheet1",
    owner_answers: Any = None,
    semantic_run_override: Mapping[str, Any] | None = None,
    requested_capability: str | None = None,
    deliver_result: bool = False,
    governed_results: object = None,
    reconciliation_request: Mapping[str, Any] | None = None,
    collection_aging_request: Mapping[str, Any] | None = None,
    expense_variance_request: Mapping[str, Any] | None = None,
    semantic_provider: Any = None,
    semantic_assistance_state: Mapping[str, Any] | None = None,
    semantic_dialogue_responses: Sequence[Mapping[str, Any]] | None = None,
    semantic_owner_actor_id: str | None = None,
    semantic_owner_actor_role: str | None = None,
    compatible_tenant_memory_hints: Sequence[Mapping[str, Any]] = (),
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = (),
    semantic_scope_capabilities: Sequence[str] = (),
    use_assisted_semantics: bool = False,
    tenant_id: str | None = None,
    source_system_ref: str | None = None,
    source_context_ref: str | None = None,
    schema_family_memory_records: Sequence[Mapping[str, Any] | Any] = (),
) -> dict[str, Any]:
    # Legacy callers may still pass ``sheet_name``. D7 never uses that value to
    # manufacture semantic identity; canonical sheet-qualified column_refs are
    # the only semantic source identity. Keep the argument only for API compatibility.
    _ = sheet_name
    if expense_variance_request is not None:
        if (
            collection_aging_request is not None
            or reconciliation_request is not None
            or requested_capability is not None
            or bool(tool_requests)
            or deliver_result
            or owner_answers is not None
            or semantic_run_override is not None
            or governed_results is not None
        ):
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="EXPENSE_VARIANCE_REQUEST_MUST_BE_EXCLUSIVE",
            )
        variance_run = build_expense_variance_product_request_v1(request=dict(expense_variance_request))
        if variance_run.get("status") != "EXPENSE_VARIANCE_REVIEW_READY":
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason=str(variance_run.get("reason") or variance_run.get("status") or "EXPENSE_VARIANCE_REQUEST_BLOCKED"),
                expense_variance_run=variance_run,
            )
        return _packet(
            status="EXPENSE_VARIANCE_REVIEW_READY",
            computation_result=variance_run.get("computation_result"),
            bounded_outcome=variance_run.get("bounded_outcome"),
            expense_variance_run=variance_run,
        )

    if collection_aging_request is not None:
        if (
            reconciliation_request is not None
            or requested_capability is not None
            or bool(tool_requests)
            or deliver_result
            or owner_answers is not None
            or semantic_run_override is not None
            or governed_results is not None
        ):
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="COLLECTION_AGING_REQUEST_MUST_BE_EXCLUSIVE",
            )
        aging_run = build_collection_aging_product_request_v1(request=dict(collection_aging_request))
        if aging_run.get("status") != "AGING_REVIEW_READY":
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason=str(aging_run.get("reason") or aging_run.get("status") or "AGING_REQUEST_BLOCKED"),
                collection_aging_run=aging_run,
            )
        return _packet(
            status="AGING_REVIEW_READY",
            computation_result=aging_run.get("computation_result"),
            bounded_outcome=aging_run.get("bounded_outcome"),
            collection_aging_run=aging_run,
        )

    if reconciliation_request is not None:
        if (
            requested_capability is not None
            or bool(tool_requests)
            or deliver_result
            or owner_answers is not None
            or semantic_run_override is not None
            or governed_results is not None
        ):
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="RECONCILIATION_REQUEST_MUST_BE_EXCLUSIVE",
            )
        reconciliation_run = build_service_1_reconciliation_product_request_v1(
            reconciliation_request=reconciliation_request,
        )
        reconciliation_status = str(reconciliation_run.get("status") or "")
        if reconciliation_status == RECONCILIATION_STATUS_REVIEW_READY:
            product_status = STATUS_RECONCILIATION_REVIEW_READY
            blocked_reason = None
        elif reconciliation_status == RECONCILIATION_STATUS_NEEDS_OWNER:
            product_status = STATUS_RECONCILIATION_NEEDS_OWNER
            blocked_reason = reconciliation_run.get("reason")
        elif reconciliation_status == RECONCILIATION_STATUS_NEEDS_EVIDENCE:
            product_status = STATUS_RECONCILIATION_NEEDS_EVIDENCE
            blocked_reason = reconciliation_run.get("reason")
        else:
            product_status = STATUS_BLOCKED
            blocked_reason = (
                reconciliation_run.get("reason")
                or RECONCILIATION_STATUS_BLOCKED
            )
        return _packet(
            status=product_status,
            blocked_reason=blocked_reason,
            reconciliation_run=reconciliation_run,
        )

    workbook_logical_model = None
    if (
        isinstance(ingestion_output, Mapping)
        and isinstance(ingestion_output.get("normalized_tables"), list)
        and bool(ingestion_output.get("normalized_tables"))
        and isinstance(ingestion_output.get("column_refs"), list)
        and bool(ingestion_output.get("column_refs"))
    ):
        workbook_logical_model = build_service_1_workbook_logical_model_v1(
            ingestion_output=ingestion_output,
            tenant_id=tenant_id,
            source_system_ref=source_system_ref,
            source_context_ref=source_context_ref,
            schema_family_memory_records=schema_family_memory_records,
        )
        if workbook_logical_model.get("status") != WORKBOOK_LOGICAL_MODEL_READY:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason=str(
                    workbook_logical_model.get("blocked_reason")
                    or "WORKBOOK_LOGICAL_MODEL_UNRESOLVED"
                ),
                workbook_logical_model=workbook_logical_model,
            )

    assisted_semantic_requested = any(
        (
            use_assisted_semantics,
            semantic_provider is not None,
            semantic_assistance_state is not None,
            semantic_dialogue_responses is not None,
        )
    )
    assisted_state = None
    if assisted_semantic_requested:
        if workbook_logical_model is None:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="WORKBOOK_LOGICAL_MODEL_REQUIRED_FOR_ASSISTED_SEMANTICS",
            )
        if owner_answers is not None or semantic_run_override is not None:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="ASSISTED_SEMANTIC_AND_PRECONFIRMED_SEMANTIC_CONFLICT",
            )
        if requested_capability is None:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="ASSISTED_SEMANTIC_REQUIRES_REQUESTED_CAPABILITY",
            )
        if semantic_assistance_state is None:
            if semantic_dialogue_responses is not None:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="ASSISTED_SEMANTIC_STATE_REQUIRED_FOR_OWNER_REENTRY",
                )
            assisted_state = run_service_1_assisted_semantic_initial_v1(
                ingestion_output=ingestion_output,
                requested_capability=requested_capability,
                provider=semantic_provider,
                compatible_tenant_memory_hints=compatible_tenant_memory_hints,
                semantic_scope_capabilities=semantic_scope_capabilities,
                logical_table_candidates=workbook_logical_model.get("logical_tables"),
                logical_relationship_graph=workbook_logical_model.get("relationship_graph"),
            )
            assisted_state = dict(assisted_state or {})
            assisted_state["workbook_logical_model_ref"] = str(
                (workbook_logical_model.get("schema_identity") or {}).get("schema_fingerprint")
                or ""
            )
        else:
            current_case_id = str(
                ingestion_output.get("case_id") if isinstance(ingestion_output, dict) else ""
            ).strip()
            state_case_id = str(semantic_assistance_state.get("case_id") or "").strip()
            state_model_ref = str(
                semantic_assistance_state.get("workbook_logical_model_ref") or ""
            ).strip()
            current_model_ref = str(
                (workbook_logical_model.get("schema_identity") or {}).get("schema_fingerprint")
                or ""
            ).strip()
            state_capability = str(
                semantic_assistance_state.get("requested_capability") or ""
            ).strip()
            state_scope_capabilities = {
                str(item or "").strip()
                for item in (semantic_assistance_state.get("semantic_scope_capabilities") or ())
                if str(item or "").strip()
            }
            capability_matches_state = (
                state_capability == requested_capability
                or requested_capability in state_scope_capabilities
            )
            if (
                not current_case_id
                or current_case_id != state_case_id
                or (state_model_ref and state_model_ref != current_model_ref)
                or not capability_matches_state
            ):
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="ASSISTED_SEMANTIC_STATE_CONTEXT_MISMATCH",
                    semantic_assistance_state=dict(semantic_assistance_state),
                )
            if semantic_dialogue_responses is None:
                assisted_state = dict(semantic_assistance_state)
            else:
                assisted_state = run_service_1_assisted_semantic_reentry_v1(
                    previous_state=dict(semantic_assistance_state),
                    owner_responses=semantic_dialogue_responses,
                    owner_actor_id=str(semantic_owner_actor_id or ""),
                    owner_actor_role=str(semantic_owner_actor_role or ""),
                    file_ref=str(
                        (ingestion_output or {}).get("source_file_ref")
                        or (ingestion_output or {}).get("filename")
                        or ""
                    ).strip()
                    or None,
                )

        assisted_state = dict(assisted_state or {})
        assisted_state["workbook_logical_model_ref"] = str(
            (workbook_logical_model.get("schema_identity") or {}).get("schema_fingerprint")
            or ""
        )
        assisted_status = str((assisted_state or {}).get("status") or "")
        if assisted_status in {
            ASSISTED_SEMANTIC_OWNER_REQUIRED,
            ASSISTED_SEMANTIC_FOLLOWUP,
        }:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                owner_questions=list((assisted_state or {}).get("owner_questions") or []),
                semantic_assistance_state=assisted_state,
                workbook_logical_model=workbook_logical_model,
            )
        if assisted_status == ASSISTED_SEMANTIC_BLOCKED:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason=(assisted_state or {}).get("blocked_reason")
                or "ASSISTED_SEMANTIC_BLOCKED",
                semantic_assistance_state=assisted_state,
            )
        if assisted_status != ASSISTED_SEMANTIC_CONFIRMED:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="ASSISTED_SEMANTIC_STATE_INVALID",
                semantic_assistance_state=assisted_state,
            )
        semantic_run = (assisted_state or {}).get("semantic_run")
    else:
        if owner_answers is not None:
            return _packet(
                status=STATUS_BLOCKED,
                blocked_reason="LEGACY_OWNER_ANSWERS_REQUIRE_UPSTREAM_COMPATIBILITY",
            )
        if semantic_run_override is None:
            semantic_run = run_initial_pass(
                ingestion_output=ingestion_output,
            )
        else:
            semantic_run = dict(semantic_run_override)
            current_case_id = str(
                ingestion_output.get("case_id") if isinstance(ingestion_output, dict) else ""
            ).strip()
            semantic_case_id = str(
                ((semantic_run.get("bridge_packet") or {}).get("case_id"))
                if isinstance(semantic_run.get("bridge_packet"), dict)
                else ""
            ).strip()
            if current_case_id and semantic_case_id and current_case_id != semantic_case_id:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason="SEMANTIC_RUN_OVERRIDE_CONTEXT_MISMATCH",
                    semantic_run=semantic_run,
                )

        if semantic_run.get("status") == STATUS_OWNER_QUESTIONS:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                semantic_run=semantic_run,
                owner_questions=list(semantic_run.get("owner_questions") or []),
            )
        if semantic_run.get("status") == STATUS_OWNER_FOLLOWUP:
            return _packet(
                status=STATUS_NEEDS_OWNER,
                semantic_run=semantic_run,
                owner_questions=list(semantic_run.get("owner_questions") or []),
                owner_followup=list(semantic_run.get("owner_followup") or []),
            )

    if semantic_run.get("status") != STATUS_CONFIRMED_BINDINGS:
        return _packet(
            status=STATUS_BLOCKED,
            blocked_reason=semantic_run.get("blocked_reason") or "SEMANTIC_BINDINGS_NOT_CONFIRMED",
            semantic_run=semantic_run,
            workbook_logical_model=workbook_logical_model,
        )

    if workbook_logical_model is not None:
        semantic_run = dict(semantic_run)
        semantic_run["workbook_logical_model_evidence"] = dict(
            workbook_logical_model.get("p7_p8_evidence_projection") or {}
        )

    evidence = ingestion_output if isinstance(ingestion_output, dict) else {}
    normalized_tables = evidence.get("normalized_tables")
    column_refs = evidence.get("column_refs")
    has_complete_row_evidence = (
        isinstance(normalized_tables, list)
        and bool(normalized_tables)
        and isinstance(column_refs, list)
        and bool(column_refs)
    )
    derived_evidence = None

    if requested_capability is not None:
        capability_definition = get_capability_definition_v1(requested_capability)
        if capability_definition is not None and capability_definition.kind == "COMPOSITE":
            bridge = semantic_run.get("bridge_packet") if isinstance(semantic_run, dict) else None
            case_id = str((bridge or {}).get("case_id") or "").strip()
            try:
                governed_input = build_service_1_composite_governed_computation_input_v1(
                    case_id=case_id,
                    capability_ref=requested_capability,
                )
            except ValueError as exc:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=str(exc) or "P8_COMPOSITE_INPUT_BLOCKED",
                    semantic_run=semantic_run,
                )
            computability_decision = None
        else:
            try:
                computability_decision = build_computability_decision_from_confirmed_bindings_v1(
                    confirmed_bindings=semantic_run,
                    requested_capability=requested_capability,
                )
            except ValueError as exc:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=str(exc) or "P8_COMPUTABILITY_BLOCKED",
                    semantic_run=semantic_run,
                )
            if (
                computability_decision.status != P8_STATUS_COMPUTABLE
                or computability_decision.governed_computation_input is None
            ) and has_complete_row_evidence:
                derived_evidence = build_service_1_derived_evidence_v1(
                    ingestion_output=evidence,
                    semantic_run=semantic_run,
                    requested_capability=requested_capability,
                    owner_unit_confirmation_events=owner_unit_confirmation_events,
                )
                derived_owner_questions = [
                    dict(item)
                    for item in (derived_evidence.get("owner_questions") or [])
                    if isinstance(item, Mapping)
                ]
                if (
                    derived_evidence.get("status") == DERIVED_EVIDENCE_NEEDS
                    and derived_owner_questions
                ):
                    return _packet(
                        status=STATUS_NEEDS_OWNER,
                        blocked_reason=(derived_evidence.get("evidence_requirements") or [None])[0],
                        semantic_run=semantic_run,
                        computability_decision=computability_decision.to_dict(),
                        derived_evidence=derived_evidence,
                        owner_questions=derived_owner_questions,
                        semantic_assistance_state=assisted_state,
                        owner_unit_confirmation_events=owner_unit_confirmation_events,
                    )
                should_retry_with_derived = (
                    derived_evidence.get("status") != DERIVED_EVIDENCE_BLOCKED
                    and (
                        int(derived_evidence.get("derived_variable_count") or 0) > 0
                        or derived_evidence.get("status") == DERIVED_EVIDENCE_NEEDS
                    )
                )
                if should_retry_with_derived:
                    try:
                        computability_decision = build_computability_decision_from_confirmed_bindings_v1(
                            confirmed_bindings=semantic_run,
                            requested_capability=requested_capability,
                            derived_evidence_packet=derived_evidence,
                        )
                    except ValueError as exc:
                        return _packet(
                            status=STATUS_BLOCKED,
                            blocked_reason=str(exc) or "P8_DERIVED_COMPUTABILITY_BLOCKED",
                            semantic_run=semantic_run,
                            derived_evidence=derived_evidence,
                        )
            if computability_decision.status != P8_STATUS_COMPUTABLE or computability_decision.governed_computation_input is None:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=(
                        derived_evidence.get("evidence_requirements", [None])[0]
                        if isinstance(derived_evidence, dict)
                        and derived_evidence.get("status") == DERIVED_EVIDENCE_NEEDS
                        and derived_evidence.get("evidence_requirements")
                        else computability_decision.reason or computability_decision.status
                    ),
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict(),
                    derived_evidence=derived_evidence,
                    owner_unit_confirmation_events=owner_unit_confirmation_events,
                )
            governed_input = computability_decision.governed_computation_input

        governed_payload = governed_input.to_dict()
        computation_result = None
        bounded_outcome = None
        delivery_result = None

        if requested_capability == LIQ_001_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = evaluate_liq_001_from_normalized_tables_v1(
                computation_plan=governed_payload,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
            )
            if computation_result.get("status") != LIQ_001_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "LIQ_001_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                )
            bounded_outcome = build_liq_001_outcome_v1(computation_result=computation_result)
            if bounded_outcome.get("status") != LIQ_001_OUTCOME_READY:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "LIQ_001_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                delivery_result = deliver_liq_001_outcome_xlsx_v1(
                    outcome=bounded_outcome,
                    output_dir=output_dir,
                )
                if delivery_result.get("status") != "DELIVERED":
                    return _packet(
                        status=STATUS_BLOCKED,
                        blocked_reason=delivery_result.get("blocked_reason") or "LIQ_001_DELIVERY_BLOCKED",
                        semantic_run=semantic_run,
                        computability_decision=computability_decision.to_dict() if computability_decision else None,
                        governed_computation_input=governed_payload,
                        computation_result=computation_result,
                        bounded_outcome=bounded_outcome,
                        delivery_result=delivery_result,
                    )

        elif requested_capability == REN_001_CAPABILITY_REF and has_complete_row_evidence:
            computation_result = evaluate_ren_001_from_normalized_tables_v1(
                computation_plan=governed_payload,
                normalized_tables=normalized_tables,
                column_refs=column_refs,
                derived_evidence_packet=derived_evidence,
            )
            if computation_result.get("status") != REN_001_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "REN_001_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    derived_evidence=derived_evidence,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                )
            bounded_outcome = build_ren_001_outcome_v1(computation_result=computation_result)
            if bounded_outcome.get("status") != REN_001_OUTCOME_READY:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "REN_001_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                delivery_result = deliver_ren_001_outcome_xlsx_v1(
                    outcome=bounded_outcome,
                    output_dir=output_dir,
                )
                if delivery_result.get("status") != "DELIVERED":
                    return _packet(
                        status=STATUS_BLOCKED,
                        blocked_reason=delivery_result.get("blocked_reason") or "REN_001_DELIVERY_BLOCKED",
                        semantic_run=semantic_run,
                        computability_decision=computability_decision.to_dict() if computability_decision else None,
                        governed_computation_input=governed_payload,
                        computation_result=computation_result,
                        bounded_outcome=bounded_outcome,
                        delivery_result=delivery_result,
                    )

        elif capability_definition is not None:
            generic_normalized_tables = None if capability_definition.kind == "COMPOSITE" else normalized_tables
            generic_column_refs = None if capability_definition.kind == "COMPOSITE" else column_refs
            if capability_definition.kind == "ATOMIC" and not has_complete_row_evidence:
                return _packet(
                    status=STATUS_COMPUTATION_PLAN_READY,
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                )
            computation_result = execute_generic_capability_v1(
                capability_ref=requested_capability,
                governed_computation_input=governed_payload,
                normalized_tables=generic_normalized_tables,
                column_refs=generic_column_refs,
                governed_results=governed_results,
            )
            if computation_result.get("status") != GENERIC_STATUS_EVALUATED:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=computation_result.get("status") or "GENERIC_COMPUTATION_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                )
            bounded_outcome = computation_result["outcome"]
            if bounded_outcome.get("status") != "OUTCOME_READY":
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=bounded_outcome.get("blocked_reason") or "GENERIC_OUTCOME_BLOCKED",
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )
            if deliver_result:
                return _packet(
                    status=STATUS_BLOCKED,
                    blocked_reason=_delivery_block_reason(capability_definition),
                    semantic_run=semantic_run,
                    computability_decision=computability_decision.to_dict() if computability_decision else None,
                    governed_computation_input=governed_payload,
                    computation_result=computation_result,
                    bounded_outcome=bounded_outcome,
                )

        return _packet(
            status=STATUS_COMPUTATION_PLAN_READY,
            semantic_run=semantic_run,
            computability_decision=computability_decision.to_dict() if computability_decision else None,
            derived_evidence=derived_evidence,
            governed_computation_input=governed_payload,
            computation_result=computation_result,
            bounded_outcome=bounded_outcome,
            delivery_result=delivery_result,
            owner_unit_confirmation_events=owner_unit_confirmation_events,
        )

    if deliver_result:
        return _packet(
            status=STATUS_BLOCKED,
            blocked_reason="DELIVERY_REQUIRES_REQUESTED_CAPABILITY",
            semantic_run=semantic_run,
        )

    physical_run = run_service_1_pipeline_v1(tool_requests=tool_requests, output_dir=output_dir)
    return _packet(status=STATUS_READY, semantic_run=semantic_run, physical_run=physical_run)


def _delivery_block_reason(capability_definition: Any) -> str:
    code = str(capability_definition.pathology_code or "").strip()
    if "_PREREQUISITE_" in code:
        code = str(capability_definition.capability_ref or "").strip().upper()
    return f"{code}_DELIVERY_NOT_AUTHORIZED"


def _packet(
    *,
    status: str,
    blocked_reason: str | None = None,
    semantic_run: Any = None,
    physical_run: Any = None,
    computability_decision: Any = None,
    derived_evidence: Any = None,
    governed_computation_input: Any = None,
    computation_result: Any = None,
    bounded_outcome: Any = None,
    delivery_result: Any = None,
    reconciliation_run: Any = None,
    collection_aging_run: Any = None,
    expense_variance_run: Any = None,
    owner_questions: list[dict[str, Any]] | None = None,
    owner_followup: list[dict[str, Any]] | None = None,
    semantic_assistance_state: Any = None,
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] | None = None,
    workbook_logical_model: Any = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "status": status,
        "blocked_reason": blocked_reason,
        "semantic_run": _public_semantic_run(semantic_run),
        "physical_run": physical_run,
        "computability_decision": computability_decision,
        "derived_evidence": derived_evidence,
        "governed_computation_input": governed_computation_input,
        "computation_result": computation_result,
        "bounded_outcome": bounded_outcome,
        "delivery_result": delivery_result,
        "reconciliation_run": reconciliation_run,
        "collection_aging_run": collection_aging_run,
        "expense_variance_run": expense_variance_run,
        "owner_questions": list(owner_questions or []),
        "owner_followup": [dict(item) for item in (owner_followup or [])],
        "semantic_assistance_state": semantic_assistance_state,
        "owner_unit_confirmation_events": [
            dict(item)
            for item in (owner_unit_confirmation_events or [])
            if isinstance(item, Mapping)
        ],
        "workbook_logical_model": workbook_logical_model,
        "semantic_bindings_confirmed": bool(
            isinstance(semantic_run, dict) and semantic_run.get("status") == STATUS_CONFIRMED_BINDINGS
        ),
        "tools_executed": bool(isinstance(physical_run, dict)),
        "computation_executed": bool(
            isinstance(computation_result, dict)
            and computation_result.get("status")
            in {
                LIQ_001_STATUS_EVALUATED,
                REN_001_STATUS_EVALUATED,
                GENERIC_STATUS_EVALUATED,
            }
        ),
        "bounded_finding_generated": bool(
            isinstance(bounded_outcome, dict)
            and bounded_outcome.get("bounded_finding_generated") is True
        ),
        "delivery_generated": bool(
            isinstance(delivery_result, dict) and delivery_result.get("status") == "DELIVERED"
        ),
        "reconciliation_review_prepared": bool(
            isinstance(reconciliation_run, dict)
            and reconciliation_run.get("status")
            == RECONCILIATION_STATUS_REVIEW_READY
        ),
        "requires_human_review": bool(
            isinstance(reconciliation_run, dict)
            and reconciliation_run.get("requires_human_review") is True
        ),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _public_semantic_run(semantic_run: Any) -> dict[str, Any] | None:
    if not isinstance(semantic_run, dict):
        return None
    payload = {
        "schema_version": semantic_run.get("schema_version"),
        "service_name": semantic_run.get("service_name"),
        "status": semantic_run.get("status"),
        "blocked_reason": semantic_run.get("blocked_reason"),
        "owner_questions": list(semantic_run.get("owner_questions") or []),
        "owner_followup": [dict(item) for item in (semantic_run.get("owner_followup") or [])],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    logical_model_evidence = semantic_run.get("workbook_logical_model_evidence")
    if isinstance(logical_model_evidence, Mapping):
        payload["workbook_logical_model_evidence"] = dict(logical_model_evidence)
    owner_loop = semantic_run.get("owner_loop_packet")
    if isinstance(owner_loop, dict):
        events = owner_loop.get("owner_confirmation_events")
        if isinstance(events, list) and events:
            payload["owner_confirmation_events"] = [
                dict(item) for item in events if isinstance(item, dict)
            ]
        relationship_events = owner_loop.get("owner_relationship_confirmation_events")
        if isinstance(relationship_events, list) and relationship_events:
            payload["owner_relationship_confirmation_events"] = [
                dict(item) for item in relationship_events if isinstance(item, dict)
            ]
    return payload


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_COMPUTATION_PLAN_READY",
    "STATUS_NEEDS_OWNER",
    "STATUS_BLOCKED",
    "STATUS_RECONCILIATION_REVIEW_READY",
    "STATUS_RECONCILIATION_NEEDS_OWNER",
    "STATUS_RECONCILIATION_NEEDS_EVIDENCE",
    "run_service_1_governed_analysis_v1",
    "run_service_1_product_pipeline_v1",
]
