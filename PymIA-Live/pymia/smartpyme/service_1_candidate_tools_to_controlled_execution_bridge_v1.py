from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import (
    BLOCKED as CANDIDATE_TOOLS_BLOCKED,
    CANDIDATE_TOOLS_READY,
    NEEDS_EVIDENCE as CANDIDATE_TOOLS_NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS as CANDIDATE_TOOLS_NONE,
    Service1EvidenceProfileToCandidateToolsResultV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_CANDIDATE_TOOLS_TO_CONTROLLED_EXECUTION_BRIDGE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

CONTROLLED_EXECUTION_CANDIDATES_READY: Final[str] = "CONTROLLED_EXECUTION_CANDIDATES_READY"
BLOCKED_INVALID_CANDIDATE_TOOLS: Final[str] = "BLOCKED_INVALID_CANDIDATE_TOOLS"
BLOCKED_MISSING_OPERATOR: Final[str] = "BLOCKED_MISSING_OPERATOR"
BLOCKED_MISSING_EXECUTION_WINDOW: Final[str] = "BLOCKED_MISSING_EXECUTION_WINDOW"
BLOCKED_UNSAFE_RUNTIME_FLAGS: Final[str] = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
NO_CANDIDATE_TOOLS: Final[str] = "NO_CANDIDATE_TOOLS"
UNKNOWN: Final[str] = "UNKNOWN"

ALLOWED_EXECUTION_MODE: Final[str] = "SUPERVISED_CLI_OPERATOR_FLOW"

ControlledExecutionBridgeStatusV1 = Literal[
    "CONTROLLED_EXECUTION_CANDIDATES_READY",
    "BLOCKED_INVALID_CANDIDATE_TOOLS",
    "BLOCKED_MISSING_OPERATOR",
    "BLOCKED_MISSING_EXECUTION_WINDOW",
    "BLOCKED_UNSAFE_RUNTIME_FLAGS",
    "NEEDS_EVIDENCE",
    "NO_CANDIDATE_TOOLS",
    "UNKNOWN",
]


@dataclass(frozen=True)
class Service1ControlledExecutionCandidateFromToolV1:
    candidate_kind: str
    status: str
    ready: bool
    tool_ref: str
    source_signal_name: str
    source_file_name: str
    source_headers: tuple[str, ...]
    case_ref: str
    operator_ref: str
    execution_window_ref: str
    dry_run_required: bool
    allowed_execution_mode: str
    reason: str
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
class Service1CandidateToolsToControlledExecutionBridgeResultV1:
    schema_version: str
    service_name: str
    status: ControlledExecutionBridgeStatusV1
    ready: bool
    case_ref: str
    source_file_name: str
    controlled_execution_candidates: tuple[Service1ControlledExecutionCandidateFromToolV1, ...]
    candidate_tool_refs: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    allowed_execution_mode: str
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


def build_service_1_candidate_tools_to_controlled_execution_bridge_v1(
    *,
    candidate_tools_result: Service1EvidenceProfileToCandidateToolsResultV1,
    operator_ref: str | None,
    execution_window_ref: str | None,
    dry_run_required: bool = True,
    metadata: dict[str, Any] | None = None,
) -> Service1CandidateToolsToControlledExecutionBridgeResultV1:
    """Build controlled execution candidates from governed candidate tools.

    This bridge is pure. It does not execute tools, create executable tool
    requests, call pipelines, write delivery artifacts, call LLM runtimes, or
    authorize real execution.
    """
    if not isinstance(candidate_tools_result, Service1EvidenceProfileToCandidateToolsResultV1):
        return _result(
            status=UNKNOWN,
            ready=False,
            case_ref="",
            source_file_name="",
            controlled_execution_candidates=(),
            candidate_tool_refs=(),
            blocked_reasons=("candidate_tools_result must be a Service1EvidenceProfileToCandidateToolsResultV1",),
            missing_requirements=(),
            metadata=metadata,
        )
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    unsafe_flags = _unsafe_upstream_flags(candidate_tools_result)
    if unsafe_flags:
        return _result(
            status=BLOCKED_UNSAFE_RUNTIME_FLAGS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=unsafe_flags,
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if candidate_tools_result.status == CANDIDATE_TOOLS_NEEDS_EVIDENCE:
        return _result(
            status=NEEDS_EVIDENCE,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=(),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if candidate_tools_result.status == CANDIDATE_TOOLS_NONE:
        return _result(
            status=NO_CANDIDATE_TOOLS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=(),
            blocked_reasons=(),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if candidate_tools_result.status == CANDIDATE_TOOLS_BLOCKED or candidate_tools_result.blockers:
        return _result(
            status=BLOCKED_INVALID_CANDIDATE_TOOLS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=tuple(candidate_tools_result.blockers) or ("candidate_tools_result is blocked",),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if candidate_tools_result.status != CANDIDATE_TOOLS_READY:
        return _result(
            status=BLOCKED_INVALID_CANDIDATE_TOOLS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=(f"candidate_tools_result status must be {CANDIDATE_TOOLS_READY}",),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if not candidate_tools_result.candidate_tools:
        return _result(
            status=NO_CANDIDATE_TOOLS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=(),
            blocked_reasons=(),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if not _has_text(operator_ref):
        return _result(
            status=BLOCKED_MISSING_OPERATOR,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=("operator_ref is required",),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if not _has_text(execution_window_ref):
        return _result(
            status=BLOCKED_MISSING_EXECUTION_WINDOW,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=("execution_window_ref is required",),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    if dry_run_required is not True:
        return _result(
            status=BLOCKED_INVALID_CANDIDATE_TOOLS,
            ready=False,
            case_ref=candidate_tools_result.case_ref,
            source_file_name=candidate_tools_result.source_file_name,
            controlled_execution_candidates=(),
            candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
            blocked_reasons=("dry_run_required must be True",),
            missing_requirements=candidate_tools_result.missing_requirements,
            metadata=metadata,
        )

    candidates = tuple(
        sorted(
            (
                Service1ControlledExecutionCandidateFromToolV1(
                    candidate_kind="SERVICE_1_CONTROLLED_TOOL_EXECUTION_CANDIDATE",
                    status="CONTROLLED_TOOL_EXECUTION_CANDIDATE_PREPARED",
                    ready=True,
                    tool_ref=candidate_tool.tool_ref,
                    source_signal_name=candidate_tool.source_signal_name,
                    source_file_name=candidate_tools_result.source_file_name,
                    source_headers=candidate_tool.source_headers,
                    case_ref=candidate_tools_result.case_ref,
                    operator_ref=str(operator_ref).strip(),
                    execution_window_ref=str(execution_window_ref).strip(),
                    dry_run_required=True,
                    allowed_execution_mode=ALLOWED_EXECUTION_MODE,
                    reason=candidate_tool.reason,
                    limitations=candidate_tool.limitations,
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
                for candidate_tool in candidate_tools_result.candidate_tools
            ),
            key=lambda candidate: candidate.tool_ref,
        )
    )

    return _result(
        status=CONTROLLED_EXECUTION_CANDIDATES_READY,
        ready=True,
        case_ref=candidate_tools_result.case_ref,
        source_file_name=candidate_tools_result.source_file_name,
        controlled_execution_candidates=candidates,
        candidate_tool_refs=tuple(candidate.tool_ref for candidate in candidates),
        blocked_reasons=(),
        missing_requirements=candidate_tools_result.missing_requirements,
        metadata=metadata,
    )


def _unsafe_upstream_flags(
    candidate_tools_result: Service1EvidenceProfileToCandidateToolsResultV1,
) -> tuple[str, ...]:
    unsafe = []
    for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "executable_tool_requests_authorized",
        "autonomous_delivery_authorized",
    ):
        if getattr(candidate_tools_result, flag) is True:
            unsafe.append(f"unsafe upstream flag is true: {flag}")
    for candidate_tool in candidate_tools_result.candidate_tools:
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "executable_tool_request_authorized",
        ):
            if getattr(candidate_tool, flag) is True:
                unsafe.append(f"unsafe candidate tool flag is true: {candidate_tool.tool_ref}.{flag}")
    return tuple(sorted(dict.fromkeys(unsafe)))


def _result(
    *,
    status: ControlledExecutionBridgeStatusV1,
    ready: bool,
    case_ref: str,
    source_file_name: str,
    controlled_execution_candidates: tuple[Service1ControlledExecutionCandidateFromToolV1, ...],
    candidate_tool_refs: tuple[str, ...],
    blocked_reasons: tuple[str, ...],
    missing_requirements: tuple[str, ...],
    metadata: dict[str, Any] | None,
) -> Service1CandidateToolsToControlledExecutionBridgeResultV1:
    return Service1CandidateToolsToControlledExecutionBridgeResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        ready=ready,
        case_ref=case_ref,
        source_file_name=source_file_name,
        controlled_execution_candidates=controlled_execution_candidates,
        candidate_tool_refs=candidate_tool_refs,
        blocked_reasons=tuple(blocked_reasons),
        missing_requirements=tuple(missing_requirements),
        allowed_execution_mode=ALLOWED_EXECUTION_MODE if ready else "NONE",
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


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "CONTROLLED_EXECUTION_CANDIDATES_READY",
    "BLOCKED_INVALID_CANDIDATE_TOOLS",
    "BLOCKED_MISSING_OPERATOR",
    "BLOCKED_MISSING_EXECUTION_WINDOW",
    "BLOCKED_UNSAFE_RUNTIME_FLAGS",
    "NEEDS_EVIDENCE",
    "NO_CANDIDATE_TOOLS",
    "ALLOWED_EXECUTION_MODE",
    "Service1ControlledExecutionCandidateFromToolV1",
    "Service1CandidateToolsToControlledExecutionBridgeResultV1",
    "build_service_1_candidate_tools_to_controlled_execution_bridge_v1",
]
