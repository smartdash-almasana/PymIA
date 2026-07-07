from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    PATHOLOGY_CSH_001,
    PATHOLOGY_LIQ_001,
    PATHOLOGY_REN_001,
    PATHOLOGY_STK_001,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_READY_FOR_COMPUTATION_PLAN: Final[str] = "READY_FOR_COMPUTATION_PLAN"
STATUS_NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY: Final[str] = "BLOCKED_UNSUPPORTED_PATHOLOGY"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_READY_FOR_COMPUTATION_PLAN,
    STATUS_NEEDS_EVIDENCE,
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
)

AllowedComputationCandidateStatusV1 = Literal[
    "READY_FOR_COMPUTATION_PLAN",
    "NEEDS_EVIDENCE",
    "BLOCKED_UNSUPPORTED_PATHOLOGY",
]

_PATHOLOGY_TO_COMPUTATION: Final[dict[str, dict[str, Any]]] = {
    PATHOLOGY_REN_001: {
        "allowed_computation_ref": "first_aid_precio_margen_basico_v1",
        "required_fields": ("precio_venta", "costo_unitario", "volumen_vendido"),
    },
    PATHOLOGY_LIQ_001: {
        "allowed_computation_ref": "first_aid_caja_diaria_triage_v1",
        "required_fields": ("ventas_periodo", "cobranzas_periodo", "saldo_pendiente"),
    },
    PATHOLOGY_STK_001: {
        "allowed_computation_ref": "first_aid_stock_alertas_basicas_v1",
        "required_fields": ("producto", "stock_actual", "movimientos_stock"),
    },
    PATHOLOGY_CSH_001: {
        "allowed_computation_ref": "first_aid_caja_diaria_triage_v1",
        "required_fields": ("fecha", "monto", "entrada_salida"),
    },
}

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
class Service1AllowedComputationCandidateV1:
    schema_version: str
    service_name: str
    pathology_code: str
    status: AllowedComputationCandidateStatusV1
    allowed_computation_ref: str | None
    required_fields: tuple[str, ...]
    available_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    readiness_status: AllowedComputationCandidateStatusV1
    blocked_reason: str | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (tuple, list, set)):
        items = value
    else:
        items = (value,)
    cleaned: list[str] = []
    for item in items:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return tuple(cleaned)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _available_fields_for_required(
    required_fields: tuple[str, ...],
    available_data_fields: tuple[str, ...],
) -> tuple[str, ...]:
    normalized_available = {_normalize_text(field) for field in available_data_fields}
    matched: list[str] = []
    for required_field in required_fields:
        aliases = _FIELD_ALIASES.get(required_field, (required_field,))
        if any(_normalize_text(alias) in normalized_available for alias in aliases):
            matched.append(required_field)
    return tuple(matched)


def _resolve_missing_fields(
    *,
    required_fields: tuple[str, ...],
    available_fields: tuple[str, ...],
    missing_evidence_items: tuple[str, ...],
) -> tuple[str, ...]:
    missing = [field for field in required_fields if field not in available_fields]
    normalized_known_missing = {_normalize_text(field) for field in missing_evidence_items}
    for field in required_fields:
        aliases = _FIELD_ALIASES.get(field, (field,))
        if any(_normalize_text(alias) in normalized_known_missing for alias in aliases) and field not in missing:
            missing.append(field)
    return tuple(missing)


def build_service_1_pathology_to_allowed_computation_candidate_v1(
    *,
    pathology_code: str,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    missing_evidence_items: list[str] | tuple[str, ...] | None = None,
    business_period_reference: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1AllowedComputationCandidateV1:
    pathology_code = _required_text(pathology_code, field_name="pathology_code")
    available_data_fields_tuple = _clean_tuple(available_data_fields)
    missing_evidence_items_tuple = _clean_tuple(missing_evidence_items)
    business_period_reference = _clean_optional_text(business_period_reference)

    definition = _PATHOLOGY_TO_COMPUTATION.get(pathology_code)
    if definition is None:
        status = STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY
        return Service1AllowedComputationCandidateV1(
            schema_version=SCHEMA_VERSION,
            service_name=SERVICE_NAME,
            pathology_code=pathology_code,
            status=status,
            allowed_computation_ref=None,
            required_fields=(),
            available_fields=(),
            missing_fields=(),
            readiness_status=status,
            blocked_reason="unsupported_pathology_code",
            runtime_authorized=False,
            reexecution_authorized=False,
            recalculation_authorized=False,
            delivery_authorized=False,
            metadata=dict(metadata or {}),
        )

    required_fields = tuple(definition["required_fields"])
    available_fields = _available_fields_for_required(required_fields, available_data_fields_tuple)
    missing_fields = _resolve_missing_fields(
        required_fields=required_fields,
        available_fields=available_fields,
        missing_evidence_items=missing_evidence_items_tuple,
    )

    if business_period_reference is None and "fecha" in required_fields and "fecha" not in missing_fields:
        missing_fields = tuple(dict.fromkeys((*missing_fields, "business_period_reference")))

    if missing_fields:
        status = STATUS_NEEDS_EVIDENCE
        blocked_reason = "missing_required_fields"
    else:
        status = STATUS_READY_FOR_COMPUTATION_PLAN
        blocked_reason = None

    return Service1AllowedComputationCandidateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        pathology_code=pathology_code,
        status=status,
        allowed_computation_ref=str(definition["allowed_computation_ref"]),
        required_fields=required_fields,
        available_fields=available_fields,
        missing_fields=missing_fields,
        readiness_status=status,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={
            "business_period_reference": business_period_reference,
            **dict(metadata or {}),
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_READY_FOR_COMPUTATION_PLAN",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY",
    "ALLOWED_STATUSES",
    "Service1AllowedComputationCandidateV1",
    "build_service_1_pathology_to_allowed_computation_candidate_v1",
]
