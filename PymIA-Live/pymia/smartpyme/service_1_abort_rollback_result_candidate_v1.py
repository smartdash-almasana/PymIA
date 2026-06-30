"""Pure abort/rollback result candidate for Phase I.

This module does not execute rollback, CLI, tools, runtime, or any real work.
It only models the result of an abort/rollback decision as a pure candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_ABORT_ROLLBACK_RESULT_CANDIDATE_READY = "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"
_NO_ABORT_OR_ROLLBACK_REQUIRED = "NO_ABORT_OR_ROLLBACK_REQUIRED"
_BLOCKED_INVALID_SUPERVISED_RUN_RESULT = "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
_BLOCKED_INVALID_EXECUTION_CANDIDATE = "BLOCKED_INVALID_EXECUTION_CANDIDATE"
_BLOCKED_OPERATOR_MISMATCH = "BLOCKED_OPERATOR_MISMATCH"
_BLOCKED_MISSING_ROLLBACK_REASON = "BLOCKED_MISSING_ROLLBACK_REASON"
_BLOCKED_MISSING_ROLLBACK_ARTIFACT_REFS = "BLOCKED_MISSING_ROLLBACK_ARTIFACT_REFS"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_UNKNOWN = "UNKNOWN"

_ALLOWED_EXECUTION_MODE = "SUPERVISED_CLI_OPERATOR_FLOW"

_RUN_RESULT_CONTRACT_KIND = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE"
_RUN_RESULT_READY = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"

_EXECUTION_CONTRACT_KIND = "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"
_EXECUTION_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"

_DANGEROUS_FLAGS = (
    "execution_executed",
    "cli_executed",
    "rollback_executed",
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

AbortRollbackStatusV1 = Literal[
    _ABORT_ROLLBACK_RESULT_CANDIDATE_READY,
    _NO_ABORT_OR_ROLLBACK_REQUIRED,
    _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
    _BLOCKED_INVALID_EXECUTION_CANDIDATE,
    _BLOCKED_OPERATOR_MISMATCH,
    _BLOCKED_MISSING_ROLLBACK_REASON,
    _BLOCKED_MISSING_ROLLBACK_ARTIFACT_REFS,
    _BLOCKED_UNSAFE_RUNTIME_FLAGS,
    _UNKNOWN,
]


class AbortRollbackResultCandidateV1(TypedDict):
    candidate_kind: Literal["ABORT_ROLLBACK_RESULT_CANDIDATE"]
    status: Literal[_ABORT_ROLLBACK_RESULT_CANDIDATE_READY]
    ready: Literal[True]
    abort_requested: bool
    rollback_required: bool
    rollback_recorded: Literal[True]
    rollback_executed: Literal[False]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    source_run_result_ref: str
    source_execution_candidate_ref: str
    operator_ref: str
    owner_ref: str
    tenant_ref: str
    case_ref: str
    rollback_reason: str
    rollback_artifact_refs: list[str]
    rollback_observation: str
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


class AbortRollbackResultCandidateResultV1(TypedDict):
    contract_kind: Literal["ABORT_ROLLBACK_RESULT_CANDIDATE"]
    status: AbortRollbackStatusV1
    ready: bool
    abort_rollback_result_candidate: AbortRollbackResultCandidateV1 | None
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


def build_service_1_abort_rollback_result_candidate_v1(
    *,
    supervised_cli_run_result_candidate: Mapping[str, Any] | None,
    controlled_execution_candidate: Mapping[str, Any] | None,
    operator_ref: str | None,
    abort_requested: bool = False,
    rollback_required: bool = False,
    rollback_reason: str | None = None,
    rollback_artifact_refs: list[str] | object = None,
    rollback_observation: str | None = None,
) -> AbortRollbackResultCandidateResultV1:
    """Create a pure abort/rollback result candidate from validated upstream data."""

    if not isinstance(supervised_cli_run_result_candidate, Mapping):
        return _blocked(_UNKNOWN, ["supervised_cli_run_result_candidate must be a mapping"])

    if not isinstance(controlled_execution_candidate, Mapping):
        return _blocked(_UNKNOWN, ["controlled_execution_candidate must be a mapping"])

    run_snapshot = deepcopy(dict(supervised_cli_run_result_candidate))
    execution_snapshot = deepcopy(dict(controlled_execution_candidate))

    # Dangerous flags check across both candidates
    all_flags = {}
    for source_name, source in (
        ("supervised_cli_run_result_candidate", supervised_cli_run_result_candidate),
        ("controlled_execution_candidate", controlled_execution_candidate),
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
            run_snapshot,
            execution_snapshot,
        )

    # Validate supervised CLI run result candidate
    if supervised_cli_run_result_candidate.get("contract_kind") != _RUN_RESULT_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["contract_kind must be SUPERVISED_CLI_RUN_RESULT_CANDIDATE"],
            run_snapshot,
            execution_snapshot,
        )

    if supervised_cli_run_result_candidate.get("status") != _RUN_RESULT_READY:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result status must be SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"],
            run_snapshot,
            execution_snapshot,
        )

    if supervised_cli_run_result_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result ready must be True"],
            run_snapshot,
            execution_snapshot,
        )

    inner_run = supervised_cli_run_result_candidate.get("supervised_cli_run_result_candidate")
    if not isinstance(inner_run, Mapping):
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result_candidate.supervised_cli_run_result_candidate is required"],
            run_snapshot,
            execution_snapshot,
        )

    # Validate controlled execution candidate
    if controlled_execution_candidate.get("contract_kind") != _EXECUTION_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["contract_kind must be CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"],
            run_snapshot,
            execution_snapshot,
        )

    if controlled_execution_candidate.get("status") != _EXECUTION_READY:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution status must be CONTROLLED_EXECUTION_CANDIDATE_READY"],
            run_snapshot,
            execution_snapshot,
        )

    if controlled_execution_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution ready must be True"],
            run_snapshot,
            execution_snapshot,
        )

    inner_execution = controlled_execution_candidate.get("controlled_execution_candidate")
    if not isinstance(inner_execution, Mapping):
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.controlled_execution_candidate is required"],
            run_snapshot,
            execution_snapshot,
        )

    # Operator ref
    if not _has_text(operator_ref):
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref is required"],
            run_snapshot,
            execution_snapshot,
        )

    # Operator mismatch against run result
    run_operator = inner_run.get("operator_ref")
    if _has_text(run_operator) and run_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match supervised_cli_run_result_candidate.operator_ref"],
            run_snapshot,
            execution_snapshot,
        )

    # Operator mismatch against execution candidate
    execution_operator = inner_execution.get("operator_ref")
    if _has_text(execution_operator) and execution_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match controlled_execution_candidate.operator_ref"],
            run_snapshot,
            execution_snapshot,
        )

    # No abort/rollback required fast path
    if not abort_requested and not rollback_required:
        return {
            "contract_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
            "status": _NO_ABORT_OR_ROLLBACK_REQUIRED,
            "ready": True,
            "abort_rollback_result_candidate": None,
            "blocked_reasons": [],
            "allowed_execution_mode": "NONE",
            **_safe_flags(),
        }

    # If abort_requested=True, require rollback_reason even if rollback_required=False
    if abort_requested and not _has_text(rollback_reason):
        return _blocked(
            _BLOCKED_MISSING_ROLLBACK_REASON,
            ["rollback_reason is required when abort_requested=True"],
            run_snapshot,
            execution_snapshot,
        )

    # If rollback_required=True, require rollback_reason and rollback_artifact_refs
    if rollback_required:
        if not _has_text(rollback_reason):
            return _blocked(
                _BLOCKED_MISSING_ROLLBACK_REASON,
                ["rollback_reason is required when rollback_required=True"],
                run_snapshot,
                execution_snapshot,
            )

        cleaned_rollback_artifacts = _clean_refs(rollback_artifact_refs)
        if not cleaned_rollback_artifacts:
            return _blocked(
                _BLOCKED_MISSING_ROLLBACK_ARTIFACT_REFS,
                ["rollback_artifact_refs is required when rollback_required=True"],
                run_snapshot,
                execution_snapshot,
            )

    owner_ref = inner_run.get("owner_ref", "")
    tenant_ref = inner_run.get("tenant_ref", "")
    case_ref = inner_run.get("case_ref", "")
    run_ref = str(inner_run.get("source_execution_candidate_ref", "unknown"))
    execution_ref = str(inner_execution.get("source_operator_supervision_ref", "unknown"))

    cleaned_rollback_artifacts = _clean_refs(rollback_artifact_refs)

    candidate: AbortRollbackResultCandidateV1 = {
        "candidate_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": _ABORT_ROLLBACK_RESULT_CANDIDATE_READY,
        "ready": True,
        "abort_requested": bool(abort_requested),
        "rollback_required": bool(rollback_required),
        "rollback_recorded": True,
        "rollback_executed": False,
        "cli_executed": False,
        "execution_executed": False,
        "source_run_result_ref": run_ref,
        "source_execution_candidate_ref": execution_ref,
        "operator_ref": operator_ref.strip(),
        "owner_ref": str(owner_ref).strip() if _has_text(owner_ref) else "",
        "tenant_ref": str(tenant_ref).strip() if _has_text(tenant_ref) else "",
        "case_ref": str(case_ref).strip() if _has_text(case_ref) else "",
        "rollback_reason": str(rollback_reason).strip() if _has_text(rollback_reason) else "",
        "rollback_artifact_refs": cleaned_rollback_artifacts,
        "rollback_observation": str(rollback_observation).strip() if _has_text(rollback_observation) else "",
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }

    return {
        "contract_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": _ABORT_ROLLBACK_RESULT_CANDIDATE_READY,
        "ready": True,
        "abort_rollback_result_candidate": candidate,
        "blocked_reasons": [],
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }


def _blocked(
    status: str,
    reasons: list[str],
    run_snapshot: dict[str, Any] | None = None,
    execution_snapshot: dict[str, Any] | None = None,
) -> AbortRollbackResultCandidateResultV1:
    return {
        "contract_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": status,
        "ready": False,
        "abort_rollback_result_candidate": None,
        "blocked_reasons": list(reasons),
        "allowed_execution_mode": "NONE",
        **_safe_flags(),
    }


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if _has_text(value)]


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "build_service_1_abort_rollback_result_candidate_v1",
    "AbortRollbackResultCandidateV1",
    "AbortRollbackResultCandidateResultV1",
    "AbortRollbackStatusV1",
]
