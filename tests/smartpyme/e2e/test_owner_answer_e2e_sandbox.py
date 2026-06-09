from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


def test_owner_answer_e2e_sandbox_replays_composition_to_projected_render_contract() -> None:
    from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions

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


def test_owner_answer_e2e_sandbox_has_no_prohibited_imports() -> None:
    source = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden_tokens = [
        "graph",
        "state",
        "conversation_adapter",
        "core_delivery_bridge",
        "telegram",
        "diagnostic_core",
        "owner_facing_report",
        "llm",
        "runtime",
    ]

    for token in forbidden_tokens:
        assert f"import {token}" not in source
        assert f"from {token} import" not in source
