"""Inference result contracts for document intelligence phase 1."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .fio import FichaInformativaOpacidad
from .semantic_schema import SemanticSchema


class MathematicalConsistencyCheck(BaseModel):
    """Placeholder consistency check output for future financial validations."""

    passed: bool = False
    details: str = Field(default="Not implemented in phase 1.")


class SchemaInferenceResult(BaseModel):
    """Contractual result of schema inference execution."""

    semantic_schema: Optional[SemanticSchema] = None
    context_present: bool = False
    mathematical_consistency: MathematicalConsistencyCheck = Field(
        default_factory=MathematicalConsistencyCheck
    )
    fio: List[FichaInformativaOpacidad] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    @property
    def can_run_benchmark(self) -> bool:
        """Benchmark can run only when context exists and no blocking errors exist."""
        return self.context_present and not self.errors
