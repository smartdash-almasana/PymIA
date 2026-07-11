"""
Service 1 Controlled Execution Candidate -> Owner Confirmation Loop V1

Fail-closed owner-confirmation loop for the Servicio 1 assisted flow.

Flow position:

    controlled execution gate output -> owner confirmation LOOP (this module)

The loop consumes the packet produced by
``build_service_1_controlled_execution_gate_from_semantic_bridge_v1`` and:

- if the gate already reported CONTROLLED_EXECUTION_CANDIDATE_READY, reports
  ALREADY_READY (nothing to ask),
- if the gate reported NEEDS_OWNER_CONFIRMATION and no answers were supplied,
  emits an owner confirmation question packet (OWNER_CONFIRMATION_REQUIRED),
- if valid, complete owner answers are supplied, reports
  OWNER_CONFIRMATION_RECHECK_READY (the caller may re-run the gate),
- otherwise BLOCKED.

The loop NEVER executes tools, NEVER creates delivery, NEVER authorizes
runtime/product/delivery/diagnosis.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_BLOCKED as GATE_STATUS_BLOCKED,
    STATUS_NEEDS_OWNER_CONFIRMATION as GATE_STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY as GATE_STATUS_READY,
)

SCHEMA_VERSION = "SERVICE_1_CONTROLLED_EXECUTION_CANDIDATE_TO_OWNER_CONFIRMATION_LOOP_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "CONTROLLED_EXECUTION_CANDIDATE_TO_OWNER_CONFIRMATION_LOOP"

STATUS_ALREADY_READY = "ALREADY_READY"
STATUS_OWNER_CONFIRMATION_REQUIRED = "OWNER_CONFIRMATION_REQUIRED"
STATUS_OWNER_CONFIRMATION_RECHECK_READY = "OWNER_CONFIRMATION_RECHECK_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_GATE_NOT_DICT = "GATE_PACKET_NOT_DICT"
BLOCK_GATE_FLAGS_FORBIDDEN = "GATE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_GATE_BLOCKED = "GATE_STATUS_BLOCKED"
BLOCK_GATE_UNKNOWN_STATUS = "GATE_UNKNOWN_STATUS"
BLOCK_ANSWERS_NOT_DICT = "OWNER_ANSWERS_NOT_DICT"
BLOCK_NO_QUESTIONS = "NO_OWNER_QUESTIONS"
BLOCK_MISSING_ANSWERS = "MISSING_ANSWERS"
BLOCK_UNKNOWN_ANSWERS = "UNKNOWN_ANSWERS"
BLOCK_EMPTY_ANSWERS = "EMPTY_ANSWERS"

_GATE_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1(
    *,
    gate_packet: Any,
    owner_answers: Any = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Run one owner-confirmation loop step over a controlled execution gate.

    Args:
        gate_packet: Output of the controlled execution gate.
        owner_answers: Optional mapping ``{column_name: answer_text}``. When
            omitted for a NEEDS_OWNER_CONFIRMATION gate, the loop emits the
            question packet. When supplied, all pending questions must be
            answered with non-empty text.
        runtime_authorized / ...: Must remain False; any True is blocking.

    Returns:
        A loop packet dict. Status is one of ALREADY_READY,
        OWNER_CONFIRMATION_REQUIRED, OWNER_CONFIRMATION_RECHECK_READY, or
        BLOCKED (with ``blocked_reason``).
    """
    if (
        runtime_authorized
        or tool_execution_authorized
        or product_ready
        or delivery_authorized
        or diagnosis_generated
    ):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(gate_packet, dict) or not gate_packet:
        return _blocked(BLOCK_GATE_NOT_DICT)

    if any(gate_packet.get(flag) for flag in _GATE_FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_GATE_FLAGS_FORBIDDEN,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    gate_status = gate_packet.get("status")
    case_id = gate_packet.get("case_id")
    source_kind = gate_packet.get("source_kind")
    filename = gate_packet.get("filename")

    if gate_status == GATE_STATUS_BLOCKED:
        return _blocked(
            BLOCK_GATE_BLOCKED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    if gate_status == GATE_STATUS_READY:
        return _packet(
            status=STATUS_ALREADY_READY,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            owner_questions=[],
            confirmed_answers={},
        )

    if gate_status != GATE_STATUS_NEEDS_OWNER_CONFIRMATION:
        return _blocked(
            BLOCK_GATE_UNKNOWN_STATUS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    # NEEDS_OWNER_CONFIRMATION path.
    questions = gate_packet.get("owner_questions") or []
    if not isinstance(questions, list) or not questions:
        return _blocked(
            BLOCK_NO_QUESTIONS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    pending_columns = [
        str(q.get("column_name")).strip()
        for q in questions
        if isinstance(q, dict) and str(q.get("column_name") or "").strip()
    ]

    # No answers yet -> emit the confirmation question packet.
    if owner_answers is None:
        return _packet(
            status=STATUS_OWNER_CONFIRMATION_REQUIRED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            owner_questions=list(questions),
            confirmed_answers={},
        )

    if not isinstance(owner_answers, dict):
        return _blocked(
            BLOCK_ANSWERS_NOT_DICT,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    answer_keys = [str(key).strip() for key in owner_answers.keys()]
    pending_set = set(pending_columns)

    # Unknown answers (for columns not pending) are blocking.
    unknown = [key for key in answer_keys if key not in pending_set]
    if unknown:
        return _blocked(
            BLOCK_UNKNOWN_ANSWERS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=sorted(set(unknown)),
        )

    confirmed: dict[str, str] = {}
    missing: list[str] = []
    empty: list[str] = []
    for column in pending_columns:
        raw = _answer_for(owner_answers, column)
        if raw is None:
            missing.append(column)
            continue
        if not raw.strip():
            empty.append(column)
            continue
        confirmed[column] = raw.strip()

    if empty:
        return _blocked(
            BLOCK_EMPTY_ANSWERS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=empty,
        )
    if missing:
        return _blocked(
            BLOCK_MISSING_ANSWERS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=missing,
        )

    return _packet(
        status=STATUS_OWNER_CONFIRMATION_RECHECK_READY,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
        owner_questions=[],
        confirmed_answers=confirmed,
    )


def _answer_for(owner_answers: dict[Any, Any], column: str) -> Optional[str]:
    for key, value in owner_answers.items():
        if str(key).strip() == column:
            return "" if value is None else str(value)
    return None


def _packet(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    owner_questions: list[Any],
    confirmed_answers: dict[str, str],
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
        "owner_questions": owner_questions,
        "owner_question_count": len(owner_questions),
        "confirmed_answers": confirmed_answers,
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
    detail: Optional[list[str]] = None,
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
        "owner_questions": [],
        "owner_question_count": 0,
        "confirmed_answers": {},
        "detail": list(detail or []),
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
    "STATUS_ALREADY_READY",
    "STATUS_OWNER_CONFIRMATION_REQUIRED",
    "STATUS_OWNER_CONFIRMATION_RECHECK_READY",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_GATE_NOT_DICT",
    "BLOCK_GATE_FLAGS_FORBIDDEN",
    "BLOCK_GATE_BLOCKED",
    "BLOCK_GATE_UNKNOWN_STATUS",
    "BLOCK_ANSWERS_NOT_DICT",
    "BLOCK_NO_QUESTIONS",
    "BLOCK_MISSING_ANSWERS",
    "BLOCK_UNKNOWN_ANSWERS",
    "BLOCK_EMPTY_ANSWERS",
    "build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1",
]
