from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.smartpyme.service_1_owner_prompt_batch_to_question_bundle_alignment_v1 import (
    Service1OwnerPromptBatchToQuestionBundleAlignmentV1,
)

SCHEMA_VERSION = "SERVICE_1_ALIGNED_OWNER_PROMPT_DISPLAY_PACKET_V1"
SERVICE_NAME = "SERVICE_1"
DISPLAY_STATUS_READY = "READY"
DISPLAY_STATUS_EMPTY = "EMPTY"
DISPLAY_STATUS_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Service1AlignedOwnerPromptDisplayItemV1:
    display_index: int
    question_ref: str
    target_ref: str
    answer_type: str
    question_status: str
    file_name: str
    sheet_name: str
    column_name: str
    owner_label: str
    display_title: str
    prompt_text: str
    allowed_owner_responses: tuple[str, ...]
    operator_note: str
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_owner_responses"] = list(self.allowed_owner_responses)
        return data

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required


@dataclass(frozen=True)
class Service1AlignedOwnerPromptDisplayPacketV1:
    schema_version: str
    service_name: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    file_name: str
    display_status: str
    total_items: int
    items: tuple[Service1AlignedOwnerPromptDisplayItemV1, ...]
    blocked_reason: str | None
    unaligned_prompt_targets: tuple[str, ...]
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["items"] = [item.to_dict() for item in self.items]
        data["unaligned_prompt_targets"] = list(self.unaligned_prompt_targets)
        return data

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _display_status(alignment: Service1OwnerPromptBatchToQuestionBundleAlignmentV1) -> tuple[str, str | None]:
    if alignment.aligned_prompts_count == 0 and alignment.total_prompts == 0:
        return DISPLAY_STATUS_EMPTY, "NO_ALIGNED_PROMPTS_TO_DISPLAY"
    if alignment.aligned_prompts_count == 0:
        return DISPLAY_STATUS_BLOCKED, "NO_PROMPTS_WITH_QUESTION_REF"
    return DISPLAY_STATUS_READY, None


def build_service_1_aligned_owner_prompt_display_packet_v1(
    *,
    alignment: Service1OwnerPromptBatchToQuestionBundleAlignmentV1,
    metadata: dict[str, Any] | None = None,
) -> Service1AlignedOwnerPromptDisplayPacketV1:
    if not isinstance(alignment, Service1OwnerPromptBatchToQuestionBundleAlignmentV1):
        raise ValueError("alignment must be a Service1OwnerPromptBatchToQuestionBundleAlignmentV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    packet_metadata = dict(metadata or {})
    status, blocked_reason = _display_status(alignment)
    items: list[Service1AlignedOwnerPromptDisplayItemV1] = []
    for index, prompt in enumerate(alignment.aligned_prompts, start=1):
        item_metadata = dict(packet_metadata)
        item_metadata.update(prompt.metadata)
        items.append(
            Service1AlignedOwnerPromptDisplayItemV1(
                display_index=index,
                question_ref=prompt.question_ref,
                target_ref=prompt.target_ref,
                answer_type=prompt.answer_type,
                question_status=prompt.question_status,
                file_name=prompt.file_name,
                sheet_name=prompt.sheet_name,
                column_name=prompt.column_name,
                owner_label=prompt.owner_label,
                display_title=f"Pregunta {index}: confirmar columna {prompt.column_name}",
                prompt_text=prompt.prompt_text,
                allowed_owner_responses=prompt.allowed_owner_responses,
                operator_note="Registrar la respuesta usando este question_ref. No recalcular ni reejecutar automaticamente.",
                runtime_authorized=False,
                owner_confirmation_required=True,
                reexecution_authorized=False,
                recalculation_authorized=False,
                persistence_authorized=False,
                metadata=item_metadata,
            )
        )

    return Service1AlignedOwnerPromptDisplayPacketV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=alignment.case_id,
        tenant_id=alignment.tenant_id,
        intake_id=alignment.intake_id,
        run_id=alignment.run_id,
        file_name=alignment.file_name,
        display_status=status,
        total_items=len(items),
        items=tuple(items),
        blocked_reason=blocked_reason,
        unaligned_prompt_targets=alignment.unaligned_prompt_targets,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=packet_metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "DISPLAY_STATUS_READY",
    "DISPLAY_STATUS_EMPTY",
    "DISPLAY_STATUS_BLOCKED",
    "Service1AlignedOwnerPromptDisplayItemV1",
    "Service1AlignedOwnerPromptDisplayPacketV1",
    "build_service_1_aligned_owner_prompt_display_packet_v1",
]
