from __future__ import annotations

from pymia.contracts.formula_contract import FormulaInput, FormulaStatus
from pymia.services.formula_engine_service import FormulaEngineService


def _engine() -> FormulaEngineService:
    return FormulaEngineService()


def _input(name: str, value: float | int) -> FormulaInput:
    return FormulaInput(name=name, value=value)


# --- Not supported ---

def test_unknown_formula_returns_not_supported():
    result = _engine().calculate("unknown_formula", [_input("x", 1)])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "FORMULA_NOT_SUPPORTED"


# --- OK results for all 17 formulas ---

def test_margen_bruto_ok():
    result = _engine().calculate("margen_bruto", [_input("ventas", 100), _input("costos", 60)])
    assert result.status == FormulaStatus.OK
    assert result.value == 0.4


def test_ganancia_bruta_ok():
    result = _engine().calculate("ganancia_bruta", [_input("ventas", 100), _input("costos", 60)])
    assert result.status == FormulaStatus.OK
    assert result.value == 40.0


def test_ren_001_margen_neto_real_ok():
    result = _engine().calculate("REN_001_margen_neto_real", [
        _input("sale_price", 1000),
        _input("costs", 600),
        _input("taxes", 100),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 30.0


def test_liq_001_vendido_cobrado_ok():
    result = _engine().calculate("LIQ_001_vendido_cobrado", [
        _input("sold_amount", 5000),
        _input("collected_amount", 3000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 2000.0


def test_inv_002_rotacion_stock_ok():
    result = _engine().calculate("INV_002_rotacion_stock", [
        _input("cost_of_goods_sold", 10000),
        _input("average_stock", 2000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 5.0


def test_inv_001_punto_reposicion_ok():
    result = _engine().calculate("INV_001_punto_reposicion", [
        _input("average_sales", 50),
        _input("lead_time", 7),
        _input("safety_stock", 100),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 450.0


def test_pyme_011_dso_ok():
    result = _engine().calculate("PYME_011_dso", [
        _input("accounts_receivable", 50000),
        _input("sales", 200000),
        _input("days", 365),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 91.25


def test_pyme_013_dso_dpo_gap_ok():
    result = _engine().calculate("PYME_013_dso_dpo_gap", [
        _input("dso", 45),
        _input("dpo", 30),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 15.0


def test_liq_002_saldo_final_proyectado_ok():
    result = _engine().calculate("LIQ_002_saldo_final_proyectado", [
        _input("initial_balance", 10000),
        _input("expected_collections", 5000),
        _input("expected_payments", 3000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 12000.0


def test_pyme_024_liquidez_corriente_ok():
    result = _engine().calculate("PYME_024_liquidez_corriente", [
        _input("current_assets", 200000),
        _input("current_liabilities", 100000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 2.0


def test_pyme_017_pricing_drift_ok():
    result = _engine().calculate("PYME_017_pricing_drift", [
        _input("own_price", 110),
        _input("market_price", 100),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 10.0


def test_punto_equilibrio_ventas_ok():
    result = _engine().calculate("punto_equilibrio_ventas", [
        _input("fixed_costs", 50000),
        _input("contribution_margin_rate", 0.25),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 200000.0


def test_pyme_026_flujo_operativo_ok():
    result = _engine().calculate("PYME_026_flujo_operativo", [
        _input("net_income", 100000),
        _input("depreciation", 20000),
        _input("amortization", 5000),
        _input("working_capital_change", 15000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 110000.0


def test_pyme_027_intereses_ebitda_ok():
    result = _engine().calculate("PYME_027_intereses_ebitda", [
        _input("interest_expense", 5000),
        _input("ebitda", 100000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 0.05


def test_pyme_044_margen_cliente_ok():
    result = _engine().calculate("PYME_044_margen_cliente", [
        _input("client_revenue", 50000),
        _input("client_direct_costs", 20000),
        _input("client_service_costs", 5000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 25000.0


def test_pyme_033_concentracion_sku_ok():
    result = _engine().calculate("PYME_033_concentracion_sku", [
        _input("main_sku_sales", 30000),
        _input("total_sales", 100000),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 30.0


def test_ren_002_coeficiente_reposicion_ok():
    result = _engine().calculate("REN_002_coeficiente_reposicion", [
        _input("closing_index", 1.5),
        _input("origin_index", 1.0),
    ])
    assert result.status == FormulaStatus.OK
    assert result.value == 1.5


# --- Blocked: DIVISION_BY_ZERO ---

def test_margen_bruto_blocked_division_by_zero():
    result = _engine().calculate("margen_bruto", [_input("ventas", 0), _input("costos", 60)])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: ventas"


def test_ren_001_margen_neto_real_blocked_division_by_zero():
    result = _engine().calculate("REN_001_margen_neto_real", [
        _input("sale_price", 0),
        _input("costs", 600),
        _input("taxes", 100),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: sale_price"


def test_inv_002_rotacion_stock_blocked_division_by_zero():
    result = _engine().calculate("INV_002_rotacion_stock", [
        _input("cost_of_goods_sold", 10000),
        _input("average_stock", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: average_stock"


def test_pyme_011_dso_blocked_division_by_zero():
    result = _engine().calculate("PYME_011_dso", [
        _input("accounts_receivable", 50000),
        _input("sales", 0),
        _input("days", 365),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: sales"


def test_pyme_024_liquidez_corriente_blocked_division_by_zero():
    result = _engine().calculate("PYME_024_liquidez_corriente", [
        _input("current_assets", 200000),
        _input("current_liabilities", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: current_liabilities"


def test_pyme_017_pricing_drift_blocked_division_by_zero():
    result = _engine().calculate("PYME_017_pricing_drift", [
        _input("own_price", 110),
        _input("market_price", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: market_price"


def test_punto_equilibrio_ventas_blocked_division_by_zero():
    result = _engine().calculate("punto_equilibrio_ventas", [
        _input("fixed_costs", 50000),
        _input("contribution_margin_rate", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: contribution_margin_rate"


def test_pyme_027_intereses_ebitda_blocked_division_by_zero():
    result = _engine().calculate("PYME_027_intereses_ebitda", [
        _input("interest_expense", 5000),
        _input("ebitda", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: ebitda"


def test_pyme_033_concentracion_sku_blocked_division_by_zero():
    result = _engine().calculate("PYME_033_concentracion_sku", [
        _input("main_sku_sales", 30000),
        _input("total_sales", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: total_sales"


def test_ren_002_coeficiente_reposicion_blocked_division_by_zero():
    result = _engine().calculate("REN_002_coeficiente_reposicion", [
        _input("closing_index", 1.5),
        _input("origin_index", 0),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: origin_index"


# --- Blocked: INVALID_INPUT ---

def test_punto_equilibrio_ventas_blocked_negative_rate():
    result = _engine().calculate("punto_equilibrio_ventas", [
        _input("fixed_costs", 50000),
        _input("contribution_margin_rate", -0.1),
    ])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "INVALID_INPUT: contribution_margin_rate"


# --- Blocked: MISSING_INPUTS ---

def test_missing_input_blocks_formula():
    result = _engine().calculate("margen_bruto", [_input("ventas", 100)])
    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert "MISSING_INPUTS: costos" in result.blocking_reason
