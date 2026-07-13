from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.smartpyme.service_1_owner_answers_to_column_confirmation_matrix_application_v1 import (
    Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    Service1OwnerRectifiedEvidenceProfileResultV1,
    build_service_1_owner_rectified_evidence_profile_v1,
)

SCHEMA_VERSION = "SERVICE_1_MATRIX_APPLICATION_TO_OWNER_RECTIFIED_EVIDENCE_PROFILE_BRIDGE_V1"
SERVICE_NAME = "SERVICE_1"
STATUS_EVIDENCE_PROFILE_READY = "EVIDENCE_PROFILE_READY"
STATUS_EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE = "EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE"
STATUS_EVIDENCE_PROFILE_BLOCKED = "EVIDENCE_PROFILE_BLOCKED"


@dataclass(frozen=True)
class Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1:
    source_matrix_status: str
    source_total_entries: int
    source_confirmed_count: int
    source_blocked_count: int
    source_pending_count: int
    source_ignored_count: int
    source_owner_rectified_functions_count: int
    evidence_source_columns_count: int
    evidence_signals_count: int
    evidence_ready_signals_count: int
    missing_requirements_count: int
    blockers_count: int
    evidence_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1:
    schema_version: str
    service_name: str
    status: str
    source_file_name: str
    evidence_profile: Service1OwnerRectifiedEvidenceProfileResultV1
    summary: Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    candidate_tools_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "status": self.status,
            "source_file_name": self.source_file_name,
            "evidence_profile": self.evidence_profile.to_dict(),
            "summary": self.summary.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "candidate_tools_generated": self.candidate_tools_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1(
    *,
    matrix_application_result: Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1,
    case_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1:
    """Build an owner-rectified evidence profile from a matrix application result.

    This bridge is intentionally thin. It reuses
    build_service_1_owner_rectified_evidence_profile_v1(...) and does not create
    candidate tools, executable requests, diagnostics, runtime authorization, or
    deliveries.
    """
    if not isinstance(
        matrix_application_result,
        Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1,
    ):
        raise ValueError(
            "matrix_application_result must be a Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1"
        )
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    bridge_metadata = dict(metadata or matrix_application_result.metadata)
    evidence_profile = build_service_1_owner_rectified_evidence_profile_v1(
        matrix=matrix_application_result.updated_matrix,
        case_ref=case_ref,
        metadata=bridge_metadata,
    )
    summary = _summarize(
        matrix_application_result=matrix_application_result,
        evidence_profile=evidence_profile,
    )

    return Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=_resolve_status(summary=summary),
        source_file_name=matrix_application_result.source_file_name,
        evidence_profile=evidence_profile,
        summary=summary,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        candidate_tools_generated=False,
        metadata=bridge_metadata,
    )


def _summarize(
    *,
    matrix_application_result: Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1,
    evidence_profile: Service1OwnerRectifiedEvidenceProfileResultV1,
) -> Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1:
    source_summary = matrix_application_result.summary
    ready_signals_count = sum(1 for signal in evidence_profile.evidence_signals if signal.evidence_ready)
    return Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1(
        source_matrix_status=source_summary.matrix_status,
        source_total_entries=source_summary.total_entries,
        source_confirmed_count=source_summary.confirmed_count,
        source_blocked_count=source_summary.blocked_count,
        source_pending_count=source_summary.pending_count,
        source_ignored_count=source_summary.ignored_count,
        source_owner_rectified_functions_count=source_summary.owner_rectified_functions_count,
        evidence_source_columns_count=len(evidence_profile.source_columns),
        evidence_signals_count=len(evidence_profile.evidence_signals),
        evidence_ready_signals_count=ready_signals_count,
        missing_requirements_count=len(evidence_profile.missing_requirements),
        blockers_count=len(evidence_profile.blockers),
        evidence_ready=evidence_profile.evidence_ready,
    )


def _resolve_status(
    *,
    summary: Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1,
) -> str:
    if summary.blockers_count > 0:
        return STATUS_EVIDENCE_PROFILE_BLOCKED
    if summary.evidence_ready:
        return STATUS_EVIDENCE_PROFILE_READY
    return STATUS_EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_EVIDENCE_PROFILE_READY",
    "STATUS_EVIDENCE_PROFILE_NEEDS_MORE_EVIDENCE",
    "STATUS_EVIDENCE_PROFILE_BLOCKED",
    "Service1MatrixApplicationToOwnerRectifiedEvidenceProfileSummaryV1",
    "Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1",
    "build_service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1",
]
