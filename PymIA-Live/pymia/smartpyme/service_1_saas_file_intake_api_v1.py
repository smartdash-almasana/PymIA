from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_SAAS_FILE_INTAKE_API_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"

ALLOWED_FILE_KINDS: Final[tuple[str, ...]] = (
    "XLSX",
)

ALLOWED_MIME_TYPES: Final[tuple[str, ...]] = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

SaasFileIntakeStatusV1 = Literal[
    "SAAS_FILE_INTAKE_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_FILE_REF",
    "BLOCKED_MISSING_FILE_METADATA",
    "BLOCKED_UNSUPPORTED_FILE_KIND",
    "UNKNOWN",
]


class Service1SaasFileIntakeApiInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    file_ref: str
    declared_filename: str
    declared_file_kind: str
    declared_mime_type: str
    declared_size_bytes: int | None
    notes: list[str]


class Service1SaasFileIntakeCandidateV1(TypedDict):
    intake_kind: Literal["SAAS_FILE_INTAKE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    file_ref: str
    declared_filename: str
    declared_file_kind: str
    declared_mime_type: str
    declared_size_bytes: int | None
    evidence_ref_candidate: str
    task_spec_candidate_allowed: Literal[False]
    upload_authorized: Literal[False]
    file_read_authorized: Literal[False]
    parser_authorized: Literal[False]
    job_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1SaasFileIntakeApiResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: SaasFileIntakeStatusV1
    saas_file_intake_candidate: Service1SaasFileIntakeCandidateV1 | None
    blocked_reason: str | None
    upload_authorized: Literal[False]
    file_read_authorized: Literal[False]
    parser_authorized: Literal[False]
    job_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_saas_file_intake_api_v1(
    intake_input: Service1SaasFileIntakeApiInputV1,
) -> Service1SaasFileIntakeApiResultV1:
    """Build a SaaS file intake candidate without exposing a real API.

    Despite the roadmap name, this is a pure in-memory contract. It does not
    expose endpoints, upload files, read bytes, parse spreadsheets, create storage,
    persist state, start jobs, run pipelines, or call runners.
    """
    session = intake_input.get("saas_case_session_candidate")
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=["SaaS file intake candidate requires a SaaS case session candidate."],
        )

    invalid_session_reason = _validate_session(session)
    if invalid_session_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=invalid_session_reason,
            notes=["SaaS case session candidate is invalid for file intake."],
        )

    file_ref = _clean_required_ref(intake_input.get("file_ref"))
    if file_ref is None:
        return _result(
            status="BLOCKED_MISSING_FILE_REF",
            blocked_reason="file_ref_required",
            notes=["SaaS file intake candidate requires file_ref."],
        )

    declared_filename = _clean_required_ref(intake_input.get("declared_filename"))
    if declared_filename is None:
        return _result(
            status="BLOCKED_MISSING_FILE_METADATA",
            blocked_reason="declared_filename_required",
            notes=["SaaS file intake candidate requires declared_filename."],
        )

    declared_file_kind = _clean_required_ref(intake_input.get("declared_file_kind"))
    if declared_file_kind is None:
        return _result(
            status="BLOCKED_MISSING_FILE_METADATA",
            blocked_reason="declared_file_kind_required",
            notes=["SaaS file intake candidate requires declared_file_kind."],
        )
    declared_file_kind = declared_file_kind.upper()
    if declared_file_kind not in ALLOWED_FILE_KINDS:
        return _result(
            status="BLOCKED_UNSUPPORTED_FILE_KIND",
            blocked_reason="declared_file_kind_not_supported",
            notes=["Declared file kind is not supported by this contract."],
        )

    declared_mime_type = _clean_required_ref(intake_input.get("declared_mime_type"))
    if declared_mime_type is None:
        return _result(
            status="BLOCKED_MISSING_FILE_METADATA",
            blocked_reason="declared_mime_type_required",
            notes=["SaaS file intake candidate requires declared_mime_type."],
        )
    if declared_mime_type not in ALLOWED_MIME_TYPES:
        return _result(
            status="BLOCKED_UNSUPPORTED_FILE_KIND",
            blocked_reason="declared_mime_type_not_supported",
            notes=["Declared MIME type is not supported by this contract."],
        )

    declared_size_bytes = intake_input.get("declared_size_bytes")
    if declared_size_bytes is not None:
        if not isinstance(declared_size_bytes, int) or declared_size_bytes < 0:
            return _result(
                status="BLOCKED_MISSING_FILE_METADATA",
                blocked_reason="declared_size_bytes_must_be_non_negative_int_or_none",
                notes=["Declared size must be a non-negative integer or None."],
            )

    owner_ref = str(session["owner_ref"])
    case_ref = str(session["case_ref"])
    source_session_ref = _source_session_ref(session)

    candidate: Service1SaasFileIntakeCandidateV1 = {
        "intake_kind": INTAKE_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "file_ref": file_ref,
        "declared_filename": declared_filename,
        "declared_file_kind": declared_file_kind,
        "declared_mime_type": declared_mime_type,
        "declared_size_bytes": declared_size_bytes,
        "evidence_ref_candidate": _evidence_ref_candidate(owner_ref=owner_ref, case_ref=case_ref, file_ref=file_ref),
        "task_spec_candidate_allowed": False,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="SAAS_FILE_INTAKE_CANDIDATE_READY",
        saas_file_intake_candidate=candidate,
        notes=["SaaS file intake candidate created without API exposure, upload, IO, parsing, jobs, or runtime."],
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
    if session.get("api_exposed") is not False:
        return "session_api_exposed_must_be_false"
    if session.get("runtime_authorized") is not False:
        return "session_runtime_authorized_must_be_false"
    return None


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _evidence_ref_candidate(*, owner_ref: str, case_ref: str, file_ref: str) -> str:
    return f"evidence_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}:{_safe_ref(file_ref)}"


def _safe_ref(value: str) -> str:
    return value.strip().replace(" ", "_")


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _result(
    *,
    status: SaasFileIntakeStatusV1,
    saas_file_intake_candidate: Service1SaasFileIntakeCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1SaasFileIntakeApiResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "saas_file_intake_candidate": saas_file_intake_candidate,
        "blocked_reason": blocked_reason,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "SESSION_KIND",
    "INTAKE_KIND",
    "ALLOWED_FILE_KINDS",
    "ALLOWED_MIME_TYPES",
    "Service1SaasFileIntakeApiInputV1",
    "Service1SaasFileIntakeCandidateV1",
    "Service1SaasFileIntakeApiResultV1",
    "build_service_1_saas_file_intake_api_v1",
]
