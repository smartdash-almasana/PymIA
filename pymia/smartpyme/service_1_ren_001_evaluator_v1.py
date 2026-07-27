"""Deterministic evaluator for REN_001 real net margin.

Evaluates only explicit numeric evidence. It does not infer business meaning,
select data sources, authorize runtime, generate a diagnosis, or deliver files.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_REN_001_EVALUATION_V1"
PATHOLOGY_CODE: Final[str] = "REN_001"
FORMULA_REF: Final[str] = "REN_001_margen_neto_real"
CAPABILITY_REF: Final[str] = "net_margin_real"

STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_PLAN_BLOCKED: Final[str] = "PLAN_BLOCKED"

CLASS_POSITIVE_MARGIN: Final[str] = "POSITIVE_MARGIN"
CLASS_BREAK_EVEN: Final[str] = "BREAK_EVEN"
CLASS_NEGATIVE_MARGIN: Final[str] = "NEGATIVE_MARGIN"

_REQUIRED_VARIABLES: Final[tuple[str, str, str]] = (
    "sale_price",
    "costs",
    "taxes",
)


def evaluate_ren_001_from_computation_plan_v1(
    *, computation_plan: object, inputs: object
) -> dict[str, object]:
    """Validate a governed REN_001 plan before evaluating explicit totals."""
    plan_errors = _validate_computation_plan(computation_plan)
    if plan_errors:
        return _packet(
            status=STATUS_PLAN_BLOCKED,
            classification=None,
            inputs={},
            errors=plan_errors,
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
        errors = [f"missing required input: {name}." for name in missing]
        errors.extend(f"unknown input: {name}." for name in unknown)
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs={},
            errors=errors,
            plan_validation=_validated_plan_projection(computation_plan),
        )
    result = evaluate_ren_001_v1(
        sale_price=inputs["sale_price"],
        costs=inputs["costs"],
        taxes=inputs["taxes"],
    )
    result["plan_validation"] = _validated_plan_projection(computation_plan)
    return result


def evaluate_ren_001_v1(
    *, sale_price: object, costs: object, taxes: object
) -> dict[str, object]:
    """Compute real net margin from explicit monetary values.

    Domain:
    - sale_price must be finite and strictly greater than zero;
    - costs and taxes must be finite and greater than or equal to zero;
    - net_margin_amount = sale_price - costs - taxes;
    - net_margin_percentage = net_margin_amount / sale_price * 100.
    """
    normalized, errors = _normalize_inputs(
        sale_price=sale_price,
        costs=costs,
        taxes=taxes,
    )
    if errors:
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs=normalized,
            errors=errors,
        )

    sale = normalized["sale_price"]
    total_costs = normalized["costs"]
    total_taxes = normalized["taxes"]
    margin_amount = sale - total_costs - total_taxes
    margin_percentage = margin_amount / sale * 100.0

    if margin_amount > 0:
        classification = CLASS_POSITIVE_MARGIN
    elif margin_amount == 0:
        classification = CLASS_BREAK_EVEN
    else:
        classification = CLASS_NEGATIVE_MARGIN

    return _packet(
        status=STATUS_EVALUATED,
        classification=classification,
        inputs=normalized,
        errors=[],
        computed={
            "net_margin_amount": margin_amount,
            "net_margin_percentage": margin_percentage,
            "total_outflows": total_costs + total_taxes,
        },
        mathematical_limits={
            "sale_price_min_exclusive": 0.0,
            "costs_min_inclusive": 0.0,
            "taxes_min_inclusive": 0.0,
            "positive_margin_meaning": CLASS_POSITIVE_MARGIN,
            "zero_margin_meaning": CLASS_BREAK_EVEN,
            "negative_margin_meaning": CLASS_NEGATIVE_MARGIN,
        },
    )


def _normalize_inputs(
    *, sale_price: object, costs: object, taxes: object
) -> tuple[dict[str, float], list[str]]:
    normalized: dict[str, float] = {}
    errors: list[str] = []
    for name, raw_value in (
        ("sale_price", sale_price),
        ("costs", costs),
        ("taxes", taxes),
    ):
        value, error = _parse_number(raw_value)
        if error:
            errors.append(f"{name} {error}")
            continue
        normalized[name] = float(value)

    if "sale_price" in normalized and normalized["sale_price"] <= 0:
        errors.append("sale_price must be greater than 0.")
    for name in ("costs", "taxes"):
        if name in normalized and normalized[name] < 0:
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


def _execution_input_payload(computation_plan: object) -> object:
    if isinstance(computation_plan, dict):
        if computation_plan.get("schema_version") == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1":
            return computation_plan
        governed = computation_plan.get("governed_computation_input")
        if isinstance(governed, dict):
            return governed
    return None


def _validate_computation_plan(computation_plan: object) -> list[str]:
    payload = _execution_input_payload(computation_plan)
    if not isinstance(payload, dict):
        return ["governed computation input is required."]
    if payload.get("schema_version") != "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1":
        return ["governed computation input schema is required."]
    expected = {"requested_capability": CAPABILITY_REF, "pathology_code": PATHOLOGY_CODE, "formula_id": FORMULA_REF}
    errors = [f"execution input {field} must equal {expected_value}." for field, expected_value in expected.items() if payload.get(field) != expected_value]
    if tuple(payload.get("required_variables") or ()) != _REQUIRED_VARIABLES:
        errors.append("execution input required_variables do not match REN_001.")
    if any(payload.get(flag) is not False for flag in ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated")):
        errors.append("execution input safety flags must remain false.")
    return errors


def _validated_plan_projection(computation_plan: object) -> dict[str, object]:
    payload = _execution_input_payload(computation_plan)
    plan = payload if isinstance(payload, dict) else {}
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
    "CLASS_POSITIVE_MARGIN",
    "CLASS_BREAK_EVEN",
    "CLASS_NEGATIVE_MARGIN",
    "evaluate_ren_001_v1",
    "evaluate_ren_001_from_computation_plan_v1",
]
