from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
PATCH_KIND: Final[str] = "CASE_TRUTH_PATCH_CANDIDATE"
RERUN_KIND: Final[str] = "AUTONOMOUS_RERUN_CANDIDATE"
DEFAULT_RECALCULATION_TARGETS: Final[tuple[str, ...]] = (
    "case_truth_integration",
    "auto_tool_plan_candidate",
    "explicit_request_candidate_gate",
    "pipeline_request_candidate_gate",
)

OwnerReentryToAutonomousRerunStatusV1 = Literal[
    "AUTONOMOUS_RERUN_CANDIDATE_READY",
    "BLOCKED_INVALID_PATCH_CANDIDATE",
    "BLOCKED_MISSING_CASE_TRUTH",
    "BLOCKED_MISSING_PRIOR_CHAIN_CONTEXT",
    "UNKNOWN",
]


class Service1OwnerReentryToAutonomousRerunInputV1(TypedDict):
    case_truth_patch_candidate: dict[str, Any] | None
    current_case_truth: dict[str, Any] | None
    prior_chain_context: dict[str, Any] | None
    notes: list[str]


class Service1AutonomousRerunCandidateV1(TypedDict):
    rerun_kind: Literal["AUTONOMOUS_RERUN_CANDIDATE"]
    source_case_truth_patch_ref: str
    source_case_truth_ref: str
    prior_chain_refs: list[str]
    recalculation_targets: list[str]
    patch_applied: Literal[False]
    runtime_authorized: Literal[False]
    rerun_authorized: Literal[False]
    autonomous_rerun_authorized: Literal[False]


class Service1OwnerReentryToAutonomousRerunResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: OwnerReentryToAutonomousRerunStatusV1
    autonomous_rerun_candidate: Service1AutonomousRerunCandidateV1 | None
    blocked_reason: str | None
    patch_applied: Literal[False]
    runtime_authorized: Literal[False]
    rerun_authorized: Literal[False]
    autonomous_rerun_authorized: Literal[False]
    notes: list[str]


def build_service_1_owner_reentry_to_autonomous_rerun_v1(
    reentry_input: Service1OwnerReentryToAutonomousRerunInputV1,
) -> Service1OwnerReentryToAutonomousRerunResultV1:
    """Build a non-executable autonomous rerun candidate from owner reentry.

    This pure validator does not apply the patch, persist state, execute tools,
    call runners, call pipelines, publish delivery, or authorize rerun. It only
    preserves the prior chain context and declares deterministic recalculation
    targets for a later explicit gate.
    """
    case_truth_patch_candidate = reentry_input.get("case_truth_patch_candidate")
    if not isinstance(case_truth_patch_candidate, dict) or not case_truth_patch_candidate:
        return _result(
            status="BLOCKED_INVALID_PATCH_CANDIDATE",
            blocked_reason="case_truth_patch_candidate_required",
            notes=["Autonomous rerun candidate requires a case truth patch candidate."],
        )

    current_case_truth = reentry_input.get("current_case_truth")
    if not isinstance(current_case_truth, dict) or not current_case_truth:
        return _result(
            status="BLOCKED_MISSING_CASE_TRUTH",
            blocked_reason="current_case_truth_required",
            notes=["Autonomous rerun candidate requires current case truth."],
        )

    prior_chain_context = reentry_input.get("prior_chain_context")
    if not isinstance(prior_chain_context, dict) or not prior_chain_context:
        return _result(
            status="BLOCKED_MISSING_PRIOR_CHAIN_CONTEXT",
            blocked_reason="prior_chain_context_required",
            notes=["Autonomous rerun candidate requires prior chain context."],
        )

    invalid_reason = _validate_patch_candidate(case_truth_patch_candidate)
    if invalid_reason is not None:
        return _result(
            status="BLOCKED_INVALID_PATCH_CANDIDATE",
            blocked_reason=invalid_reason,
            notes=["Patch candidate is not valid for autonomous rerun planning."],
        )

    if current_case_truth.get("status") is None:
        return _result(
            status="BLOCKED_MISSING_CASE_TRUTH",
            blocked_reason="current_case_truth_status_required",
            notes=["Current case truth must expose status before rerun planning."],
        )

    prior_chain_refs = _prior_chain_refs(prior_chain_context)
    if not prior_chain_refs:
        return _result(
            status="BLOCKED_MISSING_PRIOR_CHAIN_CONTEXT",
            blocked_reason="prior_chain_refs_required",
            notes=["Prior chain context must include chain references."],
        )

    recalculation_targets = _recalculation_targets(prior_chain_context)
    if not recalculation_targets:
        return _result(
            status="UNKNOWN",
            blocked_reason="recalculation_targets_required",
            notes=["Autonomous rerun candidate requires recalculation targets."],
        )

    candidate: Service1AutonomousRerunCandidateV1 = {
        "rerun_kind": RERUN_KIND,
        "source_case_truth_patch_ref": _source_case_truth_patch_ref(case_truth_patch_candidate),
        "source_case_truth_ref": _source_case_truth_ref(current_case_truth),
        "prior_chain_refs": prior_chain_refs,
        "recalculation_targets": recalculation_targets,
        "patch_applied": False,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "autonomous_rerun_authorized": False,
    }

    return _result(
        status="AUTONOMOUS_RERUN_CANDIDATE_READY",
        autonomous_rerun_candidate=candidate,
        notes=["Autonomous rerun candidate created without applying patch or authorizing rerun."],
    )


def _validate_patch_candidate(case_truth_patch_candidate: dict[str, Any]) -> str | None:
    if case_truth_patch_candidate.get("patch_kind") != PATCH_KIND:
        return "patch_kind_must_be_case_truth_patch_candidate"
    if case_truth_patch_candidate.get("patch_applied") is not False:
        return "patch_candidate_must_not_be_applied"
    if case_truth_patch_candidate.get("runtime_authorized") is not False:
        return "patch_candidate_runtime_authorized_must_be_false"
    if case_truth_patch_candidate.get("rerun_authorized") is not False:
        return "patch_candidate_rerun_authorized_must_be_false"
    if case_truth_patch_candidate.get("autonomous_rerun_authorized") is not False:
        return "patch_candidate_autonomous_rerun_authorized_must_be_false"
    has_content = any(
        bool(case_truth_patch_candidate.get(key))
        for key in ("confirmations", "corrections", "declared_evidence_refs", "owner_notes")
    )
    if not has_content:
        return "patch_candidate_has_no_reentry_content"
    return None


def _prior_chain_refs(prior_chain_context: dict[str, Any]) -> list[str]:
    direct_refs = _clean_refs(prior_chain_context.get("prior_chain_refs", []))
    if direct_refs:
        return direct_refs
    refs: list[str] = []
    for key in (
        "case_truth_integration_ref",
        "tool_plan_candidate_ref",
        "explicit_request_candidate_ref",
        "pipeline_request_candidate_ref",
        "execution_gate_ref",
        "pipeline_run_ref",
        "delivery_release_candidate_ref",
        "owner_delivery_packet_ref",
    ):
        value = prior_chain_context.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value)
    return refs


def _recalculation_targets(prior_chain_context: dict[str, Any]) -> list[str]:
    explicit_targets = _clean_refs(prior_chain_context.get("recalculation_targets", []))
    if explicit_targets:
        return explicit_targets
    return list(DEFAULT_RECALCULATION_TARGETS)


def _source_case_truth_patch_ref(case_truth_patch_candidate: dict[str, Any]) -> str:
    for key in ("case_truth_patch_ref", "source_owner_packet_ref", "source_case_truth_ref"):
        value = case_truth_patch_candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "case_truth_patch:unknown"


def _source_case_truth_ref(current_case_truth: dict[str, Any]) -> str:
    for key in ("case_truth_ref", "case_id", "source_case_ref"):
        value = current_case_truth.get(key)
        if isinstance(value, str) and value.strip():
            return value
    status = current_case_truth.get("status")
    if isinstance(status, str) and status.strip():
        return f"case_truth:{status}"
    return "case_truth:unknown"


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _result(
    *,
    status: OwnerReentryToAutonomousRerunStatusV1,
    autonomous_rerun_candidate: Service1AutonomousRerunCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1OwnerReentryToAutonomousRerunResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "autonomous_rerun_candidate": autonomous_rerun_candidate,
        "blocked_reason": blocked_reason,
        "patch_applied": False,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "autonomous_rerun_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "PATCH_KIND",
    "RERUN_KIND",
    "DEFAULT_RECALCULATION_TARGETS",
    "Service1OwnerReentryToAutonomousRerunInputV1",
    "Service1AutonomousRerunCandidateV1",
    "Service1OwnerReentryToAutonomousRerunResultV1",
    "build_service_1_owner_reentry_to_autonomous_rerun_v1",
]
