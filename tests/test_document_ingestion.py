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


def test_datetime_parsing_does_not_emit_pandas_warnings() -> None:
    import warnings
    from tools.document_ingestion import _to_date
    import pandas as pd
    from tools.bem_schema_builder.excel_profile_builder import ExcelProfileBuilder

    with warnings.catch_warnings():
        warnings.simplefilter("error", category=UserWarning)

        assert _to_date("2026-05-20") == "2026-05-20"
        assert _to_date("2026/05/20") == "2026-05-20"
        assert _to_date("20/05/2026") == "2026-05-20"
        assert _to_date("20-05-2026") == "2026-05-20"
        assert _to_date("remeras") is None
        assert _to_date("123456") is None
        assert _to_date("-") is None

    builder = ExcelProfileBuilder()
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=UserWarning)

        s_text = pd.Series(["remeras", "pantalones", "buzos", "camisas"])
        assert builder._infer_series_type(s_text) == "text"

        s_iso = pd.Series(["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"])
        assert builder._infer_series_type(s_iso) == "date"

        s_local = pd.Series(["01/05/2026", "02/05/2026", "03/05/2026", "04/05/2026"])
        assert builder._infer_series_type(s_local) == "date"

        s_num = pd.Series([100, 200, 300, 450])
        assert builder._infer_series_type(s_num) == "number"
