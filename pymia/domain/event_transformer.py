from __future__ import annotations

import hashlib
from typing import Any

from pymia.contracts.events_v1 import DomainEvent, WebhookEvent, canonical_json_hash

SUPPORTED_EVENT_NAMES = {"order_created", "payment_registered", "refund_registered"}
_EVENT_TO_AGGREGATE = {
    "order_created": "order",
    "payment_registered": "payment",
    "refund_registered": "refund",
}


def is_supported_webhook(event: WebhookEvent) -> bool:
    return event.event_type in SUPPORTED_EVENT_NAMES


def transform_webhook_event(event: WebhookEvent) -> list[DomainEvent]:
    if not is_supported_webhook(event):
        return []
    payload = _normalized_payload(event)
    payload_hash = canonical_json_hash(payload)
    aggregate_type = _EVENT_TO_AGGREGATE[event.event_type]
    aggregate_id = str(payload.get("aggregate_id") or payload.get("id") or event.event_id)
    idempotency_key = _idempotency_key(
        event.tenant_id,
        event.event_type,
        aggregate_type,
        aggregate_id,
        payload_hash,
    )
    domain_event_id = hashlib.sha256(f"{event.source_platform}:{event.event_id}:{idempotency_key}".encode("utf-8")).hexdigest()
    return [
        DomainEvent(
            domain_event_id=domain_event_id,
            tenant_id=event.tenant_id,
            source_event_id=event.event_id,
            source_platform=event.source_platform,
            event_name=event.event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            occurred_at=event.occurred_at or event.received_at,
            payload=payload,
            payload_hash=payload_hash,
            idempotency_key=idempotency_key,
            metadata={"source_payload_hash": event.normalized_payload_hash()},
        )
    ]


def _normalized_payload(event: WebhookEvent) -> dict[str, Any]:
    return dict(event.raw_payload)


def _idempotency_key(
    tenant_id: str,
    event_name: str,
    aggregate_type: str,
    aggregate_id: str,
    payload_hash: str,
) -> str:
    raw = f"{tenant_id}:{event_name}:{aggregate_type}:{aggregate_id}:{payload_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


__all__ = ["SUPPORTED_EVENT_NAMES", "is_supported_webhook", "transform_webhook_event"]
