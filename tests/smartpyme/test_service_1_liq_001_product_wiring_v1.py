from __future__ import annotations

from pathlib import Path

import openpyxl

from pymia.cli import service_1_product as cli


def _semantic_answers(first: dict) -> dict[str, str]:
    answers: dict[str, str] = {}
    for question in first["product_pipeline"]["owner_questions"]:
        if question["column_name"] == "cobrado":
            answers[question["column_name"]] = next(
                option["option_id"]
                for option in question["options"]
                if option["label"] == "Importe cobrado"
            )
        else:
            answers[question["column_name"]] = next(
                option_id
                for option_id in question["allowed_option_ids"]
                if option_id not in {"OTHER", "IGNORE"}
            )
    return answers


def test_official_entrypoint_executes_liq_001_from_all_normalized_rows(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "ventas_cobros.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["fecha", "venta_total", "cobrado"])
    sheet.append(["2026-06-01", 1000, 800])
    sheet.append(["2026-06-02", 2000, 1500])
    workbook.save(xlsx)

    owner_answers = {
        "fecha": "fecha de la operación",
        "venta_total": "importe total vendido",
        "cobrado": "importe efectivamente cobrado",
    }
    output_dir = tmp_path / "out"

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=None,
        tool_requests=[],
        output_dir=output_dir,
        sheet_name="Ventas",
        requested_capability="sold_vs_collected_gap",
    )
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=_semantic_answers(first),
        tool_requests=[],
        output_dir=output_dir,
        sheet_name="Ventas",
        requested_capability="sold_vs_collected_gap",
    )
    product = final["product_pipeline"]
    result = product["computation_result"]

    assert final["status"] == "COMPUTATION_PLAN_READY"
    assert product["computation_executed"] is True
    assert product["tools_executed"] is False
    assert product["physical_run"] is None
    assert result["status"] == "EVALUATED"
    assert result["inputs"] == {
        "sold_amount": 3000.0,
        "collected_amount": 2300.0,
    }
    assert result["computed"] == {
        "gap_amount": 700.0,
        "collection_ratio": 2300.0 / 3000.0,
        "gap_ratio": 700.0 / 3000.0,
    }
    assert result["aggregation"]["row_count"] == 2
    assert result["aggregation"]["sample_based"] is False
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False
    assert product["runtime_authorized"] is False
    assert product["delivery_authorized"] is False
    assert product["diagnosis_generated"] is False
    assert not list(output_dir.glob("*.xlsx"))
