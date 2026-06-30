"""Pure evidence packet contract for Phase I first controlled client case.

This module does not execute runtime work. It only transforms a valid readiness
gate result plus governed references into a controlled-case evidence packet
candidate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypedDict


SCHEMA_VERSION = "S1_FIRST_CONTROLLED_CLIENT_CASE_EVIDENCE_PACKET_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_KIND = "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"
READINESS_GATE_KIND = "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"
READINESS_READY_STATUS = "CONTROLLED_CASE_READY"

_DANGEROUS_FLAGS = (
    "runtime_authorized",
    "publish_executed",
    "notification_sent",
    "handoff_executed",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "mutation_authorized",
    "llm_authorized",
)

EvidencePacketStatusV1 = Literal[
    "EVIDENCE_PACKET_READY",
    "BLOCKED_INVALID_READINESS_GATE",
    "BLOCKED_MISSING_OWNER",
    "BLOCKED_MISSING_TENANT",
    "BLOCKED_MISSING_CASE",
    "BLOCKED_MISSING_EVIDENCE_REFS",
    "BLOCKED_MISSING_FILE_REFS",
    "BLOCKED_MISSING_SCOPE",
    "BLOCKED_MISSING_OWNER_CONSENT",
    "BLOCKED_MISSING_OPERATOR_OVERSIGHT",
    "BLOCKED_MISSING_ROLLBACK",
    "BLOCKED_UNSAFE_RUNTIME_FLAGS",
    "UNKNOWN",
]


class FirstControlledClientCaseEvidencePacketCandidateV1(TypedDict):
    candidate_kind: Literal["CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"]
    packet_ref: str
    status: Literal["EVIDENCE_PACKET_READY"]
    ready: Literal[True]
    service_name: Literal["SERVICE_1"]
    source_gate_kind: Literal["FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"]
    source_gate_status: str
    owner_ref: str
    tenant_ref: str
    case_ref: str
    evidence_refs: list[str]
    file_refs: list[str]
    scope: str
    owner_consent_ref: str
    operator_oversight_ref: str
    rollback_plan_ref: str
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW"]
    warnings: list[str]
    errors: list[str]
    runtime_authorized: Literal[False]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


class FirstControlledClientCaseEvidencePacketResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: EvidencePacketStatusV1
    controlled_case_evidence_packet_candidate: FirstControlledClientCaseEvidencePacketCandidateV1 | None
    blocked_reason: str | None
    allowed_execution_mode: Literal["SUPERVISED_CLI_OPERATOR_FLOW", "NONE"]
    warnings: list[str]
    errors: list[str]
    runtime_authorized: Literal[False]
    publish_executed: Literal[False]
    notification_sent: Literal[False]
    handoff_executed: Literal[False]
    api_exposed: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    mutation_authorized: Literal[False]
    llm_authorized: Literal[False]


def build_service_1_first_controlled_client_case_evidence_packet_v1(
    *,
    readiness_gate_result: Mapping[str, Any] | None,
    owner_ref: str,
    tenant_ref: str,
    case_ref: str,
    evidence_refs: list[str] | object,
    file_refs: list[str] | object,
    scope: str,
    owner_consent_ref: str,
    operator_oversight_ref: str,
    rollback_plan_ref: str,
) -> FirstControlledClientCaseEvidencePacketResultV1:
    """Build a pure controlled-case evidence packet candidate for Phase I."""

    if not isinstance(readiness_gate_result, Mapping):
        return _blocked(
            "BLOCKED_INVALID_READINESS_GATE",
            "readiness_gate_result must be a mapping",
        )

    gate_snapshot = deepcopy(dict(readiness_gate_result))
    unsafe_flags = [flag for flag in _DANGEROUS_FLAGS if readiness_gate_result.get(flag) is True]
    if unsafe_flags:
        return _blocked(
            "BLOCKED_UNSAFE_RUNTIME_FLAGS",
            "; ".join(f"unsafe flag is true: {flag}" for flag in unsafe_flags),
        )

    if readiness_gate_result.get("gate_kind") != READINESS_GATE_KIND:
        return _blocked(
            "BLOCKED_INVALID_READINESS_GATE",
            "readiness_gate_result.gate_kind must be FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE",
        )

    readiness_status = readiness_gate_result.get("status")
    readiness_ready = readiness_gate_result.get("ready") is True
    if readiness_status == "UNKNOWN":
        return _blocked("UNKNOWN", "readiness_gate_result status is UNKNOWN")

    if readiness_status != READINESS_READY_STATUS or not readiness_ready:
        return _blocked(
            "BLOCKED_INVALID_READINESS_GATE",
            "readiness_gate_result must be CONTROLLED_CASE_READY and ready=True",
        )

    if readiness_gate_result.get("allowed_execution_mode") != "SUPERVISED_CLI_OPERATOR_FLOW":
        return _blocked(
            "BLOCKED_INVALID_READINESS_GATE",
            "readiness_gate_result.allowed_execution_mode must be SUPERVISED_CLI_OPERATOR_FLOW",
        )

    if not _has_text(owner_ref):
        return _blocked("BLOCKED_MISSING_OWNER", "owner_ref is required")
    if not _has_text(tenant_ref):
        return _blocked("BLOCKED_MISSING_TENANT", "tenant_ref is required")
    if not _has_text(case_ref):
        return _blocked("BLOCKED_MISSING_CASE", "case_ref is required")

    cleaned_evidence_refs = _clean_refs(evidence_refs)
    if not cleaned_evidence_refs:
        return _blocked("BLOCKED_MISSING_EVIDENCE_REFS", "at least one evidence_ref is required")

    cleaned_file_refs = _clean_refs(file_refs)
    if not cleaned_file_refs:
        return _blocked("BLOCKED_MISSING_FILE_REFS", "at least one file_ref is required")

    if not _has_text(scope):
        return _blocked("BLOCKED_MISSING_SCOPE", "scope is required")
    if not _has_text(owner_consent_ref):
        return _blocked("BLOCKED_MISSING_OWNER_CONSENT", "owner_consent_ref is required")
    if not _has_text(operator_oversight_ref):
        return _blocked("BLOCKED_MISSING_OPERATOR_OVERSIGHT", "operator_oversight_ref is required")
    if not _has_text(rollback_plan_ref):
        return _blocked("BLOCKED_MISSING_ROLLBACK", "rollback_plan_ref is required")

    candidate: FirstControlledClientCaseEvidencePacketCandidateV1 = {
        "candidate_kind": PACKET_KIND,
        "packet_ref": _packet_ref(
            owner_ref=owner_ref.strip(),
            tenant_ref=tenant_ref.strip(),
            case_ref=case_ref.strip(),
        ),
        "status": "EVIDENCE_PACKET_READY",
        "ready": True,
        "service_name": SERVICE_NAME,
        "source_gate_kind": READINESS_GATE_KIND,
        "source_gate_status": str(gate_snapshot["status"]),
        "owner_ref": owner_ref.strip(),
        "tenant_ref": tenant_ref.strip(),
        "case_ref": case_ref.strip(),
        "evidence_refs": cleaned_evidence_refs,
        "file_refs": cleaned_file_refs,
        "scope": scope.strip(),
        "owner_consent_ref": owner_consent_ref.strip(),
        "operator_oversight_ref": operator_oversight_ref.strip(),
        "rollback_plan_ref": rollback_plan_ref.strip(),
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        "warnings": [],
        "errors": [],
        **_safe_flags(),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": "EVIDENCE_PACKET_READY",
        "controlled_case_evidence_packet_candidate": candidate,
        "blocked_reason": None,
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        "warnings": [],
        "errors": [],
        **_safe_flags(),
    }


def _blocked(
    status: EvidencePacketStatusV1,
    blocked_reason: str,
) -> FirstControlledClientCaseEvidencePacketResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "controlled_case_evidence_packet_candidate": None,
        "blocked_reason": blocked_reason,
        "allowed_execution_mode": "NONE",
        "warnings": [],
        "errors": [blocked_reason],
        **_safe_flags(),
    }


def _safe_flags() -> dict[str, Literal[False]]:
    return {flag: False for flag in _DANGEROUS_FLAGS}


def _clean_refs(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if _has_text(value)]


def _packet_ref(*, owner_ref: str, tenant_ref: str, case_ref: str) -> str:
    return f"controlled_case_evidence_packet:{tenant_ref}:{owner_ref}:{case_ref}"


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_KIND",
    "READINESS_GATE_KIND",
    "READINESS_READY_STATUS",
    "FirstControlledClientCaseEvidencePacketCandidateV1",
    "FirstControlledClientCaseEvidencePacketResultV1",
    "build_service_1_first_controlled_client_case_evidence_packet_v1",
]
