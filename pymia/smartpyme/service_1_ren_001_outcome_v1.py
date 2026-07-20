"""Bounded REN_001 finding and treatment composition."""
from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_ren_001_evaluator_v1 import (
    CAPABILITY_REF,
    CLASS_BREAK_EVEN,
    CLASS_NEGATIVE_MARGIN,
    CLASS_POSITIVE_MARGIN,
    STATUS_EVALUATED,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REN_001_OUTCOME_V1"
STATUS_READY: Final[str] = "OUTCOME_READY"
STATUS_BLOCKED: Final[str] = "OUTCOME_BLOCKED"

_FINDINGS: Final[dict[str, str]] = {
    CLASS_POSITIVE_MARGIN: "La evidencia confirmada muestra un margen neto real positivo.",
    CLASS_BREAK_EVEN: "La evidencia confirmada muestra un margen neto real igual a cero.",
    CLASS_NEGATIVE_MARGIN: "La evidencia confirmada muestra un margen neto real negativo.",
}

_TREATMENTS: Final[dict[str, tuple[str, ...]]] = {
    CLASS_POSITIVE_MARGIN: (
        "Conservar el cálculo como control periódico sobre el mismo alcance de evidencia.",
        "Comparar por producto, cliente o canal sólo cuando existan bindings confirmados para ese nivel de detalle.",
    ),
    CLASS_BREAK_EVEN: (
        "Revisar la composición de costos e impuestos confirmados antes de cambiar precios o estructura.",
        "Verificar si existen costos omitidos antes de concluir que la operación está en equilibrio.",
    ),
    CLASS_NEGATIVE_MARGIN: (
        "Identificar qué operaciones integran el margen negativo dentro del alcance confirmado.",
        "Revisar precio, costos e impuestos por separado antes de atribuir una causa.",
        "No corregir precios ni costos automáticamente sin evidencia adicional y decisión del dueño.",
    ),
}

_LIMITATIONS: Final[tuple[str, ...]] = (
    "El margen matemático no identifica por sí solo la causa de la rentabilidad observada.",
    "No se infieren costos omitidos, impuestos futuros, inflación, reposición ni estructura fija no presente en la evidencia.",
    "Los resultados describen únicamente filas y columnas confirmadas por el dueño.",
)

_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "Afirmar que un margen negativo se debe a precio incorrecto sin evidencia adicional.",
    "Afirmar que un margen positivo representa rentabilidad integral de la empresa.",
    "Atribuir responsabilidad, fraude, error contable o decisión defectuosa sin evidencia adicional.",
)


def build_ren_001_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict):
        return _blocked("computation_result must be an object.")
    if computation_result.get("status") != STATUS_EVALUATED:
        return _blocked("REN_001 computation must be EVALUATED.")
    if computation_result.get("capability_ref") != CAPABILITY_REF:
        return _blocked("computation_result capability does not match REN_001.")
    classification = str(computation_result.get("classification") or "")
    if classification not in _FINDINGS:
        return _blocked("unsupported REN_001 classification.")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "capability_ref": CAPABILITY_REF,
        "classification": classification,
        "finding": _FINDINGS[classification],
        "treatment_actions": list(_TREATMENTS[classification]),
        "inputs_used": dict(computation_result.get("inputs") or {}),
        "computed_results": dict(computation_result.get("computed") or {}),
        "limitations": list(_LIMITATIONS),
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "bounded_finding_generated": True,
        "causal_diagnosis_generated": False,
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "bounded_finding_generated": False,
        "causal_diagnosis_generated": False,
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "build_ren_001_outcome_v1",
]
