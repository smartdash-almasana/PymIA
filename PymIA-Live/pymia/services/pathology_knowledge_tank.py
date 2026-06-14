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
    """Tanque local mínimo alineado con los catálogos vivos."""

    def __init__(self) -> None:
        self._definitions: dict[str, PathologyDefinition] = {
            "REN_001": PathologyDefinition(
                pathology_id="REN_001",
                formula_id="REN_001_margen_neto_real",
                description="Detecta margen neto real negativo sobre ventas, costos e impuestos.",
                severity=PathologySeverity.HIGH,
                suggested_action="Revisar costos, impuestos o precios de venta.",
            ),
        }
        self._metadata: dict[str, dict] = {
            "REN_001": {
                "category": "rentabilidad",
                "requires_formula": True,
                "source": "local_chip1",
            }
        }
        self._evaluators: dict[str, PathologyEvaluator] = {
            "REN_001": self._evaluate_ren_001_margen_neto_real,
        }

    def get_definition(self, pathology_id: str) -> PathologyDefinition | None:
        return self._definitions.get(pathology_id)

    def get_metadata(self, pathology_id: str) -> dict:
        return dict(self._metadata.get(pathology_id, {}))

    def get_evaluator(self, pathology_id: str) -> PathologyEvaluator | None:
        return self._evaluators.get(pathology_id)

    def _evaluate_ren_001_margen_neto_real(self, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = self.get_definition("REN_001")
        if definition is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id="REN_001",
                formula_result_id=payload.formula_result_id,
                formula_id=payload.formula_result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=payload.formula_result.source_refs,
                explanation="Patología no encontrada en tanque local.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
            )

        result = payload.formula_result
        metadata = {"catalog": self.get_metadata("REN_001")}

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
                explanation=f"El margen neto real calculado es {result.value}, lo cual indica pérdida.",
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
