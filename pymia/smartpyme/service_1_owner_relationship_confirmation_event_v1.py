"""Canonical owner-confirmation evidence event for a Servicio 1 relationship.

ADR-029 / SEM-5. A relationship confirmation records owner evidence only. It
never grants semantic execution authority, computation readiness, product
readiness or delivery permission.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = "SERVICE_1_OWNER_RELATIONSHIP_CONFIRMATION_EVENT_V1"


def service_1_relationship_ref_v1(
    *,
    left_sheet_ref: str,
    left_column_ref: str,
    right_sheet_ref: str,
    right_column_ref: str,
) -> str:
    left_sheet = str(left_sheet_ref or "").strip()
    left_column = str(left_column_ref or "").strip()
    right_sheet = str(right_sheet_ref or "").strip()
    right_column = str(right_column_ref or "").strip()
    if not all((left_sheet, left_column, right_sheet, right_column)):
        raise ValueError("relationship endpoints are required")
    if left_sheet == right_sheet and left_column == right_column:
        raise ValueError("relationship endpoints must be different")
    return f"{left_sheet}.{left_column}->{right_sheet}.{right_column}"


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

    @property
    def relationship_ref(self) -> str:
        return service_1_relationship_ref_v1(
            left_sheet_ref=self.left_sheet_ref,
            left_column_ref=self.left_column_ref,
            right_sheet_ref=self.right_sheet_ref,
            right_column_ref=self.right_column_ref,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["relationship_ref"] = self.relationship_ref
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

    def to_relationship_binding(self) -> dict[str, Any]:
        """Project owner-confirmed relationship evidence without granting join authority."""
        return {
            "relationship_ref": self.relationship_ref,
            "left_sheet_ref": self.left_sheet_ref,
            "left_column_ref": self.left_column_ref,
            "right_sheet_ref": self.right_sheet_ref,
            "right_column_ref": self.right_column_ref,
            "relationship_kind": self.relationship_kind,
            "confirmed_by_owner": True,
            "question_ref": self.question_ref,
            "provenance": dict(self.provenance),
            "relationship_resolution_authorized": False,
            "join_execution_authorized": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }


def build_service_1_confirmed_relationship_bindings_v1(
    events: Iterable[Service1OwnerRelationshipConfirmationEventV1 | Mapping[str, Any]],
    *,
    case_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Project canonical owner-confirmed relationship evidence for downstream P8 use."""
    expected_case = str(case_id or "").strip() or None
    bindings: dict[str, dict[str, Any]] = {}
    for raw in events:
        if isinstance(raw, Service1OwnerRelationshipConfirmationEventV1):
            event = raw
        elif isinstance(raw, Mapping):
            event = Service1OwnerRelationshipConfirmationEventV1(
                case_id=str(raw.get("case_id") or "").strip(),
                file_ref=str(raw.get("file_ref")).strip() if raw.get("file_ref") is not None else None,
                left_sheet_ref=str(raw.get("left_sheet_ref") or "").strip(),
                left_column_ref=str(raw.get("left_column_ref") or "").strip(),
                right_sheet_ref=str(raw.get("right_sheet_ref") or "").strip(),
                right_column_ref=str(raw.get("right_column_ref") or "").strip(),
                relationship_kind=str(raw.get("relationship_kind") or "").strip(),
                owner_answer=str(raw.get("owner_answer") or "").strip(),
                confirmed_by_owner=raw.get("confirmed_by_owner") is True,
                question_ref=str(raw.get("question_ref") or "").strip(),
                timestamp=str(raw.get("timestamp") or "").strip(),
                provenance=dict(raw.get("provenance") or {}),
                schema_version=str(raw.get("schema_version") or SCHEMA_VERSION),
            )
        else:
            raise TypeError("events must contain relationship confirmation events or mappings")
        if expected_case is not None and event.case_id != expected_case:
            raise ValueError("relationship confirmation case_id mismatch")
        ref = event.relationship_ref
        if ref in bindings:
            raise ValueError(f"duplicate relationship confirmation:{ref}")
        bindings[ref] = event.to_relationship_binding()
    return bindings


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
    "service_1_relationship_ref_v1",
    "Service1OwnerRelationshipConfirmationEventV1",
    "build_service_1_confirmed_relationship_bindings_v1",
    "build_service_1_owner_relationship_confirmation_event_v1",
]
