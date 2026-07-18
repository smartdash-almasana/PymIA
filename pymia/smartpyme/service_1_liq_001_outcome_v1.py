"""Bounded LIQ_001 finding, treatment and XLSX delivery composition."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from pymia.smartpyme.service_1_liq_001_evaluator_v1 import (
    CAPABILITY_REF,
    CLASS_COLLECTIONS_EXCEED_PERIOD_SALES,
    CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES,
    CLASS_NO_ACTIVITY,
    CLASS_NO_GAP,
    CLASS_SALES_PENDING_COLLECTION,
    STATUS_EVALUATED,
)
from pymia.smartpyme.service_1_xlsx_delivery_v1 import build_service_1_xlsx_delivery_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_LIQ_001_OUTCOME_V1"
STATUS_READY: Final[str] = "OUTCOME_READY"
STATUS_BLOCKED: Final[str] = "OUTCOME_BLOCKED"

_FINDINGS: Final[dict[str, str]] = {
    CLASS_SALES_PENDING_COLLECTION: "En el período analizado, el importe vendido supera al importe cobrado.",
    CLASS_NO_GAP: "En el período analizado, el importe vendido coincide con el importe cobrado.",
    CLASS_COLLECTIONS_EXCEED_PERIOD_SALES: "En el período analizado, el importe cobrado supera al importe vendido registrado.",
    CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES: "Se registraron cobros en un período sin ventas registradas en la evidencia analizada.",
    CLASS_NO_ACTIVITY: "No se registraron ventas ni cobros en la evidencia del período analizado.",
}

_TREATMENTS: Final[dict[str, tuple[str, ...]]] = {
    CLASS_SALES_PENDING_COLLECTION: (
        "Identificar las operaciones que integran la brecha entre vendido y cobrado.",
        "Separar importes todavía no vencidos de importes vencidos, sólo cuando exista fecha de vencimiento.",
        "Conciliar los cobros posteriores o registrados en otra fuente antes de atribuir mora o pérdida.",
    ),
    CLASS_NO_GAP: (
        "Conservar la conciliación como control periódico.",
        "Verificar por operación cuando el total coincida pero existan dudas sobre compensaciones internas.",
    ),
    CLASS_COLLECTIONS_EXCEED_PERIOD_SALES: (
        "Revisar si los cobros corresponden a ventas de períodos anteriores.",
        "Conciliar anticipos, duplicados y diferencias de corte antes de corregir registros.",
    ),
    CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES: (
        "Verificar si los cobros corresponden a ventas de períodos anteriores o anticipos.",
        "Confirmar que la fuente de ventas cubra el mismo período y alcance que la fuente de cobros.",
    ),
    CLASS_NO_ACTIVITY: (
        "Confirmar que el archivo y el período seleccionados sean los correctos.",
        "No emitir conclusiones de liquidez sin actividad registrada.",
    ),
}

_LIMITATIONS: Final[tuple[str, ...]] = (
    "La diferencia matemática no identifica por sí sola clientes morosos, vencimientos ni pérdida definitiva.",
    "No se atribuyen causas sin evidencia adicional de operación, fecha, vencimiento o conciliación.",
    "Los resultados describen únicamente las filas y columnas confirmadas del período analizado.",
)

_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "Afirmar que toda brecha corresponde a morosidad.",
    "Afirmar que toda brecha es incobrable o pérdida definitiva.",
    "Atribuir fraude, error contable o responsabilidad de una persona sin evidencia adicional.",
)


def build_liq_001_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict):
        return _blocked("computation_result must be an object.")
    if computation_result.get("status") != STATUS_EVALUATED:
        return _blocked("LIQ_001 computation must be EVALUATED.")
    if computation_result.get("capability_ref") != CAPABILITY_REF:
        return _blocked("computation_result capability does not match LIQ_001.")
    classification = str(computation_result.get("classification") or "")
    if classification not in _FINDINGS:
        return _blocked("unsupported LIQ_001 classification.")

    computed = dict(computation_result.get("computed") or {})
    inputs = dict(computation_result.get("inputs") or {})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "capability_ref": CAPABILITY_REF,
        "classification": classification,
        "finding": _FINDINGS[classification],
        "treatment_actions": list(_TREATMENTS[classification]),
        "inputs_used": inputs,
        "computed_results": computed,
        "limitations": list(_LIMITATIONS),
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "bounded_finding_generated": True,
        "causal_diagnosis_generated": False,
        "runtime_authorized": False,
        "delivery_authorized": False,
    }


def deliver_liq_001_outcome_xlsx_v1(
    *, outcome: object, output_dir: str | Path, filename: str = "service_1_liq_001_result.xlsx"
) -> dict[str, Any]:
    if not isinstance(outcome, dict) or outcome.get("status") != STATUS_READY:
        return _blocked("LIQ_001 outcome must be OUTCOME_READY.")
    target_dir = Path(output_dir)
    if not target_dir.exists():
        return _blocked(f"output directory does not exist: {target_dir}")
    delivery = build_service_1_xlsx_delivery_v1(
        delivery_input={
            "service_name": "SERVICE_1",
            "capability_ref": CAPABILITY_REF,
            "status": str(outcome["classification"]),
            "owner_summary": str(outcome["finding"]),
            "inputs_used": dict(outcome["inputs_used"]),
            "computed_results": {
                **dict(outcome["computed_results"]),
                "treatment_actions": list(outcome["treatment_actions"]),
            },
            "missing_inputs": [],
            "limitations": list(outcome["limitations"]),
            "forbidden_claims": list(outcome["forbidden_claims"]),
            "technical_notes": [
                "Hallazgo acotado derivado de LIQ_001.",
                "No se generó atribución causal ni diagnóstico autónomo.",
            ],
            "runtime_authorized": False,
            "summary_ref_label": "pathology_code",
        },
        output_path=target_dir / filename,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "DELIVERED",
        "delivery": delivery,
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
    "build_liq_001_outcome_v1",
    "deliver_liq_001_outcome_xlsx_v1",
]
