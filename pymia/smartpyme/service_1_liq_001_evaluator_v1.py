"""Deterministic evaluator for LIQ_001 sold-versus-collected mismatch.

This module evaluates only explicit numeric evidence. It does not infer business
meaning, select data sources, authorize runtime, or generate an autonomous final
diagnosis. The owner-confirmed semantic layer remains responsible for bindings.
"""
from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Any, Final

from pymia.contracts.formula_contract import FormulaInput, FormulaStatus, calculate_formula

SCHEMA_VERSION: Final[str] = "SERVICE_1_LIQ_001_EVALUATION_V1"
PATHOLOGY_CODE: Final[str] = "LIQ_001"
FORMULA_REF: Final[str] = "LIQ_001_vendido_cobrado"
CAPABILITY_REF: Final[str] = "sold_vs_collected_gap"

STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_PLAN_BLOCKED: Final[str] = "PLAN_BLOCKED"
STATUS_EVIDENCE_BLOCKED: Final[str] = "EVIDENCE_BLOCKED"
PLAN_VALIDATED: Final[str] = "VALIDATED"

CLASS_NO_ACTIVITY: Final[str] = "NO_ACTIVITY"
CLASS_NO_GAP: Final[str] = "NO_GAP"
CLASS_SALES_PENDING_COLLECTION: Final[str] = "SALES_PENDING_COLLECTION"
CLASS_COLLECTIONS_EXCEED_PERIOD_SALES: Final[str] = "COLLECTIONS_EXCEED_PERIOD_SALES"
CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES: Final[str] = "COLLECTIONS_WITHOUT_PERIOD_SALES"

_REQUIRED_VARIABLES: Final[tuple[str, str]] = ("sold_amount", "collected_amount")


def evaluate_liq_001_from_normalized_tables_v1(
    *, computation_plan: object, normalized_tables: object, column_refs: object
) -> dict[str, object]:
    """Aggregate every normalized row selected by the governed LIQ_001 plan.

    Resolution is exact and deterministic:
    - the plan must be a validated LIQ_001 computation candidate;
    - each required variable must resolve to exactly one confirmed column ref;
    - the referenced sheet and normalized header must exist exactly once;
    - every participating row value must be present, numeric, finite and non-negative.

    No sample values, aliases, thresholds or inferred mappings are accepted here.
    """
    plan_errors = _validate_computation_plan(computation_plan)
    if plan_errors:
        return _packet(
            status=STATUS_PLAN_BLOCKED,
            classification=None,
            inputs={},
            errors=plan_errors,
            plan_validation={"status": STATUS_PLAN_BLOCKED},
        )
    if not isinstance(normalized_tables, list) or not normalized_tables:
        return _evidence_blocked(
            computation_plan,
            ["normalized_tables must be a non-empty list."],
        )
    if not isinstance(column_refs, list) or not column_refs:
        return _evidence_blocked(
            computation_plan,
            ["column_refs must be a non-empty list."],
        )

    plan = _execution_input_payload(computation_plan)
    source_bindings = plan.get("source_bindings") if isinstance(plan, dict) else None
    if not isinstance(source_bindings, dict):
        return _evidence_blocked(
            computation_plan,
            ["computation_plan source_bindings must be an object."],
        )

    tables_by_sheet: dict[str, dict[str, Any]] = {}
    table_errors: list[str] = []
    for raw_table in normalized_tables:
        if not isinstance(raw_table, dict):
            table_errors.append("normalized table entries must be objects.")
            continue
        sheet_name = str(raw_table.get("sheet_name") or "").strip()
        if not sheet_name:
            table_errors.append("normalized table sheet_name is required.")
            continue
        if sheet_name in tables_by_sheet:
            table_errors.append(f"duplicate normalized table for sheet: {sheet_name}.")
            continue
        tables_by_sheet[sheet_name] = raw_table
    if table_errors:
        return _evidence_blocked(computation_plan, table_errors)

    totals: dict[str, float] = {}
    aggregation_sources: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    expected_row_count: int | None = None

    for variable_name in _REQUIRED_VARIABLES:
        source_column = str(source_bindings.get(variable_name) or "").strip()
        if not source_column:
            errors.append(f"missing source binding for {variable_name}.")
            continue
        matches = [
            ref
            for ref in column_refs
            if isinstance(ref, dict)
            and str(ref.get("column_name") or "").strip() == source_column
        ]
        if len(matches) != 1:
            errors.append(
                f"source binding for {variable_name} must resolve exactly once: {source_column}."
            )
            continue
        ref = matches[0]
        sheet_name = str(ref.get("sheet_name") or "").strip()
        normalized_column = str(
            ref.get("normalized_column_name") or ref.get("column_name") or ""
        ).strip()
        table = tables_by_sheet.get(sheet_name)
        if table is None:
            errors.append(f"normalized table missing for sheet: {sheet_name}.")
            continue
        rows = table.get("rows")
        if not isinstance(rows, list):
            errors.append(f"normalized rows must be a list for sheet: {sheet_name}.")
            continue
        if expected_row_count is None:
            expected_row_count = len(rows)
        elif len(rows) != expected_row_count:
            errors.append("LIQ_001 source columns must cover the same row count.")
            continue

        total = Decimal("0")
        for row_index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row {row_index} in {sheet_name} must be an object.")
                continue
            raw_value = row.get(normalized_column)
            value, value_error = _parse_normalized_amount(raw_value)
            if value_error:
                errors.append(
                    f"{sheet_name}.{normalized_column} row {row_index}: {value_error}"
                )
                continue
            total += value
        totals[variable_name] = float(total)
        aggregation_sources[variable_name] = {
            "sheet_name": sheet_name,
            "column_name": source_column,
            "normalized_column_name": normalized_column,
            "row_count": len(rows),
        }

    if errors:
        return _evidence_blocked(
            computation_plan,
            errors,
            aggregation={
                "sources": aggregation_sources,
                "row_count": expected_row_count,
            },
        )

    result = evaluate_liq_001_from_computation_plan_v1(
        computation_plan=computation_plan,
        inputs=totals,
    )
    result["aggregation"] = {
        "status": "AGGREGATED",
        "sources": aggregation_sources,
        "row_count": expected_row_count,
        "sample_based": False,
    }
    return result


def evaluate_liq_001_from_computation_plan_v1(
    *, computation_plan: object, inputs: object
) -> dict[str, object]:
    """Validate one governed LIQ_001 plan before evaluating explicit totals.

    This boundary does not extract or infer values from workbook samples. The
    caller must provide explicit period totals for exactly the variables governed
    by the validated plan.
    """
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

    result = evaluate_liq_001_v1(
        sold_amount=inputs["sold_amount"],
        collected_amount=inputs["collected_amount"],
    )
    result["plan_validation"] = _validated_plan_projection(computation_plan)
    return result


def evaluate_liq_001_v1(*, sold_amount: object, collected_amount: object) -> dict[str, object]:
    """Evaluate LIQ_001 from explicit period totals.

    Mathematical domain:
    - both inputs must be finite real numbers;
    - both inputs must be greater than or equal to zero;
    - ``gap = sold_amount - collected_amount``;
    - ratios are undefined when ``sold_amount == 0``.
    """
    normalized, errors = _normalize_inputs(
        sold_amount=sold_amount,
        collected_amount=collected_amount,
    )
    if errors:
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs=normalized,
            errors=errors,
        )

    sold = normalized["sold_amount"]
    collected = normalized["collected_amount"]
    kernel_result = calculate_formula(
        FORMULA_REF,
        [
            FormulaInput(name="sold_amount", value=sold, source_refs=["LIQ_001:sold_amount"]),
            FormulaInput(name="collected_amount", value=collected, source_refs=["LIQ_001:collected_amount"]),
        ],
    )
    if kernel_result.status != FormulaStatus.OK or kernel_result.value is None:
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs=normalized,
            errors=[kernel_result.blocking_reason or "LIQ_001 formula calculation blocked."],
        )
    gap = kernel_result.value

    if sold == 0:
        if collected == 0:
            classification = CLASS_NO_ACTIVITY
        else:
            classification = CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES
        collection_ratio = None
        gap_ratio = None
    else:
        collection_ratio = collected / sold
        gap_ratio = gap / sold
        if gap > 0:
            classification = CLASS_SALES_PENDING_COLLECTION
        elif gap == 0:
            classification = CLASS_NO_GAP
        else:
            classification = CLASS_COLLECTIONS_EXCEED_PERIOD_SALES

    return _packet(
        status=STATUS_EVALUATED,
        classification=classification,
        inputs=normalized,
        computed={
            "gap_amount": gap,
            "collection_ratio": collection_ratio,
            "gap_ratio": gap_ratio,
        },
        mathematical_limits={
            "sold_amount_min_inclusive": 0.0,
            "collected_amount_min_inclusive": 0.0,
            "gap_positive_meaning": CLASS_SALES_PENDING_COLLECTION,
            "gap_zero_meaning": CLASS_NO_GAP,
            "gap_negative_meaning": CLASS_COLLECTIONS_EXCEED_PERIOD_SALES,
            "ratios_defined_when": "sold_amount > 0",
        },
    )


def _parse_normalized_amount(value: object) -> tuple[Decimal, str | None]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0"), "value is required."
    if isinstance(value, bool):
        return Decimal("0"), "value must be numeric."
    text = str(value).strip()
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError):
        return Decimal("0"), "value must be numeric."
    if not number.is_finite():
        return Decimal("0"), "value must be finite."
    if number < 0:
        return Decimal("0"), "value must be greater than or equal to 0."
    return number, None


def _evidence_blocked(
    computation_plan: object,
    errors: list[str],
    *,
    aggregation: dict[str, object] | None = None,
) -> dict[str, object]:
    packet = _packet(
        status=STATUS_EVIDENCE_BLOCKED,
        classification=None,
        inputs={},
        errors=errors,
        plan_validation=_validated_plan_projection(computation_plan),
    )
    packet["aggregation"] = dict(aggregation or {})
    return packet


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
    expected = {
        "requested_capability": CAPABILITY_REF,
        "pathology_code": PATHOLOGY_CODE,
        "formula_id": FORMULA_REF,
    }
    errors = [f"execution input {field} must equal {expected_value}." for field, expected_value in expected.items() if payload.get(field) != expected_value]
    if tuple(payload.get("required_variables") or ()) != _REQUIRED_VARIABLES:
        errors.append("execution input required_variables do not match LIQ_001.")
    if any(payload.get(flag) is not False for flag in ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated")):
        errors.append("execution input safety flags must remain false.")
    return errors


def _validated_plan_projection(computation_plan: object) -> dict[str, object]:
    payload = _execution_input_payload(computation_plan)
    plan = payload if isinstance(payload, dict) else {}
    return {
        "status": PLAN_VALIDATED,
        "schema_version": plan.get("schema_version"),
        "requested_capability": plan.get("requested_capability"),
        "pathology_code": plan.get("pathology_code"),
        "formula_id": plan.get("formula_id"),
        "required_variables": list(plan.get("required_variables") or []),
    }


def _normalize_inputs(
    *, sold_amount: object, collected_amount: object
) -> tuple[dict[str, float], list[str]]:
    normalized: dict[str, float] = {}
    errors: list[str] = []
    for field_name, value in (
        ("sold_amount", sold_amount),
        ("collected_amount", collected_amount),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{field_name} must be numeric.")
            continue
        number = float(value)
        if not math.isfinite(number):
            errors.append(f"{field_name} must be finite.")
            continue
        normalized[field_name] = number
        if number < 0:
            errors.append(f"{field_name} must be greater than or equal to 0.")
    return normalized, errors


def _packet(
    *,
    status: str,
    classification: str | None,
    inputs: dict[str, float],
    computed: dict[str, object] | None = None,
    mathematical_limits: dict[str, object] | None = None,
    errors: list[str] | None = None,
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
        "mathematical_limits": dict(mathematical_limits or {}),
        "errors": list(errors or []),
        "plan_validation": dict(plan_validation or {}),
        "runtime_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "CAPABILITY_REF",
    "CLASS_COLLECTIONS_EXCEED_PERIOD_SALES",
    "CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES",
    "CLASS_NO_ACTIVITY",
    "CLASS_NO_GAP",
    "CLASS_SALES_PENDING_COLLECTION",
    "FORMULA_REF",
    "PATHOLOGY_CODE",
    "PLAN_VALIDATED",
    "SCHEMA_VERSION",
    "STATUS_EVALUATED",
    "STATUS_EVIDENCE_BLOCKED",
    "STATUS_INVALID_INPUT",
    "STATUS_PLAN_BLOCKED",
    "evaluate_liq_001_from_computation_plan_v1",
    "evaluate_liq_001_from_normalized_tables_v1",
    "evaluate_liq_001_v1",
]
