from __future__ import annotations

import math
from typing import Final

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FirstAidToolResultV1,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)

TOOL_REF: Final[str] = "precio_margen_basico"
REQUIRED_INPUTS: Final[tuple[str, str]] = ("precio_venta", "costo_unitario")

_BASE_LIMITATIONS: Final[tuple[str, ...]] = (
    "No incluye impuestos.",
    "No incluye comisiones.",
    "No incluye costos fijos.",
    "No incluye costos indirectos.",
    "No reemplaza analisis contable.",
)

_BASE_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Tool scope is limited to deterministic math over explicit inputs.",
)


def run_precio_margen_basico_v1(
    *,
    precio_venta: object | None = None,
    costo_unitario: object | None = None,
) -> FirstAidToolResultV1:
    raw_inputs = {
        "precio_venta": precio_venta,
        "costo_unitario": costo_unitario,
    }
    missing_inputs = [field for field in REQUIRED_INPUTS if raw_inputs[field] is None]
    inputs_used = _provided_inputs(raw_inputs)

    if missing_inputs:
        return build_missing_inputs_tool_result_v1(
            tool_ref=TOOL_REF,
            missing_inputs=missing_inputs,
            owner_summary="Faltan datos explicitos para el calculo preliminar.",
            inputs_used=inputs_used,
            limitations=list(_BASE_LIMITATIONS),
            technical_notes=list(_BASE_TECHNICAL_NOTES),
        )

    try:
        normalized_precio_venta = _normalize_number(
            field_name="precio_venta",
            value=precio_venta,
        )
        normalized_costo_unitario = _normalize_number(
            field_name="costo_unitario",
            value=costo_unitario,
        )
    except ValueError as exc:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[*list(_BASE_TECHNICAL_NOTES), str(exc)],
        )

    if normalized_precio_venta <= 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "precio_venta must be greater than 0.",
            ],
        )

    if normalized_costo_unitario < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "costo_unitario cannot be negative.",
            ],
        )

    margen_bruto_pesos = normalized_precio_venta - normalized_costo_unitario
    computed_results: dict[str, object] = {
        "margen_bruto_pesos": margen_bruto_pesos,
        "margen_bruto_porcentaje": margen_bruto_pesos / normalized_precio_venta,
        "markup_porcentaje": None,
    }
    limitations = list(_BASE_LIMITATIONS)
    owner_summary = "Calculo preliminar sobre precio y costo declarados."

    if normalized_costo_unitario == 0:
        limitations.append("No se calcula markup con costo_unitario=0.")
        owner_summary = "Calculo preliminar con markup no calculable por costo cero."
    else:
        computed_results["markup_porcentaje"] = margen_bruto_pesos / normalized_costo_unitario

    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="OK",
        inputs_used=inputs_used,
        computed_results=computed_results,
        limitations=limitations,
        owner_summary=owner_summary,
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
        owner_summary="Los valores declarados no permiten un calculo preliminar prudente.",
        technical_notes=technical_notes,
    )


def _provided_inputs(raw_inputs: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in raw_inputs.items() if value is not None}


def _normalize_number(*, field_name: str, value: object | None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")

    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{field_name} must be finite.")

    return normalized
