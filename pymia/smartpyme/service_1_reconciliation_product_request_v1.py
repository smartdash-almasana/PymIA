"""Product boundary for governed reconciliation review in Servicio 1.

This module receives an explicit reconciliation request whose source packets
have already passed Servicio 1 semantic governance. It delegates preparation
to the reconciliation request gate and then routes ready candidates to the
existing assisted-review adapter.

It never reads files, accepts matches, writes accounting entries, creates a
delivery, or closes a reconciliation automatically.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from pymia.smartpyme.service_1_reconciliation_candidate_to_assisted_review_v1 import (
    STATUS_BLOCKED as REVIEW_STATUS_BLOCKED,
    STATUS_NEEDS_EVIDENCE as REVIEW_STATUS_NEEDS_EVIDENCE,
    build_service_1_reconciliation_assisted_review_v1,
)
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    STATUS_BLOCKED as GATE_STATUS_BLOCKED,
    STATUS_MISSING_REQUIRED_FIELD,
    STATUS_MISSING_REQUIRED_SOURCE,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY as GATE_STATUS_READY,
    build_service_1_reconciliation_request_gate_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_RECONCILIATION_PRODUCT_REQUEST_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
PACKET_TYPE: Final[str] = "RECONCILIATION_PRODUCT_REQUEST"

STATUS_REVIEW_READY: Final[str] = "RECONCILIATION_REVIEW_READY"
STATUS_NEEDS_OWNER: Final[str] = "RECONCILIATION_NEEDS_OWNER_CONFIRMATION"
STATUS_NEEDS_EVIDENCE: Final[str] = "RECONCILIATION_NEEDS_EVIDENCE"
STATUS_BLOCKED: Final[str] = "RECONCILIATION_BLOCKED"
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {
        STATUS_REVIEW_READY,
        STATUS_NEEDS_OWNER,
        STATUS_NEEDS_EVIDENCE,
        STATUS_BLOCKED,
    }
)

_SAFETY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_reconciliation_product_request_v1(
    *,
    reconciliation_request: Mapping[str, Any],
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Prepare one product-level reconciliation review request."""
    if any(
        (
            runtime_authorized,
            tool_execution_authorized,
            product_ready,
            delivery_authorized,
            diagnosis_generated,
        )
    ):
        return _blocked(reason="REQUEST_SAFETY_FLAGS_FORBIDDEN")
    if not isinstance(reconciliation_request, Mapping) or not reconciliation_request:
        return _blocked(reason="RECONCILIATION_REQUEST_REQUIRED")
    if any(reconciliation_request.get(flag) is True for flag in _SAFETY_FLAGS):
        return _blocked(reason="RECONCILIATION_REQUEST_SAFETY_FLAGS_FORBIDDEN")

    case_id = _text(reconciliation_request.get("case_id"))
    reconciliation_type = _text(
        reconciliation_request.get("reconciliation_type")
    )
    source_packets = reconciliation_request.get("source_packets")
    if not isinstance(source_packets, Sequence) or isinstance(
        source_packets, (str, bytes)
    ):
        return _blocked(
            reason="SOURCE_PACKETS_REQUIRED",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
        )

    options = reconciliation_request.get("options")
    if options is not None and not isinstance(options, Mapping):
        return _blocked(
            reason="OPTIONS_MUST_BE_A_MAPPING",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
        )

    gate_packet = build_service_1_reconciliation_request_gate_v1(
        case_id=case_id,
        owner_requested=reconciliation_request.get("owner_requested") is True,
        reconciliation_type=reconciliation_type,
        source_packets=source_packets,
    )
    gate_status = _text(gate_packet.get("status"))

    if gate_status == STATUS_NEEDS_OWNER_CONFIRMATION:
        return _packet(
            status=STATUS_NEEDS_OWNER,
            reason=_text(gate_packet.get("reason")) or None,
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=None,
            next_allowed_action="confirm_reconciliation_source_meanings",
        )
    if gate_status in {
        STATUS_MISSING_REQUIRED_SOURCE,
        STATUS_MISSING_REQUIRED_FIELD,
    }:
        return _packet(
            status=STATUS_NEEDS_EVIDENCE,
            reason=_text(gate_packet.get("reason")) or None,
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=None,
            next_allowed_action="provide_reconciliation_evidence",
        )
    if gate_status == GATE_STATUS_BLOCKED:
        return _packet(
            status=STATUS_BLOCKED,
            reason=_text(gate_packet.get("reason")) or "REQUEST_GATE_BLOCKED",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=None,
            next_allowed_action="fix_reconciliation_request",
        )
    if gate_status != GATE_STATUS_READY:
        return _packet(
            status=STATUS_BLOCKED,
            reason="REQUEST_GATE_STATUS_INVALID",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=None,
            next_allowed_action="fix_reconciliation_request",
        )

    assisted_review = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=gate_packet,
        options=dict(options or {}),
    )
    review_status = _text(assisted_review.get("status"))
    if review_status == REVIEW_STATUS_BLOCKED:
        return _packet(
            status=STATUS_BLOCKED,
            reason=_text(assisted_review.get("reason"))
            or "ASSISTED_REVIEW_BLOCKED",
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=assisted_review,
            next_allowed_action="fix_reconciliation_candidate",
        )
    if review_status == REVIEW_STATUS_NEEDS_EVIDENCE:
        return _packet(
            status=STATUS_NEEDS_EVIDENCE,
            reason=None,
            case_id=case_id,
            reconciliation_type=reconciliation_type,
            gate_packet=gate_packet,
            assisted_review=assisted_review,
            next_allowed_action="provide_reconciliation_evidence",
        )

    return _packet(
        status=STATUS_REVIEW_READY,
        reason=None,
        case_id=case_id,
        reconciliation_type=reconciliation_type,
        gate_packet=gate_packet,
        assisted_review=assisted_review,
        next_allowed_action="human_reconciliation_review",
    )


def _packet(
    *,
    status: str,
    reason: str | None,
    case_id: str,
    reconciliation_type: str,
    gate_packet: Mapping[str, Any] | None,
    assisted_review: Mapping[str, Any] | None,
    next_allowed_action: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "reason": reason,
        "case_id": case_id,
        "reconciliation_type": reconciliation_type,
        "gate_packet": dict(gate_packet) if gate_packet is not None else None,
        "assisted_review": (
            dict(assisted_review) if assisted_review is not None else None
        ),
        "requires_human_review": True,
        "next_allowed_action": next_allowed_action,
        "io_performed": False,
        "files_created": [],
        "api_used": False,
        "llm_used": False,
        **_safety_flags(),
    }


def _blocked(
    *,
    reason: str,
    case_id: str = "",
    reconciliation_type: str = "",
) -> dict[str, Any]:
    return _packet(
        status=STATUS_BLOCKED,
        reason=reason,
        case_id=case_id,
        reconciliation_type=reconciliation_type,
        gate_packet=None,
        assisted_review=None,
        next_allowed_action="fix_reconciliation_request",
    )


def _text(value: object) -> str:
    return str(value or "").strip()


def _safety_flags() -> dict[str, bool]:
    return {
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_REVIEW_READY",
    "STATUS_NEEDS_OWNER",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_BLOCKED",
    "ALLOWED_STATUSES",
    "build_service_1_reconciliation_product_request_v1",
]
