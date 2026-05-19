from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from pymia.contracts.pathology_contract import (
    PathologyDefinition,
    PathologyEvaluationInput,
    PathologyFinding,
    PathologySeverity,
    PathologyStatus,
)


PathologyEvaluator = Callable[[PathologyEvaluationInput], PathologyFinding]


class PathologyKnowledgeTank(Protocol):
    """Interfaz mínima para tanques de conocimiento de patologías.

    El kernel consume esta interfaz. El corpus concreto es reemplazable.
    """

    def get_definition(self, pathology_id: str) -> PathologyDefinition | None: ...

    def get_metadata(self, pathology_id: str) -> dict: ...

    def get_evaluator(self, pathology_id: str) -> PathologyEvaluator | None: ...


class LocalPathologyKnowledgeTank:
    """Tanque local mínimo para Chip 1.

    Solo incluye patologías con fórmula/evaluador ejecutable en este chip.
    """

    def __init__(self) -> None:
        self._definitions: dict[str, PathologyDefinition] = {
            "margen_bruto_negativo": PathologyDefinition(
                pathology_id="margen_bruto_negativo",
                formula_id="margen_bruto",
                description="Detecta margen bruto negativo sobre ventas y costos declarados.",
                severity=PathologySeverity.HIGH,
                suggested_action="Revisar costos o precios de venta.",
            ),
        }
        self._metadata: dict[str, dict] = {
            "margen_bruto_negativo": {
                "category": "rentabilidad",
                "requires_formula": True,
                "source": "local_chip1",
            }
        }
        self._evaluators: dict[str, PathologyEvaluator] = {
            "margen_bruto_negativo": self._evaluate_margen_bruto_negativo,
        }

    def get_definition(self, pathology_id: str) -> PathologyDefinition | None:
        return self._definitions.get(pathology_id)

    def get_metadata(self, pathology_id: str) -> dict:
        return dict(self._metadata.get(pathology_id, {}))

    def get_evaluator(self, pathology_id: str) -> PathologyEvaluator | None:
        return self._evaluators.get(pathology_id)

    def _evaluate_margen_bruto_negativo(self, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = self.get_definition("margen_bruto_negativo")
        if definition is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id="margen_bruto_negativo",
                formula_result_id=payload.formula_result_id,
                formula_id=payload.formula_result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=payload.formula_result.source_refs,
                explanation="Patología no encontrada en tanque local.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
            )

        result = payload.formula_result
        metadata = {"catalog": self.get_metadata("margen_bruto_negativo")}

        if result.value is not None and result.value < 0:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=definition.pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.ACTIVE,
                severity=definition.severity,
                suggested_action=definition.suggested_action,
                source_refs=result.source_refs,
                explanation=f"El margen bruto calculado es {result.value}, lo cual indica pérdida.",
                metadata=metadata,
            )

        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=definition.pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.NOT_DETECTED,
            source_refs=result.source_refs,
            explanation="No se detectó la patología con el resultado calculado.",
            metadata=metadata,
        )
