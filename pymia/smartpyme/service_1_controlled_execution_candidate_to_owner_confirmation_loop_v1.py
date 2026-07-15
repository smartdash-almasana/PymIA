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
- if valid, complete option-ID answers are supplied, translates them through
  the gate's internal bindings and reports OWNER_CONFIRMATION_RECHECK_READY,
- if the owner chooses OTHER, captures optional free text and reports
  OWNER_FOLLOWUP_REQUIRED without creating semantic truth,
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
STATUS_OWNER_FOLLOWUP_REQUIRED = "OWNER_FOLLOWUP_REQUIRED"
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
BLOCK_OWNER_ANSWER_BINDINGS_INVALID = "OWNER_ANSWER_BINDINGS_INVALID"
BLOCK_INVALID_OPTION_ID = "INVALID_OWNER_OPTION_ID"
BLOCK_CONFLICTING_OWNER_ANSWER = "CONFLICTING_OWNER_ANSWER"

OWNER_OPTION_OTHER = "OTHER"

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
        owner_answers: Optional mapping ``{question_id: option_id}``. For
            historical single-sheet packets, ``question_id`` equals column_name. ``OTHER``
            may be submitted as ``{"option_id": "OTHER", "free_text": "..."}``.
            When omitted for a NEEDS_OWNER_CONFIRMATION gate, the loop emits
            the owner-safe question packet. Every pending column must be answered.
        runtime_authorized / ...: Must remain False; any True is blocking.

    Returns:
        A loop packet dict. Status is one of ALREADY_READY,
        OWNER_CONFIRMATION_REQUIRED, OWNER_CONFIRMATION_RECHECK_READY,
        OWNER_FOLLOWUP_REQUIRED, or BLOCKED (with ``blocked_reason``).
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

    pending_refs = [
        _question_ref_id(q)
        for q in questions
        if isinstance(q, dict) and _question_ref_id(q)
    ]
    if len(set(pending_refs)) != len(pending_refs):
        return _blocked(
            BLOCK_NO_QUESTIONS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

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
    pending_set = set(pending_refs)

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

    raw_bindings = gate_packet.get("owner_answer_bindings")
    if not isinstance(raw_bindings, dict):
        return _blocked(
            BLOCK_OWNER_ANSWER_BINDINGS_INVALID,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    confirmed: dict[str, str] = {}
    followup: list[dict[str, Any]] = []
    missing: list[str] = []
    empty: list[str] = []
    invalid_options: list[str] = []
    conflicting_answers: list[str] = []
    questions_by_ref = {
        _question_ref_id(question): question
        for question in questions
        if isinstance(question, dict) and _question_ref_id(question)
    }
    for ref_id in pending_refs:
        raw = _answer_for(owner_answers, ref_id)
        if raw is None:
            missing.append(ref_id)
            continue
        option_id, free_text = _parse_owner_answer(raw)
        if not option_id:
            empty.append(ref_id)
            continue

        question = questions_by_ref.get(ref_id, {})
        allowed_option_ids = {
            str(value).strip()
            for value in question.get("allowed_option_ids", [])
            if str(value).strip()
        }
        column_bindings = raw_bindings.get(ref_id)
        if not allowed_option_ids or not isinstance(column_bindings, dict):
            return _blocked(
                BLOCK_OWNER_ANSWER_BINDINGS_INVALID,
                case_id=case_id,
                source_kind=source_kind,
                filename=filename,
                detail=[ref_id],
            )
        if option_id not in allowed_option_ids:
            invalid_options.append(ref_id)
            continue
        if free_text and option_id != OWNER_OPTION_OTHER:
            conflicting_answers.append(ref_id)
            continue
        if option_id == OWNER_OPTION_OTHER:
            column = str(question.get("column_name") or "").strip()
            followup_item: dict[str, Any] = {
                "column_name": column,
                "option_id": OWNER_OPTION_OTHER,
                "owner_free_text": free_text,
                "normalization_required": True,
            }
            # Preserve the legacy single-sheet public shape. Multisheet or
            # synthetic refs need the stable ref identifiers to avoid merging
            # homonymous columns.
            if ref_id != column:
                followup_item.update(
                    {
                        "question_id": ref_id,
                        "field_id": ref_id,
                        "sheet_name": str(question.get("sheet_name") or "").strip(),
                    }
                )
            followup.append(followup_item)
            continue

        canonical_answer = str(column_bindings.get(option_id) or "").strip()
        if not canonical_answer:
            invalid_options.append(ref_id)
            continue
        confirmed[ref_id] = canonical_answer

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
    if conflicting_answers:
        return _blocked(
            BLOCK_CONFLICTING_OWNER_ANSWER,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=conflicting_answers,
        )
    if invalid_options:
        return _blocked(
            BLOCK_INVALID_OPTION_ID,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            detail=invalid_options,
        )
    if followup:
        return _packet(
            status=STATUS_OWNER_FOLLOWUP_REQUIRED,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            owner_questions=_followup_questions(followup),
            confirmed_answers={},
            owner_followup=followup,
        )

    return _packet(
        status=STATUS_OWNER_CONFIRMATION_RECHECK_READY,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
        owner_questions=[],
        confirmed_answers=confirmed,
    )


def _question_ref_id(question: dict[str, Any]) -> str:
    return str(
        question.get("question_id")
        or question.get("field_id")
        or question.get("column_name")
        or ""
    ).strip()


def _answer_for(owner_answers: dict[Any, Any], column: str) -> Any:
    for key, value in owner_answers.items():
        if str(key).strip() == column:
            return value
    return None


def _parse_owner_answer(value: Any) -> tuple[str, str | None]:
    if isinstance(value, str):
        return value.strip(), None
    if isinstance(value, dict):
        option_id = str(value.get("option_id") or "").strip()
        raw_free_text = value.get("free_text", value.get("owner_free_text"))
        free_text = None
        if raw_free_text is not None:
            free_text = str(raw_free_text).strip() or None
        return option_id, free_text
    return "", None


def _followup_questions(
    followup: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for item in followup:
        ref_id = str(item.get("question_id") or item.get("field_id") or "").strip()
        column = str(item.get("column_name") or "").strip()
        sheet = str(item.get("sheet_name") or "").strip()
        owner_free_text = item.get("owner_free_text")
        if owner_free_text:
            question = (
                "Tu descripción quedó registrada, pero PymIA todavía no puede "
                "convertirla en una opción gobernada ni usarla en cálculos."
            )
            answer_type = "semantic_normalization_required"
        else:
            question = (
                f"Contame brevemente qué representa la columna '{column}' "
                f"de la hoja '{sheet}' en tu negocio."
            )
            answer_type = "owner_free_text"
        questions.append(
            {
                "question_id": ref_id,
                "field_id": ref_id,
                "column_name": column,
                "sheet_name": sheet,
                "question": question,
                "answer_type": answer_type,
                "required": True,
                "runtime_authorized": False,
                "tool_execution_authorized": False,
            }
        )
    return questions


def _packet(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    owner_questions: list[Any],
    confirmed_answers: dict[str, str],
    owner_followup: list[dict[str, Any]] | None = None,
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
        "owner_followup": [dict(item) for item in (owner_followup or [])],
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
        "owner_followup": [],
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
    "STATUS_OWNER_FOLLOWUP_REQUIRED",
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
    "BLOCK_OWNER_ANSWER_BINDINGS_INVALID",
    "BLOCK_INVALID_OPTION_ID",
    "BLOCK_CONFLICTING_OWNER_ANSWER",
    "build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1",
]
