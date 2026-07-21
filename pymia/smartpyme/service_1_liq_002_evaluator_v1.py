"""Deterministic evaluator for LIQ_002 projected closing cash balance."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_LIQ_002_EVALUATION_V1"
COMPUTATION_PLAN_SCHEMA_VERSION: Final[str] = "SERVICE_1_COMPUTATION_PLAN_V1"
PATHOLOGY_CODE: Final[str] = "LIQ_002"
FORMULA_REF: Final[str] = "LIQ_002_saldo_final_proyectado"
CAPABILITY_REF: Final[str] = "projected_closing_cash_balance"
PLAN_STATUS_READY: Final[str] = "READY_FOR_COMPUTATION"

STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_PLAN_BLOCKED: Final[str] = "PLAN_BLOCKED"

CLASS_POSITIVE_BALANCE: Final[str] = "POSITIVE_PROJECTED_BALANCE"
CLASS_ZERO_BALANCE: Final[str] = "ZERO_PROJECTED_BALANCE"
CLASS_NEGATIVE_BALANCE: Final[str] = "NEGATIVE_PROJECTED_BALANCE"

_REQUIRED_VARIABLES: Final[tuple[str, str, str]] = (
    "initial_balance",
    "expected_collections",
    "expected_payments",
)


def evaluate_liq_002_from_computation_plan_v1(
    *, computation_plan: object, inputs: object
) -> dict[str, object]:
    errors = _validate_computation_plan(computation_plan)
    if errors:
        return _packet(
            status=STATUS_PLAN_BLOCKED,
            classification=None,
            inputs={},
            errors=errors,
            plan_validation={"status": STATUS_PLAN_BLOCKED},
        )
    if not isinstance(inputs, dict):
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs={},
            errors=["inputs must be an object."],
            plan_validation=_validated_plan_projection(computation_plan),
        )
    missing = [name for name in _REQUIRED_VARIABLES if name not in inputs]
    unknown = sorted(str(name) for name in inputs if name not in _REQUIRED_VARIABLES)
    if missing or unknown:
        validation_errors = [f"missing required input: {name}." for name in missing]
        validation_errors.extend(f"unknown input: {name}." for name in unknown)
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs={},
            errors=validation_errors,
            plan_validation=_validated_plan_projection(computation_plan),
        )
    result = evaluate_liq_002_v1(
        initial_balance=inputs["initial_balance"],
        expected_collections=inputs["expected_collections"],
        expected_payments=inputs["expected_payments"],
    )
    result["plan_validation"] = _validated_plan_projection(computation_plan)
    return result


def evaluate_liq_002_v1(
    *, initial_balance: object, expected_collections: object, expected_payments: object
) -> dict[str, object]:
    normalized, errors = _normalize_inputs(
        initial_balance=initial_balance,
        expected_collections=expected_collections,
        expected_payments=expected_payments,
    )
    if errors:
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs=normalized,
            errors=errors,
        )

    opening = normalized["initial_balance"]
    collections = normalized["expected_collections"]
    payments = normalized["expected_payments"]
    closing = opening + collections - payments

    if closing > 0:
        classification = CLASS_POSITIVE_BALANCE
    elif closing == 0:
        classification = CLASS_ZERO_BALANCE
    else:
        classification = CLASS_NEGATIVE_BALANCE

    return _packet(
        status=STATUS_EVALUATED,
        classification=classification,
        inputs=normalized,
        errors=[],
        computed={
            "projected_closing_balance": closing,
            "projected_net_cash_change": collections - payments,
            "total_expected_inflows": collections,
            "total_expected_outflows": payments,
        },
        mathematical_limits={
            "initial_balance_min_inclusive": 0.0,
            "expected_collections_min_inclusive": 0.0,
            "expected_payments_min_inclusive": 0.0,
            "positive_balance_meaning": CLASS_POSITIVE_BALANCE,
            "zero_balance_meaning": CLASS_ZERO_BALANCE,
            "negative_balance_meaning": CLASS_NEGATIVE_BALANCE,
        },
    )


def _normalize_inputs(
    *, initial_balance: object, expected_collections: object, expected_payments: object
) -> tuple[dict[str, float], list[str]]:
    normalized: dict[str, float] = {}
    errors: list[str] = []
    for name, raw_value in (
        ("initial_balance", initial_balance),
        ("expected_collections", expected_collections),
        ("expected_payments", expected_payments),
    ):
        value, error = _parse_number(raw_value)
        if error:
            errors.append(f"{name} {error}")
            continue
        normalized[name] = float(value)
        if value < 0:
            errors.append(f"{name} must be greater than or equal to 0.")
    return normalized, errors


def _parse_number(value: object) -> tuple[Decimal, str | None]:
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


def _validate_computation_plan(computation_plan: object) -> list[str]:
    if not isinstance(computation_plan, dict):
        return ["computation_plan must be an object."]
    expected = {
        "schema_version": COMPUTATION_PLAN_SCHEMA_VERSION,
        "status": PLAN_STATUS_READY,
        "requested_capability": CAPABILITY_REF,
        "pathology_code": PATHOLOGY_CODE,
        "formula_id": FORMULA_REF,
    }
    errors = [
        f"computation_plan {field} must equal {expected_value}."
        for field, expected_value in expected.items()
        if computation_plan.get(field) != expected_value
    ]
    if tuple(computation_plan.get("required_variables") or ()) != _REQUIRED_VARIABLES:
        errors.append("computation_plan required_variables do not match LIQ_002.")
    if computation_plan.get("computation_candidate_ready") is not True:
        errors.append("computation_plan candidate is not ready.")
    if any(
        computation_plan.get(flag)
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    ):
        errors.append("computation_plan safety flags must remain false.")
    return errors


def _validated_plan_projection(computation_plan: object) -> dict[str, object]:
    plan = computation_plan if isinstance(computation_plan, dict) else {}
    return {
        "status": "VALIDATED",
        "schema_version": plan.get("schema_version"),
        "requested_capability": plan.get("requested_capability"),
        "pathology_code": plan.get("pathology_code"),
        "formula_id": plan.get("formula_id"),
        "required_variables": list(plan.get("required_variables") or []),
    }


def _packet(
    *,
    status: str,
    classification: str | None,
    inputs: dict[str, float],
    errors: list[str],
    computed: dict[str, float] | None = None,
    mathematical_limits: dict[str, object] | None = None,
    plan_validation: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pathology_code": PATHOLOGY_CODE,
        "formula_ref": FORMULA_REF,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "classification": classification,
        "inputs": dict(inputs),
        "computed": dict(computed or {}),
        "errors": list(errors),
        "mathematical_limits": dict(mathematical_limits or {}),
        "plan_validation": dict(plan_validation or {}),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "PATHOLOGY_CODE",
    "FORMULA_REF",
    "CAPABILITY_REF",
    "STATUS_EVALUATED",
    "STATUS_INVALID_INPUT",
    "STATUS_PLAN_BLOCKED",
    "CLASS_POSITIVE_BALANCE",
    "CLASS_ZERO_BALANCE",
    "CLASS_NEGATIVE_BALANCE",
    "evaluate_liq_002_v1",
    "evaluate_liq_002_from_computation_plan_v1",
]
