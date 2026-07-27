from __future__ import annotations

from copy import deepcopy
from typing import Any, get_args

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle, OwnerAnswerType
from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


VALID_ANSWER_TYPES = set(get_args(OwnerAnswerType))


def capture_owner_answers_from_structured_payload(
    *,
    questions_bundle: OwnerQuestionsBundle,
    answers_payload: list[dict],
    source_ref: str,
    tenant_id: str | None = None,
) -> OwnerAnswersBundle:
    source_ref_text = str(source_ref or "").strip()
    if not source_ref_text:
        raise ValueError("source_ref must be non-empty")

    payloads = [deepcopy(dict(item)) for item in answers_payload]
    questions_by_id = {
        question.question_id: question
        for question in questions_bundle.questions
    }
    answers = [
        _capture_answer(
            payload=payload,
            question=_resolve_question(payload=payload, questions_by_id=questions_by_id),
            questions_bundle=questions_bundle,
            source_ref=source_ref_text,
            index=index,
        )
        for index, payload in enumerate(payloads)
    ]

    metadata: dict[str, Any] = {
        "source_questions_bundle_id": questions_bundle.bundle_id,
        "capture_mode": "structured_payload",
    }
    if tenant_id is not None:
        metadata["tenant_id"] = tenant_id

    return OwnerAnswersBundle(
        bundle_id=f"{questions_bundle.bundle_id}:answers",
        answers=answers,
        metadata=metadata,
    )


def _resolve_question(
    *,
    payload: dict,
    questions_by_id: dict[str, OwnerQuestion],
) -> OwnerQuestion:
    question_id = str(payload.get("question_id") or "").strip()
    if not question_id:
        raise ValueError("question_id is required")
    question = questions_by_id.get(question_id)
    if question is None:
        raise ValueError(f"unknown question_id: {question_id}")
    payload_question_text = payload.get("question_text")
    if payload_question_text is not None:
        text = str(payload_question_text).strip()
        if text and text != question.question_text:
            raise ValueError("payload question_text does not match contractual question_text")
    return question


def _capture_answer(
    *,
    payload: dict,
    question: OwnerQuestion,
    questions_bundle: OwnerQuestionsBundle,
    source_ref: str,
    index: int,
) -> OwnerAnswer:
    answer_text = _normalize_optional_text(payload.get("answer_text"))
    structured_answer = _normalize_structured_answer(payload.get("structured_answer"))
    if answer_text is None and not structured_answer:
        raise ValueError("answer_text or structured_answer is required")

    answer_type = _resolve_answer_type(payload=payload, question=question)
    question_id = question.question_id
    answer_metadata = dict(payload.get("metadata") or {})
    if question.missing_key:
        answer_metadata["missing_key"] = question.missing_key
    missing_input_type = question.metadata.get("missing_input_type")
    if missing_input_type:
        answer_metadata["missing_input_type"] = missing_input_type
    return OwnerAnswer(
        answer_id=f"{questions_bundle.bundle_id}:answer:{index}:{question_id}",
        question_id=question_id,
        question_text=question.question_text,
        answer_text=answer_text,
        structured_answer=structured_answer,
        answer_type=answer_type,
        source_ref=source_ref,
        metadata=answer_metadata,
    )


def _resolve_answer_type(*, payload: dict, question: OwnerQuestion) -> str:
    payload_answer_type = payload.get("answer_type")
    if payload_answer_type is not None:
        answer_type = str(payload_answer_type).strip()
        if answer_type not in VALID_ANSWER_TYPES:
            raise ValueError(f"invalid answer_type: {answer_type}")
        return answer_type

    expected_answer_type = str(question.expected_answer_type or "").strip()
    if expected_answer_type in VALID_ANSWER_TYPES:
        return expected_answer_type
    return "unknown"


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_structured_answer(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("structured_answer must be a dict when provided")
    return dict(value)
