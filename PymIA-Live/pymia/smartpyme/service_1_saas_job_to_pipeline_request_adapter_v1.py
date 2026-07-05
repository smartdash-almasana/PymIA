from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_SAAS_JOB_TO_PIPELINE_REQUEST_ADAPTER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_SAAS_JOB_STATUS: Final[str] = "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY"
READY_EXPLICIT_REQUEST_STATUS: Final[str] = "EXPLICIT_REQUEST_CANDIDATE_READY"
FINAL_EXECUTION_GATE_STATUS: Final[str] = "CLOSED_NOT_EXECUTABLE"
PIPELINE_REQUEST_POLICY: Final[str] = "SAAS_JOB_ADAPTER_V1"
SOURCE_REQUEST_KIND: Final[str] = "CANDIDATE_ONLY"

INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE: Final[str] = "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE"
AUTONOMOUS_RERUN_PROCESSING_CANDIDATE: Final[str] = "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE"

_ALLOWED_JOB_KINDS: Final[tuple[str, ...]] = (
    INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
    AUTONOMOUS_RERUN_PROCESSING_CANDIDATE,
)

_ALLOWED_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)

AdapterStatusV1 = Literal[
    "ADAPTER_INPUTS_READY",
    "BLOCKED_MISSING_SAAS_JOB",
    "BLOCKED_INVALID_SAAS_JOB",
    "BLOCKED_UNSUPPORTED_JOB_KIND",
    "BLOCKED_MISSING_EXPLICIT_REQUESTS",
    "BLOCKED_INVALID_EXPLICIT_REQUEST",
    "BLOCKED_UNSAFE_FLAGS",
    "BLOCKED_MISSING_INPUTS",
    "UNKNOWN",
]


class Service1SaasJobToPipelineRequestAdapterInputV1(TypedDict):
    saas_job_orchestration_status: str
    saas_job_orchestration_candidate: dict[str, Any] | None
    explicit_request_status: str
    explicit_tool_request_candidate: list[dict[str, Any]]
    allowed_tool_refs: list[str]
    case_truth_status: str | None
    missing_inputs: list[str]
    unsafe_flags: list[str]
    notes: list[str]


class Service1ExplicitToPipelineGateInputV1(TypedDict):
    explicit_request_status: str
    explicit_tool_request_candidate: list[dict[str, Any]]
    allowed_tool_refs: list[str]
    final_execution_gate_status: str
    pipeline_request_policy: str


class Service1SaasJobToPipelineRequestAdapterResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: AdapterStatusV1
    explicit_to_pipeline_gate_input: Service1ExplicitToPipelineGateInputV1 | None
    pipeline_execution_gate_input_required_later: bool
    blocked_reason: str | None
    runtime_authorized: Literal[False]
    execution_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    delivery_authorized: Literal[False]
    notes: list[str]


def build_service_1_saas_job_to_pipeline_request_adapter_v1(
    adapter_input: Service1SaasJobToPipelineRequestAdapterInputV1,
) -> Service1SaasJobToPipelineRequestAdapterResultV1:
    """Prepare explicit-request gate input from a SaaS job candidate.

    This adapter does not call gates, build pipeline tool requests, authorize
    execution, call runners, perform I/O, expose APIs, persist state, or invoke
    models. It only validates candidate lineage and prepares the next gate input.
    """
    job_candidate = adapter_input.get("saas_job_orchestration_candidate")
    if not isinstance(job_candidate, dict) or not job_candidate:
        return _result(
            status="BLOCKED_MISSING_SAAS_JOB",
            blocked_reason="saas_job_orchestration_candidate_required",
            notes=["SaaS job orchestration candidate is required."],
        )

    if adapter_input.get("saas_job_orchestration_status") != READY_SAAS_JOB_STATUS:
        return _result(
            status="BLOCKED_INVALID_SAAS_JOB",
            blocked_reason="saas_job_orchestration_status_not_ready",
            notes=["SaaS job orchestration status is not ready."],
        )

    invalid_job_reason = _validate_job_candidate(job_candidate)
    if invalid_job_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SAAS_JOB",
            blocked_reason=invalid_job_reason,
            notes=["SaaS job orchestration candidate is invalid for adapter V1."],
        )

    requested_job_kind = str(job_candidate.get("requested_job_kind", ""))
    if requested_job_kind not in _ALLOWED_JOB_KINDS:
        return _result(
            status="BLOCKED_UNSUPPORTED_JOB_KIND",
            blocked_reason="requested_job_kind_not_supported_by_adapter_v1",
            notes=["Requested job kind is not supported by adapter V1."],
        )

    if _list_has_values(adapter_input.get("unsafe_flags", [])):
        return _result(
            status="BLOCKED_UNSAFE_FLAGS",
            blocked_reason="unsafe_flags_present",
            notes=["Unsafe flags block adapter handoff."],
        )

    if _list_has_values(adapter_input.get("missing_inputs", [])):
        return _result(
            status="BLOCKED_MISSING_INPUTS",
            blocked_reason="missing_inputs_present",
            notes=["Missing inputs block adapter handoff."],
        )

    explicit_candidates = list(adapter_input.get("explicit_tool_request_candidate", []))
    if not explicit_candidates:
        return _result(
            status="BLOCKED_MISSING_EXPLICIT_REQUESTS",
            blocked_reason="explicit_tool_request_candidate_required",
            notes=["Explicit tool request candidates are required."],
        )

    if adapter_input.get("explicit_request_status") != READY_EXPLICIT_REQUEST_STATUS:
        return _result(
            status="BLOCKED_MISSING_EXPLICIT_REQUESTS",
            blocked_reason="explicit_request_status_not_ready",
            notes=["Explicit request status is not ready."],
        )

    allowed_tool_refs = [str(ref) for ref in adapter_input.get("allowed_tool_refs", [])]
    for candidate in explicit_candidates:
        invalid_explicit_reason = _validate_explicit_candidate(
            candidate=candidate,
            allowed_tool_refs=allowed_tool_refs,
            job_candidate=job_candidate,
        )
        if invalid_explicit_reason is not None:
            return _result(
                status="BLOCKED_INVALID_EXPLICIT_REQUEST",
                blocked_reason=invalid_explicit_reason,
                notes=["Explicit request candidate is invalid for adapter V1."],
            )

    gate_input: Service1ExplicitToPipelineGateInputV1 = {
        "explicit_request_status": READY_EXPLICIT_REQUEST_STATUS,
        "explicit_tool_request_candidate": copy_candidates(explicit_candidates),
        "allowed_tool_refs": list(allowed_tool_refs),
        "final_execution_gate_status": FINAL_EXECUTION_GATE_STATUS,
        "pipeline_request_policy": PIPELINE_REQUEST_POLICY,
    }

    return _result(
        status="ADAPTER_INPUTS_READY",
        explicit_to_pipeline_gate_input=gate_input,
        pipeline_execution_gate_input_required_later=True,
        notes=["Adapter prepared explicit_to_pipeline_gate_input only; pipeline execution gate input requires later gate output."],
    )


def _validate_job_candidate(job_candidate: dict[str, Any]) -> str | None:
    if job_candidate.get("job_kind") != "SAAS_JOB_ORCHESTRATION_CANDIDATE":
        return "job_kind_must_be_saas_job_orchestration_candidate"
    if job_candidate.get("service_name") != SERVICE_NAME:
        return "job_service_name_must_be_service_1"
    if _clean_required_ref(job_candidate.get("owner_ref")) is None:
        return "job_owner_ref_required"
    if _clean_required_ref(job_candidate.get("case_ref")) is None:
        return "job_case_ref_required"
    for flag in (
        "worker_authorized",
        "queue_authorized",
        "async_execution_authorized",
        "pipeline_authorized",
        "runner_authorized",
        "runtime_authorized",
        "api_exposed",
    ):
        if job_candidate.get(flag) is not False:
            return f"job_{flag}_must_be_false"
    return None


def _validate_explicit_candidate(
    *,
    candidate: dict[str, Any],
    allowed_tool_refs: list[str],
    job_candidate: dict[str, Any],
) -> str | None:
    tool_ref = candidate.get("tool_ref")
    if not isinstance(tool_ref, str) or not tool_ref.strip():
        return "candidate_tool_ref_required"
    if tool_ref not in _ALLOWED_TOOL_REFS or tool_ref not in allowed_tool_refs:
        return "candidate_tool_ref_not_allowlisted"
    if candidate.get("request_kind") != SOURCE_REQUEST_KIND:
        return "request_kind_not_candidate_only"
    if candidate.get("executable") is not False:
        return "explicit_request_candidate_must_not_be_executable"
    if not _dict_has_values(candidate.get("input_refs", {})):
        return "explicit_request_input_refs_required"
    owner_ref = candidate.get("owner_ref")
    if isinstance(owner_ref, str) and owner_ref.strip() and owner_ref != job_candidate.get("owner_ref"):
        return "explicit_request_owner_ref_conflicts_with_job"
    case_ref = candidate.get("case_ref")
    if isinstance(case_ref, str) and case_ref.strip() and case_ref != job_candidate.get("case_ref"):
        return "explicit_request_case_ref_conflicts_with_job"
    return None


def _result(
    *,
    status: AdapterStatusV1,
    explicit_to_pipeline_gate_input: Service1ExplicitToPipelineGateInputV1 | None = None,
    pipeline_execution_gate_input_required_later: bool = False,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1SaasJobToPipelineRequestAdapterResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "explicit_to_pipeline_gate_input": explicit_to_pipeline_gate_input,
        "pipeline_execution_gate_input_required_later": pipeline_execution_gate_input_required_later,
        "blocked_reason": blocked_reason,
        "runtime_authorized": False,
        "execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "delivery_authorized": False,
        "notes": list(notes or []),
    }


def copy_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{str(key): value for key, value in candidate.items()} for candidate in candidates]


def _list_has_values(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return any(isinstance(item, str) and bool(item.strip()) for item in value)


def _dict_has_values(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return any(isinstance(item, str) and bool(item.strip()) for item in value.values())


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "READY_SAAS_JOB_STATUS",
    "READY_EXPLICIT_REQUEST_STATUS",
    "FINAL_EXECUTION_GATE_STATUS",
    "PIPELINE_REQUEST_POLICY",
    "SOURCE_REQUEST_KIND",
    "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
    "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE",
    "Service1SaasJobToPipelineRequestAdapterInputV1",
    "Service1ExplicitToPipelineGateInputV1",
    "Service1SaasJobToPipelineRequestAdapterResultV1",
    "build_service_1_saas_job_to_pipeline_request_adapter_v1",
]
