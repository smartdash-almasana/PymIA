from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_REAL_STORAGE_UPLOAD_BOUNDARY_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
BOUNDARY_KIND: Final[str] = "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE"
TENANT_ISOLATION_GUARD_KIND: Final[str] = "TENANT_ISOLATION_GUARD_CANDIDATE"
COST_AND_RATE_LIMIT_GUARD_KIND: Final[str] = "COST_AND_RATE_LIMIT_GUARD_CANDIDATE"
FILE_INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"

ALLOWED_FILE_KINDS: Final[tuple[str, ...]] = (
    "XLSX",
    "CSV",
    "TXT",
)

ALLOWED_CONTENT_TYPES_BY_FILE_KIND: Final[dict[str, tuple[str, ...]]] = {
    "XLSX": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",),
    "CSV": ("text/csv",),
    "TXT": ("text/plain",),
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

FILE_INTAKE_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "task_spec_candidate_allowed": "file_intake_task_spec_candidate_allowed_must_be_false",
    "upload_authorized": "file_intake_upload_authorized_must_be_false",
    "file_read_authorized": "file_intake_file_read_authorized_must_be_false",
    "parser_authorized": "file_intake_parser_authorized_must_be_false",
    "job_authorized": "file_intake_job_authorized_must_be_false",
    "runtime_authorized": "file_intake_runtime_authorized_must_be_false",
    "api_exposed": "file_intake_api_exposed_must_be_false",
}

StorageUploadBoundaryStatusV1 = Literal[
    "STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY",
    "BLOCKED_MISSING_TENANT",
    "BLOCKED_MISSING_OWNER",
    "BLOCKED_MISSING_CASE",
    "BLOCKED_INVALID_FILE_NAME",
    "BLOCKED_INVALID_FILE_KIND",
    "BLOCKED_INVALID_FILE_SIZE",
    "BLOCKED_MISSING_STORAGE_REF",
    "BLOCKED_TENANT_ISOLATION",
    "BLOCKED_COST_OR_RATE_LIMIT",
    "NEEDS_FILE_INTAKE",
    "NEEDS_OWNER_CONFIRMATION",
    "UNKNOWN",
]


class Service1StorageUploadBoundaryInputV1(TypedDict):
    tenant_ref: str
    owner_ref: str
    case_ref: str
    upload_request_ref: str
    file_name: str
    file_kind: str
    file_size_bytes: int
    content_type: str
    storage_object_ref: str | None
    checksum: str | None
    client_channel: str
    tenant_isolation_candidate: dict[str, object] | None
    cost_rate_limit_candidate: dict[str, object] | None
    file_intake_candidate: dict[str, object] | None
    notes: list[str]


class Service1StorageUploadBoundaryAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE"]
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


class Service1StorageUploadBoundaryCandidateV1(TypedDict):
    boundary_kind: Literal["REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    upload_request_ref: str
    client_channel: str
    file_name: str
    file_kind: str
    file_size_bytes: int
    content_type: str
    storage_object_ref: str
    checksum: str
    safe_file_ref: str
    file_intake_candidate_ref: str
    evidence_ref_candidate: str
    processing_job_candidate_required: Literal[False]
    warnings: list[str]
    errors: list[str]
    audit_event_candidate: Service1StorageUploadBoundaryAuditEventCandidateV1
    storage_write_authorized: Literal[False]
    file_processing_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    evidence_authorized: Literal[False]
    mutation_authorized: Literal[False]
    db_authorized: Literal[False]
    api_exposed: Literal[False]
    llm_authorized: Literal[False]


class Service1StorageUploadBoundaryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: StorageUploadBoundaryStatusV1
    storage_upload_boundary_candidate: Service1StorageUploadBoundaryCandidateV1 | None
    blocked_reason: str | None
    audit_event_candidate: Service1StorageUploadBoundaryAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    storage_write_authorized: Literal[False]
    file_processing_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    evidence_authorized: Literal[False]
    mutation_authorized: Literal[False]
    db_authorized: Literal[False]
    api_exposed: Literal[False]
    llm_authorized: Literal[False]
    notes: list[str]


def build_service_1_real_storage_upload_boundary_contract_v1(
    boundary_input: Service1StorageUploadBoundaryInputV1,
) -> Service1StorageUploadBoundaryResultV1:
    """Evaluate one future storage upload reference as pure governed data."""
    tenant_ref = _clean_required_ref(boundary_input.get("tenant_ref"))
    if tenant_ref is None:
        return _result(
            status="BLOCKED_MISSING_TENANT",
            blocked_reason="tenant_ref_required",
            errors=["tenant_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Storage upload boundary requires tenant_ref."),
        )

    owner_ref = _clean_required_ref(boundary_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="BLOCKED_MISSING_OWNER",
            blocked_reason="owner_ref_required",
            errors=["owner_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Storage upload boundary requires owner_ref."),
        )

    case_ref = _clean_required_ref(boundary_input.get("case_ref"))
    if case_ref is None:
        return _result(
            status="BLOCKED_MISSING_CASE",
            blocked_reason="case_ref_required",
            errors=["case_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Storage upload boundary requires case_ref."),
        )

    upload_request_ref = _clean_required_ref(boundary_input.get("upload_request_ref"))
    if upload_request_ref is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="upload_request_ref_required",
            errors=["upload_request_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Missing upload_request_ref forces fail-closed behavior."),
        )

    file_name = _clean_required_ref(boundary_input.get("file_name"))
    if file_name is None or any(char in file_name for char in ("/", "\\")):
        return _result(
            status="BLOCKED_INVALID_FILE_NAME",
            blocked_reason="file_name_required_or_invalid",
            errors=["file_name_required_or_invalid"],
            notes=_notes(boundary_input.get("notes"), "file_name must be present and path-free."),
        )

    file_kind = _clean_required_ref(boundary_input.get("file_kind"))
    if file_kind is None:
        return _result(
            status="BLOCKED_INVALID_FILE_KIND",
            blocked_reason="file_kind_required",
            errors=["file_kind_required"],
            notes=_notes(boundary_input.get("notes"), "file_kind is required."),
        )
    normalized_file_kind = file_kind.upper()
    if normalized_file_kind not in ALLOWED_FILE_KINDS:
        return _result(
            status="BLOCKED_INVALID_FILE_KIND",
            blocked_reason="file_kind_not_supported",
            errors=["file_kind_not_supported"],
            notes=_notes(boundary_input.get("notes"), "file_kind is outside the governed intake contract."),
        )

    content_type = _clean_required_ref(boundary_input.get("content_type"))
    if content_type is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="content_type_required",
            errors=["content_type_required"],
            notes=_notes(boundary_input.get("notes"), "Missing content_type forces fail-closed behavior."),
        )
    if content_type not in ALLOWED_CONTENT_TYPES_BY_FILE_KIND[normalized_file_kind]:
        return _result(
            status="BLOCKED_INVALID_FILE_KIND",
            blocked_reason="content_type_not_supported_for_file_kind",
            errors=["content_type_not_supported_for_file_kind"],
            notes=_notes(boundary_input.get("notes"), "content_type does not match the declared file_kind."),
        )

    file_size_bytes = boundary_input.get("file_size_bytes")
    if not isinstance(file_size_bytes, int) or file_size_bytes <= 0:
        return _result(
            status="BLOCKED_INVALID_FILE_SIZE",
            blocked_reason="file_size_bytes_must_be_positive_int",
            errors=["file_size_bytes_must_be_positive_int"],
            notes=_notes(boundary_input.get("notes"), "file_size_bytes must be a positive integer."),
        )

    storage_object_ref = _clean_required_ref(boundary_input.get("storage_object_ref"))
    if storage_object_ref is None:
        return _result(
            status="BLOCKED_MISSING_STORAGE_REF",
            blocked_reason="storage_object_ref_required",
            errors=["storage_object_ref_required"],
            notes=_notes(boundary_input.get("notes"), "Storage upload boundary requires storage_object_ref."),
        )

    client_channel = _clean_required_ref(boundary_input.get("client_channel"))
    if client_channel is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="client_channel_required",
            errors=["client_channel_required"],
            notes=_notes(boundary_input.get("notes"), "Missing client_channel forces fail-closed behavior."),
        )

    tenant_validation_reason = _validate_tenant_isolation_candidate(
        tenant_isolation_candidate=boundary_input.get("tenant_isolation_candidate"),
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
    )
    if tenant_validation_reason is not None:
        return _result(
            status="BLOCKED_TENANT_ISOLATION",
            blocked_reason=tenant_validation_reason,
            errors=[tenant_validation_reason],
            notes=_notes(boundary_input.get("notes"), "Tenant isolation candidate did not clear this upload boundary."),
        )

    cost_validation_reason = _validate_cost_rate_limit_candidate(
        cost_rate_limit_candidate=boundary_input.get("cost_rate_limit_candidate"),
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
    )
    if cost_validation_reason is not None:
        return _result(
            status="BLOCKED_COST_OR_RATE_LIMIT",
            blocked_reason=cost_validation_reason,
            errors=[cost_validation_reason],
            notes=_notes(boundary_input.get("notes"), "Cost or rate guard did not clear this upload boundary."),
        )

    file_intake_candidate = boundary_input.get("file_intake_candidate")
    if file_intake_candidate is None:
        return _result(
            status="NEEDS_FILE_INTAKE",
            blocked_reason="file_intake_candidate_required",
            errors=["file_intake_candidate_required"],
            notes=_notes(boundary_input.get("notes"), "A governed file intake candidate is required before upload acceptance."),
        )
    if not isinstance(file_intake_candidate, dict) or not file_intake_candidate:
        return _result(
            status="NEEDS_FILE_INTAKE",
            blocked_reason="file_intake_candidate_invalid",
            errors=["file_intake_candidate_invalid"],
            notes=_notes(boundary_input.get("notes"), "Provided file intake candidate is invalid."),
        )

    file_intake_validation_reason = _validate_file_intake_candidate(
        file_intake_candidate=file_intake_candidate,
        owner_ref=owner_ref,
        case_ref=case_ref,
        storage_object_ref=storage_object_ref,
        file_name=file_name,
        file_kind=normalized_file_kind,
        file_size_bytes=file_size_bytes,
        content_type=content_type,
    )
    if file_intake_validation_reason is not None:
        return _result(
            status="NEEDS_FILE_INTAKE",
            blocked_reason=file_intake_validation_reason,
            errors=[file_intake_validation_reason],
            notes=_notes(boundary_input.get("notes"), "File intake candidate did not clear the upload boundary."),
        )

    checksum = _clean_optional_ref(boundary_input.get("checksum"))
    if checksum is None:
        return _result(
            status="NEEDS_OWNER_CONFIRMATION",
            blocked_reason="checksum_required_for_owner_confirmation",
            errors=["checksum_required_for_owner_confirmation"],
            notes=_notes(boundary_input.get("notes"), "Checksum is required before the boundary can accept the upload reference."),
        )

    safe_file_ref = _safe_file_ref(
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
        upload_request_ref=upload_request_ref,
        storage_object_ref=storage_object_ref,
    )
    evidence_ref_candidate = _evidence_ref_candidate(
        tenant_ref=tenant_ref,
        owner_ref=owner_ref,
        case_ref=case_ref,
        upload_request_ref=upload_request_ref,
        file_kind=normalized_file_kind,
    )
    source_session_ref = _clean_optional_ref(file_intake_candidate.get("source_session_ref")) or case_ref
    audit_event_candidate = _audit_event_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        source_session_ref=source_session_ref,
        safe_file_ref=safe_file_ref,
        upload_request_ref=upload_request_ref,
        storage_object_ref=storage_object_ref,
        tenant_ref=tenant_ref,
        file_kind=normalized_file_kind,
    )
    candidate: Service1StorageUploadBoundaryCandidateV1 = {
        "boundary_kind": BOUNDARY_KIND,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "upload_request_ref": upload_request_ref,
        "client_channel": client_channel,
        "file_name": file_name,
        "file_kind": normalized_file_kind,
        "file_size_bytes": file_size_bytes,
        "content_type": content_type,
        "storage_object_ref": storage_object_ref,
        "checksum": checksum,
        "safe_file_ref": safe_file_ref,
        "file_intake_candidate_ref": storage_object_ref,
        "evidence_ref_candidate": evidence_ref_candidate,
        "processing_job_candidate_required": False,
        "warnings": [],
        "errors": [],
        "audit_event_candidate": audit_event_candidate,
        "storage_write_authorized": False,
        "file_processing_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "evidence_authorized": False,
        "mutation_authorized": False,
        "db_authorized": False,
        "api_exposed": False,
        "llm_authorized": False,
    }
    return _result(
        status="STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY",
        storage_upload_boundary_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        notes=_notes(
            boundary_input.get("notes"),
            "Storage reference accepted as governed data only; it is not evidence, case truth, or runtime authority.",
        ),
    )


def _validate_tenant_isolation_candidate(
    *,
    tenant_isolation_candidate: object,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
) -> str | None:
    if tenant_isolation_candidate is None:
        return None
    if not isinstance(tenant_isolation_candidate, dict) or not tenant_isolation_candidate:
        return "tenant_isolation_candidate_invalid"
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
    checked_source_refs = tenant_isolation_candidate.get("checked_source_refs")
    if checked_source_refs is not None:
        if not isinstance(checked_source_refs, dict):
            return "tenant_isolation_checked_source_refs_invalid"
        for key, value in checked_source_refs.items():
            if "tenant" not in str(key).lower():
                continue
            if _clean_required_ref(value) != tenant_ref:
                return "tenant_ref_must_match_tenant_isolation_refs"
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
) -> str | None:
    if cost_rate_limit_candidate is None:
        return None
    if not isinstance(cost_rate_limit_candidate, dict) or not cost_rate_limit_candidate:
        return "cost_rate_limit_candidate_invalid"
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


def _validate_file_intake_candidate(
    *,
    file_intake_candidate: dict[str, object],
    owner_ref: str,
    case_ref: str,
    storage_object_ref: str,
    file_name: str,
    file_kind: str,
    file_size_bytes: int,
    content_type: str,
) -> str | None:
    if file_intake_candidate.get("intake_kind") != FILE_INTAKE_KIND:
        return "file_intake_kind_must_be_saas_file_intake_candidate"
    if file_intake_candidate.get("service_name") != SERVICE_NAME:
        return "file_intake_service_name_must_be_service_1"
    if _clean_required_ref(file_intake_candidate.get("owner_ref")) != owner_ref:
        return "file_intake_owner_ref_must_match_input"
    if _clean_required_ref(file_intake_candidate.get("case_ref")) != case_ref:
        return "file_intake_case_ref_must_match_input"
    if _clean_required_ref(file_intake_candidate.get("file_ref")) != storage_object_ref:
        return "storage_object_ref_must_match_file_intake_candidate"
    if _clean_required_ref(file_intake_candidate.get("declared_filename")) != file_name:
        return "file_name_must_match_file_intake_candidate"
    if _clean_required_ref(file_intake_candidate.get("declared_file_kind")) != file_kind:
        return "file_kind_must_match_file_intake_candidate"
    if _clean_required_ref(file_intake_candidate.get("declared_mime_type")) != content_type:
        return "content_type_must_match_file_intake_candidate"
    if file_intake_candidate.get("declared_size_bytes") != file_size_bytes:
        return "file_size_bytes_must_match_file_intake_candidate"
    for flag_name, reason in FILE_INTAKE_FLAG_REASON_BY_NAME.items():
        if file_intake_candidate.get(flag_name) is not False:
            return reason
    return None


def _audit_event_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    source_session_ref: str,
    safe_file_ref: str,
    upload_request_ref: str,
    storage_object_ref: str,
    tenant_ref: str,
    file_kind: str,
) -> Service1StorageUploadBoundaryAuditEventCandidateV1:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE_RECORDED",
        "event_status": "STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "source_slice_kind": BOUNDARY_KIND,
        "source_slice_ref": safe_file_ref,
        "audit_log_ref_candidate": f"audit_log:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}",
        "audit_event_ref_candidate": f"audit_event:{_safe_ref(upload_request_ref)}:{_safe_ref(safe_file_ref)}",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Real storage upload boundary candidate recorded.",
        "source_context_refs": {
            "tenant_ref": tenant_ref,
            "upload_request_ref": upload_request_ref,
            "storage_object_ref": storage_object_ref,
            "safe_file_ref": safe_file_ref,
            "file_kind": file_kind,
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


def _safe_file_ref(
    *,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    upload_request_ref: str,
    storage_object_ref: str,
) -> str:
    return (
        "safe_file_ref:"
        f"{_safe_ref(tenant_ref)}:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:"
        f"{_safe_ref(upload_request_ref)}:{_safe_ref(storage_object_ref)}"
    )


def _evidence_ref_candidate(
    *,
    tenant_ref: str,
    owner_ref: str,
    case_ref: str,
    upload_request_ref: str,
    file_kind: str,
) -> str:
    return (
        "evidence_candidate:"
        f"{_safe_ref(tenant_ref)}:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:"
        f"{_safe_ref(upload_request_ref)}:{_safe_ref(file_kind)}"
    )


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
    status: StorageUploadBoundaryStatusV1,
    storage_upload_boundary_candidate: Service1StorageUploadBoundaryCandidateV1 | None = None,
    blocked_reason: str | None = None,
    audit_event_candidate: Service1StorageUploadBoundaryAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1StorageUploadBoundaryResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "storage_upload_boundary_candidate": storage_upload_boundary_candidate,
        "blocked_reason": blocked_reason,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "storage_write_authorized": False,
        "file_processing_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "evidence_authorized": False,
        "mutation_authorized": False,
        "db_authorized": False,
        "api_exposed": False,
        "llm_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "BOUNDARY_KIND",
    "TENANT_ISOLATION_GUARD_KIND",
    "COST_AND_RATE_LIMIT_GUARD_KIND",
    "FILE_INTAKE_KIND",
    "ALLOWED_FILE_KINDS",
    "Service1StorageUploadBoundaryInputV1",
    "Service1StorageUploadBoundaryAuditEventCandidateV1",
    "Service1StorageUploadBoundaryCandidateV1",
    "Service1StorageUploadBoundaryResultV1",
    "build_service_1_real_storage_upload_boundary_contract_v1",
]
