from __future__ import annotations

from pathlib import Path
from typing import Literal, TypedDict

from pymia.smartpyme.service_1_csv_to_normalized_table_v1 import read_csv_to_normalized_table_v1
from pymia.smartpyme.service_1_normalized_table_v1 import NormalizedTableV1
from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import read_xlsx_to_normalized_table_v1

RouterStatus = Literal["OK", "BLOCKED"]
RouteKind = Literal["csv", "xlsx", "pdf", "unsupported"]


class Service1CommonNormalizationRouterV1(TypedDict):
    schema_version: str
    service_name: str
    status: RouterStatus
    source_path: str
    source_extension: str
    route_kind: RouteKind
    normalized_table: NormalizedTableV1 | None
    warnings: list[str]
    blocking_errors: list[str]
    runtime_authorized: Literal[False]


def route_service_1_common_normalization_v1(
    source_path: str | Path,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    sheet_name: str | None = None,
) -> Service1CommonNormalizationRouterV1:
    """Route supported Stage 5 sources into the common NormalizedTableV1 contract.

    CSV and XLSX are routed to their existing adapters. PDF and unknown file types
    are explicitly blocked; this module does not implement OCR or PDF parsing.
    """
    path = Path(source_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        table = read_csv_to_normalized_table_v1(path, delimiter=delimiter, encoding=encoding)
        return _from_table(path, "csv", table)

    if extension == ".xlsx":
        table = read_xlsx_to_normalized_table_v1(path, sheet_name=sheet_name)
        return _from_table(path, "xlsx", table)

    if extension == ".pdf":
        return _blocked(
            path,
            "pdf",
            "PDF_INTAKE_DEFERRED: PDF normalization is explicitly blocked for Stage 5.",
        )

    return _blocked(
        path,
        "unsupported",
        f"UNSUPPORTED_FILE_TYPE: '{extension or '<none>'}' is not supported by Stage 5 normalization.",
    )


def _from_table(
    path: Path,
    route_kind: Literal["csv", "xlsx"],
    table: NormalizedTableV1,
) -> Service1CommonNormalizationRouterV1:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": table["status"],
        "source_path": str(path),
        "source_extension": path.suffix.lower(),
        "route_kind": route_kind,
        "normalized_table": table,
        "warnings": table["warnings"],
        "blocking_errors": table["blocking_errors"],
        "runtime_authorized": False,
    }


def _blocked(
    path: Path,
    route_kind: Literal["pdf", "unsupported"],
    message: str,
) -> Service1CommonNormalizationRouterV1:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": "BLOCKED",
        "source_path": str(path),
        "source_extension": path.suffix.lower(),
        "route_kind": route_kind,
        "normalized_table": None,
        "warnings": [],
        "blocking_errors": [message],
        "runtime_authorized": False,
    }
