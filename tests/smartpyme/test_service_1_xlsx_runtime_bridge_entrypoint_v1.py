from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook

from pymia.cli import service_1_xlsx_runtime_bridge
from pymia.cli.service_1_xlsx_runtime_bridge import (
    run_service_1_xlsx_runtime_bridge_entrypoint_v1,
)


CASE_REF = "controlled-operational-case-001"
OPERATOR_REF = "operator-001"


def _save_workbook(path: Path, rows_by_sheet: dict[str, list[list[object | None]]]) -> None:
    workbook = Workbook()
    default = workbook.active
    workbook.remove(default)
    for sheet_name, rows in rows_by_sheet.items():
        worksheet = workbook.create_sheet(sheet_name)
        for row in rows:
            worksheet.append(row)
    workbook.save(path)


def test_callable_entrypoint_returns_ready_contract_result(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha", "Importe"], ["2026-06-01", 100]]})

    result = run_service_1_xlsx_runtime_bridge_entrypoint_v1(
        xlsx_path=path,
        case_ref=CASE_REF,
        operator_ref=OPERATOR_REF,
    )

    assert result["contract_kind"] == "SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT"
    assert result["status"] == "XLSX_RUNTIME_BRIDGE_CONTRACT_READY"
    assert result["ready"] is True
    packet = result["bridge_packet"]
    assert packet is not None
    assert packet["source_path_basename"] == "ventas.xlsx"
    assert packet["normalized_headers"] == ["fecha", "importe"]


def test_callable_entrypoint_accepts_sheet_name(tmp_path: Path) -> None:
    path = tmp_path / "multi.xlsx"
    _save_workbook(
        path,
        {
            "Ventas": [["Fecha", "Importe"], ["2026-06-01", 100]],
            "Stock": [["SKU", "Stock"], ["A1", 7]],
        },
    )

    result = run_service_1_xlsx_runtime_bridge_entrypoint_v1(
        xlsx_path=path,
        case_ref=CASE_REF,
        operator_ref=OPERATOR_REF,
        sheet_name="Stock",
    )

    packet = result["bridge_packet"]
    assert packet is not None
    assert packet["sheet_name"] == "Stock"
    assert packet["normalized_headers"] == ["sku", "stock"]


def test_cli_prints_json_and_returns_zero_when_ready(tmp_path: Path, capsys) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha", "Importe"], ["2026-06-01", 100]]})

    rc = service_1_xlsx_runtime_bridge.main([
        "--xlsx",
        str(path),
        "--case-ref",
        CASE_REF,
        "--operator-ref",
        OPERATOR_REF,
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert payload["ready"] is True
    assert payload["bridge_packet"]["source_path_basename"] == "ventas.xlsx"


def test_cli_writes_output_file(tmp_path: Path, capsys) -> None:
    path = tmp_path / "ventas.xlsx"
    output_path = tmp_path / "out" / "bridge.json"
    _save_workbook(path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    rc = service_1_xlsx_runtime_bridge.main([
        "--xlsx",
        str(path),
        "--case-ref",
        CASE_REF,
        "--operator-ref",
        OPERATOR_REF,
        "--output",
        str(output_path),
    ])

    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["ready"] is True
    assert payload["bridge_packet"]["operator_ref"] == OPERATOR_REF


def test_cli_returns_two_for_blocked_result(tmp_path: Path, capsys) -> None:
    rc = service_1_xlsx_runtime_bridge.main([
        "--xlsx",
        str(tmp_path / "missing.xlsx"),
        "--case-ref",
        CASE_REF,
        "--operator-ref",
        OPERATOR_REF,
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 2
    assert payload["ready"] is False
    assert payload["status"] == "BLOCKED_XLSX_NORMALIZATION"


def test_cli_accepts_controlled_operational_case_ref(tmp_path: Path, capsys) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    rc = service_1_xlsx_runtime_bridge.main([
        "--xlsx",
        str(path),
        "--case-ref",
        CASE_REF,
        "--operator-ref",
        OPERATOR_REF,
        "--controlled-operational-case-ref",
        "case-op-ref-001",
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert payload["bridge_packet"]["controlled_operational_case_ref"] == "case-op-ref-001"


def test_cli_required_args_are_enforced() -> None:
    try:
        service_1_xlsx_runtime_bridge.main([])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("argparse should exit for missing required args")
