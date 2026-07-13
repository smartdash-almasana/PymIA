from __future__ import annotations

import hashlib
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    STATUS_READY_FOR_COMPUTATION_PLAN as READINESS_STATUS_READY_FOR_COMPUTATION_PLAN,
    Service1PathologyEvidenceReadinessGateV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_CONTROLLED_COMPUTATION_PLAN_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
EXECUTION_MODE_DRY_RUN_CANDIDATE: Final[str] = "DRY_RUN_CANDIDATE"

STATUS_READY_FOR_DRY_RUN_CANDIDATE: Final[str] = "READY_FOR_DRY_RUN_CANDIDATE"
STATUS_BLOCKED_READINESS_NOT_READY: Final[str] = "BLOCKED_READINESS_NOT_READY"
STATUS_BLOCKED_UNSUPPORTED_COMPUTATION: Final[str] = "BLOCKED_UNSUPPORTED_COMPUTATION"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_READY_FOR_DRY_RUN_CANDIDATE,
    STATUS_BLOCKED_READINESS_NOT_READY,
    STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
)

ALLOWED_EXECUTION_MODES: Final[tuple[str, ...]] = (EXECUTION_MODE_DRY_RUN_CANDIDATE,)

ALLOWLISTED_COMPUTATIONS: Final[tuple[str, ...]] = (
    "first_aid_precio_margen_basico_v1",
    "first_aid_caja_diaria_triage_v1",
    "first_aid_stock_alertas_basicas_v1",
)

ControlledComputationPlanStatusV1 = Literal[
    "READY_FOR_DRY_RUN_CANDIDATE",
    "BLOCKED_READINESS_NOT_READY",
    "BLOCKED_UNSUPPORTED_COMPUTATION",
]

_FIELD_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "precio_venta": ("precio_venta", "precio", "precio_unitario", "precio_de_venta"),
    "costo_unitario": ("costo_unitario", "costo", "costo_base", "precio_compra"),
    "volumen_vendido": ("volumen_vendido", "cantidad", "cantidad_vendida", "unidades_vendidas"),
    "ventas_periodo": ("ventas_periodo", "ventas", "venta_total", "total_ventas", "importe_venta"),
    "cobranzas_periodo": ("cobranzas_periodo", "cobranzas", "cobros", "total_cobrado", "importe_cobrado"),
    "saldo_pendiente": ("saldo_pendiente", "saldo", "saldo_cobrar", "cuentas_por_cobrar"),
    "producto": ("producto", "sku", "articulo", "item"),
    "stock_actual": ("stock_actual", "stock", "inventario_actual"),
    "movimientos_stock": ("movimientos_stock", "movimientos", "entradas_salidas"),
    "fecha": ("fecha", "periodo", "periodo_ref", "fecha_movimiento"),
    "monto": ("monto", "importe", "valor", "total"),
    "entrada_salida": ("entrada_salida", "tipo_movimiento", "debe_haber", "ingreso_egreso"),
}


@dataclass(frozen=True)
class Service1ControlledComputationPlanV1:
    schema_version: str
    service_name: str
    status: ControlledComputationPlanStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    computation_plan_id: str | None
    execution_mode: str
    required_fields: tuple[str, ...]
    available_fields: tuple[str, ...]
    field_bindings: dict[str, str]
    blocked_reason: str | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_readiness_gate(
    evidence_readiness_gate_result: Service1PathologyEvidenceReadinessGateV1,
) -> Service1PathologyEvidenceReadinessGateV1:
    if not isinstance(evidence_readiness_gate_result, Service1PathologyEvidenceReadinessGateV1):
        raise ValueError("evidence_readiness_gate_result must be a Service1PathologyEvidenceReadinessGateV1")
    return evidence_readiness_gate_result


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _plan_id(*, case_id: str, pathology_code: str | None, allowed_computation_ref: str | None) -> str | None:
    if not pathology_code or not allowed_computation_ref:
        return None
    raw = f"{case_id}|{pathology_code}|{allowed_computation_ref}"
    short_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"service_1:dry_run_plan:{short_hash}"


def _field_bindings(
    required_fields: tuple[str, ...],
    available_fields: tuple[str, ...],
) -> dict[str, str]:
    normalized_available = {_normalize_text(field) for field in available_fields}
    bindings: dict[str, str] = {}
    for required_field in required_fields:
        aliases = _FIELD_ALIASES.get(required_field, (required_field,))
        if any(_normalize_text(alias) in normalized_available for alias in aliases):
            bindings[required_field] = required_field
    return bindings


def _build_result(
    *,
    readiness_gate: Service1PathologyEvidenceReadinessGateV1,
    status: ControlledComputationPlanStatusV1,
    blocked_reason: str | None,
    field_bindings: dict[str, str],
    metadata: dict[str, Any] | None,
) -> Service1ControlledComputationPlanV1:
    return Service1ControlledComputationPlanV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=readiness_gate.case_id,
        tenant_id=readiness_gate.tenant_id,
        intake_id=readiness_gate.intake_id,
        run_id=readiness_gate.run_id,
        pathology_code=readiness_gate.pathology_code,
        allowed_computation_ref=readiness_gate.allowed_computation_ref,
        computation_plan_id=(
            _plan_id(
                case_id=readiness_gate.case_id,
                pathology_code=readiness_gate.pathology_code,
                allowed_computation_ref=readiness_gate.allowed_computation_ref,
            )
            if status == STATUS_READY_FOR_DRY_RUN_CANDIDATE
            else None
        ),
        execution_mode=EXECUTION_MODE_DRY_RUN_CANDIDATE,
        required_fields=readiness_gate.required_fields,
        available_fields=readiness_gate.available_fields,
        field_bindings=field_bindings,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_controlled_computation_plan_v1(
    *,
    evidence_readiness_gate_result: Service1PathologyEvidenceReadinessGateV1,
    metadata: dict[str, Any] | None = None,
) -> Service1ControlledComputationPlanV1:
    readiness_gate = _required_readiness_gate(evidence_readiness_gate_result)

    if readiness_gate.status != READINESS_STATUS_READY_FOR_COMPUTATION_PLAN:
        return _build_result(
            readiness_gate=readiness_gate,
            status=STATUS_BLOCKED_READINESS_NOT_READY,
            blocked_reason="readiness_gate_not_ready_for_computation_plan",
            field_bindings={},
            metadata=metadata,
        )

    if readiness_gate.allowed_computation_ref not in ALLOWLISTED_COMPUTATIONS:
        return _build_result(
            readiness_gate=readiness_gate,
            status=STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
            blocked_reason="unsupported_allowed_computation_ref",
            field_bindings={},
            metadata=metadata,
        )

    field_bindings = _field_bindings(
        readiness_gate.required_fields,
        readiness_gate.available_fields,
    )

    return _build_result(
        readiness_gate=readiness_gate,
        status=STATUS_READY_FOR_DRY_RUN_CANDIDATE,
        blocked_reason=None,
        field_bindings=field_bindings,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "EXECUTION_MODE_DRY_RUN_CANDIDATE",
    "STATUS_READY_FOR_DRY_RUN_CANDIDATE",
    "STATUS_BLOCKED_READINESS_NOT_READY",
    "STATUS_BLOCKED_UNSUPPORTED_COMPUTATION",
    "ALLOWED_STATUSES",
    "ALLOWLISTED_COMPUTATIONS",
    "Service1ControlledComputationPlanV1",
    "build_service_1_controlled_computation_plan_v1",
]
