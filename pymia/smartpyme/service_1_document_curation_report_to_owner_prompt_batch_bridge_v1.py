from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    Service1ColumnConfirmationOwnerPromptBatchV1,
    build_service_1_column_confirmation_owner_prompt_batch_v1,
)
from pymia.smartpyme.excel_lab_ingestion_v1 import DocumentCurationReport

SCHEMA_VERSION = "SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1"
SERVICE_NAME = "SERVICE_1"
MISSING_MATRIX = "COLUMN_CONFIRMATION_MATRIX_MISSING"
FILE_NAME_MISMATCH = "COLUMN_CONFIRMATION_MATRIX_FILE_NAME_MISMATCH"


@dataclass(frozen=True)
class Service1DocumentCurationReportToOwnerPromptBatchBridgeV1:
    schema_version: str
    service_name: str
    file_name: str
    report_status: str
    has_column_confirmation_matrix: bool
    owner_prompt_batch: Service1ColumnConfirmationOwnerPromptBatchV1 | None
    prompts_count: int
    has_prompts: bool
    blocked_reason: str | None
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    persistence_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["owner_prompt_batch"] = (
            self.owner_prompt_batch.to_dict() if self.owner_prompt_batch is not None else None
        )
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_result(
    *,
    report: DocumentCurationReport,
    blocked_reason: str,
    metadata: dict[str, Any],
    has_matrix: bool,
) -> Service1DocumentCurationReportToOwnerPromptBatchBridgeV1:
    return Service1DocumentCurationReportToOwnerPromptBatchBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=report.file_name,
        report_status=report.status,
        has_column_confirmation_matrix=has_matrix,
        owner_prompt_batch=None,
        prompts_count=0,
        has_prompts=False,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=metadata,
    )


def build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1(
    *,
    report: DocumentCurationReport,
    metadata: dict[str, Any] | None = None,
) -> Service1DocumentCurationReportToOwnerPromptBatchBridgeV1:
    if not isinstance(report, DocumentCurationReport):
        raise ValueError("report must be a DocumentCurationReport")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    bridge_metadata = dict(metadata or {})
    matrix = report.column_confirmation_matrix
    if matrix is None:
        return _blocked_result(
            report=report,
            blocked_reason=MISSING_MATRIX,
            metadata=bridge_metadata,
            has_matrix=False,
        )

    if matrix.file_name != report.file_name:
        return _blocked_result(
            report=report,
            blocked_reason=FILE_NAME_MISMATCH,
            metadata=bridge_metadata,
            has_matrix=True,
        )

    owner_prompt_batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=matrix,
        metadata=bridge_metadata,
    )
    return Service1DocumentCurationReportToOwnerPromptBatchBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=report.file_name,
        report_status=report.status,
        has_column_confirmation_matrix=True,
        owner_prompt_batch=owner_prompt_batch,
        prompts_count=owner_prompt_batch.actionable_entries_count,
        has_prompts=owner_prompt_batch.has_prompts,
        blocked_reason=None,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=_now_iso(),
        metadata=bridge_metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "MISSING_MATRIX",
    "FILE_NAME_MISMATCH",
    "Service1DocumentCurationReportToOwnerPromptBatchBridgeV1",
    "build_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1",
]
