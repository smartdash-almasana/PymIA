"""Pure readiness gate for Phase I first controlled client case.

This module does not execute runtime work. It only decides whether a candidate
case is safe to enter a supervised controlled-client flow.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, TypedDict, Literal


_CONTROLLED_CASE_READY = "CONTROLLED_CASE_READY"
_BLOCKED_MISSING_OWNER_CONSENT = "BLOCKED_MISSING_OWNER_CONSENT"
_BLOCKED_MISSING_EVIDENCE = "BLOCKED_MISSING_EVIDENCE"
_BLOCKED_UNCLEAR_SCOPE = "BLOCKED_UNCLEAR_SCOPE"
_BLOCKED_NO_OPERATOR_OVERSIGHT = "BLOCKED_NO_OPERATOR_OVERSIGHT"
_BLOCKED_NO_ROLLBACK_PLAN = "BLOCKED_NO_ROLLBACK_PLAN"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_NEEDS_SCOPE_REDUCTION = "NEEDS_SCOPE_REDUCTION"
_UNKNOWN = "UNKNOWN"

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


class FirstControlledClientCaseReadinessResult(TypedDict, total=False):
    gate_kind: Literal["FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"]
    status: str
    ready: bool
    controlled_case_candidate: dict[str, Any] | None
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


def build_service_1_first_controlled_client_case_readiness_gate_v1(
    *,
    case_candidate: Mapping[str, Any] | None,
) -> FirstControlledClientCaseReadinessResult:
    """Return a fail-closed readiness decision for a first controlled case."""

    if not isinstance(case_candidate, Mapping):
        return _blocked(_UNKNOWN, ["case_candidate must be a mapping"])

    candidate_snapshot = deepcopy(dict(case_candidate))

    unsafe_flags = [flag for flag in _DANGEROUS_FLAGS if case_candidate.get(flag) is True]
    if unsafe_flags:
        return _blocked(
            _BLOCKED_UNSAFE_RUNTIME_FLAGS,
            [f"unsafe flag is true: {flag}" for flag in unsafe_flags],
            candidate_snapshot,
        )

    if not _has_text(case_candidate.get("owner_ref")):
        return _blocked(_BLOCKED_MISSING_OWNER_CONSENT, ["owner_ref is required"], candidate_snapshot)

    if not _has_text(case_candidate.get("tenant_ref")):
        return _blocked(_UNKNOWN, ["tenant_ref is required"], candidate_snapshot)

    if not _has_text(case_candidate.get("case_ref")):
        return _blocked(_UNKNOWN, ["case_ref is required"], candidate_snapshot)

    if case_candidate.get("owner_consent") is not True:
        return _blocked(
            _BLOCKED_MISSING_OWNER_CONSENT,
            ["explicit owner_consent=True is required"],
            candidate_snapshot,
        )

    evidence_refs = case_candidate.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(_has_text(ref) for ref in evidence_refs):
        return _blocked(
            _BLOCKED_MISSING_EVIDENCE,
            ["at least one valid evidence_ref is required"],
            candidate_snapshot,
        )

    scope = case_candidate.get("scope")
    if not isinstance(scope, Mapping) or not _has_text(scope.get("problem_statement")):
        return _blocked(
            _BLOCKED_UNCLEAR_SCOPE,
            ["scope.problem_statement is required"],
            candidate_snapshot,
        )

    if scope.get("too_broad") is True:
        return _blocked(
            _NEEDS_SCOPE_REDUCTION,
            ["scope is marked too_broad"],
            candidate_snapshot,
        )

    if case_candidate.get("operator_oversight_enabled") is not True:
        return _blocked(
            _BLOCKED_NO_OPERATOR_OVERSIGHT,
            ["operator_oversight_enabled=True is required"],
            candidate_snapshot,
        )

    rollback_plan = case_candidate.get("rollback_plan")
    if not isinstance(rollback_plan, Mapping) or rollback_plan.get("abort_allowed") is not True:
        return _blocked(
            _BLOCKED_NO_ROLLBACK_PLAN,
            ["rollback_plan.abort_allowed=True is required"],
            candidate_snapshot,
        )

    return {
        "gate_kind": "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE",
        "status": _CONTROLLED_CASE_READY,
        "ready": True,
        "controlled_case_candidate": candidate_snapshot,
        "blocked_reasons": [],
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        **_safe_flags(),
    }


def _blocked(
    status: str,
    reasons: list[str],
    candidate_snapshot: dict[str, Any] | None = None,
) -> FirstControlledClientCaseReadinessResult:
    return {
        "gate_kind": "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE",
        "status": status,
        "ready": False,
        "controlled_case_candidate": candidate_snapshot,
        "blocked_reasons": list(reasons),
        "allowed_execution_mode": "NONE",
        **_safe_flags(),
    }


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
