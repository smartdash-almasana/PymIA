from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_FAILURE_RECOVERY_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
RETRY_KIND: Final[str] = "FAILURE_RECOVERY_RETRY_CANDIDATE"
FALLBACK_KIND: Final[str] = "FAILURE_RECOVERY_FALLBACK_CANDIDATE"

SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
FILE_INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"
JOB_KIND: Final[str] = "SAAS_JOB_ORCHESTRATION_CANDIDATE"
AUDIT_KIND: Final[str] = "AUDIT_LOG_APPEND_CANDIDATE"
BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"
GUARDED_KIND: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE"
ROUTE_KIND: Final[str] = "OWNER_QUESTION_ROUTE_CANDIDATE"

SLICE_BLOCKED_TEMPORARY: Final[str] = "SLICE_BLOCKED_TEMPORARY"
SESSION_LIFECYCLE_BLOCKED: Final[str] = "SESSION_LIFECYCLE_BLOCKED"
FILE_INTAKE_BLOCKED_RETRYABLE: Final[str] = "FILE_INTAKE_BLOCKED_RETRYABLE"
JOB_ORCHESTRATION_BLOCKED_TEMPORARY: Final[str] = "JOB_ORCHESTRATION_BLOCKED_TEMPORARY"
AUDIT_APPEND_BLOCKED_RETRYABLE: Final[str] = "AUDIT_APPEND_BLOCKED_RETRYABLE"
CONVERSATIONAL_BRIDGE_BLOCKED_TEMPORARY: Final[str] = "CONVERSATIONAL_BRIDGE_BLOCKED_TEMPORARY"
GUARDED_RESPONSE_BLOCKED_TEMPORARY: Final[str] = "GUARDED_RESPONSE_BLOCKED_TEMPORARY"
OWNER_ROUTE_BLOCKED_TEMPORARY: Final[str] = "OWNER_ROUTE_BLOCKED_TEMPORARY"

SLICE_BLOCKED_PERMANENT: Final[str] = "SLICE_BLOCKED_PERMANENT"
SESSION_CROSS_TENANT_VIOLATION: Final[str] = "SESSION_CROSS_TENANT_VIOLATION"
FILE_INTAKE_KIND_UNSUPPORTED: Final[str] = "FILE_INTAKE_KIND_UNSUPPORTED"
JOB_ORCHESTRATION_KIND_UNSUPPORTED: Final[str] = "JOB_ORCHESTRATION_KIND_UNSUPPORTED"
SOURCE_CANDIDATE_MISSING_SESSION_LINEAGE: Final[str] = "SOURCE_CANDIDATE_MISSING_SESSION_LINEAGE"
UNSUPPORTED_FAILURE_KIND: Final[str] = "UNSUPPORTED_FAILURE_KIND"
FATAL_CONTRACT_VIOLATION: Final[str] = "FATAL_CONTRACT_VIOLATION"

RECOVERABLE_FAILURE_KINDS: Final[tuple[str, ...]] = (
    SLICE_BLOCKED_TEMPORARY,
    SESSION_LIFECYCLE_BLOCKED,
    FILE_INTAKE_BLOCKED_RETRYABLE,
    JOB_ORCHESTRATION_BLOCKED_TEMPORARY,
    AUDIT_APPEND_BLOCKED_RETRYABLE,
    CONVERSATIONAL_BRIDGE_BLOCKED_TEMPORARY,
    GUARDED_RESPONSE_BLOCKED_TEMPORARY,
    OWNER_ROUTE_BLOCKED_TEMPORARY,
)

NON_RECOVERABLE_FAILURE_KINDS: Final[tuple[str, ...]] = (
    SLICE_BLOCKED_PERMANENT,
    SESSION_CROSS_TENANT_VIOLATION,
    FILE_INTAKE_KIND_UNSUPPORTED,
    JOB_ORCHESTRATION_KIND_UNSUPPORTED,
    SOURCE_CANDIDATE_MISSING_SESSION_LINEAGE,
    UNSUPPORTED_FAILURE_KIND,
    FATAL_CONTRACT_VIOLATION,
)

ALLOWED_FAILURE_KINDS: Final[tuple[str, ...]] = (*RECOVERABLE_FAILURE_KINDS, *NON_RECOVERABLE_FAILURE_KINDS)

ALLOWED_SOURCE_SLICE_KINDS: Final[tuple[str, ...]] = (
    SESSION_KIND,
    FILE_INTAKE_KIND,
    JOB_KIND,
    AUDIT_KIND,
    BRIDGE_KIND,
    GUARDED_KIND,
    ROUTE_KIND,
)

KIND_FIELD_BY_SOURCE_KIND: Final[dict[str, str]] = {
    SESSION_KIND: "session_kind",
    FILE_INTAKE_KIND: "intake_kind",
    JOB_KIND: "job_kind",
    AUDIT_KIND: "audit_kind",
    BRIDGE_KIND: "bridge_kind",
    GUARDED_KIND: "gate_kind",
    ROUTE_KIND: "router_kind",
}

PAYLOAD_KEY_BY_SOURCE_KIND: Final[dict[str, str]] = {
    FILE_INTAKE_KIND: "saas_file_intake_candidate",
    JOB_KIND: "saas_job_orchestration_candidate",
    AUDIT_KIND: "audit_log_append_candidate",
    BRIDGE_KIND: "conversational_owner_bridge_candidate",
    GUARDED_KIND: "guarded_llm_response_candidate",
    ROUTE_KIND: "owner_question_route_candidate",
}

SESSION_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "runtime_authorized": "session_runtime_authorized_must_be_false",
    "job_authorized": "session_runtime_authorized_must_be_false",
    "file_upload_authorized": "session_runtime_authorized_must_be_false",
    "api_exposed": "session_api_exposed_must_be_false",
}

SOURCE_FLAG_REASON_BY_KIND: Final[dict[str, dict[str, str]]] = {
    SESSION_KIND: {
        "runtime_authorized": "runtime_authorized_must_be_false",
        "job_authorized": "source_candidate_flags_must_be_false",
        "file_upload_authorized": "source_candidate_flags_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    FILE_INTAKE_KIND: {
        "task_spec_candidate_allowed": "source_candidate_flags_must_be_false",
        "upload_authorized": "source_candidate_flags_must_be_false",
        "file_read_authorized": "source_candidate_flags_must_be_false",
        "parser_authorized": "source_candidate_flags_must_be_false",
        "job_authorized": "source_candidate_flags_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    JOB_KIND: {
        "worker_authorized": "worker_authorized_must_be_false",
        "queue_authorized": "source_candidate_flags_must_be_false",
        "async_execution_authorized": "source_candidate_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    AUDIT_KIND: {
        "storage_write_authorized": "storage_write_authorized_must_be_false",
        "db_authorized": "db_authorized_must_be_false",
        "worker_authorized": "worker_authorized_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    BRIDGE_KIND: {
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "prompt_runtime_authorized": "source_candidate_flags_must_be_false",
        "chatbot_authorized": "source_candidate_flags_must_be_false",
        "tool_authorized": "source_candidate_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "mutation_authorized_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    GUARDED_KIND: {
        "client_delivery_authorized": "source_candidate_flags_must_be_false",
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "prompt_runtime_authorized": "source_candidate_flags_must_be_false",
        "chatbot_authorized": "source_candidate_flags_must_be_false",
        "tool_authorized": "source_candidate_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "mutation_authorized_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    ROUTE_KIND: {
        "client_delivery_authorized": "source_candidate_flags_must_be_false",
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "prompt_runtime_authorized": "source_candidate_flags_must_be_false",
        "chatbot_authorized": "source_candidate_flags_must_be_false",
        "tool_authorized": "source_candidate_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "mutation_authorized_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
}

FAILURE_EVENT_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "owner_visible": "recovery_flags_must_be_false",
    "owner_notified": "owner_notified_must_be_false",
    "operator_escalation_authorized": "operator_escalation_authorized_must_be_false",
    "hide_failure": "hide_failure_must_be_false",
    "mutation_requested": "mutation_requested_must_be_false",
    "recovery_execution_authorized": "recovery_execution_authorized_must_be_false",
    "scheduled_retry_authorized": "scheduled_retry_authorized_must_be_false",
    "worker_authorized": "recovery_flags_must_be_false",
    "queue_authorized": "recovery_flags_must_be_false",
    "db_authorized": "recovery_flags_must_be_false",
    "storage_write_authorized": "recovery_flags_must_be_false",
    "pipeline_authorized": "pipeline_authorized_must_be_false",
    "runner_authorized": "runner_authorized_must_be_false",
    "llm_authorized": "llm_authorized_must_be_false",
    "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
    "mutation_authorized": "mutation_requested_must_be_false",
    "runtime_authorized": "runtime_authorized_must_be_false",
    "api_exposed": "api_exposed_must_be_false",
}

GENERIC_SOURCE_FORBIDDEN_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "correction_applied": "source_candidate_flags_must_be_false",
    "auth_authorized": "source_candidate_flags_must_be_false",
    "storage_write_authorized": "storage_write_authorized_must_be_false",
    "db_authorized": "db_authorized_must_be_false",
    "worker_authorized": "worker_authorized_must_be_false",
    "pipeline_authorized": "pipeline_authorized_must_be_false",
    "runner_authorized": "runner_authorized_must_be_false",
    "llm_authorized": "llm_authorized_must_be_false",
    "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
    "mutation_authorized": "mutation_authorized_must_be_false",
    "runtime_authorized": "runtime_authorized_must_be_false",
    "api_exposed": "api_exposed_must_be_false",
}

SOURCE_PREFIX_BY_KIND: Final[dict[str, str]] = {
    SESSION_KIND: "session",
    FILE_INTAKE_KIND: "file_intake",
    JOB_KIND: "job",
    AUDIT_KIND: "audit",
    BRIDGE_KIND: "bridge",
    GUARDED_KIND: "guarded",
    ROUTE_KIND: "route",
}

FailureRecoveryStatusV1 = Literal[
    "FAILURE_RECOVERY_RETRY_CANDIDATE_READY",
    "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_FAILURE_EVENT",
    "BLOCKED_INVALID_FAILURE_EVENT",
    "BLOCKED_UNSUPPORTED_FAILURE_KIND",
    "BLOCKED_MISSING_SOURCE_CANDIDATE",
    "BLOCKED_INVALID_SOURCE_CANDIDATE",
    "BLOCKED_SOURCE_CONTEXT_MISMATCH",
    "BLOCKED_RECOVERY_ATTEMPT_EXHAUSTED",
    "BLOCKED_UNSAFE_RECOVERY_FLAGS",
    "BLOCKED_UNSAFE_SOURCE_FLAGS",
    "BLOCKED_SOURCE_OWNER_MISMATCH",
    "BLOCKED_SOURCE_CASE_MISMATCH",
    "BLOCKED_SOURCE_SERVICE_MISMATCH",
    "BLOCKED_SOURCE_MUTATION_VIOLATION",
    "BLOCKED_HIDE_FAILURE_VIOLATION",
    "UNKNOWN",
]


class Service1FailureEventV1(TypedDict):
    failure_kind: str
    failure_status: str
    failure_summary: str
    failure_ref_suffix: str
    source_slice_kind: str
    source_ref_keys: list[str]
    recovery_attempt_count: int
    recovery_max_attempts: int
    is_recoverable: Literal[False]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1FailureRecoveryInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    audit_log_append_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    failure_event: dict[str, object] | None
    notes: list[str]


class Service1FailureRecoveryRetryCandidateV1(TypedDict):
    recovery_kind: Literal["FAILURE_RECOVERY_RETRY_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    failure_event_ref_candidate: str
    failure_kind: str
    failure_status: str
    failure_summary: str
    source_slice_kind: str
    source_slice_ref: str | None
    recovery_attempt_count: int
    recovery_max_attempts: int
    source_context_refs: dict[str, str]
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1FailureRecoveryFallbackCandidateV1(TypedDict):
    recovery_kind: Literal["FAILURE_RECOVERY_FALLBACK_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    failure_event_ref_candidate: str
    failure_kind: str
    failure_status: str
    failure_summary: str
    source_slice_kind: str
    source_slice_ref: str | None
    recovery_attempt_count: int
    recovery_max_attempts: int
    fallback_reason: str
    requires_owner_intervention: bool
    requires_operator_escalation: bool
    hide_failure: Literal[False]
    source_context_refs: dict[str, str]
    owner_notified: Literal[False]
    operator_escalation_authorized: Literal[False]
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1FailureRecoveryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: FailureRecoveryStatusV1
    failure_recovery_candidate: Service1FailureRecoveryRetryCandidateV1 | Service1FailureRecoveryFallbackCandidateV1 | None
    blocked_reason: str | None
    is_recoverable: bool
    recovery_attempt_count: int
    recovery_max_attempts: int
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_failure_recovery_v1(
    recovery_input: Service1FailureRecoveryInputV1,
) -> Service1FailureRecoveryResultV1:
    """Classify a Servicio 1 failure and emit a non-executable recovery candidate."""
    session = recovery_input.get("saas_case_session_candidate")
    if session is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=_notes(recovery_input.get("notes"), "Failure recovery requires a SaaS case session candidate."),
        )
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_invalid",
            notes=_notes(recovery_input.get("notes"), "SaaS case session candidate is invalid for failure recovery."),
        )

    session_validation_reason = _validate_session(session)
    if session_validation_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=session_validation_reason,
            notes=_notes(recovery_input.get("notes"), "SaaS case session candidate failed recovery anchor validation."),
        )

    failure_event = recovery_input.get("failure_event")
    if failure_event is None:
        return _result(
            status="BLOCKED_MISSING_FAILURE_EVENT",
            blocked_reason="failure_event_required",
            notes=_notes(recovery_input.get("notes"), "Failure recovery requires a structured failure event."),
        )
    if not isinstance(failure_event, dict) or not failure_event:
        return _result(
            status="BLOCKED_INVALID_FAILURE_EVENT",
            blocked_reason="failure_event_required",
            notes=_notes(recovery_input.get("notes"), "Failure event is invalid for recovery classification."),
        )

    event_validation = _validate_failure_event_shape(failure_event)
    if event_validation is not None:
        status, reason = event_validation
        return _result(
            status=status,
            blocked_reason=reason,
            recovery_attempt_count=_safe_int(failure_event.get("recovery_attempt_count")),
            recovery_max_attempts=_safe_int(failure_event.get("recovery_max_attempts")),
            notes=_notes(recovery_input.get("notes"), "Failure event failed shape or safety validation."),
        )

    failure_kind = str(failure_event["failure_kind"]).strip()
    source_slice_kind = str(failure_event["source_slice_kind"]).strip()
    source_candidate = _select_source_candidate(recovery_input=recovery_input, source_kind=source_slice_kind, session=session)
    if source_candidate is None:
        return _result(
            status="BLOCKED_MISSING_SOURCE_CANDIDATE",
            blocked_reason="source_candidate_required_for_failure_kind",
            recovery_attempt_count=int(failure_event["recovery_attempt_count"]),
            recovery_max_attempts=int(failure_event["recovery_max_attempts"]),
            notes=_notes(recovery_input.get("notes"), "Failure recovery requires the failed source candidate."),
        )

    source_validation = _validate_source_candidate(source_kind=source_slice_kind, source_candidate=source_candidate, session=session)
    if source_validation is not None:
        status, reason = source_validation
        if status in (
            "BLOCKED_SOURCE_OWNER_MISMATCH",
            "BLOCKED_SOURCE_CASE_MISMATCH",
            "BLOCKED_SOURCE_SERVICE_MISMATCH",
            "BLOCKED_SOURCE_CONTEXT_MISMATCH",
            "BLOCKED_UNSAFE_SOURCE_FLAGS",
            "BLOCKED_SOURCE_MUTATION_VIOLATION",
        ):
            candidate = _fallback_candidate(
                session=session,
                failure_event=failure_event,
                source_candidate=source_candidate,
                fallback_reason=reason,
                requires_owner_intervention=status
                in ("BLOCKED_SOURCE_OWNER_MISMATCH", "BLOCKED_SOURCE_CASE_MISMATCH", "BLOCKED_SOURCE_CONTEXT_MISMATCH"),
                requires_operator_escalation=True,
            )
            return _result(
                status="FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY",
                failure_recovery_candidate=candidate,
                blocked_reason=None,
                is_recoverable=False,
                recovery_attempt_count=int(failure_event["recovery_attempt_count"]),
                recovery_max_attempts=int(failure_event["recovery_max_attempts"]),
                notes=_notes(recovery_input.get("notes"), "Unsafe or mismatched source failure classified as visible fallback candidate."),
            )
        return _result(
            status=status,
            blocked_reason=reason,
            recovery_attempt_count=int(failure_event["recovery_attempt_count"]),
            recovery_max_attempts=int(failure_event["recovery_max_attempts"]),
            notes=_notes(recovery_input.get("notes"), "Failed source candidate is invalid for recovery classification."),
        )

    recovery_attempt_count = int(failure_event["recovery_attempt_count"])
    recovery_max_attempts = int(failure_event["recovery_max_attempts"])

    if failure_kind in RECOVERABLE_FAILURE_KINDS and recovery_attempt_count < recovery_max_attempts:
        candidate = _retry_candidate(session=session, failure_event=failure_event, source_candidate=source_candidate)
        return _result(
            status="FAILURE_RECOVERY_RETRY_CANDIDATE_READY",
            failure_recovery_candidate=candidate,
            blocked_reason=None,
            is_recoverable=True,
            recovery_attempt_count=recovery_attempt_count,
            recovery_max_attempts=recovery_max_attempts,
            notes=_notes(recovery_input.get("notes"), "Recoverable failure classified as non-executable retry candidate."),
        )

    fallback_reason = "recovery_attempt_exhausted" if recovery_attempt_count >= recovery_max_attempts else "failure_kind_not_recoverable"
    candidate = _fallback_candidate(
        session=session,
        failure_event=failure_event,
        source_candidate=source_candidate,
        fallback_reason=fallback_reason,
        requires_owner_intervention=failure_kind in (SESSION_CROSS_TENANT_VIOLATION, SOURCE_CANDIDATE_MISSING_SESSION_LINEAGE),
        requires_operator_escalation=failure_kind in NON_RECOVERABLE_FAILURE_KINDS,
    )
    return _result(
        status="FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY",
        failure_recovery_candidate=candidate,
        blocked_reason=None,
        is_recoverable=False,
        recovery_attempt_count=recovery_attempt_count,
        recovery_max_attempts=recovery_max_attempts,
        notes=_notes(recovery_input.get("notes"), "Failure classified as visible fallback candidate without retry execution."),
    )


def _validate_session(session: dict[str, object]) -> str | None:
    if session.get("session_kind") != SESSION_KIND:
        return "session_kind_must_be_saas_case_session_candidate"
    if session.get("service_name") != SERVICE_NAME:
        return "session_service_name_must_be_service_1"
    if _clean_required_ref(session.get("owner_ref")) is None:
        return "session_owner_ref_required"
    if _clean_required_ref(session.get("case_ref")) is None:
        return "session_case_ref_required"
    for flag_name, reason in SESSION_FLAG_REASON_BY_NAME.items():
        if session.get(flag_name) is not False:
            return reason
    return None


def _validate_failure_event_shape(failure_event: dict[str, object]) -> tuple[FailureRecoveryStatusV1, str] | None:
    failure_kind = _clean_required_ref(failure_event.get("failure_kind"))
    if failure_kind is None:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "failure_kind_required")
    if failure_kind not in ALLOWED_FAILURE_KINDS:
        return ("BLOCKED_UNSUPPORTED_FAILURE_KIND", "failure_kind_not_supported")
    if _clean_required_ref(failure_event.get("failure_status")) is None:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "failure_status_required")
    if _clean_required_ref(failure_event.get("failure_summary")) is None:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "failure_summary_required")
    if _clean_required_ref(failure_event.get("failure_ref_suffix")) is None:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "failure_ref_suffix_required")

    source_slice_kind = _clean_required_ref(failure_event.get("source_slice_kind"))
    if source_slice_kind is None:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "source_slice_kind_required")
    if source_slice_kind not in ALLOWED_SOURCE_SLICE_KINDS:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "source_slice_kind_not_supported")

    attempt_count = failure_event.get("recovery_attempt_count")
    if not isinstance(attempt_count, int) or isinstance(attempt_count, bool) or attempt_count < 0:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "recovery_attempt_count_invalid")
    max_attempts = failure_event.get("recovery_max_attempts")
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts <= 0:
        return ("BLOCKED_INVALID_FAILURE_EVENT", "recovery_max_attempts_invalid")

    for flag_name, reason in FAILURE_EVENT_FLAG_REASON_BY_NAME.items():
        if failure_event.get(flag_name, False) is not False:
            status: FailureRecoveryStatusV1 = "BLOCKED_HIDE_FAILURE_VIOLATION" if flag_name == "hide_failure" else "BLOCKED_UNSAFE_RECOVERY_FLAGS"
            return (status, reason)
    return None


def _select_source_candidate(
    *,
    recovery_input: Service1FailureRecoveryInputV1,
    source_kind: str,
    session: dict[str, object],
) -> dict[str, object] | None:
    if source_kind == SESSION_KIND:
        return dict(session)
    payload_key = PAYLOAD_KEY_BY_SOURCE_KIND.get(source_kind)
    if payload_key is None:
        return None
    candidate = recovery_input.get(payload_key)
    if not isinstance(candidate, dict) or not candidate:
        return None
    return dict(candidate)


def _validate_source_candidate(
    *,
    source_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> tuple[FailureRecoveryStatusV1, str] | None:
    if source_candidate.get(KIND_FIELD_BY_SOURCE_KIND[source_kind]) != source_kind:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_kind_mismatch")
    if source_candidate.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_SOURCE_SERVICE_MISMATCH", "source_candidate_service_name_must_be_service_1")

    source_owner_ref = _clean_required_ref(source_candidate.get("owner_ref"))
    if source_owner_ref is None:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_owner_ref_must_match_session")
    if source_owner_ref != str(session["owner_ref"]).strip():
        return ("BLOCKED_SOURCE_OWNER_MISMATCH", "source_candidate_owner_ref_must_match_session")

    source_case_ref = _clean_required_ref(source_candidate.get("case_ref"))
    if source_case_ref is None:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_case_ref_must_match_session")
    if source_case_ref != str(session["case_ref"]).strip():
        return ("BLOCKED_SOURCE_CASE_MISMATCH", "source_candidate_case_ref_must_match_session")

    source_session_ref = _candidate_source_session_ref(source_kind=source_kind, source_candidate=source_candidate)
    if source_session_ref is not None and source_session_ref != _source_session_ref(session):
        return ("BLOCKED_SOURCE_CONTEXT_MISMATCH", "source_candidate_session_ref_must_match_session")

    generic_reason = _generic_source_forbidden_reason(source_candidate)
    if generic_reason is not None:
        return ("BLOCKED_SOURCE_MUTATION_VIOLATION" if "mutation" in generic_reason else "BLOCKED_UNSAFE_SOURCE_FLAGS", generic_reason)

    source_flag_reason = _source_flag_reason(source_kind=source_kind, source_candidate=source_candidate)
    if source_flag_reason is not None:
        return ("BLOCKED_SOURCE_MUTATION_VIOLATION" if "mutation" in source_flag_reason else "BLOCKED_UNSAFE_SOURCE_FLAGS", source_flag_reason)

    if source_kind == AUDIT_KIND:
        audit_event_candidate = source_candidate.get("audit_event_candidate")
        if not isinstance(audit_event_candidate, dict) or not audit_event_candidate:
            return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_kind_mismatch")
        nested_reason = _generic_source_forbidden_reason(audit_event_candidate)
        if nested_reason is not None:
            return ("BLOCKED_UNSAFE_SOURCE_FLAGS", nested_reason)
    return None


def _retry_candidate(
    *,
    session: dict[str, object],
    failure_event: dict[str, object],
    source_candidate: dict[str, object],
) -> Service1FailureRecoveryRetryCandidateV1:
    base = _candidate_base(session=session, failure_event=failure_event, source_candidate=source_candidate)
    return {
        "recovery_kind": RETRY_KIND,
        **base,
        "recovery_execution_authorized": False,
        "scheduled_retry_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _fallback_candidate(
    *,
    session: dict[str, object],
    failure_event: dict[str, object],
    source_candidate: dict[str, object],
    fallback_reason: str,
    requires_owner_intervention: bool,
    requires_operator_escalation: bool,
) -> Service1FailureRecoveryFallbackCandidateV1:
    base = _candidate_base(session=session, failure_event=failure_event, source_candidate=source_candidate)
    return {
        "recovery_kind": FALLBACK_KIND,
        **base,
        "fallback_reason": fallback_reason,
        "requires_owner_intervention": requires_owner_intervention,
        "requires_operator_escalation": requires_operator_escalation,
        "hide_failure": False,
        "owner_notified": False,
        "operator_escalation_authorized": False,
        "recovery_execution_authorized": False,
        "scheduled_retry_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _candidate_base(
    *,
    session: dict[str, object],
    failure_event: dict[str, object],
    source_candidate: dict[str, object],
) -> dict[str, object]:
    return {
        "owner_ref": str(session["owner_ref"]).strip(),
        "case_ref": str(session["case_ref"]).strip(),
        "service_name": SERVICE_NAME,
        "source_session_ref": _source_session_ref(session),
        "failure_event_ref_candidate": _failure_event_ref_candidate(session=session, failure_event=failure_event),
        "failure_kind": str(failure_event["failure_kind"]).strip(),
        "failure_status": str(failure_event["failure_status"]).strip(),
        "failure_summary": str(failure_event["failure_summary"]).strip(),
        "source_slice_kind": str(failure_event["source_slice_kind"]).strip(),
        "source_slice_ref": _source_slice_ref(source_candidate),
        "recovery_attempt_count": int(failure_event["recovery_attempt_count"]),
        "recovery_max_attempts": int(failure_event["recovery_max_attempts"]),
        "source_context_refs": _source_context_refs(
            source_kind=str(failure_event["source_slice_kind"]).strip(),
            source_candidate=source_candidate,
            requested_keys=failure_event.get("source_ref_keys"),
        ),
    }


def _failure_event_ref_candidate(*, session: dict[str, object], failure_event: dict[str, object]) -> str:
    return "failure_event_candidate:{}:{}:{}:{}".format(
        _safe_ref(str(session["owner_ref"])),
        _safe_ref(str(session["case_ref"])),
        _safe_ref(str(failure_event["failure_kind"])),
        _safe_ref(str(failure_event["failure_ref_suffix"])),
    )


def _source_slice_ref(source_candidate: dict[str, object]) -> str | None:
    for key in (
        "failure_ref_candidate",
        "audit_event_ref_candidate",
        "audit_log_ref_candidate",
        "saas_job_orchestration_ref",
        "source_file_intake_ref",
        "evidence_ref_candidate",
        "file_ref",
        "owner_question_route_ref_candidate",
        "guarded_response_ref_candidate",
        "owner_message_ref_candidate",
        "source_session_ref",
        "case_ref",
    ):
        value = source_candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    audit_event_candidate = source_candidate.get("audit_event_candidate")
    if isinstance(audit_event_candidate, dict):
        for key in ("audit_event_ref_candidate", "source_slice_ref"):
            value = audit_event_candidate.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _source_context_refs(
    *,
    source_kind: str,
    source_candidate: dict[str, object],
    requested_keys: object,
) -> dict[str, str]:
    safe_refs = _default_source_refs(source_kind=source_kind, source_candidate=source_candidate)
    if not isinstance(requested_keys, list) or not requested_keys:
        return dict(safe_refs)
    filtered: dict[str, str] = {}
    for key in requested_keys:
        if not isinstance(key, str) or not key.strip():
            continue
        stripped = key.strip()
        if stripped in safe_refs:
            filtered[stripped] = safe_refs[stripped]
    return filtered


def _default_source_refs(*, source_kind: str, source_candidate: dict[str, object]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for key in (
        "source_session_ref",
        "file_ref",
        "evidence_ref_candidate",
        "source_file_intake_ref",
        "saas_job_orchestration_ref",
        "audit_log_ref_candidate",
        "audit_event_ref_candidate",
        "owner_message_ref_candidate",
        "guarded_response_ref_candidate",
        "owner_question_route_ref_candidate",
        "case_ref",
    ):
        value = source_candidate.get(key)
        if isinstance(value, str) and value.strip():
            refs[key] = value.strip()
    audit_event_candidate = source_candidate.get("audit_event_candidate")
    if isinstance(audit_event_candidate, dict):
        for key in ("audit_event_ref_candidate", "source_slice_ref", "audit_log_ref_candidate", "source_session_ref"):
            value = audit_event_candidate.get(key)
            if isinstance(value, str) and value.strip():
                refs[f"audit_event.{key}"] = value.strip()
    if source_kind == JOB_KIND:
        refs.update(_clean_refs_map(source_candidate.get("autonomous_chain_candidate_refs")))
    if source_kind in (BRIDGE_KIND, GUARDED_KIND, ROUTE_KIND):
        refs.update(_clean_refs_map(source_candidate.get("cited_safe_context_refs")))
        refs.update(_clean_refs_map(source_candidate.get("safe_context_refs_for_future_llm")))
    return refs


def _clean_refs_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if isinstance(key, str) and key.strip() and isinstance(item, str) and item.strip():
            clean[key.strip()] = item.strip()
    return clean


def _candidate_source_session_ref(*, source_kind: str, source_candidate: dict[str, object]) -> str | None:
    if source_kind == SESSION_KIND:
        return _optional_ref(source_candidate, ("session_ref", "case_ref"))
    if source_kind == AUDIT_KIND:
        return _optional_ref(source_candidate, ("source_session_ref",))
    return _optional_ref(source_candidate, ("source_session_ref", "case_ref"))


def _generic_source_forbidden_reason(candidate: dict[str, object]) -> str | None:
    for flag_name, reason in GENERIC_SOURCE_FORBIDDEN_FLAG_REASON_BY_NAME.items():
        if flag_name in candidate and candidate.get(flag_name) is not False:
            return reason
    return None


def _source_flag_reason(*, source_kind: str, source_candidate: dict[str, object]) -> str | None:
    for flag_name, reason in SOURCE_FLAG_REASON_BY_KIND[source_kind].items():
        if flag_name in source_candidate and source_candidate.get(flag_name) is not False:
            return reason
    return None


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _optional_ref(candidate: dict[str, object], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _safe_ref(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_")
    safe_chars: list[str] = []
    for char in normalized:
        if char.isalnum() or char in ("-", "_", ":"):
            safe_chars.append(char)
        else:
            safe_chars.append("_")
    return "".join(safe_chars).strip("_") or "unknown"


def _safe_int(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: FailureRecoveryStatusV1,
    failure_recovery_candidate: Service1FailureRecoveryRetryCandidateV1 | Service1FailureRecoveryFallbackCandidateV1 | None = None,
    blocked_reason: str | None = None,
    is_recoverable: bool = False,
    recovery_attempt_count: int = 0,
    recovery_max_attempts: int = 0,
    notes: list[str] | None = None,
) -> Service1FailureRecoveryResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "failure_recovery_candidate": failure_recovery_candidate,
        "blocked_reason": blocked_reason,
        "is_recoverable": is_recoverable,
        "recovery_attempt_count": recovery_attempt_count,
        "recovery_max_attempts": recovery_max_attempts,
        "recovery_execution_authorized": False,
        "scheduled_retry_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "RETRY_KIND",
    "FALLBACK_KIND",
    "SESSION_KIND",
    "FILE_INTAKE_KIND",
    "JOB_KIND",
    "AUDIT_KIND",
    "BRIDGE_KIND",
    "GUARDED_KIND",
    "ROUTE_KIND",
    "RECOVERABLE_FAILURE_KINDS",
    "NON_RECOVERABLE_FAILURE_KINDS",
    "Service1FailureEventV1",
    "Service1FailureRecoveryInputV1",
    "Service1FailureRecoveryRetryCandidateV1",
    "Service1FailureRecoveryFallbackCandidateV1",
    "Service1FailureRecoveryResultV1",
    "build_service_1_failure_recovery_v1",
]
