from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_candidate_tools_to_controlled_execution_bridge_v1 import (
    CONTROLLED_EXECUTION_CANDIDATES_READY,
    NEEDS_EVIDENCE as CONTROLLED_EXECUTION_NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS as CONTROLLED_EXECUTION_NO_CANDIDATE_TOOLS,
    Service1CandidateToolsToControlledExecutionBridgeResultV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_CONTROLLED_EXECUTION_CANDIDATES_TO_SUPERVISED_DRY_RUN_PLAN_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

SUPERVISED_DRY_RUN_PLAN_READY: Final[str] = "SUPERVISED_DRY_RUN_PLAN_READY"
NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
NO_CANDIDATE_TOOLS: Final[str] = "NO_CANDIDATE_TOOLS"
BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES: Final[str] = (
    "BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES"
)
BLOCKED_UNSAFE_RUNTIME_FLAGS: Final[str] = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
UNKNOWN: Final[str] = "UNKNOWN"

SupervisedDryRunPlanStatusV1 = Literal[
    "SUPERVISED_DRY_RUN_PLAN_READY",
    "NEEDS_EVIDENCE",
    "NO_CANDIDATE_TOOLS",
    "BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES",
    "BLOCKED_UNSAFE_RUNTIME_FLAGS",
    "UNKNOWN",
]


@dataclass(frozen=True)
class Service1SupervisedDryRunStepV1:
    step_order: int
    step_ref: str
    tool_ref: str
    source_signal_name: str
    source_file_name: str
    source_headers: tuple[str, ...]
    operator_ref: str
    execution_window_ref: str
    dry_run_required: bool
    operator_action: str
    required_manual_confirmations: tuple[str, ...]
    limitations: tuple[str, ...]
    execution_authorized: bool
    execution_executed: bool
    runtime_authorized: bool
    tool_execution_authorized: bool
    executable_tool_request_authorized: bool
    pipeline_authorized: bool
    delivery_authorized: bool
    autonomous_delivery_authorized: bool
    llm_authorized: bool


@dataclass(frozen=True)
class Service1SupervisedDryRunPlanResultV1:
    schema_version: str
    service_name: str
    status: SupervisedDryRunPlanStatusV1
    ready: bool
    case_ref: str
    source_file_name: str
    supervised_dry_run_plan_ref: str
    ordered_candidate_steps: tuple[Service1SupervisedDryRunStepV1, ...]
    operator_checklist: tuple[str, ...]
    required_manual_confirmations: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    dry_run_required: bool
    execution_authorized: bool
    execution_executed: bool
    runtime_authorized: bool
    tool_execution_authorized: bool
    executable_tool_requests_authorized: bool
    pipeline_authorized: bool
    delivery_authorized: bool
    autonomous_delivery_authorized: bool
    llm_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1(
    *,
    controlled_execution_candidates_result: Service1CandidateToolsToControlledExecutionBridgeResultV1,
    metadata: dict[str, Any] | None = None,
) -> Service1SupervisedDryRunPlanResultV1:
    """Build a supervised dry-run plan from prepared controlled execution candidates.

    This contract is pure. It does not execute tools, create executable tool
    requests, call pipelines, call CLI, write delivery artifacts, call LLM
    runtimes, or authorize real execution.
    """
    if not isinstance(
        controlled_execution_candidates_result,
        Service1CandidateToolsToControlledExecutionBridgeResultV1,
    ):
        return _result(
            status=UNKNOWN,
            ready=False,
            case_ref="",
            source_file_name="",
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=(
                "controlled_execution_candidates_result must be a Service1CandidateToolsToControlledExecutionBridgeResultV1",
            ),
            missing_requirements=(),
            metadata=metadata,
        )
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    unsafe_flags = _unsafe_flags(controlled_execution_candidates_result)
    if unsafe_flags:
        return _result(
            status=BLOCKED_UNSAFE_RUNTIME_FLAGS,
            ready=False,
            case_ref=controlled_execution_candidates_result.case_ref,
            source_file_name=controlled_execution_candidates_result.source_file_name,
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=unsafe_flags,
            missing_requirements=controlled_execution_candidates_result.missing_requirements,
            metadata=metadata,
        )

    if controlled_execution_candidates_result.status == CONTROLLED_EXECUTION_NEEDS_EVIDENCE:
        return _result(
            status=NEEDS_EVIDENCE,
            ready=False,
            case_ref=controlled_execution_candidates_result.case_ref,
            source_file_name=controlled_execution_candidates_result.source_file_name,
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=(),
            missing_requirements=controlled_execution_candidates_result.missing_requirements,
            metadata=metadata,
        )

    if controlled_execution_candidates_result.status == CONTROLLED_EXECUTION_NO_CANDIDATE_TOOLS:
        return _result(
            status=NO_CANDIDATE_TOOLS,
            ready=False,
            case_ref=controlled_execution_candidates_result.case_ref,
            source_file_name=controlled_execution_candidates_result.source_file_name,
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=(),
            missing_requirements=controlled_execution_candidates_result.missing_requirements,
            metadata=metadata,
        )

    if (
        controlled_execution_candidates_result.status != CONTROLLED_EXECUTION_CANDIDATES_READY
        or not controlled_execution_candidates_result.ready
        or controlled_execution_candidates_result.blocked_reasons
    ):
        return _result(
            status=BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES,
            ready=False,
            case_ref=controlled_execution_candidates_result.case_ref,
            source_file_name=controlled_execution_candidates_result.source_file_name,
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=controlled_execution_candidates_result.blocked_reasons
            or (f"controlled_execution_candidates_result status must be {CONTROLLED_EXECUTION_CANDIDATES_READY}",),
            missing_requirements=controlled_execution_candidates_result.missing_requirements,
            metadata=metadata,
        )

    if not controlled_execution_candidates_result.controlled_execution_candidates:
        return _result(
            status=NO_CANDIDATE_TOOLS,
            ready=False,
            case_ref=controlled_execution_candidates_result.case_ref,
            source_file_name=controlled_execution_candidates_result.source_file_name,
            ordered_candidate_steps=(),
            operator_checklist=(),
            required_manual_confirmations=(),
            blocked_reasons=(),
            missing_requirements=controlled_execution_candidates_result.missing_requirements,
            metadata=metadata,
        )

    sorted_candidates = tuple(
        sorted(
            controlled_execution_candidates_result.controlled_execution_candidates,
            key=lambda candidate: candidate.tool_ref,
        )
    )
    steps = tuple(
        _step_from_candidate(index=index, candidate=candidate)
        for index, candidate in enumerate(sorted_candidates, start=1)
    )
    manual_confirmations = _manual_confirmations(steps)
    checklist = _operator_checklist(steps)

    return _result(
        status=SUPERVISED_DRY_RUN_PLAN_READY,
        ready=True,
        case_ref=controlled_execution_candidates_result.case_ref,
        source_file_name=controlled_execution_candidates_result.source_file_name,
        ordered_candidate_steps=steps,
        operator_checklist=checklist,
        required_manual_confirmations=manual_confirmations,
        blocked_reasons=(),
        missing_requirements=controlled_execution_candidates_result.missing_requirements,
        metadata=metadata,
    )


def _step_from_candidate(*, index: int, candidate: Any) -> Service1SupervisedDryRunStepV1:
    return Service1SupervisedDryRunStepV1(
        step_order=index,
        step_ref=f"DRY_RUN_STEP_{index:03d}_{candidate.tool_ref}",
        tool_ref=candidate.tool_ref,
        source_signal_name=candidate.source_signal_name,
        source_file_name=candidate.source_file_name,
        source_headers=tuple(candidate.source_headers),
        operator_ref=candidate.operator_ref,
        execution_window_ref=candidate.execution_window_ref,
        dry_run_required=True,
        operator_action=(
            "Review the candidate tool, source headers, limitations, and manual confirmations. "
            "Do not execute the tool in this plan."
        ),
        required_manual_confirmations=(
            f"CONFIRM_OPERATOR:{candidate.operator_ref}",
            f"CONFIRM_EXECUTION_WINDOW:{candidate.execution_window_ref}",
            f"CONFIRM_DRY_RUN_ONLY:{candidate.tool_ref}",
            f"CONFIRM_SOURCE_HEADERS:{candidate.tool_ref}",
        ),
        limitations=tuple(candidate.limitations),
        execution_authorized=False,
        execution_executed=False,
        runtime_authorized=False,
        tool_execution_authorized=False,
        executable_tool_request_authorized=False,
        pipeline_authorized=False,
        delivery_authorized=False,
        autonomous_delivery_authorized=False,
        llm_authorized=False,
    )


def _manual_confirmations(
    steps: tuple[Service1SupervisedDryRunStepV1, ...],
) -> tuple[str, ...]:
    confirmations = [
        "CONFIRM_NO_REAL_EXECUTION",
        "CONFIRM_NO_PIPELINE_CALL",
        "CONFIRM_NO_DELIVERY_CREATION",
    ]
    for step in steps:
        confirmations.extend(step.required_manual_confirmations)
    return tuple(sorted(dict.fromkeys(confirmations)))


def _operator_checklist(
    steps: tuple[Service1SupervisedDryRunStepV1, ...],
) -> tuple[str, ...]:
    checklist = [
        "Verify that this is a dry-run plan only.",
        "Verify that no executable tool request is produced.",
        "Verify that no pipeline, CLI, delivery, API, or LLM runtime is called.",
    ]
    for step in steps:
        checklist.append(
            f"Step {step.step_order}: review {step.tool_ref} using source headers {', '.join(step.source_headers)}."
        )
    return tuple(checklist)


def _unsafe_flags(
    result: Service1CandidateToolsToControlledExecutionBridgeResultV1,
) -> tuple[str, ...]:
    unsafe = []
    for flag in (
        "execution_authorized",
        "execution_executed",
        "runtime_authorized",
        "tool_execution_authorized",
        "executable_tool_requests_authorized",
        "pipeline_authorized",
        "delivery_authorized",
        "autonomous_delivery_authorized",
        "llm_authorized",
    ):
        if getattr(result, flag) is True:
            unsafe.append(f"unsafe upstream flag is true: {flag}")
    for candidate in result.controlled_execution_candidates:
        for flag in (
            "execution_authorized",
            "execution_executed",
            "runtime_authorized",
            "tool_execution_authorized",
            "executable_tool_request_authorized",
            "pipeline_authorized",
            "delivery_authorized",
            "autonomous_delivery_authorized",
            "llm_authorized",
        ):
            if getattr(candidate, flag) is True:
                unsafe.append(f"unsafe candidate flag is true: {candidate.tool_ref}.{flag}")
    return tuple(sorted(dict.fromkeys(unsafe)))


def _result(
    *,
    status: SupervisedDryRunPlanStatusV1,
    ready: bool,
    case_ref: str,
    source_file_name: str,
    ordered_candidate_steps: tuple[Service1SupervisedDryRunStepV1, ...],
    operator_checklist: tuple[str, ...],
    required_manual_confirmations: tuple[str, ...],
    blocked_reasons: tuple[str, ...],
    missing_requirements: tuple[str, ...],
    metadata: dict[str, Any] | None,
) -> Service1SupervisedDryRunPlanResultV1:
    return Service1SupervisedDryRunPlanResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        ready=ready,
        case_ref=case_ref,
        source_file_name=source_file_name,
        supervised_dry_run_plan_ref=(
            f"SUPERVISED_DRY_RUN_PLAN:{case_ref}" if ready and case_ref else ""
        ),
        ordered_candidate_steps=ordered_candidate_steps,
        operator_checklist=operator_checklist,
        required_manual_confirmations=required_manual_confirmations,
        blocked_reasons=tuple(blocked_reasons),
        missing_requirements=tuple(missing_requirements),
        dry_run_required=True,
        execution_authorized=False,
        execution_executed=False,
        runtime_authorized=False,
        tool_execution_authorized=False,
        executable_tool_requests_authorized=False,
        pipeline_authorized=False,
        delivery_authorized=False,
        autonomous_delivery_authorized=False,
        llm_authorized=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "SUPERVISED_DRY_RUN_PLAN_READY",
    "NEEDS_EVIDENCE",
    "NO_CANDIDATE_TOOLS",
    "BLOCKED_INVALID_CONTROLLED_EXECUTION_CANDIDATES",
    "BLOCKED_UNSAFE_RUNTIME_FLAGS",
    "Service1SupervisedDryRunStepV1",
    "Service1SupervisedDryRunPlanResultV1",
    "build_service_1_controlled_execution_candidates_to_supervised_dry_run_plan_v1",
]
