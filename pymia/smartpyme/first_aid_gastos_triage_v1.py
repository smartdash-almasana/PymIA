from __future__ import annotations

import math
from collections import defaultdict
from typing import Final

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FirstAidToolResultV1,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)

TOOL_REF: Final[str] = "gastos_triage"
REQUIRED_INPUTS: Final[tuple[str, str]] = ("concepto", "importe")

_BASE_LIMITATIONS: Final[tuple[str, ...]] = (
    "No clasifica gastos en forma contable definitiva.",
    "No clasifica gastos en forma fiscal definitiva.",
    "No audita gastos.",
    "No confirma rentabilidad.",
    "No reemplaza revision contable.",
)

_BASE_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Tool scope is limited to deterministic triage over explicit expense inputs.",
)


def run_gastos_triage_v1(
    *,
    concepto: object | None = None,
    importe: object | None = None,
    categoria: object | None = None,
) -> FirstAidToolResultV1:
    raw_inputs = {
        "concepto": concepto,
        "importe": importe,
        "categoria": categoria,
    }
    missing_inputs = [field for field in REQUIRED_INPUTS if raw_inputs[field] is None]
    inputs_used = _provided_inputs(raw_inputs)

    if missing_inputs:
        return build_missing_inputs_tool_result_v1(
            tool_ref=TOOL_REF,
            missing_inputs=missing_inputs,
            owner_summary="Faltan datos explicitos para ordenar gastos.",
            inputs_used=inputs_used,
            limitations=list(_BASE_LIMITATIONS),
            technical_notes=list(_BASE_TECHNICAL_NOTES),
        )

    try:
        normalized_rows = _normalize_expense_rows(
            concepto=concepto,
            importe=importe,
            categoria=categoria,
        )
    except ValueError as exc:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[*list(_BASE_TECHNICAL_NOTES), str(exc)],
        )

    total_gastos = sum(row["importe"] for row in normalized_rows)
    gastos_por_categoria = _totals_by_category(normalized_rows)
    gastos_sin_categoria = sum(1 for row in normalized_rows if row["categoria"] == "sin_categoria")

    computed_results: dict[str, object] = {
        "cantidad_gastos": len(normalized_rows),
        "total_gastos": total_gastos,
        "gastos_por_categoria": gastos_por_categoria,
        "gastos_sin_categoria": gastos_sin_categoria,
    }

    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="OK",
        inputs_used=inputs_used,
        computed_results=computed_results,
        limitations=list(_BASE_LIMITATIONS),
        owner_summary="Orden inicial de gastos sobre conceptos e importes declarados.",
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
        owner_summary="Los valores declarados no permiten ordenar gastos de forma prudente.",
        technical_notes=technical_notes,
    )


def _normalize_expense_rows(
    *,
    concepto: object | None,
    importe: object | None,
    categoria: object | None,
) -> list[dict[str, object]]:
    conceptos = _normalize_text_sequence(field_name="concepto", value=concepto)
    importes = _normalize_number_sequence(field_name="importe", value=importe)
    categorias = _normalize_optional_text_sequence(field_name="categoria", value=categoria, expected_len=len(conceptos))

    if len(conceptos) != len(importes):
        raise ValueError("concepto and importe must have the same length.")

    rows: list[dict[str, object]] = []
    for index, concepto_value in enumerate(conceptos):
        importe_value = importes[index]
        if importe_value < 0:
            raise ValueError("importe cannot be negative.")
        rows.append(
            {
                "concepto": concepto_value,
                "importe": importe_value,
                "categoria": categorias[index],
            }
        )
    return rows


def _normalize_text_sequence(*, field_name: str, value: object | None) -> list[str]:
    values = value if isinstance(value, (list, tuple)) else [value]
    normalized: list[str] = []
    for item in values:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must be text.")
        text = item.strip()
        if not text:
            raise ValueError(f"{field_name} cannot be empty.")
        normalized.append(text)
    return normalized


def _normalize_optional_text_sequence(
    *,
    field_name: str,
    value: object | None,
    expected_len: int,
) -> list[str]:
    if value is None:
        return ["sin_categoria"] * expected_len

    values = value if isinstance(value, (list, tuple)) else [value]
    if len(values) != expected_len:
        raise ValueError(f"{field_name} must have the same length as concepto.")

    normalized: list[str] = []
    for item in values:
        if item is None:
            normalized.append("sin_categoria")
            continue
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must be text.")
        text = item.strip()
        normalized.append(text or "sin_categoria")
    return normalized


def _normalize_number_sequence(*, field_name: str, value: object | None) -> list[float]:
    values = value if isinstance(value, (list, tuple)) else [value]
    normalized: list[float] = []
    for item in values:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"{field_name} must be numeric.")
        number = float(item)
        if not math.isfinite(number):
            raise ValueError(f"{field_name} must be finite.")
        normalized.append(number)
    return normalized


def _totals_by_category(rows: list[dict[str, object]]) -> dict[str, float]:
    totals: defaultdict[str, float] = defaultdict(float)
    for row in rows:
        totals[str(row["categoria"])] += float(row["importe"])
    return dict(totals)


def _provided_inputs(raw_inputs: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in raw_inputs.items() if value is not None}
