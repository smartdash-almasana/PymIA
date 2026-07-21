"""Contracts for the minimal generic productive capability kernel."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

SCHEMA_VERSION: Final[str] = "SERVICE_1_GENERIC_CAPABILITY_CONTRACTS_V1"

CapabilityKind = Literal["ATOMIC", "COMPOSITE"]
AggregationMode = Literal["SUM", "SINGLE_VALUE"]
Operation = Literal["VALUE", "VARIABLE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"]
Comparison = Literal["LT", "LE", "EQ", "GE", "GT"]


@dataclass(frozen=True)
class FormulaNodeV1:
    operation: Operation
    variable_name: str | None = None
    value: Decimal | None = None
    left: "FormulaNodeV1 | None" = None
    right: "FormulaNodeV1 | None" = None


@dataclass(frozen=True)
class VariableRequirementV1:
    name: str
    aggregation: AggregationMode
    minimum: Decimal | None = None
    minimum_inclusive: bool = True
    maximum: Decimal | None = None
    maximum_inclusive: bool = True
    unit: str | None = None
    source_capability_ref: str | None = None
    source_result_key: str | None = None


@dataclass(frozen=True)
class ClassificationRuleV1:
    code: str
    comparison: Comparison
    reference_variable: str | None = None
    reference_value: Decimal | None = None


@dataclass(frozen=True)
class OutcomePolicyV1:
    findings: tuple[tuple[str, str], ...]
    treatments: tuple[tuple[str, tuple[str, ...]], ...]
    limitations: tuple[str, ...]
    forbidden_claims: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityDefinitionV1:
    capability_ref: str
    pathology_code: str
    formula_ref: str
    kind: CapabilityKind
    variables: tuple[VariableRequirementV1, ...]
    formula: FormulaNodeV1
    result_key: str
    result_unit: str
    classifications: tuple[ClassificationRuleV1, ...]
    outcome_policy: OutcomePolicyV1
    delivery_authorized: bool = False


__all__ = [
    "SCHEMA_VERSION",
    "FormulaNodeV1",
    "VariableRequirementV1",
    "ClassificationRuleV1",
    "OutcomePolicyV1",
    "CapabilityDefinitionV1",
]
