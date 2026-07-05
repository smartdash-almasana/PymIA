from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_SHADOW_EVIDENCE_OPERATOR_REVIEW_PACKET_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
READY_EVIDENCE_STATUS: Final[str] = "SHADOW_EVIDENCE_READY"

OperatorReviewPacketStatusV1 = Literal[
    "OPERATOR_REVIEW_PACKET_READY",
    "BLOCKED_INVALID_SHADOW_EVIDENCE",
    "BLOCKED_SHADOW_EVIDENCE_NOT_READY",
    "BLOCKED_OWNER_PUBLICATION_ATTEMPT",
    "UNKNOWN",
]


class Service1ShadowEvidenceOperatorReviewPacketInputV1(TypedDict):
    shadow_evidence: dict[str, Any]
    operator_ref: str
    review_packet_ref: str
    notes: list[str]
    owner_publication_requested: bool


class Service1ShadowEvidenceOperatorReviewPacketV1(TypedDict):
    schema_version: str
    service_name: str
    status: OperatorReviewPacketStatusV1
    blocked_reason: str | None
    review_packet_ref: str | None
    operator_ref: str | None
    evidence_ref: str | None
    case_id: str | None
    run_id: str | None
    review_required: Literal[True]
    owner_publication_authorized: Literal[False]
    owner_delivery_authorized: Literal[False]
    autonomous_delivery_authorized: Literal[False]
    runtime_authorized: Literal[False]
    pipeline_called: Literal[False]
    processed_tool_refs: list[str]
    processed_request_count: int
    review_items: list[dict[str, Any]]
    operator_summary: dict[str, Any] | None
    notes: list[str]


def build_service_1_shadow_evidence_operator_review_packet_v1(
    packet_input: Service1ShadowEvidenceOperatorReviewPacketInputV1,
) -> Service1ShadowEvidenceOperatorReviewPacketV1:
    """Build a review-only operator packet from shadow evidence.

    This module is pure: it does not write files, publish owner delivery, call the
    real runner, call the pipeline, use storage, API, workers, clocks, or LLMs.
    """
    if packet_input.get("owner_publication_requested") is True:
        return _result(
            status="BLOCKED_OWNER_PUBLICATION_ATTEMPT",
            blocked_reason="owner_publication_requested_true",
            notes=["Shadow evidence cannot be published to owner as delivery."],
        )

    operator_ref = packet_input.get("operator_ref")
    if not isinstance(operator_ref, str) or not operator_ref.strip():
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="operator_ref_required",
            notes=["Operator review packet requires operator_ref."],
        )

    review_packet_ref = packet_input.get("review_packet_ref")
    if not isinstance(review_packet_ref, str) or not review_packet_ref.strip():
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="review_packet_ref_required",
            operator_ref=operator_ref,
            notes=["Operator review packet requires review_packet_ref."],
        )

    shadow_evidence = packet_input.get("shadow_evidence")
    if not isinstance(shadow_evidence, dict):
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="shadow_evidence_must_be_dict",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            notes=["Operator review packet requires dict shadow_evidence."],
        )

    if shadow_evidence.get("status") != READY_EVIDENCE_STATUS:
        return _result(
            status="BLOCKED_SHADOW_EVIDENCE_NOT_READY",
            blocked_reason="shadow_evidence_not_ready",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["Shadow evidence must be SHADOW_EVIDENCE_READY before operator review."],
        )

    if shadow_evidence.get("runtime_authorized") is True or shadow_evidence.get("pipeline_called") is True:
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="shadow_evidence_must_not_authorize_runtime_or_call_pipeline",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["Operator review rejects runtime-authorized or pipeline-called shadow evidence."],
        )

    if shadow_evidence.get("delivery_authorized") is True or shadow_evidence.get("owner_delivery_authorized") is True or shadow_evidence.get("autonomous_delivery_authorized") is True:
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="shadow_evidence_must_not_authorize_delivery",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["Operator review rejects delivery-authorized shadow evidence."],
        )

    processed_tool_refs = shadow_evidence.get("processed_tool_refs")
    processed_request_count = shadow_evidence.get("processed_request_count")
    if not isinstance(processed_tool_refs, list) or not processed_tool_refs:
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="processed_tool_refs_required",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["Operator review requires non-empty processed_tool_refs."],
        )
    if not isinstance(processed_request_count, int) or processed_request_count != len(processed_tool_refs):
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="processed_request_count_mismatch",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["processed_request_count must match processed_tool_refs length."],
        )

    normalized_tool_refs: list[str] = []
    for tool_ref in processed_tool_refs:
        if not isinstance(tool_ref, str) or not tool_ref.strip():
            return _result(
                status="BLOCKED_INVALID_SHADOW_EVIDENCE",
                blocked_reason="processed_tool_ref_must_be_string",
                operator_ref=operator_ref,
                review_packet_ref=review_packet_ref,
                shadow_evidence=shadow_evidence,
                notes=["Every processed_tool_ref must be a non-empty string."],
            )
        normalized_tool_refs.append(tool_ref)

    evidence_packet = shadow_evidence.get("evidence_packet")
    if not isinstance(evidence_packet, dict):
        return _result(
            status="BLOCKED_INVALID_SHADOW_EVIDENCE",
            blocked_reason="evidence_packet_required",
            operator_ref=operator_ref,
            review_packet_ref=review_packet_ref,
            shadow_evidence=shadow_evidence,
            notes=["Operator review requires evidence_packet."],
        )

    review_items = _build_review_items(normalized_tool_refs)
    operator_summary = {
        "review_packet_ref": review_packet_ref,
        "operator_ref": operator_ref,
        "evidence_ref": shadow_evidence.get("evidence_ref"),
        "case_id": shadow_evidence.get("case_id"),
        "run_id": shadow_evidence.get("run_id"),
        "processed_tool_refs": list(normalized_tool_refs),
        "processed_request_count": processed_request_count,
        "review_required": True,
        "owner_publication_authorized": False,
        "operator_decision_required": "APPROVE_FOR_INTERNAL_NEXT_STEP_OR_REJECT",
    }

    return _result(
        status="OPERATOR_REVIEW_PACKET_READY",
        blocked_reason=None,
        operator_ref=operator_ref,
        review_packet_ref=review_packet_ref,
        shadow_evidence=shadow_evidence,
        processed_tool_refs=normalized_tool_refs,
        processed_request_count=processed_request_count,
        review_items=review_items,
        operator_summary=operator_summary,
        notes=list(packet_input.get("notes", [])) + ["Operator review packet created from shadow evidence without owner publication."],
    )


def _build_review_items(processed_tool_refs: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "item_ref": f"operator_review_item:{index}:{tool_ref}",
            "tool_ref": tool_ref,
            "required_check": "OPERATOR_VALIDATE_SHADOW_EVIDENCE_BEFORE_ANY_OWNER_DELIVERY",
            "status": "PENDING_OPERATOR_REVIEW",
            "owner_visible": False,
        }
        for index, tool_ref in enumerate(processed_tool_refs, start=1)
    ]


def _result(
    *,
    status: OperatorReviewPacketStatusV1,
    blocked_reason: str | None,
    operator_ref: str | None = None,
    review_packet_ref: str | None = None,
    shadow_evidence: dict[str, Any] | None = None,
    processed_tool_refs: list[str] | None = None,
    processed_request_count: int = 0,
    review_items: list[dict[str, Any]] | None = None,
    operator_summary: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> Service1ShadowEvidenceOperatorReviewPacketV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "blocked_reason": blocked_reason,
        "review_packet_ref": review_packet_ref,
        "operator_ref": operator_ref,
        "evidence_ref": shadow_evidence.get("evidence_ref") if isinstance(shadow_evidence, dict) else None,
        "case_id": shadow_evidence.get("case_id") if isinstance(shadow_evidence, dict) else None,
        "run_id": shadow_evidence.get("run_id") if isinstance(shadow_evidence, dict) else None,
        "review_required": True,
        "owner_publication_authorized": False,
        "owner_delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "runtime_authorized": False,
        "pipeline_called": False,
        "processed_tool_refs": list(processed_tool_refs or []),
        "processed_request_count": processed_request_count,
        "review_items": list(review_items or []),
        "operator_summary": operator_summary,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "READY_EVIDENCE_STATUS",
    "Service1ShadowEvidenceOperatorReviewPacketInputV1",
    "Service1ShadowEvidenceOperatorReviewPacketV1",
    "build_service_1_shadow_evidence_operator_review_packet_v1",
]
