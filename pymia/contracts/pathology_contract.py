from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from pymia.contracts.formula_contract import FormulaResult


class PathologyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    NOT_DETECTED = "NOT_DETECTED"
    PENDING_DATA = "PENDING_DATA"


class PathologySeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PathologyDefinition(BaseModel):
    pathology_id: str
    formula_id: str
    description: str
    severity: PathologySeverity
    suggested_action: str | None = None


class PathologyEvaluationInput(BaseModel):
    cliente_id: str
    formula_result_id: str
    formula_result: FormulaResult


class PathologyFinding(BaseModel):
    cliente_id: str
    pathology_id: str
    formula_result_id: str
    formula_id: str
    status: PathologyStatus
    severity: PathologySeverity | None = None
    suggested_action: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


def evaluate_pathology(pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
    from pymia.services.pathology_engine_service import PathologyEngineService

    return PathologyEngineService().evaluate(pathology_id, payload)
