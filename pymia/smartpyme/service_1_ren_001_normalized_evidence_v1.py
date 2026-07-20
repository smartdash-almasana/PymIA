"""Resolve owner-confirmed normalized evidence for REN_001."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Final

from pymia.smartpyme.service_1_ren_001_evaluator_v1 import (
    evaluate_ren_001_from_computation_plan_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REN_001_NORMALIZED_EVIDENCE_V1"
STATUS_EVIDENCE_BLOCKED: Final[str] = "EVIDENCE_BLOCKED"
_REQUIRED_VARIABLES: Final[tuple[str, str, str]] = ("sale_price", "costs", "taxes")


def evaluate_ren_001_from_normalized_tables_v1(
    *, computation_plan: object, normalized_tables: object, column_refs: object
) -> dict[str, object]:
    if not isinstance(computation_plan, dict):
        return _blocked(["computation_plan must be an object."])
    if not isinstance(normalized_tables, list) or not normalized_tables:
        return _blocked(["normalized_tables must be a non-empty list."])
    if not isinstance(column_refs, list) or not column_refs:
        return _blocked(["column_refs must be a non-empty list."])

    source_bindings = computation_plan.get("source_bindings")
    if not isinstance(source_bindings, dict):
        return _blocked(["computation_plan source_bindings must be an object."])

    tables_by_sheet: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for raw_table in normalized_tables:
        if not isinstance(raw_table, dict):
            errors.append("normalized table entries must be objects.")
            continue
        sheet_name = str(raw_table.get("sheet_name") or "").strip()
        if not sheet_name:
            errors.append("normalized table sheet_name is required.")
            continue
        if sheet_name in tables_by_sheet:
            errors.append(f"duplicate normalized table for sheet: {sheet_name}.")
            continue
        tables_by_sheet[sheet_name] = raw_table
    if errors:
        return _blocked(errors)

    totals: dict[str, float] = {}
    aggregation_sources: dict[str, dict[str, object]] = {}
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
            errors.append("REN_001 source columns must cover the same row count.")
            continue

        total = Decimal("0")
        for row_index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row {row_index} in {sheet_name} must be an object.")
                continue
            value, value_error = _parse_nonnegative(row.get(normalized_column))
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
        return _blocked(
            errors,
            aggregation={"sources": aggregation_sources, "row_count": expected_row_count},
        )

    result = evaluate_ren_001_from_computation_plan_v1(
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


def _parse_nonnegative(value: object) -> tuple[Decimal, str | None]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0"), "value is required."
    if isinstance(value, bool):
        return Decimal("0"), "value must be numeric."
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0"), "value must be numeric."
    if not number.is_finite():
        return Decimal("0"), "value must be finite."
    if number < 0:
        return Decimal("0"), "value must be greater than or equal to 0."
    return number, None


def _blocked(
    errors: list[str], *, aggregation: dict[str, object] | None = None
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_EVIDENCE_BLOCKED,
        "errors": list(errors),
        "aggregation": dict(aggregation or {}),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_EVIDENCE_BLOCKED",
    "evaluate_ren_001_from_normalized_tables_v1",
]
