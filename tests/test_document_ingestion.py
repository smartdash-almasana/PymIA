from __future__ import annotations

import json
from pathlib import Path

from tools.document_ingestion import (
    build_structured_evidence_from_xlsx,
    curate_xlsx_document,
    persist_curation_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "prueba_excels" / "pyme_textil_compleja.xlsx"


def test_curate_xlsx_document_builds_artifact() -> None:
    curated = curate_xlsx_document(XLSX)
    payload = curated.to_dict()

    assert payload["file_name"] == "pyme_textil_compleja.xlsx"
    assert payload["raw_tables"]
    assert payload["normalized_tables"]
    assert payload["report"]["tables_count"] > 0
    assert payload["report"]["rows_count"] > 0
    assert payload["report"]["sheet_reports"]
    assert payload["report"]["status"] in {"CURATED", "PARTIAL", "BLOCKED"}


def test_curated_document_is_json_serializable() -> None:
    curated = curate_xlsx_document(XLSX)
    decoded = json.loads(json.dumps(curated.to_dict(), ensure_ascii=False))

    assert decoded["file_name"] == "pyme_textil_compleja.xlsx"
    assert isinstance(decoded["raw_tables"], list)
    assert isinstance(decoded["report"], dict)


def test_document_ingestion_exports_structured_evidence() -> None:
    evidence = build_structured_evidence_from_xlsx(
        excel_path=XLSX,
        tenant_id="tenant-document-ingestion-test",
    )

    assert evidence.tenant_id == "tenant-document-ingestion-test"
    assert evidence.document_type == "xlsx_operational_evidence"
    assert evidence.source == "xlsx_upload"
    assert evidence.file_name == "pyme_textil_compleja.xlsx"
    assert evidence.tables
    assert evidence.computed_variables == {}
    assert evidence.metadata["calculation_blocked"] is True
    assert evidence.metadata["owner_questions"]
    assert evidence.metadata["extraction_engine"] == "local_excel_evidence_v1"
    assert evidence.metadata["sheet_reports"]


def test_document_ingestion_persists_expected_artifacts(tmp_path: Path) -> None:
    curated = curate_xlsx_document(XLSX)
    evidence = build_structured_evidence_from_xlsx(
        excel_path=XLSX,
        tenant_id="tenant-document-ingestion-artifacts",
    )
    paths = persist_curation_artifacts(
        curated=curated,
        evidence=evidence,
        output_dir=tmp_path,
        stem="pyme_textil_compleja",
    )

    assert Path(paths["raw_tables"]).exists()
    assert Path(paths["normalized_tables"]).exists()
    assert Path(paths["sheet_reports"]).exists()
    assert Path(paths["structured_evidence"]).exists()


def test_document_ingestion_of_internal_fact_runs_operational_audit(tmp_path: Path) -> None:
    import base64
    import importlib.util
    import sys

    # Add conversa-engine to sys.path for importing router
    conversa_dir = Path(__file__).resolve().parents[1] / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))

    module_path = conversa_dir / "document_intake.py"
    spec = importlib.util.spec_from_file_location("document_intake", module_path)
    assert spec is not None
    assert spec.loader is not None
    document_intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_intake)

    from pymia.audit_result.models import OperationalAuditResult
    from operational_audit_router import route_operational_audit_message

    TEXTIL_XLSX = Path(__file__).resolve().parents[1] / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"

    tenant_id = "tenant-intake-test"
    user_id = "user-123"
    session_id = f"{tenant_id}/{user_id}"

    # Use tmp_path for base_path and fallback_path for test isolation
    msg = document_intake.intake_document(
        tenant_id=tenant_id,
        user_id=user_id,
        file_path=str(TEXTIL_XLSX),
        file_name="la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        mime_type=None,
        expected_schema="unknown",
        entropy_level=0.1,  # Under 0.3 for INTERNAL_FACT
        base_path=tmp_path,
        fallback_path=tmp_path,
    )

    assert "[Auditoría Operacional Activa]" in msg
    assert "Concentración de SKU (PYME_033)" in msg

    session_bytes = session_id.encode("utf-8")
    encoded_id = base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")
    audit_file = tmp_path / "audits" / encoded_id / "operational_audit_result.json"

    assert audit_file.exists()

    with open(audit_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconcile date fields for model validation
    pa = data["business_context"]["period_analyzed"]
    if "from_date" in pa:
        pa["from"] = pa.pop("from_date")
    if "to_date" in pa:
        pa["to"] = pa.pop("to_date")

    audit = OperationalAuditResult.model_validate(data)

    assert audit.audit_id == "audit_tenant-intake-test_la_textil_cosida_srl_mar_abr_may_2026"
    assert audit.pathology_routing_summary

    decision = route_operational_audit_message("quiero ver PYME_033", audit)
    assert decision.pathology_code == "PYME_033"
    assert "ventas_por_sku" in decision.missing_evidence


def test_datetime_parsing_does_not_emit_pandas_warnings() -> None:
    import warnings
    from tools.document_ingestion import _to_date
    import pandas as pd
    from tools.bem_schema_builder.excel_profile_builder import ExcelProfileBuilder

    # Verify _to_date cases
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=UserWarning)
        
        # ISO formats
        assert _to_date("2026-05-20") == "2026-05-20"
        assert _to_date("2026/05/20") == "2026-05-20"
        
        # Local localized format
        assert _to_date("20/05/2026") == "2026-05-20"
        assert _to_date("20-05-2026") == "2026-05-20"
        
        # Non-date strings
        assert _to_date("remeras") is None
        assert _to_date("123456") is None
        assert _to_date("-") is None

    # Verify _infer_series_type cases
    builder = ExcelProfileBuilder()
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=UserWarning)
        
        # Text columns
        s_text = pd.Series(["remeras", "pantalones", "buzos", "camisas"])
        assert builder._infer_series_type(s_text) == "text"
        
        # Date columns ISO
        s_iso = pd.Series(["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"])
        assert builder._infer_series_type(s_iso) == "date"
        
        # Date columns Localized
        s_local = pd.Series(["01/05/2026", "02/05/2026", "03/05/2026", "04/05/2026"])
        assert builder._infer_series_type(s_local) == "date"
        
        # Number columns
        s_num = pd.Series([100, 200, 300, 450])
        assert builder._infer_series_type(s_num) == "number"


def test_intake_forces_bem_ai_on_administrative_contexts(tmp_path: Path) -> None:
    import importlib.util
    import sys
    import base64

    conversa_dir = Path(__file__).resolve().parents[1] / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))

    module_path = conversa_dir / "document_intake.py"
    spec = importlib.util.spec_from_file_location("document_intake_admin", module_path)
    document_intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_intake)

    dummy_xlsx = tmp_path / "declaracion_iva_afip.xlsx"
    dummy_xlsx.write_text("dummy content")

    tenant_id = "tenant-intake-admin-test"
    user_id = "user-456"

    # Since it is a fiscal/impositivo context, it should degrade to BEM_AI and NOT run audit
    msg = document_intake.intake_document(
        tenant_id=tenant_id,
        user_id=user_id,
        file_path=str(dummy_xlsx),
        file_name="declaracion_iva_afip.xlsx",
        mime_type=None,
        expected_schema="unknown",
        entropy_level=0.1,  # Normally qualifies for INTERNAL_FACT
        base_path=tmp_path,
        fallback_path=tmp_path,
    )

    assert "Recibí el archivo, pero todavía no fue procesado." in msg
    
    # Assert that no audits folder is created since it did not execute the socratic audit runner
    session_id = f"{tenant_id}/{user_id}"
    session_bytes = session_id.encode("utf-8")
    encoded_id = base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")
    audit_file = tmp_path / "audits" / encoded_id / "operational_audit_result.json"
    assert not audit_file.exists()



