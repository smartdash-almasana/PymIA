from __future__ import annotations

from pymia.contracts.owner_actions import OwnerNextAction, OwnerNextActionBundle
from pymia.contracts.owner_evaluation import OwnerAnswerEvaluationBundle


def decide_owner_next_action(
    bundle: OwnerAnswerEvaluationBundle,
) -> OwnerNextActionBundle:
    action = _decide_action(bundle)
    return OwnerNextActionBundle(
        bundle_id=f"{bundle.bundle_id}:next_action",
        source_evaluation_bundle_id=bundle.bundle_id,
        actions=[action],
    )


def _decide_action(bundle: OwnerAnswerEvaluationBundle) -> OwnerNextAction:
    evaluations = list(bundle.evaluations)
    action_id = f"{bundle.bundle_id}:action:0"

    if not evaluations:
        return OwnerNextAction(
            action_id=action_id,
            action_type="ask_clarification",
            target_questions=[],
            metadata={"reason": "empty_bundle"},
        )

    clarification_questions = [
        item.linked_question_id
        for item in evaluations
        if item.verdict == "needs_clarification"
    ]
    if clarification_questions:
        return OwnerNextAction(
            action_id=action_id,
            action_type="ask_clarification",
            target_questions=clarification_questions,
            metadata={"reason": "needs_clarification"},
        )

    rejected_questions = [
        item.linked_question_id
        for item in evaluations
        if item.verdict == "rejected"
    ]
    if rejected_questions:
        return OwnerNextAction(
            action_id=action_id,
            action_type="reject_answer",
            target_questions=rejected_questions,
            metadata={"reason": "rejected"},
        )

    return OwnerNextAction(
        action_id=action_id,
        action_type="keep_as_declared",
        target_questions=[item.linked_question_id for item in evaluations],
        metadata={"reason": "accepted_or_verified"},
    )
