"""Minimal runtime bridge for SmartPyme.

Transforms an AnalysisReadinessResult (or dict) into a RuntimeExecutionCandidate
that is safe to dispatch in a later slice.

This module does NOT execute runtime code and does NOT import analysis modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .readiness import (
    ALLOWED_RUNTIME_CLASSIFICATIONS,
    AnalysisReadinessResult,
    READINESS_READY_FOR_ANALYSIS,
)

EXECUTION_READY_TO_EXECUTE = "READY_TO_EXECUTE"
EXECUTION_BLOCKED = "BLOCKED"
EXECUTION_UNSUPPORTED = "UNSUPPORTED"

ALLOWED_EXECUTION_STATUSES: tuple[str, ...] = (
    EXECUTION_READY_TO_EXECUTE,
    EXECUTION_BLOCKED,
    EXECUTION_UNSUPPORTED,
)

MICROSERVICE_MAP: dict[str, str] = {
    "excel_diagnostic": "excel_diagnostic_worker",
    "supplier_duplicate_check": "supplier_duplicate_check_worker",
}

ALLOWED_MICROSERVICE_NAMES: tuple[str, ...] = tuple(sorted(MICROSERVICE_MAP.values()))


@dataclass
class RuntimeExecutionCandidate:
    tenant_id: str
    intake_id: str
    runtime_classification: str
    microservice_name: str
    evidence_ids: list[str] = field(default_factory=list)
    status: str = EXECUTION_BLOCKED
    can_dispatch: bool = False
    blocking_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    audit_notes: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "intake_id": self.intake_id,
            "runtime_classification": self.runtime_classification,
            "microservice_name": self.microservice_name,
            "evidence_ids": list(self.evidence_ids),
            "status": self.status,
            "can_dispatch": self.can_dispatch,
            "blocking_reasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "audit_notes": list(self.audit_notes),
            "created_at": self.created_at,
        }


def _as_dict(readiness_result: Any) -> dict:
    if isinstance(readiness_result, dict):
        return dict(readiness_result)
    if isinstance(readiness_result, AnalysisReadinessResult):
        return readiness_result.to_dict()
    if hasattr(readiness_result, "to_dict") and callable(readiness_result.to_dict):
        result = readiness_result.to_dict()
        if not isinstance(result, dict):
            raise ValueError("readiness_result.to_dict() must return dict")
        return dict(result)
    raise ValueError("readiness_result must be dict or AnalysisReadinessResult")


def _require_non_empty(data: dict, key: str) -> str:
    value = data.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"readiness_result is missing required field: {key}")
    return str(value)


def _optional_str(data: dict, key: str) -> str:
    value = data.get(key)
    if value is None or str(value).strip() == "":
        return ""
    return str(value)


def prepare_runtime_execution(
    readiness_result: AnalysisReadinessResult | dict,
) -> RuntimeExecutionCandidate:
    """Translate readiness output into a future dispatch candidate.

    Rules:
    - status != READY_FOR_ANALYSIS -> BLOCKED
    - can_execute == False -> BLOCKED
    - missing classification while ready -> BLOCKED
    - runtime_classification unsupported -> UNSUPPORTED
    - else -> READY_TO_EXECUTE
    """
    rr = _as_dict(readiness_result)

    tenant_id = _require_non_empty(rr, "tenant_id")
    intake_id = _require_non_empty(rr, "intake_id")

    if "status" not in rr:
        raise ValueError("readiness_result is missing required field: status")
    status = str(rr["status"])

    if "can_execute" not in rr:
        raise ValueError("readiness_result is missing required field: can_execute")
    can_execute = bool(rr["can_execute"])

    runtime_classification = _optional_str(rr, "runtime_classification")

    evidence_ids = [str(x) for x in (rr.get("matched_evidence_ids") or [])]
    warnings = [str(x) for x in (rr.get("warnings") or [])]
    audit_notes = [str(x) for x in (rr.get("audit_notes") or [])]
    blocking_reasons = [str(x) for x in (rr.get("blocking_reasons") or [])]

    if status != READINESS_READY_FOR_ANALYSIS:
        if not blocking_reasons:
            blocking_reasons.append(
                f"Readiness status {status!r} is not READY_FOR_ANALYSIS."
            )
        return RuntimeExecutionCandidate(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name="",
            evidence_ids=evidence_ids,
            status=EXECUTION_BLOCKED,
            can_dispatch=False,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            audit_notes=audit_notes,
        )

    if not can_execute:
        if not blocking_reasons:
            blocking_reasons.append("Readiness can_execute is False.")
        return RuntimeExecutionCandidate(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name="",
            evidence_ids=evidence_ids,
            status=EXECUTION_BLOCKED,
            can_dispatch=False,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            audit_notes=audit_notes,
        )

    if not runtime_classification:
        blocking_reasons = list(blocking_reasons)
        blocking_reasons.append("Missing runtime_classification for ready analysis.")
        return RuntimeExecutionCandidate(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification="",
            microservice_name="",
            evidence_ids=evidence_ids,
            status=EXECUTION_BLOCKED,
            can_dispatch=False,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            audit_notes=audit_notes,
        )

    if runtime_classification not in ALLOWED_RUNTIME_CLASSIFICATIONS:
        blocking_reasons = list(blocking_reasons)
        blocking_reasons.append(
            f"Unsupported runtime_classification: {runtime_classification!r}."
        )
        return RuntimeExecutionCandidate(
            tenant_id=tenant_id,
            intake_id=intake_id,
            runtime_classification=runtime_classification,
            microservice_name="",
            evidence_ids=evidence_ids,
            status=EXECUTION_UNSUPPORTED,
            can_dispatch=False,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            audit_notes=audit_notes,
        )

    return RuntimeExecutionCandidate(
        tenant_id=tenant_id,
        intake_id=intake_id,
        runtime_classification=runtime_classification,
        microservice_name=MICROSERVICE_MAP[runtime_classification],
        evidence_ids=evidence_ids,
        status=EXECUTION_READY_TO_EXECUTE,
        can_dispatch=True,
        blocking_reasons=blocking_reasons,
        warnings=warnings,
        audit_notes=audit_notes,
    )


__all__ = [
    "RuntimeExecutionCandidate",
    "prepare_runtime_execution",
    "EXECUTION_READY_TO_EXECUTE",
    "EXECUTION_BLOCKED",
    "EXECUTION_UNSUPPORTED",
    "ALLOWED_EXECUTION_STATUSES",
    "MICROSERVICE_MAP",
    "ALLOWED_MICROSERVICE_NAMES",
]
