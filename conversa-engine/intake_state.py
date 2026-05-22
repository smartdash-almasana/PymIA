from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from inbound_event import RawInboundEvent


@dataclass
class DocumentIntakeState:
    received_events: list[str] = field(default_factory=list)
    received_files: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    last_file_name: str | None = None
    last_lifecycle_state: str | None = None
    last_parse_status: str | None = None
    last_parse_error: str | None = None
    last_root_cause: str | None = None
    last_user_message: str | None = None

    def register(self, event: RawInboundEvent) -> None:
        self.received_events.append(event.event_id)
        if event.file_extension:
            self.received_files.append(event.payload)

    def require_evidence(self, evidence_key: str) -> None:
        if evidence_key not in self.missing_evidence:
            self.missing_evidence.append(evidence_key)

    def resolve_evidence(self, evidence_key: str) -> None:
        if evidence_key in self.missing_evidence:
            self.missing_evidence.remove(evidence_key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "received_events": list(self.received_events),
            "received_files": list(self.received_files),
            "missing_evidence": list(self.missing_evidence),
            "last_file_name": self.last_file_name,
            "last_lifecycle_state": self.last_lifecycle_state,
            "last_parse_status": self.last_parse_status,
            "last_parse_error": self.last_parse_error,
            "last_root_cause": self.last_root_cause,
            "last_user_message": self.last_user_message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DocumentIntakeState":
        payload = data or {}
        return cls(
            received_events=list(payload.get("received_events", [])),
            received_files=list(payload.get("received_files", [])),
            missing_evidence=list(payload.get("missing_evidence", [])),
            last_file_name=payload.get("last_file_name"),
            last_lifecycle_state=payload.get("last_lifecycle_state"),
            last_parse_status=payload.get("last_parse_status"),
            last_parse_error=payload.get("last_parse_error"),
            last_root_cause=payload.get("last_root_cause"),
            last_user_message=payload.get("last_user_message"),
        )
