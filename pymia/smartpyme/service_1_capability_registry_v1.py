"""Minimal governed registry for generic Service 1 capabilities."""
from __future__ import annotations

from decimal import Decimal
from typing import Final

from pymia.smartpyme.service_1_capability_contracts_v1 import (
    CapabilityDefinitionV1,
    ClassificationRuleV1,
    OutcomePolicyV1,
    VariableRequirementV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_GENERIC_CAPABILITY_REGISTRY_V1"


LIQ_002 = CapabilityDefinitionV1(
    capability_ref="projected_closing_cash_balance",
    pathology_code="LIQ_002",
    formula_ref="LIQ_002_saldo_final_proyectado",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("initial_balance", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("expected_collections", "SUM", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("expected_payments", "SUM", minimum=Decimal("0"), unit="currency"),
    ),
    result_key="projected_closing_balance",
    result_unit="currency",
    classifications=(
        ClassificationRuleV1("NEGATIVE_PROJECTED_BALANCE", "LT", reference_value=Decimal("0")),
        ClassificationRuleV1("ZERO_PROJECTED_BALANCE", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("POSITIVE_PROJECTED_BALANCE", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("POSITIVE_PROJECTED_BALANCE", "La evidencia confirmada muestra un saldo final proyectado positivo."),
            ("ZERO_PROJECTED_BALANCE", "La evidencia confirmada muestra un saldo final proyectado igual a cero."),
            ("NEGATIVE_PROJECTED_BALANCE", "La evidencia confirmada muestra un saldo final proyectado negativo."),
        ),
        treatments=(
            ("POSITIVE_PROJECTED_BALANCE", ("Conservar la proyección como control del período confirmado.",)),
            ("ZERO_PROJECTED_BALANCE", ("Revisar cobranzas y pagos confirmados antes de asumir disponibilidad.",)),
            ("NEGATIVE_PROJECTED_BALANCE", ("Revisar vencimientos y cobranzas sin atribuir una causa automática.",)),
        ),
        limitations=("La proyección no confirma iliquidez ni causas estructurales.",),
        forbidden_claims=("Afirmar fraude, error de caja o responsabilidad causal sin evidencia adicional.",),
    ),
)


INV_001 = CapabilityDefinitionV1(
    capability_ref="reorder_point",
    pathology_code="INV_001",
    formula_ref="INV_001_punto_reposicion",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("average_sales", "SINGLE_VALUE", minimum=Decimal("0"), unit="units_per_day"),
        VariableRequirementV1(
            "lead_time",
            "SINGLE_VALUE",
            minimum=Decimal("0"),
            minimum_inclusive=False,
            unit="days",
        ),
        VariableRequirementV1("safety_stock", "SINGLE_VALUE", minimum=Decimal("0"), unit="units"),
    ),
    result_key="reorder_point_units",
    result_unit="units",
    classifications=(
        ClassificationRuleV1("NO_REORDER_REQUIREMENT", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("REORDER_POINT_CALCULATED", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("NO_REORDER_REQUIREMENT", "La evidencia confirmada produce un punto de reposición igual a cero."),
            ("REORDER_POINT_CALCULATED", "La evidencia confirmada produce un punto de reposición mayor que cero."),
        ),
        treatments=(
            ("NO_REORDER_REQUIREMENT", ("Revisar las variables confirmadas antes de utilizar el resultado operativo.",)),
            ("REORDER_POINT_CALCULATED", ("Usar el nivel calculado como referencia y contrastarlo con la política de inventario vigente.",)),
        ),
        limitations=(
            "El cálculo no confirma riesgo de quiebre ni sustituye la revisión de demanda, plazo y stock de seguridad.",
        ),
        forbidden_claims=(
            "Ordenar una compra automáticamente o atribuir faltantes futuros sin evidencia adicional.",
        ),
    ),
)


INV_002 = CapabilityDefinitionV1(
    capability_ref="inventory_turnover",
    pathology_code="INV_002",
    formula_ref="INV_002_rotacion_stock",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("cost_of_goods_sold", "SUM", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1(
            "average_stock",
            "SINGLE_VALUE",
            minimum=Decimal("0"),
            minimum_inclusive=False,
            unit="currency",
        ),
    ),
    result_key="inventory_turnover_ratio",
    result_unit="ratio",
    classifications=(
        ClassificationRuleV1("NO_RECORDED_TURNOVER", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("POSITIVE_RECORDED_TURNOVER", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("NO_RECORDED_TURNOVER", "La evidencia confirmada produce una rotación de inventario igual a cero."),
            ("POSITIVE_RECORDED_TURNOVER", "La evidencia confirmada produce una rotación de inventario mayor que cero."),
        ),
        treatments=(
            ("NO_RECORDED_TURNOVER", ("Revisar el costo de ventas y el stock promedio confirmados antes de interpretar el resultado.",)),
            ("POSITIVE_RECORDED_TURNOVER", ("Conservar el indicador como referencia comparable entre períodos equivalentes.",)),
        ),
        limitations=(
            "La rotación describe una relación matemática y no confirma exceso, obsolescencia ni faltantes de inventario.",
            "El stock promedio debe ser evidencia explícita gobernada o provenir de una capacidad previa identificable; no se deriva silenciosamente.",
        ),
        forbidden_claims=(
            "Afirmar sobrestock, quiebre, obsolescencia o mala gestión sin evidencia adicional y umbrales contextualizados.",
        ),
    ),
)


DPO = CapabilityDefinitionV1(
    capability_ref="dpo",
    pathology_code="PYME_013_PREREQUISITE_DPO",
    formula_ref="PYME_013_PREREQUISITE_dpo",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("accounts_payable", "SUM", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("purchases", "SUM", minimum=Decimal("0"), minimum_inclusive=False, unit="currency"),
        VariableRequirementV1("days", "SINGLE_VALUE", minimum=Decimal("0"), minimum_inclusive=False, unit="days"),
    ),
    result_key="dpo_days",
    result_unit="days",
    classifications=(
        ClassificationRuleV1("DPO_BELOW_PERIOD", "LT", reference_variable="days"),
        ClassificationRuleV1("DPO_EQUALS_PERIOD", "EQ", reference_variable="days"),
        ClassificationRuleV1("DPO_ABOVE_PERIOD", "GT", reference_variable="days"),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("DPO_BELOW_PERIOD", "La evidencia confirmada muestra un DPO menor que la duración del período analizado."),
            ("DPO_EQUALS_PERIOD", "La evidencia confirmada muestra un DPO igual a la duración del período analizado."),
            ("DPO_ABOVE_PERIOD", "La evidencia confirmada muestra un DPO mayor que la duración del período analizado."),
        ),
        treatments=(
            ("DPO_BELOW_PERIOD", ("Conservar el indicador como control periódico comparable.",)),
            ("DPO_EQUALS_PERIOD", ("Revisar la composición confirmada antes de interpretar el resultado.",)),
            ("DPO_ABOVE_PERIOD", ("Revisar cuentas por pagar y compras por separado antes de atribuir una causa.",)),
        ),
        limitations=("El DPO describe una relación matemática y no identifica causas.",),
        forbidden_claims=("Afirmar retraso, incumplimiento contractual o falta de liquidez sin evidencia adicional.",),
    ),
)


PYME_013 = CapabilityDefinitionV1(
    capability_ref="payment_collection_gap",
    pathology_code="PYME_013",
    formula_ref="PYME_013_dso_dpo_gap",
    kind="COMPOSITE",
    variables=(
        VariableRequirementV1(
            "dso",
            "SINGLE_VALUE",
            minimum=Decimal("0"),
            unit="days",
            source_capability_ref="dso",
            source_result_key="dso_days",
        ),
        VariableRequirementV1(
            "dpo",
            "SINGLE_VALUE",
            minimum=Decimal("0"),
            unit="days",
            source_capability_ref="dpo",
            source_result_key="dpo_days",
        ),
    ),
    result_key="payment_collection_gap_days",
    result_unit="days",
    classifications=(
        ClassificationRuleV1("COLLECTIONS_BEFORE_PAYMENTS", "LT", reference_value=Decimal("0")),
        ClassificationRuleV1("COLLECTIONS_MATCH_PAYMENTS", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("COLLECTIONS_AFTER_PAYMENTS", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("COLLECTIONS_BEFORE_PAYMENTS", "Los resultados gobernados muestran cobros antes que pagos."),
            ("COLLECTIONS_MATCH_PAYMENTS", "Los resultados gobernados muestran cobros y pagos en la misma relación temporal."),
            ("COLLECTIONS_AFTER_PAYMENTS", "Los resultados gobernados muestran cobros después que pagos."),
        ),
        treatments=(
            ("COLLECTIONS_BEFORE_PAYMENTS", ("Mantener la relación temporal como control del período confirmado.",)),
            ("COLLECTIONS_MATCH_PAYMENTS", ("Revisar el período confirmado antes de interpretar la coincidencia.",)),
            ("COLLECTIONS_AFTER_PAYMENTS", ("Revisar cobranzas y pagos por separado sin atribuir una causa.",)),
        ),
        limitations=("La brecha DSO-DPO describe una relación temporal y no identifica causas.",),
        forbidden_claims=("Afirmar insolvencia, mala gestión o necesidad de financiamiento sin evidencia adicional.",),
    ),
)


PYME_024 = CapabilityDefinitionV1(
    capability_ref="current_ratio",
    pathology_code="PYME_024",
    formula_ref="PYME_024_liquidez_corriente",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("current_assets", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("current_liabilities", "SINGLE_VALUE", minimum=Decimal("0"), minimum_inclusive=False, unit="currency"),
    ),
    result_key="current_ratio_value",
    result_unit="ratio",
    classifications=(
        ClassificationRuleV1("ZERO_CURRENT_RATIO", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("POSITIVE_CURRENT_RATIO", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("ZERO_CURRENT_RATIO", "la evidencia confirmada produce una razón corriente igual a cero."),
            ("POSITIVE_CURRENT_RATIO", "la evidencia confirmada produce una razón corriente mayor que cero."),
        ),
        treatments=(
            ("ZERO_CURRENT_RATIO", ("revisar activo y pasivo corriente confirmados antes de interpretar.",)),
            ("POSITIVE_CURRENT_RATIO", ("conservar el indicador para comparar períodos equivalentes.",)),
        ),
        limitations=(
            "La razón corriente es una relación matemática y no confirma solvencia ni capacidad efectiva de pago.",
            "No aplicar umbrales universales sin contexto sectorial, temporal y contable.",
        ),
        forbidden_claims=(
            "No afirmar insolvencia, liquidez suficiente, mala gestión o necesidad de financiamiento sin evidencia adicional.",
        ),
    ),
)


PYME_033 = CapabilityDefinitionV1(
    capability_ref="sales_concentration",
    pathology_code="PYME_033",
    formula_ref="PYME_033_concentracion_sku",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("main_sku_sales", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("total_sales", "SINGLE_VALUE", minimum=Decimal("0"), minimum_inclusive=False, unit="currency"),
    ),
    result_key="sales_concentration_percentage",
    result_unit="percentage",
    classifications=(
        ClassificationRuleV1("ZERO_RECORDED_CONCENTRATION", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("CONCENTRATION_WITHIN_RECORDED_TOTAL", "LE", reference_value=Decimal("100")),
        ClassificationRuleV1("CONCENTRATION_ABOVE_RECORDED_TOTAL", "GT", reference_value=Decimal("100")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("ZERO_RECORDED_CONCENTRATION", "la evidencia confirmada produce una concentración de ventas igual a cero."),
            ("CONCENTRATION_WITHIN_RECORDED_TOTAL", "la evidencia confirmada muestra una concentración de ventas entre 0 y 100 por ciento del total registrado."),
            ("CONCENTRATION_ABOVE_RECORDED_TOTAL", "la evidencia confirmada muestra una concentración de ventas mayor al total registrado."),
        ),
        treatments=(
            ("ZERO_RECORDED_CONCENTRATION", ("revisar main_sku_sales y total_sales confirmados antes de interpretar.",)),
            ("CONCENTRATION_WITHIN_RECORDED_TOTAL", ("conservar el indicador para comparar períodos equivalentes.",)),
            ("CONCENTRATION_ABOVE_RECORDED_TOTAL", ("revisar main_sku_sales y total_sales por separado antes de atribuir una causa.",)),
        ),
        limitations=(
            "La concentración de ventas describe una relación matemática y no identifica causas.",
            "No aplicar umbrales universales de concentración sin contexto sectorial, temporal y contable.",
        ),
        forbidden_claims=(
            "No afirmar dependencia excesiva de un producto o necesidad de diversificación sin evidencia adicional.",
        ),
    ),
)


PYME_027 = CapabilityDefinitionV1(
    capability_ref="interest_burden_ratio",
    pathology_code="PYME_027",
    formula_ref="PYME_027_intereses_ebitda",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("interest_expense", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1(
            "ebitda",
            "SINGLE_VALUE",
            minimum=Decimal("0"),
            minimum_inclusive=False,
            unit="currency",
        ),
    ),
    result_key="interest_burden_ratio_value",
    result_unit="ratio",
    classifications=(
        ClassificationRuleV1("ZERO_INTEREST_BURDEN", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("POSITIVE_INTEREST_BURDEN", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("ZERO_INTEREST_BURDEN", "La evidencia confirmada muestra una carga de intereses igual a cero."),
            ("POSITIVE_INTEREST_BURDEN", "La evidencia confirmada muestra una carga de intereses positiva respecto del EBITDA."),
        ),
        treatments=(
            ("ZERO_INTEREST_BURDEN", ("Conservar el indicador como control del período confirmado.",)),
            ("POSITIVE_INTEREST_BURDEN", ("Revisar intereses y EBITDA confirmados antes de interpretar su evolución.",)),
        ),
        limitations=("La razón describe una relación matemática y no confirma sostenibilidad financiera ni causas.",),
        forbidden_claims=("Afirmar estrés financiero, insolvencia o decisiones de financiamiento sin evidencia adicional.",),
    ),
)


PYME_026 = CapabilityDefinitionV1(
    capability_ref="adjusted_operating_cash_flow",
    pathology_code="PYME_026",
    formula_ref="PYME_026_flujo_operativo",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("net_income", "SINGLE_VALUE", unit="currency"),
        VariableRequirementV1("depreciation", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("amortization", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("working_capital_change", "SINGLE_VALUE", unit="currency"),
    ),
    result_key="adjusted_operating_cash_flow_value",
    result_unit="currency",
    classifications=(
        ClassificationRuleV1("NEGATIVE_ADJUSTED_OPERATING_CASH_FLOW", "LT", reference_value=Decimal("0")),
        ClassificationRuleV1("ZERO_ADJUSTED_OPERATING_CASH_FLOW", "EQ", reference_value=Decimal("0")),
        ClassificationRuleV1("POSITIVE_ADJUSTED_OPERATING_CASH_FLOW", "GT", reference_value=Decimal("0")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("NEGATIVE_ADJUSTED_OPERATING_CASH_FLOW", "La evidencia confirmada produce un flujo operativo ajustado negativo."),
            ("ZERO_ADJUSTED_OPERATING_CASH_FLOW", "La evidencia confirmada produce un flujo operativo ajustado igual a cero."),
            ("POSITIVE_ADJUSTED_OPERATING_CASH_FLOW", "La evidencia confirmada produce un flujo operativo ajustado positivo."),
        ),
        treatments=(
            ("NEGATIVE_ADJUSTED_OPERATING_CASH_FLOW", ("Revisar los componentes confirmados y la convención de signo antes de interpretar el resultado.",)),
            ("ZERO_ADJUSTED_OPERATING_CASH_FLOW", ("Conservar el cálculo como control del período confirmado.",)),
            ("POSITIVE_ADJUSTED_OPERATING_CASH_FLOW", ("Revisar la comparabilidad de los períodos antes de usar el indicador como referencia.",)),
        ),
        limitations=(
            "El cálculo usa working_capital_change explícitamente provisto y no lo reconstruye desde balances.",
            "El resultado no confirma disponibilidad de caja, causas operativas ni sostenibilidad financiera.",
        ),
        forbidden_claims=(
            "Afirmar problemas de caja, solvencia, causas o tratamientos automáticos sin evidencia adicional.",
        ),
    ),
)


REN_002 = CapabilityDefinitionV1(
    capability_ref="index_update_ratio",
    pathology_code="REN_002",
    formula_ref="REN_002_coeficiente_reposicion",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("closing_index", "SINGLE_VALUE", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("origin_index", "SINGLE_VALUE", minimum=Decimal("0"), minimum_inclusive=False, unit="currency"),
    ),
    result_key="index_update_ratio",
    result_unit="ratio",
    classifications=(
        ClassificationRuleV1("INDEX_BELOW_ORIGIN", "LT", reference_value=Decimal("1")),
        ClassificationRuleV1("INDEX_EQUALS_ORIGIN", "EQ", reference_value=Decimal("1")),
        ClassificationRuleV1("INDEX_ABOVE_ORIGIN", "GT", reference_value=Decimal("1")),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("INDEX_BELOW_ORIGIN", "el índice de cierre es menor que el índice de origen."),
            ("INDEX_EQUALS_ORIGIN", "el índice de cierre es igual al índice de origen."),
            ("INDEX_ABOVE_ORIGIN", "el índice de cierre es mayor que el índice de origen."),
        ),
        treatments=(
            ("INDEX_BELOW_ORIGIN", ("revisar índices confirmados antes de interpretar la variación.",)),
            ("INDEX_EQUALS_ORIGIN", ("revisar índices confirmados antes de interpretar la igualdad.",)),
            ("INDEX_ABOVE_ORIGIN", ("revisar índices confirmados antes de interpretar la variación.",)),
        ),
        limitations=(
            "La relación entre índices describe una variación matemática y no identifica causas.",
            "No atribuir mejora o deterioro económico sin evidencia adicional.",
        ),
        forbidden_claims=(
            "No afirmar actualización favorable, desactualización o necesidad de reexpresión sin evidencia adicional.",
        ),
    ),
)


PYME_011 = CapabilityDefinitionV1(
    capability_ref="dso",
    pathology_code="PYME_011",
    formula_ref="PYME_011_dso",
    kind="ATOMIC",
    variables=(
        VariableRequirementV1("accounts_receivable", "SUM", minimum=Decimal("0"), unit="currency"),
        VariableRequirementV1("sales", "SUM", minimum=Decimal("0"), minimum_inclusive=False, unit="currency"),
        VariableRequirementV1("days", "SINGLE_VALUE", minimum=Decimal("0"), minimum_inclusive=False, unit="days"),
    ),
    result_key="dso_days",
    result_unit="days",
    classifications=(
        ClassificationRuleV1("DSO_WITHIN_PERIOD", "LT", reference_variable="days"),
        ClassificationRuleV1("DSO_EQUALS_PERIOD", "EQ", reference_variable="days"),
        ClassificationRuleV1("DSO_EXCEEDS_PERIOD", "GT", reference_variable="days"),
    ),
    outcome_policy=OutcomePolicyV1(
        findings=(
            ("DSO_WITHIN_PERIOD", "La evidencia confirmada muestra un DSO menor que la duración del período analizado."),
            ("DSO_EQUALS_PERIOD", "La evidencia confirmada muestra un DSO igual a la duración del período analizado."),
            ("DSO_EXCEEDS_PERIOD", "La evidencia confirmada muestra un DSO mayor que la duración del período analizado."),
        ),
        treatments=(
            ("DSO_WITHIN_PERIOD", ("Conservar el indicador como control periódico comparable.",)),
            ("DSO_EQUALS_PERIOD", ("Revisar la composición confirmada antes de interpretar el resultado.",)),
            ("DSO_EXCEEDS_PERIOD", ("Revisar vencimientos y cobranzas por separado antes de atribuir una causa.",)),
        ),
        limitations=("El DSO describe una relación matemática y no identifica causas.",),
        forbidden_claims=("Afirmar morosidad, incobrabilidad, fraude o error contable sin evidencia adicional.",),
    ),
)


_REGISTRY: Final[dict[str, CapabilityDefinitionV1]] = {
    LIQ_002.capability_ref: LIQ_002,
    INV_001.capability_ref: INV_001,
    INV_002.capability_ref: INV_002,
    DPO.capability_ref: DPO,
    PYME_011.capability_ref: PYME_011,
    PYME_013.capability_ref: PYME_013,
    PYME_024.capability_ref: PYME_024,
    PYME_033.capability_ref: PYME_033,
    PYME_027.capability_ref: PYME_027,
    PYME_026.capability_ref: PYME_026,
    REN_002.capability_ref: REN_002,
}


def get_capability_definition_v1(capability_ref: str) -> CapabilityDefinitionV1 | None:
    return _REGISTRY.get(capability_ref)


def list_capability_refs_v1() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


__all__ = [
    "SCHEMA_VERSION",
    "LIQ_002",
    "INV_001",
    "INV_002",
    "DPO",
    "PYME_011",
    "PYME_013",
    "PYME_024",
    "PYME_033",
    "PYME_027",
    "PYME_026",
    "REN_002",
    "get_capability_definition_v1",
    "list_capability_refs_v1",
]
