from __future__ import annotations

from typing import Any, Literal, TypedDict

SourceKind = Literal["csv", "xlsx"]
TableStatus = Literal["OK", "BLOCKED"]


class NormalizedTableV1(TypedDict):
    schema_version: str
    service_name: str
    status: TableStatus
    source_kind: SourceKind
    source_path: str
    sheet_name: str | None
    headers: list[str]
    normalized_headers: list[str]
    rows: list[dict[str, str]]
    header_row_number: int | None
    source_row_numbers: list[int]
    row_count: int
    column_count: int
    warnings: list[str]
    blocking_errors: list[str]
    runtime_authorized: Literal[False]


def build_normalized_table_v1(
    *,
    source_kind: SourceKind,
    source_path: str,
    headers: list[str],
    rows: list[dict[str, Any]],
    sheet_name: str | None = None,
    warnings: list[str] | None = None,
    blocking_errors: list[str] | None = None,
    header_row_number: int | None = 1,
    source_row_numbers: list[int] | None = None,
) -> NormalizedTableV1:
    clean_headers = [_clean(value) for value in headers]
    normalized_headers = [_normalize_header(value) for value in clean_headers]
    errors = list(blocking_errors or [])
    notes = list(warnings or [])

    if not clean_headers or any(not value for value in clean_headers):
        errors.append("headers_required")

    duplicates = _duplicates(normalized_headers)
    if duplicates:
        errors.append("duplicate_headers:" + ",".join(duplicates))

    normalized_rows: list[dict[str, str]] = []
    resolved_source_rows = list(source_row_numbers) if source_row_numbers is not None else list(range((header_row_number or 1) + 1, (header_row_number or 1) + 1 + len(rows)))
    if len(resolved_source_rows) != len(rows) or any(int(v) < 1 for v in resolved_source_rows) or len(set(resolved_source_rows)) != len(resolved_source_rows):
        errors.append("invalid_source_row_numbers")
    if header_row_number is not None and int(header_row_number) < 1:
        errors.append("invalid_header_row_number")
    if not errors:
        for row in rows:
            normalized_rows.append(
                {
                    normalized_header: _clean(row.get(header, row.get(normalized_header, "")))
                    for header, normalized_header in zip(clean_headers, normalized_headers)
                }
            )

    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": "BLOCKED" if errors else "OK",
        "source_kind": source_kind,
        "source_path": source_path,
        "sheet_name": sheet_name,
        "headers": clean_headers,
        "normalized_headers": normalized_headers,
        "rows": normalized_rows,
        "header_row_number": int(header_row_number) if header_row_number is not None else None,
        "source_row_numbers": [int(v) for v in resolved_source_rows] if not errors else [],
        "row_count": len(normalized_rows),
        "column_count": len(clean_headers),
        "warnings": list(dict.fromkeys(notes)),
        "blocking_errors": list(dict.fromkeys(errors)),
        "runtime_authorized": False,
    }


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _normalize_header(value: str) -> str:
    text = _clean(value).lower()
    for source, target in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}.items():
        text = text.replace(source, target)
    chars = [char if char.isalnum() else "_" for char in text]
    return "_".join(part for part in "".join(chars).split("_") if part)


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen and value not in result:
            result.append(value)
        seen.add(value)
    return result
