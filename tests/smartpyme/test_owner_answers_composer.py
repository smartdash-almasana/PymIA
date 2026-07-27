from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle
from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


def _questions_bundle() -> OwnerQuestionsBundle:
    return OwnerQuestionsBundle(
        bundle_id="questions-composer",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Cuántos días tiene el período?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
                expected_answer_type="number",
            ),
            OwnerQuestion(
                question_id="q-2",
                question_text="¿Qué significa esta columna?",
                reason="blocked_message",
                source_ref="render_contract://blocked_message",
                expected_answer_type="text",
            ),
        ],
    )


def test_compose_owner_answers_to_actions_happy_path_returns_all_artifacts() -> None:
    from pymia.smartpyme.owner_answers_composer import (
        OwnerAnswerToActionCompositionResult,
        compose_owner_answers_to_actions,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_steps": [],
        "limit_warnings": [],
    }
    result = compose_owner_answers_to_actions(
        questions_bundle=_questions_bundle(),
        answers_payload=[{"question_id": "q-1", "answer_text": "30"}],
        source_ref="operator_assisted_capture",
        render_contract=render_contract,
        tenant_id="tenant-1",
    )

    assert isinstance(result, OwnerAnswerToActionCompositionResult)
    assert result.owner_answers_bundle.bundle_id == "questions-composer:answers"
    assert result.evaluation_bundle.evaluations[0].verdict == "accepted_as_declared"
    assert result.action_bundle.actions[0].action_type == "keep_as_declared"
    assert result.resolved_action_bundle.resolved_actions[0].resolved_questions == [
        "¿Cuántos días tiene el período?"
    ]
    assert isinstance(result.projected_render_contract, dict)
    assert any(
        "declaración del dueño" in step
        for step in result.projected_render_contract["next_steps"]
    )


def test_compose_owner_answers_to_actions_does_not_mutate_answers_payload_or_render_contract() -> None:
    from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions

    answers_payload = [{"question_id": "q-1", "answer_text": "30"}]
    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_steps": [],
        "limit_warnings": [],
    }
    payload_before = deepcopy(answers_payload)
    render_before = deepcopy(render_contract)

    result = compose_owner_answers_to_actions(
        questions_bundle=_questions_bundle(),
        answers_payload=answers_payload,
        source_ref="operator_assisted_capture",
        render_contract=render_contract,
    )

    assert answers_payload == payload_before
    assert render_contract == render_before
    assert result.projected_render_contract is not render_contract


def test_compose_owner_answers_to_actions_fails_when_m61_rejects_unknown_question_id() -> None:
    from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions

    with pytest.raises(ValueError) as exc:
        compose_owner_answers_to_actions(
            questions_bundle=_questions_bundle(),
            answers_payload=[{"question_id": "q-missing", "answer_text": "30"}],
            source_ref="operator_assisted_capture",
            render_contract={"tenant_id": "tenant-1"},
        )

    assert "unknown question_id" in str(exc.value)


def test_compose_owner_answers_to_actions_fails_when_m61_rejects_empty_answer() -> None:
    from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions

    with pytest.raises(ValueError) as exc:
        compose_owner_answers_to_actions(
            questions_bundle=_questions_bundle(),
            answers_payload=[{"question_id": "q-1"}],
            source_ref="operator_assisted_capture",
            render_contract={"tenant_id": "tenant-1"},
        )

    assert "answer_text or structured_answer is required" in str(exc.value)


def test_compose_owner_answers_to_actions_propagates_m59_alignment_error() -> None:
    from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions

    questions_bundle = _questions_bundle()
    answers_bundle = OwnerAnswersBundle(
        bundle_id="questions-composer:answers",
        answers=[
            OwnerAnswer(
                answer_id="questions-composer:answer:0:q-missing",
                question_id="q-missing",
                question_text="Pregunta no alineada",
                answer_text="30",
                answer_type="number",
                source_ref="operator_assisted_capture",
            )
        ],
    )

    import pymia.smartpyme.owner_answers_composer as composer_module

    original_capture = composer_module.capture_owner_answers_from_structured_payload

    def _fake_capture(**kwargs):
        return answers_bundle

    composer_module.capture_owner_answers_from_structured_payload = _fake_capture
    try:
        with pytest.raises(ValueError) as exc:
            compose_owner_answers_to_actions(
                questions_bundle=questions_bundle,
                answers_payload=[{"question_id": "q-1", "answer_text": "30"}],
                source_ref="operator_assisted_capture",
                render_contract={"tenant_id": "tenant-1"},
            )
    finally:
        composer_module.capture_owner_answers_from_structured_payload = original_capture

    assert "owner answers not aligned with questions bundle" in str(exc.value)


def test_owner_answers_composer_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_answers_composer.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "graph",
        "state",
        "conversation_adapter",
        "core_delivery_bridge",
        "telegram_bot_runtime",
        "diagnosticcore",
        "diagnostic_core",
        "telegram",
        "hermes",
        "fastapi",
        "runtime",
        "parser",
        "llm",
        "learningmemory",
    ]

    for token in forbidden_tokens:
        assert f"import {token}" not in lowered
        assert f"from {token} import" not in lowered
