"""Deterministic evaluator for PYME_011 Days Sales Outstanding."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Final

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
    calculate_formula,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_capability_contracts_v1 import (
    ClassificationPredicate,
    ClassificationRule,
    classify_classification_rules,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PYME_011_EVALUATION_V1"
COMPUTATION_PLAN_SCHEMA_VERSION: Final[str] = "SERVICE_1_COMPUTATION_PLAN_V1"
PATHOLOGY_CODE: Final[str] = "PYME_011"
FORMULA_REF: Final[str] = "PYME_011_dso"
CAPABILITY_REF: Final[str] = "dso"
PLAN_STATUS_READY: Final[str] = "READY_FOR_COMPUTATION"
STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_PLAN_BLOCKED: Final[str] = "PLAN_BLOCKED"
CLASS_WITHIN_PERIOD: Final[str] = "DSO_WITHIN_PERIOD"
CLASS_EQUALS_PERIOD: Final[str] = "DSO_EQUALS_PERIOD"
CLASS_EXCEEDS_PERIOD: Final[str] = "DSO_EXCEEDS_PERIOD"
_REQUIRED_VARIABLES: Final[tuple[str, str, str]] = ("accounts_receivable", "sales", "days")
_CLASSIFICATION_RULES: Final[tuple[ClassificationRule, ...]] = (
    ClassificationRule(
        CLASS_WITHIN_PERIOD,
        predicates=(ClassificationPredicate("result", "LT", right_ref="days"),),
    ),
    ClassificationRule(
        CLASS_EQUALS_PERIOD,
        predicates=(ClassificationPredicate("result", "EQ", right_ref="days"),),
    ),
    ClassificationRule(
        CLASS_EXCEEDS_PERIOD,
        predicates=(ClassificationPredicate("result", "GT", right_ref="days"),),
    ),
)


def evaluate_pyme_011_from_computation_plan_v1(*, computation_plan: object, inputs: object) -> dict[str, object]:
    errors = _validate_plan(computation_plan)
    if errors:
        return _packet(STATUS_PLAN_BLOCKED, None, {}, errors)
    if not isinstance(inputs, dict):
        return _packet(STATUS_INVALID_INPUT, None, {}, ["inputs must be an object."])
    missing = [name for name in _REQUIRED_VARIABLES if name not in inputs]
    unknown = sorted(str(name) for name in inputs if name not in _REQUIRED_VARIABLES)
    if missing or unknown:
        return _packet(STATUS_INVALID_INPUT, None, {}, [*(f"missing required input: {n}." for n in missing), *(f"unknown input: {n}." for n in unknown)])
    return evaluate_pyme_011_v1(accounts_receivable=inputs["accounts_receivable"], sales=inputs["sales"], days=inputs["days"])


def evaluate_pyme_011_v1(*, accounts_receivable: object, sales: object, days: object) -> dict[str, object]:
    normalized: dict[str, float] = {}
    errors: list[str] = []
    for name, raw in (("accounts_receivable", accounts_receivable), ("sales", sales), ("days", days)):
        value, error = _number(raw)
        if error:
            errors.append(f"{name} {error}")
            continue
        normalized[name] = float(value)
        if name == "accounts_receivable" and value < 0:
            errors.append("accounts_receivable must be greater than or equal to 0.")
        if name in {"sales", "days"} and value <= 0:
            errors.append(f"{name} must be greater than 0.")
    if errors:
        return _packet(STATUS_INVALID_INPUT, None, normalized, errors)
    kernel_result = calculate_formula(
        FORMULA_REF,
        [
            FormulaInput(name="accounts_receivable", value=normalized["accounts_receivable"], source_refs=["PYME_011:accounts_receivable"]),
            FormulaInput(name="sales", value=normalized["sales"], source_refs=["PYME_011:sales"]),
            FormulaInput(name="days", value=normalized["days"], source_refs=["PYME_011:days"]),
        ],
    )
    if kernel_result.status != FormulaStatus.OK or kernel_result.value is None:
        return _packet(
            STATUS_INVALID_INPUT,
            None,
            normalized,
            [kernel_result.blocking_reason or "PYME_011 formula calculation blocked."],
        )
    ratio_result = FormulaEngineService().calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.DIVIDE,
            values=[normalized["accounts_receivable"], normalized["sales"]],
            source_refs=["PYME_011:accounts_receivable", "PYME_011:sales"],
        )
    )
    if ratio_result.status != FormulaStatus.OK or ratio_result.value is None:
        return _packet(
            STATUS_INVALID_INPUT,
            None,
            normalized,
            [ratio_result.blocking_reason or "PYME_011 ratio calculation blocked."],
        )
    dso = kernel_result.value
    period = normalized["days"]
    classification = classify_classification_rules(
        _CLASSIFICATION_RULES,
        result=dso,
        inputs={"days": period},
    )
    if classification is None:
        return _packet(STATUS_INVALID_INPUT, None, normalized, ["PYME_011 classification policy did not match."])
    return _packet(STATUS_EVALUATED, classification, normalized, [], computed={"dso_days": dso, "period_days": period, "receivables_to_sales_ratio": ratio_result.value}, mathematical_limits={"accounts_receivable_min_inclusive": 0.0, "sales_min_exclusive": 0.0, "days_min_exclusive": 0.0, "comparison_basis": "same_confirmed_period"})


def _number(value: object) -> tuple[Decimal, str | None]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0"), "is required."
    if isinstance(value, bool):
        return Decimal("0"), "must be numeric."
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0"), "must be numeric."
    if not number.is_finite():
        return Decimal("0"), "must be finite."
    return number, None


def _validate_plan(plan: object) -> list[str]:
    if not isinstance(plan, dict):
        return ["computation_plan must be an object."]
    expected = {"schema_version": COMPUTATION_PLAN_SCHEMA_VERSION, "status": PLAN_STATUS_READY, "requested_capability": CAPABILITY_REF, "pathology_code": PATHOLOGY_CODE, "formula_id": FORMULA_REF}
    errors = [f"computation_plan {k} must equal {v}." for k, v in expected.items() if plan.get(k) != v]
    if tuple(plan.get("required_variables") or ()) != _REQUIRED_VARIABLES:
        errors.append("computation_plan required_variables do not match PYME_011.")
    if plan.get("computation_candidate_ready") is not True:
        errors.append("computation_plan candidate is not ready.")
    if any(plan.get(flag) for flag in ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated")):
        errors.append("computation_plan safety flags must remain false.")
    return errors


def _packet(status: str, classification: str | None, inputs: dict[str, float], errors: list[str], *, computed: dict[str, float] | None = None, mathematical_limits: dict[str, object] | None = None) -> dict[str, object]:
    return {"schema_version": SCHEMA_VERSION, "pathology_code": PATHOLOGY_CODE, "formula_ref": FORMULA_REF, "capability_ref": CAPABILITY_REF, "status": status, "classification": classification, "inputs": dict(inputs), "computed": dict(computed or {}), "errors": list(errors), "mathematical_limits": dict(mathematical_limits or {}), "runtime_authorized": False, "tool_execution_authorized": False, "product_ready": False, "delivery_authorized": False, "diagnosis_generated": False}


__all__ = ["SCHEMA_VERSION", "PATHOLOGY_CODE", "FORMULA_REF", "CAPABILITY_REF", "STATUS_EVALUATED", "STATUS_INVALID_INPUT", "STATUS_PLAN_BLOCKED", "CLASS_WITHIN_PERIOD", "CLASS_EQUALS_PERIOD", "CLASS_EXCEEDS_PERIOD", "evaluate_pyme_011_v1", "evaluate_pyme_011_from_computation_plan_v1"]
