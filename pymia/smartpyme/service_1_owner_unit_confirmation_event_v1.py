"""Canonical owner-confirmed unit evidence for Servicio 1.

Represents explicit owner evidence about the unit/interpretation of one already
semantically confirmed source column. It is evidence only: it cannot authorize
runtime, tools, product readiness, delivery or diagnosis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final, Mapping

SCHEMA_VERSION: Final[str] = "SERVICE_1_OWNER_UNIT_CONFIRMATION_EVENT_V1"
UNIT_DISCOUNT_FRACTION: Final[str] = "DISCOUNT_FRACTION_0_1"
UNIT_DISCOUNT_PERCENT: Final[str] = "DISCOUNT_PERCENT_0_100"
UNIT_DISCOUNT_LINE_AMOUNT: Final[str] = "DISCOUNT_LINE_AMOUNT"
ALLOWED_UNIT_KINDS: Final[frozenset[str]] = frozenset(
    {UNIT_DISCOUNT_FRACTION, UNIT_DISCOUNT_PERCENT, UNIT_DISCOUNT_LINE_AMOUNT}
)

_AUTHORITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "automatic_reuse_authorized",
        "semantic_rebind_authorized",
    }
)


@dataclass(frozen=True)
class Service1OwnerUnitConfirmationEventV1:
    case_id: str
    sheet_ref: str
    column_ref: str
    semantic_role: str
    unit_kind: str
    owner_answer: str
    question_ref: str
    confirmed_by_owner: bool = True
    file_ref: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("invalid unit confirmation schema")
        for name in (
            "case_id",
            "sheet_ref",
            "column_ref",
            "semantic_role",
            "unit_kind",
            "owner_answer",
            "question_ref",
            "timestamp",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if self.unit_kind not in ALLOWED_UNIT_KINDS:
            raise ValueError("unsupported unit_kind")
        if self.confirmed_by_owner is not True:
            raise ValueError("confirmed_by_owner must be True")
        if any(
            getattr(self, name) is not False
            for name in (
                "runtime_authorized",
                "tool_execution_authorized",
                "product_ready",
                "delivery_authorized",
                "diagnosis_generated",
            )
        ):
            raise ValueError("authority flags must remain False")
        provenance = dict(self.provenance or {})
        if set(provenance).intersection(_AUTHORITY_FIELDS):
            raise ValueError("provenance cannot carry authority fields")
        object.__setattr__(self, "provenance", provenance)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["provenance"] = dict(self.provenance)
        return payload


def build_service_1_owner_unit_confirmation_event_v1(
    *,
    case_id: str,
    sheet_ref: str,
    column_ref: str,
    semantic_role: str,
    unit_kind: str,
    owner_answer: str,
    question_ref: str,
    file_ref: str | None = None,
    timestamp: str | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> Service1OwnerUnitConfirmationEventV1:
    kwargs: dict[str, Any] = {
        "case_id": str(case_id or "").strip(),
        "sheet_ref": str(sheet_ref or "").strip(),
        "column_ref": str(column_ref or "").strip(),
        "semantic_role": str(semantic_role or "").strip(),
        "unit_kind": str(unit_kind or "").strip(),
        "owner_answer": str(owner_answer or "").strip(),
        "question_ref": str(question_ref or "").strip(),
        "file_ref": str(file_ref).strip() if file_ref else None,
        "provenance": dict(provenance or {}),
    }
    if timestamp is not None:
        kwargs["timestamp"] = str(timestamp).strip()
    return Service1OwnerUnitConfirmationEventV1(**kwargs)


__all__ = [
    "SCHEMA_VERSION",
    "UNIT_DISCOUNT_FRACTION",
    "UNIT_DISCOUNT_PERCENT",
    "UNIT_DISCOUNT_LINE_AMOUNT",
    "ALLOWED_UNIT_KINDS",
    "Service1OwnerUnitConfirmationEventV1",
    "build_service_1_owner_unit_confirmation_event_v1",
]
