from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class FormulaStatus(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"


class FormulaInput(BaseModel):
    name: str
    value: float | int | None
    source_refs: list[str] = Field(default_factory=list)


class FormulaResult(BaseModel):
    formula_id: str
    status: FormulaStatus
    value: float | None
    inputs: dict[str, float | int | None]
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
