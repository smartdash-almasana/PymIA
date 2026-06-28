from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_common_normalization_router_v1 import (
    route_service_1_common_normalization_v1,
)


def _save_xlsx(path: Path, rows: list[list[object | None]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Datos"
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


def test_csv_routes_to_existing_csv_adapter(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Cliente,Importe\n2026-06-01,Ana,1200\n", encoding="utf-8")

    result = route_service_1_common_normalization_v1(path)

    assert result["status"] == "OK"
    assert result["route_kind"] == "csv"
    assert result["normalized_table"] is not None
    assert result["normalized_table"]["source_kind"] == "csv"
    assert result["normalized_table"]["rows"] == [
        {"fecha": "2026-06-01", "cliente": "Ana", "importe": "1200"}
    ]
    assert result["runtime_authorized"] is False


def test_xlsx_routes_to_existing_xlsx_adapter(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_xlsx(path, [["Fecha", "Cliente", "Importe"], ["2026-06-01", "Ana", 1200]])

    result = route_service_1_common_normalization_v1(path)

    assert result["status"] == "OK"
    assert result["route_kind"] == "xlsx"
    assert result["normalized_table"] is not None
    assert result["normalized_table"]["source_kind"] == "xlsx"
    assert result["normalized_table"]["sheet_name"] == "Datos"
    assert result["normalized_table"]["rows"] == [
        {"fecha": "2026-06-01", "cliente": "Ana", "importe": "1200"}
    ]
    assert result["runtime_authorized"] is False


def test_pdf_returns_explicit_deferred_block(tmp_path: Path) -> None:
    path = tmp_path / "factura.pdf"
    path.write_bytes(b"%PDF-1.4")

    result = route_service_1_common_normalization_v1(path)

    assert result["status"] == "BLOCKED"
    assert result["route_kind"] == "pdf"
    assert result["normalized_table"] is None
    assert result["blocking_errors"] == [
        "PDF_INTAKE_DEFERRED: PDF normalization is explicitly blocked for Stage 5."
    ]
    assert result["runtime_authorized"] is False


def test_unknown_extension_returns_unsupported_block(tmp_path: Path) -> None:
    path = tmp_path / "ventas.txt"
    path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")

    result = route_service_1_common_normalization_v1(path)

    assert result["status"] == "BLOCKED"
    assert result["route_kind"] == "unsupported"
    assert result["normalized_table"] is None
    assert result["blocking_errors"] == [
        "UNSUPPORTED_FILE_TYPE: '.txt' is not supported by Stage 5 normalization."
    ]


def test_router_never_authorizes_runtime_for_supported_and_blocked_paths(tmp_path: Path) -> None:
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")
    pdf_path = tmp_path / "factura.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    assert route_service_1_common_normalization_v1(csv_path)["runtime_authorized"] is False
    assert route_service_1_common_normalization_v1(pdf_path)["runtime_authorized"] is False


def test_preserves_normalized_table_v1_shape(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")

    table = route_service_1_common_normalization_v1(path)["normalized_table"]

    assert table is not None
    assert set(table) == {
        "schema_version",
        "service_name",
        "status",
        "source_kind",
        "source_path",
        "sheet_name",
        "headers",
        "normalized_headers",
        "rows",
        "row_count",
        "column_count",
        "warnings",
        "blocking_errors",
        "runtime_authorized",
    }


def test_preserves_normalized_header_semantics(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_xlsx(path, [["Fecha de emisión", "Código Ñ"], ["2026-06-01", "A1"]])

    result = route_service_1_common_normalization_v1(path)

    assert result["normalized_table"] is not None
    assert result["normalized_table"]["normalized_headers"] == ["fecha_de_emision", "codigo_n"]


def test_router_has_no_cli_or_pipeline_dependency() -> None:
    source = Path("pymia/smartpyme/service_1_common_normalization_router_v1.py").read_text(
        encoding="utf-8"
    )

    assert "pymia.cli" not in source
    assert "service_1_operator" not in source
    assert "service_1_pipeline" not in source
    assert "diagnostic_core" not in source
