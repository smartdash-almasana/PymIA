from __future__ import annotations

import math
from typing import Final

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FirstAidToolResultV1,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)

TOOL_REF: Final[str] = "stock_alertas_basicas"
REQUIRED_INPUTS: Final[tuple[str, str, str]] = ("producto", "stock_actual", "stock_minimo")
OPTIONAL_INPUTS: Final[tuple[str, ...]] = ("ventas_diarias_promedio",)

_BASE_LIMITATIONS: Final[tuple[str, ...]] = (
    "No confirma stock fisico real.",
    "No reemplaza conteo fisico.",
    "No valida sistema de inventario.",
    "No confirma quiebre de stock.",
    "No calcula rotacion real.",
    "No incluye compras pendientes ni ventas no declaradas.",
)

_BASE_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Tool scope is limited to deterministic math over explicit inputs.",
)


def run_stock_alertas_basicas_v1(
    *,
    producto: object | None = None,
    stock_actual: object | None = None,
    stock_minimo: object | None = None,
    ventas_diarias_promedio: object | None = None,
) -> FirstAidToolResultV1:
    raw_inputs = {
        "producto": producto,
        "stock_actual": stock_actual,
        "stock_minimo": stock_minimo,
        "ventas_diarias_promedio": ventas_diarias_promedio,
    }
    missing_inputs = _missing_inputs(raw_inputs)
    inputs_used = _provided_inputs(raw_inputs)

    if missing_inputs:
        return build_missing_inputs_tool_result_v1(
            tool_ref=TOOL_REF,
            missing_inputs=missing_inputs,
            owner_summary="Faltan datos explicitos para la alerta preliminar de stock.",
            inputs_used=inputs_used,
            limitations=list(_BASE_LIMITATIONS),
            technical_notes=list(_BASE_TECHNICAL_NOTES),
        )

    normalized_producto = str(producto).strip()

    try:
        normalized_stock_actual = _normalize_number(
            field_name="stock_actual",
            value=stock_actual,
        )
        normalized_stock_minimo = _normalize_number(
            field_name="stock_minimo",
            value=stock_minimo,
        )
        normalized_ventas_diarias_promedio = _normalize_optional_number(
            field_name="ventas_diarias_promedio",
            value=ventas_diarias_promedio,
        )
    except ValueError as exc:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[*list(_BASE_TECHNICAL_NOTES), str(exc)],
        )

    if normalized_stock_actual < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "stock_actual cannot be negative.",
            ],
        )

    if normalized_stock_minimo < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "stock_minimo cannot be negative.",
            ],
        )

    if normalized_ventas_diarias_promedio is not None and normalized_ventas_diarias_promedio < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "ventas_diarias_promedio cannot be negative.",
            ],
        )

    computed_results: dict[str, object] = {
        "producto": normalized_producto,
        "stock_bajo": normalized_stock_actual <= normalized_stock_minimo,
        "diferencia_vs_minimo": normalized_stock_actual - normalized_stock_minimo,
        "dias_stock_restante": None,
    }
    limitations = list(_BASE_LIMITATIONS)

    if normalized_ventas_diarias_promedio is not None:
        if normalized_ventas_diarias_promedio == 0:
            limitations.append("No se calcula dias_stock_restante con ventas_diarias_promedio=0.")
        else:
            computed_results["dias_stock_restante"] = (
                normalized_stock_actual / normalized_ventas_diarias_promedio
            )

    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="OK",
        inputs_used=inputs_used,
        computed_results=computed_results,
        limitations=limitations,
        owner_summary="Alerta preliminar de stock sobre valores declarados.",
        technical_notes=list(_BASE_TECHNICAL_NOTES),
    )


def _build_invalid_input_result(
    *,
    inputs_used: dict[str, object],
    technical_notes: list[str],
) -> FirstAidToolResultV1:
    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="INVALID_INPUT",
        inputs_used=inputs_used,
        computed_results={},
        limitations=list(_BASE_LIMITATIONS),
        owner_summary="Los valores declarados no permiten una alerta preliminar prudente.",
        technical_notes=technical_notes,
    )


def _missing_inputs(raw_inputs: dict[str, object | None]) -> list[str]:
    missing_inputs: list[str] = []

    producto = raw_inputs["producto"]
    if producto is None or (isinstance(producto, str) and not producto.strip()):
        missing_inputs.append("producto")

    for field in ("stock_actual", "stock_minimo"):
        if raw_inputs[field] is None:
            missing_inputs.append(field)

    return missing_inputs


def _provided_inputs(raw_inputs: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in raw_inputs.items() if value is not None}


def _normalize_number(*, field_name: str, value: object | None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")

    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{field_name} must be finite.")

    return normalized


def _normalize_optional_number(*, field_name: str, value: object | None) -> float | None:
    if value is None:
        return None
    return _normalize_number(field_name=field_name, value=value)
