from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from evidence_router import IngestionRoute, route_evidence


class InboundEventType(StrEnum):
    TEXT = "text"
    FILE = "file"


@dataclass(frozen=True)
class RawInboundEvent:
    event_id: str
    tenant_id: str
    user_id: str
    event_type: InboundEventType
    payload: str
    file_extension: str = ""
    mime_type: str = "text/plain"
    expected_schema: str = "human_claim"
    entropy_level: float = 0.0

    @classmethod
    def text(
        cls,
        *,
        event_id: str,
        tenant_id: str,
        user_id: str,
        text: str,
    ) -> Self:
        return cls(
            event_id=event_id,
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=InboundEventType.TEXT,
            payload=text,
            expected_schema="human_claim",
        )

    @classmethod
    def file(
        cls,
        *,
        event_id: str,
        tenant_id: str,
        user_id: str,
        file_name: str,
        mime_type: str,
        expected_schema: str,
        entropy_level: float,
    ) -> Self:
        extension = ""
        if "." in file_name:
            extension = f".{file_name.rsplit('.', 1)[1].lower()}"
        return cls(
            event_id=event_id,
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=InboundEventType.FILE,
            payload=file_name,
            file_extension=extension,
            mime_type=mime_type,
            expected_schema=expected_schema,
            entropy_level=entropy_level,
        )

    def get_ingestion_route(self) -> IngestionRoute:
        if self.event_type == InboundEventType.TEXT:
            return IngestionRoute.NARRATIVE
        return route_evidence(
            evidence_id=self.event_id,
            file_extension=self.file_extension,
            mime_type=self.mime_type,
            expected_schema=self.expected_schema,
            entropy_level=self.entropy_level,
        )

