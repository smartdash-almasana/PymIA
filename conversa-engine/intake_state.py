from __future__ import annotations

from dataclasses import dataclass, field

from inbound_event import RawInboundEvent


@dataclass
class DocumentIntakeState:
    received_events: list[str] = field(default_factory=list)
    received_files: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)

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

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "received_events": list(self.received_events),
            "received_files": list(self.received_files),
            "missing_evidence": list(self.missing_evidence),
        }

    @classmethod
    def from_dict(cls, data: dict[str, list[str]] | None) -> "DocumentIntakeState":
        payload = data or {}
        return cls(
            received_events=list(payload.get("received_events", [])),
            received_files=list(payload.get("received_files", [])),
            missing_evidence=list(payload.get("missing_evidence", [])),
        )
