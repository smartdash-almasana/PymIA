"""Runtime entry points for deterministic service execution."""

from __future__ import annotations

from pymia.contracts.formula_contract import FormulaInput, FormulaResult
from pymia.contracts.pathology_contract import PathologyEvaluationInput, PathologyFinding
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.services.pathology_engine_service import PathologyEngineService


def calculate_formula(formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
    """Execute a formula through the authoritative deterministic engine."""
    return FormulaEngineService().calculate(formula_id, inputs)


def evaluate_pathology(pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
    """Evaluate a pathology through the authoritative deterministic engine."""
    return PathologyEngineService().evaluate(pathology_id, payload)


__all__ = ["calculate_formula", "evaluate_pathology"]
