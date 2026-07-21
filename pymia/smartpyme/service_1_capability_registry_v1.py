"""Minimal governed registry for generic Service 1 capabilities."""
from __future__ import annotations

from decimal import Decimal
from typing import Final

from pymia.smartpyme.service_1_capability_contracts_v1 import (
    CapabilityDefinitionV1,
    ClassificationRuleV1,
    FormulaNodeV1,
    OutcomePolicyV1,
    VariableRequirementV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_GENERIC_CAPABILITY_REGISTRY_V1"


def _var(name: str) -> FormulaNodeV1:
    return FormulaNodeV1(operation="VARIABLE", variable_name=name)


def _op(operation: str, left: FormulaNodeV1, right: FormulaNodeV1) -> FormulaNodeV1:
    return FormulaNodeV1(operation=operation, left=left, right=right)  # type: ignore[arg-type]


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
    formula=_op("SUBTRACT", _op("ADD", _var("initial_balance"), _var("expected_collections")), _var("expected_payments")),
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
    formula=_op("MULTIPLY", _op("DIVIDE", _var("accounts_payable"), _var("purchases")), _var("days")),
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
    formula=_op("MULTIPLY", _op("DIVIDE", _var("accounts_receivable"), _var("sales")), _var("days")),
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
    DPO.capability_ref: DPO,
    PYME_011.capability_ref: PYME_011,
}


def get_capability_definition_v1(capability_ref: str) -> CapabilityDefinitionV1 | None:
    return _REGISTRY.get(capability_ref)


def list_capability_refs_v1() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


__all__ = ["SCHEMA_VERSION", "LIQ_002", "DPO", "PYME_011", "get_capability_definition_v1", "list_capability_refs_v1"]
