from __future__ import annotations

import math

from pymia.contracts.formula_contract import (
    SUPPORTED_FORMULAS,
    FormulaInput,
    FormulaResult,
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
    MathPrimitiveResult,
)


class FormulaEngineService:
    """Motor determinístico mínimo de fórmulas y primitivas matemáticas.

    No interpreta. No conversa. Solo calcula o bloquea con causa explícita.
    """

    def calculate_math_primitive(self, item: MathPrimitiveInput) -> MathPrimitiveResult:
        """Execute a generic mathematical primitive without business semantics."""
        if not isinstance(item, MathPrimitiveInput):
            raise TypeError("item must be MathPrimitiveInput")
        values = [float(value) for value in item.values]
        paired = [float(value) for value in item.paired_values]
        refs = list(dict.fromkeys(str(ref).strip() for ref in item.source_refs if str(ref).strip()))
        if any(not math.isfinite(value) for value in (*values, *paired)):
            return MathPrimitiveResult(
                operation=item.operation,
                status=FormulaStatus.BLOCKED,
                value=None,
                source_refs=refs,
                blocking_reason="NON_FINITE_INPUT",
            )

        operation = item.operation
        if operation is not MathPrimitiveOperation.SUM_PRODUCT and paired:
            return self._math_blocked(item, refs, "UNEXPECTED_PAIRED_VALUES")
        if operation is MathPrimitiveOperation.SINGLE_VALUE:
            if not values:
                return self._math_blocked(item, refs, "EMPTY_INPUT")
            unique = set(values)
            if len(unique) != 1:
                return self._math_blocked(item, refs, "MULTIPLE_DISTINCT_VALUES")
            return self._math_ok(item, values[0], refs, value_count=len(values))
        if operation is MathPrimitiveOperation.SUM:
            if not values:
                return self._math_blocked(item, refs, "EMPTY_INPUT")
            return self._math_ok(item, sum(values), refs, value_count=len(values))
        if operation is MathPrimitiveOperation.COUNT:
            return self._math_ok(item, len(values), refs, value_count=len(values))
        if operation is MathPrimitiveOperation.AVG:
            if not values:
                return self._math_blocked(item, refs, "EMPTY_INPUT")
            return self._math_ok(item, sum(values) / len(values), refs, value_count=len(values))
        if operation is MathPrimitiveOperation.MIN:
            if not values:
                return self._math_blocked(item, refs, "EMPTY_INPUT")
            return self._math_ok(item, min(values), refs, value_count=len(values))
        if operation is MathPrimitiveOperation.MAX:
            if not values:
                return self._math_blocked(item, refs, "EMPTY_INPUT")
            return self._math_ok(item, max(values), refs, value_count=len(values))
        if operation is MathPrimitiveOperation.SUM_PRODUCT:
            if not values or len(values) != len(paired):
                return self._math_blocked(item, refs, "PAIRED_INPUT_LENGTH_MISMATCH")
            total = sum(left * right for left, right in zip(values, paired))
            return self._math_ok(item, total, refs, value_count=len(values))
        if operation is MathPrimitiveOperation.MULTIPLY:
            if len(values) != 2 or paired:
                return self._math_blocked(item, refs, "MULTIPLY_REQUIRES_TWO_VALUES")
            return self._math_ok(item, values[0] * values[1], refs, value_count=2)
        if operation is MathPrimitiveOperation.SUBTRACT:
            if len(values) != 2 or paired:
                return self._math_blocked(item, refs, "SUBTRACT_REQUIRES_TWO_VALUES")
            return self._math_ok(item, values[0] - values[1], refs, value_count=2)
        if operation is MathPrimitiveOperation.PERCENT_OF:
            if len(values) != 2 or paired:
                return self._math_blocked(item, refs, "PERCENT_OF_REQUIRES_BASE_AND_PERCENT")
            return self._math_ok(item, (values[0] * values[1]) / 100.0, refs, value_count=2)
        return self._math_blocked(item, refs, "MATH_PRIMITIVE_NOT_SUPPORTED")

    def _math_ok(
        self,
        item: MathPrimitiveInput,
        value: float | int,
        source_refs: list[str],
        *,
        value_count: int,
    ) -> MathPrimitiveResult:
        return MathPrimitiveResult(
            operation=item.operation,
            status=FormulaStatus.OK,
            value=float(value),
            source_refs=source_refs,
            metadata={"value_count": value_count},
        )

    def _math_blocked(
        self,
        item: MathPrimitiveInput,
        source_refs: list[str],
        reason: str,
    ) -> MathPrimitiveResult:
        return MathPrimitiveResult(
            operation=item.operation,
            status=FormulaStatus.BLOCKED,
            value=None,
            source_refs=source_refs,
            blocking_reason=reason,
        )

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

        if formula_id == "PYME_013_PREREQUISITE_dpo":
            accounts_payable = values["accounts_payable"]
            purchases = values["purchases"]
            days = values["days"]
            if purchases == 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="DIVISION_BY_ZERO: purchases",
                )
            return self._ok(formula_id, (accounts_payable / purchases) * days, values, source_refs)

        if formula_id == "INV_002_rotacion_stock":
            return self._calculate_inv_002_rotacion_stock(values, source_refs)

        if formula_id == "INV_001_punto_reposicion":
            average_sales = values["average_sales"]
            lead_time = values["lead_time"]
            safety_stock = values["safety_stock"]
            return self._ok(
                formula_id,
                (average_sales * lead_time) + safety_stock,
                values,
                source_refs,
            )

        if formula_id == "PYME_011_dso":
            return self._calculate_pyme_011_dso(values, source_refs)

        if formula_id == "PYME_013_dso_dpo_gap":
            dso = values["dso"]
            dpo = values["dpo"]
            return self._ok(formula_id, dso - dpo, values, source_refs)

        if formula_id == "LIQ_002_saldo_final_proyectado":
            initial_balance = values["initial_balance"]
            expected_collections = values["expected_collections"]
            expected_payments = values["expected_payments"]
            return self._ok(
                formula_id,
                initial_balance + expected_collections - expected_payments,
                values,
                source_refs,
            )

        if formula_id == "PYME_024_liquidez_corriente":
            return self._calculate_pyme_024_liquidez_corriente(values, source_refs)

        if formula_id == "PYME_017_pricing_drift":
            return self._calculate_pyme_017_pricing_drift(values, source_refs)

        if formula_id == "punto_equilibrio_ventas":
            fixed_costs = values["fixed_costs"]
            contribution_margin_rate = values["contribution_margin_rate"]
            if contribution_margin_rate < 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="INVALID_INPUT: contribution_margin_rate",
                )
            if contribution_margin_rate == 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="DIVISION_BY_ZERO: contribution_margin_rate",
                )
            return self._ok(
                formula_id,
                fixed_costs / contribution_margin_rate,
                values,
                source_refs,
            )

        if formula_id == "PYME_026_flujo_operativo":
            net_income = values["net_income"]
            depreciation = values["depreciation"]
            amortization = values["amortization"]
            working_capital_change = values["working_capital_change"]
            return self._ok(
                formula_id,
                net_income + depreciation + amortization - working_capital_change,
                values,
                source_refs,
            )

        if formula_id == "PYME_027_intereses_ebitda":
            interest_expense = values["interest_expense"]
            ebitda = values["ebitda"]
            if ebitda == 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="DIVISION_BY_ZERO: ebitda",
                )
            return self._ok(
                formula_id,
                interest_expense / ebitda,
                values,
                source_refs,
            )

        if formula_id == "PYME_044_margen_cliente":
            client_revenue = values["client_revenue"]
            client_direct_costs = values["client_direct_costs"]
            client_service_costs = values["client_service_costs"]
            return self._ok(
                formula_id,
                client_revenue - client_direct_costs - client_service_costs,
                values,
                source_refs,
            )

        if formula_id == "PYME_033_concentracion_sku":
            main_sku_sales = values["main_sku_sales"]
            total_sales = values["total_sales"]
            if total_sales == 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="DIVISION_BY_ZERO: total_sales",
                )
            return self._ok(
                formula_id,
                (main_sku_sales / total_sales) * 100,
                values,
                source_refs,
            )

        if formula_id == "REN_002_coeficiente_reposicion":
            closing_index = values["closing_index"]
            origin_index = values["origin_index"]
            if origin_index == 0:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason="DIVISION_BY_ZERO: origin_index",
                )
            return self._ok(
                formula_id,
                closing_index / origin_index,
                values,
                source_refs,
            )

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

        total_outflows = costs + taxes
        net_margin_amount = sale_price - total_outflows
        value = (net_margin_amount / sale_price) * 100
        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.OK,
            value=float(value),
            inputs=inputs,
            source_refs=source_refs,
            metadata={
                "net_margin_amount": float(net_margin_amount),
                "net_margin_percentage": float(value),
                "total_outflows": float(total_outflows),
            },
        )

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

    def _calculate_pyme_024_liquidez_corriente(
        self,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "PYME_024_liquidez_corriente"
        current_assets = inputs["current_assets"]
        current_liabilities = inputs["current_liabilities"]

        if current_liabilities == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: current_liabilities",
            )

        return self._ok(formula_id, current_assets / current_liabilities, inputs, source_refs)

    def _calculate_pyme_017_pricing_drift(
        self,
        inputs: dict,
        source_refs: list[str],
    ) -> FormulaResult:
        formula_id = "PYME_017_pricing_drift"
        own_price = inputs["own_price"]
        market_price = inputs["market_price"]

        if market_price == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=inputs,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: market_price",
            )

        return self._ok(formula_id, ((own_price - market_price) / market_price) * 100, inputs, source_refs)

    def _collect_source_refs(self, inputs: list[FormulaInput]) -> list[str]:
        refs: list[str] = []
        for input_item in inputs:
            refs.extend(input_item.source_refs)
        return refs
