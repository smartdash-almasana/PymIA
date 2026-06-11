from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


SupportedSourcePlatform = Literal["mercadolibre", "shopify", "manual_fixture"]
SCHEMA_VERSION = "events_v1"


def canonical_json_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WebhookEvent(BaseModel):
    event_id: str
    tenant_id: str
    source_platform: SupportedSourcePlatform
    event_type: str
    occurred_at: str | None = None
    received_at: str = Field(default_factory=utc_now_iso)
    payload_hash: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def normalized_payload_hash(self) -> str:
        return self.payload_hash or canonical_json_hash(self.raw_payload)


class DomainEvent(BaseModel):
    domain_event_id: str
    tenant_id: str
    source_event_id: str
    source_platform: SupportedSourcePlatform
    event_name: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: str
    payload: dict[str, Any] = Field(default_factory=dict)
    payload_hash: str
    idempotency_key: str
    schema_version: str = SCHEMA_VERSION
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReplaySummary(BaseModel):
    received_count: int = 0
    emitted_count: int = 0
    skipped_duplicate_count: int = 0
    skipped_unsupported_count: int = 0
    invalid_count: int = 0
    output_path: str


__all__ = [
    "DomainEvent",
    "ReplaySummary",
    "SCHEMA_VERSION",
    "WebhookEvent",
    "canonical_json_hash",
]
