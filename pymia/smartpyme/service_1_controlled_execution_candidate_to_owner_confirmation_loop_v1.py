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

from pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1 import (
    Service1ColumnOwnerQuestionViewV1,
)
from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
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
BLOCK_OWNER_QUESTION_VIEW_MISSING = "OWNER_QUESTION_VIEW_MISSING"
BLOCK_OWNER_QUESTION_VIEW_INVALID = "OWNER_QUESTION_VIEW_INVALID"
BLOCK_OWNER_QUESTION_SURFACE_UNSAFE = "OWNER_QUESTION_SURFACE_UNSAFE"

OWNER_OPTION_OTHER = "OTHER"
OWNER_OPTION_IGNORE = "IGNORE"

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

    # NEEDS_OWNER_CONFIRMATION path. The gate exposes only canonical P6/context;
    # this dialogue layer owns owner-safe question composition and answer bindings.
    questions, raw_bindings, question_error = _owner_questions_from_gate_context(gate_packet)
    if question_error is not None:
        return _blocked(
            question_error,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )
    if not questions:
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
            owner_answer_bindings=raw_bindings,
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

    confirmed: dict[str, str] = {}
    followup: list[dict[str, Any]] = []
    system_scope_exclusions: set[str] = set()
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
        system_scope_exclusion = _is_system_scope_exclusion(raw)
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
        if system_scope_exclusion:
            if option_id != OWNER_OPTION_IGNORE or canonical_answer != "IGNORED_NOT_RELEVANT":
                conflicting_answers.append(ref_id)
                continue
            system_scope_exclusions.add(ref_id)
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
    events = _owner_confirmation_events(
        case_id=case_id,
        filename=filename,
        questions_by_ref=questions_by_ref,
        owner_answers=owner_answers,
        confirmed=confirmed,
        followup=followup,
        system_scope_exclusions=system_scope_exclusions,
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
            owner_confirmation_events=events,
            system_scope_exclusions=system_scope_exclusions,
        )

    return _packet(
        status=STATUS_OWNER_CONFIRMATION_RECHECK_READY,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
        owner_questions=[],
        confirmed_answers=confirmed,
        owner_confirmation_events=events,
        system_scope_exclusions=system_scope_exclusions,
    )


def _owner_questions_from_gate_context(
    gate_packet: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]], str | None]:
    raw_candidates = gate_packet.get("owner_confirmation_candidates")
    raw_views = gate_packet.get("owner_question_views")
    if not isinstance(raw_candidates, (list, tuple)) or not raw_candidates:
        return [], {}, BLOCK_NO_QUESTIONS
    if not isinstance(raw_views, (list, tuple)):
        return [], {}, BLOCK_OWNER_QUESTION_VIEW_MISSING

    views_by_identity: dict[tuple[str, str], Service1ColumnOwnerQuestionViewV1] = {}
    for view in raw_views:
        if not isinstance(view, Service1ColumnOwnerQuestionViewV1):
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        if view.question_required:
            identity = (str(view.sheet_name).strip(), str(view.column_name).strip())
            if identity in views_by_identity:
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            views_by_identity[identity] = view

    questions: list[dict[str, Any]] = []
    bindings_by_ref: dict[str, dict[str, str]] = {}
    for candidate in raw_candidates:
        column = str(getattr(candidate, "source_column_name", "") or "").strip()
        sheet = str(getattr(candidate, "sheet_name", "") or "").strip()
        ref_id = _candidate_ref_id(candidate)
        if not ref_id:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        view = views_by_identity.get((sheet, column))
        if view is None or not view.question or not view.options:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_MISSING

        metadata = dict(getattr(candidate, "metadata", {}) or {})
        raw_options = metadata.get("allowed_owner_answers")
        if not isinstance(raw_options, list):
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID

        internal_bindings: dict[str, str] = {}
        for option in raw_options:
            if not isinstance(option, dict):
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            option_id = str(option.get("option_id") or "").strip()
            linked = option.get("linked_hypothesis")
            if option_id == OWNER_OPTION_OTHER:
                continue
            if not option_id or not isinstance(linked, dict):
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            semantic_role = str(linked.get("semantic_role") or "").strip()
            if not semantic_role:
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            if semantic_role == "unknown":
                continue
            internal_bindings[option_id] = semantic_role

        safe_options = [
            option.to_dict()
            for option in view.options
            if option.option_id in internal_bindings
            or option.option_id == OWNER_OPTION_OTHER
        ]
        safe_options.append(
            {
                "option_id": OWNER_OPTION_IGNORE,
                "label": "No usar esta columna",
                "description": (
                    "La columna no es necesaria para este análisis y queda fuera "
                    "sin modificar el archivo original."
                ),
            }
        )
        question = {
            "question_id": ref_id,
            "field_id": ref_id,
            "column_name": column,
            "sheet_name": view.sheet_name,
            "title": view.title,
            "context": view.context,
            "question": view.question,
            "options": safe_options,
            "allowed_option_ids": [item["option_id"] for item in safe_options],
            "free_text_option_id": OWNER_OPTION_OTHER,
            "risk_note": view.risk_note,
            "confidence_note": view.confidence_note,
            "answer_type": "select_owner_option_id",
            "required": True,
        }
        if not _owner_question_surface_is_safe(question, candidate):
            return [], {}, BLOCK_OWNER_QUESTION_SURFACE_UNSAFE

        internal_bindings[OWNER_OPTION_IGNORE] = "IGNORED_NOT_RELEVANT"
        questions.append(question)
        if ref_id in bindings_by_ref:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        bindings_by_ref[ref_id] = internal_bindings

    return questions, bindings_by_ref, None


def _candidate_ref_id(candidate: Any) -> str:
    metadata = dict(getattr(candidate, "metadata", {}) or {})
    return str(
        metadata.get("column_ref_id")
        or metadata.get("question_id")
        or getattr(candidate, "source_column_name", "")
        or ""
    ).strip()


def _owner_question_surface_is_safe(
    question: dict[str, Any], candidate: Any
) -> bool:
    generated_surface = {
        "options": question.get("options", []),
        "answer_type": question.get("answer_type"),
        "free_text_option_id": question.get("free_text_option_id"),
    }
    rendered = str(generated_surface).lower()
    internal_tokens = {
        str(role).strip().lower()
        for role in (getattr(candidate, "candidate_semantic_roles", ()) or ())
        if str(role).strip()
    }
    internal_tokens.update(
        {
            "ignored_not_relevant",
            "owner_rectified_function",
            "computed_variables",
        }
    )
    return not any(token in rendered for token in internal_tokens)


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


def _is_system_scope_exclusion(value: Any) -> bool:
    return isinstance(value, dict) and value.get("scope_excluded") is True


def _owner_confirmation_events(
    *,
    case_id: Any,
    filename: Any,
    questions_by_ref: dict[str, dict[str, Any]],
    owner_answers: dict[Any, Any],
    confirmed: dict[str, str],
    followup: list[dict[str, Any]],
    system_scope_exclusions=None,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    followup_by_ref = {
        str(item.get("question_id") or item.get("field_id") or item.get("column_name") or "").strip(): item
        for item in followup
    }
    for ref_id, question in questions_by_ref.items():
        if ref_id in set(system_scope_exclusions or ()):
            continue
        raw = _answer_for(owner_answers, ref_id)
        option_id, free_text = _parse_owner_answer(raw)
        column = str(question.get("column_name") or ref_id).strip()
        sheet = str(question.get("sheet_name") or "").strip()
        if not sheet:
            # A physical sheet is part of the owner-evidence identity.  Do
            # not fabricate one when a legacy question is incomplete.
            continue
        if ref_id in confirmed:
            canonical_answer = confirmed[ref_id]
            scope = "COLUMN_EXCLUSION" if canonical_answer == "IGNORED_NOT_RELEVANT" else "SEMANTIC_ROLE"
            event = build_service_1_owner_confirmation_event_v1(
                case_id=str(case_id or "").strip(),
                file_ref=str(filename).strip() if filename else None,
                region_ref=None,
                sheet_ref=sheet,
                column_ref=column,
                question_ref=ref_id,
                owner_answer=option_id,
                confirmation_scope=scope,
                proposed_role=canonical_answer if scope == "SEMANTIC_ROLE" else None,
                confirmed_role=canonical_answer if scope == "SEMANTIC_ROLE" else None,
                provenance={"producer": SCHEMA_VERSION, "source": "owner_confirmation_loop"},
            )
            events.append(event.to_dict())
            continue
        followup_item = followup_by_ref.get(ref_id)
        if followup_item is not None and free_text:
            event = build_service_1_owner_confirmation_event_v1(
                case_id=str(case_id or "").strip(),
                file_ref=str(filename).strip() if filename else None,
                region_ref=None,
                sheet_ref=sheet,
                column_ref=column,
                question_ref=ref_id,
                owner_answer=option_id,
                confirmation_scope="FREE_TEXT_MEANING",
                corrected_meaning=free_text,
                provenance={"producer": SCHEMA_VERSION, "source": "owner_confirmation_loop", "normalization_required": True},
            )
            events.append(event.to_dict())
    return events


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
    owner_confirmation_events: list[dict[str, Any]] | None = None,
    owner_answer_bindings: dict[str, dict[str, str]] | None = None,
    system_scope_exclusions: set[str] | None = None,
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
        "system_scope_exclusions": sorted(system_scope_exclusions or ()),
        "owner_answer_bindings": {
            ref_id: dict(bindings)
            for ref_id, bindings in (owner_answer_bindings or {}).items()
        },
        "owner_confirmation_events": [dict(item) for item in (owner_confirmation_events or [])],
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
        "owner_confirmation_events": [],
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
