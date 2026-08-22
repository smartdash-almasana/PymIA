"""Deterministic physical-region detection over canonical XLSX evidence.

This module never opens an XLSX file and never infers business meaning. It
only turns the additive physical-row evidence preserved by the canonical
normalizer into region specifications consumed by Service1RegionV1.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Final, Mapping

from pymia.smartpyme.service_1_region_physical_evidence_contracts_v1 import (
    REGION_SHAPE_RECTANGULAR,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PHYSICAL_REGION_DETECTION_V1"
STATUS_READY: Final[str] = "PHYSICAL_REGIONS_READY"
STATUS_UNRESOLVED: Final[str] = "UNRESOLVED"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_TABLE_INVALID: Final[str] = "BLOCK_PHYSICAL_REGION_TABLE_INVALID"
BLOCK_BOUNDARY_UNRESOLVED: Final[str] = "PHYSICAL_REGION_BOUNDARY_UNRESOLVED"

_TOTAL_MARKERS: Final[frozenset[str]] = frozenset(
    {"total", "totales", "subtotal", "subtotales", "sub_total", "sub_totales"}
)


def detect_service_1_physical_regions_v1(
    *,
    normalized_table: Mapping[str, Any],
) -> dict[str, Any]:
    """Detect rectangular regions from canonical physical-row evidence.

    If the canonical table was produced before physical-row evidence existed,
    the function returns one conservative fallback region. When physical rows
    expose a boundary that cannot be distinguished deterministically, it
    returns UNRESOLVED instead of inventing a table boundary.
    """
    if (
        not isinstance(normalized_table, Mapping)
        or normalized_table.get("status") not in {None, "OK"}
    ):
        return _blocked(BLOCK_TABLE_INVALID)

    sheet = str(normalized_table.get("sheet_name") or "").strip()
    headers = [str(value).strip() for value in normalized_table.get("normalized_headers") or []]
    if not sheet or not headers:
        return _blocked(BLOCK_TABLE_INVALID)

    physical_rows = normalized_table.get("physical_rows")
    if not isinstance(physical_rows, list) or not physical_rows:
        return _fallback_single_region(normalized_table)

    rows = _coerce_physical_rows(physical_rows)
    if rows is None:
        return _unresolved("physical_rows_invalid")

    nonempty_rows = [row for row in rows if _has_nonempty_cell(row["cells"])]
    if not nonempty_rows:
        return _unresolved("no_nonempty_physical_rows")

    header_rows: list[dict[str, Any]] = []
    first = nonempty_rows[0]
    first_header = _header_shape(first)
    if first_header is None:
        return _unresolved("first_nonempty_row_is_not_rectangular_header")
    header_rows.append({**first, **first_header})

    for position, row in enumerate(nonempty_rows[1:], start=1):
        if _header_fingerprint(row) in {_header_fingerprint(item) for item in header_rows}:
            continue
        previous = nonempty_rows[position - 1]
        gap_has_separator = _has_blank_row_between(rows, previous["row_number"], row["row_number"])
        following = nonempty_rows[position + 1] if position + 1 < len(nonempty_rows) else None
        previous_width = int(header_rows[-1]["column_end"]) - int(header_rows[-1]["column_start"]) + 1
        shape = _header_shape(row)
        if shape is None:
            continue
        if _looks_like_new_header(
            row=row,
            shape=shape,
            following=following,
            previous_width=previous_width,
            gap_has_separator=gap_has_separator,
        ):
            header_rows.append({**row, **shape})

    specs: list[dict[str, Any]] = []
    for index, header in enumerate(header_rows, start=1):
        next_header_row = (
            int(header_rows[index]["row_number"])
            if index < len(header_rows)
            else None
        )
        segment = [
            row
            for row in rows
            if int(row["row_number"]) > int(header["row_number"])
            and (next_header_row is None or int(row["row_number"]) < next_header_row)
        ]
        spec = _build_region_spec(
            sheet=sheet,
            index=index,
            header=header,
            segment=segment,
        )
        if spec is None:
            return _unresolved(f"region_{index}_boundary_or_shape_ambiguous")
        specs.append(spec)

    if not specs:
        return _unresolved("no_rectangular_region_detected")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "sheet_ref": sheet,
        "region_specs": specs,
        "physical_evidence_preserved": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _build_region_spec(
    *,
    sheet: str,
    index: int,
    header: Mapping[str, Any],
    segment: list[Mapping[str, Any]],
) -> dict[str, Any] | None:
    column_start = int(header["column_start"])
    column_end = int(header["column_end"])
    header_values = list(header["header_values"])
    normalized_headers = [_normalize_header(value) for value in header_values]
    if not normalized_headers or any(not value for value in normalized_headers):
        return None
    if len(set(normalized_headers)) != len(normalized_headers):
        return None

    data_rows: list[int] = []
    excluded_rows: list[int] = []
    separator_rows: list[int] = []
    repeated_header_rows: list[int] = []
    total_rows: list[int] = []

    for row in segment:
        row_number = int(row["row_number"])
        cells = list(row["cells"])
        if not _has_nonempty_cell(cells):
            separator_rows.append(row_number)
            excluded_rows.append(row_number)
            continue
        if _header_fingerprint(row) == _header_fingerprint(header):
            repeated_header_rows.append(row_number)
            excluded_rows.append(row_number)
            continue
        if _is_total_or_subtotal(cells, column_start):
            total_rows.append(row_number)
            excluded_rows.append(row_number)
            continue
        outside = [
            position
            for position, value in enumerate(cells)
            if _clean(value) and not (column_start <= position <= column_end)
        ]
        if outside:
            return None
        if not any(_clean(value) for value in cells[column_start : column_end + 1]):
            excluded_rows.append(row_number)
            continue
        data_rows.append(row_number)

    if not data_rows:
        return None

    return {
        "sheet_ref": sheet,
        "region_ref": f"{sheet}:region:{index}",
        "header_rows": [int(header["row_number"])],
        "first_data_row": min(data_rows),
        "last_data_row": max(data_rows),
        "data_row_numbers": data_rows,
        "column_refs": normalized_headers,
        "physical_column_indexes": list(range(column_start, column_end + 1)),
        "excluded_rows": sorted(
            row
            for row in set(excluded_rows)
            if min(data_rows) <= row <= max(data_rows)
        ),
        "region_shape": REGION_SHAPE_RECTANGULAR,
        "detection_evidence": {
            "detector": SCHEMA_VERSION,
            "header_row": int(header["row_number"]),
            "column_start": column_start,
            "column_end": column_end,
            "separator_rows": separator_rows,
            "repeated_header_rows": repeated_header_rows,
            "total_or_subtotal_rows": total_rows,
            "data_row_numbers": data_rows,
        },
    }


def _header_shape(row: Mapping[str, Any]) -> dict[str, Any] | None:
    cells = list(row["cells"])
    nonempty_positions = [index for index, value in enumerate(cells) if _clean(value)]
    if not nonempty_positions:
        return None
    start = min(nonempty_positions)
    end = max(nonempty_positions)
    header_values = [_clean(value) for value in cells[start : end + 1]]
    if any(not value for value in header_values):
        return None
    normalized = [_normalize_header(value) for value in header_values]
    if any(not value for value in normalized) or len(set(normalized)) != len(normalized):
        return None
    return {
        "column_start": start,
        "column_end": end,
        "header_values": header_values,
    }


def _looks_like_new_header(
    *,
    row: Mapping[str, Any],
    shape: Mapping[str, Any],
    following: Mapping[str, Any] | None,
    previous_width: int,
    gap_has_separator: bool,
) -> bool:
    values = list(shape["header_values"])
    if any(_parse_number(value) is not None or _parse_date(value) is not None for value in values):
        return False
    width = int(shape["column_end"]) - int(shape["column_start"]) + 1
    width_changed = width != previous_width
    following_has_typed_value = bool(
        following
        and any(
            _parse_number(value) is not None or _parse_date(value) is not None
            for value in following["cells"]
            if _clean(value)
        )
    )
    if gap_has_separator and (width_changed or following_has_typed_value):
        return True
    return width_changed and following_has_typed_value


def _fallback_single_region(normalized_table: Mapping[str, Any]) -> dict[str, Any]:
    sheet = str(normalized_table.get("sheet_name") or "").strip()
    headers = [str(value).strip() for value in normalized_table.get("normalized_headers") or []]
    source_rows = [int(value) for value in normalized_table.get("source_row_numbers") or []]
    header_row = int(normalized_table.get("header_row_number") or 1)
    if not sheet or not headers:
        return _blocked(BLOCK_TABLE_INVALID)
    if not source_rows:
        return _unresolved("canonical_physical_rows_unavailable")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "sheet_ref": sheet,
        "region_specs": [
            {
                "sheet_ref": sheet,
                "region_ref": f"{sheet}:region:1",
                "header_rows": [header_row],
                "first_data_row": min(source_rows),
                "last_data_row": max(source_rows),
                "data_row_numbers": source_rows,
                "column_refs": headers,
                "physical_column_indexes": list(range(len(headers))),
                "excluded_rows": [],
                "region_shape": REGION_SHAPE_RECTANGULAR,
                "detection_evidence": {
                    "detector": SCHEMA_VERSION,
                    "mode": "CANONICAL_SINGLE_TABLE_FALLBACK",
                    "physical_evidence_preserved": False,
                },
            }
        ],
        "physical_evidence_preserved": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _coerce_physical_rows(value: list[Any]) -> list[dict[str, Any]] | None:
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            return None
        try:
            row_number = int(item.get("row_number"))
            cells = list(item.get("cells") or [])
            width = int(item.get("physical_width") or len(cells))
        except (TypeError, ValueError):
            return None
        if row_number < 1 or width < 0:
            return None
        result.append(
            {
                "row_number": row_number,
                "cells": [_clean(value) for value in cells],
                "physical_width": width,
            }
        )
    result.sort(key=lambda item: item["row_number"])
    if len({item["row_number"] for item in result}) != len(result):
        return None
    return result


def _header_fingerprint(row: Mapping[str, Any]) -> tuple[str, ...]:
    shape = _header_shape(row)
    return tuple(_normalize_header(value) for value in shape["header_values"]) if shape else ()


def _has_blank_row_between(rows: list[Mapping[str, Any]], start: int, end: int) -> bool:
    return any(
        start < int(row["row_number"]) < end and not _has_nonempty_cell(row["cells"])
        for row in rows
    )


def _has_nonempty_cell(cells: list[Any]) -> bool:
    return any(_clean(value) for value in cells)


def _is_total_or_subtotal(cells: list[Any], column_start: int) -> bool:
    first = _normalize_header(cells[column_start]) if column_start < len(cells) else ""
    return first in _TOTAL_MARKERS


def _normalize_header(value: Any) -> str:
    text = _clean(value).casefold()
    for source, target in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}.items():
        text = text.replace(source, target)
    chars = [char if char.isalnum() else "_" for char in text]
    return "_".join(part for part in "".join(chars).split("_") if part)


def _parse_number(value: Any) -> float | None:
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for candidate in (text, text[:10]):
        try:
            return date.fromisoformat(candidate)
        except ValueError:
            pass
    return None


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _unresolved(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_UNRESOLVED,
        "blocked_reason": BLOCK_BOUNDARY_UNRESOLVED,
        "detail": reason,
        "region_specs": [],
        "physical_evidence_preserved": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "region_specs": [],
        "physical_evidence_preserved": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "BLOCK_TABLE_INVALID",
    "BLOCK_BOUNDARY_UNRESOLVED",
    "detect_service_1_physical_regions_v1",
]
