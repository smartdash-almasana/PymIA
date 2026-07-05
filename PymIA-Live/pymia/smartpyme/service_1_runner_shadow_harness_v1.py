from __future__ import annotations

from typing import Any, Final, Literal, NotRequired, TypedDict

SCHEMA_VERSION: Final[str] = "S1_RUNNER_SHADOW_HARNESS_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_EXECUTION_STATUS: Final[str] = "EXECUTION_AUTHORIZED"
AUTHORIZED_REQUEST_KIND: Final[str] = "AUTHORIZED_PIPELINE_TOOL_REQUEST"

RunnerShadowHarnessStatusV1 = Literal[
    "SHADOW_RUNNER_READY",
    "BLOCKED_EXECUTION_NOT_AUTHORIZED",
    "BLOCKED_PIPELINE_NOT_AUTHORIZED",
    "BLOCKED_UNSAFE_TO_CALL_PIPELINE",
    "BLOCKED_EMPTY_REQUESTS",
    "BLOCKED_INVALID_REQUEST",
    "UNKNOWN",
]


class Service1RunnerShadowHarnessInputV1(TypedDict):
    execution_gate_status: str
    execution_authorized: bool
    pipeline_authorized: bool
    safe_to_call_pipeline: bool
    authorized_pipeline_tool_requests: list[dict[str, Any]]
    case_id: str | None
    run_id: str | None
    notes: list[str]
    runtime_authorized: NotRequired[bool]
    owner_delivery_authorized: NotRequired[bool]
    autonomous_delivery_authorized: NotRequired[bool]


class Service1RunnerShadowProcessedRequestV1(TypedDict):
    tool_ref: str
    inputs: dict[str, Any]
    source_pipeline_request_ref: str | None
    request_kind: Literal["SHADOW_PROCESSED_PIPELINE_TOOL_REQUEST"]
    executable: Literal[False]
    pipeline_called: Literal[False]


class Service1RunnerShadowHarnessResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: RunnerShadowHarnessStatusV1
    blocked_reason: str | None
    case_id: str | None
    run_id: str | None
    shadow_run_authorized: bool
    runtime_authorized: Literal[False]
    pipeline_called: Literal[False]
    delivery_authorized: Literal[False]
    owner_delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    shadow_processed_requests: list[Service1RunnerShadowProcessedRequestV1]
    executed_tool_refs: list[str]
    notes: list[str]


def build_service_1_runner_shadow_harness_v1(
    harness_input: Service1RunnerShadowHarnessInputV1,
) -> Service1RunnerShadowHarnessResultV1:
    """Validate execution-gate output in a deterministic shadow harness.

    This module does not import or call the real autonomous runner, pipeline,
    delivery, storage, API, worker, CLI, or LLM layers. It only validates that an
    execution-gate result can be represented as a safe shadow execution signal.
    """
    if harness_input.get("execution_gate_status") != READY_EXECUTION_STATUS:
        return _result(
            status="BLOCKED_EXECUTION_NOT_AUTHORIZED",
            blocked_reason="execution_gate_status_not_authorized",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["Shadow harness requires EXECUTION_AUTHORIZED."],
        )

    if harness_input.get("execution_authorized") is not True:
        return _result(
            status="BLOCKED_EXECUTION_NOT_AUTHORIZED",
            blocked_reason="execution_authorized_false",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["execution_authorized must be true for shadow harness."],
        )

    if harness_input.get("pipeline_authorized") is not True:
        return _result(
            status="BLOCKED_PIPELINE_NOT_AUTHORIZED",
            blocked_reason="pipeline_authorized_false",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["pipeline_authorized must be true for shadow harness."],
        )

    if harness_input.get("safe_to_call_pipeline") is not True:
        return _result(
            status="BLOCKED_UNSAFE_TO_CALL_PIPELINE",
            blocked_reason="safe_to_call_pipeline_false",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["safe_to_call_pipeline must be true for shadow harness."],
        )

    if harness_input.get("runtime_authorized") is True:
        return _result(
            status="BLOCKED_INVALID_REQUEST",
            blocked_reason="runtime_authorized_must_remain_false_for_shadow",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["Shadow harness cannot accept runtime_authorized=true."],
        )

    if harness_input.get("owner_delivery_authorized") is True or harness_input.get("autonomous_delivery_authorized") is True:
        return _result(
            status="BLOCKED_INVALID_REQUEST",
            blocked_reason="delivery_authorization_must_remain_false_for_shadow",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["Shadow harness cannot authorize owner or autonomous delivery."],
        )

    authorized_requests = list(harness_input.get("authorized_pipeline_tool_requests", []))
    if not authorized_requests:
        return _result(
            status="BLOCKED_EMPTY_REQUESTS",
            blocked_reason="authorized_pipeline_tool_requests_empty",
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["No authorized pipeline tool requests were provided."],
        )

    try:
        shadow_processed_requests = _to_shadow_processed_requests(authorized_requests)
    except ValueError as exc:
        return _result(
            status="BLOCKED_INVALID_REQUEST",
            blocked_reason=str(exc),
            case_id=harness_input.get("case_id"),
            run_id=harness_input.get("run_id"),
            notes=["Authorized request payload is invalid for shadow harness."],
        )

    return _result(
        status="SHADOW_RUNNER_READY",
        blocked_reason=None,
        case_id=harness_input.get("case_id"),
        run_id=harness_input.get("run_id"),
        shadow_run_authorized=True,
        shadow_processed_requests=shadow_processed_requests,
        executed_tool_refs=[request["tool_ref"] for request in shadow_processed_requests],
        notes=list(harness_input.get("notes", [])) + ["Shadow harness validated authorized pipeline tool requests without calling pipeline."],
    )


def _to_shadow_processed_requests(
    authorized_requests: list[dict[str, Any]],
) -> list[Service1RunnerShadowProcessedRequestV1]:
    shadow_processed_requests: list[Service1RunnerShadowProcessedRequestV1] = []
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
        source_pipeline_request_ref = request.get("source_pipeline_request_ref")
        shadow_processed_requests.append(
            {
                "tool_ref": tool_ref,
                "inputs": dict(inputs),
                "source_pipeline_request_ref": source_pipeline_request_ref if isinstance(source_pipeline_request_ref, str) else None,
                "request_kind": "SHADOW_PROCESSED_PIPELINE_TOOL_REQUEST",
                "executable": False,
                "pipeline_called": False,
            }
        )
    return shadow_processed_requests


def _result(
    *,
    status: RunnerShadowHarnessStatusV1,
    blocked_reason: str | None,
    case_id: str | None,
    run_id: str | None,
    shadow_run_authorized: bool = False,
    shadow_processed_requests: list[Service1RunnerShadowProcessedRequestV1] | None = None,
    executed_tool_refs: list[str] | None = None,
    notes: list[str] | None = None,
) -> Service1RunnerShadowHarnessResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "blocked_reason": blocked_reason,
        "case_id": case_id,
        "run_id": run_id,
        "shadow_run_authorized": shadow_run_authorized,
        "runtime_authorized": False,
        "pipeline_called": False,
        "delivery_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "shadow_processed_requests": list(shadow_processed_requests or []),
        "executed_tool_refs": list(executed_tool_refs or []),
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "READY_EXECUTION_STATUS",
    "AUTHORIZED_REQUEST_KIND",
    "Service1RunnerShadowHarnessInputV1",
    "Service1RunnerShadowHarnessResultV1",
    "Service1RunnerShadowProcessedRequestV1",
    "build_service_1_runner_shadow_harness_v1",
]
