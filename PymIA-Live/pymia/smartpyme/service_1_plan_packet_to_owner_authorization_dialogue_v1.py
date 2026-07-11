"""
Service 1 Plan Packet -> Owner Authorization Dialogue V1

Fail-closed owner-authorization dialogue for the Servicio 1 assisted flow.

Flow position:

    execution_plan_packet (READY) -> owner AUTHORIZATION dialogue (this module)

The module takes a READY execution plan packet and emits the owner
authorization dialogue:

- without an ``owner_authorization`` answer -> OWNER_AUTHORIZATION_REQUIRED
  (emits the consent prompt + the planned steps for review),
- with ``owner_authorization == "accept"`` -> OWNER_AUTHORIZATION_ACCEPTED,
- with ``owner_authorization == "reject"`` -> OWNER_AUTHORIZATION_REJECTED.

The module NEVER executes tools, NEVER creates delivery, and NEVER authorizes
runtime/product/delivery/diagnosis. ``execution_executed`` and
``delivery_created`` are always False; all safety flags are always False.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_controlled_execution_ready_to_plan_packet_v1 import (
    STATUS_PLAN_READY as PLAN_STATUS_READY,
)

SCHEMA_VERSION = "SERVICE_1_PLAN_PACKET_TO_OWNER_AUTHORIZATION_DIALOGUE_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "PLAN_PACKET_TO_OWNER_AUTHORIZATION_DIALOGUE"

STATUS_REQUIRED = "OWNER_AUTHORIZATION_REQUIRED"
STATUS_ACCEPTED = "OWNER_AUTHORIZATION_ACCEPTED"
STATUS_REJECTED = "OWNER_AUTHORIZATION_REJECTED"
STATUS_BLOCKED = "BLOCKED"

AUTH_ACCEPT = "accept"
AUTH_REJECT = "reject"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_PLAN_NOT_DICT = "PLAN_PACKET_NOT_DICT"
BLOCK_PLAN_WRONG_STATUS = "PLAN_WRONG_STATUS"
BLOCK_PLAN_FLAGS_FORBIDDEN = "PLAN_SAFETY_FLAGS_FORBIDDEN"
BLOCK_MISSING_PLANNED_STEPS = "MISSING_PLANNED_STEPS"

_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_owner_authorization_dialogue_from_plan_packet_v1(
    *,
    plan_packet: Any,
    owner_authorization: Any = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Emit the owner authorization dialogue for a READY execution plan.

    Args:
        plan_packet: Output of the plan packet builder (status EXECUTION_PLAN_READY).
        owner_authorization: Optional "accept"/"reject". When omitted -> REQUIRED.

    Returns:
        An authorization dialogue packet dict with status one of REQUIRED,
        ACCEPTED, REJECTED, or BLOCKED (with ``blocked_reason``).
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(plan_packet, dict) or not plan_packet:
        return _blocked(BLOCK_PLAN_NOT_DICT)

    if any(plan_packet.get(flag) for flag in _FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_PLAN_FLAGS_FORBIDDEN,
            case_id=plan_packet.get("case_id"),
            source_kind=plan_packet.get("source_kind"),
            filename=plan_packet.get("filename"),
        )

    if plan_packet.get("status") != PLAN_STATUS_READY:
        return _blocked(
            BLOCK_PLAN_WRONG_STATUS,
            case_id=plan_packet.get("case_id"),
            source_kind=plan_packet.get("source_kind"),
            filename=plan_packet.get("filename"),
        )

    planned_steps = plan_packet.get("planned_steps")
    if not isinstance(planned_steps, (list, tuple)) or not planned_steps:
        return _blocked(
            BLOCK_MISSING_PLANNED_STEPS,
            case_id=plan_packet.get("case_id"),
            source_kind=plan_packet.get("source_kind"),
            filename=plan_packet.get("filename"),
        )

    case_id = plan_packet.get("case_id")
    source_kind = plan_packet.get("source_kind")
    filename = plan_packet.get("filename")

    # No answer yet -> emit the consent dialogue.
    if owner_authorization is None:
        return _dialogue(
            status=STATUS_REQUIRED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            plan_packet=plan_packet,
        )

    answer = str(owner_authorization).strip().lower()
    if answer == AUTH_ACCEPT:
        return _dialogue(
            status=STATUS_ACCEPTED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            plan_packet=plan_packet,
        )
    if answer == AUTH_REJECT:
        return _dialogue(
            status=STATUS_REJECTED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            plan_packet=plan_packet,
        )

    # Any other answer is not a valid authorization decision -> BLOCKED.
    return _blocked(
        BLOCK_PLAN_WRONG_STATUS,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
    )


def _dialogue(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    plan_packet: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "candidate_count": plan_packet.get("candidate_count"),
        "roles": list(plan_packet.get("roles") or []),
        "planned_steps": list(plan_packet.get("planned_steps") or []),
        "authorization_decision": status,
        "execution_executed": False,
        "delivery_created": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "candidate_count": 0,
        "roles": [],
        "planned_steps": [],
        "authorization_decision": None,
        "execution_executed": False,
        "delivery_created": False,
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
    "STATUS_REQUIRED",
    "STATUS_ACCEPTED",
    "STATUS_REJECTED",
    "STATUS_BLOCKED",
    "AUTH_ACCEPT",
    "AUTH_REJECT",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_PLAN_NOT_DICT",
    "BLOCK_PLAN_WRONG_STATUS",
    "BLOCK_PLAN_FLAGS_FORBIDDEN",
    "BLOCK_MISSING_PLANNED_STEPS",
    "build_service_1_owner_authorization_dialogue_from_plan_packet_v1",
]
