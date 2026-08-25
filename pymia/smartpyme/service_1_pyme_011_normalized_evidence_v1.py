"""Resolve confirmed normalized evidence for PYME_011 DSO."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Final

from pymia.contracts.formula_contract import FormulaStatus, MathPrimitiveInput, MathPrimitiveOperation
from pymia.services.formula_engine_service import FormulaEngineService

from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import evaluate_pyme_011_from_computation_plan_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_PYME_011_NORMALIZED_EVIDENCE_V1"
STATUS_EVIDENCE_BLOCKED: Final[str] = "EVIDENCE_BLOCKED"
_REQUIRED_VARIABLES: Final[tuple[str, str, str]] = ("accounts_receivable", "sales", "days")


def evaluate_pyme_011_from_normalized_tables_v1(*, computation_plan: object, normalized_tables: object, column_refs: object) -> dict[str, object]:
    if not isinstance(computation_plan, dict):
        return _blocked(["computation_plan must be an object."])
    if not isinstance(normalized_tables, list) or not normalized_tables:
        return _blocked(["normalized_tables must be a non-empty list."])
    if not isinstance(column_refs, list) or not column_refs:
        return _blocked(["column_refs must be a non-empty list."])
    source_bindings = computation_plan.get("source_bindings")
    if not isinstance(source_bindings, dict):
        return _blocked(["computation_plan source_bindings must be an object."])

    tables: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for raw in normalized_tables:
        if not isinstance(raw, dict):
            errors.append("normalized table entries must be objects.")
            continue
        sheet = str(raw.get("sheet_name") or "").strip()
        if not sheet or sheet in tables:
            errors.append("normalized table sheet_name must be present and unique.")
            continue
        tables[sheet] = raw
    if errors:
        return _blocked(errors)

    inputs: dict[str, float] = {}
    sources: dict[str, dict[str, object]] = {}
    for variable in _REQUIRED_VARIABLES:
        source_column = str(source_bindings.get(variable) or "").strip()
        matches = [ref for ref in column_refs if isinstance(ref, dict) and str(ref.get("column_name") or "").strip() == source_column]
        if len(matches) != 1:
            errors.append(f"source binding for {variable} must resolve exactly once: {source_column}.")
            continue
        ref = matches[0]
        sheet = str(ref.get("sheet_name") or "").strip()
        normalized_column = str(ref.get("normalized_column_name") or ref.get("column_name") or "").strip()
        rows = (tables.get(sheet) or {}).get("rows")
        if not isinstance(rows, list) or not rows:
            errors.append(f"normalized rows must be a non-empty list for sheet: {sheet}.")
            continue
        values: list[Decimal] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row {index} in {sheet} must be an object.")
                continue
            raw_value = row.get(normalized_column)
            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                continue
            value, error = _number(raw_value)
            if error:
                errors.append(f"{sheet}.{normalized_column} row {index}: {error}")
            else:
                values.append(value)
        if not values:
            errors.append(f"{variable} requires at least one confirmed numeric value.")
            continue
        operation = (
            MathPrimitiveOperation.SINGLE_VALUE
            if variable == "days"
            else MathPrimitiveOperation.SUM
        )
        primitive = FormulaEngineService().calculate_math_primitive(
            MathPrimitiveInput(
                operation=operation,
                values=[float(value) for value in values],
                source_refs=[f"{sheet}.{source_column}"],
            )
        )
        if primitive.status != FormulaStatus.OK or primitive.value is None:
            if variable == "days":
                errors.append("days must resolve to one consistent confirmed period value.")
            else:
                errors.append(
                    f"{variable} aggregation blocked: {primitive.blocking_reason or 'math primitive blocked'}."
                )
            continue
        inputs[variable] = float(primitive.value)
        aggregation = operation.value
        sources[variable] = {"sheet_name": sheet, "column_name": source_column, "normalized_column_name": normalized_column, "value_count": len(values), "aggregation": aggregation}

    if errors:
        return _blocked(errors, aggregation={"sources": sources, "sample_based": False})
    result = evaluate_pyme_011_from_computation_plan_v1(computation_plan=computation_plan, inputs=inputs)
    result["aggregation"] = {"status": "AGGREGATED", "sources": sources, "sample_based": False}
    return result


def _number(value: object) -> tuple[Decimal, str | None]:
    if isinstance(value, bool):
        return Decimal("0"), "value must be numeric."
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0"), "value must be numeric."
    if not number.is_finite():
        return Decimal("0"), "value must be finite."
    return number, None


def _blocked(errors: list[str], *, aggregation: dict[str, object] | None = None) -> dict[str, object]:
    return {"schema_version": SCHEMA_VERSION, "status": STATUS_EVIDENCE_BLOCKED, "errors": list(errors), "aggregation": dict(aggregation or {}), "runtime_authorized": False, "tool_execution_authorized": False, "product_ready": False, "delivery_authorized": False, "diagnosis_generated": False}


__all__ = ["SCHEMA_VERSION", "STATUS_EVIDENCE_BLOCKED", "evaluate_pyme_011_from_normalized_tables_v1"]
