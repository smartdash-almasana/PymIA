from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal

ReceptionStatus = Literal[
    "RECEIVED",
    "CLASSIFIED",
    "NEEDS_EVIDENCE",
    "READY_TO_PROCESS",
    "PROCESSING",
    "DELIVERED",
    "BLOCKED",
    "UNSUPPORTED",
]


@dataclass(frozen=True)
class ReceptionRecord:
    tenant_id: str
    message: str
    classification: str
    status: ReceptionStatus
    evidence_refs: list[str]
    output_refs: list[str]
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_reception(
    *,
    tenant_id: str,
    message: str,
    classification: str,
    status: ReceptionStatus = "RECEIVED",
    evidence_refs: list[str] | None = None,
    output_refs: list[str] | None = None,
) -> ReceptionRecord:
    if not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if not message.strip():
        raise ValueError("message is required")
    if not classification.strip():
        raise ValueError("classification is required")
    return ReceptionRecord(
        tenant_id=tenant_id,
        message=message,
        classification=classification,
        status=status,
        evidence_refs=evidence_refs or [],
        output_refs=output_refs or [],
        created_at=utc_now_iso(),
    )
