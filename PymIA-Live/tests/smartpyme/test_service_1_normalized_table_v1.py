from __future__ import annotations

from pymia.smartpyme.service_1_normalized_table_v1 import build_normalized_table_v1


def test_build_ok_from_csv_with_original_headers() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha", "Cliente", "Importe"],
        rows=[
            {"Fecha": "2026-06-01", "Cliente": "Ana", "Importe": "1200"},
            {"Fecha": "2026-06-02", "Cliente": "Beto", "Importe": "900"},
        ],
    )

    assert result["status"] == "OK"
    assert result["source_kind"] == "csv"
    assert result["source_path"] == "ventas.csv"
    assert result["sheet_name"] is None
    assert result["headers"] == ["Fecha", "Cliente", "Importe"]
    assert result["normalized_headers"] == ["fecha", "cliente", "importe"]
    assert result["row_count"] == 2
    assert result["column_count"] == 3
    assert result["rows"][0] == {"fecha": "2026-06-01", "cliente": "Ana", "importe": "1200"}
    assert result["runtime_authorized"] is False
    assert result["blocking_errors"] == []
    assert result["warnings"] == []


def test_build_ok_from_xlsx_with_sheet_name() -> None:
    result = build_normalized_table_v1(
        source_kind="xlsx",
        source_path="inventario.xlsx",
        sheet_name="Sheet1",
        headers=["Producto", "Stock"],
        rows=[
            {"Producto": "Yerba", "Stock": "50"},
        ],
    )

    assert result["status"] == "OK"
    assert result["source_kind"] == "xlsx"
    assert result["sheet_name"] == "Sheet1"
    assert result["headers"] == ["Producto", "Stock"]
    assert result["row_count"] == 1
    assert result["column_count"] == 2
    assert result["runtime_authorized"] is False


def test_accepts_rows_with_normalized_keys() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha", "Cliente"],
        rows=[
            {"fecha": "2026-06-01", "cliente": "Ana"},
        ],
    )

    assert result["status"] == "OK"
    assert result["rows"][0] == {"fecha": "2026-06-01", "cliente": "Ana"}


def test_blocks_empty_headers() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="bad.csv",
        headers=[],
        rows=[],
    )

    assert result["status"] == "BLOCKED"
    assert "headers_required" in result["blocking_errors"]
    assert result["row_count"] == 0
    assert result["rows"] == []
    assert result["runtime_authorized"] is False


def test_blocks_header_with_empty_string() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="bad.csv",
        headers=["Fecha", "", "Importe"],
        rows=[],
    )

    assert result["status"] == "BLOCKED"
    assert "headers_required" in result["blocking_errors"]
    assert result["runtime_authorized"] is False


def test_blocks_duplicate_normalized_headers() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="dup.csv",
        headers=["Cliente", "cliente", "Importe"],
        rows=[],
    )

    assert result["status"] == "BLOCKED"
    assert any("duplicate_headers" in e for e in result["blocking_errors"])
    assert "cliente" in " ".join(result["blocking_errors"])
    assert result["runtime_authorized"] is False


def test_normalizes_accents_and_spaces() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha de emisi\u00f3n", "C\u00f3digo \u00d1", "Importe Total"],
        rows=[
            {"Fecha de emisi\u00f3n": "2026-06-01", "C\u00f3digo \u00d1": "A1", "Importe Total": "100"},
        ],
    )

    assert result["status"] == "OK"
    assert result["normalized_headers"] == ["fecha_de_emision", "codigo_n", "importe_total"]


def test_collapses_multiple_consecutive_non_alnum() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha  doble", "Campo--guion"],
        rows=[
            {"Fecha  doble": "2026-06-01", "Campo--guion": "val"},
        ],
    )

    assert result["status"] == "OK"
    assert result["normalized_headers"] == ["fecha_doble", "campo_guion"]


def test_preserves_warnings_without_duplicates() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha", "Importe"],
        rows=[{"Fecha": "2026-06-01", "Importe": "100"}],
        warnings=["Low confidence on header mapping", "Low confidence on header mapping"],
    )

    assert result["status"] == "OK"
    assert result["warnings"] == ["Low confidence on header mapping"]


def test_respects_blocking_errors_and_skips_rows() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="bad.csv",
        headers=["Fecha", "Importe"],
        rows=[{"Fecha": "2026-06-01", "Importe": "100"}],
        blocking_errors=["Source rejected by intake stage."],
    )

    assert result["status"] == "BLOCKED"
    assert "Source rejected by intake stage." in result["blocking_errors"]
    assert result["row_count"] == 0
    assert result["rows"] == []
    assert result["runtime_authorized"] is False


def test_runtime_authorized_always_false_when_ok() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="ventas.csv",
        headers=["Fecha"],
        rows=[{"Fecha": "2026-06-01"}],
    )

    assert result["status"] == "OK"
    assert result["runtime_authorized"] is False


def test_runtime_authorized_always_false_when_blocked() -> None:
    result = build_normalized_table_v1(
        source_kind="csv",
        source_path="bad.csv",
        headers=[],
        rows=[],
    )

    assert result["status"] == "BLOCKED"
    assert result["runtime_authorized"] is False
