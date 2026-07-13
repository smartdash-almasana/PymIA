"""Pure composition for Service 1 synthetic controlled case candidate chain.

This module verifies that the synthetic controlled case candidate model can
compose with Phase I candidate results without executing CLI, runtime, data
processing, artifact generation, delivery, Servicio 2, or Phase J.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_READY = "SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION_READY"
_BLOCKED_INVALID_SYNTHETIC_MODEL = "BLOCKED_INVALID_SYNTHETIC_MODEL"
_BLOCKED_INVALID_PHASE_I_CHAIN = "BLOCKED_INVALID_PHASE_I_CHAIN"
_BLOCKED_OPERATOR_MISMATCH = "BLOCKED_OPERATOR_MISMATCH"
_BLOCKED_CASE_MISMATCH = "BLOCKED_CASE_MISMATCH"
_BLOCKED_UNSAFE_EXECUTION_FLAGS = "BLOCKED_UNSAFE_EXECUTION_FLAGS"
_UNKNOWN = "UNKNOWN"

_SYNTHETIC_MODEL_CONTRACT = "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL"
_SYNTHETIC_MODEL_READY = "SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL_READY"
_SYNTHETIC_MODEL_KEY = "synthetic_controlled_case_candidate_model"

_EXECUTION_CONTRACT = "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"
_EXECUTION_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"
_EXECUTION_KEY = "controlled_execution_candidate"

_RUN_RESULT_CONTRACT = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE"
_RUN_RESULT_READY = "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"
_RUN_RESULT_KEY = "supervised_cli_run_result_candidate"

_ABORT_CONTRACT = "ABORT_ROLLBACK_RESULT_CANDIDATE"
_ABORT_READY = "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"
_ABORT_KEY = "abort_rollback_result_candidate"

_DELIVERY_CONTRACT = "CONTROLLED_DELIVERY_REVIEW_CANDIDATE"
_DELIVERY_READY = "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY"
_DELIVERY_KEY = "controlled_delivery_review_candidate"

_DANGEROUS_FLAGS = (
    "business_files_used",
    "cli_executed",
    "execution_executed",
    "runtime_executed",
    "runtime_authorized",
    "data_processed",
    "artifacts_generated",
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "notification_sent",
    "owner_delivery_executed",
    "rollback_executed",
    "handoff_executed",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "mutation_authorized",
    "llm_authorized",
    "service_2_opened",
    "phase_j_opened",
)

CompositionStatusV1 = Literal[
    _READY,
    _BLOCKED_INVALID_SYNTHETIC_MODEL,
    _BLOCKED_INVALID_PHASE_I_CHAIN,
    _BLOCKED_OPERATOR_MISMATCH,
    _BLOCKED_CASE_MISMATCH,
    _BLOCKED_UNSAFE_EXECUTION_FLAGS,
    _UNKNOWN,
]


class SyntheticControlledCaseCandidateChainCompositionV1(TypedDict):
    candidate_kind: Literal["SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION"]
    status: Literal[_READY]
    ready: Literal[True]
    case_ref: str
    operator_ref: str
    synthetic_model_status: str
    controlled_execution_status: str
    supervised_run_result_status: str
    abort_rollback_status: str
    delivery_review_status: str
    full_chain_bound: Literal[True]
    run_result_binding: Literal["CANDIDATE_READY_NOT_CLI_EXECUTED"]
    abort_rollback_binding: Literal["CANDIDATE_READY_NOT_ROLLBACK_EXECUTED"]
    delivery_review_binding: Literal["CANDIDATE_READY_NOT_DELIVERED"]
    business_files_used: Literal[False]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    runtime_executed: Literal[False]
    runtime_authorized: Literal[False]
    data_processed: Literal[False]
    artifacts_generated: Literal[False]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    notification_sent: Literal[False]
    owner_delivery_executed: Literal[False]
    rollback_executed: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]


class SyntheticControlledCaseCandidateChainCompositionResultV1(TypedDict):
    contract_kind: Literal["SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION"]
    status: CompositionStatusV1
    ready: bool
    synthetic_controlled_case_candidate_chain_composition: SyntheticControlledCaseCandidateChainCompositionV1 | None
    blocked_reasons: list[str]
    business_files_used: Literal[False]
    cli_executed: Literal[False]
    execution_executed: Literal[False]
    runtime_executed: Literal[False]
    runtime_authorized: Literal[False]
    data_processed: Literal[False]
    artifacts_generated: Literal[False]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    notification_sent: Literal[False]
    owner_delivery_executed: Literal[False]
    rollback_executed: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]


def build_service_1_synthetic_controlled_case_candidate_chain_composition_v1(
    *,
    synthetic_candidate_model_result: Mapping[str, Any] | None,
    controlled_execution_candidate_result: Mapping[str, Any] | None,
    supervised_run_result_candidate_result: Mapping[str, Any] | None,
    abort_rollback_result_candidate_result: Mapping[str, Any] | None,
    controlled_delivery_review_candidate_result: Mapping[str, Any] | None,
    operator_ref: str | None,
) -> SyntheticControlledCaseCandidateChainCompositionResultV1:
    """Compose the synthetic candidate model with Phase I candidate results."""

    sources = (
        synthetic_candidate_model_result,
        controlled_execution_candidate_result,
        supervised_run_result_candidate_result,
        abort_rollback_result_candidate_result,
        controlled_delivery_review_candidate_result,
    )
    if not all(isinstance(source, Mapping) for source in sources):
        return _blocked(_UNKNOWN, ["all candidate inputs must be mappings"])

    snapshots = [deepcopy(dict(source)) for source in sources if isinstance(source, Mapping)]

    unsafe = _unsafe_flags(*snapshots)
    if unsafe:
        return _blocked(
            _BLOCKED_UNSAFE_EXECUTION_FLAGS,
            [f"unsafe flag is true: {flag}" for flag in unsafe],
        )

    synthetic_model = _inner_ready_candidate(
        synthetic_candidate_model_result,
        contract_kind=_SYNTHETIC_MODEL_CONTRACT,
        status=_SYNTHETIC_MODEL_READY,
        inner_key=_SYNTHETIC_MODEL_KEY,
    )
    if synthetic_model is None:
        return _blocked(_BLOCKED_INVALID_SYNTHETIC_MODEL, ["synthetic candidate model must be ready"])

    if not _has_text(operator_ref):
        return _blocked(_BLOCKED_OPERATOR_MISMATCH, ["operator_ref is required"])

    case_ref = synthetic_model.get("case_ref")
    if not _has_text(case_ref):
        return _blocked(_BLOCKED_INVALID_SYNTHETIC_MODEL, ["synthetic model case_ref is required"])

    if synthetic_model.get("operator_ref") != operator_ref.strip():
        return _blocked(_BLOCKED_OPERATOR_MISMATCH, ["operator_ref does not match synthetic model"])

    if synthetic_model.get("synthetic_only") is not True:
        return _blocked(_BLOCKED_INVALID_SYNTHETIC_MODEL, ["synthetic model must be synthetic_only"])

    if synthetic_model.get("service_family") != "SERVICE_1":
        return _blocked(_BLOCKED_INVALID_SYNTHETIC_MODEL, ["synthetic model service_family must be SERVICE_1"])

    execution_candidate = _inner_ready_candidate(
        controlled_execution_candidate_result,
        contract_kind=_EXECUTION_CONTRACT,
        status=_EXECUTION_READY,
        inner_key=_EXECUTION_KEY,
    )
    run_result_candidate = _inner_ready_candidate(
        supervised_run_result_candidate_result,
        contract_kind=_RUN_RESULT_CONTRACT,
        status=_RUN_RESULT_READY,
        inner_key=_RUN_RESULT_KEY,
    )
    abort_candidate = _inner_ready_candidate(
        abort_rollback_result_candidate_result,
        contract_kind=_ABORT_CONTRACT,
        status=_ABORT_READY,
        inner_key=_ABORT_KEY,
    )
    delivery_candidate = _inner_ready_candidate(
        controlled_delivery_review_candidate_result,
        contract_kind=_DELIVERY_CONTRACT,
        status=_DELIVERY_READY,
        inner_key=_DELIVERY_KEY,
    )

    if any(candidate is None for candidate in (execution_candidate, run_result_candidate, abort_candidate, delivery_candidate)):
        return _blocked(_BLOCKED_INVALID_PHASE_I_CHAIN, ["all Phase I candidate results must be ready"])

    phase_i_candidates = (
        execution_candidate,
        run_result_candidate,
        abort_candidate,
        delivery_candidate,
    )

    mismatched_case = [str(candidate.get("case_ref", "")) for candidate in phase_i_candidates if candidate.get("case_ref") != case_ref]
    if mismatched_case:
        return _blocked(_BLOCKED_CASE_MISMATCH, ["case_ref must match across synthetic model and Phase I candidates"])

    mismatched_operator = [str(candidate.get("operator_ref", "")) for candidate in phase_i_candidates if candidate.get("operator_ref") != operator_ref.strip()]
    if mismatched_operator:
        return _blocked(_BLOCKED_OPERATOR_MISMATCH, ["operator_ref must match across all candidates"])

    if execution_candidate.get("execution_authorized") is not True:
        return _blocked(_BLOCKED_INVALID_PHASE_I_CHAIN, ["execution candidate must be authorized as candidate data"])

    if run_result_candidate.get("run_recorded") is not True:
        return _blocked(_BLOCKED_INVALID_PHASE_I_CHAIN, ["run result candidate must be recorded as candidate data"])

    if abort_candidate.get("rollback_recorded") is not True:
        return _blocked(_BLOCKED_INVALID_PHASE_I_CHAIN, ["abort/rollback candidate must be recorded as candidate data"])

    if delivery_candidate.get("delivery_review_recorded") is not True:
        return _blocked(_BLOCKED_INVALID_PHASE_I_CHAIN, ["delivery review candidate must be recorded as candidate data"])

    composition: SyntheticControlledCaseCandidateChainCompositionV1 = {
        "candidate_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION",
        "status": _READY,
        "ready": True,
        "case_ref": str(case_ref).strip(),
        "operator_ref": operator_ref.strip(),
        "synthetic_model_status": str(synthetic_candidate_model_result.get("status")),
        "controlled_execution_status": str(controlled_execution_candidate_result.get("status")),
        "supervised_run_result_status": str(supervised_run_result_candidate_result.get("status")),
        "abort_rollback_status": str(abort_rollback_result_candidate_result.get("status")),
        "delivery_review_status": str(controlled_delivery_review_candidate_result.get("status")),
        "full_chain_bound": True,
        "run_result_binding": "CANDIDATE_READY_NOT_CLI_EXECUTED",
        "abort_rollback_binding": "CANDIDATE_READY_NOT_ROLLBACK_EXECUTED",
        "delivery_review_binding": "CANDIDATE_READY_NOT_DELIVERED",
        **_safe_flags(),
    }

    return {
        "contract_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION",
        "status": _READY,
        "ready": True,
        "synthetic_controlled_case_candidate_chain_composition": composition,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _inner_ready_candidate(
    result: Mapping[str, Any] | None,
    *,
    contract_kind: str,
    status: str,
    inner_key: str,
) -> Mapping[str, Any] | None:
    if not isinstance(result, Mapping):
        return None
    if result.get("contract_kind") != contract_kind:
        return None
    if result.get("status") != status:
        return None
    if result.get("ready") is not True:
        return None
    inner = result.get(inner_key)
    if not isinstance(inner, Mapping):
        return None
    if inner.get("ready") is not True:
        return None
    return inner


def _blocked(
    status: str,
    reasons: list[str],
) -> SyntheticControlledCaseCandidateChainCompositionResultV1:
    return {
        "contract_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION",
        "status": status,
        "ready": False,
        "synthetic_controlled_case_candidate_chain_composition": None,
        "blocked_reasons": list(reasons),
        **_safe_flags(),
    }


def _unsafe_flags(*sources: Mapping[str, Any]) -> list[str]:
    unsafe: list[str] = []
    for flag in _DANGEROUS_FLAGS:
        if any(_flag_true(source, flag) for source in sources):
            unsafe.append(flag)
    return unsafe


def _flag_true(value: Any, flag: str) -> bool:
    if isinstance(value, Mapping):
        if value.get(flag) is True:
            return True
        return any(_flag_true(item, flag) for item in value.values())
    if isinstance(value, list):
        return any(_flag_true(item, flag) for item in value)
    return False


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "build_service_1_synthetic_controlled_case_candidate_chain_composition_v1",
    "SyntheticControlledCaseCandidateChainCompositionV1",
    "SyntheticControlledCaseCandidateChainCompositionResultV1",
    "CompositionStatusV1",
]
