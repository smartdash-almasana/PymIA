from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_HUMAN_REVIEW_RELEASE_INTEGRATION_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
GATE_KIND: Final[str] = "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE"

DELIVERY_RELEASE_KIND: Final[str] = "DELIVERY_RELEASE_CANDIDATE"
OWNER_PACKET_KIND: Final[str] = "OWNER_DELIVERY_PACKET_CANDIDATE"
ENDPOINT_BOUNDARY_KIND: Final[str] = "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE"
AUTH_BOUNDARY_KIND: Final[str] = "REAL_AUTH_BOUNDARY_CANDIDATE"
STORAGE_BOUNDARY_KIND: Final[str] = "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE"
WORKER_BOUNDARY_KIND: Final[str] = "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE"

ALLOWED_DECISIONS: Final[tuple[str, ...]] = (
    "APPROVED_FOR_DELIVERY",
    "NEEDS_CORRECTION",
    "BLOCKED",
)

BLOCKED_CLAIMS: Final[list[str]] = [
    "auditoria",
    "certificacion",
    "conciliacion_definitiva",
    "diagnostico_integral",
    "rentabilidad_real_confirmada",
    "reemplazo_contador",
]

IntegrationDangerFlagNames = Literal[
    "publish_authorized",
    "final_release_authorized",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "runtime_authorized",
    "mutation_authorized",
    "llm_authorized",
]

HumanReviewReleaseIntegrationStatusV1 = Literal[
    "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY",
    "PENDING_HUMAN_REVIEW",
    "BLOCKED_INVALID_DELIVERY_RELEASE",
    "BLOCKED_INVALID_OWNER_PACKET",
    "BLOCKED_INVALID_ENDPOINT_BOUNDARY",
    "BLOCKED_INVALID_AUTH_BOUNDARY",
    "BLOCKED_INVALID_STORAGE_BOUNDARY",
    "BLOCKED_INVALID_WORKER_BOUNDARY",
    "BLOCKED_UNSAFE_PUBLISH_FLAGS",
    "NEEDS_SIGNOFF",
    "UNKNOWN",
]


class Service1HumanReviewReleaseIntegrationGateInputV1(TypedDict):
    delivery_release_candidate: dict[str, object] | None
    owner_delivery_packet_candidate: dict[str, object] | None
    endpoint_api_boundary_candidate: dict[str, object] | None
    auth_boundary_candidate: dict[str, object] | None
    storage_upload_boundary_candidate: dict[str, object] | None
    worker_runtime_boundary_candidate: dict[str, object] | None
    notes: list[str]


class Service1HumanReviewReleaseIntegrationAuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: Literal["HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE"]
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


class Service1HumanReviewReleaseIntegrationCandidateV1(TypedDict):
    gate_kind: Literal["HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE"]
    candidate_status: Literal["HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY"]
    status: Literal["PENDING_HUMAN_REVIEW"]
    service_name: Literal["SERVICE_1"]
    source_pipeline_run_ref: str
    tenant_ref: str
    owner_ref: str
    case_ref: str
    session_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    owner_facing_summary: str
    human_review_required: Literal[True]
    reviewer_role: str
    decision_required_before_client_use: Literal[True]
    allowed_decisions: list[str]
    blocked_claims: list[str]
    publishable: Literal[False]
    signoff_required: Literal[True]
    final_release_authorized: Literal[False]
    boundary_candidate_kinds: dict[str, str]
    audit_event_candidate: Service1HumanReviewReleaseIntegrationAuditEventCandidateV1
    warnings: list[str]
    errors: list[str]
    publish_authorized: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


class Service1HumanReviewReleaseIntegrationGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: HumanReviewReleaseIntegrationStatusV1
    human_review_release_integration_candidate: Service1HumanReviewReleaseIntegrationCandidateV1 | None
    blocked_reason: str | None
    audit_event_candidate: Service1HumanReviewReleaseIntegrationAuditEventCandidateV1 | None
    warnings: list[str]
    errors: list[str]
    publish_authorized: Literal[False]
    final_release_authorized: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    runtime_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]
    notes: list[str]


def build_service_1_human_review_release_integration_gate_v1(
    gate_input: Service1HumanReviewReleaseIntegrationGateInputV1,
) -> Service1HumanReviewReleaseIntegrationGateResultV1:
    """Integrate release, packet, and boundary evidence into a pending human review candidate."""
    delivery_release_candidate = gate_input.get("delivery_release_candidate")
    if not isinstance(delivery_release_candidate, dict) or not delivery_release_candidate:
        return _result(
            status="BLOCKED_INVALID_DELIVERY_RELEASE",
            blocked_reason="delivery_release_candidate_required",
            errors=["delivery_release_candidate_required"],
            notes=_notes(gate_input.get("notes"), "Human review release integration requires delivery_release_candidate."),
        )

    unsafe_delivery_reason = _unsafe_publish_reason(delivery_release_candidate)
    if unsafe_delivery_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_PUBLISH_FLAGS",
            blocked_reason=unsafe_delivery_reason,
            errors=[unsafe_delivery_reason],
            notes=_notes(gate_input.get("notes"), "Unsafe publish or release flags are blocked."),
        )

    delivery_release_validation = _validate_delivery_release_candidate(delivery_release_candidate)
    if delivery_release_validation is not None:
        status, reason = delivery_release_validation
        return _result(
            status=status,
            blocked_reason=reason,
            errors=[reason],
            notes=_notes(gate_input.get("notes"), "Delivery release candidate is invalid for human review integration."),
        )

    owner_delivery_packet_candidate = gate_input.get("owner_delivery_packet_candidate")
    if not isinstance(owner_delivery_packet_candidate, dict) or not owner_delivery_packet_candidate:
        return _result(
            status="BLOCKED_INVALID_OWNER_PACKET",
            blocked_reason="owner_delivery_packet_candidate_required",
            errors=["owner_delivery_packet_candidate_required"],
            notes=_notes(gate_input.get("notes"), "Human review release integration requires owner_delivery_packet_candidate."),
        )

    unsafe_packet_reason = _unsafe_publish_reason(owner_delivery_packet_candidate)
    if unsafe_packet_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_PUBLISH_FLAGS",
            blocked_reason=unsafe_packet_reason,
            errors=[unsafe_packet_reason],
            notes=_notes(gate_input.get("notes"), "Unsafe publish or release flags are blocked."),
        )

    owner_packet_validation = _validate_owner_packet_candidate(
        owner_delivery_packet_candidate=owner_delivery_packet_candidate,
        delivery_release_candidate=delivery_release_candidate,
    )
    if owner_packet_validation is not None:
        status, reason = owner_packet_validation
        return _result(
            status=status,
            blocked_reason=reason,
            errors=[reason],
            notes=_notes(gate_input.get("notes"), "Owner delivery packet candidate is invalid for human review integration."),
        )

    source_pipeline_run_ref = str(delivery_release_candidate["source_pipeline_run_ref"]).strip()
    if source_pipeline_run_ref == "pipeline_run:unknown":
        return _result(
            status="UNKNOWN",
            blocked_reason="source_pipeline_run_ref_unknown",
            errors=["source_pipeline_run_ref_unknown"],
            notes=_notes(gate_input.get("notes"), "The source pipeline run cannot be classified safely."),
        )

    endpoint_api_boundary_candidate = gate_input.get("endpoint_api_boundary_candidate")
    endpoint_boundary_validation = _validate_endpoint_boundary_candidate(endpoint_api_boundary_candidate)
    if endpoint_boundary_validation is not None:
        return _result(
            status="BLOCKED_INVALID_ENDPOINT_BOUNDARY",
            blocked_reason=endpoint_boundary_validation,
            errors=[endpoint_boundary_validation],
            notes=_notes(gate_input.get("notes"), "Endpoint API boundary candidate is invalid for human review integration."),
        )
    endpoint_candidate = dict(endpoint_api_boundary_candidate)

    auth_boundary_candidate = gate_input.get("auth_boundary_candidate")
    auth_boundary_validation = _validate_auth_boundary_candidate(auth_boundary_candidate)
    if auth_boundary_validation is not None:
        return _result(
            status="BLOCKED_INVALID_AUTH_BOUNDARY",
            blocked_reason=auth_boundary_validation,
            errors=[auth_boundary_validation],
            notes=_notes(gate_input.get("notes"), "Auth boundary candidate is invalid for human review integration."),
        )
    auth_candidate = dict(auth_boundary_candidate)

    storage_upload_boundary_candidate = gate_input.get("storage_upload_boundary_candidate")
    storage_boundary_validation = _validate_storage_boundary_candidate(storage_upload_boundary_candidate)
    if storage_boundary_validation is not None:
        return _result(
            status="BLOCKED_INVALID_STORAGE_BOUNDARY",
            blocked_reason=storage_boundary_validation,
            errors=[storage_boundary_validation],
            notes=_notes(gate_input.get("notes"), "Storage upload boundary candidate is invalid for human review integration."),
        )
    storage_candidate = dict(storage_upload_boundary_candidate)

    worker_runtime_boundary_candidate = gate_input.get("worker_runtime_boundary_candidate")
    worker_boundary_validation = _validate_worker_boundary_candidate(worker_runtime_boundary_candidate)
    if worker_boundary_validation is not None:
        return _result(
            status="BLOCKED_INVALID_WORKER_BOUNDARY",
            blocked_reason=worker_boundary_validation,
            errors=[worker_boundary_validation],
            notes=_notes(gate_input.get("notes"), "Worker runtime boundary candidate is invalid for human review integration."),
        )
    worker_candidate = dict(worker_runtime_boundary_candidate)

    signoff_needed_reason = _signoff_needed_reason(
        delivery_release_candidate=delivery_release_candidate,
        owner_delivery_packet_candidate=owner_delivery_packet_candidate,
    )
    if signoff_needed_reason is not None:
        return _result(
            status="NEEDS_SIGNOFF",
            blocked_reason=signoff_needed_reason,
            errors=[signoff_needed_reason],
            notes=_notes(gate_input.get("notes"), "Human signoff remains mandatory before final release."),
        )

    lineage_validation_reason = _validate_common_lineage(
        endpoint_candidate=endpoint_candidate,
        auth_candidate=auth_candidate,
        storage_candidate=storage_candidate,
        worker_candidate=worker_candidate,
    )
    if lineage_validation_reason is not None:
        status = {
            "endpoint": "BLOCKED_INVALID_ENDPOINT_BOUNDARY",
            "auth": "BLOCKED_INVALID_AUTH_BOUNDARY",
            "storage": "BLOCKED_INVALID_STORAGE_BOUNDARY",
            "worker": "BLOCKED_INVALID_WORKER_BOUNDARY",
        }[_lineage_owner(lineage_validation_reason)]
        return _result(
            status=status,
            blocked_reason=lineage_validation_reason,
            errors=[lineage_validation_reason],
            notes=_notes(gate_input.get("notes"), "Cross-boundary lineage mismatch blocks human review integration."),
        )

    tenant_ref = str(auth_candidate["tenant_ref"]).strip()
    owner_ref = str(auth_candidate["owner_ref"]).strip()
    case_ref = str(storage_candidate["case_ref"]).strip()
    session_ref = str(worker_candidate["session_ref"]).strip()
    artifact_refs = _clean_refs(delivery_release_candidate.get("artifact_refs"))
    warning_refs = _clean_refs(owner_delivery_packet_candidate.get("warning_refs"))
    owner_facing_summary = str(owner_delivery_packet_candidate["owner_facing_summary"]).strip()

    audit_event_candidate = _audit_event_candidate(
        owner_ref=owner_ref,
        case_ref=case_ref,
        session_ref=session_ref,
        source_pipeline_run_ref=source_pipeline_run_ref,
        tenant_ref=tenant_ref,
    )
    candidate: Service1HumanReviewReleaseIntegrationCandidateV1 = {
        "gate_kind": GATE_KIND,
        "candidate_status": "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY",
        "status": "PENDING_HUMAN_REVIEW",
        "service_name": SERVICE_NAME,
        "source_pipeline_run_ref": source_pipeline_run_ref,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "session_ref": session_ref,
        "artifact_refs": artifact_refs,
        "warning_refs": warning_refs,
        "owner_facing_summary": owner_facing_summary,
        "human_review_required": True,
        "reviewer_role": "operator_or_accountant",
        "decision_required_before_client_use": True,
        "allowed_decisions": list(ALLOWED_DECISIONS),
        "blocked_claims": list(BLOCKED_CLAIMS),
        "publishable": False,
        "signoff_required": True,
        "final_release_authorized": False,
        "boundary_candidate_kinds": {
            "endpoint_api_boundary_kind": ENDPOINT_BOUNDARY_KIND,
            "auth_boundary_kind": AUTH_BOUNDARY_KIND,
            "storage_upload_boundary_kind": STORAGE_BOUNDARY_KIND,
            "worker_runtime_boundary_kind": WORKER_BOUNDARY_KIND,
        },
        "audit_event_candidate": audit_event_candidate,
        "warnings": [],
        "errors": [],
        "publish_authorized": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }
    return _result(
        status="PENDING_HUMAN_REVIEW",
        human_review_release_integration_candidate=candidate,
        audit_event_candidate=audit_event_candidate,
        notes=_notes(
            gate_input.get("notes"),
            "Human review release integration candidate created as pending human review only; it does not publish or authorize final release.",
        ),
    )


def _validate_delivery_release_candidate(
    delivery_release_candidate: dict[str, object],
) -> tuple[HumanReviewReleaseIntegrationStatusV1, str] | None:
    if delivery_release_candidate.get("release_kind") != DELIVERY_RELEASE_KIND:
        return ("BLOCKED_INVALID_DELIVERY_RELEASE", "release_kind_must_be_delivery_release_candidate")
    source_pipeline_run_ref = _clean_required_ref(delivery_release_candidate.get("source_pipeline_run_ref"))
    if source_pipeline_run_ref is None:
        return ("BLOCKED_INVALID_DELIVERY_RELEASE", "source_pipeline_run_ref_required")
    artifact_refs = _clean_refs(delivery_release_candidate.get("artifact_refs"))
    if not artifact_refs:
        return ("BLOCKED_INVALID_DELIVERY_RELEASE", "artifact_refs_required")
    return None


def _validate_owner_packet_candidate(
    *,
    owner_delivery_packet_candidate: dict[str, object],
    delivery_release_candidate: dict[str, object],
) -> tuple[HumanReviewReleaseIntegrationStatusV1, str] | None:
    if owner_delivery_packet_candidate.get("packet_kind") != OWNER_PACKET_KIND:
        return ("BLOCKED_INVALID_OWNER_PACKET", "packet_kind_must_be_owner_delivery_packet_candidate")
    source_pipeline_run_ref = _clean_required_ref(owner_delivery_packet_candidate.get("source_pipeline_run_ref"))
    if source_pipeline_run_ref is None:
        return ("BLOCKED_INVALID_OWNER_PACKET", "source_pipeline_run_ref_required")
    if source_pipeline_run_ref != _clean_required_ref(delivery_release_candidate.get("source_pipeline_run_ref")):
        return ("BLOCKED_INVALID_OWNER_PACKET", "source_pipeline_run_ref_must_match_delivery_release_candidate")
    artifact_refs = _clean_refs(owner_delivery_packet_candidate.get("artifact_refs"))
    if not artifact_refs:
        return ("BLOCKED_INVALID_OWNER_PACKET", "artifact_refs_required")
    if artifact_refs != _clean_refs(delivery_release_candidate.get("artifact_refs")):
        return ("BLOCKED_INVALID_OWNER_PACKET", "artifact_refs_must_match_delivery_release_candidate")
    owner_facing_summary = _clean_required_ref(owner_delivery_packet_candidate.get("owner_facing_summary"))
    if owner_facing_summary is None:
        return ("BLOCKED_INVALID_OWNER_PACKET", "owner_facing_summary_required")
    return None


def _validate_endpoint_boundary_candidate(value: object) -> str | None:
    if not isinstance(value, dict) or not value:
        return "endpoint_api_boundary_candidate_required"
    if value.get("boundary_kind") != ENDPOINT_BOUNDARY_KIND:
        return "endpoint_boundary_kind_must_match"
    if value.get("service_name") != SERVICE_NAME:
        return "endpoint_service_name_must_be_service_1"
    if _clean_required_ref(value.get("tenant_ref")) is None:
        return "endpoint_tenant_ref_required"
    if _clean_required_ref(value.get("owner_ref")) is None:
        return "endpoint_owner_ref_required"
    if _clean_required_ref(value.get("request_id")) is None:
        return "endpoint_request_id_required"
    if _clean_required_ref(value.get("accepted_operation_kind")) is None:
        return "endpoint_accepted_operation_kind_required"
    if _unsafe_boundary_reason(value) is not None:
        return _unsafe_boundary_reason(value)
    return None


def _validate_auth_boundary_candidate(value: object) -> str | None:
    if not isinstance(value, dict) or not value:
        return "auth_boundary_candidate_required"
    if value.get("boundary_kind") != AUTH_BOUNDARY_KIND:
        return "auth_boundary_kind_must_match"
    if value.get("service_name") != SERVICE_NAME:
        return "auth_service_name_must_be_service_1"
    if _clean_required_ref(value.get("tenant_ref")) is None:
        return "auth_tenant_ref_required"
    if _clean_required_ref(value.get("owner_ref")) is None:
        return "auth_owner_ref_required"
    if _clean_required_ref(value.get("authorized_operation_kind")) is None:
        return "auth_authorized_operation_kind_required"
    unsafe_reason = _unsafe_boundary_reason(value)
    if unsafe_reason is not None:
        return unsafe_reason
    return None


def _validate_storage_boundary_candidate(value: object) -> str | None:
    if not isinstance(value, dict) or not value:
        return "storage_boundary_candidate_required"
    if value.get("boundary_kind") != STORAGE_BOUNDARY_KIND:
        return "storage_boundary_kind_must_match"
    if value.get("service_name") != SERVICE_NAME:
        return "storage_service_name_must_be_service_1"
    if _clean_required_ref(value.get("tenant_ref")) is None:
        return "storage_tenant_ref_required"
    if _clean_required_ref(value.get("owner_ref")) is None:
        return "storage_owner_ref_required"
    if _clean_required_ref(value.get("case_ref")) is None:
        return "storage_case_ref_required"
    unsafe_reason = _unsafe_boundary_reason(value)
    if unsafe_reason is not None:
        return unsafe_reason
    return None


def _validate_worker_boundary_candidate(value: object) -> str | None:
    if not isinstance(value, dict) or not value:
        return "worker_boundary_candidate_required"
    if value.get("boundary_kind") != WORKER_BOUNDARY_KIND:
        return "worker_boundary_kind_must_match"
    if value.get("service_name") != SERVICE_NAME:
        return "worker_service_name_must_be_service_1"
    if _clean_required_ref(value.get("tenant_ref")) is None:
        return "worker_tenant_ref_required"
    if _clean_required_ref(value.get("owner_ref")) is None:
        return "worker_owner_ref_required"
    if _clean_required_ref(value.get("case_ref")) is None:
        return "worker_case_ref_required"
    if _clean_required_ref(value.get("session_ref")) is None:
        return "worker_session_ref_required"
    unsafe_reason = _unsafe_boundary_reason(value)
    if unsafe_reason is not None:
        return unsafe_reason
    return None


def _signoff_needed_reason(
    *,
    delivery_release_candidate: dict[str, object],
    owner_delivery_packet_candidate: dict[str, object],
) -> str | None:
    if delivery_release_candidate.get("signoff_required") is not True:
        return "delivery_release_candidate_must_require_signoff"
    if owner_delivery_packet_candidate.get("signoff_required") is not True:
        return "owner_delivery_packet_candidate_must_require_signoff"
    return None


def _unsafe_publish_reason(candidate: dict[str, object]) -> str | None:
    if candidate.get("publishable") is not False:
        return "publishable_must_be_false"
    for key in ("delivery_authorized", "autonomous_delivery_authorized", "signoff_authorized", "release_authorized"):
        if key in candidate and candidate.get(key) is not False:
            return f"{key}_must_be_false"
    return None


def _unsafe_boundary_reason(candidate: dict[str, object]) -> str | None:
    for key in (
        "api_exposed",
        "runtime_authorized",
        "storage_write_authorized",
        "db_authorized",
        "worker_authorized",
        "queue_authorized",
        "mutation_authorized",
        "llm_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "publish_authorized",
        "final_release_authorized",
    ):
        if key in candidate and candidate.get(key) is not False:
            return f"{key}_must_be_false"
    return None


def _validate_common_lineage(
    *,
    endpoint_candidate: dict[str, object],
    auth_candidate: dict[str, object],
    storage_candidate: dict[str, object],
    worker_candidate: dict[str, object],
) -> str | None:
    auth_tenant_ref = str(auth_candidate["tenant_ref"]).strip()
    auth_owner_ref = str(auth_candidate["owner_ref"]).strip()
    storage_case_ref = str(storage_candidate["case_ref"]).strip()
    worker_session_ref = str(worker_candidate["session_ref"]).strip()

    if str(endpoint_candidate["tenant_ref"]).strip() != auth_tenant_ref:
        return "endpoint_boundary_tenant_ref_must_match_auth_boundary"
    if str(endpoint_candidate["owner_ref"]).strip() != auth_owner_ref:
        return "endpoint_boundary_owner_ref_must_match_auth_boundary"
    if endpoint_candidate.get("case_ref") is not None and str(endpoint_candidate["case_ref"]).strip() != storage_case_ref:
        return "endpoint_boundary_case_ref_must_match_storage_boundary"
    if str(storage_candidate["tenant_ref"]).strip() != auth_tenant_ref:
        return "storage_boundary_tenant_ref_must_match_auth_boundary"
    if str(storage_candidate["owner_ref"]).strip() != auth_owner_ref:
        return "storage_boundary_owner_ref_must_match_auth_boundary"
    if str(worker_candidate["tenant_ref"]).strip() != auth_tenant_ref:
        return "worker_boundary_tenant_ref_must_match_auth_boundary"
    if str(worker_candidate["owner_ref"]).strip() != auth_owner_ref:
        return "worker_boundary_owner_ref_must_match_auth_boundary"
    if str(worker_candidate["case_ref"]).strip() != storage_case_ref:
        return "worker_boundary_case_ref_must_match_storage_boundary"
    if _clean_required_ref(worker_session_ref) is None:
        return "worker_boundary_session_ref_required"
    return None


def _lineage_owner(reason: str) -> str:
    if reason.startswith("endpoint_"):
        return "endpoint"
    if reason.startswith("storage_"):
        return "storage"
    if reason.startswith("worker_"):
        return "worker"
    return "auth"


def _audit_event_candidate(
    *,
    owner_ref: str,
    case_ref: str,
    session_ref: str,
    source_pipeline_run_ref: str,
    tenant_ref: str,
) -> Service1HumanReviewReleaseIntegrationAuditEventCandidateV1:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_RECORDED",
        "event_status": "PENDING_HUMAN_REVIEW",
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": session_ref,
        "source_slice_kind": GATE_KIND,
        "source_slice_ref": source_pipeline_run_ref,
        "audit_log_ref_candidate": f"audit_log:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}",
        "audit_event_ref_candidate": f"audit_event:{_safe_ref(source_pipeline_run_ref)}:{_safe_ref(session_ref)}",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Human review release integration candidate recorded.",
        "source_context_refs": {
            "tenant_ref": tenant_ref,
            "source_pipeline_run_ref": source_pipeline_run_ref,
            "session_ref": session_ref,
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


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if isinstance(value, str) and value.strip()]


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _notes(notes: object, fallback_note: str) -> list[str]:
    if not isinstance(notes, list):
        return [fallback_note]
    cleaned_notes = [str(item) for item in notes]
    cleaned_notes.append(fallback_note)
    return cleaned_notes


def _result(
    *,
    status: HumanReviewReleaseIntegrationStatusV1,
    human_review_release_integration_candidate: Service1HumanReviewReleaseIntegrationCandidateV1 | None = None,
    blocked_reason: str | None = None,
    audit_event_candidate: Service1HumanReviewReleaseIntegrationAuditEventCandidateV1 | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1HumanReviewReleaseIntegrationGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "human_review_release_integration_candidate": human_review_release_integration_candidate,
        "blocked_reason": blocked_reason,
        "audit_event_candidate": audit_event_candidate,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "publish_authorized": False,
        "final_release_authorized": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "GATE_KIND",
    "DELIVERY_RELEASE_KIND",
    "OWNER_PACKET_KIND",
    "ENDPOINT_BOUNDARY_KIND",
    "AUTH_BOUNDARY_KIND",
    "STORAGE_BOUNDARY_KIND",
    "WORKER_BOUNDARY_KIND",
    "ALLOWED_DECISIONS",
    "BLOCKED_CLAIMS",
    "Service1HumanReviewReleaseIntegrationGateInputV1",
    "Service1HumanReviewReleaseIntegrationAuditEventCandidateV1",
    "Service1HumanReviewReleaseIntegrationCandidateV1",
    "Service1HumanReviewReleaseIntegrationGateResultV1",
    "build_service_1_human_review_release_integration_gate_v1",
]
