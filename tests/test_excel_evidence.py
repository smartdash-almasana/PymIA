from __future__ import annotations

import json
from pathlib import Path

from tools.excel_evidence import build_excel_structured_evidence, evidence_to_kernel_artifact


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_XLSX = REPO_ROOT / "prueba_excels" / "pyme_textil_compleja.xlsx"
TEXTIL_XLSX = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def test_local_excel_evidence_builds_structured_evidence_from_real_xlsx() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=REAL_XLSX,
        tenant_id="tenant-local-excel-test",
    )

    assert evidence.tenant_id == "tenant-local-excel-test"
    assert evidence.document_type == "xlsx_operational_evidence"
    assert evidence.source == "xlsx_upload"
    assert evidence.file_name == "pyme_textil_compleja.xlsx"
    assert evidence.tables
    assert evidence.metadata["extraction_engine"] == "local_excel_evidence_v1"
    assert evidence.metadata["rows_count"] > 0
    assert evidence.computed_variables


def test_local_excel_evidence_reaches_kernel() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=REAL_XLSX,
        tenant_id="tenant-local-excel-kernel-test",
    )

    artifact = evidence_to_kernel_artifact(evidence)

    assert artifact["ok"] is True
    assert artifact["kernel"]["status"] in {"ok", "no_signal"}
    assert artifact["evidence"]["source"] == "xlsx_upload"
    assert artifact["evidence"]["computed_variables"]


def test_local_excel_evidence_artifact_is_json_serializable(tmp_path: Path) -> None:
    evidence = build_excel_structured_evidence(
        excel_path=REAL_XLSX,
        tenant_id="tenant-local-excel-json-test",
    )
    out = tmp_path / "evidence.json"
    out.write_text(json.dumps(evidence.model_dump(mode="json"), ensure_ascii=False), encoding="utf-8")

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["tenant_id"] == "tenant-local-excel-json-test"
    assert loaded["tables"]
    assert loaded["computed_variables"]


def test_signal_sheet_is_exported_to_metadata_without_blocking_workbook() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=TEXTIL_XLSX,
        tenant_id="tenant-local-excel-signals-test",
    )

    assert evidence.metadata["sheet_reports"]["señales_operativas"] == "OK"
    assert isinstance(evidence.metadata["signals"], list)
    assert evidence.metadata["signals"]
