from __future__ import annotations

from pathlib import Path

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle


def test_evaluate_owner_answers_accepts_valid_number() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-1",
        answers=[
            OwnerAnswer(
                answer_id="a-1",
                question_id="q-1",
                question_text="¿Cuántos días tiene el período?",
                answer_text="30",
                answer_type="number",
                source_ref="owner_reply://1",
                metadata={"missing_key": "dias_periodo"},
            )
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert result.bundle_id == "answers-1:evaluation"
    assert result.evaluations[0].verdict == "accepted_as_declared"
    assert result.evaluations[0].mapped_key == "dias_periodo"
    assert result.evaluations[0].normalized_value == 30


def test_evaluate_owner_answers_rejects_non_parseable_number() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-2",
        answers=[
            OwnerAnswer(
                answer_id="a-2",
                question_id="q-2",
                question_text="¿Cuál es el monto?",
                answer_text="treinta",
                answer_type="number",
                source_ref="owner_reply://2",
            )
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "rejected"
    assert "number_not_parseable" in result.evaluations[0].validation_errors


def test_evaluate_owner_answers_rejects_negative_number() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-3",
        answers=[
            OwnerAnswer(
                answer_id="a-3",
                question_id="q-3",
                question_text="¿Cuál es el saldo?",
                answer_text="-5",
                answer_type="number",
                source_ref="owner_reply://3",
            )
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "rejected"
    assert "number_negative" in result.evaluations[0].validation_errors


def test_evaluate_owner_answers_marks_empty_answer_as_needs_clarification() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    answer = OwnerAnswer.model_construct(
        answer_id="a-4",
        question_id="q-4",
        question_text="¿Qué significa esta columna?",
        answer_text=None,
        structured_answer={},
        answer_type="text",
        capture_status="provided",
        source_ref="owner_reply://4",
        metadata={},
    )
    bundle = OwnerAnswersBundle.model_construct(
        bundle_id="answers-4",
        captured_at="2026-06-09T00:00:00+00:00",
        answers=[answer],
        metadata={},
    )

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "needs_clarification"
    assert "empty_answer" in result.evaluations[0].validation_errors


def test_evaluate_owner_answers_rejects_declined_capture() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-5",
        answers=[
            OwnerAnswer(
                answer_id="a-5",
                question_id="q-5",
                question_text="¿Podés responder?",
                answer_text="No.",
                answer_type="text",
                capture_status="declined",
                source_ref="owner_reply://5",
            )
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "rejected"
    assert "capture_status=declined" in result.evaluations[0].validation_errors


def test_evaluate_owner_answers_rejects_unclear_capture() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-6",
        answers=[
            OwnerAnswer(
                answer_id="a-6",
                question_id="q-6",
                question_text="¿Qué período es?",
                answer_text="No entendí.",
                answer_type="text",
                capture_status="unclear",
                source_ref="owner_reply://6",
            )
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "rejected"
    assert "capture_status=unclear" in result.evaluations[0].validation_errors


def test_evaluate_owner_answers_accepts_operational_meaning_text() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    answer = OwnerAnswer.model_construct(
        answer_id="a-7",
        question_id="q-7",
        question_text="¿Qué significa la columna ajustes?",
        answer_text="Es un ajuste manual al cierre.",
        structured_answer={},
        answer_type="operational_meaning",
        capture_status="provided",
        source_ref="owner_reply://7",
        metadata={"mapped_key": "ajustes"},
    )
    bundle = OwnerAnswersBundle(bundle_id="answers-7", answers=[answer])

    result = evaluate_owner_answers(bundle)

    assert result.evaluations[0].verdict == "accepted_as_declared"
    assert result.evaluations[0].mapped_key == "ajustes"
    assert result.evaluations[0].normalized_value == "Es un ajuste manual al cierre."


def test_evaluate_owner_answers_preserves_order_and_never_uses_verified() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    answer_fact = OwnerAnswer.model_construct(
        answer_id="a-8",
        question_id="q-8",
        question_text="¿Qué representa este dato?",
        answer_text="Es una venta extraordinaria.",
        structured_answer={},
        answer_type="owner_declared_fact",
        capture_status="provided",
        source_ref="owner_reply://8",
        metadata={},
    )
    bundle = OwnerAnswersBundle(
        bundle_id="answers-8",
        answers=[
            OwnerAnswer(
                answer_id="a-9",
                question_id="q-9",
                question_text="¿Cuántos días tiene el período?",
                answer_text="15",
                answer_type="number",
                source_ref="owner_reply://9",
            ),
            answer_fact,
        ],
    )

    result = evaluate_owner_answers(bundle)

    assert [item.source_answer_id for item in result.evaluations] == ["a-9", "a-8"]
    assert [item.linked_question_id for item in result.evaluations] == ["q-9", "q-8"]
    assert all(item.verdict != "verified" for item in result.evaluations)


def test_evaluate_owner_answers_output_has_no_evidence_candidate() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    bundle = OwnerAnswersBundle(
        bundle_id="answers-9",
        answers=[
            OwnerAnswer(
                answer_id="a-10",
                question_id="q-10",
                question_text="¿Cuántos días tiene el período?",
                answer_text="10",
                answer_type="number",
                source_ref="owner_reply://10",
            )
        ],
    )

    payload = evaluate_owner_answers(bundle).model_dump(mode="json")

    assert "evidence_candidate" not in str(payload)


def test_owner_answers_evaluator_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_answers_evaluator.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "graph",
        "pymiastate",
        "diagnosticcore",
        "diagnostic_core",
        "telegram",
        "hermes",
        "fastapi",
        "runtime",
        "llm",
        "learningmemory",
    ]

    for token in forbidden_tokens:
        assert f"import {token}" not in lowered
        assert f"from {token} import" not in lowered
