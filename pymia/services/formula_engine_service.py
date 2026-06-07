from __future__ import annotations

from pymia.contracts.formula_contract import (
    SUPPORTED_FORMULAS,
    FormulaInput,
    FormulaResult,
    FormulaStatus,
)


class FormulaEngineService:
    """Motor determinístico mínimo de fórmulas.

    No interpreta. No conversa. Solo calcula o bloquea con causa explícita.
    """

    def calculate(self, formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
        values = {input_item.name: input_item.value for input_item in inputs}
        source_refs = self._collect_source_refs(inputs)

        if formula_id not in SUPPORTED_FORMULAS:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason="FORMULA_NOT_SUPPORTED",
            )

        definition = SUPPORTED_FORMULAS[formula_id]
        missing = [name for name in definition.required_inputs if values.get(name) is None]
        if missing:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason=f"MISSING_INPUTS: {','.join(missing)}",
            )

        if formula_id == "margen_bruto":
            ventas = values["ventas"]
            costos = values["costos"]
            return self._calculate_margen_bruto(ventas, costos, values, source_refs)

        if formula_id == "ganancia_bruta":
            ventas = values["ventas"]
            costos = values["costos"]
            return self._ok(formula_id, ventas - costos, values, source_refs)

        if formula_id == "REN_001_margen_neto_real":
            return self._calculate_ren_001_margen_neto_real(values, source_refs)

        if formula_id == "LIQ_001_vendido_cobrado":
            sold_amount = values["sold_amount"]
            collected_amount = values["collected_amount"]
            return self._ok(formula_id, sold_amount - collected_amount, values, source_refs)

        if formula_id == "INV_002_rotacion_stock":
            return self._calculate_inv_002_rotacion_stock(values, source_refs)

        if formula_id == "PYME_011_dso":
            return self._calculate_pyme_011_dso(values, source_refs)

        if formula_id == "PYME_013_dso_dpo_gap":
            dso = values["dso"]
            dpo = values["dpo"]
            return self._ok(formula_id, dso - dpo, values, source_refs)

        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.BLOCKED,
            value=None,
            inputs=values,
            source_refs=source_refs,
            blocking_reason="FORMULA_NOT_IMPLEMENTED",
        )

    def _calculate_margen_bruto(
        self,
        ventas: float | int,
        costos: float | int,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "margen_bruto"
        if ventas == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: ventas",
            )

        return self._ok(formula_id, (ventas - costos) / ventas, inputs, source_refs)

    def _ok(
        self,
        formula_id: str,
        value: float | int,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.OK,
            value=float(value),
            inputs=inputs,
            source_refs=source_refs,
        )

    def _calculate_ren_001_margen_neto_real(
        self,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "REN_001_margen_neto_real"
        sale_price = inputs["sale_price"]
        costs = inputs["costs"]
        taxes = inputs["taxes"]

        if sale_price == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: sale_price",
            )

        value = ((sale_price - costs - taxes) / sale_price) * 100
        return self._ok(formula_id, value, inputs, source_refs)

    def _calculate_inv_002_rotacion_stock(
        self,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "INV_002_rotacion_stock"
        cost_of_goods_sold = inputs["cost_of_goods_sold"]
        average_stock = inputs["average_stock"]

        if average_stock == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: average_stock",
            )

        return self._ok(formula_id, cost_of_goods_sold / average_stock, inputs, source_refs)

    def _calculate_pyme_011_dso(
        self,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "PYME_011_dso"
        accounts_receivable = inputs["accounts_receivable"]
        sales = inputs["sales"]
        days = inputs["days"]

        if sales == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: sales",
            )

        return self._ok(formula_id, (accounts_receivable / sales) * days, inputs, source_refs)

    def _collect_source_refs(self, inputs: list[FormulaInput]) -> list[str]:
        refs: list[str] = []
        for input_item in inputs:
            refs.extend(input_item.source_refs)
        return refs
