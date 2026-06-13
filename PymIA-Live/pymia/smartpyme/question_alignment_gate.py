from __future__ import annotations

from typing import Any

AXIS_CAJA_LIQUIDEZ = "caja_liquidez"
AXIS_VENTAS_MARGEN = "ventas_margen"
AXIS_STOCK_REPOSICION = "stock_reposicion"
AXIS_COSTOS_PROVEEDORES = "costos_proveedores"
AXIS_PRODUCCION = "produccion"
AXIS_RRHH = "rrhh"
AXIS_AUTOMATIZACION_MANUAL = "automatizacion_manual"
AXIS_DESCONOCIDO = "desconocido"

_OWNER_KEYWORDS: dict[str, list[str]] = {
    AXIS_CAJA_LIQUIDEZ: [
        "no me cierra la caja",
        "no tengo plata",
        "no me alcanza",
        "sin plata",
        "sin efectivo",
        "caja", "banco", "plata", "efectivo", "cobro", "cobranza",
        "pago", "pagar", "saldo", "liquidez", "disponible",
        "flujo", "descubierto", "cheque",
    ],
    AXIS_VENTAS_MARGEN: [
        "vendo pero no me queda",
        "vendo mucho",
        "vendo un monton",
        "no me queda margen",
        "vendo", "venta", "margen", "facturacion", "rentabilidad",
        "ganancia", "facturo", "precio",
    ],
    AXIS_STOCK_REPOSICION: [
        "stock", "inventario", "reposicion", "faltante",
        "merma", "rotura", "deposito",
    ],
    AXIS_COSTOS_PROVEEDORES: [
        "costo", "proveedor", "compra", "insumo", "materia prima",
        "cuenta por pagar", "proveedore",
    ],
    AXIS_PRODUCCION: [
        "produccion", "elaboracion", "fabrica", "planta",
        "proceso", "producir",
    ],
    AXIS_RRHH: [
        "sueldo", "empleado", "personal", "dotacion",
        "hora extra", "trabajador", "nomina",
    ],
    AXIS_AUTOMATIZACION_MANUAL: [
        "automatizacion", "planilla", "proceso manual",
        "carga manual", "automatizar",
    ],
}

_FORMULA_PREFIX_AXIS: dict[str, str] = {
    "LIQ": AXIS_CAJA_LIQUIDEZ,
    "INV": AXIS_STOCK_REPOSICION,
    "REN": AXIS_VENTAS_MARGEN,
}

_PATHOLOGY_AXIS: dict[str, str] = {
    "LIQ_001": AXIS_CAJA_LIQUIDEZ,
    "LIQ_002": AXIS_CAJA_LIQUIDEZ,
    "INV_001": AXIS_STOCK_REPOSICION,
    "INV_002": AXIS_STOCK_REPOSICION,
    "REN_001": AXIS_VENTAS_MARGEN,
    "REN_002": AXIS_VENTAS_MARGEN,
}


def detect_owner_axis(message: str) -> str:
    if not message or not message.strip():
        return AXIS_DESCONOCIDO
    msg_lower = message.lower()
    for axis, keywords in _OWNER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in msg_lower:
                return axis
    return AXIS_DESCONOCIDO


def detect_question_axis(entry: dict[str, Any]) -> str:
    formula_id = entry.get("formula_id", "") or ""
    pathology_code = entry.get("pathology_code", "") or ""
    if pathology_code in _PATHOLOGY_AXIS:
        return _PATHOLOGY_AXIS[pathology_code]
    if "_" in formula_id:
        prefix = formula_id.split("_")[0]
        if prefix in _FORMULA_PREFIX_AXIS:
            return _FORMULA_PREFIX_AXIS[prefix]
    return AXIS_DESCONOCIDO


def _get_question_text(entry: dict[str, Any]) -> str:
    questions = entry.get("next_audit_questions") or []
    return str(questions[0]) if questions else ""


def align_next_question(
    owner_message: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    if not candidates:
        return {
            "status": "UNKNOWN",
            "declared_axis": detect_owner_axis(owner_message),
            "question_axis": AXIS_DESCONOCIDO,
            "final_question_text": "",
            "technical_reference": "sin candidatos para evaluar",
        }
    owner_axis = detect_owner_axis(owner_message)
    target_entry = candidates[0]
    question_axis = detect_question_axis(target_entry)
    question_text = _get_question_text(target_entry)
    formula_id = target_entry.get("formula_id", "") or ""
    if not owner_message or not owner_message.strip():
        status = "UNKNOWN"
    elif owner_axis == AXIS_DESCONOCIDO:
        status = "UNKNOWN"
    elif owner_axis == AXIS_CAJA_LIQUIDEZ and question_axis == AXIS_STOCK_REPOSICION:
        status = "MISALIGNED"
    else:
        status = "ALIGNED"
    return {
        "status": status,
        "declared_axis": owner_axis,
        "question_axis": question_axis,
        "final_question_text": question_text,
        "technical_reference": formula_id if formula_id else "",
    }


__all__ = [
    "AXIS_CAJA_LIQUIDEZ",
    "AXIS_VENTAS_MARGEN",
    "AXIS_STOCK_REPOSICION",
    "AXIS_COSTOS_PROVEEDORES",
    "AXIS_PRODUCCION",
    "AXIS_RRHH",
    "AXIS_AUTOMATIZACION_MANUAL",
    "AXIS_DESCONOCIDO",
    "detect_owner_axis",
    "detect_question_axis",
    "align_next_question",
]
