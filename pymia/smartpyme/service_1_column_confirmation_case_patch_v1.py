from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_confirmation_applier_v1 import (
    Service1ColumnConfirmationApplierResultV1,
)

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_CASE_PATCH_V1"
SERVICE_NAME = "SERVICE_1"
OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED = "DECLARED_NOT_VALIDATED"


class Service1ColumnConfirmationCasePatchKindV1(str, Enum):
    CONFIRM_COMPUTATIONAL = "CONFIRM_COMPUTATIONAL"
    CONFIRM_INFORMATIONAL = "CONFIRM_INFORMATIONAL"
    IGNORE_NOT_RELEVANT = "IGNORE_NOT_RELEVANT"
    BLOCK_REJECTED = "BLOCK_REJECTED"
    KEEP_PENDING = "KEEP_PENDING"


@dataclass(frozen=True)
class Service1ColumnConfirmationCasePatchV1:
    schema_version: str
    service_name: str
    case_id: str
    tenant_id: str
    intake_id: str
    target_ref: str
    parsed_target_ref: dict[str, str]
    patch_kind: Service1ColumnConfirmationCasePatchKindV1
    confirmation_status_before: str
    confirmation_status_after: str
    computation_unlocked: bool
    variables_affected: list[str]
    applied_entry_snapshot: ColumnConfirmationEntry
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    owner_answer_validation_status: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["patch_kind"] = self.patch_kind.value
        data["applied_entry_snapshot"] = self.applied_entry_snapshot.model_dump()
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def derive_service_1_column_confirmation_case_patch_kind_v1(
    *,
    applied_entry_snapshot: ColumnConfirmationEntry,
    computation_unlocked: bool,
) -> Service1ColumnConfirmationCasePatchKindV1:
    status = applied_entry_snapshot.confirmation_status
    if status == ConfirmationStatus.CONFIRMED:
        if computation_unlocked:
            return Service1ColumnConfirmationCasePatchKindV1.CONFIRM_COMPUTATIONAL
        return Service1ColumnConfirmationCasePatchKindV1.CONFIRM_INFORMATIONAL
    if status == ConfirmationStatus.IGNORED_NOT_RELEVANT:
        return Service1ColumnConfirmationCasePatchKindV1.IGNORE_NOT_RELEVANT
    if status == ConfirmationStatus.BLOCKED_AMBIGUOUS:
        return Service1ColumnConfirmationCasePatchKindV1.BLOCK_REJECTED
    if status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION:
        return Service1ColumnConfirmationCasePatchKindV1.KEEP_PENDING
    raise ValueError(f"Unsupported confirmation status for case patch: {status}")


def build_service_1_column_confirmation_case_patch_v1(
    *,
    applier_result: Service1ColumnConfirmationApplierResultV1,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationCasePatchV1:
    if not isinstance(applier_result, Service1ColumnConfirmationApplierResultV1):
        raise ValueError("applier_result must be a Service1ColumnConfirmationApplierResultV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    patch_kind = derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=applier_result.applied_entry_snapshot,
        computation_unlocked=applier_result.computation_unlocked,
    )

    return Service1ColumnConfirmationCasePatchV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=applier_result.case_id,
        tenant_id=applier_result.tenant_id,
        intake_id=applier_result.intake_id,
        target_ref=applier_result.target_ref,
        parsed_target_ref=dict(applier_result.parsed_target_ref),
        patch_kind=patch_kind,
        confirmation_status_before=applier_result.matrix_status_before,
        confirmation_status_after=applier_result.matrix_status_after,
        computation_unlocked=applier_result.computation_unlocked,
        variables_affected=list(applier_result.variables_affected),
        applied_entry_snapshot=applier_result.applied_entry_snapshot.model_copy(deep=True),
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        owner_answer_validation_status=OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED",
    "Service1ColumnConfirmationCasePatchKindV1",
    "Service1ColumnConfirmationCasePatchV1",
    "derive_service_1_column_confirmation_case_patch_kind_v1",
    "build_service_1_column_confirmation_case_patch_v1",
]
