from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.smartpyme.service_1_evidence_profile_to_candidate_tools_contract_v1 import (
    BLOCKED,
    CANDIDATE_TOOLS_READY,
    NEEDS_EVIDENCE,
    NO_CANDIDATE_TOOLS,
    Service1EvidenceProfileToCandidateToolsResultV1,
    build_service_1_evidence_profile_to_candidate_tools_v1,
)
from pymia.smartpyme.service_1_matrix_application_to_owner_rectified_evidence_profile_bridge_v1 import (
    Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_TO_CANDIDATE_TOOLS_GATE_V1"
SERVICE_NAME = "SERVICE_1"
STATUS_CANDIDATE_TOOLS_READY = "CANDIDATE_TOOLS_READY"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_BLOCKED = "BLOCKED"
STATUS_NO_CANDIDATE_TOOLS = "NO_CANDIDATE_TOOLS"


@dataclass(frozen=True)
class Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateSummaryV1:
    evidence_profile_status: str
    evidence_ready: bool
    evidence_source_columns_count: int
    evidence_ready_signals_count: int
    candidate_tools_status: str
    candidate_tools_count: int
    missing_requirements_count: int
    blockers_count: int
    candidate_tool_refs: tuple[str, ...]
    phase_closed_without_execution: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateResultV1:
    schema_version: str
    service_name: str
    status: str
    source_file_name: str
    candidate_tools_result: Service1EvidenceProfileToCandidateToolsResultV1
    summary: Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateSummaryV1
    runtime_authorized: bool
    tool_execution_authorized: bool
    executable_tool_requests_authorized: bool
    autonomous_delivery_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "status": self.status,
            "source_file_name": self.source_file_name,
            "candidate_tools_result": self.candidate_tools_result.to_dict(),
            "summary": self.summary.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "executable_tool_requests_authorized": self.executable_tool_requests_authorized,
            "autonomous_delivery_authorized": self.autonomous_delivery_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1(
    *,
    evidence_profile_bridge_result: Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1,
    allowed_tool_refs: tuple[str, ...] | list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateResultV1:
    """Gate owner-rectified evidence into candidate tools without execution.

    This bridge reuses build_service_1_evidence_profile_to_candidate_tools_v1(...).
    It does not execute tools, create executable tool requests, call runtime,
    produce delivery, or generate diagnostics.
    """
    if not isinstance(
        evidence_profile_bridge_result,
        Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1,
    ):
        raise ValueError(
            "evidence_profile_bridge_result must be a Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1"
        )
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    gate_metadata = dict(metadata or evidence_profile_bridge_result.metadata)
    candidate_tools_result = build_service_1_evidence_profile_to_candidate_tools_v1(
        evidence_profile=evidence_profile_bridge_result.evidence_profile,
        allowed_tool_refs=allowed_tool_refs,
        metadata=gate_metadata,
    )
    summary = _summarize(
        evidence_profile_bridge_result=evidence_profile_bridge_result,
        candidate_tools_result=candidate_tools_result,
    )

    return Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=_normalize_status(candidate_tools_result.status),
        source_file_name=candidate_tools_result.source_file_name,
        candidate_tools_result=candidate_tools_result,
        summary=summary,
        runtime_authorized=False,
        tool_execution_authorized=False,
        executable_tool_requests_authorized=False,
        autonomous_delivery_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=gate_metadata,
    )


def _summarize(
    *,
    evidence_profile_bridge_result: Service1MatrixApplicationToOwnerRectifiedEvidenceProfileBridgeResultV1,
    candidate_tools_result: Service1EvidenceProfileToCandidateToolsResultV1,
) -> Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateSummaryV1:
    return Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateSummaryV1(
        evidence_profile_status=evidence_profile_bridge_result.status,
        evidence_ready=evidence_profile_bridge_result.evidence_profile.evidence_ready,
        evidence_source_columns_count=len(evidence_profile_bridge_result.evidence_profile.source_columns),
        evidence_ready_signals_count=evidence_profile_bridge_result.summary.evidence_ready_signals_count,
        candidate_tools_status=candidate_tools_result.status,
        candidate_tools_count=len(candidate_tools_result.candidate_tools),
        missing_requirements_count=len(candidate_tools_result.missing_requirements),
        blockers_count=len(candidate_tools_result.blockers),
        candidate_tool_refs=candidate_tools_result.candidate_tool_refs,
        phase_closed_without_execution=True,
    )


def _normalize_status(candidate_tools_status: str) -> str:
    if candidate_tools_status == CANDIDATE_TOOLS_READY:
        return STATUS_CANDIDATE_TOOLS_READY
    if candidate_tools_status == NEEDS_EVIDENCE:
        return STATUS_NEEDS_EVIDENCE
    if candidate_tools_status == BLOCKED:
        return STATUS_BLOCKED
    if candidate_tools_status == NO_CANDIDATE_TOOLS:
        return STATUS_NO_CANDIDATE_TOOLS
    return STATUS_BLOCKED


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_CANDIDATE_TOOLS_READY",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_BLOCKED",
    "STATUS_NO_CANDIDATE_TOOLS",
    "Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateSummaryV1",
    "Service1OwnerRectifiedEvidenceProfileToCandidateToolsGateResultV1",
    "build_service_1_owner_rectified_evidence_profile_to_candidate_tools_gate_v1",
]
