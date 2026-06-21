"""Owner-facing rendering for column confirmation questions."""
from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
)

_RESPONSE_OPTIONS = (
    "1. Si, es correcto.",
    "2. No, significa otra cosa: ______",
    "3. No se.",
    "4. Ignorar esta columna.",
)


def render_column_confirmation_owner_view(matrix: ColumnConfirmationMatrix) -> str:
    """Render pending column-confirmation questions for the owner."""
    actionable_entries = [entry for entry in matrix.entries if entry.is_actionable()]

    if not actionable_entries:
        return _render_no_pending_confirmations(matrix.file_name)

    lines: list[str] = [
        "Confirmacion de columnas",
        "",
        f"Archivo: {matrix.file_name}",
        "",
        "Necesitamos confirmar el significado de algunas columnas antes de usarlas en el analisis.",
        "El mapper solo sugiere; el dueno confirma.",
        "",
    ]

    for index, entry in enumerate(actionable_entries, start=1):
        lines.extend(_render_entry(index, entry))
        lines.append("")

    lines.extend([
        "Opciones de respuesta permitidas:",
        *_RESPONSE_OPTIONS,
    ])

    return "\n".join(lines).rstrip() + "\n"


def _render_no_pending_confirmations(file_name: str) -> str:
    return "\n".join([
        "Confirmacion de columnas",
        "",
        f"Archivo: {file_name}",
        "",
        "No hay confirmaciones de columnas pendientes para el dueno.",
    ]) + "\n"


def _render_entry(index: int, entry: ColumnConfirmationEntry) -> list[str]:
    return [
        f"{index}. Hoja: {entry.sheet_name}",
        f"   Columna: {entry.original_column_name}",
        f"   Rol sugerido: {_humanize_role(entry.suggested_semantic_role, entry.original_column_name)}",
        f"   Relevancia: {_render_relevance(entry)}",
        f"   Pregunta: {_entry_question(entry)}",
    ]


def _entry_question(entry: ColumnConfirmationEntry) -> str:
    if entry.owner_question:
        return entry.owner_question
    return f'Que significa la columna "{entry.original_column_name}" en este archivo?'


def _render_relevance(entry: ColumnConfirmationEntry) -> str:
    if entry.calculation_relevance == CalculationRelevance.INFORMATIONAL:
        return "informativa; no bloquea ventas/margen, pero requiere confirmacion."
    return "computacional; puede bloquear calculos dependientes si no se confirma."


def _humanize_role(role: str, column_name: str) -> str:
    normalized_role = role.strip().lower()
    normalized_column = column_name.strip().lower()

    if normalized_role in {"payment_method", "metodo_pago", "metodopago"}:
        return "metodo o forma de pago"
    if normalized_column in {"metodopago", "metodo_pago"}:
        return "metodo o forma de pago"

    labels = {
        "venta_total": "importe total de venta",
        "precio_venta": "precio de venta",
        "costo_unitario": "costo unitario",
        "costo_total": "costo total",
        "cantidad": "cantidad",
        "producto": "producto",
        "fecha": "fecha",
        "unknown": "desconocido; requiere confirmacion del dueno",
    }
    return labels.get(normalized_role, role)
