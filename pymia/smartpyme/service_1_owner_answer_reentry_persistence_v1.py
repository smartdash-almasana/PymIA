from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymia.smartpyme.owner_answer import OwnerAnswerRecord
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    REENTRY_STATUS_ACCEPTED,
    Service1OwnerAnswerReentryV1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import SERVICE_NAME
from pymia.smartpyme.storage import save_owner_answer_record

SCHEMA_VERSION = "SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1"

PERSISTENCE_STATUS_PERSISTED = "PERSISTED"
PERSISTENCE_STATUS_BLOCKED = "BLOCKED"

PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED = "REENTRY_NOT_ACCEPTED"
PERSISTENCE_BLOCK_OWNER_ANSWER_RECORD_MISSING = "OWNER_ANSWER_RECORD_MISSING"


@dataclass(frozen=True)
class Service1OwnerAnswerReentryPersistenceV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    source_run_id: str
    question_ref: str
    answer_id: str | None
    persisted_path: str | None
    blocked_reason: str | None
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_packet(
    *,
    reentry_packet: Service1OwnerAnswerReentryV1,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1OwnerAnswerReentryPersistenceV1:
    return Service1OwnerAnswerReentryPersistenceV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=PERSISTENCE_STATUS_BLOCKED,
        case_id=reentry_packet.case_id,
        tenant_id=reentry_packet.tenant_id,
        intake_id=reentry_packet.intake_id,
        source_run_id=reentry_packet.source_run_id,
        question_ref=reentry_packet.question_ref,
        answer_id=(
            reentry_packet.owner_answer_record.answer_id
            if reentry_packet.owner_answer_record is not None
            else None
        ),
        persisted_path=None,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def persist_service_1_owner_answer_reentry_v1(
    *,
    reentry_packet: Service1OwnerAnswerReentryV1,
    storage_dir: str | Path,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerAnswerReentryPersistenceV1:
    """Persist an accepted Servicio 1 owner-answer reentry packet.

    This function deliberately persists only the already-created OwnerAnswerRecord.
    It does not recreate the record, re-run the pipeline, recalculate evidence,
    update evidence request status, or apply column confirmation.
    """

    if not isinstance(reentry_packet, Service1OwnerAnswerReentryV1):
        raise ValueError("reentry_packet must be Service1OwnerAnswerReentryV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    if reentry_packet.status != REENTRY_STATUS_ACCEPTED:
        return _blocked_packet(
            reentry_packet=reentry_packet,
            blocked_reason=PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED,
            metadata=metadata,
        )

    owner_answer_record = reentry_packet.owner_answer_record
    if not isinstance(owner_answer_record, OwnerAnswerRecord):
        return _blocked_packet(
            reentry_packet=reentry_packet,
            blocked_reason=PERSISTENCE_BLOCK_OWNER_ANSWER_RECORD_MISSING,
            metadata=metadata,
        )

    persisted_path = save_owner_answer_record(
        reentry_packet.tenant_id,
        owner_answer_record,
        base_dir=Path(storage_dir),
    )

    packet_metadata = {
        "source_reentry_schema_version": reentry_packet.schema_version,
        "owner_answer_validation_status": owner_answer_record.metadata.get(
            "owner_answer_validation_status", "DECLARED_NOT_VALIDATED"
        ),
        "persisted_record_type": "OwnerAnswerRecord",
    }
    packet_metadata.update(dict(metadata or {}))

    return Service1OwnerAnswerReentryPersistenceV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=PERSISTENCE_STATUS_PERSISTED,
        case_id=reentry_packet.case_id,
        tenant_id=reentry_packet.tenant_id,
        intake_id=reentry_packet.intake_id,
        source_run_id=reentry_packet.source_run_id,
        question_ref=reentry_packet.question_ref,
        answer_id=owner_answer_record.answer_id,
        persisted_path=str(persisted_path),
        blocked_reason=None,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=_now_iso(),
        metadata=packet_metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "PERSISTENCE_STATUS_PERSISTED",
    "PERSISTENCE_STATUS_BLOCKED",
    "PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED",
    "PERSISTENCE_BLOCK_OWNER_ANSWER_RECORD_MISSING",
    "Service1OwnerAnswerReentryPersistenceV1",
    "persist_service_1_owner_answer_reentry_v1",
]
