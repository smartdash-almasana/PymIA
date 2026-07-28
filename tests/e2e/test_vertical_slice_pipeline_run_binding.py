from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook

from pymia.cli import vertical_slice


def _make_operational_excel(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "ventas"
    sheet.append(["fecha", "producto", "cantidad", "precio", "costo"])
    sheet.append(["2026-06-01", "sku-1", 2, 100, 60])
    workbook.save(path)


def test_vertical_slice_persists_pipeline_run_linked_to_evidence(tmp_path: Path):
    excel = tmp_path / "ventas.xlsx"
    output = tmp_path / "report.md"
    storage_dir = tmp_path / "storage"
    _make_operational_excel(excel)

    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "vendo mas pero no me queda plata",
        "--tenant-id",
        "tenant_test_003",
        "--intake-id",
        "intake_test_003",
        "--storage-dir",
        str(storage_dir),
        "--output",
        str(output),
    ])

    assert rc == 0
    tenant_dir = storage_dir / "tenant_test_003"
    evidence_record = json.loads((tenant_dir / "evidences.jsonl").read_text(encoding="utf-8").splitlines()[0])
    pipeline_run = json.loads((tenant_dir / "pipeline_runs.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert pipeline_run["tenant_id"] == "tenant_test_003"
    assert pipeline_run["intake_id"] == "intake_test_003"
    assert pipeline_run["pipeline_name"] == "vertical_cli_evidence_spine"
    assert pipeline_run["pipeline_module"] == "pymia.cli.vertical_slice"
    assert pipeline_run["status"] == "COMPLETED"
    assert pipeline_run["evidence_ids"] == [evidence_record["evidence_id"]]
    assert len(pipeline_run["input_hash"]) == 64
    assert len(pipeline_run["output_hash"]) == 64
    assert "evidence_sufficiency_checked" in pipeline_run["steps_executed"]
    _ = output.read_text(encoding="utf-8")


def test_vertical_slice_pipeline_run_blocks_when_minimal_evidence_is_missing(tmp_path: Path):
    excel = tmp_path / "no_operacional.xlsx"
    storage_dir = tmp_path / "storage"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["nombre", "comentario"])
    sheet.append(["abc", "sin columnas operativas"])
    workbook.save(excel)

    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "hola",
        "--tenant-id",
        "tenant_test_004",
        "--intake-id",
        "intake_test_004",
        "--storage-dir",
        str(storage_dir),
    ])

    assert rc == 0
    pipeline_run = json.loads(
        (storage_dir / "tenant_test_004" / "pipeline_runs.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert pipeline_run["status"] == "BLOCKED"
    assert pipeline_run["intake_id"] == "intake_test_004"
    assert pipeline_run["metadata"]["case_id_alias"] == "intake_test_004"
