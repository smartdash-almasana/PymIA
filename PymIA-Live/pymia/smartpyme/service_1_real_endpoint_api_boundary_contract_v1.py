from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
BOUNDARY_KIND: Final[str] = "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
TENANT_ISOLATION_GUARD_KIND: Final[str] = "TENANT_ISOLATION_GUARD_CANDIDATE"
COST_AND_RATE_LIMIT_GUARD_KIND: Final[str] = "COST_AND_RATE_LIMIT_GUARD_CANDIDATE"

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

BoundaryFlagNames: Final[tuple[str, ...]] = (
    "api_exposed",
    "runtime_authorized",
    "pipeline_authorized",
    "runner_authorized",
    "storage_write_authorized",
    "db_authorized",
    "llm_authorized",
    "mutation_authorized",
)

ApiBoundaryStatusV1 = Literal[
    "API_BOUNDARY_CANDIDATE_READY",
    "BLOCKED_MISSING_TENANT",
    "BLOCKED_MISSING_OWNER",
    "BLOCKED_INVALID_OPERATION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_TENANT_ISOLATION",
    "BLOCKED_COST_OR_RATE_LIMIT",
    "BLOCKED_UNAUTHORIZED_RUNTIME",
    "NEEDS_OWNER_INPUT",
    "NEEDS_EVIDENCE",
    "UNKNOWN",
]


class Service1ApiBoundaryInputV1(TypedDict):
    tenant_ref: str
    owner_ref: str
    case_ref: str | None
    case_creation_payload: dict[str, object] | None
    request_id: str
    operation_kind: str
    payload_ref: str | None
    payload: dict[str, object] | None
    idempotency_key: str
    client_channel: str
    saas_case_session_candidate: dict[str, object] | None
    tenant_isolation_candidate: dict[str, object] | None
    cost_rate_limit_candidate: dict[str, object] | None
    notes: list[str]


class Service1ApiBoundaryAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["REAL_ENDPOINT_API_BOUNDARY_CANDIDATE"]
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


class Service1ApiBoundaryCandidateV1(TypedDict):
    boundary_kind: Literal["REAL_ENDPOINT_API_BOUNDARY_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str | None
    service_name: Literal["SERVICE_1"]
    request_id: str
    idempotency_key: str
    client_channel: str
    accepted_operation_kind: str
    case_session_candidate_ref: str | None
    payload_ref: str | None
    payload_present: bool
    next_required_action: str
    runtime_authorization_required: Literal[False]
    warnings: list[str]
    errors: list[str]
    audit_event_candidate: Service1ApiBoundaryAuditEventCandidateV1 | None
    api_exposed: Literal[False]
    runtime_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    llm_authorized: Literal[False]
    mutation_authorized: Literal[False]


class Service1ApiBoundaryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: ApiBoundaryStatusV1
    api_boundary_candidate: Service1ApiBoundaryCandidateV1 | None
    blocked_reason: str | None
    next_required_action: str | None
    audit_event_candidate: Service1ApiBoundaryAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    api_exposed: Literal[False]
    runtime_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    llm_authorized: Literal[False]
    mutation_authorized: Literal[False]
    notes: list[str]


def build_service_1_real_endpoint_api_boundary_contract_v1(
    boundary_input: Service1ApiBoundaryInputV1,
) -> Service1ApiBoundaryResultV1:
    """Evaluate one future API operation as a pure deterministic boundary candidate."""
    tenant_ref = _clean_required_ref(boundary_input.get("tenant_ref"))
    if tenant_ref is None:
        return _result(
            status="BLOCKED_MISSING_TENANT",
            blocked_reason="tenant_ref_required",
            errors=["tenant_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Real endpoint API boundary requires tenant_ref."),
        )

    owner_ref = _clean_required_ref(boundary_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="BLOCKED_MISSING_OWNER",
            blocked_reason="owner_ref_required",
            errors=["owner_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Real endpoint API boundary requires owner_ref."),
        )

    operation_kind = _clean_required_ref(boundary_input.get("operation_kind"))
    if operation_kind is None:
        return _result(
            status="BLOCKED_INVALID_OPERATION",
            blocked_reason="operation_kind_required",
            errors=["operation_kind_required"],
            notes=_notes(boundary_input.get("notes"), "Real endpoint API boundary requires operation_kind."),
        )
    if operation_kind not in ALLOWED_OPERATION_KINDS:
        return _result(
            status="BLOCKED_INVALID_OPERATION",
            blocked_reason="operation_kind_not_supported",
            errors=["operation_kind_not_supported"],
            notes=_notes(boundary_input.get("notes"), "Requested operation_kind is not supported by this boundary."),
        )

    request_id = _clean_required_ref(boundary_input.get("request_id"))
    if request_id is None:
        return _result(
            status="BLOCKED_INVALID_OPERATION",
            blocked_reason="request_id_required",
            errors=["request_id_required"],
            notes=_notes(boundary_input.get("notes"), "Real endpoint API boundary requires request_id."),
        )

    idempotency_key = _clean_required_ref(boundary_input.get("idempotency_key"))
    if idempotency_key is None:
        return _result(
            status="BLOCKED_INVALID_OPERATION",
            blocked_reason="idempotency_key_required",
            errors=["idempotency_key_required"],
            notes=_notes(boundary_input.get("notes"), "Real endpoint API boundary requires idempotency_key."),
        )

    client_channel = _clean_required_ref(boundary_input.get("client_channel"))
    if client_channel is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="client_channel_required",
            errors=["client_channel_required"],
            notes=_notes(boundary_input.get("notes"), "Client channel is missing, so the boundary must fail closed."),
        )

    case_ref = _clean_optional_ref(boundary_input.get("case_ref"))
    case_creation_payload = _clean_payload(boundary_input.get("case_creation_payload"))
    payload = _clean_payload(boundary_input.get("payload"))
    payload_ref = _clean_optional_ref(boundary_input.get("payload_ref"))

    session = boundary_input.get("saas_case_session_candidate")
    session_required = operation_kind in {SUBMIT_CASE_PAYLOAD, REQUEST_CASE_STATUS, REQUEST_RUNTIME_EXECUTION}
    session_candidate: dict[str, object] | None = None
    if session is not None:
        if not isinstance(session, dict) or not session:
            return _result(
                status="BLOCKED_INVALID_SESSION",
                blocked_reason="saas_case_session_candidate_invalid",
                errors=["saas_case_session_candidate_invalid"],
                notes=_notes(boundary_input.get("notes"), "Provided SaaS case session candidate is invalid."),
            )
        session_candidate = dict(session)
        session_validation_reason = _validate_session_candidate(
            session_candidate=session_candidate,
            owner_ref=owner_ref,
            case_ref=case_ref,
        )
        if session_validation_reason is not None:
            return _result(
                status="BLOCKED_INVALID_SESSION",
                blocked_reason=session_validation_reason,
                errors=[session_validation_reason],
                notes=_notes(boundary_input.get("notes"), "Provided SaaS case session candidate failed boundary validation."),
            )
    elif session_required:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_required_for_operation",
            errors=["saas_case_session_candidate_required_for_operation"],
            notes=_notes(boundary_input.get("notes"), "This operation requires a SaaS case session candidate."),
        )

    if operation_kind == REQUEST_RUNTIME_EXECUTION:
        return _result(
            status="BLOCKED_UNAUTHORIZED_RUNTIME",
            blocked_reason="runtime_execution_not_authorized_by_endpoint_boundary",
            next_required_action="STOP_RUNTIME_BOUNDARY",
            errors=["runtime_execution_not_authorized_by_endpoint_boundary"],
            notes=_notes(boundary_input.get("notes"), "Endpoint boundary cannot authorize runtime execution directly."),
        )

    if operation_kind == CREATE_CASE_SESSION:
        if case_creation_payload is None:
            return _result(
                status="NEEDS_OWNER_INPUT",
                blocked_reason="case_creation_payload_required_for_create_case_session",
                next_required_action="COLLECT_CASE_CREATION_PAYLOAD",
                warnings=["case_creation_payload_required_for_create_case_session"],
                notes=_notes(boundary_input.get("notes"), "Creating a case session needs explicit owner input payload."),
            )
        inferred_case_ref = case_ref or _clean_optional_ref(case_creation_payload.get("case_ref"))
        audit_event_candidate = _audit_event_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=inferred_case_ref or "case_ref_pending",
            request_id=request_id,
            operation_kind=operation_kind,
            source_session_ref=inferred_case_ref or "case_ref_pending",
            payload_ref=payload_ref,
        )
        candidate = _ready_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=inferred_case_ref,
            request_id=request_id,
            idempotency_key=idempotency_key,
            client_channel=client_channel,
            accepted_operation_kind=operation_kind,
            case_session_candidate_ref=None,
            payload_ref=payload_ref,
            payload_present=True,
            next_required_action="BUILD_CASE_SESSION_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
        )
        return _result(
            status="API_BOUNDARY_CANDIDATE_READY",
            api_boundary_candidate=candidate,
            next_required_action="BUILD_CASE_SESSION_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
            notes=_notes(boundary_input.get("notes"), "Endpoint API boundary candidate is ready for case-session candidate preparation."),
        )

    tenant_isolation_candidate = boundary_input.get("tenant_isolation_candidate")
    tenant_validation = _validate_tenant_isolation_candidate(
        tenant_isolation_candidate=tenant_isolation_candidate,
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_candidate=session_candidate,
    )
    if tenant_validation is not None:
        return _result(
            status="BLOCKED_TENANT_ISOLATION",
            blocked_reason=tenant_validation,
            errors=[tenant_validation],
            notes=_notes(boundary_input.get("notes"), "Tenant isolation candidate blocked the endpoint boundary."),
        )

    cost_rate_limit_candidate = boundary_input.get("cost_rate_limit_candidate")
    cost_validation = _validate_cost_rate_limit_candidate(
        cost_rate_limit_candidate=cost_rate_limit_candidate,
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_candidate=session_candidate,
    )
    if cost_validation is not None:
        return _result(
            status="BLOCKED_COST_OR_RATE_LIMIT",
            blocked_reason=cost_validation,
            errors=[cost_validation],
            notes=_notes(boundary_input.get("notes"), "Cost/rate limit candidate blocked the endpoint boundary."),
        )

    if operation_kind == SUBMIT_CASE_PAYLOAD:
        if payload_ref is None and payload is None:
            return _result(
                status="NEEDS_EVIDENCE",
                blocked_reason="payload_or_payload_ref_required_for_submit_case_payload",
                next_required_action="COLLECT_PAYLOAD_OR_EVIDENCE_REF",
                warnings=["payload_or_payload_ref_required_for_submit_case_payload"],
                notes=_notes(boundary_input.get("notes"), "Submitting case payload needs evidence or payload content."),
            )
        assert session_candidate is not None
        audit_event_candidate = _audit_event_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=str(session_candidate["case_ref"]).strip(),
            request_id=request_id,
            operation_kind=operation_kind,
            source_session_ref=_source_session_ref(session_candidate),
            payload_ref=payload_ref,
        )
        candidate = _ready_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=str(session_candidate["case_ref"]).strip(),
            request_id=request_id,
            idempotency_key=idempotency_key,
            client_channel=client_channel,
            accepted_operation_kind=operation_kind,
            case_session_candidate_ref=_case_session_candidate_ref(session_candidate),
            payload_ref=payload_ref,
            payload_present=payload is not None,
            next_required_action="PREPARE_CASE_PAYLOAD_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
        )
        return _result(
            status="API_BOUNDARY_CANDIDATE_READY",
            api_boundary_candidate=candidate,
            next_required_action="PREPARE_CASE_PAYLOAD_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
            notes=_notes(boundary_input.get("notes"), "Endpoint API boundary candidate is ready for payload submission preparation."),
        )

    if operation_kind == REQUEST_CASE_STATUS:
        assert session_candidate is not None
        audit_event_candidate = _audit_event_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=str(session_candidate["case_ref"]).strip(),
            request_id=request_id,
            operation_kind=operation_kind,
            source_session_ref=_source_session_ref(session_candidate),
            payload_ref=payload_ref,
        )
        candidate = _ready_candidate(
            tenant_ref=tenant_ref,
            owner_ref=owner_ref,
            case_ref=str(session_candidate["case_ref"]).strip(),
            request_id=request_id,
            idempotency_key=idempotency_key,
            client_channel=client_channel,
            accepted_operation_kind=operation_kind,
            case_session_candidate_ref=_case_session_candidate_ref(session_candidate),
            payload_ref=payload_ref,
            payload_present=payload is not None,
            next_required_action="PREPARE_CASE_STATUS_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
        )
        return _result(
            status="API_BOUNDARY_CANDIDATE_READY",
            api_boundary_candidate=candidate,
            next_required_action="PREPARE_CASE_STATUS_CANDIDATE",
            audit_event_candidate=audit_event_candidate,
            notes=_notes(boundary_input.get("notes"), "Endpoint API boundary candidate is ready for case status preparation."),
        )

    return _result(
        status="UNKNOWN",
        blocked_reason="operation_not_classified_by_boundary",
        errors=["operation_not_classified_by_boundary"],
        notes=_notes(boundary_input.get("notes"), "Boundary could not classify the operation safely and failed closed."),
    )


def _validate_session_candidate(
    *,
    session_candidate: dict[str, object],
    owner_ref: str,
    case_ref: str | None,
) -> str | None:
    if session_candidate.get("session_kind") != SESSION_KIND:
        return "session_kind_must_be_saas_case_session_candidate"
    if session_candidate.get("service_name") != SERVICE_NAME:
        return "session_service_name_must_be_service_1"
    session_owner_ref = _clean_required_ref(session_candidate.get("owner_ref"))
    if session_owner_ref is None:
        return "session_owner_ref_required"
    if session_owner_ref != owner_ref:
        return "session_owner_ref_must_match_input"
    session_case_ref = _clean_required_ref(session_candidate.get("case_ref"))
    if session_case_ref is None:
        return "session_case_ref_required"
    if case_ref is not None and session_case_ref != case_ref:
        return "session_case_ref_must_match_input"
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
) -> str | None:
    if not isinstance(tenant_isolation_candidate, dict) or not tenant_isolation_candidate:
        return "tenant_isolation_candidate_required"
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
        return "tenant_isolation_owner_ref_must_match_input"
    candidate_case_ref = _clean_required_ref(tenant_isolation_candidate.get("case_ref"))
    if case_ref is not None and (candidate_case_ref is None or candidate_case_ref != case_ref):
        return "tenant_isolation_case_ref_must_match_input"
    if session_candidate is not None:
        source_session_ref = _clean_required_ref(tenant_isolation_candidate.get("source_session_ref"))
        if source_session_ref is None or source_session_ref != _source_session_ref(session_candidate):
            return "tenant_isolation_source_session_ref_must_match_session"
    for flag_name, reason in TENANT_GUARD_FLAG_REASON_BY_NAME.items():
        if flag_name in tenant_isolation_candidate and tenant_isolation_candidate.get(flag_name) is not False:
            return reason
    return None


def _validate_cost_rate_limit_candidate(
    *,
    cost_rate_limit_candidate: object,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str | None,
    session_candidate: dict[str, object] | None,
) -> str | None:
    if not isinstance(cost_rate_limit_candidate, dict) or not cost_rate_limit_candidate:
        return "cost_and_rate_limit_guard_candidate_required"
    if cost_rate_limit_candidate.get("guard_kind") != COST_AND_RATE_LIMIT_GUARD_KIND:
        return "cost_and_rate_limit_guard_candidate_kind_mismatch"
    if cost_rate_limit_candidate.get("service_name") != SERVICE_NAME:
        return "cost_and_rate_limit_service_name_must_be_service_1"
    if cost_rate_limit_candidate.get("cost_limit_passed") is not True:
        return "cost_limit_must_be_passed"
    if cost_rate_limit_candidate.get("rate_limit_passed") is not True:
        return "rate_limit_must_be_passed"
    if cost_rate_limit_candidate.get("budget_limit_passed") is not True:
        return "budget_limit_must_be_passed"
    candidate_tenant_ref = _clean_required_ref(cost_rate_limit_candidate.get("tenant_ref"))
    if candidate_tenant_ref is None or candidate_tenant_ref != tenant_ref:
        return "cost_and_rate_limit_tenant_ref_must_match_input"
    candidate_owner_ref = _clean_required_ref(cost_rate_limit_candidate.get("owner_ref"))
    if candidate_owner_ref is None or candidate_owner_ref != owner_ref:
        return "cost_and_rate_limit_owner_ref_must_match_input"
    candidate_case_ref = _clean_required_ref(cost_rate_limit_candidate.get("case_ref"))
    if case_ref is not None and (candidate_case_ref is None or candidate_case_ref != case_ref):
        return "cost_and_rate_limit_case_ref_must_match_input"
    if session_candidate is not None:
        source_session_ref = _clean_required_ref(cost_rate_limit_candidate.get("source_session_ref"))
        if source_session_ref is None or source_session_ref != _source_session_ref(session_candidate):
            return "cost_and_rate_limit_source_session_ref_must_match_session"
    for flag_name, reason in COST_GUARD_FLAG_REASON_BY_NAME.items():
        if flag_name in cost_rate_limit_candidate and cost_rate_limit_candidate.get(flag_name) is not False:
            return reason
    return None


def _ready_candidate(
    *,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str | None,
    request_id: str,
    idempotency_key: str,
    client_channel: str,
    accepted_operation_kind: str,
    case_session_candidate_ref: str | None,
    payload_ref: str | None,
    payload_present: bool,
    next_required_action: str,
    audit_event_candidate: Service1ApiBoundaryAuditEventCandidateV1,
) -> Service1ApiBoundaryCandidateV1:
    return {
        "boundary_kind": BOUNDARY_KIND,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "request_id": request_id,
        "idempotency_key": idempotency_key,
        "client_channel": client_channel,
        "accepted_operation_kind": accepted_operation_kind,
        "case_session_candidate_ref": case_session_candidate_ref,
        "payload_ref": payload_ref,
        "payload_present": payload_present,
        "next_required_action": next_required_action,
        "runtime_authorization_required": False,
        "warnings": [],
        "errors": [],
        "audit_event_candidate": audit_event_candidate,
        "api_exposed": False,
        "runtime_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "llm_authorized": False,
        "mutation_authorized": False,
    }


def _audit_event_candidate(
    *,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    request_id: str,
    operation_kind: str,
    source_session_ref: str,
    payload_ref: str | None,
) -> Service1ApiBoundaryAuditEventCandidateV1:
    source_slice_ref = f"api_boundary_request:{_safe_ref(request_id)}"
    audit_log_ref_candidate = f"audit_log_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}"
    audit_event_ref_candidate = (
        f"audit_event_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:"
        f"endpoint_api_boundary:{_safe_ref(request_id)}:{_safe_ref(operation_kind)}"
    )
    source_context_refs = {
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "request_id": request_id,
        "source_session_ref": source_session_ref,
    }
    if payload_ref is not None:
        source_context_refs["payload_ref"] = payload_ref
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE_RECORDED",
        "event_status": "API_BOUNDARY_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "source_slice_kind": BOUNDARY_KIND,
        "source_slice_ref": source_slice_ref,
        "audit_log_ref_candidate": audit_log_ref_candidate,
        "audit_event_ref_candidate": audit_event_ref_candidate,
        "append_operation": "APPEND_EVENT",
        "event_summary": f"Endpoint boundary candidate prepared for {operation_kind}.",
        "source_context_refs": source_context_refs,
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


def _case_session_candidate_ref(session_candidate: dict[str, object]) -> str | None:
    for key in ("session_ref", "case_ref"):
        value = session_candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _source_session_ref(session_candidate: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session_candidate.get(key)
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


def _clean_optional_ref(value: object) -> str | None:
    if value is None:
        return None
    return _clean_required_ref(value)


def _clean_payload(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or not value:
        return None
    return dict(value)


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: ApiBoundaryStatusV1,
    api_boundary_candidate: Service1ApiBoundaryCandidateV1 | None = None,
    blocked_reason: str | None = None,
    next_required_action: str | None = None,
    audit_event_candidate: Service1ApiBoundaryAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1ApiBoundaryResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "api_boundary_candidate": api_boundary_candidate,
        "blocked_reason": blocked_reason,
        "next_required_action": next_required_action,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "api_exposed": False,
        "runtime_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "llm_authorized": False,
        "mutation_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BOUNDARY_KIND",
    "SESSION_KIND",
    "TENANT_ISOLATION_GUARD_KIND",
    "COST_AND_RATE_LIMIT_GUARD_KIND",
    "CREATE_CASE_SESSION",
    "SUBMIT_CASE_PAYLOAD",
    "REQUEST_CASE_STATUS",
    "REQUEST_RUNTIME_EXECUTION",
    "ALLOWED_OPERATION_KINDS",
    "Service1ApiBoundaryInputV1",
    "Service1ApiBoundaryAuditEventCandidateV1",
    "Service1ApiBoundaryCandidateV1",
    "Service1ApiBoundaryResultV1",
    "build_service_1_real_endpoint_api_boundary_contract_v1",
]
