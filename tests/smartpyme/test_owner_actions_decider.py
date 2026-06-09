from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.owner_evaluation import (
    OwnerAnswerEvaluation,
    OwnerAnswerEvaluationBundle,
)


def test_owner_next_action_contract_rejects_invalid_action_type() -> None:
    from pymia.contracts.owner_actions import OwnerNextAction

    with pytest.raises(ValueError):
        OwnerNextAction(
            action_id="action-1",
            action_type="unsupported",
            target_questions=["q-1"],
        )


def test_decide_owner_next_action_empty_bundle_asks_clarification() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-1",
        source_answers_bundle_id="answers-1",
        evaluations=[],
    )

    result = decide_owner_next_action(bundle)

    assert result.source_evaluation_bundle_id == "eval-bundle-1"
    assert result.actions[0].action_type == "ask_clarification"
    assert result.actions[0].metadata["reason"] == "empty_bundle"


def test_decide_owner_next_action_needs_clarification_dominates_rejected() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-2",
        source_answers_bundle_id="answers-2",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-1",
                source_answer_id="a-1",
                linked_question_id="q-1",
                verdict="rejected",
            ),
            OwnerAnswerEvaluation(
                evaluation_id="eval-2",
                source_answer_id="a-2",
                linked_question_id="q-2",
                verdict="needs_clarification",
                validation_errors=["empty_answer"],
            ),
        ],
    )

    result = decide_owner_next_action(bundle)

    assert result.actions[0].action_type == "ask_clarification"
    assert result.actions[0].target_questions == ["q-2"]


def test_decide_owner_next_action_rejected_without_needs_clarification_rejects() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-3",
        source_answers_bundle_id="answers-3",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-3",
                source_answer_id="a-3",
                linked_question_id="q-3",
                verdict="rejected",
                validation_errors=["number_not_parseable"],
            )
        ],
    )

    result = decide_owner_next_action(bundle)

    assert result.actions[0].action_type == "reject_answer"
    assert result.actions[0].target_questions == ["q-3"]


def test_decide_owner_next_action_accepted_as_declared_keeps_declared() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-4",
        source_answers_bundle_id="answers-4",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-4",
                source_answer_id="a-4",
                linked_question_id="q-4",
                verdict="accepted_as_declared",
            )
        ],
    )

    result = decide_owner_next_action(bundle)

    assert result.actions[0].action_type == "keep_as_declared"
    assert result.actions[0].target_questions == ["q-4"]


def test_decide_owner_next_action_verified_also_keeps_declared_without_side_effects() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-5",
        source_answers_bundle_id="answers-5",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-5",
                source_answer_id="a-5",
                linked_question_id="q-5",
                verdict="verified",
            )
        ],
    )

    result = decide_owner_next_action(bundle)

    assert result.actions[0].action_type == "keep_as_declared"
    assert result.source_evaluation_bundle_id == "eval-bundle-5"


def test_decide_owner_next_action_serializes_bundle_without_evidence_candidate() -> None:
    from pymia.smartpyme.owner_actions_decider import decide_owner_next_action

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="eval-bundle-6",
        source_answers_bundle_id="answers-6",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-6",
                source_answer_id="a-6",
                linked_question_id="q-6",
                verdict="accepted_as_declared",
            )
        ],
    )

    payload = decide_owner_next_action(bundle).model_dump(mode="json")

    assert payload["bundle_id"] == "eval-bundle-6:next_action"
    assert payload["source_evaluation_bundle_id"] == "eval-bundle-6"
    assert "evidence_candidate" not in str(payload)


def test_owner_actions_decider_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_actions_decider.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "graph",
        "pymiastate",
        "core_delivery_bridge",
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
