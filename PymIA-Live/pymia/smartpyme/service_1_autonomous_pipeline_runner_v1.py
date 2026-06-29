from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Literal, NotRequired, TypedDict

from pymia.smartpyme.service_1_pipeline_v1 import Service1PipelineToolRequestV1, Service1PipelineV1, run_service_1_pipeline_v1

SCHEMA_VERSION: Final[str] = "S1_AUTONOMOUS_PIPELINE_RUNNER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_EXECUTION_STATUS: Final[str] = "EXECUTION_AUTHORIZED"
AUTHORIZED_REQUEST_KIND: Final[str] = "AUTHORIZED_PIPELINE_TOOL_REQUEST"

AutonomousPipelineRunnerStatusV1 = Literal[
    "PIPELINE_RUN_COMPLETED",
    "BLOCKED_EXECUTION_NOT_AUTHORIZED",
    "BLOCKED_PIPELINE_NOT_AUTHORIZED",
    "BLOCKED_UNSAFE_TO_CALL_PIPELINE",
    "BLOCKED_NO_REQUESTS",
    "PIPELINE_RUN_FAILED",
    "UNKNOWN",
]


class Service1AutonomousPipelineRunnerInputV1(TypedDict):
    execution_gate_status: str
    execution_authorized: bool
    pipeline_authorized: bool
    safe_to_call_pipeline: bool
    authorized_pipeline_tool_requests: list[dict[str, Any]]
    case_id: str | None
    run_id: str | None
    notes: list[str]
    output_dir: NotRequired[str]


class Service1AutonomousPipelineRunnerResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: AutonomousPipelineRunnerStatusV1
    pipeline_run_result: Service1PipelineV1 | None
    blocked_reason: str | None
    executed_tool_refs: list[str]
    runtime_authorized: bool
    pipeline_called: bool
    delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    notes: list[str]


def run_service_1_autonomous_pipeline_runner_v1(
    runner_input: Service1AutonomousPipelineRunnerInputV1,
) -> Service1AutonomousPipelineRunnerResultV1:
    """Run the Servicio 1 pipeline only after prior autonomous gates authorize it.

    This runner is intentionally narrow: it does not decide tools, build requests,
    map inputs, touch CLI, authorize delivery, or handle conversational interfaces.
    It only submits already authorized pipeline tool requests to the existing
    deterministic pipeline.
    """
    if runner_input.get("execution_gate_status") != READY_EXECUTION_STATUS:
        return _result(
            status="BLOCKED_EXECUTION_NOT_AUTHORIZED",
            blocked_reason="execution_gate_status_not_authorized",
            notes=["Autonomous runner requires EXECUTION_AUTHORIZED."],
        )

    if runner_input.get("execution_authorized") is not True:
        return _result(
            status="BLOCKED_EXECUTION_NOT_AUTHORIZED",
            blocked_reason="execution_authorized_false",
            notes=["execution_authorized must be true before pipeline call."],
        )

    if runner_input.get("pipeline_authorized") is not True:
        return _result(
            status="BLOCKED_PIPELINE_NOT_AUTHORIZED",
            blocked_reason="pipeline_authorized_false",
            notes=["pipeline_authorized must be true before pipeline call."],
        )

    if runner_input.get("safe_to_call_pipeline") is not True:
        return _result(
            status="BLOCKED_UNSAFE_TO_CALL_PIPELINE",
            blocked_reason="safe_to_call_pipeline_false",
            notes=["safe_to_call_pipeline must be true before pipeline call."],
        )

    authorized_requests = list(runner_input.get("authorized_pipeline_tool_requests", []))
    if not authorized_requests:
        return _result(
            status="BLOCKED_NO_REQUESTS",
            blocked_reason="authorized_pipeline_tool_requests_empty",
            notes=["No authorized pipeline tool requests were provided."],
        )

    output_dir = runner_input.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir.strip():
        return _result(
            status="UNKNOWN",
            blocked_reason="output_dir_required",
            notes=["Autonomous runner requires output_dir because the existing pipeline writes delivery artifacts."],
        )

    try:
        pipeline_tool_requests = _to_pipeline_tool_requests(authorized_requests)
    except ValueError as exc:
        return _result(
            status="PIPELINE_RUN_FAILED",
            blocked_reason=str(exc),
            pipeline_called=False,
            notes=["Authorized request payload could not be converted to pipeline tool requests."],
        )

    try:
        pipeline_run_result = run_service_1_pipeline_v1(
            tool_requests=pipeline_tool_requests,
            output_dir=Path(output_dir),
        )
    except Exception as exc:  # pragma: no cover - branch covered by tests with monkeypatch
        return _result(
            status="PIPELINE_RUN_FAILED",
            blocked_reason=f"pipeline_exception:{type(exc).__name__}:{exc}",
            pipeline_called=True,
            runtime_authorized=True,
            notes=["Pipeline call failed inside autonomous runner."],
        )

    return _result(
        status="PIPELINE_RUN_COMPLETED",
        pipeline_run_result=pipeline_run_result,
        executed_tool_refs=list(pipeline_run_result.get("executed_tool_refs", [])),
        pipeline_called=True,
        runtime_authorized=True,
        notes=["Pipeline completed through autonomous runner."],
    )


def _to_pipeline_tool_requests(
    authorized_requests: list[dict[str, Any]],
) -> list[Service1PipelineToolRequestV1]:
    pipeline_tool_requests: list[Service1PipelineToolRequestV1] = []
    for request in authorized_requests:
        if not isinstance(request, dict):
            raise ValueError("authorized_pipeline_tool_request_must_be_dict")
        if request.get("request_kind") != AUTHORIZED_REQUEST_KIND:
            raise ValueError("authorized_request_kind_required")
        if request.get("executable") is not True:
            raise ValueError("authorized_request_must_be_executable")
        tool_ref = request.get("tool_ref")
        inputs = request.get("inputs")
        if not isinstance(tool_ref, str) or not tool_ref.strip():
            raise ValueError("authorized_request_tool_ref_required")
        if not isinstance(inputs, dict) or not inputs:
            raise ValueError("authorized_request_inputs_required")
        pipeline_tool_requests.append(
            {
                "tool_ref": tool_ref,  # type: ignore[typeddict-item]
                "inputs": dict(inputs),
            }
        )
    return pipeline_tool_requests


def _result(
    *,
    status: AutonomousPipelineRunnerStatusV1,
    pipeline_run_result: Service1PipelineV1 | None = None,
    blocked_reason: str | None = None,
    executed_tool_refs: list[str] | None = None,
    runtime_authorized: bool = False,
    pipeline_called: bool = False,
    notes: list[str] | None = None,
) -> Service1AutonomousPipelineRunnerResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "pipeline_run_result": pipeline_run_result,
        "blocked_reason": blocked_reason,
        "executed_tool_refs": list(executed_tool_refs or []),
        "runtime_authorized": runtime_authorized,
        "pipeline_called": pipeline_called,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "READY_EXECUTION_STATUS",
    "AUTHORIZED_REQUEST_KIND",
    "Service1AutonomousPipelineRunnerInputV1",
    "Service1AutonomousPipelineRunnerResultV1",
    "run_service_1_autonomous_pipeline_runner_v1",
]
