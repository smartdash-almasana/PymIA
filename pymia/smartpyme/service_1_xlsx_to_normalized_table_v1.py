from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
from openpyxl.utils import get_column_letter

from openpyxl import load_workbook

from pymia.smartpyme.service_1_normalized_table_v1 import (
    NormalizedTableV1,
    build_normalized_table_v1,
)

_EMPTY_SHEET_ERROR = "XLSX sheet has no non-empty rows."


def read_xlsx_to_normalized_table_v1(
    xlsx_path: str | Path,
    *,
    sheet_name: str | None = None,
) -> NormalizedTableV1:
    """Read one worksheet through the canonical XLSX parser.

    With ``sheet_name`` omitted, the first non-empty worksheet is returned,
    preserving the historical single-sheet contract. The workbook is always
    closed before this function returns.
    """
    selected = (sheet_name,) if sheet_name is not None else None
    tables = read_xlsx_to_normalized_tables_v1(xlsx_path, sheet_names=selected)
    if not tables:
        return _blocked(str(Path(xlsx_path)), sheet_name, "XLSX workbook has no readable sheets.")
    return tables[0]


def read_xlsx_to_normalized_tables_v1(
    xlsx_path: str | Path,
    *,
    sheet_names: Iterable[str] | None = None,
) -> list[NormalizedTableV1]:
    """Read every selected non-empty worksheet using one canonical parser.

    ``sheet_names=None`` means all non-empty workbook sheets in workbook order.
    Explicit selection preserves the requested order and fails closed when a
    requested sheet is missing, duplicated or empty.
    """
    path = Path(xlsx_path)
    source_path = str(path)

    if not path.exists() or not path.is_file():
        return [_blocked(source_path, None, "File not found.")]
    if path.suffix.lower() != ".xlsx":
        return [_blocked(source_path, None, "Only .xlsx files are accepted.")]

    normalized_selection: tuple[str, ...] | None = None
    if sheet_names is not None:
        cleaned = tuple(str(name).strip() for name in sheet_names if str(name).strip())
        if not cleaned:
            return [_blocked(source_path, None, "At least one sheet name is required.")]
        if len(set(cleaned)) != len(cleaned):
            return [_blocked(source_path, None, "Duplicate sheet names are not allowed.")]
        normalized_selection = cleaned

    try:
        # One canonical ingestion, with the formula view and the cached-value
        # view aligned by physical worksheet/cell. This is deliberately not a
        # second parser or pipeline.
        workbook = load_workbook(path, data_only=False, read_only=True)
        cached_workbook = load_workbook(path, data_only=True, read_only=True)
    except Exception as exc:
        return [_blocked(source_path, None, str(exc))]

    try:
        if normalized_selection is not None:
            missing = [name for name in normalized_selection if name not in workbook.sheetnames]
            if missing:
                return [
                    _blocked(
                        source_path,
                        missing[0],
                        "Sheet not found: " + ", ".join(missing),
                    )
                ]
            worksheets = [(workbook[name], cached_workbook[name]) for name in normalized_selection]
            return [
                _normalize_worksheet(source_path=source_path, worksheet=worksheet, cached_worksheet=cached)
                for worksheet, cached in worksheets
            ]

        tables: list[NormalizedTableV1] = []
        for worksheet in workbook.worksheets:
            table = _normalize_worksheet(source_path=source_path, worksheet=worksheet, cached_worksheet=cached_workbook[worksheet.title])
            if _EMPTY_SHEET_ERROR in table["blocking_errors"]:
                continue
            tables.append(table)
        if tables:
            return tables
        return [_blocked(source_path, None, "XLSX workbook has no non-empty rows.")]
    finally:
        workbook.close()
        cached_workbook.close()


def _normalize_worksheet(*, source_path: str, worksheet: Any, cached_worksheet: Any) -> NormalizedTableV1:
    selected_sheet_name = worksheet.title
    materialized_rows: list[list[Any]] = []
    cached_rows: list[list[Any]] = []
    physical_cells: list[dict[str, Any]] = []
    cells_by_row: list[list[dict[str, Any]]] = []
    for row_number, (row, cached_row) in enumerate(
        zip(worksheet.iter_rows(), cached_worksheet.iter_rows()), start=1
    ):
        row_cells = list(row)
        cached_cells = list(cached_row)
        materialized_rows.append([_display_value(cell, cached_cells[index] if index < len(cached_cells) else None) for index, cell in enumerate(row_cells)])
        cached_rows.append([cached_cells[index].value if index < len(cached_cells) else None for index in range(len(row_cells))])
        row_records: list[dict[str, Any]] = []
        for column_number, cell in enumerate(row_cells, start=1):
            cached_cell = cached_cells[column_number - 1] if column_number <= len(cached_cells) else None
            formula = cell.value if cell.data_type == "f" or (isinstance(cell.value, str) and cell.value.startswith("=")) else None
            record = {
                "coordinate": getattr(cell, "coordinate", None) or f"{get_column_letter(column_number)}{row_number}",
                "sheet_name": selected_sheet_name,
                "row_number": row_number,
                "column_number": column_number,
                "column_letter": get_column_letter(column_number),
                "value": _display_value(cell, cached_cell),
                "formula": formula,
                "cached_value": cached_cell.value if cached_cell is not None and formula else None,
                "data_type": str(cell.data_type or ""),
            }
            physical_cells.append(record)
            row_records.append(record)
        cells_by_row.append(row_records)
    physical_rows = [
        {
            "row_number": row_number,
            "cells": [_clean(value) for value in raw_row],
            "physical_width": len(raw_row),
            "cell_records": cells_by_row[row_number - 1],
        }
        for row_number, raw_row in enumerate(materialized_rows, start=1)
    ]
    physical_max_column = max((item["physical_width"] for item in physical_rows), default=0)
    physical_max_row = len(physical_rows)
    header_index, header_candidates, header_error = _detect_header(materialized_rows)

    if header_index is None:
        return build_normalized_table_v1(
            source_kind="xlsx",
            source_path=source_path,
            sheet_name=selected_sheet_name,
            headers=[],
            rows=[],
            blocking_errors=[_EMPTY_SHEET_ERROR],
            physical_rows=physical_rows,
            physical_max_column=physical_max_column,
            physical_max_row=physical_max_row,
            physical_cells=physical_cells,
            header_candidates=header_candidates,
        )

    raw_headers = _trim_trailing_empty(materialized_rows[header_index])
    headers = [_clean(value) for value in raw_headers]
    if header_error or not headers or any(not header for header in headers):
        return build_normalized_table_v1(
            source_kind="xlsx",
            source_path=source_path,
            sheet_name=selected_sheet_name,
            headers=headers,
            rows=[],
            blocking_errors=list(dict.fromkeys(["XLSX headers are missing or incomplete.", *( [header_error] if header_error else [] )])),
            physical_rows=physical_rows,
            physical_max_column=physical_max_column,
            physical_max_row=physical_max_row,
            physical_cells=physical_cells,
            header_candidates=header_candidates,
        )

    rows: list[dict[str, Any]] = []
    source_row_numbers: list[int] = []
    warnings: list[str] = []
    width = len(headers)

    for row_number, raw_row in enumerate(
        materialized_rows[header_index + 1 :], start=header_index + 2
    ):
        if _is_empty_row(raw_row):
            continue
        if _last_non_empty_index(raw_row[:width]) < width - 1:
            warnings.append(f"Row {row_number} has fewer cells than headers.")
        if any(_clean(value) for value in raw_row[width:]):
            warnings.append(
                f"Row {row_number} has more cells than headers; extra cells ignored."
            )
        fitted = _fit_width(raw_row, width)
        rows.append({headers[index]: _clean(fitted[index]) for index in range(width)})
        source_row_numbers.append(row_number)

    return build_normalized_table_v1(
        source_kind="xlsx",
        source_path=source_path,
        sheet_name=selected_sheet_name,
        headers=headers,
        rows=rows,
        warnings=warnings,
        header_row_number=header_index + 1,
        source_row_numbers=source_row_numbers,
        physical_rows=physical_rows,
        physical_max_column=physical_max_column,
        physical_max_row=physical_max_row,
        physical_cells=physical_cells,
        header_candidates=header_candidates,
    )


def _blocked(source_path: str, sheet_name: str | None, message: str) -> NormalizedTableV1:
    return build_normalized_table_v1(
        source_kind="xlsx",
        source_path=source_path,
        sheet_name=sheet_name,
        headers=[],
        rows=[],
        blocking_errors=[message],
    )


def _detect_header(rows: list[list[Any]]) -> tuple[int | None, list[dict[str, Any]], str | None]:
    non_empty = [i for i, row in enumerate(rows) if not _is_empty_row(row)]
    if not non_empty:
        return None, [], None
    candidates: list[dict[str, Any]] = []
    for index in non_empty:
        trimmed = _trim_trailing_empty(rows[index])
        width = len(trimmed)
        if width == 0:
            continue
        nonempty = sum(bool(_clean(v)) for v in trimmed)
        textual = sum(isinstance(v, str) and bool(_clean(v)) for v in trimmed)
        has_interior_blank = any(not _clean(v) for v in trimmed)
        if width > 1 and textual < width and not has_interior_blank:
            continue
        below = rows[index + 1 : index + 4]
        data_support = sum(1 for row in below if not _is_empty_row(row) and any(not isinstance(v, str) or _looks_like_data(v) for v in row))
        score = width * 100 + nonempty * 10 + textual + data_support * 20
        candidates.append({"row_number": index + 1, "score": score, "width": width, "headers": [_clean(v) for v in trimmed]})
    if not candidates:
        return None, [], None
    candidates.sort(key=lambda item: (-int(item["width"]), -int(item["score"]), int(item["row_number"])))
    best = candidates[0]
    # A row with a blank interior cell is an explicit malformed header, not a
    # reason to reinterpret a later data row as the header.
    raw_best = rows[int(best["row_number"]) - 1]
    trimmed_best = _trim_trailing_empty(raw_best)
    if any(not _clean(value) for value in trimmed_best):
        return int(best["row_number"]) - 1, candidates[:5], "HEADER_AMBIGUOUS"
    if len(candidates) > 1 and int(best["width"]) > 1 and int(candidates[1]["score"]) == int(best["score"]):
        # Directional digit-evidence tie-break: when the earliest top-tied row
        # carries strictly fewer data-like cells (non-string values or strings
        # containing digits) than the next tied row, the earlier row is the
        # header and the tie resolves. Digit-symmetric ties (e.g. title row vs
        # header row, both digit-free) keep the veto. This never prefers a
        # later row and never weakens the veto for genuinely ambiguous ties.
        best_row = rows[int(best["row_number"]) - 1]
        second_row = rows[int(candidates[1]["row_number"]) - 1]
        if _data_like_cells(best_row) < _data_like_cells(second_row):
            return int(best["row_number"]) - 1, candidates[:5], None
        return None, candidates[:5], "HEADER_AMBIGUOUS"
    return int(best["row_number"]) - 1, candidates[:5], None


def _data_like_cells(row: list[Any]) -> int:
    """Count non-blank cells that look like data rather than header labels."""
    count = 0
    for value in row:
        if not isinstance(value, str):
            if _clean(value):
                count += 1
        elif any(ch.isdigit() for ch in value):
            count += 1
    return count


def _display_value(cell: Any, cached_cell: Any) -> Any:
    value = getattr(cell, "value", None)
    if getattr(cell, "data_type", None) == "f" or (isinstance(value, str) and value.startswith("=")):
        cached = getattr(cached_cell, "value", None) if cached_cell is not None else None
        return cached if cached is not None else value
    return value


def _looks_like_data(value: Any) -> bool:
    text = _clean(value)
    return bool(text) and (not isinstance(value, str) or any(ch.isdigit() for ch in text))


def _is_empty_row(row: list[Any]) -> bool:
    return all(not _clean(value) for value in row)


def _trim_trailing_empty(row: list[Any]) -> list[Any]:
    last_index = _last_non_empty_index(row)
    if last_index < 0:
        return []
    return row[: last_index + 1]


def _last_non_empty_index(row: list[Any]) -> int:
    for index in range(len(row) - 1, -1, -1):
        if _clean(row[index]):
            return index
    return -1


def _fit_width(row: list[Any], width: int) -> list[Any]:
    if len(row) < width:
        return row + [""] * (width - len(row))
    return row[:width]


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "read_xlsx_to_normalized_table_v1",
    "read_xlsx_to_normalized_tables_v1",
]
