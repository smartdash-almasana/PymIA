from __future__ import annotations

from dataclasses import dataclass

from pymia.contracts.owner_actions import OwnerNextActionBundle
from pymia.contracts.owner_answers import OwnerAnswersBundle
from pymia.contracts.owner_evaluation import OwnerAnswerEvaluationBundle
from pymia.contracts.owner_questions import OwnerQuestionsBundle
from pymia.contracts.owner_resolved_actions import OwnerResolvedNextActionBundle
from pymia.smartpyme.owner_action_pipeline import build_owner_action_projection_pipeline
from pymia.smartpyme.owner_answers_capture import (
    capture_owner_answers_from_structured_payload,
)


@dataclass(frozen=True)
class OwnerAnswerToActionCompositionResult:
    owner_answers_bundle: OwnerAnswersBundle
    evaluation_bundle: OwnerAnswerEvaluationBundle
    action_bundle: OwnerNextActionBundle
    resolved_action_bundle: OwnerResolvedNextActionBundle
    projected_render_contract: dict


def compose_owner_answers_to_actions(
    *,
    questions_bundle: OwnerQuestionsBundle,
    answers_payload: list[dict],
    source_ref: str,
    render_contract: dict,
    tenant_id: str | None = None,
) -> OwnerAnswerToActionCompositionResult:
    owner_answers_bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref=source_ref,
        tenant_id=tenant_id,
    )
    pipeline_result = build_owner_action_projection_pipeline(
        owner_answers_bundle=owner_answers_bundle,
        owner_questions_bundle=questions_bundle,
        render_contract=render_contract,
    )
    return OwnerAnswerToActionCompositionResult(
        owner_answers_bundle=owner_answers_bundle,
        evaluation_bundle=pipeline_result.evaluation_bundle,
        action_bundle=pipeline_result.action_bundle,
        resolved_action_bundle=pipeline_result.resolved_action_bundle,
        projected_render_contract=pipeline_result.projected_render_contract,
    )
