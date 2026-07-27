from __future__ import annotations

from dataclasses import dataclass

from pymia.contracts.owner_answers import OwnerAnswersBundle
from pymia.contracts.owner_evaluation import OwnerAnswerEvaluationBundle
from pymia.contracts.owner_questions import OwnerQuestionsBundle
from pymia.contracts.owner_actions import OwnerNextActionBundle
from pymia.contracts.owner_resolved_actions import OwnerResolvedNextActionBundle
from pymia.smartpyme.owner_actions_decider import decide_owner_next_action
from pymia.smartpyme.owner_actions_projector import (
    project_resolved_owner_actions_to_render_contract,
)
from pymia.smartpyme.owner_actions_resolver import resolve_owner_next_action_targets
from pymia.smartpyme.owner_answers_evaluator import evaluate_owner_answers


@dataclass(frozen=True)
class OwnerActionPipelineResult:
    projected_render_contract: dict
    evaluation_bundle: OwnerAnswerEvaluationBundle
    action_bundle: OwnerNextActionBundle
    resolved_action_bundle: OwnerResolvedNextActionBundle


def build_owner_action_projection_pipeline(
    *,
    owner_answers_bundle: OwnerAnswersBundle,
    owner_questions_bundle: OwnerQuestionsBundle,
    render_contract: dict,
) -> OwnerActionPipelineResult:
    _validate_answer_question_alignment(
        owner_answers_bundle=owner_answers_bundle,
        owner_questions_bundle=owner_questions_bundle,
    )

    evaluation_bundle = evaluate_owner_answers(owner_answers_bundle)
    action_bundle = decide_owner_next_action(evaluation_bundle)
    resolved_action_bundle = resolve_owner_next_action_targets(
        action_bundle=action_bundle,
        questions_bundle=owner_questions_bundle,
    )
    projected_render_contract = project_resolved_owner_actions_to_render_contract(
        render_contract=render_contract,
        resolved_action_bundle=resolved_action_bundle,
    )
    return OwnerActionPipelineResult(
        projected_render_contract=projected_render_contract,
        evaluation_bundle=evaluation_bundle,
        action_bundle=action_bundle,
        resolved_action_bundle=resolved_action_bundle,
    )


def _validate_answer_question_alignment(
    *,
    owner_answers_bundle: OwnerAnswersBundle,
    owner_questions_bundle: OwnerQuestionsBundle,
) -> None:
    question_ids = {
        question.question_id
        for question in owner_questions_bundle.questions
    }
    missing_ids = [
        answer.question_id
        for answer in owner_answers_bundle.answers
        if answer.question_id not in question_ids
    ]
    if missing_ids:
        missing_text = ", ".join(missing_ids)
        raise ValueError(f"owner answers not aligned with questions bundle: {missing_text}")
