"""Canonical owner-confirmation evidence event for a Servicio 1 relationship.

ADR-029 / SEM-5. A relationship confirmation records owner evidence only. It
never grants semantic execution authority, computation readiness, product
readiness or delivery permission.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA_VERSION = "SERVICE_1_OWNER_RELATIONSHIP_CONFIRMATION_EVENT_V1"


@dataclass(frozen=True)
class Service1OwnerRelationshipConfirmationEventV1:
    case_id: str
    file_ref: str | None
    left_sheet_ref: str
    left_column_ref: str
    right_sheet_ref: str
    right_column_ref: str
    relationship_kind: str
    owner_answer: str
    confirmed_by_owner: bool
    question_ref: str
    timestamp: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "case_id",
            "left_sheet_ref",
            "left_column_ref",
            "right_sheet_ref",
            "right_column_ref",
            "relationship_kind",
            "owner_answer",
            "question_ref",
            "timestamp",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if (
            self.left_sheet_ref == self.right_sheet_ref
            and self.left_column_ref == self.right_column_ref
        ):
            raise ValueError("relationship endpoints must be different")
        if self.confirmed_by_owner is not True:
            raise ValueError(
                "relationship confirmation event must be explicitly confirmed_by_owner"
            )
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "computation_candidate_ready",
            "automatic_reuse_authorized",
            "semantic_rebind_authorized",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("provenance cannot carry authority fields")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["provenance"] = dict(self.provenance)
        payload.update(
            {
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "product_ready": False,
                "delivery_authorized": False,
                "diagnosis_generated": False,
            }
        )
        return payload


def build_service_1_owner_relationship_confirmation_event_v1(
    *,
    case_id: str,
    file_ref: str | None,
    left_sheet_ref: str,
    left_column_ref: str,
    right_sheet_ref: str,
    right_column_ref: str,
    relationship_kind: str,
    owner_answer: str,
    question_ref: str,
    timestamp: str | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> Service1OwnerRelationshipConfirmationEventV1:
    return Service1OwnerRelationshipConfirmationEventV1(
        case_id=str(case_id or "").strip(),
        file_ref=str(file_ref).strip() if file_ref is not None else None,
        left_sheet_ref=str(left_sheet_ref or "").strip(),
        left_column_ref=str(left_column_ref or "").strip(),
        right_sheet_ref=str(right_sheet_ref or "").strip(),
        right_column_ref=str(right_column_ref or "").strip(),
        relationship_kind=str(relationship_kind or "").strip(),
        owner_answer=str(owner_answer or "").strip(),
        confirmed_by_owner=True,
        question_ref=str(question_ref or "").strip(),
        timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
        provenance=dict(provenance or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "Service1OwnerRelationshipConfirmationEventV1",
    "build_service_1_owner_relationship_confirmation_event_v1",
]
