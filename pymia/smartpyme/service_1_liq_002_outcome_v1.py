"""Bounded LIQ_002 projected cash finding and treatment composition."""
from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_liq_002_evaluator_v1 import (
    CAPABILITY_REF,
    CLASS_NEGATIVE_BALANCE,
    CLASS_POSITIVE_BALANCE,
    CLASS_ZERO_BALANCE,
    STATUS_EVALUATED,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_LIQ_002_OUTCOME_V1"
STATUS_READY: Final[str] = "OUTCOME_READY"
STATUS_BLOCKED: Final[str] = "OUTCOME_BLOCKED"

_FINDINGS: Final[dict[str, str]] = {
    CLASS_POSITIVE_BALANCE: "La evidencia confirmada proyecta un saldo final de caja positivo.",
    CLASS_ZERO_BALANCE: "La evidencia confirmada proyecta un saldo final de caja igual a cero.",
    CLASS_NEGATIVE_BALANCE: "La evidencia confirmada proyecta un saldo final de caja negativo.",
}

_TREATMENTS: Final[dict[str, tuple[str, ...]]] = {
    CLASS_POSITIVE_BALANCE: (
        "Conservar la proyección como control periódico sobre el mismo período y alcance.",
        "Verificar vencimientos y certeza de cobros y pagos antes de comprometer excedentes.",
    ),
    CLASS_ZERO_BALANCE: (
        "Revisar el calendario de cobros y pagos para identificar días de tensión dentro del período.",
        "Confirmar que no existan egresos omitidos antes de considerar equilibrada la caja.",
    ),
    CLASS_NEGATIVE_BALANCE: (
        "Identificar qué pagos y cobros integran el saldo proyectado negativo.",
        "Revisar fechas, certeza y prioridad de los movimientos antes de reprogramar compromisos.",
        "No atribuir insolvencia ni mora futura sin evidencia adicional.",
    ),
}

_LIMITATIONS: Final[tuple[str, ...]] = (
    "La proyección depende exclusivamente del saldo inicial y de los cobros y pagos esperados confirmados.",
    "No incorpora movimientos omitidos, financiación futura, impuestos no registrados ni cambios de fecha.",
    "Un saldo final positivo no demuestra liquidez suficiente durante todos los días del período.",
)

_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "Afirmar insolvencia, cesación de pagos o quiebra a partir de esta proyección.",
    "Afirmar disponibilidad libre de fondos sin revisar vencimientos y restricciones.",
    "Atribuir responsabilidad, fraude o error contable sin evidencia adicional.",
)


def build_liq_002_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict):
        return _blocked("computation_result must be an object.")
    if computation_result.get("status") != STATUS_EVALUATED:
        return _blocked("LIQ_002 computation must be EVALUATED.")
    if computation_result.get("capability_ref") != CAPABILITY_REF:
        return _blocked("computation_result capability does not match LIQ_002.")
    classification = str(computation_result.get("classification") or "")
    if classification not in _FINDINGS:
        return _blocked("unsupported LIQ_002 classification.")

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
    "build_liq_002_outcome_v1",
]
