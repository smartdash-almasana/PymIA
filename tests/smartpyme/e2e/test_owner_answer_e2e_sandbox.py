from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle
from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions
from pymia.smartpyme.owner_answer_replay_formatter import (
    format_composition_result_for_human_review,
)


def _build_sandbox_result():
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="sandbox-questions",
        questions=[
            OwnerQuestion(
                question_id="q_dias_periodo",
                question_text="¿Cuántos días tiene el período analizado?",
                reason="missing_evidence",
                missing_key="dias_periodo",
                source_ref="operational_audit_result://missing_evidence/0",
                expected_answer_type="number",
            ),
            OwnerQuestion(
                question_id="q_evidencia_ventas",
                question_text="¿Hay evidencia de ventas que no se registró?",
                reason="blocked_message",
                missing_key="evidencia_ventas",
                source_ref="render_contract://blocked_message",
                expected_answer_type="text",
            ),
        ],
        metadata={"sandbox": True},
    )
    answers_payload = [
        {
            "question_id": "q_dias_periodo",
            "answer_text": "30",
        },
        {
            "question_id": "q_evidencia_ventas",
            "answer_text": "Sí, hay ventas manuales no registradas",
        },
    ]
    render_contract = {
        "tenant_id": "tenant-sandbox",
        "references": ["source://sandbox"],
        "next_steps": [],
        "limit_warnings": [],
    }
    return questions_bundle, answers_payload, render_contract


def test_owner_answer_e2e_sandbox_replays_composition_to_projected_render_contract() -> None:
    questions_bundle, answers_payload, render_contract = _build_sandbox_result()
    payload_before = deepcopy(answers_payload)
    render_before = deepcopy(render_contract)

    result = compose_owner_answers_to_actions(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref="sandbox://owner_answers_payload",
        render_contract=render_contract,
        tenant_id="tenant-sandbox",
    )

    assert len(result.owner_answers_bundle.answers) == 2
    assert result.evaluation_bundle.evaluations
    assert result.action_bundle.actions
    assert result.resolved_action_bundle.resolved_actions
    assert isinstance(result.projected_render_contract, dict)
    assert [
        item.verdict for item in result.evaluation_bundle.evaluations
    ] == ["accepted_as_declared", "needs_clarification"]
    assert result.action_bundle.actions[0].action_type == "ask_clarification"
    assert result.resolved_action_bundle.resolved_actions[0].resolved_questions == [
        "¿Hay evidencia de ventas que no se registró?",
    ]
    assert result.projected_render_contract["next_questions"] == [
        "¿Hay evidencia de ventas que no se registró?",
    ]
    assert (
        result.projected_render_contract["blocked_message"]
        == "¿Hay evidencia de ventas que no se registró?"
    )
    assert "q_dias_periodo" not in str(result.projected_render_contract)
    assert "q_evidencia_ventas" not in str(result.projected_render_contract)
    assert answers_payload == payload_before
    assert render_contract == render_before
    assert result.projected_render_contract is not render_contract


def test_owner_answer_replay_formatter_builds_human_markdown_review() -> None:
    questions_bundle, answers_payload, render_contract = _build_sandbox_result()
    result = compose_owner_answers_to_actions(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref="sandbox://owner_answers_payload",
        render_contract=render_contract,
        tenant_id="tenant-sandbox",
    )
    projected_before = deepcopy(result.projected_render_contract)

    markdown = format_composition_result_for_human_review(result)

    assert markdown.startswith("# Revisión sandbox de respuestas del dueño")
    assert "## Respuestas capturadas" in markdown
    assert "## Evaluación de respuestas" in markdown
    assert "## Próxima acción resuelta" in markdown
    assert "## Cambios proyectados en render_contract" in markdown
    assert "30" in markdown
    assert "Sí, hay ventas manuales no registradas" in markdown
    assert "needs_clarification" in markdown
    assert "ask_clarification" in markdown
    assert "¿Hay evidencia de ventas que no se registró?" in markdown
    assert "q_dias_periodo" not in markdown
    assert "q_evidencia_ventas" not in markdown
    assert result.projected_render_contract == projected_before


def test_owner_answer_replay_formatter_handles_empty_sections_without_error() -> None:
    questions_bundle, answers_payload, render_contract = _build_sandbox_result()
    result = compose_owner_answers_to_actions(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref="sandbox://owner_answers_payload",
        render_contract=render_contract,
        tenant_id="tenant-sandbox",
    )
    empty_result = result.__class__(
        owner_answers_bundle=result.owner_answers_bundle.__class__(
            bundle_id="empty-answers",
            answers=[],
        ),
        evaluation_bundle=result.evaluation_bundle.__class__(
            bundle_id="empty-evaluations",
            source_answers_bundle_id="empty-answers",
            evaluations=[],
        ),
        action_bundle=result.action_bundle.__class__(
            bundle_id="empty-actions",
            source_evaluation_bundle_id="empty-evaluations",
            actions=[],
        ),
        resolved_action_bundle=result.resolved_action_bundle.__class__(
            bundle_id="empty-resolved-actions",
            source_action_bundle_id="empty-actions",
            source_questions_bundle_id="sandbox-questions",
            resolved_actions=[],
        ),
        projected_render_contract={},
    )

    markdown = format_composition_result_for_human_review(empty_result)

    assert "Información incompleta en replay sandbox." in markdown
    assert "## Advertencias y límites" in markdown


def test_owner_answer_e2e_sandbox_has_no_prohibited_imports() -> None:
    paths = [
        Path(__file__),
        Path("pymia/smartpyme/owner_answer_replay_formatter.py"),
    ]
    forbidden_tokens = [
        "core_delivery_bridge",
        "conversation_adapter",
        "owner_facing_report",
        "diagnostic_core",
        "telegram",
    ]

    for path in paths:
        source = path.read_text(encoding="utf-8").lower()
        for token in forbidden_tokens:
            assert f"import {token}" not in source
            assert f"from {token} import" not in source
