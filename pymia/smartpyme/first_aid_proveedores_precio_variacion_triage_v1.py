from __future__ import annotations

import math
from collections import defaultdict
from typing import Final

from pymia.smartpyme.first_aid_tool_result_v1 import (
    FirstAidToolResultV1,
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)

TOOL_REF: Final[str] = "proveedores_precio_variacion_triage"
REQUIRED_INPUTS: Final[tuple[str, str, str]] = (
    "proveedor",
    "producto_o_insumo",
    "precio_o_costo",
)

_BASE_LIMITATIONS: Final[tuple[str, ...]] = (
    "No define estrategia de compras.",
    "No confirma rentabilidad por proveedor.",
    "No recomienda compra final.",
    "No audita proveedores.",
    "No reemplaza revision comercial ni contable.",
)

_BASE_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Tool scope is limited to deterministic supplier price variation triage over explicit inputs.",
)


def run_proveedores_precio_variacion_triage_v1(
    *,
    proveedor: object | None = None,
    producto_o_insumo: object | None = None,
    precio_o_costo: object | None = None,
) -> FirstAidToolResultV1:
    raw_inputs = {
        "proveedor": proveedor,
        "producto_o_insumo": producto_o_insumo,
        "precio_o_costo": precio_o_costo,
    }
    missing_inputs = [field for field in REQUIRED_INPUTS if raw_inputs[field] is None]
    inputs_used = _provided_inputs(raw_inputs)

    if missing_inputs:
        return build_missing_inputs_tool_result_v1(
            tool_ref=TOOL_REF,
            missing_inputs=missing_inputs,
            owner_summary="Faltan datos explicitos para revisar variaciones de proveedores.",
            inputs_used=inputs_used,
            limitations=list(_BASE_LIMITATIONS),
            technical_notes=list(_BASE_TECHNICAL_NOTES),
        )

    try:
        normalized_rows = _normalize_supplier_rows(
            proveedor=proveedor,
            producto_o_insumo=producto_o_insumo,
            precio_o_costo=precio_o_costo,
        )
    except ValueError as exc:
        return _build_invalid_input_result(
            inputs_used=inputs_used,
            technical_notes=[*list(_BASE_TECHNICAL_NOTES), str(exc)],
        )

    computed_results = _compute_supplier_variations(normalized_rows)

    return build_first_aid_tool_result_v1(
        tool_ref=TOOL_REF,
        status="OK",
        inputs_used=inputs_used,
        computed_results=computed_results,
        limitations=list(_BASE_LIMITATIONS),
        owner_summary="Revision inicial de precios declarados por proveedor y producto.",
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
        owner_summary="Los valores declarados no permiten revisar proveedores de forma prudente.",
        technical_notes=technical_notes,
    )


def _normalize_supplier_rows(
    *,
    proveedor: object | None,
    producto_o_insumo: object | None,
    precio_o_costo: object | None,
) -> list[dict[str, object]]:
    proveedores = _normalize_text_sequence(field_name="proveedor", value=proveedor)
    productos = _normalize_text_sequence(field_name="producto_o_insumo", value=producto_o_insumo)
    precios = _normalize_number_sequence(field_name="precio_o_costo", value=precio_o_costo)

    if not (len(proveedores) == len(productos) == len(precios)):
        raise ValueError("proveedor, producto_o_insumo and precio_o_costo must have the same length.")

    rows: list[dict[str, object]] = []
    for index, precio in enumerate(precios):
        if precio < 0:
            raise ValueError("precio_o_costo cannot be negative.")
        rows.append(
            {
                "proveedor": proveedores[index],
                "producto_o_insumo": productos[index],
                "precio_o_costo": precio,
            }
        )
    return rows


def _compute_supplier_variations(rows: list[dict[str, object]]) -> dict[str, object]:
    prices_by_product: defaultdict[str, list[float]] = defaultdict(list)
    suppliers_by_product: defaultdict[str, set[str]] = defaultdict(set)

    for row in rows:
        product = str(row["producto_o_insumo"])
        prices_by_product[product].append(float(row["precio_o_costo"]))
        suppliers_by_product[product].add(str(row["proveedor"]))

    product_variations: dict[str, dict[str, object]] = {}
    products_with_variation = 0

    for product, prices in prices_by_product.items():
        min_price = min(prices)
        max_price = max(prices)
        absolute_variation = max_price - min_price
        variation_percentage = None if min_price == 0 else absolute_variation / min_price
        if absolute_variation > 0:
            products_with_variation += 1
        product_variations[product] = {
            "min_price": min_price,
            "max_price": max_price,
            "absolute_variation": absolute_variation,
            "variation_percentage": variation_percentage,
            "supplier_count": len(suppliers_by_product[product]),
            "records_count": len(prices),
        }

    return {
        "cantidad_registros": len(rows),
        "cantidad_productos_o_insumos": len(prices_by_product),
        "productos_con_variacion_visible": products_with_variation,
        "variaciones_por_producto": product_variations,
    }


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


def _provided_inputs(raw_inputs: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in raw_inputs.items() if value is not None}
