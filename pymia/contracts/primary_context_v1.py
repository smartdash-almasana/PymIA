from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]
PrimaryState = Literal["pending_data", "ready_for_evidence_intake"]


class PrimaryContextSignal(BaseModel):
    code: str = Field(min_length=2)
    confidence_level: ConfidenceLevel = "low"
    evidence: list[str] = Field(default_factory=list)


class EvidenceGap(BaseModel):
    required_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    optional_evidence: list[str] = Field(default_factory=list)


class PrimaryContextRecord(BaseModel):
    tenant_id: str
    raw_message: str = Field(min_length=1)
    expressed_pain: list[PrimaryContextSignal] = Field(default_factory=list)
    suspected_domains: list[PrimaryContextSignal] = Field(default_factory=list)
    urgency_level: Literal["low", "medium", "high"] = "medium"
    evidence_mentions: list[str] = Field(default_factory=list)
    operational_signals: list[PrimaryContextSignal] = Field(default_factory=list)
    linguistic_signals: list[PrimaryContextSignal] = Field(default_factory=list)
    maturity_hints: list[PrimaryContextSignal] = Field(default_factory=list)
    initial_hypotheses: list[PrimaryContextSignal] = Field(default_factory=list)
    requested_outcome: str = "clarify_operational_state"
    evidence_gap: EvidenceGap = Field(default_factory=EvidenceGap)
    state: PrimaryState = "pending_data"

