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
