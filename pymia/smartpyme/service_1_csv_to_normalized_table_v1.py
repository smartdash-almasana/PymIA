from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_normalized_table_v1 import (
    NormalizedTableV1,
    build_normalized_table_v1,
)


def read_csv_to_normalized_table_v1(
    csv_path: str | Path,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
) -> NormalizedTableV1:
    path = Path(csv_path)
    source_path = str(path)

    if not path.exists() or not path.is_file():
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=["File not found."],
        )
    if path.suffix.lower() != ".csv":
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=["Only .csv files are accepted."],
        )

    try:
        text = path.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=[str(exc)],
        )

    if not text.strip():
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=["CSV file is empty."],
        )

    reader = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if not reader:
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=["CSV file has no rows."],
        )

    headers = [cell.strip() for cell in reader[0]]
    if not headers or any(not h for h in headers):
        return build_normalized_table_v1(
            source_kind="csv",
            source_path=source_path,
            headers=[],
            rows=[],
            blocking_errors=["CSV headers are missing or incomplete."],
        )

    warnings: list[str] = []
    body = [_fit_width(row, len(headers)) for row in reader[1:]]
    for index, row in enumerate(reader[1:], start=2):
        if len(row) < len(headers):
            warnings.append(f"Row {index} has fewer cells than headers.")
        if len(row) > len(headers):
            warnings.append(f"Row {index} has more cells than headers; extra cells ignored.")

    rows: list[dict[str, Any]] = [
        {headers[i]: row[i].strip() for i in range(len(headers))}
        for row in body
    ]

    return build_normalized_table_v1(
        source_kind="csv",
        source_path=source_path,
        headers=headers,
        rows=rows,
        warnings=warnings if warnings else None,
        header_row_number=1,
        source_row_numbers=list(range(2, 2 + len(rows))),
        blocking_errors=None,
    )


def _fit_width(row: list[str], width: int) -> list[str]:
    cleaned = [cell.strip() for cell in row]
    if len(cleaned) < width:
        return cleaned + [""] * (width - len(cleaned))
    return cleaned[:width]
