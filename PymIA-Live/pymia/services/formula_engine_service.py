from __future__ import annotations

from collections.abc import Callable

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaResult,
    FormulaStatus,
)
from pymia.contracts.formula_rules_v1 import load_formula_rules

FormulaCalculator = Callable[[dict, list[str]], FormulaResult]


class FormulaEngineService:
    """Motor determinístico mínimo de fórmulas.

    Fuente primaria: formula_rules_v1.json.
    """

    def _load_rule(self, formula_id: str) -> dict | None:
        rules = load_formula_rules()
        return (rules.get("rules_by_formula") or {}).get(formula_id)

    def _required_inputs(self, formula_id: str) -> list[str]:
        rule = self._load_rule(formula_id)
        if rule is not None:
            return list(rule.get("required_inputs") or [])
        return []

    def _calculator_registry(self) -> dict[str, FormulaCalculator]:
        return {
            "margen_bruto": self._dispatch_margen_bruto,
            "ganancia_bruta": self._dispatch_ganancia_bruta,
            "REN_001_margen_neto_real": self._calculate_ren_001_margen_neto_real,
            "LIQ_001_vendido_cobrado": self._dispatch_liq_001_vendido_cobrado,
            "INV_002_rotacion_stock": self._calculate_inv_002_rotacion_stock,
            "INV_001_punto_reposicion": self._dispatch_inv_001_punto_reposicion,
            "PYME_011_dso": self._calculate_pyme_011_dso,
            "PYME_013_dso_dpo_gap": self._dispatch_pyme_013_dso_dpo_gap,
            "LIQ_002_saldo_final_proyectado": self._dispatch_liq_002_saldo_final_proyectado,
            "PYME_024_liquidez_corriente": self._calculate_pyme_024_liquidez_corriente,
            "PYME_017_pricing_drift": self._calculate_pyme_017_pricing_drift,
            "punto_equilibrio_ventas": self._dispatch_punto_equilibrio_ventas,
            "PYME_026_flujo_operativo": self._dispatch_pyme_026_flujo_operativo,
            "PYME_027_intereses_ebitda": self._dispatch_pyme_027_intereses_ebitda,
            "PYME_044_margen_cliente": self._dispatch_pyme_044_margen_cliente,
            "PYME_033_concentracion_sku": self._dispatch_pyme_033_concentracion_sku,
            "REN_002_coeficiente_reposicion": self._dispatch_ren_002_coeficiente_reposicion,
        }

    def _apply_blocking_rules(self, formula_id: str, values: dict, source_refs: list[str]) -> FormulaResult | None:
        rule = self._load_rule(formula_id)
        if rule is None:
            return None
        for br in rule.get("blocking_rules") or []:
            field = br.get("field")
            operator = br.get("operator")
            threshold = br.get("value")
            blocking_reason = br.get("blocking_reason")
            if field and operator == "eq" and values.get(field) == threshold:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason=str(blocking_reason),
                )
        return None

    def _apply_invalid_input_rules(self, formula_id: str, values: dict, source_refs: list[str]) -> FormulaResult | None:
        rule = self._load_rule(formula_id)
        if rule is None:
            return None
        for iir in rule.get("invalid_input_rules") or []:
            field = iir.get("field")
            operator = iir.get("operator")
            threshold = iir.get("value")
            blocking_reason = iir.get("blocking_reason")
            if field and operator == "lt" and values.get(field) is not None and values[field] < threshold:
                return FormulaResult(
                    formula_id=formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs=values,
                    source_refs=source_refs,
                    blocking_reason=str(blocking_reason),
                )
        return None

    def calculate(self, formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
        values = {input_item.name: input_item.value for input_item in inputs}
        source_refs = self._collect_source_refs(inputs)

        rule = self._load_rule(formula_id)
        if rule is None:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason="FORMULA_NOT_SUPPORTED",
            )

        required = self._required_inputs(formula_id)
        missing = [name for name in required if values.get(name) is None]
        if missing:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason=f"MISSING_INPUTS: {','.join(missing)}",
            )

        blocked = self._apply_blocking_rules(formula_id, values, source_refs)
        if blocked is not None:
            return blocked

        invalid = self._apply_invalid_input_rules(formula_id, values, source_refs)
        if invalid is not None:
            return invalid

        calculator = self._calculator_registry().get(formula_id)
        if calculator is None:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason="FORMULA_NOT_IMPLEMENTED",
            )

        return calculator(values, source_refs)

    def _dispatch_margen_bruto(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        return self._calculate_margen_bruto(inputs["ventas"], inputs["costos"], inputs, source_refs)

    def _dispatch_ganancia_bruta(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "ganancia_bruta"
        ventas = inputs["ventas"]
        costos = inputs["costos"]
        return self._ok(formula_id, ventas - costos, inputs, source_refs)

    def _dispatch_liq_001_vendido_cobrado(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "LIQ_001_vendido_cobrado"
        sold_amount = inputs["sold_amount"]
        collected_amount = inputs["collected_amount"]
        return self._ok(formula_id, sold_amount - collected_amount, inputs, source_refs)

    def _dispatch_inv_001_punto_reposicion(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "INV_001_punto_reposicion"
        average_sales = inputs["average_sales"]
        lead_time = inputs["lead_time"]
        safety_stock = inputs["safety_stock"]
        return self._ok(
            formula_id,
            (average_sales * lead_time) + safety_stock,
            inputs,
            source_refs,
        )

    def _dispatch_pyme_013_dso_dpo_gap(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "PYME_013_dso_dpo_gap"
        dso = inputs["dso"]
        dpo = inputs["dpo"]
        return self._ok(formula_id, dso - dpo, inputs, source_refs)

    def _dispatch_liq_002_saldo_final_proyectado(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "LIQ_002_saldo_final_proyectado"
        initial_balance = inputs["initial_balance"]
        expected_collections = inputs["expected_collections"]
        expected_payments = inputs["expected_payments"]
        return self._ok(
            formula_id,
            initial_balance + expected_collections - expected_payments,
            inputs,
            source_refs,
        )

    def _dispatch_punto_equilibrio_ventas(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "punto_equilibrio_ventas"
        fixed_costs = inputs["fixed_costs"]
        contribution_margin_rate = inputs["contribution_margin_rate"]
        return self._ok(
            formula_id,
            fixed_costs / contribution_margin_rate,
            inputs,
            source_refs,
        )

    def _dispatch_pyme_026_flujo_operativo(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "PYME_026_flujo_operativo"
        net_income = inputs["net_income"]
        depreciation = inputs["depreciation"]
        amortization = inputs["amortization"]
        working_capital_change = inputs["working_capital_change"]
        return self._ok(
            formula_id,
            net_income + depreciation + amortization - working_capital_change,
            inputs,
            source_refs,
        )

    def _dispatch_pyme_027_intereses_ebitda(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "PYME_027_intereses_ebitda"
        interest_expense = inputs["interest_expense"]
        ebitda = inputs["ebitda"]
        return self._ok(
            formula_id,
            interest_expense / ebitda,
            inputs,
            source_refs,
        )

    def _dispatch_pyme_044_margen_cliente(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "PYME_044_margen_cliente"
        client_revenue = inputs["client_revenue"]
        client_direct_costs = inputs["client_direct_costs"]
        client_service_costs = inputs["client_service_costs"]
        return self._ok(
            formula_id,
            client_revenue - client_direct_costs - client_service_costs,
            inputs,
            source_refs,
        )

    def _dispatch_pyme_033_concentracion_sku(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "PYME_033_concentracion_sku"
        main_sku_sales = inputs["main_sku_sales"]
        total_sales = inputs["total_sales"]
        return self._ok(
            formula_id,
            (main_sku_sales / total_sales) * 100,
            inputs,
            source_refs,
        )

    def _dispatch_ren_002_coeficiente_reposicion(self, inputs: dict, source_refs: list[str]) -> FormulaResult:
        formula_id = "REN_002_coeficiente_reposicion"
        closing_index = inputs["closing_index"]
        origin_index = inputs["origin_index"]
        return self._ok(
            formula_id,
            closing_index / origin_index,
            inputs,
            source_refs,
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
