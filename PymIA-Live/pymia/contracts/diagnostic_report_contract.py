from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from pymia.contracts.pathology_contract import PathologySeverity


class KernelState(StrEnum):
    BLOCKED = "BLOCKED"
    PARTIAL = "PARTIAL"
    PASS = "PASS"


class DiagnosisStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    DISPROVED = "DISPROVED"


class FindingRecord(BaseModel):
    entity: str
    finding_type: str
    measured_difference: dict[str, Any]
    compared_sources: list[str] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)
    severity: PathologySeverity
    recommendation: str | None = None
    explanation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _requires_traceable_evidence(self) -> "FindingRecord":
        if not self.evidence_used:
            raise ValueError("EVIDENCE_USED_REQUIRED")
        if not self.compared_sources:
            raise ValueError("COMPARED_SOURCES_REQUIRED")
        if not self.measured_difference:
            raise ValueError("MEASURED_DIFFERENCE_REQUIRED")
        return self


class QuantifiedImpact(BaseModel):
    amount: float | None = None
    currency: str | None = None
    percentage: float | None = None
    units: float | None = None
    time_saved: str | None = None
    risk_level: PathologySeverity | None = None

    @model_validator(mode="after")
    def _requires_some_impact(self) -> "QuantifiedImpact":
        if all(
            value is None
            for value in (
                self.amount,
                self.currency,
                self.percentage,
                self.units,
                self.time_saved,
                self.risk_level,
            )
        ):
            raise ValueError("IMPACT_REQUIRED")
        return self


class DiagnosticReport(BaseModel):
    report_id: str
    case_id: str
    cliente_id: str
    hypothesis: str
    diagnosis_status: DiagnosisStatus
    kernel_state: KernelState
    findings: list[FindingRecord] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)
    formulas_used: list[str] = Field(default_factory=list)
    quantified_impact: QuantifiedImpact | None = None
    reasoning_summary: str
    references_used: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None

    @model_validator(mode="after")
    def _confirmed_requires_traceable_findings(self) -> "DiagnosticReport":
        if self.diagnosis_status == DiagnosisStatus.CONFIRMED:
            if self.kernel_state != KernelState.PASS:
                raise ValueError("CONFIRMED_REQUIRES_PASS")
            if not self.findings:
                raise ValueError("CONFIRMED_REQUIRES_FINDINGS")
            if not self.evidence_used:
                raise ValueError("CONFIRMED_REQUIRES_EVIDENCE")
            if not self.reasoning_summary.strip():
                raise ValueError("CONFIRMED_REQUIRES_REASONING")
        return self
