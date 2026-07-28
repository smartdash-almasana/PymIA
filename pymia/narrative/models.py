from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    id: str
    source: str
    metric: str
    value: Any
    context: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class NarrativeClaim(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)
    expected_metric: str | None = None
    expected_value: float | None = None


class NarrativeSection(BaseModel):
    title: str
    claims: list[NarrativeClaim] = Field(default_factory=list)


class NarrativeReport(BaseModel):
    sections: list[NarrativeSection] = Field(default_factory=list)
    trace: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)
