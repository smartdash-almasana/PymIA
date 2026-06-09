from __future__ import annotations

from pymia.contracts.owner_actions import OwnerNextActionBundle
from pymia.contracts.owner_questions import OwnerQuestionsBundle
from pymia.contracts.owner_resolved_actions import (
    OwnerResolvedNextAction,
    OwnerResolvedNextActionBundle,
)


def resolve_owner_next_action_targets(
    action_bundle: OwnerNextActionBundle,
    questions_bundle: OwnerQuestionsBundle,
) -> OwnerResolvedNextActionBundle:
    question_text_by_id = {
        question.question_id: question.question_text
        for question in questions_bundle.questions
    }
    resolved_actions = [
        _resolve_action(action, question_text_by_id)
        for action in action_bundle.actions
    ]
    return OwnerResolvedNextActionBundle(
        bundle_id=f"{action_bundle.bundle_id}:resolved",
        source_action_bundle_id=action_bundle.bundle_id,
        source_questions_bundle_id=questions_bundle.bundle_id,
        resolved_actions=resolved_actions,
    )


def _resolve_action(
    action,
    question_text_by_id: dict[str, str],
) -> OwnerResolvedNextAction:
    resolved_questions: list[str] = []
    for question_id in action.target_questions:
        question_text = question_text_by_id.get(question_id)
        if question_text is None:
            raise ValueError(f"unknown target_question_id: {question_id}")
        resolved_questions.append(question_text)

    return OwnerResolvedNextAction(
        action_id=action.action_id,
        action_type=action.action_type,
        resolved_questions=resolved_questions,
        metadata=dict(action.metadata or {}),
    )
