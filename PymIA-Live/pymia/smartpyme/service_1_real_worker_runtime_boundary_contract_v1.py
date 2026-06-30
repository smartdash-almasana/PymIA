from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_REAL_WORKER_RUNTIME_BOUNDARY_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
BOUNDARY_KIND: Final[str] = "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE"
TENANT_ISOLATION_GUARD_KIND: Final[str] = "TENANT_ISOLATION_GUARD_CANDIDATE"
COST_AND_RATE_LIMIT_GUARD_KIND: Final[str] = "COST_AND_RATE_LIMIT_GUARD_CANDIDATE"
FAILURE_RECOVERY_RETRY_KIND: Final[str] = "FAILURE_RECOVERY_RETRY_CANDIDATE"
FAILURE_RECOVERY_FALLBACK_KIND: Final[str] = "FAILURE_RECOVERY_FALLBACK_CANDIDATE"

INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE: Final[str] = "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE"
AUTONOMOUS_RERUN_PROCESSING_CANDIDATE: Final[str] = "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE"
OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE: Final[str] = "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE"
REQUEST_RUNTIME_EXECUTION: Final[str] = "REQUEST_RUNTIME_EXECUTION"

ALLOWED_OPERATION_KINDS: Final[tuple[str, ...]] = (
    INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
    AUTONOMOUS_RERUN_PROCESSING_CANDIDATE,
    OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE,
    REQUEST_RUNTIME_EXECUTION,
)

TENANT_GUARD_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "correction_applied": "tenant_isolation_correction_applied_must_be_false",
    "auth_authorized": "tenant_isolation_auth_authorized_must_be_false",
    "storage_write_authorized": "tenant_isolation_storage_write_authorized_must_be_false",
    "db_authorized": "tenant_isolation_db_authorized_must_be_false",
    "worker_authorized": "tenant_isolation_worker_authorized_must_be_false",
    "pipeline_authorized": "tenant_isolation_pipeline_authorized_must_be_false",
    "runner_authorized": "tenant_isolation_runner_authorized_must_be_false",
    "llm_authorized": "tenant_isolation_llm_authorized_must_be_false",
    "pydantic_ai_authorized": "tenant_isolation_pydantic_ai_authorized_must_be_false",
    "runtime_authorized": "tenant_isolation_runtime_authorized_must_be_false",
    "api_exposed": "tenant_isolation_api_exposed_must_be_false",
}

COST_GUARD_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "cost_charge_authorized": "cost_guard_cost_charge_authorized_must_be_false",
    "rate_limit_mutation_authorized": "cost_guard_rate_limit_mutation_authorized_must_be_false",
    "billing_authorized": "cost_guard_billing_authorized_must_be_false",
    "storage_write_authorized": "cost_guard_storage_write_authorized_must_be_false",
    "db_authorized": "cost_guard_db_authorized_must_be_false",
    "worker_authorized": "cost_guard_worker_authorized_must_be_false",
    "queue_authorized": "cost_guard_queue_authorized_must_be_false",
    "scheduler_authorized": "cost_guard_scheduler_authorized_must_be_false",
    "pipeline_authorized": "cost_guard_pipeline_authorized_must_be_false",
    "runner_authorized": "cost_guard_runner_authorized_must_be_false",
    "llm_authorized": "cost_guard_llm_authorized_must_be_false",
    "pydantic_ai_authorized": "cost_guard_pydantic_ai_authorized_must_be_false",
    "mutation_authorized": "cost_guard_mutation_authorized_must_be_false",
    "runtime_authorized": "cost_guard_runtime_authorized_must_be_false",
    "api_exposed": "cost_guard_api_exposed_must_be_false",
}

FAILURE_RECOVERY_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "recovery_execution_authorized": "failure_recovery_execution_authorized_must_be_false",
    "scheduled_retry_authorized": "failure_scheduled_retry_authorized_must_be_false",
    "worker_authorized": "failure_worker_authorized_must_be_false",
    "queue_authorized": "failure_queue_authorized_must_be_false",
    "db_authorized": "failure_db_authorized_must_be_false",
    "storage_write_authorized": "failure_storage_write_authorized_must_be_false",
    "pipeline_authorized": "failure_pipeline_authorized_must_be_false",
    "runner_authorized": "failure_runner_authorized_must_be_false",
    "llm_authorized": "failure_llm_authorized_must_be_false",
    "pydantic_ai_authorized": "failure_pydantic_ai_authorized_must_be_false",
    "mutation_authorized": "failure_mutation_authorized_must_be_false",
    "runtime_authorized": "failure_runtime_authorized_must_be_false",
    "api_exposed": "failure_api_exposed_must_be_false",
}

WorkerRuntimeBoundaryStatusV1 = Literal[
    "WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_JOB",
    "BLOCKED_TENANT_ISOLATION",
    "BLOCKED_COST_OR_RATE_LIMIT",
    "BLOCKED_RUNTIME_NOT_AUTHORIZED",
    "BLOCKED_PIPELINE_NOT_AUTHORIZED",
    "BLOCKED_FAILURE_RECOVERY_REQUIRED",
    "NEEDS_OWNER_INPUT",
    "NEEDS_EVIDENCE",
    "UNKNOWN",
]


class Service1WorkerRuntimeRetryContextV1(TypedDict):
    retry_requested: bool
    owner_confirmation_required: bool
    retry_reason: str


class Service1WorkerRuntimeBoundaryInputV1(TypedDict):
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    job_candidate_ref: str
    operation_kind: str
    pipeline_request_candidate_ref: str | None
    file_intake_candidate_ref: str | None
    cost_estimate_units: int | None
    rate_limit_context_ref: str | None
    retry_context: dict[str, object] | None
    tenant_isolation_candidate: dict[str, object] | None
    cost_rate_limit_candidate: dict[str, object] | None
    failure_recovery_candidate: dict[str, object] | None
    notes: list[str]


class Service1WorkerRuntimeJobExecutionCandidateV1(TypedDict):
    candidate_kind: Literal["JOB_EXECUTION_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    job_candidate_ref: str
    operation_kind: str
    pipeline_request_candidate_ref: str | None
    file_intake_candidate_ref: str | None
    cost_estimate_units: int
    rate_limit_context_ref: str
    execution_granted: Literal[False]


class Service1WorkerRuntimeAuthorizationCandidateV1(TypedDict):
    candidate_kind: Literal["RUNTIME_AUTHORIZATION_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    operation_kind: str
    runtime_execution_authorized: Literal[False]
    pipeline_execution_authorized: Literal[False]
    retry_authorized: Literal[False]


class Service1WorkerRuntimeAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE"]
    source_slice_ref: str
    audit_log_ref_candidate: str
    audit_event_ref_candidate: str
    append_operation: Literal["APPEND_EVENT"]
    event_summary: str
    source_context_refs: dict[str, str]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1WorkerRuntimeBoundaryCandidateV1(TypedDict):
    boundary_kind: Literal["REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    service_name: Literal["SERVICE_1"]
    job_candidate_ref: str
    operation_kind: str
    pipeline_request_candidate_ref: str | None
    file_intake_candidate_ref: str | None
    next_required_action: str
    job_execution_candidate: Service1WorkerRuntimeJobExecutionCandidateV1
    runtime_authorization_candidate: Service1WorkerRuntimeAuthorizationCandidateV1
    failure_recovery_candidate: dict[str, object] | None
    audit_event_candidate: Service1WorkerRuntimeAuditEventCandidateV1
    warnings: list[str]
    errors: list[str]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    scheduler_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    retry_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    mutation_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1WorkerRuntimeBoundaryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: WorkerRuntimeBoundaryStatusV1
    worker_runtime_boundary_candidate: Service1WorkerRuntimeBoundaryCandidateV1 | None
    blocked_reason: str | None
    next_required_action: str | None
    audit_event_candidate: Service1WorkerRuntimeAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    scheduler_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    retry_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    mutation_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_real_worker_runtime_boundary_contract_v1(
    boundary_input: Service1WorkerRuntimeBoundaryInputV1,
) -> Service1WorkerRuntimeBoundaryResultV1:
    """Classify a future worker/runtime path without authorizing real execution."""
    tenant_ref = _clean_required_ref(boundary_input.get("tenant_ref"))
    if tenant_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="tenant_ref_required",
            errors=["tenant_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires tenant_ref."),
        )

    owner_ref = _clean_required_ref(boundary_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="owner_ref_required",
            errors=["owner_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires owner_ref."),
        )

    case_ref = _clean_required_ref(boundary_input.get("case_ref"))
    if case_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="case_ref_required",
            errors=["case_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires case_ref."),
        )

    session_ref = _clean_required_ref(boundary_input.get("session_ref"))
    if session_ref is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="session_ref_required",
            errors=["session_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires session_ref."),
        )

    job_candidate_ref = _clean_required_ref(boundary_input.get("job_candidate_ref"))
    if job_candidate_ref is None:
        return _result(
            status="BLOCKED_INVALID_JOB",
            blocked_reason="job_candidate_ref_required",
            errors=["job_candidate_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires job_candidate_ref."),
        )

    operation_kind = _clean_required_ref(boundary_input.get("operation_kind"))
    if operation_kind is None:
        return _result(
            status="BLOCKED_INVALID_JOB",
            blocked_reason="operation_kind_required",
            errors=["operation_kind_required"],
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires operation_kind."),
        )
    if operation_kind not in ALLOWED_OPERATION_KINDS:
        return _result(
            status="BLOCKED_INVALID_JOB",
            blocked_reason="operation_kind_not_supported",
            errors=["operation_kind_not_supported"],
            notes=_notes(boundary_input.get("notes"), "operation_kind is not supported by this boundary."),
        )
    if operation_kind == REQUEST_RUNTIME_EXECUTION:
        return _result(
            status="BLOCKED_RUNTIME_NOT_AUTHORIZED",
            blocked_reason="runtime_execution_not_authorized_by_worker_boundary",
            errors=["runtime_execution_not_authorized_by_worker_boundary"],
            next_required_action="KEEP_RUNTIME_GOVERNED",
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary cannot authorize direct runtime execution."),
        )

    cost_estimate_units = boundary_input.get("cost_estimate_units")
    if not isinstance(cost_estimate_units, int) or cost_estimate_units < 0:
        return _result(
            status="NEEDS_EVIDENCE",
            blocked_reason="cost_estimate_units_required",
            errors=["cost_estimate_units_required"],
            next_required_action="PROVIDE_COST_ESTIMATE_UNITS",
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires governed cost estimate evidence."),
        )

    rate_limit_context_ref = _clean_required_ref(boundary_input.get("rate_limit_context_ref"))
    if rate_limit_context_ref is None:
        return _result(
            status="NEEDS_EVIDENCE",
            blocked_reason="rate_limit_context_ref_required",
            errors=["rate_limit_context_ref_required"],
            next_required_action="PROVIDE_RATE_LIMIT_CONTEXT_REF",
            notes=_notes(boundary_input.get("notes"), "Worker runtime boundary requires governed rate-limit context evidence."),
        )

    pipeline_request_candidate_ref = _clean_optional_ref(boundary_input.get("pipeline_request_candidate_ref"))
    file_intake_candidate_ref = _clean_optional_ref(boundary_input.get("file_intake_candidate_ref"))

    if operation_kind == INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE and file_intake_candidate_ref is None:
        return _result(
            status="NEEDS_EVIDENCE",
            blocked_reason="file_intake_candidate_ref_required_for_initial_file_intake",
            errors=["file_intake_candidate_ref_required_for_initial_file_intake"],
            next_required_action="PROVIDE_FILE_INTAKE_CANDIDATE_REF",
            notes=_notes(boundary_input.get("notes"), "Initial file intake processing requires file_intake_candidate_ref."),
        )

    if operation_kind in (
        AUTONOMOUS_RERUN_PROCESSING_CANDIDATE,
        OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE,
    ) and pipeline_request_candidate_ref is None:
        return _result(
            status="BLOCKED_PIPELINE_NOT_AUTHORIZED",
            blocked_reason="pipeline_request_candidate_ref_required_for_operation",
            errors=["pipeline_request_candidate_ref_required_for_operation"],
            next_required_action="KEEP_PIPELINE_GOVERNED",
            notes=_notes(boundary_input.get("notes"), "Pipeline-linked worker runtime candidates require pipeline_request_candidate_ref."),
        )

    tenant_validation_reason = _validate_tenant_isolation_candidate(
        tenant_isolation_candidate=boundary_input.get("tenant_isolation_candidate"),
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
    )
    if tenant_validation_reason is not None:
        return _result(
            status="BLOCKED_TENANT_ISOLATION",
            blocked_reason=tenant_validation_reason,
            errors=[tenant_validation_reason],
            next_required_action="REVIEW_TENANT_ISOLATION",
            notes=_notes(boundary_input.get("notes"), "Tenant isolation candidate did not clear this worker runtime boundary."),
        )

    cost_validation_reason = _validate_cost_rate_limit_candidate(
        cost_rate_limit_candidate=boundary_input.get("cost_rate_limit_candidate"),
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
        operation_kind=operation_kind,
    )
    if cost_validation_reason is not None:
        return _result(
            status="BLOCKED_COST_OR_RATE_LIMIT",
            blocked_reason=cost_validation_reason,
            errors=[cost_validation_reason],
            next_required_action="REVIEW_COST_AND_RATE_LIMITS",
            notes=_notes(boundary_input.get("notes"), "Cost/rate candidate did not clear this worker runtime boundary."),
        )

    retry_context = _normalize_retry_context(boundary_input.get("retry_context"))
    if retry_context.get("owner_confirmation_required"):
        return _result(
            status="NEEDS_OWNER_INPUT",
            blocked_reason="owner_confirmation_required_before_worker_runtime",
            errors=["owner_confirmation_required_before_worker_runtime"],
            next_required_action="REQUEST_OWNER_CONFIRMATION",
            notes=_notes(boundary_input.get("notes"), "Owner confirmation is required before the worker runtime boundary can proceed."),
        )

    failure_recovery_candidate = boundary_input.get("failure_recovery_candidate")
    failure_recovery_validation_reason = _validate_failure_recovery_candidate(
        failure_recovery_candidate=failure_recovery_candidate,
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
        retry_requested=retry_context.get("retry_requested", False),
    )
    if failure_recovery_validation_reason is not None:
        return _result(
            status="BLOCKED_FAILURE_RECOVERY_REQUIRED",
            blocked_reason=failure_recovery_validation_reason,
            errors=[failure_recovery_validation_reason],
            next_required_action="REVIEW_FAILURE_RECOVERY",
            notes=_notes(boundary_input.get("notes"), "Failure recovery classification is required before any retry-like worker runtime path."),
        )

    job_execution_candidate: Service1WorkerRuntimeJobExecutionCandidateV1 = {
        "candidate_kind": "JOB_EXECUTION_CANDIDATE",
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "session_ref": session_ref,
        "job_candidate_ref": job_candidate_ref,
        "operation_kind": operation_kind,
        "pipeline_request_candidate_ref": pipeline_request_candidate_ref,
        "file_intake_candidate_ref": file_intake_candidate_ref,
        "cost_estimate_units": cost_estimate_units,
        "rate_limit_context_ref": rate_limit_context_ref,
        "execution_granted": False,
    }
    runtime_authorization_candidate: Service1WorkerRuntimeAuthorizationCandidateV1 = {
        "candidate_kind": "RUNTIME_AUTHORIZATION_CANDIDATE",
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "session_ref": session_ref,
        "operation_kind": operation_kind,
        "runtime_execution_authorized": False,
        "pipeline_execution_authorized": False,
        "retry_authorized": False,
    }
    audit_event_candidate = _audit_event_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
        job_candidate_ref=job_candidate_ref,
        operation_kind=operation_kind,
        tenant_ref=tenant_ref,
    )
    candidate: Service1WorkerRuntimeBoundaryCandidateV1 = {
        "boundary_kind": BOUNDARY_KIND,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "session_ref": session_ref,
        "service_name": SERVICE_NAME,
        "job_candidate_ref": job_candidate_ref,
        "operation_kind": operation_kind,
        "pipeline_request_candidate_ref": pipeline_request_candidate_ref,
        "file_intake_candidate_ref": file_intake_candidate_ref,
        "next_required_action": "KEEP_WORKER_RUNTIME_GOVERNED",
        "job_execution_candidate": job_execution_candidate,
        "runtime_authorization_candidate": runtime_authorization_candidate,
        "failure_recovery_candidate": _normalized_failure_recovery_candidate(failure_recovery_candidate),
        "audit_event_candidate": audit_event_candidate,
        "warnings": [],
        "errors": [],
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "retry_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "mutation_authorized": False,
        "api_exposed": False,
    }
    return _result(
        status="WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY",
        worker_runtime_boundary_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        next_required_action="KEEP_WORKER_RUNTIME_GOVERNED",
        notes=_notes(
            boundary_input.get("notes"),
            "Worker runtime candidate prepared as pure governed data only; it does not authorize workers, queues, pipeline execution, retries, or runtime.",
        ),
    )


def _validate_tenant_isolation_candidate(
    *,
    tenant_isolation_candidate: object,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
) -> str | None:
    if not isinstance(tenant_isolation_candidate, dict) or not tenant_isolation_candidate:
        return "tenant_isolation_candidate_required"
    if tenant_isolation_candidate.get("guard_kind") != TENANT_ISOLATION_GUARD_KIND:
        return "tenant_isolation_guard_kind_must_match"
    if tenant_isolation_candidate.get("service_name") != SERVICE_NAME:
        return "tenant_isolation_service_name_must_be_service_1"
    if tenant_isolation_candidate.get("tenant_isolation_passed") is not True:
        return "tenant_isolation_pass_must_be_true"
    if tenant_isolation_candidate.get("cross_tenant_access_detected") is not False:
        return "tenant_isolation_cross_tenant_detected"
    if tenant_isolation_candidate.get("cross_case_access_detected") is not False:
        return "tenant_isolation_cross_case_detected"
    if tenant_isolation_candidate.get("cross_session_access_detected") is not False:
        return "tenant_isolation_cross_session_detected"
    if _clean_required_ref(tenant_isolation_candidate.get("owner_ref")) != owner_ref:
        return "tenant_isolation_owner_ref_must_match_input"
    if _clean_required_ref(tenant_isolation_candidate.get("case_ref")) != case_ref:
        return "tenant_isolation_case_ref_must_match_input"
    if _clean_required_ref(tenant_isolation_candidate.get("source_session_ref")) != session_ref:
        return "tenant_isolation_source_session_ref_must_match_input"
    checked_source_refs = tenant_isolation_candidate.get("checked_source_refs")
    if checked_source_refs is not None:
        if not isinstance(checked_source_refs, dict):
            return "tenant_isolation_checked_source_refs_invalid"
        for key, value in checked_source_refs.items():
            if "tenant" in str(key).lower() and _clean_required_ref(value) != tenant_ref:
                return "tenant_ref_must_match_tenant_isolation_refs"
            if "session" in str(key).lower() and _clean_required_ref(value) != session_ref:
                return "session_ref_must_match_tenant_isolation_refs"
    for flag_name, reason in TENANT_GUARD_FLAG_REASON_BY_NAME.items():
        if tenant_isolation_candidate.get(flag_name) is not False:
            return reason
    return None


def _validate_cost_rate_limit_candidate(
    *,
    cost_rate_limit_candidate: object,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
    operation_kind: str,
) -> str | None:
    if not isinstance(cost_rate_limit_candidate, dict) or not cost_rate_limit_candidate:
        return "cost_rate_limit_candidate_required"
    if cost_rate_limit_candidate.get("guard_kind") != COST_AND_RATE_LIMIT_GUARD_KIND:
        return "cost_rate_limit_guard_kind_must_match"
    if cost_rate_limit_candidate.get("service_name") != SERVICE_NAME:
        return "cost_rate_limit_service_name_must_be_service_1"
    if _clean_required_ref(cost_rate_limit_candidate.get("tenant_ref")) != tenant_ref:
        return "tenant_ref_must_match_cost_rate_limit_candidate"
    if _clean_required_ref(cost_rate_limit_candidate.get("owner_ref")) != owner_ref:
        return "owner_ref_must_match_cost_rate_limit_candidate"
    if _clean_required_ref(cost_rate_limit_candidate.get("case_ref")) != case_ref:
        return "case_ref_must_match_cost_rate_limit_candidate"
    if _clean_required_ref(cost_rate_limit_candidate.get("source_session_ref")) != session_ref:
        return "session_ref_must_match_cost_rate_limit_candidate"
    if _clean_required_ref(cost_rate_limit_candidate.get("requested_operation_kind")) != operation_kind:
        return "operation_kind_must_match_cost_rate_limit_candidate"
    if cost_rate_limit_candidate.get("cost_limit_passed") is not True:
        return "cost_limit_must_be_passed"
    if cost_rate_limit_candidate.get("rate_limit_passed") is not True:
        return "rate_limit_must_be_passed"
    if cost_rate_limit_candidate.get("budget_limit_passed") is not True:
        return "budget_limit_must_be_passed"
    for flag_name, reason in COST_GUARD_FLAG_REASON_BY_NAME.items():
        if cost_rate_limit_candidate.get(flag_name) is not False:
            return reason
    return None


def _validate_failure_recovery_candidate(
    *,
    failure_recovery_candidate: object,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
    retry_requested: bool,
) -> str | None:
    if not retry_requested:
        if failure_recovery_candidate is None:
            return None
        if not isinstance(failure_recovery_candidate, dict) or not failure_recovery_candidate:
            return "failure_recovery_candidate_invalid"
    elif not isinstance(failure_recovery_candidate, dict) or not failure_recovery_candidate:
        return "failure_recovery_candidate_required_for_retry"

    if not isinstance(failure_recovery_candidate, dict) or not failure_recovery_candidate:
        return None

    recovery_kind = _clean_required_ref(failure_recovery_candidate.get("recovery_kind"))
    if recovery_kind is None:
        return "failure_recovery_kind_required"
    if recovery_kind not in (FAILURE_RECOVERY_RETRY_KIND, FAILURE_RECOVERY_FALLBACK_KIND):
        return "failure_recovery_kind_not_supported"
    if retry_requested and recovery_kind != FAILURE_RECOVERY_RETRY_KIND:
        return "retry_recovery_candidate_required"
    if recovery_kind == FAILURE_RECOVERY_FALLBACK_KIND:
        return "fallback_recovery_candidate_cannot_authorize_worker_runtime"
    if failure_recovery_candidate.get("service_name") != SERVICE_NAME:
        return "failure_recovery_service_name_must_be_service_1"
    if _clean_required_ref(failure_recovery_candidate.get("owner_ref")) != owner_ref:
        return "failure_recovery_owner_ref_must_match_input"
    if _clean_required_ref(failure_recovery_candidate.get("case_ref")) != case_ref:
        return "failure_recovery_case_ref_must_match_input"
    if _clean_required_ref(failure_recovery_candidate.get("source_session_ref")) != session_ref:
        return "failure_recovery_source_session_ref_must_match_input"

    recovery_attempt_count = failure_recovery_candidate.get("recovery_attempt_count")
    recovery_max_attempts = failure_recovery_candidate.get("recovery_max_attempts")
    if not isinstance(recovery_attempt_count, int) or recovery_attempt_count < 0:
        return "failure_recovery_attempt_count_invalid"
    if not isinstance(recovery_max_attempts, int) or recovery_max_attempts <= 0:
        return "failure_recovery_max_attempts_invalid"
    if recovery_attempt_count >= recovery_max_attempts:
        return "failure_recovery_attempt_limit_reached"

    for flag_name, reason in FAILURE_RECOVERY_FLAG_REASON_BY_NAME.items():
        if failure_recovery_candidate.get(flag_name) is not False:
            return reason
    return None


def _normalized_failure_recovery_candidate(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict) or not value:
        return None
    return dict(value)


def _normalize_retry_context(value: object) -> Service1WorkerRuntimeRetryContextV1:
    if not isinstance(value, dict):
        return {
            "retry_requested": False,
            "owner_confirmation_required": False,
            "retry_reason": "",
        }
    retry_requested = value.get("retry_requested") is True
    owner_confirmation_required = value.get("owner_confirmation_required") is True
    retry_reason_value = value.get("retry_reason")
    retry_reason = retry_reason_value.strip() if isinstance(retry_reason_value, str) else ""
    return {
        "retry_requested": retry_requested,
        "owner_confirmation_required": owner_confirmation_required,
        "retry_reason": retry_reason,
    }


def _audit_event_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
    job_candidate_ref: str,
    operation_kind: str,
    tenant_ref: str,
) -> Service1WorkerRuntimeAuditEventCandidateV1:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE_RECORDED",
        "event_status": "WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": session_ref,
        "source_slice_kind": BOUNDARY_KIND,
        "source_slice_ref": job_candidate_ref,
        "audit_log_ref_candidate": f"audit_log:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}",
        "audit_event_ref_candidate": f"audit_event:{_safe_ref(session_ref)}:{_safe_ref(job_candidate_ref)}",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Real worker runtime boundary candidate recorded.",
        "source_context_refs": {
            "tenant_ref": tenant_ref,
            "session_ref": session_ref,
            "job_candidate_ref": job_candidate_ref,
            "operation_kind": operation_kind,
        },
        "owner_visible": False,
        "mutation_requested": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_optional_ref(value: object) -> str | None:
    if value is None:
        return None
    return _clean_required_ref(value)


def _notes(notes: object, fallback_note: str) -> list[str]:
    if not isinstance(notes, list):
        return [fallback_note]
    cleaned_notes = [str(item) for item in notes]
    cleaned_notes.append(fallback_note)
    return cleaned_notes


def _result(
    *,
    status: WorkerRuntimeBoundaryStatusV1,
    worker_runtime_boundary_candidate: Service1WorkerRuntimeBoundaryCandidateV1 | None = None,
    blocked_reason: str | None = None,
    next_required_action: str | None = None,
    audit_event_candidate: Service1WorkerRuntimeAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1WorkerRuntimeBoundaryResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "worker_runtime_boundary_candidate": worker_runtime_boundary_candidate,
        "blocked_reason": blocked_reason,
        "next_required_action": next_required_action,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "retry_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "mutation_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BOUNDARY_KIND",
    "TENANT_ISOLATION_GUARD_KIND",
    "COST_AND_RATE_LIMIT_GUARD_KIND",
    "FAILURE_RECOVERY_RETRY_KIND",
    "FAILURE_RECOVERY_FALLBACK_KIND",
    "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
    "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE",
    "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE",
    "REQUEST_RUNTIME_EXECUTION",
    "ALLOWED_OPERATION_KINDS",
    "Service1WorkerRuntimeRetryContextV1",
    "Service1WorkerRuntimeBoundaryInputV1",
    "Service1WorkerRuntimeJobExecutionCandidateV1",
    "Service1WorkerRuntimeAuthorizationCandidateV1",
    "Service1WorkerRuntimeAuditEventCandidateV1",
    "Service1WorkerRuntimeBoundaryCandidateV1",
    "Service1WorkerRuntimeBoundaryResultV1",
    "build_service_1_real_worker_runtime_boundary_contract_v1",
]
