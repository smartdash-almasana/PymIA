"""Column confirmation contract for PymIA Excel ingestion.

This contract enforces that the mapper only suggests and the owner confirms.
Only confirmed columns may feed computed_variables calculations.

Statuses:
- PENDING_OWNER_CONFIRMATION: column may affect calculation, awaiting owner decision
- CONFIRMED: owner confirmed the role, safe to use in calculations
- IGNORED_NOT_RELEVANT: column does not affect calculations (informational)
- BLOCKED_AMBIGUOUS: column is ambiguous and cannot be safely classified

Calculation relevance:
- VENTAS, COSTOS, MARGEN, STOCK, PAGOS, CANTIDADES: feeds computed_variables
- SEGMENTATION: feeds grouping/segmentation (not aggregation)
- INFORMATIONAL: pure description, never feeds calculations
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ConfirmationStatus(str, Enum):
    PENDING_OWNER_CONFIRMATION = "PENDING_OWNER_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    IGNORED_NOT_RELEVANT = "IGNORED_NOT_RELEVANT"
    BLOCKED_AMBIGUOUS = "BLOCKED_AMBIGUOUS"


class CalculationRelevance(str, Enum):
    VENTAS = "VENTAS"
    COSTOS = "COSTOS"
    MARGEN = "MARGEN"
    STOCK = "STOCK"
    PAGOS = "PAGOS"
    CANTIDADES = "CANTIDADES"
    SEGMENTATION = "SEGMENTATION"
    INFORMATIONAL = "INFORMATIONAL"


# Labels that feed numerical aggregation in computed_variables
_CALCULATION_FEEDING_LABELS: dict[str, CalculationRelevance] = {
    "venta_total": CalculationRelevance.VENTAS,
    "precio_venta": CalculationRelevance.VENTAS,
    "costo_unitario": CalculationRelevance.COSTOS,
    "costo_total": CalculationRelevance.COSTOS,
    "margen": CalculationRelevance.MARGEN,
    "cantidad": CalculationRelevance.CANTIDADES,
    "stock": CalculationRelevance.STOCK,
    "stock_final": CalculationRelevance.STOCK,
    "pago": CalculationRelevance.PAGOS,
    "cobro": CalculationRelevance.PAGOS,
    "ingreso": CalculationRelevance.PAGOS,
    "egreso": CalculationRelevance.PAGOS,
    "saldo": CalculationRelevance.PAGOS,
    "gasto": CalculationRelevance.COSTOS,
    "impuesto": CalculationRelevance.COSTOS,
    "descuento": CalculationRelevance.VENTAS,
}

# Labels that are categorical/informational
_INFORMATIONAL_LABELS = {
    "producto",
    "sku",
    "cliente",
    "proveedor",
    "fecha",
    "moneda",
    "factura",
}

# Segmentation labels
_SEGMENTATION_LABELS = {
    "canal",
}


def infer_calculation_relevance(semantic_label: str) -> CalculationRelevance:
    if semantic_label in _CALCULATION_FEEDING_LABELS:
        return _CALCULATION_FEEDING_LABELS[semantic_label]
    if semantic_label in _SEGMENTATION_LABELS:
        return CalculationRelevance.SEGMENTATION
    if semantic_label in _INFORMATIONAL_LABELS:
        return CalculationRelevance.INFORMATIONAL
    return CalculationRelevance.INFORMATIONAL


class ColumnConfirmationEntry(BaseModel):
    original_column_name: str = Field(..., description="Nombre original de la columna en el Excel.")
    sheet_name: str = Field(..., description="Hoja de origen.")
    sample_values: list[Any] = Field(default_factory=list, description="Hasta 5 valores de muestra.")
    inferred_type: str = Field(default="unknown", description="Tipo inferido: number|text|date|mixed|empty.")
    suggested_semantic_role: str = Field(..., description="Sugerencia del mapper (puede ser 'unknown').")
    suggested_data_type: str = Field(default="unknown", description="Tipo sugerido: float|int|date|text.")
    calculation_relevance: CalculationRelevance = Field(
        default=CalculationRelevance.INFORMATIONAL,
        description="Cómo afecta esta columna a los cálculos.",
    )
    confidence: str = Field(default="unknown", description="mapped|ambiguous|unknown")
    owner_question: str | None = Field(default=None, description="Pregunta específica para el dueño.")
    owner_confirmed_role: str | None = Field(
        default=None,
        description="Rol confirmado por el dueño. None si aún no confirmó.",
    )
    confirmation_status: ConfirmationStatus = Field(
        default=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
        description="Estado actual de confirmación.",
    )

    def feeds_calculation(self) -> bool:
        """True if this column could affect computed_variables when confirmed."""
        return self.calculation_relevance not in {
            CalculationRelevance.INFORMATIONAL,
        }

    def is_actionable(self) -> bool:
        """True if the owner needs to answer something about this column."""
        return self.confirmation_status in {
            ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ConfirmationStatus.BLOCKED_AMBIGUOUS,
        }


class ColumnConfirmationMatrix(BaseModel):
    file_name: str = Field(..., description="Nombre del archivo auditado.")
    entries: list[ColumnConfirmationEntry] = Field(default_factory=list)

    def status(self) -> str:
        if not self.entries:
            return "no_columns"
        # BLOCKED_AMBIGUOUS takes precedence over PENDING_OWNER_CONFIRMATION
        if any(e.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS for e in self.entries):
            return "blocked"
        if any(e.is_actionable() and e.feeds_calculation() for e in self.entries):
            return "pending_confirmation"
        return "all_confirmed"

    def confirmed_entries(self) -> list[ColumnConfirmationEntry]:
        return [e for e in self.entries if e.confirmation_status == ConfirmationStatus.CONFIRMED]

    def pending_entries(self) -> list[ColumnConfirmationEntry]:
        return [e for e in self.entries if e.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION]

    def blocked_entries(self) -> list[ColumnConfirmationEntry]:
        return [e for e in self.entries if e.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS]

    def ignored_entries(self) -> list[ColumnConfirmationEntry]:
        return [e for e in self.entries if e.confirmation_status == ConfirmationStatus.IGNORED_NOT_RELEVANT]

    def actionable_for_calculation(self) -> list[ColumnConfirmationEntry]:
        """Entries that are pending/blocked AND could feed calculations."""
        return [e for e in self.entries if e.is_actionable() and e.feeds_calculation()]

    def can_compute_variable(self, variable_name: str) -> bool:
        """Returns True if the variable can be safely computed given current confirmations.

        Mapping of variable_name -> relevant semantic labels that feed it.
        """
        required_labels = _VARIABLE_REQUIRED_LABELS.get(variable_name, set())
        if not required_labels:
            return True

        for entry in self.entries:
            if entry.suggested_semantic_role in required_labels:
                if entry.confirmation_status != ConfirmationStatus.CONFIRMED:
                    return False
        return True

    def owner_questions(self) -> list[dict[str, str]]:
        questions: list[dict[str, str]] = []
        for entry in self.entries:
            if entry.owner_question and entry.is_actionable():
                questions.append({
                    "sheet": entry.sheet_name,
                    "column": entry.original_column_name,
                    "question": entry.owner_question,
                    "suggested_role": entry.suggested_semantic_role,
                    "relevance": entry.calculation_relevance.value,
                    "status": entry.confirmation_status.value,
                })
        return questions


# Variables computed in StructuredEvidenceExporter and the labels they depend on
_VARIABLE_REQUIRED_LABELS: dict[str, set[str]] = {
    "ventas_total": {"venta_total", "precio_venta", "cantidad"},
    "costos_total": {"costo_unitario", "cantidad", "costo_total"},
    "cantidad_total": {"cantidad"},
    "margen_bruto": {"margen", "venta_total", "precio_venta", "costo_unitario", "cantidad"},
    "margen_bruto_pct": {"margen", "venta_total", "precio_venta", "costo_unitario", "cantidad"},
}
