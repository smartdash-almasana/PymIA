from __future__ import annotations

import hashlib
import json
from typing import Any

from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


_KNOWN_MISSING_EVIDENCE_QUESTIONS: dict[str, tuple[str, str]] = {
    "dias_periodo": (
        "¿Cuál es la cantidad de días del período analizado?",
        "number",
    ),
    "taxes": (
        "¿Podés informar los impuestos del período analizado?",
        "number",
    ),
    "periodo": (
        "¿Qué período cubre esta información?",
        "period",
    ),
    "extracto_bancario": (
        "¿Podés subir el extracto bancario faltante?",
        "document",
    ),
}

_GENERIC_MISSING_EVIDENCE_QUESTION = (
    "¿Podés aportar el dato, archivo o aclaración que falta para poder avanzar con el análisis?"
)
MISSING_INPUT_TYPE_STRUCTURAL = "STRUCTURAL_INPUT"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_list(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [_normalize_text(value) for value in values if _normalize_text(value)]


def _looks_like_technical_key(value: str) -> bool:
    if "_" in value:
        return True
    if value.isascii() and value.replace("-", "_").isidentifier() and value.lower() == value:
        return True
    return value in _KNOWN_MISSING_EVIDENCE_QUESTIONS


def _owner_visible_next_question(question_text: str) -> tuple[str, str]:
    known = _KNOWN_MISSING_EVIDENCE_QUESTIONS.get(question_text)
    if known is not None:
        return known
    if _looks_like_technical_key(question_text):
        return _GENERIC_MISSING_EVIDENCE_QUESTION, "unknown"
    return question_text, "unknown"


def _build_question_id(
    *,
    reason: str,
    question_text: str,
    missing_key: str | None,
    source_ref: str,
) -> str:
    payload = {
        "reason": reason,
        "question_text": question_text,
        "missing_key": missing_key,
        "source_ref": source_ref,
    }
    digest = hashlib.sha1(
        json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"owner_question_{digest[:12]}"


def _build_missing_evidence_question(
    *,
    missing_key: str,
    source_ref: str,
    metadata: dict[str, Any],
) -> OwnerQuestion:
    known = _KNOWN_MISSING_EVIDENCE_QUESTIONS.get(missing_key)
    if known is not None:
        question_text, expected_answer_type = known
    else:
        question_text = _GENERIC_MISSING_EVIDENCE_QUESTION
        expected_answer_type = "unknown"

    question_metadata = dict(metadata)
    question_metadata["missing_input_type"] = MISSING_INPUT_TYPE_STRUCTURAL

    return OwnerQuestion(
        question_id=_build_question_id(
            reason="missing_evidence",
            question_text=question_text,
            missing_key=missing_key,
            source_ref=source_ref,
        ),
        question_text=question_text,
        reason="missing_evidence",
        missing_key=missing_key,
        missing_input_type=MISSING_INPUT_TYPE_STRUCTURAL,
        source_ref=source_ref,
        expected_answer_type=expected_answer_type,
        required=True,
        metadata=question_metadata,
    )


def _build_next_question(
    *,
    question_text: str,
    source_ref: str,
    metadata: dict[str, Any],
) -> OwnerQuestion:
    owner_visible_question, expected_answer_type = _owner_visible_next_question(question_text)
    question_metadata = dict(metadata)
    if owner_visible_question != question_text:
        question_metadata["source_next_question"] = question_text
    return OwnerQuestion(
        question_id=_build_question_id(
            reason="next_question",
            question_text=owner_visible_question,
            missing_key=None,
            source_ref=source_ref,
        ),
        question_text=owner_visible_question,
        reason="next_question",
        missing_key=None,
        source_ref=source_ref,
        expected_answer_type=expected_answer_type,
        required=True,
        metadata=question_metadata,
    )


def _build_blocked_message_question(
    *,
    blocked_message: str,
    source_ref: str,
    metadata: dict[str, Any],
) -> OwnerQuestion:
    question_text = "El caso está bloqueado. ¿Podés aportar la evidencia o aclaración necesaria para destrabarlo?"
    question_metadata = dict(metadata)
    question_metadata["blocked_message"] = blocked_message
    return OwnerQuestion(
        question_id=_build_question_id(
            reason="blocked_message",
            question_text=question_text,
            missing_key=None,
            source_ref=source_ref,
        ),
        question_text=question_text,
        reason="blocked_message",
        missing_key=None,
        source_ref=source_ref,
        expected_answer_type="unknown",
        required=True,
        metadata=question_metadata,
    )


def _dedupe_preserve_order(questions: list[OwnerQuestion]) -> list[OwnerQuestion]:
    seen: set[tuple[str, str, str | None, str]] = set()
    deduped: list[OwnerQuestion] = []
    for question in questions:
        key = (
            question.reason,
            question.question_text,
            question.missing_key,
            question.source_ref,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(question)
    return deduped


def build_owner_questions_bundle(
    *,
    source_ref: str,
    missing_evidence: list[str] | None = None,
    next_questions: list[str] | None = None,
    blocked_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> OwnerQuestionsBundle:
    source_ref_text = _normalize_text(source_ref)
    if not source_ref_text:
        raise ValueError("source_ref must be non-empty")

    base_metadata = dict(metadata or {})
    questions: list[OwnerQuestion] = []

    for missing_key in _normalize_list(missing_evidence):
        questions.append(
            _build_missing_evidence_question(
                missing_key=missing_key,
                source_ref=source_ref_text,
                metadata=base_metadata,
            )
        )

    for question_text in _normalize_list(next_questions):
        questions.append(
            _build_next_question(
                question_text=question_text,
                source_ref=source_ref_text,
                metadata=base_metadata,
            )
        )

    blocked_message_text = _normalize_text(blocked_message)
    if blocked_message_text:
        questions.append(
            _build_blocked_message_question(
                blocked_message=blocked_message_text,
                source_ref=source_ref_text,
                metadata=base_metadata,
            )
        )

    deduped_questions = _dedupe_preserve_order(questions)
    bundle_id = _build_question_id(
        reason="bundle",
        question_text=json.dumps(
            [question.question_id for question in deduped_questions],
            ensure_ascii=True,
        ),
        missing_key=None,
        source_ref=source_ref_text,
    ).replace("owner_question_", "owner_questions_bundle_")

    return OwnerQuestionsBundle(
        bundle_id=bundle_id,
        questions=deduped_questions,
        metadata=dict(base_metadata),
    )
