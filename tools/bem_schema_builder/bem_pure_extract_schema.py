from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]


def minimal_item_properties() -> JsonObject:
    return {
        "producto": {
            "type": "string",
            "description": "Nombre o descripcion del producto vendido o registrado.",
        },
        "cantidad": {
            "type": "number",
            "description": "Cantidad de unidades registradas en la fila.",
        },
        "venta_total": {
            "type": "number",
            "description": "Importe total de venta de la fila cuando exista en el documento.",
        },
    }


def full_item_properties() -> JsonObject:
    return {
        "fecha": {
            "type": "string",
            "description": "Fecha del registro comercial/operativo tal como aparece en el Excel.",
        },
        "factura": {
            "type": "string",
            "description": "Identificador de factura o comprobante del movimiento.",
        },
        "producto": {
            "type": "string",
            "description": "Nombre o descripcion del producto vendido o registrado.",
        },
        "sku": {
            "type": "string",
            "description": "Codigo SKU o codigo interno de producto cuando exista.",
        },
        "canal": {
            "type": "string",
            "description": "Canal de venta o de operacion asociado al registro.",
        },
        "cantidad": {
            "type": "number",
            "description": "Cantidad de unidades registradas en la fila.",
        },
        "precio_venta": {
            "type": "number",
            "description": "Precio de venta unitario observado en el documento.",
        },
        "costo_unitario": {
            "type": "number",
            "description": "Costo unitario del producto si esta presente en el Excel.",
        },
        "venta_total": {
            "type": "number",
            "description": "Importe total de venta de la fila cuando exista en el documento.",
        },
        "margen": {
            "type": "number",
            "description": "Margen reportado o calculado en la fila si el documento lo incluye.",
        },
        "moneda": {
            "type": "string",
            "description": "Moneda del registro (por ejemplo ARS, USD) cuando aparezca en el archivo.",
        },
    }


def _schema_from_item_properties(*, title: str, item_properties: JsonObject) -> JsonObject:
    schema: JsonObject = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": title,
        "type": "object",
        "description": "Schema de extraccion pura de datos tabulares desde Excel para flujo BEM.",
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "description": "Registros tabulares extraidos del Excel.",
                "items": {
                    "type": "object",
                    "description": "Fila extraida del Excel con campos economicos y operativos.",
                    "properties": item_properties,
                },
            }
        },
    }
    return schema


def build_pure_extract_schema(*, title: str = "PymIA Excel Extract Schema v1") -> JsonObject:
    return _schema_from_item_properties(title=title, item_properties=full_item_properties())


def build_minimal_extract_schema(*, title: str = "PymIA Minimal Excel Extract Schema v1") -> JsonObject:
    return _schema_from_item_properties(title=title, item_properties=minimal_item_properties())


def _write_schema(output_path: str | Path, schema: JsonObject) -> JsonObject:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    return schema


def build_pure_extract_schema_for_excel(excel_path: str | Path, output_path: str | Path) -> JsonObject:
    excel = Path(excel_path)
    title = f"PymIA Extract Schema for {excel.stem}"
    return _write_schema(output_path, build_pure_extract_schema(title=title))


def build_minimal_extract_schema_for_excel(excel_path: str | Path, output_path: str | Path) -> JsonObject:
    excel = Path(excel_path)
    title = f"PymIA Minimal Extract Schema for {excel.stem}"
    return _write_schema(output_path, build_minimal_extract_schema(title=title))
