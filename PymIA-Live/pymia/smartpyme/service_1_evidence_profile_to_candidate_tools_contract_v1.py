from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    MARGIN_SIGNAL,
    SALES_COLLECTION_SIGNAL,
    STOCK_SIGNAL,
    Service1OwnerRectifiedEvidenceProfileResultV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_EVIDENCE_PROFILE_TO_CANDIDATE_TOOLS_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

CANDIDATE_TOOLS_READY: Final[str] = "CANDIDATE_TOOLS_READY"
NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
BLOCKED: Final[str] = "BLOCKED"
NO_CANDIDATE_TOOLS: Final[str] = "NO_CANDIDATE_TOOLS"

CandidateToolsStatusV1 = Literal[
    "CANDIDATE_TOOLS_READY",
    "NEEDS_EVIDENCE",
    "BLOCKED",
    "NO_CANDIDATE_TOOLS",
]

ALLOWED_CANDIDATE_TOOL_REFS: Final[tuple[str, ...]] = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)

SIGNAL_TO_CANDIDATE_TOOL_REF: Final[dict[str, str]] = {
    MARGIN_SIGNAL: "precio_margen_basico",
    STOCK_SIGNAL: "stock_alertas_basicas",
    SALES_COLLECTION_SIGNAL: "caja_diaria_triage",
}

LIMITATIONS_BY_TOOL_REF: Final[dict[str, tuple[str, ...]]] = {
    "precio_margen_basico": (
        "Candidate only: does not compute final margin, price, tax effect, or profitability.",
    ),
    "stock_alertas_basicas": (
        "Candidate only: does not confirm physical stock, stock cause, or replenishment decision.",
    ),
    "caja_diaria_triage": (
        "Candidate only: does not certify bank balance, cash balance, or reconciliation result.",
    ),
    "gastos_triage": (
        "Candidate only: not mapped from V1 evidence profile signals yet.",
    ),
    "proveedores_precio_variacion_triage": (
        "Candidate only: not mapped from V1 evidence profile signals yet.",
    ),
}


@dataclass(frozen=True)
class Service1CandidateToolV1:
    tool_ref: str
    source_signal_name: str
    source_headers: tuple[str, ...]
    present_functions: tuple[str, ...]
    reason: str
    limitations: tuple[str, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    executable_tool_request_authorized: bool


@dataclass(frozen=True)
class Service1EvidenceProfileToCandidateToolsResultV1:
    schema_version: str
    service_name: str
    case_ref: str
    source_file_name: str
    status: CandidateToolsStatusV1
    candidate_tools: tuple[Service1CandidateToolV1, ...]
    candidate_tool_refs: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    blockers: tuple[str, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    executable_tool_requests_authorized: bool
    autonomous_delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_evidence_profile_to_candidate_tools_v1(
    *,
    evidence_profile: Service1OwnerRectifiedEvidenceProfileResultV1,
    allowed_tool_refs: tuple[str, ...] | list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1EvidenceProfileToCandidateToolsResultV1:
    """Build governed candidate tools from an owner-rectified evidence profile.

    This contract is pure. It does not execute tools, create executable tool
    requests, call pipelines, read files, write files, authorize runtime, or
    deliver outputs.
    """
    if not isinstance(evidence_profile, Service1OwnerRectifiedEvidenceProfileResultV1):
        raise ValueError("evidence_profile must be a Service1OwnerRectifiedEvidenceProfileResultV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    explicit_allowlist = _normalize_allowed_tool_refs(allowed_tool_refs)
    blockers = list(evidence_profile.blockers)

    if evidence_profile.runtime_authorized:
        blockers.append("UPSTREAM_RUNTIME_AUTHORIZED_UNEXPECTED")
    if evidence_profile.tool_execution_authorized:
        blockers.append("UPSTREAM_TOOL_EXECUTION_AUTHORIZED_UNEXPECTED")

    if blockers:
        return _result(
            evidence_profile=evidence_profile,
            status=BLOCKED,
            candidate_tools=(),
            missing_requirements=evidence_profile.missing_requirements,
            blockers=tuple(sorted(dict.fromkeys(blockers))),
            metadata=metadata,
        )

    if not evidence_profile.evidence_ready:
        return _result(
            evidence_profile=evidence_profile,
            status=NEEDS_EVIDENCE,
            candidate_tools=(),
            missing_requirements=evidence_profile.missing_requirements,
            blockers=(),
            metadata=metadata,
        )

    candidates: list[Service1CandidateToolV1] = []
    candidate_blockers: list[str] = []

    for signal in evidence_profile.evidence_signals:
        if not signal.evidence_ready:
            continue
        tool_ref = SIGNAL_TO_CANDIDATE_TOOL_REF.get(signal.signal_name)
        if tool_ref is None:
            continue
        if tool_ref not in ALLOWED_CANDIDATE_TOOL_REFS:
            candidate_blockers.append(f"TOOL_REF_NOT_IN_STATIC_ALLOWLIST:{tool_ref}")
            continue
        if explicit_allowlist is not None and tool_ref not in explicit_allowlist:
            candidate_blockers.append(f"TOOL_REF_NOT_IN_EXPLICIT_ALLOWLIST:{tool_ref}")
            continue
        candidates.append(
            Service1CandidateToolV1(
                tool_ref=tool_ref,
                source_signal_name=signal.signal_name,
                source_headers=signal.source_headers,
                present_functions=signal.present_functions,
                reason=f"Evidence signal {signal.signal_name} is ready and maps conservatively to {tool_ref}.",
                limitations=LIMITATIONS_BY_TOOL_REF[tool_ref],
                runtime_authorized=False,
                tool_execution_authorized=False,
                executable_tool_request_authorized=False,
            )
        )

    if candidate_blockers:
        return _result(
            evidence_profile=evidence_profile,
            status=BLOCKED,
            candidate_tools=tuple(sorted(candidates, key=lambda candidate: candidate.tool_ref)),
            missing_requirements=evidence_profile.missing_requirements,
            blockers=tuple(sorted(dict.fromkeys(candidate_blockers))),
            metadata=metadata,
        )

    candidates_tuple = tuple(sorted(candidates, key=lambda candidate: candidate.tool_ref))
    if not candidates_tuple:
        return _result(
            evidence_profile=evidence_profile,
            status=NO_CANDIDATE_TOOLS,
            candidate_tools=(),
            missing_requirements=evidence_profile.missing_requirements,
            blockers=(),
            metadata=metadata,
        )

    return _result(
        evidence_profile=evidence_profile,
        status=CANDIDATE_TOOLS_READY,
        candidate_tools=candidates_tuple,
        missing_requirements=evidence_profile.missing_requirements,
        blockers=(),
        metadata=metadata,
    )


def _normalize_allowed_tool_refs(
    allowed_tool_refs: tuple[str, ...] | list[str] | None,
) -> tuple[str, ...] | None:
    if allowed_tool_refs is None:
        return None
    normalized = tuple(sorted(dict.fromkeys(str(ref).strip() for ref in allowed_tool_refs if str(ref).strip())))
    return normalized


def _result(
    *,
    evidence_profile: Service1OwnerRectifiedEvidenceProfileResultV1,
    status: CandidateToolsStatusV1,
    candidate_tools: tuple[Service1CandidateToolV1, ...],
    missing_requirements: tuple[str, ...],
    blockers: tuple[str, ...],
    metadata: dict[str, Any] | None,
) -> Service1EvidenceProfileToCandidateToolsResultV1:
    return Service1EvidenceProfileToCandidateToolsResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_ref=evidence_profile.case_ref,
        source_file_name=evidence_profile.source_file_name,
        status=status,
        candidate_tools=candidate_tools,
        candidate_tool_refs=tuple(candidate.tool_ref for candidate in candidate_tools),
        missing_requirements=tuple(missing_requirements),
        blockers=tuple(blockers),
        runtime_authorized=False,
        tool_execution_authorized=False,
        executable_tool_requests_authorized=False,
        autonomous_delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "CANDIDATE_TOOLS_READY",
    "NEEDS_EVIDENCE",
    "BLOCKED",
    "NO_CANDIDATE_TOOLS",
    "ALLOWED_CANDIDATE_TOOL_REFS",
    "SIGNAL_TO_CANDIDATE_TOOL_REF",
    "Service1CandidateToolV1",
    "Service1EvidenceProfileToCandidateToolsResultV1",
    "build_service_1_evidence_profile_to_candidate_tools_v1",
]
