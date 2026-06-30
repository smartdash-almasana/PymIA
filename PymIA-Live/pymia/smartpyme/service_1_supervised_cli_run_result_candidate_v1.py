"""Pure supervised CLI run result candidate for Phase I.

This module does not execute CLI, tools, runtime, or any real work.
It only converts a valid controlled_execution_candidate and supporting
observations into a supervised_cli_run_result_candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"
_BLOCKED_INVALID_EXECUTION_CANDIDATE = "BLOCKED_INVALID_EXECUTION_CANDIDATE"
_BLOCKED_INVALID_OPERATOR_SUPERVISION = "BLOCKED_INVALID_OPERATOR_SUPERVISION"
_BLOCKED_OPERATOR_MISMATCH = "BLOCKED_OPERATOR_MISMATCH"
_BLOCKED_MISSING_ARTIFACT_REFS = "BLOCKED_MISSING_ARTIFACT_REFS"
_BLOCKED_RUN_FAILED = "BLOCKED_RUN_FAILED"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_UNKNOWN = "UNKNOWN"

_ALLOWED_EXECUTION_MODE = "SUPERVISED_CLI_OPERATOR_FLOW"

_EXECUTION_CONTRACT_KIND = "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"
_EXECUTION_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"

_SUPERVISION_CONTRACT_KIND = "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"
_SUPERVISION_READY = "OPERATOR_SUPERVISION_READY"

_DANGEROUS_FLAGS = (
    "execution_executed",
    "cli_executed",
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

RunResultStatusV1 = Literal[
    _SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY,
    _BLOCKED_INVALID_EXECUTION_CANDIDATE,
    _BLOCKED_INVALID_OPERATOR_SUPERVISION,
    _BLOCKED_OPERATOR_MISMATCH,
    _BLOCKED_MISSING_ARTIFACT_REFS,
    _BLOCKED_RUN_FAILED,
    _BLOCKED_UNSAFE_RUNTIME_FLAGS,
    _UNKNOWN,
]


class SupervisedCliRunResultCandidateV1(TypedDict):
    candidate_kind: Literal["SUPERVISED_CLI_RUN_RESULT_CANDIDATE"]
    status: Literal[_SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY]
    ready: Literal[True]
    run_recorded: Literal[True]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    source_execution_candidate_ref: str
    source_operator_supervision_ref: str
    operator_ref: str
    owner_ref: str
    tenant_ref: str
    case_ref: str
    artifact_refs: list[str]
    warning_refs: list[str]
    error_refs: list[str]
    run_observation: str
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


class SupervisedCliRunResultCandidateResultV1(TypedDict):
    contract_kind: Literal["SUPERVISED_CLI_RUN_RESULT_CANDIDATE"]
    status: RunResultStatusV1
    ready: bool
    supervised_cli_run_result_candidate: SupervisedCliRunResultCandidateV1 | None
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


def build_service_1_supervised_cli_run_result_candidate_v1(
    *,
    controlled_execution_candidate: Mapping[str, Any] | None,
    operator_supervision_candidate: Mapping[str, Any] | None,
    artifact_refs: list[str] | object,
    warning_refs: list[str] | object,
    error_refs: list[str] | object,
    run_observation: str,
    operator_ref: str | None,
) -> SupervisedCliRunResultCandidateResultV1:
    """Create a pure supervised CLI run result candidate from validated upstream data."""

    if not isinstance(controlled_execution_candidate, Mapping):
        return _blocked(_UNKNOWN, ["controlled_execution_candidate must be a mapping"])

    if not isinstance(operator_supervision_candidate, Mapping):
        return _blocked(_UNKNOWN, ["operator_supervision_candidate must be a mapping"])

    execution_snapshot = deepcopy(dict(controlled_execution_candidate))
    supervision_snapshot = deepcopy(dict(operator_supervision_candidate))

    # Dangerous flags check across both candidates
    all_flags = {}
    for source_name, source in (
        ("controlled_execution_candidate", controlled_execution_candidate),
        ("operator_supervision_candidate", operator_supervision_candidate),
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
            execution_snapshot,
            supervision_snapshot,
        )

    # Validate controlled execution candidate
    if controlled_execution_candidate.get("contract_kind") != _EXECUTION_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["contract_kind must be CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"],
            execution_snapshot,
            supervision_snapshot,
        )

    if controlled_execution_candidate.get("status") != _EXECUTION_READY:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution status must be CONTROLLED_EXECUTION_CANDIDATE_READY"],
            execution_snapshot,
            supervision_snapshot,
        )

    if controlled_execution_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution ready must be True"],
            execution_snapshot,
            supervision_snapshot,
        )

    inner_execution = controlled_execution_candidate.get("controlled_execution_candidate")
    if not isinstance(inner_execution, Mapping):
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.controlled_execution_candidate is required"],
            execution_snapshot,
            supervision_snapshot,
        )

    if inner_execution.get("execution_authorized") is not True:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.execution_authorized must be True"],
            execution_snapshot,
            supervision_snapshot,
        )

    if inner_execution.get("execution_executed") is not False:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.execution_executed must be False"],
            execution_snapshot,
            supervision_snapshot,
        )

    if inner_execution.get("allowed_execution_mode") != _ALLOWED_EXECUTION_MODE:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.allowed_execution_mode must be SUPERVISED_CLI_OPERATOR_FLOW"],
            execution_snapshot,
            supervision_snapshot,
        )

    # Validate operator supervision candidate
    if operator_supervision_candidate.get("contract_kind") != _SUPERVISION_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["contract_kind must be CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"],
            execution_snapshot,
            supervision_snapshot,
        )

    if operator_supervision_candidate.get("status") != _SUPERVISION_READY:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["operator_supervision status must be OPERATOR_SUPERVISION_READY"],
            execution_snapshot,
            supervision_snapshot,
        )

    if operator_supervision_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_OPERATOR_SUPERVISION,
            ["operator_supervision ready must be True"],
            execution_snapshot,
            supervision_snapshot,
        )

    # Operator ref
    if not _has_text(operator_ref):
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref is required"],
            execution_snapshot,
            supervision_snapshot,
        )

    # Operator mismatch against execution candidate inner operator_ref
    execution_operator = inner_execution.get("operator_ref")
    if _has_text(execution_operator) and execution_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match controlled_execution_candidate.operator_ref"],
            execution_snapshot,
            supervision_snapshot,
        )

    # Operator mismatch against supervision candidate operator_ref
    inner_supervision = operator_supervision_candidate.get("operator_supervision_candidate")
    if isinstance(inner_supervision, Mapping):
        supervision_operator = inner_supervision.get("operator_ref")
        if _has_text(supervision_operator) and supervision_operator.strip() != operator_ref.strip():
            return _blocked(
                _BLOCKED_OPERATOR_MISMATCH,
                ["operator_ref does not match operator_supervision_candidate.operator_ref"],
                execution_snapshot,
                supervision_snapshot,
            )

    # Artifact refs
    cleaned_artifact_refs = _clean_refs(artifact_refs)
    if not cleaned_artifact_refs:
        return _blocked(
            _BLOCKED_MISSING_ARTIFACT_REFS,
            ["at least one artifact_ref is required"],
            execution_snapshot,
            supervision_snapshot,
        )

    # Run failure detection
    cleaned_error_refs = _clean_refs(error_refs)
    run_failed = False
    run_failure_reasons = []

    if cleaned_error_refs:
        run_failed = True
        run_failure_reasons.append("error_refs is not empty")

    if run_observation and _run_observation_indicates_failure(run_observation):
        run_failed = True
        run_failure_reasons.append("run_observation indicates failure")

    if run_failed:
        return _blocked(
            _BLOCKED_RUN_FAILED,
            run_failure_reasons,
            execution_snapshot,
            supervision_snapshot,
        )

    owner_ref = inner_execution.get("owner_ref", "")
    tenant_ref = inner_execution.get("tenant_ref", "")
    case_ref = inner_execution.get("case_ref", "")
    execution_ref = str(inner_execution.get("source_operator_supervision_ref", "unknown"))
    supervision_ref = str(
        inner_supervision.get("source_evidence_packet_ref", "unknown")
        if isinstance(inner_supervision, Mapping)
        else "unknown"
    )

    cleaned_warning_refs = _clean_refs(warning_refs)

    candidate: SupervisedCliRunResultCandidateV1 = {
        "candidate_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": _SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY,
        "ready": True,
        "run_recorded": True,
        "cli_executed": False,
        "execution_executed": False,
        "source_execution_candidate_ref": execution_ref,
        "source_operator_supervision_ref": supervision_ref,
        "operator_ref": operator_ref.strip(),
        "owner_ref": str(owner_ref).strip() if _has_text(owner_ref) else "",
        "tenant_ref": str(tenant_ref).strip() if _has_text(tenant_ref) else "",
        "case_ref": str(case_ref).strip() if _has_text(case_ref) else "",
        "artifact_refs": cleaned_artifact_refs,
        "warning_refs": cleaned_warning_refs,
        "error_refs": cleaned_error_refs,
        "run_observation": str(run_observation).strip(),
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }

    return {
        "contract_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": _SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY,
        "ready": True,
        "supervised_cli_run_result_candidate": candidate,
        "blocked_reasons": [],
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }


def _run_observation_indicates_failure(run_observation: str) -> bool:
    lowered = str(run_observation).lower()
    failure_indicators = (
        "failed",
        "error",
        "exception",
        "crash",
        "abort",
        "fatal",
        "panic",
    )
    for indicator in failure_indicators:
        idx = lowered.find(indicator)
        if idx == -1:
            continue
        # Check word boundaries: char before and after must not be alphanumeric
        before = idx - 1
        after = idx + len(indicator)
        before_ok = before < 0 or not lowered[before].isalnum()
        after_ok = after >= len(lowered) or not lowered[after].isalnum()
        if before_ok and after_ok:
            return True
    return False


def _blocked(
    status: str,
    reasons: list[str],
    execution_snapshot: dict[str, Any] | None = None,
    supervision_snapshot: dict[str, Any] | None = None,
) -> SupervisedCliRunResultCandidateResultV1:
    return {
        "contract_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": status,
        "ready": False,
        "supervised_cli_run_result_candidate": None,
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
    "build_service_1_supervised_cli_run_result_candidate_v1",
    "SupervisedCliRunResultCandidateV1",
    "SupervisedCliRunResultCandidateResultV1",
    "RunResultStatusV1",
]
