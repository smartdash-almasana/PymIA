from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_AUDIT_LOG_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
AUDIT_KIND: Final[str] = "AUDIT_LOG_APPEND_CANDIDATE"
AUDIT_EVENT_KIND: Final[str] = "AUDIT_EVENT_CANDIDATE"
APPEND_OPERATION: Final[str] = "APPEND_EVENT"

SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
FILE_INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"
JOB_KIND: Final[str] = "SAAS_JOB_ORCHESTRATION_CANDIDATE"
BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"
GUARDED_KIND: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE"
ROUTE_KIND: Final[str] = "OWNER_QUESTION_ROUTE_CANDIDATE"

SESSION_CANDIDATE_RECORDED: Final[str] = "SESSION_CANDIDATE_RECORDED"
FILE_INTAKE_CANDIDATE_RECORDED: Final[str] = "FILE_INTAKE_CANDIDATE_RECORDED"
JOB_ORCHESTRATION_CANDIDATE_RECORDED: Final[str] = "JOB_ORCHESTRATION_CANDIDATE_RECORDED"
CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED: Final[str] = "CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED"
GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED"
OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED: Final[str] = "OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED"
SLICE_BLOCKED_RECORDED: Final[str] = "SLICE_BLOCKED_RECORDED"

ALLOWED_EVENT_KINDS: Final[tuple[str, ...]] = (
    SESSION_CANDIDATE_RECORDED,
    FILE_INTAKE_CANDIDATE_RECORDED,
    JOB_ORCHESTRATION_CANDIDATE_RECORDED,
    CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED,
    GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED,
    OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED,
    SLICE_BLOCKED_RECORDED,
)

ALLOWED_SOURCE_SLICE_KINDS: Final[tuple[str, ...]] = (
    SESSION_KIND,
    FILE_INTAKE_KIND,
    JOB_KIND,
    BRIDGE_KIND,
    GUARDED_KIND,
    ROUTE_KIND,
)

EVENT_KIND_TO_SOURCE_KIND: Final[dict[str, str]] = {
    SESSION_CANDIDATE_RECORDED: SESSION_KIND,
    FILE_INTAKE_CANDIDATE_RECORDED: FILE_INTAKE_KIND,
    JOB_ORCHESTRATION_CANDIDATE_RECORDED: JOB_KIND,
    CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED: BRIDGE_KIND,
    GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED: GUARDED_KIND,
    OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED: ROUTE_KIND,
}

SESSION_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "runtime_authorized": "session_runtime_authorized_must_be_false",
    "job_authorized": "session_job_authorized_must_be_false",
    "file_upload_authorized": "session_file_upload_authorized_must_be_false",
    "api_exposed": "session_api_exposed_must_be_false",
}

SOURCE_FLAG_NAMES_BY_KIND: Final[dict[str, tuple[str, ...]]] = {
    SESSION_KIND: ("runtime_authorized", "job_authorized", "file_upload_authorized", "api_exposed"),
    FILE_INTAKE_KIND: (
        "task_spec_candidate_allowed",
        "upload_authorized",
        "file_read_authorized",
        "parser_authorized",
        "job_authorized",
        "runtime_authorized",
        "api_exposed",
    ),
    JOB_KIND: (
        "worker_authorized",
        "queue_authorized",
        "async_execution_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "runtime_authorized",
        "api_exposed",
    ),
    BRIDGE_KIND: (
        "llm_authorized",
        "pydantic_ai_authorized",
        "prompt_runtime_authorized",
        "chatbot_authorized",
        "tool_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "mutation_authorized",
        "runtime_authorized",
        "api_exposed",
    ),
    GUARDED_KIND: (
        "client_delivery_authorized",
        "llm_authorized",
        "pydantic_ai_authorized",
        "prompt_runtime_authorized",
        "chatbot_authorized",
        "tool_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "mutation_authorized",
        "runtime_authorized",
        "api_exposed",
    ),
    ROUTE_KIND: (
        "client_delivery_authorized",
        "llm_authorized",
        "pydantic_ai_authorized",
        "prompt_runtime_authorized",
        "chatbot_authorized",
        "tool_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "mutation_authorized",
        "runtime_authorized",
        "api_exposed",
    ),
}

AuditLogStatusV1 = Literal[
    "AUDIT_LOG_APPEND_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_AUDIT_EVENT_REQUEST",
    "BLOCKED_INVALID_AUDIT_EVENT_REQUEST",
    "BLOCKED_UNSUPPORTED_EVENT_KIND",
    "BLOCKED_MISSING_SOURCE_CANDIDATE",
    "BLOCKED_INVALID_SOURCE_CANDIDATE",
    "BLOCKED_SOURCE_CONTEXT_MISMATCH",
    "BLOCKED_APPEND_ONLY_VIOLATION",
    "BLOCKED_MUTATION_VIOLATION",
    "BLOCKED_UNSAFE_FLAGS",
    "UNKNOWN",
]


class Service1AuditEventRequestV1(TypedDict):
    event_kind: str
    event_status: str
    event_summary: str
    event_ref_suffix: str
    append_operation: Literal["APPEND_EVENT"]
    source_slice_kind: str
    source_ref_keys: list[str]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1AuditLogInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    audit_event_request: dict[str, object] | None
    notes: list[str]


class Service1AuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: str
    source_slice_ref: str | None
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


class Service1AuditLogAppendCandidateV1(TypedDict):
    audit_kind: Literal["AUDIT_LOG_APPEND_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    audit_log_ref_candidate: str
    append_operation: Literal["APPEND_EVENT"]
    appended_event_count: Literal[1]
    audit_event_candidate: Service1AuditEventCandidateV1
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1AuditLogResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: AuditLogStatusV1
    audit_log_append_candidate: Service1AuditLogAppendCandidateV1 | None
    blocked_reason: str | None
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_audit_log_v1(
    audit_input: Service1AuditLogInputV1,
) -> Service1AuditLogResultV1:
    """Build one deterministic append-only audit candidate for Servicio 1.

    This contract validates session-anchored audit metadata only. It does not
    persist events, open files, expose APIs, start workers, call pipelines,
    runners, LLMs, or any runtime boundary.
    """
    session = audit_input.get("saas_case_session_candidate")
    if session is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=_notes(audit_input.get("notes"), "Audit log append candidate requires a SaaS case session candidate."),
        )
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_invalid",
            notes=_notes(audit_input.get("notes"), "SaaS case session candidate is invalid for audit logging."),
        )

    session_validation_reason = _validate_session(session)
    if session_validation_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=session_validation_reason,
            notes=_notes(audit_input.get("notes"), "SaaS case session candidate failed audit anchor validation."),
        )

    event_request = audit_input.get("audit_event_request")
    if event_request is None:
        return _result(
            status="BLOCKED_MISSING_AUDIT_EVENT_REQUEST",
            blocked_reason="audit_event_request_required",
            notes=_notes(audit_input.get("notes"), "Audit log append candidate requires a structured audit_event_request."),
        )
    if not isinstance(event_request, dict) or not event_request:
        return _result(
            status="BLOCKED_INVALID_AUDIT_EVENT_REQUEST",
            blocked_reason="audit_event_request_invalid",
            notes=_notes(audit_input.get("notes"), "Structured audit_event_request is invalid."),
        )

    request_validation = _validate_event_request(event_request)
    if request_validation is not None:
        status, reason = request_validation
        return _result(
            status=status,
            blocked_reason=reason,
            notes=_notes(audit_input.get("notes"), "Audit event request failed validation."),
        )

    event_kind = str(event_request["event_kind"]).strip()
    source_slice_kind = str(event_request["source_slice_kind"]).strip()
    expected_source_kind = EVENT_KIND_TO_SOURCE_KIND.get(event_kind)
    if expected_source_kind is not None and source_slice_kind != expected_source_kind:
        return _result(
            status="BLOCKED_INVALID_AUDIT_EVENT_REQUEST",
            blocked_reason="source_candidate_required_for_event_kind",
            notes=_notes(audit_input.get("notes"), "Audit event kind and source slice kind do not match."),
        )

    source_candidate = _select_source_candidate(audit_input=audit_input, source_slice_kind=source_slice_kind, session=session)
    if source_candidate is None:
        return _result(
            status="BLOCKED_MISSING_SOURCE_CANDIDATE",
            blocked_reason="source_candidate_required_for_event_kind",
            notes=_notes(audit_input.get("notes"), "Audit event requires a matching source slice candidate."),
        )

    source_validation = _validate_source_candidate(source_slice_kind=source_slice_kind, source_candidate=source_candidate, session=session)
    if source_validation is not None:
        status, reason = source_validation
        return _result(
            status=status,
            blocked_reason=reason,
            notes=_notes(audit_input.get("notes"), "Source slice candidate failed audit validation."),
        )

    source_context = _source_context_refs(source_slice_kind=source_slice_kind, source_candidate=source_candidate, session=session)
    source_ref_keys = _clean_str_list(event_request.get("source_ref_keys"))
    if any(ref_key not in source_context for ref_key in source_ref_keys):
        return _result(
            status="BLOCKED_SOURCE_CONTEXT_MISMATCH",
            blocked_reason="source_ref_key_not_allowed",
            notes=_notes(audit_input.get("notes"), "Requested source_ref_keys are not available in the safe source context."),
        )

    owner_ref = str(session["owner_ref"]).strip()
    case_ref = str(session["case_ref"]).strip()
    source_session_ref = _source_session_ref(session)
    event_status = str(event_request["event_status"]).strip()
    event_summary = _clean_summary(event_request.get("event_summary"))
    event_ref_suffix = str(event_request["event_ref_suffix"]).strip()
    audit_log_ref_candidate = _audit_log_ref_candidate(owner_ref=owner_ref, case_ref=case_ref)
    audit_event_ref_candidate = _audit_event_ref_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        event_kind=event_kind,
        event_ref_suffix=event_ref_suffix,
    )

    audit_event_candidate: Service1AuditEventCandidateV1 = {
        "audit_event_kind": AUDIT_EVENT_KIND,
        "event_kind": event_kind,
        "event_status": event_status,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "source_slice_kind": source_slice_kind,
        "source_slice_ref": _source_slice_ref(source_slice_kind=source_slice_kind, source_candidate=source_candidate, session=session),
        "audit_log_ref_candidate": audit_log_ref_candidate,
        "audit_event_ref_candidate": audit_event_ref_candidate,
        "append_operation": APPEND_OPERATION,
        "event_summary": event_summary,
        "source_context_refs": {ref_key: source_context[ref_key] for ref_key in source_ref_keys},
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

    append_candidate: Service1AuditLogAppendCandidateV1 = {
        "audit_kind": AUDIT_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "audit_log_ref_candidate": audit_log_ref_candidate,
        "append_operation": APPEND_OPERATION,
        "appended_event_count": 1,
        "audit_event_candidate": audit_event_candidate,
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

    return _result(
        status="AUDIT_LOG_APPEND_CANDIDATE_READY",
        audit_log_append_candidate=append_candidate,
        notes=_notes(audit_input.get("notes"), "Audit log append candidate created without persistence, IO, or runtime authority."),
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


def _validate_event_request(event_request: dict[str, object]) -> tuple[AuditLogStatusV1, str] | None:
    event_kind = _clean_required_ref(event_request.get("event_kind"))
    if event_kind is None:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "event_kind_required")
    if event_kind not in ALLOWED_EVENT_KINDS:
        return ("BLOCKED_UNSUPPORTED_EVENT_KIND", "event_kind_not_supported")

    if _clean_required_ref(event_request.get("event_status")) is None:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "event_status_required")
    if _clean_summary(event_request.get("event_summary")) is None:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "event_summary_required")
    if _clean_required_ref(event_request.get("event_ref_suffix")) is None:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "event_ref_suffix_required")

    source_slice_kind = _clean_required_ref(event_request.get("source_slice_kind"))
    if source_slice_kind is None:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "source_slice_kind_required")
    if source_slice_kind not in ALLOWED_SOURCE_SLICE_KINDS:
        return ("BLOCKED_INVALID_AUDIT_EVENT_REQUEST", "source_slice_kind_not_supported")

    if event_request.get("append_operation") != APPEND_OPERATION:
        return ("BLOCKED_APPEND_ONLY_VIOLATION", "append_operation_must_be_append_event")
    if event_request.get("mutation_requested") is not False:
        return ("BLOCKED_MUTATION_VIOLATION", "mutation_requested_must_be_false")
    if event_request.get("owner_visible") is not False:
        return ("BLOCKED_UNSAFE_FLAGS", "audit_event_flags_must_be_false")
    if event_request.get("runtime_authorized") is not False:
        return ("BLOCKED_UNSAFE_FLAGS", "audit_event_flags_must_be_false")
    if event_request.get("api_exposed") is not False:
        return ("BLOCKED_UNSAFE_FLAGS", "audit_event_flags_must_be_false")
    return None


def _select_source_candidate(
    *,
    audit_input: Service1AuditLogInputV1,
    source_slice_kind: str,
    session: dict[str, object],
) -> dict[str, object] | None:
    if source_slice_kind == SESSION_KIND:
        return dict(session)
    key_by_kind: dict[str, str] = {
        FILE_INTAKE_KIND: "saas_file_intake_candidate",
        JOB_KIND: "saas_job_orchestration_candidate",
        BRIDGE_KIND: "conversational_owner_bridge_candidate",
        GUARDED_KIND: "guarded_llm_response_candidate",
        ROUTE_KIND: "owner_question_route_candidate",
    }
    payload_key = key_by_kind.get(source_slice_kind)
    if payload_key is None:
        return None
    value = audit_input.get(payload_key)
    if not isinstance(value, dict) or not value:
        return None
    return dict(value)


def _validate_source_candidate(
    *,
    source_slice_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> tuple[AuditLogStatusV1, str] | None:
    kind_field_by_kind: dict[str, str] = {
        SESSION_KIND: "session_kind",
        FILE_INTAKE_KIND: "intake_kind",
        JOB_KIND: "job_kind",
        BRIDGE_KIND: "bridge_kind",
        GUARDED_KIND: "gate_kind",
        ROUTE_KIND: "router_kind",
    }
    kind_field_name = kind_field_by_kind[source_slice_kind]
    if source_candidate.get(kind_field_name) != source_slice_kind:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_kind_mismatch")
    if source_candidate.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_service_name_must_be_service_1")

    session_owner_ref = str(session["owner_ref"]).strip()
    session_case_ref = str(session["case_ref"]).strip()
    session_source_session_ref = _source_session_ref(session)

    source_owner_ref = _clean_required_ref(source_candidate.get("owner_ref"))
    if source_owner_ref is None or source_owner_ref != session_owner_ref:
        return ("BLOCKED_SOURCE_CONTEXT_MISMATCH", "source_candidate_owner_ref_must_match_session")

    source_case_ref = _clean_required_ref(source_candidate.get("case_ref"))
    if source_case_ref is None or source_case_ref != session_case_ref:
        return ("BLOCKED_SOURCE_CONTEXT_MISMATCH", "source_candidate_case_ref_must_match_session")

    candidate_source_session_ref = _optional_ref(
        source_candidate,
        preferred_keys=("source_session_ref", "case_ref"),
        fallback=None,
    )
    if candidate_source_session_ref is not None and candidate_source_session_ref != session_source_session_ref:
        return ("BLOCKED_SOURCE_CONTEXT_MISMATCH", "source_candidate_source_session_ref_must_match_session")

    if _flags_are_unsafe(source_candidate, SOURCE_FLAG_NAMES_BY_KIND[source_slice_kind]):
        return ("BLOCKED_UNSAFE_FLAGS", "source_candidate_flags_must_be_false")
    return None


def _source_context_refs(
    *,
    source_slice_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> dict[str, str]:
    owner_ref = str(session["owner_ref"]).strip()
    case_ref = str(session["case_ref"]).strip()
    source_session_ref = _source_session_ref(session)
    context: dict[str, str] = {
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "source_session_ref": source_session_ref,
    }

    if source_slice_kind == SESSION_KIND:
        context.update(_clean_refs_map(source_candidate.get("service_1_state_refs")))
        return context

    if source_slice_kind == FILE_INTAKE_KIND:
        context.update(
            _refs_from_keys(
                source_candidate,
                ("file_ref", "evidence_ref_candidate", "source_session_ref"),
            )
        )
        return context

    if source_slice_kind == JOB_KIND:
        context.update(
            _refs_from_keys(
                source_candidate,
                ("source_file_intake_ref", "source_session_ref"),
            )
        )
        context.update(_clean_refs_map(source_candidate.get("autonomous_chain_candidate_refs")))
        return context

    if source_slice_kind == BRIDGE_KIND:
        context.update(
            _refs_from_keys(
                source_candidate,
                ("owner_message_ref_candidate", "owner_delivery_packet_ref", "saas_job_orchestration_ref", "source_session_ref"),
            )
        )
        context.update(_clean_refs_map(source_candidate.get("service_1_state_refs")))
        context.update(_clean_refs_map(source_candidate.get("generated_folder_refs")))
        context.update(_clean_refs_map(source_candidate.get("safe_context_refs_for_future_llm")))
        return context

    if source_slice_kind == GUARDED_KIND:
        context.update(
            _refs_from_keys(
                source_candidate,
                ("source_bridge_ref_candidate", "source_owner_message_ref_candidate", "source_session_ref"),
            )
        )
        context.update(_clean_refs_map(source_candidate.get("cited_safe_context_refs")))
        return context

    if source_slice_kind == ROUTE_KIND:
        context.update(_clean_refs_map(source_candidate.get("cited_safe_context_refs")))
        return context

    return context


def _source_slice_ref(
    *,
    source_slice_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> str | None:
    if source_slice_kind == SESSION_KIND:
        return _optional_ref(source_candidate, preferred_keys=("session_ref", "case_ref"), fallback=_source_session_ref(session))
    if source_slice_kind == FILE_INTAKE_KIND:
        return _optional_ref(
            source_candidate,
            preferred_keys=("file_intake_ref", "evidence_ref_candidate", "file_ref"),
            fallback=None,
        )
    if source_slice_kind == JOB_KIND:
        return _optional_ref(
            source_candidate,
            preferred_keys=("saas_job_orchestration_ref", "source_file_intake_ref", "source_session_ref"),
            fallback=None,
        )
    if source_slice_kind == BRIDGE_KIND:
        return _optional_ref(
            source_candidate,
            preferred_keys=("owner_message_ref_candidate", "source_session_ref"),
            fallback=None,
        )
    if source_slice_kind == GUARDED_KIND:
        return _optional_ref(
            source_candidate,
            preferred_keys=("source_bridge_ref_candidate", "source_owner_message_ref_candidate", "source_session_ref"),
            fallback=None,
        )
    if source_slice_kind == ROUTE_KIND:
        return _optional_ref(
            source_candidate,
            preferred_keys=("source_session_ref",),
            fallback=None,
        )
    return None


def _audit_log_ref_candidate(*, owner_ref: str, case_ref: str) -> str:
    return f"audit_log_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}"


def _audit_event_ref_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    event_kind: str,
    event_ref_suffix: str,
) -> str:
    return (
        f"audit_event_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:"
        f"{_safe_ref(event_kind)}:{_safe_ref(event_ref_suffix)}"
    )


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_summary(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return normalized


def _clean_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    clean: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if not stripped:
            continue
        clean.append(stripped)
    return clean


def _clean_refs_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(item, str) or not item.strip():
            continue
        clean[key] = item.strip()
    return clean


def _refs_from_keys(source_candidate: dict[str, object], keys: tuple[str, ...]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for key in keys:
        value = source_candidate.get(key)
        if isinstance(value, str) and value.strip():
            refs[key] = value.strip()
    return refs


def _optional_ref(
    source_candidate: dict[str, object],
    *,
    preferred_keys: tuple[str, ...],
    fallback: str | None,
) -> str | None:
    for key in preferred_keys:
        value = source_candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _flags_are_unsafe(candidate: dict[str, object], flag_names: tuple[str, ...]) -> bool:
    return any(candidate.get(flag_name) is not False for flag_name in flag_names)


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: AuditLogStatusV1,
    audit_log_append_candidate: Service1AuditLogAppendCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1AuditLogResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "audit_log_append_candidate": audit_log_append_candidate,
        "blocked_reason": blocked_reason,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "AUDIT_KIND",
    "AUDIT_EVENT_KIND",
    "APPEND_OPERATION",
    "SESSION_KIND",
    "FILE_INTAKE_KIND",
    "JOB_KIND",
    "BRIDGE_KIND",
    "GUARDED_KIND",
    "ROUTE_KIND",
    "ALLOWED_EVENT_KINDS",
    "ALLOWED_SOURCE_SLICE_KINDS",
    "Service1AuditEventRequestV1",
    "Service1AuditLogInputV1",
    "Service1AuditEventCandidateV1",
    "Service1AuditLogAppendCandidateV1",
    "Service1AuditLogResultV1",
    "build_service_1_audit_log_v1",
]
