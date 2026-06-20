from __future__ import annotations

from typing import Literal, TypedDict

from pymia.smartpyme.first_aid_toolbox_selector import FirstAidToolboxSelection

FirstAidToolboxOwnerOutputStatus = Literal[
    "PRESENT_TOOLBOX_OPTIONS",
    "REQUEST_EVIDENCE_BEFORE_TOOLBOX",
    "REDIRECT_BEFORE_TOOLBOX",
]


class FirstAidToolboxOwnerOption(TypedDict):
    option_id: str
    title: str
    description: str
    limit: str


class FirstAidToolboxOwnerOutput(TypedDict):
    status: FirstAidToolboxOwnerOutputStatus
    message: str
    options: list[FirstAidToolboxOwnerOption]
    next_question: str
    limits: list[str]
    warnings: list[str]


def build_first_aid_toolbox_owner_view(*, selection: FirstAidToolboxSelection) -> FirstAidToolboxOwnerOutput:
    """Translate a toolbox selection into safe owner-facing options.

    This helper is pure presentation logic. It does not execute selected components,
    calculate formulas, diagnose, read files, persist data, or call pipelines.
    """
    _validate_selection(selection)

    if selection["status"] == "TOOLBOX_SELECTION_READY":
        return {
            "status": "PRESENT_TOOLBOX_OPTIONS",
            "message": "Con tu fuente puedo hacer una primera revisión limitada. Estas son las opciones disponibles:",
            "options": _owner_options_from_selection(selection),
            "next_question": "¿Con cuál de estas opciones querés empezar?",
            "limits": _global_limits(),
            "warnings": [],
        }

    if selection["status"] == "TOOLBOX_SELECTION_NEEDS_EVIDENCE":
        return {
            "status": "REQUEST_EVIDENCE_BEFORE_TOOLBOX",
            "message": "Antes de elegir una opción necesito una fuente mínima para revisar.",
            "options": [],
            "next_question": "¿Qué archivo, planilla o fuente querés que revisemos primero?",
            "limits": _global_limits(),
            "warnings": list(selection.get("warnings") or []),
        }

    return {
        "status": "REDIRECT_BEFORE_TOOLBOX",
        "message": "Este pedido necesita más contexto antes de elegir una opción de revisión inicial.",
        "options": [],
        "next_question": "¿Cuál es el problema principal que querés ordenar primero?",
        "limits": _global_limits(),
        "warnings": list(selection.get("warnings") or []),
    }


def _owner_options_from_selection(selection: FirstAidToolboxSelection) -> list[FirstAidToolboxOwnerOption]:
    composition_ids = {composition["id"] for composition in selection["compositions"]}
    options: list[FirstAidToolboxOwnerOption] = []

    for option_id, option in _KNOWN_OWNER_OPTIONS.items():
        if option_id in composition_ids:
            options.append(option)

    return options


def _global_limits() -> list[str]:
    return [
        "Es una revisión inicial, no reemplaza una evaluación completa.",
        "Sólo se trabaja con la evidencia disponible.",
        "Si falta evidencia, se marcará como no determinable.",
        "No valida resultados contables, deuda real, stock físico ni causa raíz.",
    ]


_KNOWN_OWNER_OPTIONS: dict[str, FirstAidToolboxOwnerOption] = {
    "excel_triage_basic": {
        "option_id": "excel_triage_basic",
        "title": "Ordenar archivo y datos básicos",
        "description": "Revisar estructura, datos visibles, faltantes y cálculos básicos posibles con la fuente entregada.",
        "limit": "No valida la verdad del negocio ni convierte una planilla desordenada en diagnóstico.",
    },
    "cash_ordering_basic": {
        "option_id": "cash_ordering_basic",
        "title": "Ordenar caja declarada",
        "description": "Separar ingresos, egresos, saldos declarados y movimientos visibles.",
        "limit": "No confirma caja real ni conciliación bancaria.",
    },
    "price_margin_basic": {
        "option_id": "price_margin_basic",
        "title": "Revisar precio y margen básico",
        "description": "Calcular señales básicas de precio, costo declarado y margen bruto con los datos disponibles.",
        "limit": "No define precio óptimo ni rentabilidad real.",
    },
    "operational_alert_basic": {
        "option_id": "operational_alert_basic",
        "title": "Armar alerta operativa breve",
        "description": "Transformar señales visibles en una alerta corta, con límite y próximo paso.",
        "limit": "No explica causa raíz ni reemplaza un análisis completo.",
    },
    "stock_minimal_alert": {
        "option_id": "stock_minimal_alert",
        "title": "Marcar alerta mínima de stock",
        "description": "Señalar faltantes o desvíos visibles si la fuente tiene datos suficientes.",
        "limit": "No confirma stock físico, rotación ni causa de merma.",
    },
}


def _validate_selection(selection: FirstAidToolboxSelection) -> None:
    if not isinstance(selection, dict):
        raise ValueError("selection must be a dict")
    status = selection.get("status")
    if status not in {
        "TOOLBOX_SELECTION_READY",
        "TOOLBOX_SELECTION_NEEDS_EVIDENCE",
        "TOOLBOX_SELECTION_NOT_ALLOWED",
    }:
        raise ValueError("selection.status is unsupported")


__all__ = [
    "FirstAidToolboxOwnerOption",
    "FirstAidToolboxOwnerOutput",
    "FirstAidToolboxOwnerOutputStatus",
    "build_first_aid_toolbox_owner_view",
]
