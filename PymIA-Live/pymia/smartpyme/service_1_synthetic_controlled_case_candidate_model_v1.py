"""Pure candidate model for the Service 1 synthetic controlled case phase.

This module converts the closed documentation phase into a pure Python
candidate model. It does not execute CLI, runtime, data processing,
artifact generation, delivery, publish, notification, Servicio 2, or Phase J.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


_READY = "SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL_READY"
_BLOCKED_INVALID_INPUT = "BLOCKED_INVALID_INPUT"
_BLOCKED_MISSING_REQUIRED_REF = "BLOCKED_MISSING_REQUIRED_REF"
_BLOCKED_NOT_SYNTHETIC = "BLOCKED_NOT_SYNTHETIC"
_BLOCKED_SCOPE_NOT_SERVICE_1 = "BLOCKED_SCOPE_NOT_SERVICE_1"
_BLOCKED_MISSING_EVIDENCE = "BLOCKED_MISSING_EVIDENCE"
_BLOCKED_MISSING_KNOWN_GAPS = "BLOCKED_MISSING_KNOWN_GAPS"
_BLOCKED_PRE_RUN_NOT_READY = "BLOCKED_PRE_RUN_NOT_READY"
_BLOCKED_NEGATIVE_VARIANTS_NOT_BLOCKED = "BLOCKED_NEGATIVE_VARIANTS_NOT_BLOCKED"
_BLOCKED_UNSAFE_EXECUTION_FLAGS = "BLOCKED_UNSAFE_EXECUTION_FLAGS"
_UNKNOWN = "UNKNOWN"

_CASE_KIND = "SYNTHETIC_CONTROLLED_CASE"
_ALLOWED_SERVICE_FAMILY = "SERVICE_1"

_DANGEROUS_FLAGS = (
    "business_files_used",
    "cli_executed",
    "runtime_executed",
    "data_processed",
    "artifacts_generated",
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "owner_delivery_executed",
    "service_2_opened",
    "phase_j_opened",
)

_REQUIRED_CASE_REFS = (
    "case_ref",
    "case_name",
    "case_type",
    "operator_ref",
    "tenant_ref",
    "owner_ref",
    "packet_ref",
    "input_set_ref",
)

SyntheticControlledCaseCandidateStatusV1 = Literal[
    _READY,
    _BLOCKED_INVALID_INPUT,
    _BLOCKED_MISSING_REQUIRED_REF,
    _BLOCKED_NOT_SYNTHETIC,
    _BLOCKED_SCOPE_NOT_SERVICE_1,
    _BLOCKED_MISSING_EVIDENCE,
    _BLOCKED_MISSING_KNOWN_GAPS,
    _BLOCKED_PRE_RUN_NOT_READY,
    _BLOCKED_NEGATIVE_VARIANTS_NOT_BLOCKED,
    _BLOCKED_UNSAFE_EXECUTION_FLAGS,
    _UNKNOWN,
]


class SyntheticControlledCaseCandidateModelV1(TypedDict):
    candidate_kind: Literal["SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL"]
    status: Literal[_READY]
    ready: Literal[True]
    case_ref: str
    case_name: str
    case_type: Literal["SYNTHETIC_CONTROLLED_CASE"]
    operator_ref: str
    tenant_ref: str
    owner_ref: str
    packet_ref: str
    input_set_ref: str
    service_family: Literal["SERVICE_1"]
    synthetic_only: Literal[True]
    scope_service_1_only: Literal[True]
    evidence_categories: list[str]
    expected_columns: dict[str, list[str]]
    known_gaps: list[str]
    pre_run_gate_closed: Literal[True]
    run_request_model_ready: Literal[True]
    negative_variants_blocked: Literal[True]
    execution_candidate_alignment: Literal[True]
    full_chain_dry_binding: dict[str, str | bool]
    business_files_used: Literal[False]
    cli_executed: Literal[False]
    runtime_executed: Literal[False]
    data_processed: Literal[False]
    artifacts_generated: Literal[False]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    owner_delivery_executed: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]


class SyntheticControlledCaseCandidateModelResultV1(TypedDict):
    contract_kind: Literal["SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL"]
    status: SyntheticControlledCaseCandidateStatusV1
    ready: bool
    synthetic_controlled_case_candidate_model: SyntheticControlledCaseCandidateModelV1 | None
    blocked_reasons: list[str]
    business_files_used: Literal[False]
    cli_executed: Literal[False]
    runtime_executed: Literal[False]
    data_processed: Literal[False]
    artifacts_generated: Literal[False]
    delivery_executed: Literal[False]
    publish_executed: Literal[False]
    notification_executed: Literal[False]
    owner_delivery_executed: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]


def build_service_1_synthetic_controlled_case_candidate_model_v1(
    *,
    synthetic_case_instance: Mapping[str, Any] | None,
    pre_run_gate_closeout: Mapping[str, Any] | None,
    operator_ref: str | None,
) -> SyntheticControlledCaseCandidateModelResultV1:
    """Build a pure candidate model from the closed synthetic documentation phase."""

    if not isinstance(synthetic_case_instance, Mapping):
        return _blocked(_UNKNOWN, ["synthetic_case_instance must be a mapping"])

    if not isinstance(pre_run_gate_closeout, Mapping):
        return _blocked(_UNKNOWN, ["pre_run_gate_closeout must be a mapping"])

    case_snapshot = deepcopy(dict(synthetic_case_instance))
    gate_snapshot = deepcopy(dict(pre_run_gate_closeout))

    unsafe = _unsafe_flags(case_snapshot, gate_snapshot)
    if unsafe:
        return _blocked(
            _BLOCKED_UNSAFE_EXECUTION_FLAGS,
            [f"unsafe flag is true: {flag}" for flag in unsafe],
        )

    missing_refs = [ref for ref in _REQUIRED_CASE_REFS if not _has_text(case_snapshot.get(ref))]
    if missing_refs:
        return _blocked(
            _BLOCKED_MISSING_REQUIRED_REF,
            [f"missing required ref: {ref}" for ref in missing_refs],
        )

    if not _has_text(operator_ref):
        return _blocked(_BLOCKED_MISSING_REQUIRED_REF, ["operator_ref is required"])

    if str(case_snapshot.get("operator_ref")).strip() != operator_ref.strip():
        return _blocked(
            _BLOCKED_MISSING_REQUIRED_REF,
            ["operator_ref does not match synthetic case operator_ref"],
        )

    if case_snapshot.get("case_type") != _CASE_KIND:
        return _blocked(
            _BLOCKED_NOT_SYNTHETIC,
            ["case_type must be SYNTHETIC_CONTROLLED_CASE"],
        )

    if case_snapshot.get("synthetic_only") is not True:
        return _blocked(_BLOCKED_NOT_SYNTHETIC, ["synthetic_only must be True"])

    if case_snapshot.get("service_family") != _ALLOWED_SERVICE_FAMILY:
        return _blocked(_BLOCKED_SCOPE_NOT_SERVICE_1, ["service_family must be SERVICE_1"])

    if case_snapshot.get("scope_service_1_only") is not True:
        return _blocked(_BLOCKED_SCOPE_NOT_SERVICE_1, ["scope_service_1_only must be True"])

    evidence_categories = case_snapshot.get("evidence_categories")
    if not _non_empty_text_list(evidence_categories):
        return _blocked(
            _BLOCKED_MISSING_EVIDENCE,
            ["evidence_categories must be a non-empty list of text"],
        )

    expected_columns = case_snapshot.get("expected_columns")
    if not _valid_expected_columns(expected_columns):
        return _blocked(
            _BLOCKED_MISSING_EVIDENCE,
            ["expected_columns must be a mapping of non-empty text lists"],
        )

    known_gaps = case_snapshot.get("known_gaps")
    if not _non_empty_text_list(known_gaps):
        return _blocked(
            _BLOCKED_MISSING_KNOWN_GAPS,
            ["known_gaps must be a non-empty list of text"],
        )

    if gate_snapshot.get("pre_run_gate_closed") is not True:
        return _blocked(_BLOCKED_PRE_RUN_NOT_READY, ["pre_run_gate_closed must be True"])

    if gate_snapshot.get("run_request_model_ready") is not True:
        return _blocked(_BLOCKED_PRE_RUN_NOT_READY, ["run_request_model_ready must be True"])

    if gate_snapshot.get("negative_variants_blocked") is not True:
        return _blocked(
            _BLOCKED_NEGATIVE_VARIANTS_NOT_BLOCKED,
            ["negative_variants_blocked must be True"],
        )

    if gate_snapshot.get("execution_candidate_alignment") is not True:
        return _blocked(_BLOCKED_PRE_RUN_NOT_READY, ["execution_candidate_alignment must be True"])

    if gate_snapshot.get("full_chain_dry_binding") is not True:
        return _blocked(_BLOCKED_PRE_RUN_NOT_READY, ["full_chain_dry_binding must be True"])

    candidate: SyntheticControlledCaseCandidateModelV1 = {
        "candidate_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL",
        "status": _READY,
        "ready": True,
        "case_ref": str(case_snapshot["case_ref"]).strip(),
        "case_name": str(case_snapshot["case_name"]).strip(),
        "case_type": "SYNTHETIC_CONTROLLED_CASE",
        "operator_ref": operator_ref.strip(),
        "tenant_ref": str(case_snapshot["tenant_ref"]).strip(),
        "owner_ref": str(case_snapshot["owner_ref"]).strip(),
        "packet_ref": str(case_snapshot["packet_ref"]).strip(),
        "input_set_ref": str(case_snapshot["input_set_ref"]).strip(),
        "service_family": "SERVICE_1",
        "synthetic_only": True,
        "scope_service_1_only": True,
        "evidence_categories": [str(item).strip() for item in evidence_categories],
        "expected_columns": {
            str(key).strip(): [str(item).strip() for item in value]
            for key, value in expected_columns.items()
        },
        "known_gaps": [str(item).strip() for item in known_gaps],
        "pre_run_gate_closed": True,
        "run_request_model_ready": True,
        "negative_variants_blocked": True,
        "execution_candidate_alignment": True,
        "full_chain_dry_binding": {
            "readiness_bound": True,
            "evidence_packet_bound": True,
            "operator_supervision_bound": True,
            "execution_candidate_bound": True,
            "run_result_bound": "DRY_PLACEHOLDER_ONLY",
            "abort_rollback_bound": "DRY_BOUNDARY_ONLY",
            "delivery_review_bound": "DRY_BOUNDARY_ONLY",
        },
        **_safe_flags(),
    }

    return {
        "contract_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL",
        "status": _READY,
        "ready": True,
        "synthetic_controlled_case_candidate_model": candidate,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _blocked(
    status: str,
    reasons: list[str],
) -> SyntheticControlledCaseCandidateModelResultV1:
    return {
        "contract_kind": "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL",
        "status": status,
        "ready": False,
        "synthetic_controlled_case_candidate_model": None,
        "blocked_reasons": list(reasons),
        **_safe_flags(),
    }


def _unsafe_flags(*sources: Mapping[str, Any]) -> list[str]:
    unsafe: list[str] = []
    for flag in _DANGEROUS_FLAGS:
        if any(source.get(flag) is True for source in sources):
            unsafe.append(flag)
    return unsafe


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_text_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_has_text(item) for item in value)


def _valid_expected_columns(value: Any) -> bool:
    if not isinstance(value, Mapping) or not value:
        return False
    return all(_has_text(key) and _non_empty_text_list(items) for key, items in value.items())


__all__ = [
    "build_service_1_synthetic_controlled_case_candidate_model_v1",
    "SyntheticControlledCaseCandidateModelV1",
    "SyntheticControlledCaseCandidateModelResultV1",
    "SyntheticControlledCaseCandidateStatusV1",
]
