from __future__ import annotations

import pytest

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle
from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


def test_build_owner_action_projection_pipeline_keep_as_declared_flow() -> None:
    from pymia.smartpyme.owner_action_pipeline import (
        OwnerActionPipelineResult,
        build_owner_action_projection_pipeline,
    )

    answers_bundle = OwnerAnswersBundle(
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
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-1",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Cuántos días tiene el período?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
            )
        ],
    )
    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_steps": [],
        "limit_warnings": [],
    }

    result = build_owner_action_projection_pipeline(
        owner_answers_bundle=answers_bundle,
        owner_questions_bundle=questions_bundle,
        render_contract=render_contract,
    )

    assert isinstance(result, OwnerActionPipelineResult)
    assert result.evaluation_bundle.evaluations[0].verdict == "accepted_as_declared"
    assert result.action_bundle.actions[0].action_type == "keep_as_declared"
    assert result.resolved_action_bundle.resolved_actions[0].resolved_questions == [
        "¿Cuántos días tiene el período?"
    ]
    assert any(
        "declaración del dueño" in step
        for step in result.projected_render_contract["next_steps"]
    )


def test_build_owner_action_projection_pipeline_ask_clarification_flow() -> None:
    from pymia.smartpyme.owner_action_pipeline import build_owner_action_projection_pipeline

    answer = OwnerAnswer.model_construct(
        answer_id="a-2",
        question_id="q-2",
        question_text="¿Qué significa esta columna?",
        answer_text=None,
        structured_answer={},
        answer_type="text",
        capture_status="provided",
        source_ref="owner_reply://2",
        metadata={},
    )
    answers_bundle = OwnerAnswersBundle.model_construct(
        bundle_id="answers-2",
        captured_at="2026-06-09T00:00:00+00:00",
        answers=[answer],
        metadata={},
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-2",
        questions=[
            OwnerQuestion(
                question_id="q-2",
                question_text="¿Qué significa esta columna?",
                reason="blocked_message",
                source_ref="render_contract://blocked_message",
            )
        ],
    )
    render_contract = {"tenant_id": "tenant-1", "references": ["ref-2"]}

    result = build_owner_action_projection_pipeline(
        owner_answers_bundle=answers_bundle,
        owner_questions_bundle=questions_bundle,
        render_contract=render_contract,
    )

    assert result.evaluation_bundle.evaluations[0].verdict == "needs_clarification"
    assert result.action_bundle.actions[0].action_type == "ask_clarification"
    assert result.projected_render_contract["next_questions"] == [
        "¿Qué significa esta columna?"
    ]
    assert result.projected_render_contract["blocked_message"] == "¿Qué significa esta columna?"


def test_build_owner_action_projection_pipeline_reject_answer_flow() -> None:
    from pymia.smartpyme.owner_action_pipeline import build_owner_action_projection_pipeline

    answers_bundle = OwnerAnswersBundle(
        bundle_id="answers-3",
        answers=[
            OwnerAnswer(
                answer_id="a-3",
                question_id="q-3",
                question_text="¿Cuál es el monto de impuestos?",
                answer_text="treinta",
                answer_type="number",
                source_ref="owner_reply://3",
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-3",
        questions=[
            OwnerQuestion(
                question_id="q-3",
                question_text="¿Cuál es el monto de impuestos?",
                reason="missing_evidence",
                source_ref="operational_audit_result://missing_evidence/0",
            )
        ],
    )
    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-3"],
        "forbidden_inferences": [],
    }

    result = build_owner_action_projection_pipeline(
        owner_answers_bundle=answers_bundle,
        owner_questions_bundle=questions_bundle,
        render_contract=render_contract,
    )

    assert result.evaluation_bundle.evaluations[0].verdict == "rejected"
    assert result.action_bundle.actions[0].action_type == "reject_answer"
    assert result.projected_render_contract["next_questions"] == [
        "¿Cuál es el monto de impuestos?"
    ]
    assert (
        result.projected_render_contract["blocked_message"]
        == "No puedo usar esa respuesta sin una aclaración o respaldo adicional."
    )


def test_build_owner_action_projection_pipeline_fails_closed_on_question_misalignment() -> None:
    from pymia.smartpyme.owner_action_pipeline import build_owner_action_projection_pipeline

    answers_bundle = OwnerAnswersBundle(
        bundle_id="answers-4",
        answers=[
            OwnerAnswer(
                answer_id="a-4",
                question_id="q-missing",
                question_text="¿Pregunta no alineada?",
                answer_text="10",
                answer_type="number",
                source_ref="owner_reply://4",
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(bundle_id="questions-4", questions=[])

    with pytest.raises(ValueError) as exc:
        build_owner_action_projection_pipeline(
            owner_answers_bundle=answers_bundle,
            owner_questions_bundle=questions_bundle,
            render_contract={"tenant_id": "tenant-1"},
        )

    assert "owner answers not aligned with questions bundle" in str(exc.value)
