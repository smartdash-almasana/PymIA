from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_REAL_AUTH_BOUNDARY_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
BOUNDARY_KIND: Final[str] = "REAL_AUTH_BOUNDARY_CANDIDATE"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
TENANT_ISOLATION_GUARD_KIND: Final[str] = "TENANT_ISOLATION_GUARD_CANDIDATE"

CREATE_CASE_SESSION: Final[str] = "CREATE_CASE_SESSION"
SUBMIT_CASE_PAYLOAD: Final[str] = "SUBMIT_CASE_PAYLOAD"
REQUEST_CASE_STATUS: Final[str] = "REQUEST_CASE_STATUS"
REQUEST_RUNTIME_EXECUTION: Final[str] = "REQUEST_RUNTIME_EXECUTION"

ALLOWED_OPERATION_KINDS: Final[tuple[str, ...]] = (
    CREATE_CASE_SESSION,
    SUBMIT_CASE_PAYLOAD,
    REQUEST_CASE_STATUS,
    REQUEST_RUNTIME_EXECUTION,
)

SESSION_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "runtime_authorized": "session_runtime_authorized_must_be_false",
    "job_authorized": "session_job_authorized_must_be_false",
    "file_upload_authorized": "session_file_upload_authorized_must_be_false",
    "api_exposed": "session_api_exposed_must_be_false",
}

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

AuthBoundaryStatusV1 = Literal[
    "AUTH_BOUNDARY_CANDIDATE_READY",
    "BLOCKED_MISSING_SUBJECT",
    "BLOCKED_MISSING_TENANT_CLAIM",
    "BLOCKED_MISSING_OWNER_CLAIM",
    "BLOCKED_TENANT_MISMATCH",
    "BLOCKED_OWNER_CASE_MISMATCH",
    "BLOCKED_OPERATION_NOT_ALLOWED",
    "BLOCKED_SESSION_NOT_ALLOWED",
    "UNKNOWN",
]


class Service1AuthBoundaryAccessCandidateV1(TypedDict):
    candidate_kind: str
    tenant_ref: str
    owner_ref: str
    case_ref: str | None
    session_ref: str | None
    access_granted: Literal[False]


class Service1AuthBoundaryAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["REAL_AUTH_BOUNDARY_CANDIDATE"]
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


class Service1AuthBoundaryInputV1(TypedDict):
    auth_subject_ref: str
    external_identity_ref: str
    tenant_claim_ref: str
    owner_claim_ref: str
    requested_operation_kind: str
    case_ref: str | None
    session_ref: str | None
    client_channel: str
    tenant_isolation_candidate: dict[str, object] | None
    case_session_candidate: dict[str, object] | None
    notes: list[str]


class Service1AuthBoundaryCandidateV1(TypedDict):
    boundary_kind: Literal["REAL_AUTH_BOUNDARY_CANDIDATE"]
    auth_subject_ref: str
    external_identity_ref: str
    tenant_ref: str
    owner_ref: str
    service_name: Literal["SERVICE_1"]
    authorized_operation_kind: str
    client_channel: str
    case_access_candidate: Service1AuthBoundaryAccessCandidateV1
    session_access_candidate: Service1AuthBoundaryAccessCandidateV1
    warnings: list[str]
    errors: list[str]
    audit_event_candidate: Service1AuthBoundaryAuditEventCandidateV1
    auth_authorized: Literal[False]
    api_exposed: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]


class Service1AuthBoundaryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: AuthBoundaryStatusV1
    auth_boundary_candidate: Service1AuthBoundaryCandidateV1 | None
    blocked_reason: str | None
    audit_event_candidate: Service1AuthBoundaryAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    auth_authorized: Literal[False]
    api_exposed: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    notes: list[str]


def build_service_1_real_auth_boundary_contract_v1(
    boundary_input: Service1AuthBoundaryInputV1,
) -> Service1AuthBoundaryResultV1:
    """Map future external identity inputs into safe PymIA refs without real auth."""
    auth_subject_ref = _clean_required_ref(boundary_input.get("auth_subject_ref"))
    if auth_subject_ref is None:
        return _result(
            status="BLOCKED_MISSING_SUBJECT",
            blocked_reason="auth_subject_ref_required",
            errors=["auth_subject_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Real auth boundary requires auth_subject_ref."),
        )

    tenant_claim_ref = _clean_required_ref(boundary_input.get("tenant_claim_ref"))
    if tenant_claim_ref is None:
        return _result(
            status="BLOCKED_MISSING_TENANT_CLAIM",
            blocked_reason="tenant_claim_ref_required",
            errors=["tenant_claim_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Real auth boundary requires tenant_claim_ref."),
        )

    owner_claim_ref = _clean_required_ref(boundary_input.get("owner_claim_ref"))
    if owner_claim_ref is None:
        return _result(
            status="BLOCKED_MISSING_OWNER_CLAIM",
            blocked_reason="owner_claim_ref_required",
            errors=["owner_claim_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Real auth boundary requires owner_claim_ref."),
        )

    requested_operation_kind = _clean_required_ref(boundary_input.get("requested_operation_kind"))
    if requested_operation_kind is None:
        return _result(
            status="BLOCKED_OPERATION_NOT_ALLOWED",
            blocked_reason="requested_operation_kind_required",
            errors=["requested_operation_kind_required"],
            notes=_notes(boundary_input.get("notes"), "Real auth boundary requires requested_operation_kind."),
        )
    if requested_operation_kind not in ALLOWED_OPERATION_KINDS:
        return _result(
            status="BLOCKED_OPERATION_NOT_ALLOWED",
            blocked_reason="requested_operation_kind_not_supported",
            errors=["requested_operation_kind_not_supported"],
            notes=_notes(boundary_input.get("notes"), "Requested operation is not supported by this auth boundary."),
        )
    if requested_operation_kind == REQUEST_RUNTIME_EXECUTION:
        return _result(
            status="BLOCKED_OPERATION_NOT_ALLOWED",
            blocked_reason="runtime_operation_not_allowed_at_auth_boundary",
            errors=["runtime_operation_not_allowed_at_auth_boundary"],
            notes=_notes(boundary_input.get("notes"), "Auth boundary cannot authorize runtime execution directly."),
        )

    external_identity_ref = _clean_required_ref(boundary_input.get("external_identity_ref"))
    if external_identity_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="external_identity_ref_required",
            errors=["external_identity_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Missing external_identity_ref prevents safe identity classification."),
        )

    client_channel = _clean_required_ref(boundary_input.get("client_channel"))
    if client_channel is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="client_channel_required",
            errors=["client_channel_required"],
            notes=_notes(boundary_input.get("notes"), "Client channel is missing, so auth boundary must fail closed."),
        )

    case_ref = _clean_optional_ref(boundary_input.get("case_ref"))
    session_ref = _clean_optional_ref(boundary_input.get("session_ref"))

    case_session_candidate = boundary_input.get("case_session_candidate")
    session_candidate: dict[str, object] | None = None
    if case_session_candidate is not None:
        if not isinstance(case_session_candidate, dict) or not case_session_candidate:
            return _result(
                status="BLOCKED_SESSION_NOT_ALLOWED",
                blocked_reason="case_session_candidate_invalid",
                errors=["case_session_candidate_invalid"],
                notes=_notes(boundary_input.get("notes"), "Provided case_session_candidate is invalid."),
            )
        session_candidate = dict(case_session_candidate)
        session_validation_reason = _validate_session_candidate(
            session_candidate=session_candidate,
            owner_ref=owner_claim_ref,
            case_ref=case_ref,
            session_ref=session_ref,
        )
        if session_validation_reason is not None:
            return _result(
                status="BLOCKED_SESSION_NOT_ALLOWED",
                blocked_reason=session_validation_reason,
                errors=[session_validation_reason],
                notes=_notes(boundary_input.get("notes"), "Provided case session candidate is not allowed for this auth boundary input."),
            )

    tenant_isolation_candidate = boundary_input.get("tenant_isolation_candidate")
    tenant_validation = _validate_tenant_isolation_candidate(
        tenant_isolation_candidate=tenant_isolation_candidate,
        owner_ref=owner_claim_ref,
        case_ref=case_ref,
        session_candidate=session_candidate,
        tenant_claim_ref=tenant_claim_ref,
    )
    if tenant_validation is not None:
        status = (
            "BLOCKED_OWNER_CASE_MISMATCH"
            if tenant_validation in {
                "tenant_isolation_owner_ref_must_match_owner_claim_ref",
                "tenant_isolation_case_ref_must_match_input",
            }
            else "BLOCKED_TENANT_MISMATCH"
        )
        return _result(
            status=status,
            blocked_reason=tenant_validation,
            errors=[tenant_validation],
            notes=_notes(boundary_input.get("notes"), "Tenant isolation evidence does not match the auth input claims."),
        )

    if requested_operation_kind in {SUBMIT_CASE_PAYLOAD, REQUEST_CASE_STATUS} and session_candidate is None:
        return _result(
            status="BLOCKED_SESSION_NOT_ALLOWED",
            blocked_reason="case_session_candidate_required_for_operation",
            errors=["case_session_candidate_required_for_operation"],
            notes=_notes(boundary_input.get("notes"), "This operation requires an allowed case session candidate."),
        )

    resolved_case_ref = case_ref
    resolved_session_ref = session_ref
    if session_candidate is not None:
        resolved_case_ref = resolved_case_ref or _clean_optional_ref(session_candidate.get("case_ref"))
        resolved_session_ref = resolved_session_ref or _case_session_ref(session_candidate)

    audit_case_ref = resolved_case_ref or "case_ref_pending"
    audit_session_ref = resolved_session_ref or audit_case_ref
    audit_event_candidate = _audit_event_candidate(
        auth_subject_ref=auth_subject_ref,
        tenant_ref=tenant_claim_ref,
        owner_ref=owner_claim_ref,
        case_ref=audit_case_ref,
        requested_operation_kind=requested_operation_kind,
        source_session_ref=audit_session_ref,
    )

    case_access_candidate: Service1AuthBoundaryAccessCandidateV1 = {
        "candidate_kind": "CASE_ACCESS_CANDIDATE",
        "tenant_ref": tenant_claim_ref,
        "owner_ref": owner_claim_ref,
        "case_ref": resolved_case_ref,
        "session_ref": None,
        "access_granted": False,
    }
    session_access_candidate: Service1AuthBoundaryAccessCandidateV1 = {
        "candidate_kind": "SESSION_ACCESS_CANDIDATE",
        "tenant_ref": tenant_claim_ref,
        "owner_ref": owner_claim_ref,
        "case_ref": resolved_case_ref,
        "session_ref": resolved_session_ref,
        "access_granted": False,
    }

    candidate: Service1AuthBoundaryCandidateV1 = {
        "boundary_kind": BOUNDARY_KIND,
        "auth_subject_ref": auth_subject_ref,
        "external_identity_ref": external_identity_ref,
        "tenant_ref": tenant_claim_ref,
        "owner_ref": owner_claim_ref,
        "service_name": SERVICE_NAME,
        "authorized_operation_kind": requested_operation_kind,
        "client_channel": client_channel,
        "case_access_candidate": case_access_candidate,
        "session_access_candidate": session_access_candidate,
        "warnings": [],
        "errors": [],
        "audit_event_candidate": audit_event_candidate,
        "auth_authorized": False,
        "api_exposed": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
    }

    return _result(
        status="AUTH_BOUNDARY_CANDIDATE_READY",
        auth_boundary_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        notes=_notes(boundary_input.get("notes"), "Auth boundary candidate created as pure identity mapping without real auth or runtime authority."),
    )


def _validate_session_candidate(
    *,
    session_candidate: dict[str, object],
    owner_ref: str,
    case_ref: str | None,
    session_ref: str | None,
) -> str | None:
    if session_candidate.get("session_kind") != SESSION_KIND:
        return "session_kind_must_be_saas_case_session_candidate"
    if session_candidate.get("service_name") != SERVICE_NAME:
        return "session_service_name_must_be_service_1"
    session_owner_ref = _clean_required_ref(session_candidate.get("owner_ref"))
    if session_owner_ref is None:
        return "session_owner_ref_required"
    if session_owner_ref != owner_ref:
        return "session_owner_ref_must_match_owner_claim_ref"
    session_case_ref = _clean_required_ref(session_candidate.get("case_ref"))
    if session_case_ref is None:
        return "session_case_ref_required"
    if case_ref is not None and session_case_ref != case_ref:
        return "session_case_ref_must_match_input"
    resolved_session_ref = _case_session_ref(session_candidate)
    if session_ref is not None and resolved_session_ref != session_ref:
        return "session_ref_must_match_case_session_candidate"
    for flag_name, reason in SESSION_FLAG_REASON_BY_NAME.items():
        if session_candidate.get(flag_name) is not False:
            return reason
    return None


def _validate_tenant_isolation_candidate(
    *,
    tenant_isolation_candidate: object,
    owner_ref: str,
    case_ref: str | None,
    session_candidate: dict[str, object] | None,
    tenant_claim_ref: str,
) -> str | None:
    if tenant_isolation_candidate is None:
        return None
    if not isinstance(tenant_isolation_candidate, dict) or not tenant_isolation_candidate:
        return "tenant_isolation_candidate_invalid"
    if tenant_isolation_candidate.get("guard_kind") != TENANT_ISOLATION_GUARD_KIND:
        return "tenant_isolation_candidate_kind_mismatch"
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
    candidate_owner_ref = _clean_required_ref(tenant_isolation_candidate.get("owner_ref"))
    if candidate_owner_ref is None or candidate_owner_ref != owner_ref:
        return "tenant_isolation_owner_ref_must_match_owner_claim_ref"
    candidate_case_ref = _clean_required_ref(tenant_isolation_candidate.get("case_ref"))
    if case_ref is not None and (candidate_case_ref is None or candidate_case_ref != case_ref):
        return "tenant_isolation_case_ref_must_match_input"
    if session_candidate is not None:
        source_session_ref = _clean_required_ref(tenant_isolation_candidate.get("source_session_ref"))
        if source_session_ref is None or source_session_ref != _case_session_ref(session_candidate):
            return "tenant_isolation_source_session_ref_must_match_session"
    checked_source_refs = tenant_isolation_candidate.get("checked_source_refs")
    if isinstance(checked_source_refs, dict):
        tenant_ref_values = {
            str(value).strip()
            for key, value in checked_source_refs.items()
            if isinstance(key, str)
            and "tenant_ref" in key
            and isinstance(value, str)
            and value.strip()
        }
        if tenant_ref_values and (len(tenant_ref_values) != 1 or tenant_claim_ref not in tenant_ref_values):
            return "tenant_claim_ref_must_match_tenant_isolation_refs"
    for flag_name, reason in TENANT_GUARD_FLAG_REASON_BY_NAME.items():
        if flag_name in tenant_isolation_candidate and tenant_isolation_candidate.get(flag_name) is not False:
            return reason
    return None


def _audit_event_candidate(
    *,
    auth_subject_ref: str,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    requested_operation_kind: str,
    source_session_ref: str,
) -> Service1AuthBoundaryAuditEventCandidateV1:
    source_slice_ref = f"auth_boundary_subject:{_safe_ref(auth_subject_ref)}"
    audit_log_ref_candidate = f"audit_log_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}"
    audit_event_ref_candidate = (
        f"audit_event_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:"
        f"auth_boundary:{_safe_ref(auth_subject_ref)}:{_safe_ref(requested_operation_kind)}"
    )
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "REAL_AUTH_BOUNDARY_CANDIDATE_RECORDED",
        "event_status": "AUTH_BOUNDARY_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "source_slice_kind": BOUNDARY_KIND,
        "source_slice_ref": source_slice_ref,
        "audit_log_ref_candidate": audit_log_ref_candidate,
        "audit_event_ref_candidate": audit_event_ref_candidate,
        "append_operation": "APPEND_EVENT",
        "event_summary": f"Auth boundary candidate prepared for {requested_operation_kind}.",
        "source_context_refs": {
            "auth_subject_ref": auth_subject_ref,
            "tenant_ref": tenant_ref,
            "owner_ref": owner_ref,
            "case_ref": case_ref,
            "source_session_ref": source_session_ref,
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


def _case_session_ref(session_candidate: dict[str, object]) -> str | None:
    for key in ("session_ref", "case_ref"):
        value = session_candidate.get(key)
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


def _clean_optional_ref(value: object) -> str | None:
    if value is None:
        return None
    return _clean_required_ref(value)


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: AuthBoundaryStatusV1,
    auth_boundary_candidate: Service1AuthBoundaryCandidateV1 | None = None,
    blocked_reason: str | None = None,
    audit_event_candidate: Service1AuthBoundaryAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1AuthBoundaryResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "auth_boundary_candidate": auth_boundary_candidate,
        "blocked_reason": blocked_reason,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "auth_authorized": False,
        "api_exposed": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BOUNDARY_KIND",
    "SESSION_KIND",
    "TENANT_ISOLATION_GUARD_KIND",
    "CREATE_CASE_SESSION",
    "SUBMIT_CASE_PAYLOAD",
    "REQUEST_CASE_STATUS",
    "REQUEST_RUNTIME_EXECUTION",
    "ALLOWED_OPERATION_KINDS",
    "Service1AuthBoundaryAccessCandidateV1",
    "Service1AuthBoundaryAuditEventCandidateV1",
    "Service1AuthBoundaryInputV1",
    "Service1AuthBoundaryCandidateV1",
    "Service1AuthBoundaryResultV1",
    "build_service_1_real_auth_boundary_contract_v1",
]
