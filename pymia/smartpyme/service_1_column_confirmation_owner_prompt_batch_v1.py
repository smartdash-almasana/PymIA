from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.contracts.column_confirmation_v1 import ColumnConfirmationMatrix
from pymia.smartpyme.service_1_column_interpretation_to_owner_prompt_bridge_v1 import (
    Service1ColumnInterpretationToOwnerPromptBridgeV1,
    build_service_1_column_interpretation_to_owner_prompt_bridge_v1,
)

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1"
SERVICE_NAME = "SERVICE_1"


@dataclass(frozen=True)
class Service1ColumnConfirmationOwnerPromptBatchV1:
    schema_version: str
    service_name: str
    file_name: str
    matrix_status: str
    total_entries: int
    actionable_entries_count: int
    prompts: tuple[Service1ColumnInterpretationToOwnerPromptBridgeV1, ...]
    has_prompts: bool
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["prompts"] = [prompt.to_dict() for prompt in self.prompts]
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_service_1_column_confirmation_owner_prompt_batch_v1(
    *,
    matrix: ColumnConfirmationMatrix,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationOwnerPromptBatchV1:
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    batch_metadata = dict(metadata or {})
    prompts = tuple(
        build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
            file_name=matrix.file_name,
            entry=entry,
            metadata=batch_metadata,
        )
        for entry in matrix.entries
        if entry.is_actionable()
    )

    return Service1ColumnConfirmationOwnerPromptBatchV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=matrix.file_name,
        matrix_status=matrix.status(),
        total_entries=len(matrix.entries),
        actionable_entries_count=len(prompts),
        prompts=prompts,
        has_prompts=bool(prompts),
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=batch_metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "Service1ColumnConfirmationOwnerPromptBatchV1",
    "build_service_1_column_confirmation_owner_prompt_batch_v1",
]
