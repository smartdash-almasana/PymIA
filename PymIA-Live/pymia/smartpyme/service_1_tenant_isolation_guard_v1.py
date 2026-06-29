from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_TENANT_ISOLATION_GUARD_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
GUARD_KIND: Final[str] = "TENANT_ISOLATION_GUARD_CANDIDATE"

SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
FILE_INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"
JOB_KIND: Final[str] = "SAAS_JOB_ORCHESTRATION_CANDIDATE"
AUDIT_KIND: Final[str] = "AUDIT_LOG_APPEND_CANDIDATE"
BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"
GUARDED_KIND: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE"
ROUTE_KIND: Final[str] = "OWNER_QUESTION_ROUTE_CANDIDATE"

ALLOWED_SOURCE_CANDIDATE_KINDS: Final[tuple[str, ...]] = (
    SESSION_KIND,
    FILE_INTAKE_KIND,
    JOB_KIND,
    AUDIT_KIND,
    BRIDGE_KIND,
    GUARDED_KIND,
    ROUTE_KIND,
)

SESSION_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "runtime_authorized": "session_runtime_authorized_must_be_false",
    "job_authorized": "session_job_authorized_must_be_false",
    "file_upload_authorized": "session_file_upload_authorized_must_be_false",
    "api_exposed": "session_api_exposed_must_be_false",
}

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

SOURCE_FLAG_REASON_BY_KIND: Final[dict[str, dict[str, str]]] = {
    SESSION_KIND: {
        "runtime_authorized": "runtime_authorized_must_be_false",
        "job_authorized": "source_flags_must_be_false",
        "file_upload_authorized": "source_flags_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    FILE_INTAKE_KIND: {
        "task_spec_candidate_allowed": "source_flags_must_be_false",
        "upload_authorized": "source_flags_must_be_false",
        "file_read_authorized": "source_flags_must_be_false",
        "parser_authorized": "source_flags_must_be_false",
        "job_authorized": "source_flags_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    JOB_KIND: {
        "worker_authorized": "worker_authorized_must_be_false",
        "queue_authorized": "source_flags_must_be_false",
        "async_execution_authorized": "source_flags_must_be_false",
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
        "prompt_runtime_authorized": "source_flags_must_be_false",
        "chatbot_authorized": "source_flags_must_be_false",
        "tool_authorized": "source_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "source_flags_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    GUARDED_KIND: {
        "client_delivery_authorized": "source_flags_must_be_false",
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "prompt_runtime_authorized": "source_flags_must_be_false",
        "chatbot_authorized": "source_flags_must_be_false",
        "tool_authorized": "source_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "source_flags_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
    ROUTE_KIND: {
        "client_delivery_authorized": "source_flags_must_be_false",
        "llm_authorized": "llm_authorized_must_be_false",
        "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
        "prompt_runtime_authorized": "source_flags_must_be_false",
        "chatbot_authorized": "source_flags_must_be_false",
        "tool_authorized": "source_flags_must_be_false",
        "pipeline_authorized": "pipeline_authorized_must_be_false",
        "runner_authorized": "runner_authorized_must_be_false",
        "mutation_authorized": "source_flags_must_be_false",
        "runtime_authorized": "runtime_authorized_must_be_false",
        "api_exposed": "api_exposed_must_be_false",
    },
}

GENERIC_FORBIDDEN_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "correction_applied": "correction_applied_must_be_false",
    "auth_authorized": "auth_authorized_must_be_false",
    "storage_write_authorized": "storage_write_authorized_must_be_false",
    "db_authorized": "db_authorized_must_be_false",
    "worker_authorized": "worker_authorized_must_be_false",
    "pipeline_authorized": "pipeline_authorized_must_be_false",
    "runner_authorized": "runner_authorized_must_be_false",
    "llm_authorized": "llm_authorized_must_be_false",
    "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
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

TenantIsolationGuardStatusV1 = Literal[
    "TENANT_ISOLATION_GUARD_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_SOURCE_CANDIDATES",
    "BLOCKED_UNSUPPORTED_SOURCE_KIND",
    "BLOCKED_MISSING_SOURCE_CANDIDATE",
    "BLOCKED_INVALID_SOURCE_CANDIDATE",
    "BLOCKED_CROSS_TENANT_CONTEXT",
    "BLOCKED_CROSS_CASE_CONTEXT",
    "BLOCKED_CROSS_SESSION_CONTEXT",
    "BLOCKED_UNSAFE_FLAGS",
    "UNKNOWN",
]


class Service1TenantIsolationGuardInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    audit_log_append_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    requested_source_candidate_kinds: list[str]
    notes: list[str]


class Service1TenantIsolationGuardCandidateV1(TypedDict):
    guard_kind: Literal["TENANT_ISOLATION_GUARD_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    checked_source_candidate_kinds: list[str]
    checked_source_refs: dict[str, str]
    tenant_isolation_passed: Literal[True]
    cross_tenant_access_detected: Literal[False]
    cross_case_access_detected: Literal[False]
    cross_session_access_detected: Literal[False]
    correction_applied: Literal[False]
    auth_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1TenantIsolationGuardResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: TenantIsolationGuardStatusV1
    tenant_isolation_guard_candidate: Service1TenantIsolationGuardCandidateV1 | None
    blocked_reason: str | None
    auth_authorized: Literal[False]
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


def build_service_1_tenant_isolation_guard_v1(
    guard_input: Service1TenantIsolationGuardInputV1,
) -> Service1TenantIsolationGuardResultV1:
    """Validate tenant/session/case lineage across Servicio 1 candidates.

    This guard is deterministic and read-only. It does not authenticate users,
    correct lineage mismatches, write storage, expose APIs, or invoke runtime
    execution layers.
    """
    session = guard_input.get("saas_case_session_candidate")
    if session is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=_notes(guard_input.get("notes"), "Tenant isolation guard requires a SaaS case session candidate."),
        )
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_invalid",
            notes=_notes(guard_input.get("notes"), "SaaS case session candidate is invalid for tenant isolation."),
        )

    session_validation_reason = _validate_session(session)
    if session_validation_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=session_validation_reason,
            notes=_notes(guard_input.get("notes"), "SaaS case session candidate failed tenant isolation anchor validation."),
        )

    requested_source_candidate_kinds = _clean_requested_source_candidate_kinds(
        guard_input.get("requested_source_candidate_kinds")
    )
    if not requested_source_candidate_kinds:
        return _result(
            status="BLOCKED_MISSING_SOURCE_CANDIDATES",
            blocked_reason="requested_source_candidate_kinds_required",
            notes=_notes(guard_input.get("notes"), "Tenant isolation guard requires at least one requested source candidate kind."),
        )

    unsupported_kind = next(
        (kind for kind in requested_source_candidate_kinds if kind not in ALLOWED_SOURCE_CANDIDATE_KINDS),
        None,
    )
    if unsupported_kind is not None:
        return _result(
            status="BLOCKED_UNSUPPORTED_SOURCE_KIND",
            blocked_reason="source_candidate_kind_not_supported",
            notes=_notes(guard_input.get("notes"), "Requested source candidate kind is not supported by tenant isolation guard."),
        )

    owner_ref = str(session["owner_ref"]).strip()
    case_ref = str(session["case_ref"]).strip()
    source_session_ref = _source_session_ref(session)
    checked_source_refs: dict[str, str] = {}

    for source_kind in requested_source_candidate_kinds:
        source_candidate = _select_source_candidate(guard_input=guard_input, source_kind=source_kind, session=session)
        if source_candidate is None:
            return _result(
                status="BLOCKED_MISSING_SOURCE_CANDIDATE",
                blocked_reason="source_candidate_required",
                notes=_notes(guard_input.get("notes"), "Requested source candidate is missing for tenant isolation guard."),
            )

        source_validation = _validate_source_candidate(
            source_kind=source_kind,
            source_candidate=source_candidate,
            session=session,
        )
        if source_validation is not None:
            status, reason = source_validation
            return _result(
                status=status,
                blocked_reason=reason,
                notes=_notes(guard_input.get("notes"), "Requested source candidate failed tenant isolation validation."),
            )

        checked_source_refs.update(
            _checked_source_refs(source_kind=source_kind, source_candidate=source_candidate, session=session)
        )

    candidate: Service1TenantIsolationGuardCandidateV1 = {
        "guard_kind": GUARD_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "checked_source_candidate_kinds": list(requested_source_candidate_kinds),
        "checked_source_refs": dict(checked_source_refs),
        "tenant_isolation_passed": True,
        "cross_tenant_access_detected": False,
        "cross_case_access_detected": False,
        "cross_session_access_detected": False,
        "correction_applied": False,
        "auth_authorized": False,
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
        status="TENANT_ISOLATION_GUARD_CANDIDATE_READY",
        tenant_isolation_guard_candidate=candidate,
        notes=_notes(guard_input.get("notes"), "Tenant isolation guard candidate created without correction, persistence, or runtime authority."),
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


def _clean_requested_source_candidate_kinds(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    clean: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if not stripped or stripped in seen:
            continue
        clean.append(stripped)
        seen.add(stripped)
    return clean


def _select_source_candidate(
    *,
    guard_input: Service1TenantIsolationGuardInputV1,
    source_kind: str,
    session: dict[str, object],
) -> dict[str, object] | None:
    if source_kind == SESSION_KIND:
        return dict(session)
    payload_key = PAYLOAD_KEY_BY_SOURCE_KIND.get(source_kind)
    if payload_key is None:
        return None
    candidate = guard_input.get(payload_key)
    if not isinstance(candidate, dict) or not candidate:
        return None
    return dict(candidate)


def _validate_source_candidate(
    *,
    source_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> tuple[TenantIsolationGuardStatusV1, str] | None:
    if source_candidate.get(KIND_FIELD_BY_SOURCE_KIND[source_kind]) != source_kind:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_kind_mismatch")
    if source_candidate.get("service_name") != SERVICE_NAME:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_service_name_must_be_service_1")

    source_owner_ref = _clean_required_ref(source_candidate.get("owner_ref"))
    if source_owner_ref is None:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_owner_ref_required")
    if source_owner_ref != str(session["owner_ref"]).strip():
        return ("BLOCKED_CROSS_TENANT_CONTEXT", "source_owner_ref_must_match_session")

    source_case_ref = _clean_required_ref(source_candidate.get("case_ref"))
    if source_case_ref is None:
        return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_case_ref_required")
    if source_case_ref != str(session["case_ref"]).strip():
        return ("BLOCKED_CROSS_CASE_CONTEXT", "source_case_ref_must_match_session")

    source_session_ref = _candidate_source_session_ref(source_kind=source_kind, source_candidate=source_candidate)
    if source_session_ref is not None and source_session_ref != _source_session_ref(session):
        return ("BLOCKED_CROSS_SESSION_CONTEXT", "source_session_ref_must_match_session_anchor")

    generic_forbidden_reason = _generic_forbidden_reason(source_candidate)
    if generic_forbidden_reason is not None:
        return ("BLOCKED_UNSAFE_FLAGS", generic_forbidden_reason)

    source_flag_reason = _source_flag_reason(source_kind=source_kind, source_candidate=source_candidate)
    if source_flag_reason is not None:
        return ("BLOCKED_UNSAFE_FLAGS", source_flag_reason)

    if source_kind == AUDIT_KIND:
        audit_event_candidate = source_candidate.get("audit_event_candidate")
        if not isinstance(audit_event_candidate, dict) or not audit_event_candidate:
            return ("BLOCKED_INVALID_SOURCE_CANDIDATE", "source_candidate_kind_mismatch")
        generic_nested_reason = _generic_forbidden_reason(audit_event_candidate)
        if generic_nested_reason is not None:
            return ("BLOCKED_UNSAFE_FLAGS", generic_nested_reason)
    return None


def _candidate_source_session_ref(*, source_kind: str, source_candidate: dict[str, object]) -> str | None:
    if source_kind == SESSION_KIND:
        return _optional_ref(source_candidate, ("session_ref", "case_ref"))
    if source_kind == AUDIT_KIND:
        return _optional_ref(source_candidate, ("source_session_ref",))
    return _optional_ref(source_candidate, ("source_session_ref", "case_ref"))


def _generic_forbidden_reason(candidate: dict[str, object]) -> str | None:
    for flag_name, reason in GENERIC_FORBIDDEN_FLAG_REASON_BY_NAME.items():
        if flag_name in candidate and candidate.get(flag_name) is not False:
            return reason
    return None


def _source_flag_reason(*, source_kind: str, source_candidate: dict[str, object]) -> str | None:
    for flag_name, reason in SOURCE_FLAG_REASON_BY_KIND[source_kind].items():
        if flag_name in source_candidate and source_candidate.get(flag_name) is not False:
            return reason
    return None


def _checked_source_refs(
    *,
    source_kind: str,
    source_candidate: dict[str, object],
    session: dict[str, object],
) -> dict[str, str]:
    prefix = SOURCE_PREFIX_BY_KIND[source_kind]
    refs: dict[str, str] = {}

    if source_kind == SESSION_KIND:
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("service_1_state_refs"))))
        session_ref = _optional_ref(source_candidate, ("session_ref", "case_ref"))
        if session_ref is not None:
            refs[f"{prefix}.session_ref"] = session_ref
        return refs

    if source_kind == FILE_INTAKE_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("file_ref", "evidence_ref_candidate", "source_session_ref"))))
        return refs

    if source_kind == JOB_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("source_file_intake_ref", "source_session_ref"))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("autonomous_chain_candidate_refs"))))
        return refs

    if source_kind == AUDIT_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("audit_log_ref_candidate", "source_session_ref"))))
        audit_event_candidate = source_candidate.get("audit_event_candidate")
        if isinstance(audit_event_candidate, dict):
            refs.update(
                _prefix_map(
                    f"{prefix}.audit_event",
                    _refs_from_keys(
                        audit_event_candidate,
                        ("audit_event_ref_candidate", "source_slice_ref", "audit_log_ref_candidate", "source_session_ref"),
                    ),
                )
            )
        return refs

    if source_kind == BRIDGE_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("owner_message_ref_candidate", "owner_delivery_packet_ref", "saas_job_orchestration_ref", "source_session_ref"))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("service_1_state_refs"))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("generated_folder_refs"))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("safe_context_refs_for_future_llm"))))
        return refs

    if source_kind == GUARDED_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("source_bridge_ref_candidate", "source_owner_message_ref_candidate", "source_session_ref"))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("cited_safe_context_refs"))))
        return refs

    if source_kind == ROUTE_KIND:
        refs.update(_prefix_map(prefix, _refs_from_keys(source_candidate, ("source_session_ref",))))
        refs.update(_prefix_map(prefix, _clean_refs_map(source_candidate.get("cited_safe_context_refs"))))
        return refs

    refs[f"{prefix}.source_session_ref"] = _source_session_ref(session)
    return refs


def _prefix_map(prefix: str, values: dict[str, str]) -> dict[str, str]:
    return {f"{prefix}.{key}": value for key, value in values.items()}


def _refs_from_keys(source_candidate: dict[str, object], keys: tuple[str, ...]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for key in keys:
        value = source_candidate.get(key)
        if isinstance(value, str) and value.strip():
            refs[key] = value.strip()
    return refs


def _clean_refs_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(item, str) or not item.strip():
            continue
        clean[key.strip()] = item.strip()
    return clean


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


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: TenantIsolationGuardStatusV1,
    tenant_isolation_guard_candidate: Service1TenantIsolationGuardCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1TenantIsolationGuardResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "tenant_isolation_guard_candidate": tenant_isolation_guard_candidate,
        "blocked_reason": blocked_reason,
        "auth_authorized": False,
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
    "GUARD_KIND",
    "SESSION_KIND",
    "FILE_INTAKE_KIND",
    "JOB_KIND",
    "AUDIT_KIND",
    "BRIDGE_KIND",
    "GUARDED_KIND",
    "ROUTE_KIND",
    "ALLOWED_SOURCE_CANDIDATE_KINDS",
    "Service1TenantIsolationGuardInputV1",
    "Service1TenantIsolationGuardCandidateV1",
    "Service1TenantIsolationGuardResultV1",
    "build_service_1_tenant_isolation_guard_v1",
]
