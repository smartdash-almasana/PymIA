"""Pure controlled delivery review candidate for Phase I.

This module does not execute delivery, publish, notifications, CLI, tools,
runtime, or any real work. It only models a controlled delivery review as a
pure candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY = "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY"
_BLOCKED_INVALID_SUPERVISED_RUN_RESULT = "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
_BLOCKED_INVALID_ABORT_ROLLBACK_RESULT = "BLOCKED_INVALID_ABORT_ROLLBACK_RESULT"
_BLOCKED_INVALID_EXECUTION_CANDIDATE = "BLOCKED_INVALID_EXECUTION_CANDIDATE"
_BLOCKED_OPERATOR_MISMATCH = "BLOCKED_OPERATOR_MISMATCH"
_BLOCKED_ABORT_OR_ROLLBACK_REQUIRED = "BLOCKED_ABORT_OR_ROLLBACK_REQUIRED"
_BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS = "BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS"
_BLOCKED_OWNER_DELIVERY_NOT_READY = "BLOCKED_OWNER_DELIVERY_NOT_READY"
_BLOCKED_UNSAFE_RUNTIME_FLAGS = "BLOCKED_UNSAFE_RUNTIME_FLAGS"
_UNKNOWN = "UNKNOWN"

_ALLOWED_EXECUTION_MODE = "SUPERVISED_CLI_OPERATOR_FLOW"

_RUN_RESULT_CONTRACT_KIND = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE"
_RUN_RESULT_READY = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"

_ABORT_ROLLBACK_CONTRACT_KIND = "ABORT_ROLLBACK_RESULT_CANDIDATE"
_ABORT_ROLLBACK_READY = "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"

_EXECUTION_CONTRACT_KIND = "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"
_EXECUTION_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"

_DANGEROUS_FLAGS = (
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "notification_sent",
    "cli_executed",
    "execution_executed",
    "rollback_executed",
    "runtime_authorized",
    "handoff_executed",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "mutation_authorized",
    "llm_authorized",
)

DeliveryReviewStatusV1 = Literal[
    _CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY,
    _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
    _BLOCKED_INVALID_ABORT_ROLLBACK_RESULT,
    _BLOCKED_INVALID_EXECUTION_CANDIDATE,
    _BLOCKED_OPERATOR_MISMATCH,
    _BLOCKED_ABORT_OR_ROLLBACK_REQUIRED,
    _BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS,
    _BLOCKED_OWNER_DELIVERY_NOT_READY,
    _BLOCKED_UNSAFE_RUNTIME_FLAGS,
    _UNKNOWN,
]


class ControlledDeliveryReviewCandidateV1(TypedDict):
    candidate_kind: Literal["CONTROLLED_DELIVERY_REVIEW_CANDIDATE"]
    status: Literal[_CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY]
    ready: Literal[True]
    delivery_review_recorded: Literal[True]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    source_run_result_ref: str
    source_abort_rollback_ref: str
    source_execution_candidate_ref: str
    operator_ref: str
    owner_ref: str
    tenant_ref: str
    case_ref: str
    delivery_artifact_refs: list[str]
    review_observation: str
    delivery_review_required: Literal[True]
    owner_delivery_ready: Literal[True]
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW"]
    runtime_authorized: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


class ControlledDeliveryReviewCandidateResultV1(TypedDict):
    contract_kind: Literal["CONTROLLED_DELIVERY_REVIEW_CANDIDATE"]
    status: DeliveryReviewStatusV1
    ready: bool
    controlled_delivery_review_candidate: ControlledDeliveryReviewCandidateV1 | None
    blocked_reasons: list[str]
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW", "NONE"]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    runtime_authorized: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


def build_service_1_controlled_delivery_review_candidate_v1(
    *,
    supervised_cli_run_result_candidate: Mapping[str, Any] | None,
    abort_rollback_result_candidate: Mapping[str, Any] | None,
    controlled_execution_candidate: Mapping[str, Any] | None,
    operator_ref: str | None,
    delivery_artifact_refs: list[str] | object,
    review_observation: str,
    delivery_review_required: bool = True,
    owner_delivery_ready: bool = False,
) -> ControlledDeliveryReviewCandidateResultV1:
    """Create a pure controlled delivery review candidate from validated upstream data."""

    if not isinstance(supervised_cli_run_result_candidate, Mapping):
        return _blocked(_UNKNOWN, ["supervised_cli_run_result_candidate must be a mapping"])

    if not isinstance(abort_rollback_result_candidate, Mapping):
        return _blocked(_UNKNOWN, ["abort_rollback_result_candidate must be a mapping"])

    if not isinstance(controlled_execution_candidate, Mapping):
        return _blocked(_UNKNOWN, ["controlled_execution_candidate must be a mapping"])

    run_snapshot = deepcopy(dict(supervised_cli_run_result_candidate))
    abort_snapshot = deepcopy(dict(abort_rollback_result_candidate))
    execution_snapshot = deepcopy(dict(controlled_execution_candidate))

    # Dangerous flags check across all three candidates
    all_flags = {}
    for source_name, source in (
        ("supervised_cli_run_result_candidate", supervised_cli_run_result_candidate),
        ("abort_rollback_result_candidate", abort_rollback_result_candidate),
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
            abort_snapshot,
            execution_snapshot,
        )

    # Validate supervised CLI run result candidate
    if supervised_cli_run_result_candidate.get("contract_kind") != _RUN_RESULT_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["contract_kind must be SUPERVISED_CLI_RUN_RESULT_CANDIDATE"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if supervised_cli_run_result_candidate.get("status") != _RUN_RESULT_READY:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result status must be SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if supervised_cli_run_result_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result ready must be True"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    inner_run = supervised_cli_run_result_candidate.get("supervised_cli_run_result_candidate")
    if not isinstance(inner_run, Mapping):
        return _blocked(
            _BLOCKED_INVALID_SUPERVISED_RUN_RESULT,
            ["supervised_cli_run_result_candidate.supervised_cli_run_result_candidate is required"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Validate abort/rollback result candidate
    if abort_rollback_result_candidate.get("contract_kind") != _ABORT_ROLLBACK_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_ABORT_ROLLBACK_RESULT,
            ["contract_kind must be ABORT_ROLLBACK_RESULT_CANDIDATE"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    abort_status = abort_rollback_result_candidate.get("status")
    if abort_status == _UNKNOWN:
        return _blocked(
            _BLOCKED_INVALID_ABORT_ROLLBACK_RESULT,
            ["abort_rollback_result status is UNKNOWN"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if abort_status not in (_ABORT_ROLLBACK_READY, "NO_ABORT_OR_ROLLBACK_REQUIRED"):
        return _blocked(
            _BLOCKED_INVALID_ABORT_ROLLBACK_RESULT,
            ["abort_rollback_result status must be ABORT_ROLLBACK_RESULT_CANDIDATE_READY or NO_ABORT_OR_ROLLBACK_REQUIRED"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if abort_rollback_result_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_ABORT_ROLLBACK_RESULT,
            ["abort_rollback_result ready must be True"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Check abort/rollback required
    inner_abort = abort_rollback_result_candidate.get("abort_rollback_result_candidate")
    if isinstance(inner_abort, Mapping):
        if inner_abort.get("abort_requested") is True or inner_abort.get("rollback_required") is True:
            return _blocked(
                _BLOCKED_ABORT_OR_ROLLBACK_REQUIRED,
                ["abort or rollback is required; delivery review is blocked"],
                run_snapshot,
                abort_snapshot,
                execution_snapshot,
            )

    # Validate controlled execution candidate
    if controlled_execution_candidate.get("contract_kind") != _EXECUTION_CONTRACT_KIND:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["contract_kind must be CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if controlled_execution_candidate.get("status") != _EXECUTION_READY:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution status must be CONTROLLED_EXECUTION_CANDIDATE_READY"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    if controlled_execution_candidate.get("ready") is not True:
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution ready must be True"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    inner_execution = controlled_execution_candidate.get("controlled_execution_candidate")
    if not isinstance(inner_execution, Mapping):
        return _blocked(
            _BLOCKED_INVALID_EXECUTION_CANDIDATE,
            ["controlled_execution_candidate.controlled_execution_candidate is required"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Operator ref
    if not _has_text(operator_ref):
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref is required"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Operator mismatch against run result
    run_operator = inner_run.get("operator_ref")
    if _has_text(run_operator) and run_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match supervised_cli_run_result_candidate.operator_ref"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Operator mismatch against execution candidate
    execution_operator = inner_execution.get("operator_ref")
    if _has_text(execution_operator) and execution_operator.strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_OPERATOR_MISMATCH,
            ["operator_ref does not match controlled_execution_candidate.operator_ref"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # delivery_review_required must be True
    if delivery_review_required is not True:
        return _blocked(
            _BLOCKED_OWNER_DELIVERY_NOT_READY,
            ["delivery_review_required must be True"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # owner_delivery_ready must be True
    if owner_delivery_ready is not True:
        return _blocked(
            _BLOCKED_OWNER_DELIVERY_NOT_READY,
            ["owner_delivery_ready must be True"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    # Delivery artifact refs
    cleaned_artifact_refs = _clean_refs(delivery_artifact_refs)
    if not cleaned_artifact_refs:
        return _blocked(
            _BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS,
            ["delivery_artifact_refs is required"],
            run_snapshot,
            abort_snapshot,
            execution_snapshot,
        )

    owner_ref = inner_run.get("owner_ref", "")
    tenant_ref = inner_run.get("tenant_ref", "")
    case_ref = inner_run.get("case_ref", "")
    run_ref = str(inner_run.get("source_execution_candidate_ref", "unknown"))
    abort_ref = str(
        inner_abort.get("source_run_result_ref", "unknown")
        if isinstance(inner_abort, Mapping)
        else "unknown"
    )
    execution_ref = str(inner_execution.get("source_operator_supervision_ref", "unknown"))

    candidate: ControlledDeliveryReviewCandidateV1 = {
        "candidate_kind": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE",
        "status": _CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY,
        "ready": True,
        "delivery_review_recorded": True,
        "delivery_executed": False,
        "publish_executed": False,
        "notification_executed": False,
        "cli_executed": False,
        "execution_executed": False,
        "source_run_result_ref": run_ref,
        "source_abort_rollback_ref": abort_ref,
        "source_execution_candidate_ref": execution_ref,
        "operator_ref": operator_ref.strip(),
        "owner_ref": str(owner_ref).strip() if _has_text(owner_ref) else "",
        "tenant_ref": str(tenant_ref).strip() if _has_text(tenant_ref) else "",
        "case_ref": str(case_ref).strip() if _has_text(case_ref) else "",
        "delivery_artifact_refs": cleaned_artifact_refs,
        "review_observation": str(review_observation).strip(),
        "delivery_review_required": True,
        "owner_delivery_ready": True,
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }

    return {
        "contract_kind": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE",
        "status": _CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY,
        "ready": True,
        "controlled_delivery_review_candidate": candidate,
        "blocked_reasons": [],
        "allowed_execution_mode": _ALLOWED_EXECUTION_MODE,
        **_safe_flags(),
    }


def _blocked(
    status: str,
    reasons: list[str],
    run_snapshot: dict[str, Any] | None = None,
    abort_snapshot: dict[str, Any] | None = None,
    execution_snapshot: dict[str, Any] | None = None,
) -> ControlledDeliveryReviewCandidateResultV1:
    return {
        "contract_kind": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE",
        "status": status,
        "ready": False,
        "controlled_delivery_review_candidate": None,
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
    "build_service_1_controlled_delivery_review_candidate_v1",
    "ControlledDeliveryReviewCandidateV1",
    "ControlledDeliveryReviewCandidateResultV1",
    "DeliveryReviewStatusV1",
]
