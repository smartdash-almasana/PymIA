from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_OWNER_FEEDBACK_TO_CASE_TRUTH_PATCH_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
OWNER_PACKET_KIND: Final[str] = "OWNER_DELIVERY_PACKET_CANDIDATE"
PATCH_KIND: Final[str] = "CASE_TRUTH_PATCH_CANDIDATE"

OwnerFeedbackPatchStatusV1 = Literal[
    "CASE_TRUTH_PATCH_CANDIDATE_READY",
    "BLOCKED_INVALID_FEEDBACK",
    "BLOCKED_MISSING_DELIVERY_PACKET",
    "BLOCKED_MISSING_CASE_TRUTH",
    "UNKNOWN",
]


class Service1OwnerFeedbackToCaseTruthPatchInputV1(TypedDict):
    structured_owner_feedback: dict[str, Any]
    owner_delivery_packet_candidate: dict[str, Any] | None
    current_case_truth: dict[str, Any] | None
    notes: list[str]


class Service1CaseTruthPatchCandidateV1(TypedDict):
    patch_kind: Literal["CASE_TRUTH_PATCH_CANDIDATE"]
    source_owner_packet_ref: str
    source_case_truth_ref: str
    confirmations: dict[str, Any]
    corrections: dict[str, Any]
    declared_evidence_refs: list[str]
    owner_notes: list[str]
    patch_applied: Literal[False]
    runtime_authorized: Literal[False]
    rerun_authorized: Literal[False]
    autonomous_rerun_authorized: Literal[False]


class Service1OwnerFeedbackToCaseTruthPatchResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: OwnerFeedbackPatchStatusV1
    case_truth_patch_candidate: Service1CaseTruthPatchCandidateV1 | None
    blocked_reason: str | None
    runtime_authorized: Literal[False]
    rerun_authorized: Literal[False]
    patch_applied: Literal[False]
    autonomous_rerun_authorized: Literal[False]
    notes: list[str]


def build_service_1_owner_feedback_to_case_truth_patch_v1(
    patch_input: Service1OwnerFeedbackToCaseTruthPatchInputV1,
) -> Service1OwnerFeedbackToCaseTruthPatchResultV1:
    """Build a candidate case-truth patch from structured PyME owner feedback.

    This pure transformer does not parse free text, apply patches, persist state,
    execute tools, rerun pipelines, publish delivery, or authorize runtime. It only
    maps deterministic feedback fields into a non-applied patch candidate.
    """
    owner_delivery_packet_candidate = patch_input.get("owner_delivery_packet_candidate")
    if not isinstance(owner_delivery_packet_candidate, dict) or not owner_delivery_packet_candidate:
        return _result(
            status="BLOCKED_MISSING_DELIVERY_PACKET",
            blocked_reason="owner_delivery_packet_candidate_required",
            notes=["Owner feedback patch requires an owner delivery packet candidate."],
        )

    current_case_truth = patch_input.get("current_case_truth")
    if not isinstance(current_case_truth, dict) or not current_case_truth:
        return _result(
            status="BLOCKED_MISSING_CASE_TRUTH",
            blocked_reason="current_case_truth_required",
            notes=["Owner feedback patch requires current case truth."],
        )

    structured_owner_feedback = patch_input.get("structured_owner_feedback")
    if not isinstance(structured_owner_feedback, dict) or not structured_owner_feedback:
        return _result(
            status="BLOCKED_INVALID_FEEDBACK",
            blocked_reason="structured_owner_feedback_required",
            notes=["Structured owner feedback is required."],
        )

    if owner_delivery_packet_candidate.get("packet_kind") != OWNER_PACKET_KIND:
        return _result(
            status="BLOCKED_MISSING_DELIVERY_PACKET",
            blocked_reason="owner_delivery_packet_candidate_kind_required",
            notes=["Feedback must target an OWNER_DELIVERY_PACKET_CANDIDATE."],
        )

    if owner_delivery_packet_candidate.get("publishable") is not False:
        return _result(
            status="BLOCKED_MISSING_DELIVERY_PACKET",
            blocked_reason="owner_delivery_packet_must_not_be_publishable",
            notes=["Owner packet candidate must remain non-publishable."],
        )

    if current_case_truth.get("status") is None:
        return _result(
            status="BLOCKED_MISSING_CASE_TRUTH",
            blocked_reason="current_case_truth_status_required",
            notes=["Current case truth must expose a status before patch candidate creation."],
        )

    confirmations = _clean_mapping(structured_owner_feedback.get("confirmations", {}))
    corrections = _clean_mapping(structured_owner_feedback.get("corrections", {}))
    declared_evidence_refs = _clean_refs(structured_owner_feedback.get("declared_evidence_refs", []))
    owner_notes = _clean_refs(structured_owner_feedback.get("owner_notes", []))

    if not confirmations and not corrections and not declared_evidence_refs and not owner_notes:
        return _result(
            status="BLOCKED_INVALID_FEEDBACK",
            blocked_reason="structured_owner_feedback_has_no_patch_content",
            notes=["Feedback must contain confirmations, corrections, declared evidence refs, or owner notes."],
        )

    candidate: Service1CaseTruthPatchCandidateV1 = {
        "patch_kind": PATCH_KIND,
        "source_owner_packet_ref": _source_owner_packet_ref(owner_delivery_packet_candidate),
        "source_case_truth_ref": _source_case_truth_ref(current_case_truth),
        "confirmations": confirmations,
        "corrections": corrections,
        "declared_evidence_refs": declared_evidence_refs,
        "owner_notes": owner_notes,
        "patch_applied": False,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "autonomous_rerun_authorized": False,
    }

    return _result(
        status="CASE_TRUTH_PATCH_CANDIDATE_READY",
        case_truth_patch_candidate=candidate,
        notes=["Case truth patch candidate created without applying changes or authorizing rerun."],
    )


def _source_owner_packet_ref(owner_delivery_packet_candidate: dict[str, Any]) -> str:
    for key in ("source_pipeline_run_ref", "packet_ref", "case_id"):
        value = owner_delivery_packet_candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "owner_delivery_packet:unknown"


def _source_case_truth_ref(current_case_truth: dict[str, Any]) -> str:
    for key in ("case_truth_ref", "case_id", "source_case_ref"):
        value = current_case_truth.get(key)
        if isinstance(value, str) and value.strip():
            return value
    status = current_case_truth.get("status")
    if isinstance(status, str) and status.strip():
        return f"case_truth:{status}"
    return "case_truth:unknown"


def _clean_mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _copy_scalar_or_container(item) for key, item in value.items() if isinstance(key, str) and key.strip()}


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _copy_scalar_or_container(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _copy_scalar_or_container(item) for key, item in value.items() if isinstance(key, str)}
    if isinstance(value, list):
        return [_copy_scalar_or_container(item) for item in value]
    return value


def _result(
    *,
    status: OwnerFeedbackPatchStatusV1,
    case_truth_patch_candidate: Service1CaseTruthPatchCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1OwnerFeedbackToCaseTruthPatchResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "case_truth_patch_candidate": case_truth_patch_candidate,
        "blocked_reason": blocked_reason,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "patch_applied": False,
        "autonomous_rerun_authorized": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "OWNER_PACKET_KIND",
    "PATCH_KIND",
    "Service1OwnerFeedbackToCaseTruthPatchInputV1",
    "Service1CaseTruthPatchCandidateV1",
    "Service1OwnerFeedbackToCaseTruthPatchResultV1",
    "build_service_1_owner_feedback_to_case_truth_patch_v1",
]
