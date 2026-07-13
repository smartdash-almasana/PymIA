from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_csv_intake_v1 import read_service_1_csv_intake_v1


def test_reads_valid_csv(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Cliente,Importe\n2026-06-01,Ana,1200\n2026-06-02,Beto,900\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "OK"
    assert result["headers"] == ["Fecha", "Cliente", "Importe"]
    assert result["normalized_headers"] == ["fecha", "cliente", "importe"]
    assert result["row_count"] == 2
    assert result["column_count"] == 3
    assert result["preview_rows"][0] == {"fecha": "2026-06-01", "cliente": "Ana", "importe": "1200"}
    assert result["runtime_authorized"] is False
    assert result["blocking_errors"] == []


def test_blocks_missing_file(tmp_path: Path) -> None:
    result = read_service_1_csv_intake_v1(tmp_path / "missing.csv")

    assert result["status"] == "FILE_NOT_FOUND"
    assert result["runtime_authorized"] is False
    assert result["blocking_errors"]


def test_blocks_non_csv_extension(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "NOT_A_CSV_FILE"
    assert result["runtime_authorized"] is False


def test_blocks_empty_csv(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("   \n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "EMPTY_FILE"
    assert result["runtime_authorized"] is False


def test_blocks_missing_headers(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("Fecha,,Importe\n2026-06-01,Ana,100\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "MISSING_HEADERS"
    assert result["runtime_authorized"] is False


def test_blocks_duplicate_normalized_headers(tmp_path: Path) -> None:
    path = tmp_path / "dup.csv"
    path.write_text("Cliente,cliente,Importe\nAna,Ana SA,100\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "DUPLICATE_HEADERS"
    assert result["normalized_headers"] == ["cliente", "cliente", "importe"]
    assert result["runtime_authorized"] is False


def test_supports_custom_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha;Cliente;Importe\n2026-06-01;Ana;1200\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path, delimiter=";")

    assert result["status"] == "OK"
    assert result["delimiter"] == ";"
    assert result["row_count"] == 1
    assert result["preview_rows"][0]["cliente"] == "Ana"


def test_warns_and_normalizes_short_and_long_rows(tmp_path: Path) -> None:
    path = tmp_path / "ragged.csv"
    path.write_text("Fecha,Cliente,Importe\n2026-06-01,Ana\n2026-06-02,Beto,900,extra\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "OK"
    assert result["row_count"] == 2
    assert result["preview_rows"][0]["importe"] == ""
    assert result["preview_rows"][1]["importe"] == "900"
    assert len(result["warnings"]) == 2
    assert result["runtime_authorized"] is False


def test_preview_limit_can_be_zero(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path, preview_limit=0)

    assert result["status"] == "OK"
    assert result["preview_rows"] == []
    assert result["row_count"] == 1


def test_header_normalization_handles_accents_and_spaces(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha de emisión,Código Ñ,Importe Total\n2026-06-01,A1,100\n", encoding="utf-8")

    result = read_service_1_csv_intake_v1(path)

    assert result["status"] == "OK"
    assert result["normalized_headers"] == ["fecha_de_emision", "codigo_n", "importe_total"]
