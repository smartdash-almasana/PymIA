from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class FormulaStatus(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"


class FormulaInput(BaseModel):
    name: str
    value: float | int | None
    source_refs: list[str] = Field(default_factory=list)


class FormulaDefinition(BaseModel):
    formula_id: str
    required_inputs: list[str]
    description: str


class FormulaResult(BaseModel):
    formula_id: str
    status: FormulaStatus
    value: float | None
    inputs: dict[str, float | int | None]
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


SUPPORTED_FORMULAS: dict[str, FormulaDefinition] = {
    "margen_bruto": FormulaDefinition(
        formula_id="margen_bruto",
        required_inputs=["ventas", "costos"],
        description="(ventas - costos) / ventas",
    ),
    "ganancia_bruta": FormulaDefinition(
        formula_id="ganancia_bruta",
        required_inputs=["ventas", "costos"],
        description="ventas - costos",
    ),
    "REN_001_margen_neto_real": FormulaDefinition(
        formula_id="REN_001_margen_neto_real",
        required_inputs=["sale_price", "costs", "taxes"],
        description="((sale_price - costs - taxes) / sale_price) * 100",
    ),
    "LIQ_001_vendido_cobrado": FormulaDefinition(
        formula_id="LIQ_001_vendido_cobrado",
        required_inputs=["sold_amount", "collected_amount"],
        description="sold_amount - collected_amount",
    ),
    "INV_002_rotacion_stock": FormulaDefinition(
        formula_id="INV_002_rotacion_stock",
        required_inputs=["cost_of_goods_sold", "average_stock"],
        description="cost_of_goods_sold / average_stock",
    ),
}


def calculate_formula(formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
    from pymia.services.formula_engine_service import FormulaEngineService

    return FormulaEngineService().calculate(formula_id, inputs)
