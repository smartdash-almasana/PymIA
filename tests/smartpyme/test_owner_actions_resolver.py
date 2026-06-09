from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.owner_actions import OwnerNextAction, OwnerNextActionBundle
from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle
from pymia.contracts.owner_resolved_actions import OwnerResolvedNextActionBundle


def test_owner_resolved_next_action_contract_rejects_invalid_action_type() -> None:
    from pymia.contracts.owner_resolved_actions import OwnerResolvedNextAction

    with pytest.raises(ValueError):
        OwnerResolvedNextAction(
            action_id="resolved-1",
            action_type="unsupported",
            resolved_questions=["Pregunta"],
        )


def test_resolve_owner_next_action_targets_resolves_single_id_to_exact_text() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-1",
        source_evaluation_bundle_id="eval-bundle-1",
        actions=[
            OwnerNextAction(
                action_id="action-1",
                action_type="ask_clarification",
                target_questions=["q-1"],
                metadata={"reason": "needs_clarification"},
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-1",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Qué período cubre esta planilla?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
            )
        ],
    )

    result = resolve_owner_next_action_targets(action_bundle, questions_bundle)

    assert isinstance(result, OwnerResolvedNextActionBundle)
    assert result.resolved_actions[0].resolved_questions == [
        "¿Qué período cubre esta planilla?"
    ]


def test_resolve_owner_next_action_targets_resolves_multiple_ids_preserving_order() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-2",
        source_evaluation_bundle_id="eval-bundle-2",
        actions=[
            OwnerNextAction(
                action_id="action-2",
                action_type="reject_answer",
                target_questions=["q-2", "q-1"],
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-2",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Cuántos días tiene el período?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
            ),
            OwnerQuestion(
                question_id="q-2",
                question_text="¿Cuál es el monto de impuestos?",
                reason="missing_evidence",
                source_ref="operational_audit_result://missing_evidence/0",
            ),
        ],
    )

    result = resolve_owner_next_action_targets(action_bundle, questions_bundle)

    assert result.resolved_actions[0].resolved_questions == [
        "¿Cuál es el monto de impuestos?",
        "¿Cuántos días tiene el período?",
    ]


def test_resolve_owner_next_action_targets_fails_closed_on_unknown_id() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-3",
        source_evaluation_bundle_id="eval-bundle-3",
        actions=[
            OwnerNextAction(
                action_id="action-3",
                action_type="ask_clarification",
                target_questions=["q-missing"],
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(bundle_id="questions-3", questions=[])

    with pytest.raises(ValueError) as exc:
        resolve_owner_next_action_targets(action_bundle, questions_bundle)

    assert "unknown target_question_id" in str(exc.value)


def test_resolve_owner_next_action_targets_keep_as_declared_also_resolves_questions() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-4",
        source_evaluation_bundle_id="eval-bundle-4",
        actions=[
            OwnerNextAction(
                action_id="action-4",
                action_type="keep_as_declared",
                target_questions=["q-4"],
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-4",
        questions=[
            OwnerQuestion(
                question_id="q-4",
                question_text="¿Qué significa la columna ajuste?",
                reason="blocked_message",
                source_ref="render_contract://blocked_message",
            )
        ],
    )

    result = resolve_owner_next_action_targets(action_bundle, questions_bundle)

    assert result.resolved_actions[0].action_type == "keep_as_declared"
    assert result.resolved_actions[0].resolved_questions == [
        "¿Qué significa la columna ajuste?"
    ]


def test_resolve_owner_next_action_targets_action_without_targets_keeps_empty_resolved_questions() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-5",
        source_evaluation_bundle_id="eval-bundle-5",
        actions=[
            OwnerNextAction(
                action_id="action-5",
                action_type="ask_clarification",
                target_questions=[],
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(bundle_id="questions-5", questions=[])

    result = resolve_owner_next_action_targets(action_bundle, questions_bundle)

    assert result.resolved_actions[0].resolved_questions == []


def test_resolve_owner_next_action_targets_preserves_source_bundle_ids_and_serializes() -> None:
    from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets

    action_bundle = OwnerNextActionBundle(
        bundle_id="action-bundle-6",
        source_evaluation_bundle_id="eval-bundle-6",
        actions=[
            OwnerNextAction(
                action_id="action-6",
                action_type="ask_clarification",
                target_questions=["q-6"],
                metadata={"reason": "needs_clarification"},
            )
        ],
    )
    questions_bundle = OwnerQuestionsBundle(
        bundle_id="questions-6",
        questions=[
            OwnerQuestion(
                question_id="q-6",
                question_text="¿Podés aclarar el período?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
            )
        ],
    )

    payload = resolve_owner_next_action_targets(
        action_bundle,
        questions_bundle,
    ).model_dump(mode="json")

    assert payload["source_action_bundle_id"] == "action-bundle-6"
    assert payload["source_questions_bundle_id"] == "questions-6"
    assert payload["resolved_actions"][0]["resolved_questions"] == [
        "¿Podés aclarar el período?"
    ]
    assert "q-6" not in payload["resolved_actions"][0]["resolved_questions"]


def test_owner_actions_resolver_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_actions_resolver.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "graph",
        "pymiastate",
        "core_delivery_bridge",
        "owner_facing_report",
        "delivery_markdown",
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
