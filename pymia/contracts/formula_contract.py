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
    "INV_001_punto_reposicion": FormulaDefinition(
        formula_id="INV_001_punto_reposicion",
        required_inputs=["average_sales", "lead_time", "safety_stock"],
        description="(average_sales * lead_time) + safety_stock",
    ),
    "PYME_011_dso": FormulaDefinition(
        formula_id="PYME_011_dso",
        required_inputs=["accounts_receivable", "sales", "days"],
        description="accounts_receivable / sales * days",
    ),
    "PYME_013_dso_dpo_gap": FormulaDefinition(
        formula_id="PYME_013_dso_dpo_gap",
        required_inputs=["dso", "dpo"],
        description="dso - dpo",
    ),
    "LIQ_002_saldo_final_proyectado": FormulaDefinition(
        formula_id="LIQ_002_saldo_final_proyectado",
        required_inputs=["initial_balance", "expected_collections", "expected_payments"],
        description="initial_balance + expected_collections - expected_payments",
    ),
    "PYME_024_liquidez_corriente": FormulaDefinition(
        formula_id="PYME_024_liquidez_corriente",
        required_inputs=["current_assets", "current_liabilities"],
        description="current_assets / current_liabilities",
    ),
    "PYME_017_pricing_drift": FormulaDefinition(
        formula_id="PYME_017_pricing_drift",
        required_inputs=["own_price", "market_price"],
        description="(own_price - market_price) / market_price * 100",
    ),
    "punto_equilibrio_ventas": FormulaDefinition(
        formula_id="punto_equilibrio_ventas",
        required_inputs=["fixed_costs", "contribution_margin_rate"],
        description="fixed_costs / contribution_margin_rate",
    ),
    "PYME_026_flujo_operativo": FormulaDefinition(
        formula_id="PYME_026_flujo_operativo",
        required_inputs=["net_income", "depreciation", "amortization", "working_capital_change"],
        description="net_income + depreciation + amortization - working_capital_change",
    ),
    "PYME_027_intereses_ebitda": FormulaDefinition(
        formula_id="PYME_027_intereses_ebitda",
        required_inputs=["interest_expense", "ebitda"],
        description="interest_expense / ebitda",
    ),
    "PYME_044_margen_cliente": FormulaDefinition(
        formula_id="PYME_044_margen_cliente",
        required_inputs=["client_revenue", "client_direct_costs", "client_service_costs"],
        description="client_revenue - client_direct_costs - client_service_costs",
    ),
}


def calculate_formula(formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
    from pymia.services.formula_engine_service import FormulaEngineService

    return FormulaEngineService().calculate(formula_id, inputs)
