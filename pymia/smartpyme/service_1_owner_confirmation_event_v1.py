"""Canonical owner-confirmation evidence event for Servicio 1 Stage 2 Package 2.

The event records what the owner answered. It is evidence only: it never grants
semantic approval, computation readiness, runtime execution, product readiness,
delivery authorization, or diagnosis authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA_VERSION = "SERVICE_1_OWNER_CONFIRMATION_EVENT_V1"

_SCOPE_SEMANTIC_ROLE = "SEMANTIC_ROLE"
_SCOPE_COLUMN_EXCLUSION = "COLUMN_EXCLUSION"
_SCOPE_FREE_TEXT_MEANING = "FREE_TEXT_MEANING"
ALLOWED_CONFIRMATION_SCOPES = frozenset(
    {_SCOPE_SEMANTIC_ROLE, _SCOPE_COLUMN_EXCLUSION, _SCOPE_FREE_TEXT_MEANING}
)


@dataclass(frozen=True)
class Service1OwnerConfirmationEventV1:
    case_id: str
    file_ref: str | None
    region_ref: str | None
    sheet_ref: str
    column_ref: str
    question_ref: str
    proposed_role: str | None
    proposed_variable: str | None
    owner_answer: str
    confirmed_role: str | None
    corrected_meaning: str | None
    confirmation_scope: str
    confirmed_by_owner: bool
    timestamp: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("case_id", "sheet_ref", "column_ref", "question_ref", "owner_answer", "timestamp"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if self.confirmation_scope not in ALLOWED_CONFIRMATION_SCOPES:
            raise ValueError("invalid confirmation_scope")
        if self.confirmed_by_owner is not True:
            raise ValueError("owner confirmation event must be explicitly confirmed_by_owner")
        if self.confirmation_scope == _SCOPE_SEMANTIC_ROLE and not str(self.confirmed_role or "").strip():
            raise ValueError("confirmed_role is required for SEMANTIC_ROLE")
        if self.confirmation_scope == _SCOPE_COLUMN_EXCLUSION and self.confirmed_role is not None:
            raise ValueError("COLUMN_EXCLUSION cannot confirm a semantic role")
        if self.confirmation_scope == _SCOPE_FREE_TEXT_MEANING and not str(self.corrected_meaning or "").strip():
            raise ValueError("corrected_meaning is required for FREE_TEXT_MEANING")
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "computation_candidate_ready",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("provenance cannot carry authorization fields")

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


def build_service_1_owner_confirmation_event_v1(
    *,
    case_id: str,
    file_ref: str | None,
    region_ref: str | None,
    sheet_ref: str,
    column_ref: str,
    question_ref: str,
    owner_answer: str,
    confirmation_scope: str,
    proposed_role: str | None = None,
    proposed_variable: str | None = None,
    confirmed_role: str | None = None,
    corrected_meaning: str | None = None,
    timestamp: str | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> Service1OwnerConfirmationEventV1:
    return Service1OwnerConfirmationEventV1(
        case_id=str(case_id or "").strip(),
        file_ref=str(file_ref).strip() if file_ref is not None else None,
        region_ref=str(region_ref).strip() if region_ref is not None else None,
        sheet_ref=str(sheet_ref or "").strip(),
        column_ref=str(column_ref or "").strip(),
        question_ref=str(question_ref or "").strip(),
        proposed_role=str(proposed_role).strip() if proposed_role else None,
        proposed_variable=str(proposed_variable).strip() if proposed_variable else None,
        owner_answer=str(owner_answer or "").strip(),
        confirmed_role=str(confirmed_role).strip() if confirmed_role else None,
        corrected_meaning=str(corrected_meaning).strip() if corrected_meaning else None,
        confirmation_scope=str(confirmation_scope or "").strip(),
        confirmed_by_owner=True,
        timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
        provenance=dict(provenance or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "ALLOWED_CONFIRMATION_SCOPES",
    "Service1OwnerConfirmationEventV1",
    "build_service_1_owner_confirmation_event_v1",
]
