from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_csv_to_normalized_table_v1 import (
    read_csv_to_normalized_table_v1,
)


def test_reads_valid_csv_all_rows(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Cliente,Importe\n2026-06-01,Ana,1200\n2026-06-02,Beto,900\n2026-06-03,Carla,800\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert result["source_kind"] == "csv"
    assert result["row_count"] == 3
    assert result["column_count"] == 3
    assert result["headers"] == ["Fecha", "Cliente", "Importe"]
    assert result["normalized_headers"] == ["fecha", "cliente", "importe"]
    assert len(result["rows"]) == 3
    assert result["rows"][2] == {"fecha": "2026-06-03", "cliente": "Carla", "importe": "800"}
    assert result["runtime_authorized"] is False
    assert result["blocking_errors"] == []


def test_all_rows_not_just_preview(tmp_path: Path) -> None:
    path = tmp_path / "muchas.csv"
    lines = "Col\n" + "\n".join(f"row_{i}" for i in range(100))
    path.write_text(lines, encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert result["row_count"] == 100
    assert len(result["rows"]) == 100


def test_fail_on_missing_file(tmp_path: Path) -> None:
    result = read_csv_to_normalized_table_v1(tmp_path / "no_existe.csv")

    assert result["status"] == "BLOCKED"
    assert "File not found" in " ".join(result["blocking_errors"])
    assert result["row_count"] == 0
    assert result["rows"] == []
    assert result["runtime_authorized"] is False


def test_fail_on_non_csv_extension(tmp_path: Path) -> None:
    path = tmp_path / "data.xlsx"
    path.write_text("a,b\n1,2\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "BLOCKED"
    assert "Only .csv" in " ".join(result["blocking_errors"])


def test_fail_on_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "vacio.csv"
    path.write_text("   \n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "BLOCKED"
    assert any("empty" in e.lower() for e in result["blocking_errors"])


def test_fail_on_missing_headers(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("Fecha,,Importe\n2026-06-01,Ana,100\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "BLOCKED"
    assert any("headers" in e.lower() for e in result["blocking_errors"])


def test_supports_custom_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha;Importe\n2026-06-01;100\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path, delimiter=";")

    assert result["status"] == "OK"
    assert result["row_count"] == 1
    assert result["rows"][0] == {"fecha": "2026-06-01", "importe": "100"}


def test_warns_on_short_rows(tmp_path: Path) -> None:
    path = tmp_path / "ragged.csv"
    path.write_text("A,B,C\n1,2\n3,4,5\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert result["row_count"] == 2
    assert any("fewer" in w for w in result["warnings"])


def test_warns_on_extra_cells(tmp_path: Path) -> None:
    path = tmp_path / "extra.csv"
    path.write_text("A,B\n1,2,3\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert any("extra" in w for w in result["warnings"])


def test_normalizes_accents_and_spaces(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha de emisi\u00f3n,C\u00f3digo \u00d1,Importe Total\n2026-06-01,A1,100\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert result["normalized_headers"] == ["fecha_de_emision", "codigo_n", "importe_total"]


def test_runtime_authorized_always_false(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("A,B\n1,2\n", encoding="utf-8")

    result = read_csv_to_normalized_table_v1(path)

    assert result["status"] == "OK"
    assert result["runtime_authorized"] is False
