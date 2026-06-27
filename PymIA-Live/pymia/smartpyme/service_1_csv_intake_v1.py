from __future__ import annotations

import csv
from pathlib import Path
from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"

CsvStatus = Literal[
    "OK",
    "FILE_NOT_FOUND",
    "NOT_A_CSV_FILE",
    "EMPTY_FILE",
    "MISSING_HEADERS",
    "DUPLICATE_HEADERS",
    "DECODE_ERROR",
]


class Service1CsvIntakeV1(TypedDict):
    schema_version: str
    service_name: str
    status: CsvStatus
    source_path: str
    filename: str | None
    delimiter: str
    encoding: str
    headers: list[str]
    normalized_headers: list[str]
    row_count: int
    column_count: int
    preview_rows: list[dict[str, str]]
    warnings: list[str]
    blocking_errors: list[str]
    runtime_authorized: Literal[False]


def read_service_1_csv_intake_v1(
    csv_path: str | Path,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    preview_limit: int = 5,
) -> Service1CsvIntakeV1:
    path = Path(csv_path)
    source_path = str(path)
    filename = path.name if path.name else None

    if not path.exists() or not path.is_file():
        return _blocked("FILE_NOT_FOUND", source_path, filename, delimiter, encoding, "CSV file not found.")
    if path.suffix.lower() != ".csv":
        return _blocked("NOT_A_CSV_FILE", source_path, filename, delimiter, encoding, "Only .csv files are accepted.")

    try:
        text = path.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        return _blocked("DECODE_ERROR", source_path, filename, delimiter, encoding, str(exc))

    if not text.strip():
        return _blocked("EMPTY_FILE", source_path, filename, delimiter, encoding, "CSV file is empty.")

    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if not rows:
        return _blocked("EMPTY_FILE", source_path, filename, delimiter, encoding, "CSV file has no rows.")

    headers = [cell.strip() for cell in rows[0]]
    if not headers or any(not header for header in headers):
        return _blocked("MISSING_HEADERS", source_path, filename, delimiter, encoding, "CSV headers are missing or incomplete.")

    normalized_headers = [_normalize_header(header) for header in headers]
    duplicates = _duplicates(normalized_headers)
    if duplicates:
        result = _blocked(
            "DUPLICATE_HEADERS",
            source_path,
            filename,
            delimiter,
            encoding,
            "Duplicate normalized headers: " + ", ".join(duplicates),
        )
        result["headers"] = headers
        result["normalized_headers"] = normalized_headers
        result["column_count"] = len(headers)
        return result

    body = [_fit_width(row, len(headers)) for row in rows[1:]]
    warnings: list[str] = []
    for index, row in enumerate(rows[1:], start=2):
        if len(row) < len(headers):
            warnings.append(f"Row {index} has fewer cells than headers.")
        if len(row) > len(headers):
            warnings.append(f"Row {index} has more cells than headers; extra cells ignored.")

    preview_rows = [
        {normalized_headers[i]: row[i].strip() for i in range(len(headers))}
        for row in body[: max(preview_limit, 0)]
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": "OK",
        "source_path": source_path,
        "filename": filename,
        "delimiter": delimiter,
        "encoding": encoding,
        "headers": headers,
        "normalized_headers": normalized_headers,
        "row_count": len(body),
        "column_count": len(headers),
        "preview_rows": preview_rows,
        "warnings": list(dict.fromkeys(warnings)),
        "blocking_errors": [],
        "runtime_authorized": False,
    }


def _blocked(
    status: CsvStatus,
    source_path: str,
    filename: str | None,
    delimiter: str,
    encoding: str,
    message: str,
) -> Service1CsvIntakeV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "source_path": source_path,
        "filename": filename,
        "delimiter": delimiter,
        "encoding": encoding,
        "headers": [],
        "normalized_headers": [],
        "row_count": 0,
        "column_count": 0,
        "preview_rows": [],
        "warnings": [],
        "blocking_errors": [message],
        "runtime_authorized": False,
    }


def _normalize_header(header: str) -> str:
    text = header.strip().lower()
    for source, target in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}.items():
        text = text.replace(source, target)
    chars = [char if char.isalnum() else "_" for char in text]
    return "_".join(part for part in "".join(chars).split("_") if part)


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _fit_width(row: list[str], width: int) -> list[str]:
    cleaned = [cell.strip() for cell in row]
    if len(cleaned) < width:
        return cleaned + [""] * (width - len(cleaned))
    return cleaned[:width]
