from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DiagnosticCoreStatus(StrEnum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    INSUFFICIENT = "INSUFFICIENT"


class CoreDiagnosticStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    NOT_CONFIRMED = "NOT_CONFIRMED"
    INSUFFICIENT = "INSUFFICIENT"
    CANDIDATE = "CANDIDATE"
    BLOCKED = "BLOCKED"


class DiagnosticCoreInput(BaseModel):
    case_id: str
    tenant_id: str
    hypothesis_codes: list[str] = Field(default_factory=list)
    formula_ids: list[str] = Field(default_factory=list)
    variables: dict[str, float | int | None] = Field(default_factory=dict)
    evidence_refs: dict[str, list[str]] = Field(default_factory=dict)
    evidence_status: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CoreFormulaResult(BaseModel):
    formula_id: str
    status: str
    value: float | None = None
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None


class CoreDiagnosticResult(BaseModel):
    pathology_code: str
    status: CoreDiagnosticStatus
    formula_id: str
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)


class CoreFinding(BaseModel):
    finding_id: str
    pathology_code: str
    formula_id: str
    status: str
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)


class DiagnosticCoreResult(BaseModel):
    case_id: str
    tenant_id: str
    status: DiagnosticCoreStatus
    formula_results: list[CoreFormulaResult] = Field(default_factory=list)
    diagnostic_results: list[CoreDiagnosticResult] = Field(default_factory=list)
    findings: list[CoreFinding] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
