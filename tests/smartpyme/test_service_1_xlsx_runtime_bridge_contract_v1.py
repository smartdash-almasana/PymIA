from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_xlsx_runtime_bridge_contract_v1 import (
    build_service_1_xlsx_runtime_bridge_contract_v1,
)


CASE_REF = "controlled-operational-case-001"
OPERATOR_REF = "operator-001"

CLOSED_FLAGS = (
    "delivery_done",
    "publish_done",
    "notification_done",
    "service_2_opened",
    "phase_j_opened",
    "saas_api_ui_opened",
)


def _save_workbook(path: Path, rows_by_sheet: dict[str, list[list[object | None]]]) -> None:
    workbook = Workbook()
    default = workbook.active
    workbook.remove(default)
    for sheet_name, rows in rows_by_sheet.items():
        worksheet = workbook.create_sheet(sheet_name)
        for row in rows:
            worksheet.append(row)
    workbook.save(path)


def _build(
    path: Path,
    *,
    case_ref: str | None = CASE_REF,
    operator_ref: str | None = OPERATOR_REF,
    controlled_operational_case_ref: str | None = None,
    sheet_name: str | None = None,
) -> dict[str, object]:
    return build_service_1_xlsx_runtime_bridge_contract_v1(
        xlsx_path=path,
        case_ref=case_ref,
        operator_ref=operator_ref,
        controlled_operational_case_ref=controlled_operational_case_ref,
        sheet_name=sheet_name,
    )


def test_valid_xlsx_builds_operator_reviewable_bridge_packet(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha", "Cliente", "Importe"], ["2026-06-01", "Ana", 1200]]})

    result = _build(path)

    assert result["contract_kind"] == "SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT"
    assert result["status"] == "XLSX_RUNTIME_BRIDGE_CONTRACT_READY"
    assert result["ready"] is True
    assert result["controlled_xlsx_read_done"] is True
    assert result["operator_review_required"] is True

    packet = result["bridge_packet"]
    assert packet is not None
    assert packet["packet_kind"] == "SERVICE_1_XLSX_RUNTIME_BRIDGE_PACKET"
    assert packet["case_ref"] == CASE_REF
    assert packet["operator_ref"] == OPERATOR_REF
    assert packet["controlled_operational_case_ref"] == CASE_REF
    assert packet["source_path_basename"] == "ventas.xlsx"
    assert packet["sheet_name"] == "Ventas"
    assert packet["normalized_headers"] == ["fecha", "cliente", "importe"]
    assert packet["row_count"] == 1
    assert packet["column_count"] == 3
    assert packet["structure"]["service_name"] == "SERVICE_1"
    assert packet["structure"]["runtime_authorized"] is False


def test_valid_xlsx_with_explicit_controlled_operational_case_ref(tmp_path: Path) -> None:
    path = tmp_path / "stock.xlsx"
    _save_workbook(path, {"Stock": [["SKU", "Stock"], ["A1", 5]]})

    result = _build(path, controlled_operational_case_ref="case-op-abc")

    packet = result["bridge_packet"]
    assert packet is not None
    assert packet["controlled_operational_case_ref"] == "case-op-abc"


def test_valid_xlsx_with_sheet_name(tmp_path: Path) -> None:
    path = tmp_path / "multi.xlsx"
    _save_workbook(
        path,
        {
            "Ventas": [["Fecha", "Importe"], ["2026-06-01", 100]],
            "Inventario": [["SKU", "Stock"], ["A1", 5]],
        },
    )

    result = _build(path, sheet_name="Inventario")

    assert result["status"] == "XLSX_RUNTIME_BRIDGE_CONTRACT_READY"
    packet = result["bridge_packet"]
    assert packet is not None
    assert packet["sheet_name"] == "Inventario"
    assert packet["normalized_headers"] == ["sku", "stock"]


def test_missing_case_ref_blocks_before_xlsx_read(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    result = _build(path, case_ref="")

    assert result["status"] == "BLOCKED_MISSING_CASE_REF"
    assert result["ready"] is False
    assert result["bridge_packet"] is None
    assert result["controlled_xlsx_read_done"] is False


def test_missing_operator_ref_blocks_before_xlsx_read(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    result = _build(path, operator_ref="")

    assert result["status"] == "BLOCKED_MISSING_OPERATOR_REF"
    assert result["ready"] is False
    assert result["bridge_packet"] is None
    assert result["controlled_xlsx_read_done"] is False


def test_missing_xlsx_file_blocks_safely(tmp_path: Path) -> None:
    result = _build(tmp_path / "missing.xlsx")

    assert result["status"] == "BLOCKED_XLSX_NORMALIZATION"
    assert result["ready"] is False
    assert result["bridge_packet"] is None
    assert result["controlled_xlsx_read_done"] is True
    assert "File not found." in result["blocked_reasons"]


def test_non_xlsx_input_blocks_safely(tmp_path: Path) -> None:
    path = tmp_path / "ventas.csv"
    path.write_text("Fecha,Importe\n2026-06-01,100\n", encoding="utf-8")

    result = _build(path)

    assert result["status"] == "BLOCKED_XLSX_NORMALIZATION"
    assert result["ready"] is False
    assert "Only .xlsx files are accepted." in result["blocked_reasons"]


def test_missing_sheet_blocks_safely(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    result = _build(path, sheet_name="NoExiste")

    assert result["status"] == "BLOCKED_XLSX_NORMALIZATION"
    assert result["ready"] is False
    assert "Sheet not found: NoExiste" in result["blocked_reasons"]


def test_duplicate_headers_block_safely(tmp_path: Path) -> None:
    path = tmp_path / "dup.xlsx"
    _save_workbook(path, {"Datos": [["Cliente", "cliente"], ["Ana", "Ana SA"]]})

    result = _build(path)

    assert result["status"] == "BLOCKED_XLSX_NORMALIZATION"
    assert result["ready"] is False
    assert any(reason.startswith("duplicate_headers") for reason in result["blocked_reasons"])


def test_warnings_are_preserved(tmp_path: Path) -> None:
    path = tmp_path / "short.xlsx"
    _save_workbook(path, {"Datos": [["Fecha", "Cliente", "Importe"], ["2026-06-01", "Ana"]]})

    result = _build(path)

    packet = result["bridge_packet"]
    assert packet is not None
    assert "Row 2 has fewer cells than headers." in packet["warnings"]


def test_closed_flags_are_false_for_ready_and_blocked(tmp_path: Path) -> None:
    ready_path = tmp_path / "ventas.xlsx"
    _save_workbook(ready_path, {"Ventas": [["Fecha"], ["2026-06-01"]]})

    ready = _build(ready_path)
    blocked = _build(tmp_path / "missing.xlsx")

    for result in (ready, blocked):
        for flag in CLOSED_FLAGS:
            assert result[flag] is False
        packet = result["bridge_packet"]
        if packet is not None:
            for flag in CLOSED_FLAGS:
                assert packet[flag] is False


def test_bridge_is_deterministic_for_same_input(tmp_path: Path) -> None:
    path = tmp_path / "ventas.xlsx"
    _save_workbook(path, {"Ventas": [["Fecha", "Importe"], ["2026-06-01", 100]]})

    first = _build(path)
    second = _build(path)

    assert first == second
