"""
Service 1 Dry Run Candidate -> Owner Validation Dialogue V1

Fail-closed owner-validation dialogue for the Servicio 1 assisted flow.

Flow position:

    dry_run_candidate (READY) -> owner VALIDATION dialogue (this module)

The module takes a READY dry-run candidate (the analysis produced after an
ACCEPTED authorization) and emits the owner validation dialogue:

- without an ``owner_validation`` answer -> OWNER_VALIDATION_REQUIRED,
- ``owner_validation == "accept"`` -> OWNER_VALIDATION_ACCEPTED,
- ``owner_validation == "reject"`` -> OWNER_VALIDATION_REJECTED,
- ``owner_validation == "request_changes"`` -> OWNER_VALIDATION_REQUEST_CHANGES.

The module NEVER executes tools, NEVER creates delivery, and NEVER authorizes
runtime/product/delivery/diagnosis. ``dry_run_evaluated`` is True (the analysis
is already present), while ``execution_executed`` and ``delivery_created`` stay
False; all safety flags stay False.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 import (
    STATUS_READY as CANDIDATE_STATUS_READY,
)

SCHEMA_VERSION = "SERVICE_1_DRY_RUN_CANDIDATE_TO_OWNER_VALIDATION_DIALOGUE_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "DRY_RUN_CANDIDATE_TO_OWNER_VALIDATION_DIALOGUE"

STATUS_REQUIRED = "OWNER_VALIDATION_REQUIRED"
STATUS_ACCEPTED = "OWNER_VALIDATION_ACCEPTED"
STATUS_REJECTED = "OWNER_VALIDATION_REJECTED"
STATUS_REQUEST_CHANGES = "OWNER_VALIDATION_REQUEST_CHANGES"
STATUS_BLOCKED = "BLOCKED"

VALIDATION_ACCEPT = "accept"
VALIDATION_REJECT = "reject"
VALIDATION_REQUEST_CHANGES = "request_changes"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_INPUT_NOT_DICT = "DRY_RUN_CANDIDATE_NOT_DICT"
BLOCK_INPUT_FLAGS_FORBIDDEN = "DRY_RUN_CANDIDATE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_WRONG_STATUS = "DRY_RUN_CANDIDATE_WRONG_STATUS"
BLOCK_MISSING_ANALYSIS = "MISSING_DRY_RUN_ANALYSIS"

_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1(
    *,
    dry_run_candidate_packet: Any,
    owner_validation: Any = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Emit the owner validation dialogue for a READY dry-run candidate.

    Args:
        dry_run_candidate_packet: Output of the dry-run candidate builder
            (status CONTROLLED_DRY_RUN_CANDIDATE_READY).
        owner_validation: Optional "accept" / "reject" / "request_changes".
            When omitted -> REQUIRED.

    Returns:
        A validation dialogue packet dict with status one of REQUIRED, ACCEPTED,
        REJECTED, REQUEST_CHANGES, or BLOCKED (with ``blocked_reason``).
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(dry_run_candidate_packet, dict) or not dry_run_candidate_packet:
        return _blocked(BLOCK_INPUT_NOT_DICT)

    if any(dry_run_candidate_packet.get(flag) for flag in _FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_INPUT_FLAGS_FORBIDDEN,
            case_id=dry_run_candidate_packet.get("case_id"),
            source_kind=dry_run_candidate_packet.get("source_kind"),
            filename=dry_run_candidate_packet.get("filename"),
        )

    if dry_run_candidate_packet.get("status") != CANDIDATE_STATUS_READY:
        return _blocked(
            BLOCK_WRONG_STATUS,
            case_id=dry_run_candidate_packet.get("case_id"),
            source_kind=dry_run_candidate_packet.get("source_kind"),
            filename=dry_run_candidate_packet.get("filename"),
        )

    analysis = dry_run_candidate_packet.get("analysis")
    if not isinstance(analysis, (list, tuple)) or not analysis:
        return _blocked(
            BLOCK_MISSING_ANALYSIS,
            case_id=dry_run_candidate_packet.get("case_id"),
            source_kind=dry_run_candidate_packet.get("source_kind"),
            filename=dry_run_candidate_packet.get("filename"),
        )

    case_id = dry_run_candidate_packet.get("case_id")
    source_kind = dry_run_candidate_packet.get("source_kind")
    filename = dry_run_candidate_packet.get("filename")

    if owner_validation is None:
        return _dialogue(
            status=STATUS_REQUIRED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            dry_run_candidate_packet=dry_run_candidate_packet,
        )

    decision = str(owner_validation).strip().lower()
    if decision == VALIDATION_ACCEPT:
        status = STATUS_ACCEPTED
    elif decision == VALIDATION_REJECT:
        status = STATUS_REJECTED
    elif decision == VALIDATION_REQUEST_CHANGES:
        status = STATUS_REQUEST_CHANGES
    else:
        # Any other answer is an invalid validation decision -> BLOCKED.
        return _blocked(
            BLOCK_WRONG_STATUS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    return _dialogue(
        status=status,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
        dry_run_candidate_packet=dry_run_candidate_packet,
    )


def _dialogue(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    dry_run_candidate_packet: dict[str, Any],
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
        "candidate_count": dry_run_candidate_packet.get("step_count"),
        "roles": list(dry_run_candidate_packet.get("roles") or []),
        "analysis": list(dry_run_candidate_packet.get("analysis") or []),
        "validation_decision": status,
        "dry_run_evaluated": True,
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
        "analysis": [],
        "validation_decision": None,
        "dry_run_evaluated": True,
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
    "STATUS_REQUEST_CHANGES",
    "STATUS_BLOCKED",
    "VALIDATION_ACCEPT",
    "VALIDATION_REJECT",
    "VALIDATION_REQUEST_CHANGES",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_INPUT_NOT_DICT",
    "BLOCK_INPUT_FLAGS_FORBIDDEN",
    "BLOCK_WRONG_STATUS",
    "BLOCK_MISSING_ANALYSIS",
    "build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1",
]
