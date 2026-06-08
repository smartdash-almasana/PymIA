from pymia.contracts.formula_contract import FormulaInput, FormulaStatus, calculate_formula
from pymia.services.formula_engine_service import FormulaEngineService


def test_engine_calculates_margen_bruto():
    result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=750, source_refs=["costos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.25
    assert result.source_refs == ["ventas:1", "costos:1"]


def test_engine_calculates_ganancia_bruta():
    result = FormulaEngineService().calculate(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 250.0


def test_engine_blocks_division_by_zero():
    result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: ventas"


def test_contract_compatibility_wrapper():
    result = calculate_formula(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 250.0


def test_engine_calculates_ren001_margen_neto_real():
    result = FormulaEngineService().calculate(
        "REN_001_margen_neto_real",
        [
            FormulaInput(name="sale_price", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costs", value=700, source_refs=["costos:1"]),
            FormulaInput(name="taxes", value=50, source_refs=["impuestos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 25.0
    assert result.source_refs == ["ventas:1", "costos:1", "impuestos:1"]


def test_engine_blocks_ren001_division_by_zero():
    result = FormulaEngineService().calculate(
        "REN_001_margen_neto_real",
        [
            FormulaInput(name="sale_price", value=0),
            FormulaInput(name="costs", value=700),
            FormulaInput(name="taxes", value=50),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: sale_price"


def test_engine_blocks_ren001_when_taxes_input_is_missing():
    result = FormulaEngineService().calculate(
        "REN_001_margen_neto_real",
        [
            FormulaInput(name="sale_price", value=1000),
            FormulaInput(name="costs", value=700),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: taxes"


def test_engine_calculates_liq001_vendido_cobrado():
    result = FormulaEngineService().calculate(
        "LIQ_001_vendido_cobrado",
        [
            FormulaInput(name="sold_amount", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="collected_amount", value=650, source_refs=["cobranzas:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 350.0
    assert result.source_refs == ["ventas:1", "cobranzas:1"]


def test_engine_blocks_liq001_when_collected_amount_is_missing():
    result = FormulaEngineService().calculate(
        "LIQ_001_vendido_cobrado",
        [
            FormulaInput(name="sold_amount", value=1000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: collected_amount"


def test_engine_allows_liq001_zero_result():
    result = FormulaEngineService().calculate(
        "LIQ_001_vendido_cobrado",
        [
            FormulaInput(name="sold_amount", value=1000),
            FormulaInput(name="collected_amount", value=1000),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_calculates_inv002_rotacion_stock():
    result = FormulaEngineService().calculate(
        "INV_002_rotacion_stock",
        [
            FormulaInput(name="cost_of_goods_sold", value=12000, source_refs=["cogs:1"]),
            FormulaInput(name="average_stock", value=3000, source_refs=["stock:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 4.0
    assert result.source_refs == ["cogs:1", "stock:1"]


def test_engine_blocks_inv002_when_average_stock_is_missing():
    result = FormulaEngineService().calculate(
        "INV_002_rotacion_stock",
        [
            FormulaInput(name="cost_of_goods_sold", value=12000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: average_stock"


def test_engine_blocks_inv002_division_by_zero():
    result = FormulaEngineService().calculate(
        "INV_002_rotacion_stock",
        [
            FormulaInput(name="cost_of_goods_sold", value=12000),
            FormulaInput(name="average_stock", value=0),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: average_stock"


def test_engine_calculates_inv001_punto_reposicion():
    result = FormulaEngineService().calculate(
        "INV_001_punto_reposicion",
        [
            FormulaInput(name="average_sales", value=20, source_refs=["avg_sales:1"]),
            FormulaInput(name="lead_time", value=5, source_refs=["lead_time:1"]),
            FormulaInput(name="safety_stock", value=30, source_refs=["safety_stock:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 130.0
    assert result.source_refs == ["avg_sales:1", "lead_time:1", "safety_stock:1"]


def test_engine_blocks_inv001_when_safety_stock_is_missing():
    result = FormulaEngineService().calculate(
        "INV_001_punto_reposicion",
        [
            FormulaInput(name="average_sales", value=20),
            FormulaInput(name="lead_time", value=5),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: safety_stock"


def test_engine_allows_inv001_zero_result():
    result = FormulaEngineService().calculate(
        "INV_001_punto_reposicion",
        [
            FormulaInput(name="average_sales", value=0),
            FormulaInput(name="lead_time", value=5),
            FormulaInput(name="safety_stock", value=0),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_allows_inv001_decimal_input():
    result = FormulaEngineService().calculate(
        "INV_001_punto_reposicion",
        [
            FormulaInput(name="average_sales", value=12.5),
            FormulaInput(name="lead_time", value=4),
            FormulaInput(name="safety_stock", value=10),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 60.0


def test_engine_calculates_pyme011_dso():
    result = FormulaEngineService().calculate(
        "PYME_011_dso",
        [
            FormulaInput(name="accounts_receivable", value=3000, source_refs=["ar:1"]),
            FormulaInput(name="sales", value=12000, source_refs=["sales:1"]),
            FormulaInput(name="days", value=30, source_refs=["days:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 7.5
    assert result.source_refs == ["ar:1", "sales:1", "days:1"]


def test_engine_blocks_pyme011_when_days_is_missing():
    result = FormulaEngineService().calculate(
        "PYME_011_dso",
        [
            FormulaInput(name="accounts_receivable", value=3000),
            FormulaInput(name="sales", value=12000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: days"


def test_engine_blocks_pyme011_division_by_zero():
    result = FormulaEngineService().calculate(
        "PYME_011_dso",
        [
            FormulaInput(name="accounts_receivable", value=3000),
            FormulaInput(name="sales", value=0),
            FormulaInput(name="days", value=30),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: sales"


def test_engine_calculates_pyme013_dso_dpo_gap():
    result = FormulaEngineService().calculate(
        "PYME_013_dso_dpo_gap",
        [
            FormulaInput(name="dso", value=45, source_refs=["dso:1"]),
            FormulaInput(name="dpo", value=30, source_refs=["dpo:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 15.0
    assert result.source_refs == ["dso:1", "dpo:1"]


def test_engine_allows_pyme013_zero_result():
    result = FormulaEngineService().calculate(
        "PYME_013_dso_dpo_gap",
        [
            FormulaInput(name="dso", value=30),
            FormulaInput(name="dpo", value=30),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_allows_pyme013_negative_result():
    result = FormulaEngineService().calculate(
        "PYME_013_dso_dpo_gap",
        [
            FormulaInput(name="dso", value=25),
            FormulaInput(name="dpo", value=40),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == -15.0


def test_engine_blocks_pyme013_when_dpo_is_missing():
    result = FormulaEngineService().calculate(
        "PYME_013_dso_dpo_gap",
        [
            FormulaInput(name="dso", value=45),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: dpo"


def test_engine_calculates_liq002_saldo_final_proyectado():
    result = FormulaEngineService().calculate(
        "LIQ_002_saldo_final_proyectado",
        [
            FormulaInput(name="initial_balance", value=5000, source_refs=["saldo:1"]),
            FormulaInput(name="expected_collections", value=2000, source_refs=["cobranzas:1"]),
            FormulaInput(name="expected_payments", value=3000, source_refs=["pagos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 4000.0
    assert result.source_refs == ["saldo:1", "cobranzas:1", "pagos:1"]


def test_engine_blocks_liq002_when_expected_payments_is_missing():
    result = FormulaEngineService().calculate(
        "LIQ_002_saldo_final_proyectado",
        [
            FormulaInput(name="initial_balance", value=5000),
            FormulaInput(name="expected_collections", value=2000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: expected_payments"


def test_engine_allows_liq002_zero_result():
    result = FormulaEngineService().calculate(
        "LIQ_002_saldo_final_proyectado",
        [
            FormulaInput(name="initial_balance", value=1000),
            FormulaInput(name="expected_collections", value=3000),
            FormulaInput(name="expected_payments", value=4000),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_allows_liq002_negative_result():
    result = FormulaEngineService().calculate(
        "LIQ_002_saldo_final_proyectado",
        [
            FormulaInput(name="initial_balance", value=1000),
            FormulaInput(name="expected_collections", value=2000),
            FormulaInput(name="expected_payments", value=4000),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == -1000.0


def test_engine_calculates_pyme024_liquidez_corriente():
    result = FormulaEngineService().calculate(
        "PYME_024_liquidez_corriente",
        [
            FormulaInput(name="current_assets", value=15000, source_refs=["assets:1"]),
            FormulaInput(name="current_liabilities", value=10000, source_refs=["liabilities:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 1.5
    assert result.source_refs == ["assets:1", "liabilities:1"]


def test_engine_blocks_pyme024_when_current_liabilities_is_missing():
    result = FormulaEngineService().calculate(
        "PYME_024_liquidez_corriente",
        [
            FormulaInput(name="current_assets", value=15000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: current_liabilities"


def test_engine_blocks_pyme024_division_by_zero():
    result = FormulaEngineService().calculate(
        "PYME_024_liquidez_corriente",
        [
            FormulaInput(name="current_assets", value=15000),
            FormulaInput(name="current_liabilities", value=0),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: current_liabilities"


def test_engine_calculates_pyme017_pricing_drift_positive():
    result = FormulaEngineService().calculate(
        "PYME_017_pricing_drift",
        [
            FormulaInput(name="own_price", value=120, source_refs=["own:1"]),
            FormulaInput(name="market_price", value=100, source_refs=["market:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 20.0
    assert result.source_refs == ["own:1", "market:1"]


def test_engine_allows_pyme017_zero_result():
    result = FormulaEngineService().calculate(
        "PYME_017_pricing_drift",
        [
            FormulaInput(name="own_price", value=100),
            FormulaInput(name="market_price", value=100),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_allows_pyme017_negative_result():
    result = FormulaEngineService().calculate(
        "PYME_017_pricing_drift",
        [
            FormulaInput(name="own_price", value=90),
            FormulaInput(name="market_price", value=100),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == -10.0


def test_engine_blocks_pyme017_when_market_price_is_missing():
    result = FormulaEngineService().calculate(
        "PYME_017_pricing_drift",
        [
            FormulaInput(name="own_price", value=120),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: market_price"


def test_engine_blocks_pyme017_division_by_zero():
    result = FormulaEngineService().calculate(
        "PYME_017_pricing_drift",
        [
            FormulaInput(name="own_price", value=120),
            FormulaInput(name="market_price", value=0),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: market_price"


def test_engine_calculates_punto_equilibrio_ventas():
    result = FormulaEngineService().calculate(
        "punto_equilibrio_ventas",
        [
            FormulaInput(name="fixed_costs", value=5000, source_refs=["fixed:1"]),
            FormulaInput(name="contribution_margin_rate", value=0.25, source_refs=["cmr:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 20000.0
    assert result.source_refs == ["fixed:1", "cmr:1"]


def test_engine_blocks_punto_equilibrio_ventas_when_contribution_margin_rate_is_missing():
    result = FormulaEngineService().calculate(
        "punto_equilibrio_ventas",
        [
            FormulaInput(name="fixed_costs", value=5000),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: contribution_margin_rate"


def test_engine_blocks_punto_equilibrio_ventas_division_by_zero():
    result = FormulaEngineService().calculate(
        "punto_equilibrio_ventas",
        [
            FormulaInput(name="fixed_costs", value=5000),
            FormulaInput(name="contribution_margin_rate", value=0),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: contribution_margin_rate"


def test_engine_blocks_punto_equilibrio_ventas_negative_margin():
    result = FormulaEngineService().calculate(
        "punto_equilibrio_ventas",
        [
            FormulaInput(name="fixed_costs", value=10000),
            FormulaInput(name="contribution_margin_rate", value=-0.1),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "INVALID_INPUT: contribution_margin_rate"


def test_engine_allows_punto_equilibrio_ventas_zero_fixed_costs():
    result = FormulaEngineService().calculate(
        "punto_equilibrio_ventas",
        [
            FormulaInput(name="fixed_costs", value=0),
            FormulaInput(name="contribution_margin_rate", value=0.25),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.0


def test_engine_calculates_pyme026_flujo_operativo():
    result = FormulaEngineService().calculate(
        "PYME_026_flujo_operativo",
        [
            FormulaInput(name="net_income", value=1000, source_refs=["ni:1"]),
            FormulaInput(name="depreciation", value=200, source_refs=["dep:1"]),
            FormulaInput(name="amortization", value=50, source_refs=["amort:1"]),
            FormulaInput(name="working_capital_change", value=150, source_refs=["wcc:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 1100.0
    assert result.source_refs == ["ni:1", "dep:1", "amort:1", "wcc:1"]


def test_engine_blocks_pyme026_when_working_capital_change_is_missing():
    result = FormulaEngineService().calculate(
        "PYME_026_flujo_operativo",
        [
            FormulaInput(name="net_income", value=1000),
            FormulaInput(name="depreciation", value=200),
            FormulaInput(name="amortization", value=50),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "MISSING_INPUTS: working_capital_change"


def test_engine_allows_pyme026_negative_result():
    result = FormulaEngineService().calculate(
        "PYME_026_flujo_operativo",
        [
            FormulaInput(name="net_income", value=-500),
            FormulaInput(name="depreciation", value=100),
            FormulaInput(name="amortization", value=50),
            FormulaInput(name="working_capital_change", value=200),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == -550.0
