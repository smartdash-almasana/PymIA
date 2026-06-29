from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_SAAS_CASE_SESSION_MODEL_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
ALLOWED_SESSION_LIFECYCLES: Final[tuple[str, ...]] = (
    "CREATED",
    "INTAKE_PENDING",
    "PROCESSING_CANDIDATE",
    "OWNER_REVIEW_PENDING",
    "REENTRY_PENDING",
    "RERUN_CANDIDATE_READY",
    "CLOSED_CANDIDATE",
)

SaasCaseSessionStatusV1 = Literal[
    "SAAS_CASE_SESSION_CANDIDATE_READY",
    "BLOCKED_MISSING_OWNER_REF",
    "BLOCKED_MISSING_CASE_REF",
    "BLOCKED_MISSING_SERVICE_STATE",
    "UNKNOWN",
]


class Service1SaasCaseSessionModelInputV1(TypedDict):
    owner_ref: str
    case_ref: str
    service_name: str
    current_chain_status: str
    service_1_state_refs: dict[str, str]
    requested_session_lifecycle: str
    notes: list[str]


class Service1SaasCaseSessionCandidateV1(TypedDict):
    session_kind: Literal["SAAS_CASE_SESSION_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    session_lifecycle: str
    current_chain_status: str
    service_1_state_refs: dict[str, str]
    runtime_authorized: Literal[False]
    job_authorized: Literal[False]
    file_upload_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1SaasCaseSessionModelResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: SaasCaseSessionStatusV1
    saas_case_session_candidate: Service1SaasCaseSessionCandidateV1 | None
    blocked_reason: str | None
    runtime_authorized: Literal[False]
    job_authorized: Literal[False]
    file_upload_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_saas_case_session_model_v1(
    session_input: Service1SaasCaseSessionModelInputV1,
) -> Service1SaasCaseSessionModelResultV1:
    """Build a minimal in-memory SaaS case session candidate for Servicio 1.

    This model does not expose APIs, authenticate users, create tenants, upload
    files, persist state, start jobs, execute pipelines, or call runners. It only
    composes owner/case/service references with the current autonomous-chain
    status into a non-executable session candidate.
    """
    owner_ref = _clean_required_ref(session_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="BLOCKED_MISSING_OWNER_REF",
            blocked_reason="owner_ref_required",
            notes=["SaaS case session candidate requires owner_ref."],
        )

    case_ref = _clean_required_ref(session_input.get("case_ref"))
    if case_ref is None:
        return _result(
            status="BLOCKED_MISSING_CASE_REF",
            blocked_reason="case_ref_required",
            notes=["SaaS case session candidate requires case_ref."],
        )

    if session_input.get("service_name") != SERVICE_NAME:
        return _result(
            status="BLOCKED_MISSING_SERVICE_STATE",
            blocked_reason="service_name_must_be_service_1",
            notes=["SaaS case session candidate is scoped only to SERVICE_1."],
        )

    current_chain_status = _clean_required_ref(session_input.get("current_chain_status"))
    if current_chain_status is None:
        return _result(
            status="BLOCKED_MISSING_SERVICE_STATE",
            blocked_reason="current_chain_status_required",
            notes=["SaaS case session candidate requires current_chain_status."],
        )

    service_1_state_refs = _clean_state_refs(session_input.get("service_1_state_refs", {}))
    if not service_1_state_refs:
        return _result(
            status="BLOCKED_MISSING_SERVICE_STATE",
            blocked_reason="service_1_state_refs_required",
            notes=["SaaS case session candidate requires service_1_state_refs."],
        )

    requested_lifecycle = _clean_required_ref(session_input.get("requested_session_lifecycle"))
    if requested_lifecycle is None:
        return _result(
            status="UNKNOWN",
            blocked_reason="requested_session_lifecycle_required",
            notes=["SaaS case session candidate requires requested_session_lifecycle."],
        )
    if requested_lifecycle not in ALLOWED_SESSION_LIFECYCLES:
        return _result(
            status="UNKNOWN",
            blocked_reason="requested_session_lifecycle_not_allowed",
            notes=["Requested session lifecycle is not allowed."],
        )

    candidate: Service1SaasCaseSessionCandidateV1 = {
        "session_kind": SESSION_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "session_lifecycle": requested_lifecycle,
        "current_chain_status": current_chain_status,
        "service_1_state_refs": dict(service_1_state_refs),
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="SAAS_CASE_SESSION_CANDIDATE_READY",
        saas_case_session_candidate=candidate,
        notes=["SaaS case session candidate created without infrastructure exposure or execution."],
    )


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_state_refs(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(item, str) or not item.strip():
            continue
        clean[key] = item
    return clean


def _result(
    *,
    status: SaasCaseSessionStatusV1,
    saas_case_session_candidate: Service1SaasCaseSessionCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1SaasCaseSessionModelResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "saas_case_session_candidate": saas_case_session_candidate,
        "blocked_reason": blocked_reason,
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "SESSION_KIND",
    "ALLOWED_SESSION_LIFECYCLES",
    "Service1SaasCaseSessionModelInputV1",
    "Service1SaasCaseSessionCandidateV1",
    "Service1SaasCaseSessionModelResultV1",
    "build_service_1_saas_case_session_model_v1",
]
