from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.contracts.column_confirmation_v1 import ColumnConfirmationEntry
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_v1 import (
    Service1ColumnConfirmationOwnerPromptV1,
    build_service_1_column_confirmation_owner_prompt_v1,
)
from pymia.smartpyme.service_1_owner_facing_role_explanation_catalog_v1 import (
    Service1OwnerFacingRoleExplanationV1,
    explain_owner_facing_semantic_role_v1,
)

SCHEMA_VERSION = "SERVICE_1_COLUMN_INTERPRETATION_TO_OWNER_PROMPT_BRIDGE_V1"
SERVICE_NAME = "SERVICE_1"


@dataclass(frozen=True)
class Service1ColumnInterpretationToOwnerPromptBridgeV1:
    schema_version: str
    service_name: str
    file_name: str
    sheet_name: str
    column_name: str
    suggested_semantic_role: str
    owner_label: str
    owner_facing_role_explanation: str
    known_role: bool
    calculation_relevance: str
    owner_prompt: Service1ColumnConfirmationOwnerPromptV1
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["owner_prompt"] = self.owner_prompt.to_dict()
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
    *,
    file_name: str,
    entry: ColumnConfirmationEntry,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnInterpretationToOwnerPromptBridgeV1:
    if not isinstance(entry, ColumnConfirmationEntry):
        raise ValueError("entry must be a ColumnConfirmationEntry")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    file_name = _required_text(file_name, field_name="file_name")
    explanation: Service1OwnerFacingRoleExplanationV1 = explain_owner_facing_semantic_role_v1(
        entry.suggested_semantic_role,
    )
    owner_prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name=file_name,
        sheet_name=entry.sheet_name,
        column_name=entry.original_column_name,
        suggested_semantic_role=explanation.semantic_role,
        owner_facing_role_explanation=explanation.owner_facing_role_explanation,
        metadata=metadata,
    )

    return Service1ColumnInterpretationToOwnerPromptBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=file_name,
        sheet_name=entry.sheet_name,
        column_name=entry.original_column_name,
        suggested_semantic_role=explanation.semantic_role,
        owner_label=explanation.owner_label,
        owner_facing_role_explanation=explanation.owner_facing_role_explanation,
        known_role=explanation.known_role,
        calculation_relevance=explanation.calculation_relevance,
        owner_prompt=owner_prompt,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "Service1ColumnInterpretationToOwnerPromptBridgeV1",
    "build_service_1_column_interpretation_to_owner_prompt_bridge_v1",
]
