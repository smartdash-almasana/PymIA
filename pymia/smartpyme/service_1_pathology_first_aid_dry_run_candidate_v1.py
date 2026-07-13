from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    EXECUTION_MODE_DRY_RUN_CANDIDATE,
    STATUS_READY_FOR_DRY_RUN_CANDIDATE as PLAN_STATUS_READY_FOR_DRY_RUN_CANDIDATE,
    Service1ControlledComputationPlanV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_FIRST_AID_DRY_RUN_CANDIDATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_DRY_RUN_CANDIDATE_BUILT: Final[str] = "DRY_RUN_CANDIDATE_BUILT"
STATUS_BLOCKED_PLAN_NOT_READY: Final[str] = "BLOCKED_PLAN_NOT_READY"
STATUS_BLOCKED_UNSUPPORTED_COMPUTATION: Final[str] = "BLOCKED_UNSUPPORTED_COMPUTATION"
STATUS_BLOCKED_MISSING_INPUT_VALUES: Final[str] = "BLOCKED_MISSING_INPUT_VALUES"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_DRY_RUN_CANDIDATE_BUILT,
    STATUS_BLOCKED_PLAN_NOT_READY,
    STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
    STATUS_BLOCKED_MISSING_INPUT_VALUES,
)

DryRunCandidateStatusV1 = Literal[
    "DRY_RUN_CANDIDATE_BUILT",
    "BLOCKED_PLAN_NOT_READY",
    "BLOCKED_UNSUPPORTED_COMPUTATION",
    "BLOCKED_MISSING_INPUT_VALUES",
]

_FIELD_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "precio_venta": ("precio_venta", "precio", "precio_unitario", "precio_de_venta"),
    "costo_unitario": ("costo_unitario", "costo", "costo_base", "precio_compra"),
    "volumen_vendido": ("volumen_vendido", "cantidad", "cantidad_vendida", "unidades_vendidas"),
    "ventas_periodo": ("ventas_periodo", "ventas", "venta_total", "total_ventas", "importe_venta"),
    "cobranzas_periodo": ("cobranzas_periodo", "cobranzas", "cobros", "total_cobrado", "importe_cobrado"),
    "stock_actual": ("stock_actual", "stock", "inventario_actual"),
    "stock_minimo": ("stock_minimo", "stock_min", "minimo_stock", "min_stock"),
}

_SUPPORTED_COMPUTATIONS: Final[dict[str, dict[str, Any]]] = {
    "first_aid_precio_margen_basico_v1": {
        "required_fields": ("precio_venta", "costo_unitario", "volumen_vendido"),
        "compute": "precio_margen",
    },
    "first_aid_caja_diaria_triage_v1": {
        "required_fields": ("ventas_periodo", "cobranzas_periodo"),
        "compute": "caja_diaria",
    },
    "first_aid_stock_alertas_basicas_v1": {
        "required_fields": ("stock_actual", "stock_minimo"),
        "compute": "stock_alertas",
    },
}


@dataclass(frozen=True)
class Service1PathologyFirstAidDryRunCandidateV1:
    schema_version: str
    service_name: str
    status: DryRunCandidateStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    computation_plan_id: str | None
    execution_mode: str
    input_values: dict[str, object]
    computed_values: dict[str, object]
    finding_summary: str | None
    blocked_reason: str | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_plan(
    computation_plan_result: Service1ControlledComputationPlanV1,
) -> Service1ControlledComputationPlanV1:
    if not isinstance(computation_plan_result, Service1ControlledComputationPlanV1):
        raise ValueError("computation_plan_result must be a Service1ControlledComputationPlanV1")
    return computation_plan_result


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _normalized_input_values(input_values: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in input_values.items():
        if not isinstance(key, str):
            continue
        normalized[_normalize_text(key)] = value
    return normalized


def _resolve_input_values(
    required_fields: tuple[str, ...],
    input_values: dict[str, object],
) -> tuple[dict[str, object], tuple[str, ...]]:
    normalized_inputs = _normalized_input_values(input_values)
    resolved: dict[str, object] = {}
    missing: list[str] = []

    for required_field in required_fields:
        aliases = _FIELD_ALIASES.get(required_field, (required_field,))
        resolved_value = None
        found = False
        for alias in aliases:
            normalized_alias = _normalize_text(alias)
            if normalized_alias in normalized_inputs:
                resolved_value = normalized_inputs[normalized_alias]
                found = True
                break
        if found:
            resolved[required_field] = resolved_value
        else:
            missing.append(required_field)

    return resolved, tuple(missing)


def _as_number(value: object, *, field_name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        return float(value.strip())
    raise ValueError(f"{field_name} must be numeric")


def _compute_precio_margen(values: dict[str, object]) -> tuple[dict[str, object], str]:
    precio = _as_number(values["precio_venta"], field_name="precio_venta")
    costo = _as_number(values["costo_unitario"], field_name="costo_unitario")
    cantidad = _as_number(values["volumen_vendido"], field_name="volumen_vendido")
    unit_margin = precio - costo
    total_margin = unit_margin * cantidad
    margin_rate = (unit_margin / precio) if precio != 0 else None
    computed = {
        "unit_margin": unit_margin,
        "total_margin": total_margin,
        "margin_rate": margin_rate,
    }
    return computed, "Dry-run candidato de margen básico calculado sin ejecutar herramientas externas."


def _compute_caja_diaria(values: dict[str, object]) -> tuple[dict[str, object], str]:
    ventas = _as_number(values["ventas_periodo"], field_name="ventas_periodo")
    cobros = _as_number(values["cobranzas_periodo"], field_name="cobranzas_periodo")
    collection_gap = ventas - cobros
    collection_rate = (cobros / ventas) if ventas != 0 else None
    computed = {
        "collection_gap": collection_gap,
        "collection_rate": collection_rate,
    }
    return computed, "Dry-run candidato de caja/cobranzas calculado sin ejecutar herramientas externas."


def _compute_stock_alertas(values: dict[str, object]) -> tuple[dict[str, object], str]:
    stock_actual = _as_number(values["stock_actual"], field_name="stock_actual")
    stock_minimo = _as_number(values["stock_minimo"], field_name="stock_minimo")
    stock_gap = stock_actual - stock_minimo
    below_minimum = stock_actual < stock_minimo
    computed = {
        "stock_gap": stock_gap,
        "below_minimum": below_minimum,
    }
    return computed, "Dry-run candidato de alertas básicas de stock calculado sin ejecutar herramientas externas."


def _build_result(
    *,
    plan: Service1ControlledComputationPlanV1,
    status: DryRunCandidateStatusV1,
    input_values: dict[str, object],
    computed_values: dict[str, object],
    finding_summary: str | None,
    blocked_reason: str | None,
    metadata: dict[str, Any] | None,
) -> Service1PathologyFirstAidDryRunCandidateV1:
    return Service1PathologyFirstAidDryRunCandidateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=plan.case_id,
        tenant_id=plan.tenant_id,
        intake_id=plan.intake_id,
        run_id=plan.run_id,
        pathology_code=plan.pathology_code,
        allowed_computation_ref=plan.allowed_computation_ref,
        computation_plan_id=plan.computation_plan_id,
        execution_mode=EXECUTION_MODE_DRY_RUN_CANDIDATE,
        input_values=dict(input_values),
        computed_values=dict(computed_values),
        finding_summary=finding_summary,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_pathology_first_aid_dry_run_candidate_v1(
    *,
    computation_plan_result: Service1ControlledComputationPlanV1,
    input_values: dict[str, object],
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyFirstAidDryRunCandidateV1:
    plan = _required_plan(computation_plan_result)

    if plan.status != PLAN_STATUS_READY_FOR_DRY_RUN_CANDIDATE:
        return _build_result(
            plan=plan,
            status=STATUS_BLOCKED_PLAN_NOT_READY,
            input_values=dict(input_values),
            computed_values={},
            finding_summary=None,
            blocked_reason="computation_plan_not_ready_for_dry_run_candidate",
            metadata=metadata,
        )

    if plan.allowed_computation_ref not in _SUPPORTED_COMPUTATIONS:
        return _build_result(
            plan=plan,
            status=STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
            input_values=dict(input_values),
            computed_values={},
            finding_summary=None,
            blocked_reason="unsupported_allowed_computation_ref",
            metadata=metadata,
        )

    supported = _SUPPORTED_COMPUTATIONS[plan.allowed_computation_ref]
    required_fields = tuple(supported["required_fields"])
    resolved_inputs, missing_fields = _resolve_input_values(required_fields, input_values)

    if missing_fields:
        return _build_result(
            plan=plan,
            status=STATUS_BLOCKED_MISSING_INPUT_VALUES,
            input_values=dict(input_values),
            computed_values={},
            finding_summary=None,
            blocked_reason="missing_input_values",
            metadata={
                "missing_input_fields": missing_fields,
                **dict(metadata or {}),
            },
        )

    compute_kind = supported["compute"]
    if compute_kind == "precio_margen":
        computed_values, finding_summary = _compute_precio_margen(resolved_inputs)
    elif compute_kind == "caja_diaria":
        computed_values, finding_summary = _compute_caja_diaria(resolved_inputs)
    elif compute_kind == "stock_alertas":
        computed_values, finding_summary = _compute_stock_alertas(resolved_inputs)
    else:
        return _build_result(
            plan=plan,
            status=STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
            input_values=dict(input_values),
            computed_values={},
            finding_summary=None,
            blocked_reason="unsupported_compute_kind",
            metadata=metadata,
        )

    return _build_result(
        plan=plan,
        status=STATUS_DRY_RUN_CANDIDATE_BUILT,
        input_values=resolved_inputs,
        computed_values=computed_values,
        finding_summary=finding_summary,
        blocked_reason=None,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_DRY_RUN_CANDIDATE_BUILT",
    "STATUS_BLOCKED_PLAN_NOT_READY",
    "STATUS_BLOCKED_UNSUPPORTED_COMPUTATION",
    "STATUS_BLOCKED_MISSING_INPUT_VALUES",
    "ALLOWED_STATUSES",
    "Service1PathologyFirstAidDryRunCandidateV1",
    "build_service_1_pathology_first_aid_dry_run_candidate_v1",
]
