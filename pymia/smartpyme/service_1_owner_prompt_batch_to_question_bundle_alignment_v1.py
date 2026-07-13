from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    Service1ColumnConfirmationOwnerPromptBatchV1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
    SOURCE_COLUMN_CONFIRMATION,
    Service1QuestionBundleV1,
    Service1QuestionV1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1"
SERVICE_NAME = "SERVICE_1"

ALIGNMENT_STATUS_ALIGNED = "ALIGNED"
ALIGNMENT_STATUS_PARTIAL = "PARTIAL"
ALIGNMENT_STATUS_EMPTY = "EMPTY"
ALIGNMENT_STATUS_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Service1AlignedOwnerPromptV1:
    question_ref: str
    target_ref: str
    answer_type: str
    question_status: str
    question_text: str
    file_name: str
    sheet_name: str
    column_name: str
    owner_label: str
    owner_facing_role_explanation: str
    prompt_text: str
    allowed_owner_responses: tuple[str, ...]
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_owner_responses"] = list(self.allowed_owner_responses)
        return data


@dataclass(frozen=True)
class Service1OwnerPromptBatchToQuestionBundleAlignmentV1:
    schema_version: str
    service_name: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    file_name: str
    selected_next_question_ref: str | None
    total_prompts: int
    aligned_prompts_count: int
    unaligned_prompts_count: int
    aligned_prompts: tuple[Service1AlignedOwnerPromptV1, ...]
    unaligned_prompt_targets: tuple[str, ...]
    alignment_status: str
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["aligned_prompts"] = [prompt.to_dict() for prompt in self.aligned_prompts]
        data["unaligned_prompt_targets"] = list(self.unaligned_prompt_targets)
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _target_ref(*, file_name: str, sheet_name: str, column_name: str) -> str:
    return ":".join(
        part
        for part in ("file", file_name, "sheet", sheet_name, "column", column_name)
        if part
    )


def _question_lookup(question_bundle: Service1QuestionBundleV1) -> dict[str, Service1QuestionV1]:
    lookup: dict[str, Service1QuestionV1] = {}
    for question in question_bundle.questions:
        if question.source != SOURCE_COLUMN_CONFIRMATION:
            continue
        if question.answer_type != ANSWER_TYPE_CONFIRM_COLUMN_ROLE:
            continue
        lookup.setdefault(question.target_ref, question)
    return lookup


def _alignment_status(*, total: int, aligned: int, unaligned: int) -> str:
    if total == 0:
        return ALIGNMENT_STATUS_EMPTY
    if aligned == total and unaligned == 0:
        return ALIGNMENT_STATUS_ALIGNED
    if aligned > 0:
        return ALIGNMENT_STATUS_PARTIAL
    return ALIGNMENT_STATUS_BLOCKED


def align_service_1_owner_prompt_batch_to_question_bundle_v1(
    *,
    question_bundle: Service1QuestionBundleV1,
    owner_prompt_batch: Service1ColumnConfirmationOwnerPromptBatchV1,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerPromptBatchToQuestionBundleAlignmentV1:
    if not isinstance(question_bundle, Service1QuestionBundleV1):
        raise ValueError("question_bundle must be a Service1QuestionBundleV1")
    if not isinstance(owner_prompt_batch, Service1ColumnConfirmationOwnerPromptBatchV1):
        raise ValueError("owner_prompt_batch must be a Service1ColumnConfirmationOwnerPromptBatchV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    alignment_metadata = dict(metadata or {})
    lookup = _question_lookup(question_bundle)
    aligned: list[Service1AlignedOwnerPromptV1] = []
    unaligned_targets: list[str] = []

    for prompt_bridge in owner_prompt_batch.prompts:
        owner_prompt = prompt_bridge.owner_prompt
        target_ref = _target_ref(
            file_name=prompt_bridge.file_name,
            sheet_name=prompt_bridge.sheet_name,
            column_name=prompt_bridge.column_name,
        )
        question = lookup.get(target_ref)
        if question is None:
            unaligned_targets.append(target_ref)
            continue

        record_metadata = dict(alignment_metadata)
        record_metadata.update(
            {
                "source_prompt_schema_version": prompt_bridge.schema_version,
                "source_owner_prompt_schema_version": owner_prompt.schema_version,
            }
        )
        aligned.append(
            Service1AlignedOwnerPromptV1(
                question_ref=question.question_ref,
                target_ref=question.target_ref,
                answer_type=question.answer_type,
                question_status=question.status,
                question_text=question.text,
                file_name=prompt_bridge.file_name,
                sheet_name=prompt_bridge.sheet_name,
                column_name=prompt_bridge.column_name,
                owner_label=prompt_bridge.owner_label,
                owner_facing_role_explanation=prompt_bridge.owner_facing_role_explanation,
                prompt_text=owner_prompt.prompt_text,
                allowed_owner_responses=owner_prompt.allowed_owner_responses,
                runtime_authorized=False,
                human_review_required=True,
                reexecution_authorized=False,
                recalculation_authorized=False,
                persistence_authorized=False,
                metadata=record_metadata,
            )
        )

    return Service1OwnerPromptBatchToQuestionBundleAlignmentV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=question_bundle.case_id,
        tenant_id=question_bundle.tenant_id,
        intake_id=question_bundle.intake_id,
        run_id=question_bundle.run_id,
        file_name=owner_prompt_batch.file_name,
        selected_next_question_ref=question_bundle.selected_next_question_ref,
        total_prompts=len(owner_prompt_batch.prompts),
        aligned_prompts_count=len(aligned),
        unaligned_prompts_count=len(unaligned_targets),
        aligned_prompts=tuple(aligned),
        unaligned_prompt_targets=tuple(unaligned_targets),
        alignment_status=_alignment_status(
            total=len(owner_prompt_batch.prompts),
            aligned=len(aligned),
            unaligned=len(unaligned_targets),
        ),
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=alignment_metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "ALIGNMENT_STATUS_ALIGNED",
    "ALIGNMENT_STATUS_PARTIAL",
    "ALIGNMENT_STATUS_EMPTY",
    "ALIGNMENT_STATUS_BLOCKED",
    "Service1AlignedOwnerPromptV1",
    "Service1OwnerPromptBatchToQuestionBundleAlignmentV1",
    "align_service_1_owner_prompt_batch_to_question_bundle_v1",
]
