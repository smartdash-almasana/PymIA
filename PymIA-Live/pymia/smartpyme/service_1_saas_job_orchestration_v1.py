from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_SAAS_JOB_ORCHESTRATION_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"
FILE_INTAKE_KIND: Final[str] = "SAAS_FILE_INTAKE_CANDIDATE"
JOB_KIND: Final[str] = "SAAS_JOB_ORCHESTRATION_CANDIDATE"

INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE: Final[str] = "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE"
AUTONOMOUS_RERUN_PROCESSING_CANDIDATE: Final[str] = "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE"
OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE: Final[str] = "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE"

ALLOWED_REQUESTED_JOB_KINDS: Final[tuple[str, ...]] = (
    INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
    AUTONOMOUS_RERUN_PROCESSING_CANDIDATE,
    OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE,
)

SaasJobOrchestrationStatusV1 = Literal[
    "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_MISSING_JOB_KIND",
    "BLOCKED_MISSING_JOB_INPUT_REFS",
    "BLOCKED_UNSUPPORTED_JOB_KIND",
    "UNKNOWN",
]


class Service1SaasJobOrchestrationInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    autonomous_chain_candidate_refs: dict[str, str]
    requested_job_kind: str
    notes: list[str]


class Service1SaasJobOrchestrationCandidateV1(TypedDict):
    job_kind: Literal["SAAS_JOB_ORCHESTRATION_CANDIDATE"]
    requested_job_kind: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_file_intake_ref: str | None
    autonomous_chain_candidate_refs: dict[str, str]
    planned_job_steps: list[str]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    async_execution_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1SaasJobOrchestrationResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: SaasJobOrchestrationStatusV1
    saas_job_orchestration_candidate: Service1SaasJobOrchestrationCandidateV1 | None
    blocked_reason: str | None
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    async_execution_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_saas_job_orchestration_v1(
    orchestration_input: Service1SaasJobOrchestrationInputV1,
) -> Service1SaasJobOrchestrationResultV1:
    """Build a non-executable SaaS job orchestration candidate for Servicio 1.

    This contract only describes the intended job and its deterministic planning
    steps. It does not start workers, queues, concurrent execution, jobs, APIs,
    storage, file parsing, pipelines, runners, or model interactions.
    """
    session = orchestration_input.get("saas_case_session_candidate")
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=["SaaS job orchestration candidate requires a SaaS case session candidate."],
        )

    invalid_session_reason = _validate_session(session)
    if invalid_session_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=invalid_session_reason,
            notes=["SaaS case session candidate is invalid for job orchestration."],
        )

    requested_job_kind = _clean_required_ref(orchestration_input.get("requested_job_kind"))
    if requested_job_kind is None:
        return _result(
            status="BLOCKED_MISSING_JOB_KIND",
            blocked_reason="requested_job_kind_required",
            notes=["SaaS job orchestration candidate requires requested_job_kind."],
        )
    if requested_job_kind not in ALLOWED_REQUESTED_JOB_KINDS:
        return _result(
            status="BLOCKED_UNSUPPORTED_JOB_KIND",
            blocked_reason="requested_job_kind_not_supported",
            notes=["Requested job kind is not supported by this contract."],
        )

    chain_refs = _clean_chain_refs(orchestration_input.get("autonomous_chain_candidate_refs", {}))
    file_intake = orchestration_input.get("saas_file_intake_candidate")

    file_intake_ref: str | None = None
    if requested_job_kind == INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE:
        if not isinstance(file_intake, dict) or not file_intake:
            return _result(
                status="BLOCKED_MISSING_JOB_INPUT_REFS",
                blocked_reason="saas_file_intake_candidate_required_for_initial_file_intake",
                notes=["Initial file intake processing requires a SaaS file intake candidate."],
            )
        invalid_file_intake_reason = _validate_file_intake(file_intake, session)
        if invalid_file_intake_reason is not None:
            return _result(
                status="BLOCKED_MISSING_JOB_INPUT_REFS",
                blocked_reason=invalid_file_intake_reason,
                notes=["SaaS file intake candidate is invalid for job orchestration."],
            )
        file_intake_ref = _source_file_intake_ref(file_intake)

    if requested_job_kind == AUTONOMOUS_RERUN_PROCESSING_CANDIDATE:
        if "autonomous_rerun_candidate_ref" not in chain_refs:
            return _result(
                status="BLOCKED_MISSING_JOB_INPUT_REFS",
                blocked_reason="autonomous_rerun_candidate_ref_required",
                notes=["Autonomous rerun processing requires autonomous_rerun_candidate_ref."],
            )

    if requested_job_kind == OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE:
        if "owner_delivery_packet_ref" not in chain_refs:
            return _result(
                status="BLOCKED_MISSING_JOB_INPUT_REFS",
                blocked_reason="owner_delivery_packet_ref_required",
                notes=["Owner delivery packet refresh requires owner_delivery_packet_ref."],
            )

    if not chain_refs and requested_job_kind != INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE:
        return _result(
            status="BLOCKED_MISSING_JOB_INPUT_REFS",
            blocked_reason="autonomous_chain_candidate_refs_required",
            notes=["Requested job kind requires autonomous chain candidate refs."],
        )

    owner_ref = str(session["owner_ref"])
    case_ref = str(session["case_ref"])

    candidate: Service1SaasJobOrchestrationCandidateV1 = {
        "job_kind": JOB_KIND,
        "requested_job_kind": requested_job_kind,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": _source_session_ref(session),
        "source_file_intake_ref": file_intake_ref,
        "autonomous_chain_candidate_refs": dict(chain_refs),
        "planned_job_steps": _planned_job_steps(requested_job_kind),
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
        saas_job_orchestration_candidate=candidate,
        notes=["SaaS job orchestration candidate created without execution, worker, queue, pipeline, runner, API, or runtime."],
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


def _validate_file_intake(file_intake: dict[str, object], session: dict[str, object]) -> str | None:
    if file_intake.get("intake_kind") != FILE_INTAKE_KIND:
        return "file_intake_kind_must_be_saas_file_intake_candidate"
    if file_intake.get("service_name") != SERVICE_NAME:
        return "file_intake_service_name_must_be_service_1"
    if file_intake.get("owner_ref") != session.get("owner_ref"):
        return "file_intake_owner_ref_must_match_session"
    if file_intake.get("case_ref") != session.get("case_ref"):
        return "file_intake_case_ref_must_match_session"
    if file_intake.get("api_exposed") is not False:
        return "file_intake_api_exposed_must_be_false"
    if file_intake.get("runtime_authorized") is not False:
        return "file_intake_runtime_authorized_must_be_false"
    if file_intake.get("job_authorized") is not False:
        return "file_intake_job_authorized_must_be_false"
    return None


def _planned_job_steps(requested_job_kind: str) -> list[str]:
    if requested_job_kind == INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE:
        return [
            "validate_session_candidate_refs",
            "validate_file_intake_candidate_refs",
            "prepare_file_processing_job_candidate",
        ]
    if requested_job_kind == AUTONOMOUS_RERUN_PROCESSING_CANDIDATE:
        return [
            "validate_session_candidate_refs",
            "validate_autonomous_rerun_candidate_ref",
            "prepare_rerun_processing_job_candidate",
        ]
    if requested_job_kind == OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE:
        return [
            "validate_session_candidate_refs",
            "validate_owner_delivery_packet_ref",
            "prepare_owner_delivery_refresh_job_candidate",
        ]
    return []


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _source_file_intake_ref(file_intake: dict[str, object]) -> str:
    for key in ("file_intake_ref", "evidence_ref_candidate", "file_ref"):
        value = file_intake.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_file_intake:unknown"


def _clean_chain_refs(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str) and key.strip() and isinstance(item, str) and item.strip()
    }


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _result(
    *,
    status: SaasJobOrchestrationStatusV1,
    saas_job_orchestration_candidate: Service1SaasJobOrchestrationCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1SaasJobOrchestrationResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "saas_job_orchestration_candidate": saas_job_orchestration_candidate,
        "blocked_reason": blocked_reason,
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "SESSION_KIND",
    "FILE_INTAKE_KIND",
    "JOB_KIND",
    "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
    "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE",
    "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE",
    "ALLOWED_REQUESTED_JOB_KINDS",
    "Service1SaasJobOrchestrationInputV1",
    "Service1SaasJobOrchestrationCandidateV1",
    "Service1SaasJobOrchestrationResultV1",
    "build_service_1_saas_job_orchestration_v1",
]
