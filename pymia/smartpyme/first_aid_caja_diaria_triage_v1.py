from __future__ import annotations

import math
from typing import Final

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FirstAidToolResultV1,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)

TOOL_REF: Final[str] = "caja_diaria_triage"
REQUIRED_INPUTS: Final[tuple[str, str, str]] = ("saldo_inicial", "ingresos", "egresos")

_BASE_LIMITATIONS: Final[tuple[str, ...]] = (
    "No confirma saldo bancario real.",
    "No equivale a conciliacion.",
    "No valida efectivo fisico.",
    "No incluye movimientos no declarados.",
    "No reemplaza revision contable.",
)

_BASE_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Tool scope is limited to deterministic math over explicit inputs.",
)


def run_caja_diaria_triage_v1(
    *,
    saldo_inicial: object | None = None,
    ingresos: object | None = None,
    egresos: object | None = None,
) -> FirstAidToolResultV1:
    raw_inputs = {
        "saldo_inicial": saldo_inicial,
        "ingresos": ingresos,
        "egresos": egresos,
    }
    missing_inputs = [field for field in REQUIRED_INPUTS if raw_inputs[field] is None]
    inputs_used = _provided_inputs(raw_inputs)

    if missing_inputs:
        return build_missing_inputs_tool_result_v1(
            tool_ref=TOOL_REF,
            missing_inputs=missing_inputs,
            owner_summary="Faltan datos explicitos para el calculo de caja.",
            inputs_used=inputs_used,
            limitations=list(_BASE_LIMITATIONS),
            technical_notes=list(_BASE_TECHNICAL_NOTES),
        )

    try:
        normalized_saldo_inicial = _normalize_number(
            field_name="saldo_inicial",
            value=saldo_inicial,
        )
        normalized_ingresos = _normalize_number(
            field_name="ingresos",
            value=ingresos,
        )
        normalized_egresos = _normalize_number(
            field_name="egresos",
            value=egresos,
        )
    except ValueError as exc:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[*list(_BASE_TECHNICAL_NOTES), str(exc)],
        )

    if normalized_ingresos < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "ingresos cannot be negative.",
            ],
        )

    if normalized_egresos < 0:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[
                *list(_BASE_TECHNICAL_NOTES),
                "egresos cannot be negative.",
            ],
        )

    flujo_neto = normalized_ingresos - normalized_egresos
    saldo_final_estimado = normalized_saldo_inicial + flujo_neto
    computed_results: dict[str, object] = {
        "flujo_neto": flujo_neto,
        "saldo_final_estimado": saldo_final_estimado,
    }

    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="OK",
        inputs_used=inputs_used,
        computed_results=computed_results,
        limitations=list(_BASE_LIMITATIONS),
        owner_summary="Calculo preliminar de caja diaria sobre saldo, ingresos y egresos declarados.",
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
