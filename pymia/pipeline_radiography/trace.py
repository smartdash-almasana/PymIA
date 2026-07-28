from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ALLOWED_RADIOGRAPHY_VERDICTS: tuple[str, ...] = (
    "PASS",
    "BLOCKED_EXPECTED",
    "FAIL",
    "AMBIGUOUS",
)


@dataclass
class PipelineStageTrace:
    name: str
    status: str
    input_type: str | None = None
    output_type: str | None = None
    summary: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineTrace:
    trace_id: str
    scenario_id: str
    stages: list[PipelineStageTrace] = field(default_factory=list)
    overall_status: str = "AMBIGUOUS"
    blocked_at: str | None = None
    final_summary: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0

    def add_stage(self, stage: PipelineStageTrace) -> None:
        self.stages.append(stage)

    def set_final(
        self,
        *,
        overall_status: str,
        blocked_at: str | None = None,
        final_summary: dict[str, Any] | None = None,
    ) -> None:
        self.overall_status = overall_status
        self.blocked_at = blocked_at
        self.final_summary = dict(final_summary or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "scenario_id": self.scenario_id,
            "stages": [stage.to_dict() for stage in self.stages],
            "overall_status": self.overall_status,
            "blocked_at": self.blocked_at,
            "final_summary": dict(self.final_summary),
            "duration_ms": self.duration_ms,
        }


__all__ = [
    "ALLOWED_RADIOGRAPHY_VERDICTS",
    "PipelineStageTrace",
    "PipelineTrace",
]
