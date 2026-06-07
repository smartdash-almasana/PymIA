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
