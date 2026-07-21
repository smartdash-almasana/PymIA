"""Bounded PYME_011 DSO finding and treatment composition."""
from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import (
    CAPABILITY_REF,
    CLASS_EQUALS_PERIOD,
    CLASS_EXCEEDS_PERIOD,
    CLASS_WITHIN_PERIOD,
    STATUS_EVALUATED,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PYME_011_OUTCOME_V1"
STATUS_READY: Final[str] = "OUTCOME_READY"
STATUS_BLOCKED: Final[str] = "OUTCOME_BLOCKED"
_FINDINGS: Final[dict[str, str]] = {
    CLASS_WITHIN_PERIOD: "La evidencia confirmada muestra un DSO menor que la duración del período analizado.",
    CLASS_EQUALS_PERIOD: "La evidencia confirmada muestra un DSO igual a la duración del período analizado.",
    CLASS_EXCEEDS_PERIOD: "La evidencia confirmada muestra un DSO mayor que la duración del período analizado.",
}
_TREATMENTS: Final[dict[str, tuple[str, ...]]] = {
    CLASS_WITHIN_PERIOD: (
        "Conservar el indicador como control periódico sobre el mismo alcance y duración.",
        "Comparar su evolución sólo entre períodos construidos con la misma convención.",
    ),
    CLASS_EQUALS_PERIOD: (
        "Revisar la composición de cuentas por cobrar y ventas confirmadas antes de interpretar el resultado.",
        "Separar saldos vencidos y no vencidos únicamente cuando exista evidencia confirmada para hacerlo.",
    ),
    CLASS_EXCEEDS_PERIOD: (
        "Identificar qué saldos integran las cuentas por cobrar dentro del alcance confirmado.",
        "Revisar vencimientos y cobranzas por separado antes de atribuir una causa.",
        "No inferir morosidad ni incobrabilidad sin evidencia adicional.",
    ),
}
_LIMITATIONS: Final[tuple[str, ...]] = (
    "El DSO describe una relación matemática entre cuentas por cobrar, ventas y días; no identifica causas.",
    "La comparación usa únicamente el período confirmado y no incorpora umbrales sectoriales.",
    "El resultado depende de que cuentas por cobrar y ventas correspondan al mismo alcance temporal.",
)
_FORBIDDEN: Final[tuple[str, ...]] = (
    "Afirmar morosidad, incobrabilidad, fraude o error contable sin evidencia adicional.",
    "Comparar períodos con convenciones temporales diferentes sin normalización explícita.",
    "Atribuir responsabilidad comercial o financiera a una persona o proceso.",
)


def build_pyme_011_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict):
        return _blocked("computation_result must be an object.")
    if computation_result.get("status") != STATUS_EVALUATED:
        return _blocked("PYME_011 computation must be EVALUATED.")
    if computation_result.get("capability_ref") != CAPABILITY_REF:
        return _blocked("computation_result capability does not match PYME_011.")
    classification = str(computation_result.get("classification") or "")
    if classification not in _FINDINGS:
        return _blocked("unsupported PYME_011 classification.")
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
        "forbidden_claims": list(_FORBIDDEN),
        "bounded_finding_generated": True,
        "causal_diagnosis_generated": False,
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "status": STATUS_BLOCKED, "blocked_reason": reason, "bounded_finding_generated": False, "causal_diagnosis_generated": False, "runtime_authorized": False, "delivery_authorized": False}


__all__ = ["SCHEMA_VERSION", "STATUS_READY", "STATUS_BLOCKED", "build_pyme_011_outcome_v1"]
