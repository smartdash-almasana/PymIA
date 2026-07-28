from __future__ import annotations

import json
from pathlib import Path

from tools.excel_evidence import build_excel_structured_evidence


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
    assert evidence.computed_variables == {}
    assert evidence.metadata["calculation_blocked"] is True
    assert evidence.metadata["owner_questions"]


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
    assert loaded["computed_variables"] == {}
    assert loaded["metadata"]["calculation_blocked"] is True
    assert loaded["metadata"]["owner_questions"]


def test_signal_sheet_is_exported_to_metadata_without_blocking_workbook() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=TEXTIL_XLSX,
        tenant_id="tenant-local-excel-signals-test",
    )

    assert evidence.metadata["sheet_reports"]["señales_operativas"] == "OK"
    assert isinstance(evidence.metadata["signals"], list)
    assert evidence.metadata["signals"]


def test_excel_evidence_cli_can_emit_operational_audit_result(tmp_path: Path) -> None:
    from tools.excel_evidence import main
    from pymia.audit_result.models import OperationalAuditResult

    evidence_out = tmp_path / "evidence.json"
    audit_out = tmp_path / "audit.json"

    argv = [
        "--excel", str(TEXTIL_XLSX),
        "--tenant-id", "test_textil_cli",
        "--evidence-output", str(evidence_out),
        "--audit-output", str(audit_out),
    ]

    ret = main(argv)
    assert ret == 0

    assert evidence_out.exists()
    assert audit_out.exists()

    with open(audit_out, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconcile date fields for model validation
    pa = data["business_context"]["period_analyzed"]
    if "from_date" in pa:
        pa["from"] = pa.pop("from_date")
    if "to_date" in pa:
        pa["to"] = pa.pop("to_date")

    audit = OperationalAuditResult.model_validate(data)

    assert audit.audit_id == "audit_test_textil_cli_la_textil_cosida_srl_mar_abr_may_2026"
    assert audit.pathology_routing_summary
    assert audit.open_audit_threads
    assert audit.narrative_payload.allowed_messages
    assert audit.narrative_payload.forbidden_inferences

    # Ensure no raw tables or kernel dump are included at the top-level of the OperationalAuditResult
    payload = audit.model_dump(mode="json")
    assert "tables" not in payload
    assert "raw_tables" not in payload
    assert "normalized_tables" not in payload
    assert "kernel_output" not in payload

