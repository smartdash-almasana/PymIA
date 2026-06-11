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


def test_vertical_slice_registers_evidence_record_and_reports_evidence_id(tmp_path: Path):
    excel = tmp_path / "ventas.xlsx"
    storage_dir = tmp_path / "storage"
    _make_operational_excel(excel)

    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "vendo mas pero no me queda plata",
        "--tenant-id",
        "tenant_test_001",
        "--intake-id",
        "intake_test_001",
        "--storage-dir",
        str(storage_dir),
    ])

    assert rc == 0
    evidence_log = storage_dir / "tenant_test_001" / "evidences.jsonl"
    records = [json.loads(line) for line in evidence_log.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    record = records[0]
    assert record["tenant_id"] == "tenant_test_001"
    assert record["intake_id"] == "intake_test_001"
    assert record["evidence_type"] == "xlsx_upload"
    assert record["source_kind"] == "uploaded_file"
    assert record["original_filename"] == "ventas.xlsx"
    assert record["status"] == "REGISTERED"
    assert len(record["content_hash"]) == 64


def test_vertical_slice_markdown_includes_persisted_evidence_identity(tmp_path: Path):
    excel = tmp_path / "ventas.xlsx"
    output = tmp_path / "report.md"
    storage_dir = tmp_path / "storage"
    _make_operational_excel(excel)

    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "tengo una pyme y quiero revisar ventas",
        "--tenant-id",
        "tenant_test_002",
        "--intake-id",
        "intake_test_002",
        "--storage-dir",
        str(storage_dir),
        "--output",
        str(output),
    ])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    evidence_log = storage_dir / "tenant_test_002" / "evidences.jsonl"
    record = json.loads(evidence_log.read_text(encoding="utf-8").splitlines()[0])
    assert f"Evidence ID: {record['evidence_id']}" in text
    assert f"Evidence SHA-256: {record['content_hash']}" in text
    assert "Intake: intake_test_002" in text
    assert "## Evidencia estructurada" in text
