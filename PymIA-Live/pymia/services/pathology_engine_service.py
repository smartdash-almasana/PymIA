from __future__ import annotations

from pymia.contracts.formula_contract import FormulaStatus
from pymia.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyFinding,
    PathologyStatus,
)
from pymia.services.pathology_knowledge_tank import (
    LocalPathologyKnowledgeTank,
    PathologyKnowledgeTank,
)


class PathologyEngineService:
    """Evalúa patologías usando un tanque de conocimiento enchufable."""

    def __init__(self, knowledge_tank: PathologyKnowledgeTank | None = None) -> None:
        self.knowledge_tank = knowledge_tank or LocalPathologyKnowledgeTank()

    def evaluate(self, pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = self.knowledge_tank.get_definition(pathology_id)
        if definition is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=payload.formula_result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=payload.formula_result.source_refs,
                explanation="Patología no soportada por el tanque de conocimiento.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
            )

        result = payload.formula_result
        tank_metadata = self.knowledge_tank.get_metadata(pathology_id)

        if result.status == FormulaStatus.BLOCKED:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="No se puede evaluar la patología porque la fórmula está bloqueada.",
                metadata={
                    "blocking_reason": result.blocking_reason,
                    "catalog": tank_metadata,
                },
            )

        if result.formula_id != definition.formula_id:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="La fórmula calculada no coincide con la patología solicitada.",
                metadata={
                    "expected_formula_id": definition.formula_id,
                    "catalog": tank_metadata,
                },
            )

        evaluator = self.knowledge_tank.get_evaluator(pathology_id)
        if evaluator is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="Patología sin evaluador implementado.",
                metadata={
                    "blocking_reason": "PATHOLOGY_NOT_IMPLEMENTED",
                    "catalog": tank_metadata,
                },
            )

        return evaluator(payload)
