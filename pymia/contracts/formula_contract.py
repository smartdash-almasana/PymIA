from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from pymia.contracts.formula_rules_v1 import load_formula_rules


class FormulaStatus(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"


class MathPrimitiveOperation(StrEnum):
    SINGLE_VALUE = "SINGLE_VALUE"
    SUM = "SUM"
    COUNT = "COUNT"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    SUM_PRODUCT = "SUM_PRODUCT"
    MULTIPLY = "MULTIPLY"
    SUBTRACT = "SUBTRACT"
    DIVIDE = "DIVIDE"
    PERCENT_OF = "PERCENT_OF"


class MathPrimitiveInput(BaseModel):
    operation: MathPrimitiveOperation
    values: list[float | int] = Field(default_factory=list)
    paired_values: list[float | int] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class MathPrimitiveResult(BaseModel):
    operation: MathPrimitiveOperation
    status: FormulaStatus
    value: float | None
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FormulaInput(BaseModel):
    name: str
    value: float | int | None
    source_refs: list[str] = Field(default_factory=list)


class FormulaDefinition(BaseModel):
    formula_id: str
    formula_version: str
    required_inputs: list[str]
    description: str
    expression: str
    output_unit: str | None = None


class FormulaResult(BaseModel):
    formula_id: str
    status: FormulaStatus
    value: float | None
    inputs: dict[str, float | int | None]
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def _load_supported_formulas() -> dict[str, FormulaDefinition]:
    rules = load_formula_rules().get("rules_by_formula")
    if not isinstance(rules, dict):
        raise RuntimeError("formula_rules_v1.json must define rules_by_formula")
    definitions: dict[str, FormulaDefinition] = {}
    for formula_id, raw_rule in rules.items():
        if not isinstance(raw_rule, dict):
            raise RuntimeError(f"formula rule must be an object: {formula_id}")
        if raw_rule.get("formula_id") != formula_id:
            raise RuntimeError(f"formula rule id mismatch: {formula_id}")
        expression = str(raw_rule.get("expression") or "").strip()
        version = str(raw_rule.get("formula_version") or "").strip()
        required_inputs = raw_rule.get("required_inputs")
        if not expression or not version or not isinstance(required_inputs, list) or not required_inputs:
            raise RuntimeError(f"formula rule is incomplete: {formula_id}")
        definitions[formula_id] = FormulaDefinition(
            formula_id=formula_id,
            formula_version=version,
            required_inputs=[str(value) for value in required_inputs],
            description=expression,
            expression=expression,
            output_unit=raw_rule.get("output_unit"),
        )
    return definitions


SUPPORTED_FORMULAS: dict[str, FormulaDefinition] = _load_supported_formulas()


def calculate_formula(formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
    from pymia.services.formula_engine_service import FormulaEngineService

    return FormulaEngineService().calculate(formula_id, inputs)
