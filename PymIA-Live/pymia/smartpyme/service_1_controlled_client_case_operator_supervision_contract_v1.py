"""Pure operator supervision contract for Phase I controlled client cases.

The contract creates a supervision candidate only. It does not execute tools,
runtime work, delivery, publication, notifications, storage, API calls, or LLM calls.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_OPERATOR_SUPERVISION_READY = "OPERATOR_SUPERVISION_READY"
_BLOCKED_INVALID_EVIDENCE_PACKET = "BLOCKED_INVALID_EVIDENCE_PACKET"
_BLOCKED_MISSING_OPERATOR = "BLOCKED_MISSING_OPERATOR"
_BLOCKED_MISSING_ABORT_POLICY = "BLOCKED_MISSING_ABORT_POLICY"
_BLOCKED_UNSAFE_ACTIONS = "BLOCKED_UNSAFE_ACTIONS"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_UNKNOWN = "UNKNOWN"

_ALLOWED_EXECUTION_MODE = "SUPERVISED_CLI_OPERATOR_FLOW"
_NONE_MODE = "NONE"

_DANGEROUS_FLAGS = (
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

_ALLOWED_ACTIONS = (
    "inspect_evidence_packet",
    "run_supervised_cli_flow",
    "review_generated_artifacts",
    "abort_controlled_case",
)


class ControlledClientCaseOperatorSupervisionResult(TypedDict, total=False):
    contract_kind: Literal["CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"]
    status: str
    ready: bool
    operator_supervision_candidate: dict[str, Any] | None
    blocked_reasons: list[str]
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW", "NONE"]
    allowed_actions: list[str]
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


def build_service_1_controlled_client_case_operator_supervision_contract_v1(
    *,
    evidence_packet_candidate: Mapping[str, Any] | None,
    operator_ref: str | None,
    abort_policy: Mapping[str, Any] | None,
    review_required: bool = True,
) -> ControlledClientCaseOperatorSupervisionResult:
    """Create a pure operator supervision candidate for a controlled case."""

    if not isinstance(evidence_packet_candidate, Mapping):
        return _blocked(_UNKNOWN, ["evidence_packet_candidate must be a mapping"])

    packet_snapshot = deepcopy(dict(evidence_packet_candidate))

    unsafe_flags = [flag for flag in _DANGEROUS_FLAGS if evidence_packet_candidate.get(flag) is True]
    if unsafe_flags:
        return _blocked(
            _BLOCKED_UNSAFE_RUNTIME_FLAGS,
            [f"unsafe flag is true: {flag}" for flag in unsafe_flags],
            packet_snapshot,
        )

    if not _valid_evidence_packet(evidence_packet_candidate):
        return _blocked(
            _BLOCKED_INVALID_EVIDENCE_PACKET,
            ["controlled_case_evidence_packet_candidate must be ready"],
            packet_snapshot,
        )

    if not _has_text(operator_ref):
        return _blocked(_BLOCKED_MISSING_OPERATOR, ["operator_ref is required"], packet_snapshot)

    if not _valid_abort_policy(abort_policy):
        return _blocked(
            _BLOCKED_MISSING_ABORT_POLICY,
            ["abort_policy.abort_allowed=True and abort_policy.rollback_ref are required"],
            packet_snapshot,
        )

    requested_actions = abort_policy.get("allowed_actions")
    if requested_actions is not None and not _valid_requested_actions(requested_actions):
        return _blocked(
            _BLOCKED_UNSAFE_ACTIONS,
            ["abort_policy.allowed_actions contains an unsafe action"],
            packet_snapshot,
        )

    candidate = {
        "candidate_kind": "OPERATOR_SUPERVISION_CANDIDATE",
        "source_evidence_packet_ref": evidence_packet_candidate.get("packet_ref"),
        "owner_ref": evidence_packet_candidate.get("owner_ref"),
        "tenant_ref": evidence_packet_candidate.get("tenant_ref"),
        "case_ref": evidence_packet_candidate.get("case_ref"),
        "operator_ref": operator_ref,
        "review_required": bool(review_required),
        "abort_policy": deepcopy(dict(abort_policy)),
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        "allowed_actions": list(_ALLOWED_ACTIONS),
        **_safe_flags(),
    }

    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT",
        "status": _OPERATOR_SUPERVISION_READY,
        "ready": True,
        "operator_supervision_candidate": candidate,
        "blocked_reasons": [],
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        "allowed_actions": list(_ALLOWED_ACTIONS),
        **_safe_flags(),
    }


def _valid_evidence_packet(packet: Mapping[str, Any]) -> bool:
    return (
        packet.get("candidate_kind") == "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"
        and packet.get("status") == "EVIDENCE_PACKET_READY"
        and packet.get("ready") is True
        and packet.get("allowed_execution_mode") == _ALLOWED_EXECUTION_MODE
        and _has_text(packet.get("owner_ref"))
        and _has_text(packet.get("tenant_ref"))
        and _has_text(packet.get("case_ref"))
    )


def _valid_abort_policy(abort_policy: Mapping[str, Any] | None) -> bool:
    return (
        isinstance(abort_policy, Mapping)
        and abort_policy.get("abort_allowed") is True
        and _has_text(abort_policy.get("rollback_ref"))
    )


def _valid_requested_actions(actions: Any) -> bool:
    if not isinstance(actions, list):
        return False
    return all(isinstance(action, str) and action in _ALLOWED_ACTIONS for action in actions)


def _blocked(
    status: str,
    reasons: list[str],
    packet_snapshot: dict[str, Any] | None = None,
) -> ControlledClientCaseOperatorSupervisionResult:
    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT",
        "status": status,
        "ready": False,
        "operator_supervision_candidate": None,
        "blocked_reasons": list(reasons),
        "allowed_execution_mode": _NONE_MODE,
        "allowed_actions": [],
        **_safe_flags(),
    }


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
