from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScenarioEvidence:
    evidence_type: str
    source_kind: str
    source_ref: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScenarioExpectation:
    final_status: str
    runtime_classification: str | None = None
    dispatch_status: str | None = None
    min_findings_count: int = 0
    must_not_dispatch: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PipelineScenario:
    scenario_id: str
    tenant_id: str
    owner_message: str
    evidence_items: tuple[ScenarioEvidence, ...]
    expected: ScenarioExpectation

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "tenant_id": self.tenant_id,
            "owner_message": self.owner_message,
            "evidence_items": [item.to_dict() for item in self.evidence_items],
            "expected": self.expected.to_dict(),
        }


__all__ = [
    "PipelineScenario",
    "ScenarioEvidence",
    "ScenarioExpectation",
]
