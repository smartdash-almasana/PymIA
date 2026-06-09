from __future__ import annotations

from pathlib import Path

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle
from pymia.contracts.owner_evaluation import OwnerAnswerEvaluationBundle


def test_evaluate_owner_answers_replay_bundle_certifies_minimal_flow() -> None:
    from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers

    empty_answer = OwnerAnswer.model_construct(
        answer_id="a-replay-3",
        question_id="q-replay-3",
        question_text="¿Qué significa esta columna?",
        answer_text=None,
        structured_answer={},
        answer_type="text",
        capture_status="provided",
        source_ref="owner_reply://replay/3",
        metadata={},
    )
    replay_bundle = OwnerAnswersBundle.model_construct(
        bundle_id="answers-replay",
        captured_at="2026-06-09T00:00:00+00:00",
        answers=[
            OwnerAnswer(
                answer_id="a-replay-1",
                question_id="q-replay-1",
                question_text="¿Cuánto pagaste de impuestos?",
                answer_text="1250",
                answer_type="number",
                source_ref="owner_reply://replay/1",
                metadata={"missing_key": "taxes"},
            ),
            OwnerAnswer(
                answer_id="a-replay-2",
                question_id="q-replay-2",
                question_text="¿Cuántos días tiene el período?",
                answer_text="30",
                answer_type="number",
                source_ref="owner_reply://replay/2",
                metadata={"missing_key": "dias_periodo"},
            ),
            empty_answer,
            OwnerAnswer(
                answer_id="a-replay-4",
                question_id="q-replay-4",
                question_text="¿Cuál es el monto declarado?",
                answer_text="treinta",
                answer_type="number",
                source_ref="owner_reply://replay/4",
            ),
            OwnerAnswer(
                answer_id="a-replay-5",
                question_id="q-replay-5",
                question_text="¿Podés confirmar este dato?",
                answer_text="Prefiero no responder.",
                answer_type="text",
                capture_status="declined",
                source_ref="owner_reply://replay/5",
            ),
        ],
        metadata={"scenario": "m54_replay"},
    )

    result = evaluate_owner_answers(replay_bundle)
    payload = result.model_dump(mode="json")

    assert isinstance(result, OwnerAnswerEvaluationBundle)
    assert [item.source_answer_id for item in result.evaluations] == [
        "a-replay-1",
        "a-replay-2",
        "a-replay-3",
        "a-replay-4",
        "a-replay-5",
    ]
    assert [item.linked_question_id for item in result.evaluations] == [
        "q-replay-1",
        "q-replay-2",
        "q-replay-3",
        "q-replay-4",
        "q-replay-5",
    ]
    assert [item.verdict for item in result.evaluations] == [
        "accepted_as_declared",
        "accepted_as_declared",
        "needs_clarification",
        "rejected",
        "rejected",
    ]
    assert result.evaluations[0].normalized_value == 1250
    assert result.evaluations[1].normalized_value == 30
    assert result.evaluations[0].mapped_key == "taxes"
    assert result.evaluations[1].mapped_key == "dias_periodo"
    assert "empty_answer" in result.evaluations[2].validation_errors
    assert "number_not_parseable" in result.evaluations[3].validation_errors
    assert "capture_status=declined" in result.evaluations[4].validation_errors
    assert all(item.verdict != "verified" for item in result.evaluations)
    assert "evidence_candidate" not in str(payload)
    assert result.metadata["evaluator"] == "minimal_owner_answer_flow_v1"


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
