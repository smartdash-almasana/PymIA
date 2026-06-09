from __future__ import annotations

from decimal import Decimal, InvalidOperation

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle
from pymia.contracts.owner_evaluation import (
    OwnerAnswerEvaluation,
    OwnerAnswerEvaluationBundle,
)


def evaluate_owner_answers(bundle: OwnerAnswersBundle) -> OwnerAnswerEvaluationBundle:
    evaluations = [
        _evaluate_answer(answer, index)
        for index, answer in enumerate(bundle.answers)
    ]
    return OwnerAnswerEvaluationBundle(
        bundle_id=f"{bundle.bundle_id}:evaluation",
        source_answers_bundle_id=bundle.bundle_id,
        evaluations=evaluations,
        metadata={"evaluator": "minimal_owner_answer_flow_v1"},
    )


def _evaluate_answer(answer: OwnerAnswer, index: int) -> OwnerAnswerEvaluation:
    evaluation_id = f"{answer.answer_id}:evaluation:{index}"
    answer_type = str(answer.answer_type)
    capture_status = str(answer.capture_status)
    answer_text = str(answer.answer_text or "").strip()
    structured_answer = dict(answer.structured_answer or {})
    mapped_key = _derive_mapped_key(answer)

    if capture_status in {"declined", "unclear"}:
        return OwnerAnswerEvaluation(
            evaluation_id=evaluation_id,
            source_answer_id=answer.answer_id,
            linked_question_id=answer.question_id,
            verdict="rejected",
            mapped_key=mapped_key,
            validation_errors=[f"capture_status={capture_status}"],
            notes=["Answer capture status is not actionable."],
        )

    if not answer_text and not structured_answer:
        return OwnerAnswerEvaluation(
            evaluation_id=evaluation_id,
            source_answer_id=answer.answer_id,
            linked_question_id=answer.question_id,
            verdict="needs_clarification",
            mapped_key=mapped_key,
            validation_errors=["empty_answer"],
            notes=["Answer did not provide text or structured content."],
        )

    if answer_type == "number":
        parsed = _parse_number(answer_text)
        if parsed is None:
            return OwnerAnswerEvaluation(
                evaluation_id=evaluation_id,
                source_answer_id=answer.answer_id,
                linked_question_id=answer.question_id,
                verdict="rejected",
                mapped_key=mapped_key,
                validation_errors=["number_not_parseable"],
                notes=["Number answer could not be parsed."],
            )
        if parsed < 0:
            return OwnerAnswerEvaluation(
                evaluation_id=evaluation_id,
                source_answer_id=answer.answer_id,
                linked_question_id=answer.question_id,
                verdict="rejected",
                mapped_key=mapped_key,
                normalized_value=_normalize_decimal(parsed),
                validation_errors=["number_negative"],
                notes=["Negative numeric answers are rejected in this minimal flow."],
            )
        return OwnerAnswerEvaluation(
            evaluation_id=evaluation_id,
            source_answer_id=answer.answer_id,
            linked_question_id=answer.question_id,
            verdict="accepted_as_declared",
            mapped_key=mapped_key,
            normalized_value=_normalize_decimal(parsed),
            notes=["Numeric answer accepted as declared."],
        )

    if answer_type in {"owner_declared_fact", "operational_meaning"} and answer_text:
        return OwnerAnswerEvaluation(
            evaluation_id=evaluation_id,
            source_answer_id=answer.answer_id,
            linked_question_id=answer.question_id,
            verdict="accepted_as_declared",
            mapped_key=mapped_key,
            normalized_value=answer_text,
            notes=["Owner-declared text accepted as declared."],
        )

    return OwnerAnswerEvaluation(
        evaluation_id=evaluation_id,
        source_answer_id=answer.answer_id,
        linked_question_id=answer.question_id,
        verdict="needs_clarification",
        mapped_key=mapped_key,
        notes=["Minimal flow could not classify the answer more strongly."],
    )


def _derive_mapped_key(answer: OwnerAnswer) -> str | None:
    for candidate in (
        answer.metadata.get("missing_key"),
        answer.metadata.get("mapped_key"),
        answer.structured_answer.get("mapped_key"),
    ):
        text = str(candidate or "").strip()
        if text:
            return text
    return None


def _parse_number(raw_value: str) -> Decimal | None:
    if not raw_value:
        return None
    normalized = raw_value.replace(",", ".").strip()
    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def _normalize_decimal(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)
