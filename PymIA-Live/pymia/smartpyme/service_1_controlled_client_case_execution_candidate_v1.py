"""Pure controlled execution candidate contract for Phase I.

This module does not execute tools, CLI, runtime, or any real work.
It only converts a valid operator_supervision_candidate into a
controlled_execution_candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_CONTROLLED_EXECUTION_CANDIDATE_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"
_BLOCKED_INVALID_OPERATOR_SUPERVISION = "BLOCKED_INVALID_OPERATOR_SUPERVISION"
_BLOCKED_INVALID_EVIDENCE_PACKET = "BLOCKED_INVALID_EVIDENCE_PACKET"
_BLOCKED_INVALID_READINESS = "BLOCKED_INVALID_READINESS"
_BLOCKED_MISSING_EXECUTION_WINDOW = "BLOCKED_MISSING_EXECUTION_WINDOW"
_BLOCKED_OPERATOR_MISMATCH = "BLOCKED_OPERATOR_MISMATCH"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_UNKNOWN = "UNKNOWN"

_ALLOWED_EXECUTION_MODE = "SUPERVISED_CLI_OPERATOR_FLOW"

_OPERATOR_SUPERVISION_CONTRACT_KIND = "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"
_OPERATOR_SUPERVISION_READY = "OPERATOR_SUPERVISION_READY"

_EVIDENCE_PACKET_KIND = "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"
_EVIDENCE_PACKET_READY = "EVIDENCE_PACKET_READY"

_READINESS_GATE_KIND = "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"
_READINESS_READY = "CONTROLLED_CASE_READY"

_DANGEROUS_FLAGS = (
    "execution_executed",
    "runtime_authorized",
    "publish_executed",
    "notification_sent",
    "handoff_executed",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "mutation_authorized",
    "llm_authorized",
)

ExecutionCandidateStatusV1 = Literal[
    _CONTROLLED_EXECUTION_CANDIDATE_READY,
    _BLOCKED_INVALID_OPERATOR_SUPERVISION,
    _BLOCKED_INVALID_EVIDENCE_PACKET,
    _BLOCKED_INVALID_READINESS,
    _BLOCKED_MISSING_EXECUTION_WINDOW,
    _BLOCKED_OPERATOR_MISMATCH,
    _BLOCKED_UNSAFE_RUNTIME_FLAGS,
    _UNKNOWN,
]


class ControlledExecutionCandidateV1(TypedDict):
    candidate_kind: Literal["CONTROLLED_EXECUTION_CANDIDATE"]
    status: Literal[_CONTROLLED_EXECUTION_CANDIDATE_READY]
    ready: Literal[True]
    execution_authorized: Literal[True]
    execution_executed: Literal[False]
    source_operator_supervision_ref: str
    source_evidence_packet_ref: str
    source_readiness_gate_ref: str
    execution_window_ref: str
    operator_ref: str
    owner_ref: str
    tenant_ref: str
    case_ref: str
    dry_run_required: Literal[True]
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW"]
    runtime_authorized: Literal[False]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


class ControlledExecutionCandidateResultV1(TypedDict):
    contract_kind: Literal["CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"]
    status: ExecutionCandidateStatusV1
    ready: bool
    controlled_execution_candidate: ControlledExecutionCandidateV1 | None
    blocked_reasons: list[str]
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW", "NONE"]
    runtime_authorized: Literal[False]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


def build_service_1_controlled_client_case_execution_candidate_v1(
    *,
    operator_supervision_candidate: Mapping[str, Any] | None,
    evidence_packet_candidate: Mapping[str, Any] | None,
    readiness_gate_result: Mapping[str, Any] | None,
    execution_window_ref: str | None,
    operator_ref: str | None,
    dry_run_required: bool = True,
) -> ControlledExecutionCandidateResultV1:
    """Create a pure controlled execution candidate from validated upstream candidates."""

    if not isinstance(operator_supervision_candidate, Mapping):
        return _blocked(_UNKNOWN, ["operator_supervision_candidate must be a mapping"])

    if not isinstance(evidence_packet_candidate, Mapping):
        return _blocked(_UNKNOWN, ["evidence_packet_candidate must be a mapping"])

    if not isinstance(readiness_gate_result, Mapping):
        return _blocked(_UNKNOWN, ["readiness_gate_result must be a mapping"])

    supervision_snapshot = deepcopy(dict(operator_supervision_candidate))
    evidence_snapshot = deepcopy(dict(evidence_packet_candidate))
    readiness_snapshot = deepcopy(dict(readiness_gate_result))

    # Dangerous flags check across all three candidates
    all_flags = {}
    for source_name, source in (
        ("operator_supervision_candidate", operator_supervision_candidate),
        ("evidence_packet_candidate", evidence_packet_candidate),
        ("readiness_gate_result", readiness_gate_result),
    ):
        for flag in _DANGEROUS_FLAGS:
            if source.get(flag) is True:
                all_flags.setdefault(flag, []).append(source_name)

    if all_flags:
        reasons = []
        for flag, sources in all_flags.items():
            reasons.append(f"unsafe flag is true: {flag} in {', '.join(sources)}")
        return _blocked(
            _BLOCKED_UNSAFE_RUNTIME_FLAGS,
            reasons,
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Validate operator supervision candidate
    if operator_supervision_candidate.get("contract_kind") != _OPERATOR_SUPERVISION_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["contract_kind must be CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if operator_supervision_candidate.get("status") != _OPERATOR_SUPERVISION_READY:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["operator_supervision status must be OPERATOR_SUPERVISION_READY"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if operator_supervision_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["operator_supervision ready must be True"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if operator_supervision_candidate.get("allowed_execution_mode") != _ALLOWED_EXECUTION_MODE:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["operator_supervision allowed_execution_mode must be SUPERVISED_CLI_OPERATOR_FLOW"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Validate evidence packet candidate
    if evidence_packet_candidate.get("candidate_kind") != _EVIDENCE_PACKET_KIND:
        return _blocked(
            _BLOCKED_INVALID_EVIDENCE_PACKET,
            ["evidence_packet candidate_kind must be CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if evidence_packet_candidate.get("status") != _EVIDENCE_PACKET_READY:
        return _blocked(
            _BLOCKED_INVALID_EVIDENCE_PACKET,
            ["evidence_packet status must be EVIDENCE_PACKET_READY"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if evidence_packet_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_EVIDENCE_PACKET,
            ["evidence_packet ready must be True"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if evidence_packet_candidate.get("allowed_execution_mode") != _ALLOWED_EXECUTION_MODE:
        return _blocked(
            _BLOCKED_INVALID_EVIDENCE_PACKET,
            ["evidence_packet allowed_execution_mode must be SUPERVISED_CLI_OPERATOR_FLOW"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Validate readiness gate result
    if readiness_gate_result.get("gate_kind") != _READINESS_GATE_KIND:
        return _blocked(
            _BLOCKED_INVALID_READINESS,
            ["readiness_gate gate_kind must be FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if readiness_gate_result.get("status") != _READINESS_READY:
        return _blocked(
            _BLOCKED_INVALID_READINESS,
            ["readiness_gate status must be CONTROLLED_CASE_READY"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if readiness_gate_result.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_READINESS,
            ["readiness_gate ready must be True"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    if readiness_gate_result.get("allowed_execution_mode") != _ALLOWED_EXECUTION_MODE:
        return _blocked(
            _BLOCKED_INVALID_READINESS,
            ["readiness_gate allowed_execution_mode must be SUPERVISED_CLI_OPERATOR_FLOW"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Execution window
    if not _has_text(execution_window_ref):
        return _blocked(
            _BLOCKED_MISSING_EXECUTION_WINDOW,
            ["execution_window_ref is required"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Operator ref
    if not _has_text(operator_ref):
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref is required"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Operator mismatch: the explicit operator_ref must match the one from supervision candidate
    supervision_operator = evidence_packet_candidate.get("operator_oversight_ref")
    if _has_text(supervision_operator) and supervision_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match operator_oversight_ref from evidence packet"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    # Dry run required
    if dry_run_required is not True:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["dry_run_required must be True"],
            supervision_snapshot,
            evidence_snapshot,
            readiness_snapshot,
        )

    owner_ref = evidence_packet_candidate.get("owner_ref")
    tenant_ref = evidence_packet_candidate.get("tenant_ref")
    case_ref = evidence_packet_candidate.get("case_ref")

    supervision_ref = str(operator_supervision_candidate.get("source_evidence_packet_ref", "unknown"))
    evidence_ref = str(evidence_packet_candidate.get("packet_ref", "unknown"))
    readiness_ref = str(readiness_gate_result.get("controlled_case_candidate", {}).get("case_ref", "unknown"))

    candidate: ControlledExecutionCandidateV1 = {
        "candidate_kind": "CONTROLLED_EXECUTION_CANDIDATE",
        "status": _CONTROLLED_EXECUTION_CANDIDATE_READY,
        "ready": True,
        "execution_authorized": True,
        "execution_executed": False,
        "source_operator_supervision_ref": supervision_ref,
        "source_evidence_packet_ref": evidence_ref,
        "source_readiness_gate_ref": readiness_ref,
        "execution_window_ref": execution_window_ref.strip(),
        "operator_ref": operator_ref.strip(),
        "owner_ref": str(owner_ref).strip() if _has_text(owner_ref) else "",
        "tenant_ref": str(tenant_ref).strip() if _has_text(tenant_ref) else "",
        "case_ref": str(case_ref).strip() if _has_text(case_ref) else "",
        "dry_run_required": True,
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }

    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE",
        "status": _CONTROLLED_EXECUTION_CANDIDATE_READY,
        "ready": True,
        "controlled_execution_candidate": candidate,
        "blocked_reasons": [],
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }


def _blocked(
    status: str,
    reasons: list[str],
    supervision_snapshot: dict[str, Any] | None = None,
    evidence_snapshot: dict[str, Any] | None = None,
    readiness_snapshot: dict[str, Any] | None = None,
) -> ControlledExecutionCandidateResultV1:
    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE",
        "status": status,
        "ready": False,
        "controlled_execution_candidate": None,
        "blocked_reasons": list(reasons),
        "allowed_execution_mode": "NONE",
        **_safe_flags(),
    }


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "build_service_1_controlled_client_case_execution_candidate_v1",
    "ControlledExecutionCandidateV1",
    "ControlledExecutionCandidateResultV1",
    "ExecutionCandidateStatusV1",
]
