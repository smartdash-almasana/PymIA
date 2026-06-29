from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_PIPELINE_REQUEST_EXECUTION_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_PIPELINE_CANDIDATE_STATUS: Final[str] = "PIPELINE_REQUEST_CANDIDATE_READY"
READY_CASE_TRUTH_STATUS: Final[str] = "READY_FOR_TOOL_PLANNING"
AUTHORIZED_REQUEST_KIND: Final[str] = "AUTHORIZED_PIPELINE_TOOL_REQUEST"

PipelineRequestExecutionGateStatusV1 = Literal[
    "EXECUTION_AUTHORIZED",
    "BLOCKED_CANDIDATE_NOT_READY",
    "BLOCKED_UNSAFE_FLAGS",
    "BLOCKED_UNSUPPORTED_TOOL",
    "BLOCKED_MISSING_INPUTS",
    "UNKNOWN",
]

_ALLOWED_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)


class Service1PipelineRequestExecutionGateInputV1(TypedDict):
    pipeline_candidate_status: str
    pipeline_tool_requests: list[dict[str, Any]]
    allowed_tool_refs: list[str]
    missing_inputs: list[str]
    unsafe_flags: list[str]
    case_truth_status: str | None
    notes: list[str]


class Service1AuthorizedPipelineToolRequestV1(TypedDict):
    tool_ref: str
    inputs: dict[str, Any]
    source_pipeline_request_ref: str
    request_kind: Literal["AUTHORIZED_PIPELINE_TOOL_REQUEST"]
    executable: Literal[True]


class Service1PipelineRequestExecutionGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: PipelineRequestExecutionGateStatusV1
    execution_authorized: bool
    pipeline_authorized: bool
    safe_to_call_pipeline: bool
    authorized_pipeline_tool_requests: list[Service1AuthorizedPipelineToolRequestV1]
    blocked_reason: str | None
    missing_inputs: list[str]
    runtime_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    notes: list[str]


def build_service_1_pipeline_request_execution_gate_v1(
    gate_input: Service1PipelineRequestExecutionGateInputV1,
) -> Service1PipelineRequestExecutionGateResultV1:
    """Authorize or block pipeline request candidates before autonomous execution.

    This pure gate does not execute tools, call pipeline runtime, touch CLI,
    create delivery artifacts, persist state, call model runtimes, or authorize delivery.
    It only decides whether previously built pipeline request candidates are safe
    for a future runner to submit to the existing pipeline.
    """
    pipeline_candidate_status = str(gate_input.get("pipeline_candidate_status") or "")
    if pipeline_candidate_status != READY_PIPELINE_CANDIDATE_STATUS:
        return _result(
            status="BLOCKED_CANDIDATE_NOT_READY",
            blocked_reason="pipeline_candidate_status_not_ready",
            notes=["Pipeline execution requires PIPELINE_REQUEST_CANDIDATE_READY."],
        )

    case_truth_status = gate_input.get("case_truth_status")
    if case_truth_status is not None and case_truth_status != READY_CASE_TRUTH_STATUS:
        return _result(
            status="BLOCKED_CANDIDATE_NOT_READY",
            blocked_reason="case_truth_status_not_ready",
            notes=["Pipeline execution requires READY_FOR_TOOL_PLANNING when case_truth_status is provided."],
        )

    unsafe_flags = _clean_list(gate_input.get("unsafe_flags", []))
    if unsafe_flags:
        return _result(
            status="BLOCKED_UNSAFE_FLAGS",
            blocked_reason="unsafe_flags_present",
            notes=["Unsafe flags block autonomous pipeline execution."],
        )

    missing_inputs = _clean_list(gate_input.get("missing_inputs", []))
    if missing_inputs:
        return _result(
            status="BLOCKED_MISSING_INPUTS",
            blocked_reason="missing_inputs_present",
            missing_inputs=missing_inputs,
            notes=["Missing inputs block autonomous pipeline execution."],
        )

    candidate_requests = list(gate_input.get("pipeline_tool_requests", []))
    if not candidate_requests:
        return _result(
            status="UNKNOWN",
            blocked_reason="missing_pipeline_tool_requests",
            notes=["No pipeline_tool_requests were provided."],
        )

    allowed_tool_refs = set(_clean_list(gate_input.get("allowed_tool_refs", [])))
    authorized_requests: list[Service1AuthorizedPipelineToolRequestV1] = []

    for candidate in candidate_requests:
        if not isinstance(candidate, dict):
            return _result(
                status="UNKNOWN",
                blocked_reason="invalid_pipeline_tool_request_candidate",
                notes=["Every pipeline tool request candidate must be a dict."],
            )

        tool_ref = candidate.get("tool_ref")
        if not isinstance(tool_ref, str) or not tool_ref.strip():
            return _result(
                status="UNKNOWN",
                blocked_reason="missing_candidate_tool_ref",
                notes=["Every pipeline tool request candidate requires a tool_ref."],
            )
        tool_ref = tool_ref.strip()

        if tool_ref not in _ALLOWED_TOOL_REFS or tool_ref not in allowed_tool_refs:
            return _result(
                status="BLOCKED_UNSUPPORTED_TOOL",
                blocked_reason="candidate_tool_ref_not_allowlisted",
                notes=[f"Candidate tool ref is not allowlisted: {tool_ref}"],
            )

        inputs = candidate.get("inputs")
        if not isinstance(inputs, dict) or not inputs:
            return _result(
                status="BLOCKED_MISSING_INPUTS",
                blocked_reason="candidate_inputs_missing",
                missing_inputs=[tool_ref],
                notes=["Every authorized pipeline request requires non-empty inputs."],
            )

        authorized_requests.append(
            {
                "tool_ref": tool_ref,
                "inputs": dict(inputs),
                "source_pipeline_request_ref": _source_pipeline_request_ref(tool_ref=tool_ref, candidate=candidate),
                "request_kind": AUTHORIZED_REQUEST_KIND,
                "executable": True,
            }
        )

    return _result(
        status="EXECUTION_AUTHORIZED",
        execution_authorized=True,
        pipeline_authorized=True,
        safe_to_call_pipeline=True,
        authorized_pipeline_tool_requests=authorized_requests,
        notes=["Pipeline request candidates authorized for future autonomous runner submission."],
    )


def _source_pipeline_request_ref(*, tool_ref: str, candidate: dict[str, Any]) -> str:
    for key in ("pipeline_request_ref", "source_pipeline_request_ref", "source_explicit_request_ref"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"pipeline_request_candidate:{tool_ref}"


def _clean_list(values: list[Any]) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _result(
    *,
    status: PipelineRequestExecutionGateStatusV1,
    execution_authorized: bool = False,
    pipeline_authorized: bool = False,
    safe_to_call_pipeline: bool = False,
    authorized_pipeline_tool_requests: list[Service1AuthorizedPipelineToolRequestV1] | None = None,
    blocked_reason: str | None = None,
    missing_inputs: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1PipelineRequestExecutionGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "execution_authorized": execution_authorized,
        "pipeline_authorized": pipeline_authorized,
        "safe_to_call_pipeline": safe_to_call_pipeline,
        "authorized_pipeline_tool_requests": list(authorized_pipeline_tool_requests or []),
        "blocked_reason": blocked_reason,
        "missing_inputs": list(missing_inputs or []),
        "runtime_authorized": False,
        "autonomous_delivery_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "READY_PIPELINE_CANDIDATE_STATUS",
    "READY_CASE_TRUTH_STATUS",
    "AUTHORIZED_REQUEST_KIND",
    "Service1PipelineRequestExecutionGateInputV1",
    "Service1AuthorizedPipelineToolRequestV1",
    "Service1PipelineRequestExecutionGateResultV1",
    "build_service_1_pipeline_request_execution_gate_v1",
]

