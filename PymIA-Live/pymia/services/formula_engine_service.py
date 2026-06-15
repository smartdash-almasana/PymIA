from __future__ import annotations

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaResult,
    FormulaStatus,
)
from pymia.contracts.formula_rules_v1 import load_formula_rules


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
