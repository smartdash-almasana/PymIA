from pathlib import Path

import pytest
from openpyxl import Workbook

from pymia.cli import vertical_slice


def _write_excel(path: Path, rows: list[list[object]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


def test_vertical_slice_cli_outputs_delivered_candidate_for_operational_excel(tmp_path: Path, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "vendo mas pero no me queda plata",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Reporte owner-facing local" in out
    assert "DELIVERED_CANDIDATE" in out
    assert "caso.xlsx" in out
    assert "Filas: 2" in out
    assert "resultado candidato" in out.lower()
    assert "no diagnostica" in out.lower()


def test_vertical_slice_build_report_returns_owner_facing_contract_dict(tmp_path: Path):
    excel = tmp_path / "caso.xlsx"
    storage_dir = tmp_path / "storage"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(
        excel,
        "vendo mas pero no me queda plata",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
        storage_dir=storage_dir,
    )
    assert report["status"] == "DELIVERED_CANDIDATE"
    assert report["tenant_id"] == "tenant_textil_001"
    assert report["intake_id"] == "intake_textil_001"
    assert report["anamnesis_record"]["tenant_id"] == "tenant_textil_001"
    assert report["anamnesis_record"]["raw_owner_message"] == "vendo mas pero no me queda plata"
    assert report["pipeline_run_record"]["metadata"]["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert report["investigation_record"]["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert report["pipeline_run_record"]["metadata"]["investigation_id"] == report["investigation_record"]["investigation_id"]
    assert report["owner_answer_record"] is None
    assert (storage_dir / "tenant_textil_001" / "anamnesis.jsonl").exists()
    assert (storage_dir / "tenant_textil_001" / "investigations.jsonl").exists()
    assert (storage_dir / "tenant_textil_001" / "owner_answers.jsonl").exists()
    assert report["evidence_used"] == ["excel_file_readable"]
    assert report["missing_evidence"] == []
    assert any("No inferir diagnóstico" in warning for warning in report["limit_warnings"])


def test_vertical_slice_build_report_binds_owner_answer_when_provided(tmp_path: Path):
    excel = tmp_path / "caso.xlsx"
    storage_dir = tmp_path / "storage"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = vertical_slice.inspect_excel(excel)

    report = vertical_slice.build_report(
        excel,
        "vendo mas pero no me queda plata",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
        storage_dir=storage_dir,
        owner_answer="Las ventas están en la hoja Ventas.",
        owner_answer_question_ref="missing_input:ventas",
    )

    answer = report["owner_answer_record"]
    assert answer["answer_id"].startswith("answer_")
    assert answer["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert answer["investigation_id"] == report["investigation_record"]["investigation_id"]
    assert answer["question_ref"] == "missing_input:ventas"
    assert answer["raw_owner_answer"] == "Las ventas están en la hoja Ventas."
    assert report["pipeline_run_record"]["metadata"]["owner_answer_id"] == answer["answer_id"]
    assert (storage_dir / "tenant_textil_001" / "owner_answers.jsonl").read_text(encoding="utf-8")


def test_vertical_slice_cli_renders_owner_answer_when_provided(tmp_path: Path, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas"], ["2026-06-01", "A", 100]])
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "vendo mas pero no me queda plata",
        "--storage-dir",
        str(tmp_path / "storage"),
        "--owner-answer",
        "Las ventas están en la hoja Ventas.",
        "--owner-answer-question-ref",
        "missing_input:ventas",
    ])
    out = capsys.readouterr().out

    assert rc == 0
    assert "Owner Answer ID: answer_" in out
    assert "## Respuesta del dueño" in out
    assert "Pregunta referida: missing_input:ventas" in out


def test_vertical_slice_cli_outputs_blocked_actionable_without_operational_columns(tmp_path: Path, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["columna_a"], ["dato"]])
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "hola",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "BLOCKED" in out
    assert "## Evidencia faltante" in out
    assert "- columnas_operativas" in out
    assert "## Próxima pregunta" in out


def test_vertical_slice_cli_uses_real_textile_fixture(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil y no me cierra la caja",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Reporte owner-facing local" in out
    assert "la_textil_cosida_srl_mar_abr_may_2026.xlsx" in out
    assert "Filas:" in out
    assert "Columnas:" in out
    assert "## Evidencia estructurada" in out
    assert "Variables computables:" in out
    assert "no diagnostica" in out.lower()


def test_vertical_slice_cli_reports_evidence_sufficiency_for_requested_formula(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil y no me cierra la caja",
        "--storage-dir",
        str(tmp_path / "storage"),
        "--formula-id",
        "PYME_033_concentracion_sku",
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "## Suficiencia de evidencia" in out
    assert "Case ID: intake_cli_local" in out
    assert "PYME_033_concentracion_sku" in out
    assert "READY" in out or "MISSING_INPUTS" in out
    assert "no diagnostica" in out.lower()


def test_vertical_slice_cli_reports_unsupported_formula_without_crashing(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil y no me cierra la caja",
        "--storage-dir",
        str(tmp_path / "storage"),
        "--formula-id",
        "FORMULA_INEXISTENTE",
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "## Suficiencia de evidencia" in out
    assert "FORMULA_INEXISTENTE: UNSUPPORTED_FORMULA" in out
    assert "no diagnostica" in out.lower()


def test_vertical_slice_cli_writes_markdown_output_file(tmp_path: Path):
    excel = tmp_path / "caso.xlsx"
    output = tmp_path / "salida" / "reporte.md"
    _write_excel(excel, [["fecha", "producto", "ventas"], ["2026-06-01", "A", 100]])
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "hola",
        "--tenant-id",
        "tenant_demo_001",
        "--intake-id",
        "intake_demo_001",
        "--storage-dir",
        str(tmp_path / "storage"),
        "--empresa-tipo",
        "comercio",
        "--industria",
        "retail",
        "--modelo-comercial",
        "b2c",
        "--canal-venta",
        "local",
        "--area-critica",
        "margen",
        "--output",
        str(output),
    ])
    assert rc == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Reporte owner-facing local" in text
    assert "DELIVERED_CANDIDATE" in text
    assert "## Evidencia usada" in text
    assert "Tenant: tenant_demo_001" in text
    assert "Intake: intake_demo_001" in text
    assert "Anamnesis ID: anamnesis_" in text
    assert "Investigation ID: investigation_" in text
    assert "## Anamnesis" in text
    assert "Empresa tipo: comercio" in text
    assert "Industria: retail" in text
    assert "Modelo comercial: b2c" in text
    assert "Canales de venta: local" in text
    assert "Áreas críticas: margen" in text
    assert "Case ID: intake_demo_001" in text


def test_vertical_slice_cli_rejects_missing_excel(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        vertical_slice.main([
            "--excel",
            str(tmp_path / "faltante.xlsx"),
            "--message",
            "hola",
            "--storage-dir",
            str(tmp_path / "storage"),
        ])


def test_vertical_slice_module_does_not_import_forbidden_runtime_layers():
    source = Path(vertical_slice.__file__).read_text(encoding="utf-8").lower()
    forbidden = [
        "telegram",
        "conversa",
        "pymia.hermes",
        "pymia.llm_operator",
        "pymia.mcp_server",
        "fastapi",
    ]
    for token in forbidden:
        assert token not in source


# --- Audit gap: variable/table names in report ---


def test_vertical_slice_report_shows_computed_variable_names(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Variables computables:" in out
    indented = [l for l in out.splitlines() if l.startswith("  - ")]
    assert len(indented) > 0, "Variable names should be listed as indented items"


def test_vertical_slice_report_uses_language_corpus_for_known_variable_labels(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ventas brutas (ventas_total)" in out
    assert "costo de mercaderia vendida (costos_total)" in out


def test_vertical_slice_report_shows_table_sheet_names(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Tablas estructuradas:" in out
    table_lines = [l for l in out.splitlines() if l.startswith("  - ") and " filas," in l]
    assert len(table_lines) > 0, "Table sheets with dimensions should be listed"


def test_vertical_slice_build_report_contains_variable_names(tmp_path):
    excel = tmp_path / "vars.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(excel, "test", profile, storage_dir=Path(tmp_path / "storage"))
    summary = report.get("structured_evidence_summary", {})
    assert "computed_variable_names" in summary
    assert isinstance(summary["computed_variable_names"], list)
    assert "table_sheets" in summary
    assert isinstance(summary["table_sheets"], list)


def test_vertical_slice_next_question_specific_not_diagnosing(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    lines = out.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.startswith("## Próxima pregunta"):
            idx = i
            break
    assert idx is not None
    for j in range(idx + 1, min(idx + 3, len(lines))):
        if lines[j].startswith("- "):
            q = lines[j][2:].strip()
            assert len(q) > 5, f"Question too short: {q}"
            for bad in ["tu margen", "estás ganando", "deberías", "tienes que", "diagnóstico"]:
                assert bad not in q.lower(), f"Question contains '{bad}': {q}"
            break


def test_vertical_slice_graceful_with_minimal_excel(tmp_path, capsys):
    excel = tmp_path / "minimal.xlsx"
    _write_excel(excel, [["a", "b"], ["1", "2"]])
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "test",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Variables computables:" in out
    assert "no diagnostica" in out.lower()


# --- Owner-facing language for next question ---


def test_vertical_slice_next_question_uses_owner_language(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    lines = out.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.startswith("## Próxima pregunta"):
            idx = i
            break
    assert idx is not None
    for j in range(idx + 1, len(lines)):
        line = lines[j]
        if line.startswith("- ") and not line.startswith("  - "):
            q = line[2:].strip()
            assert "información sobre" in q, f"Expected owner language, got: {q}"
            assert "INV_" not in q.split(" ")[0] if q.startswith("Falta") else True
            assert "PYME_" not in q, f"Question should not contain formula IDs: {q}"
            assert "_" not in q.replace("¿", "").replace("?", ""), f"Question has snake_case: {q}"
            break


def test_vertical_slice_next_question_keeps_technical_reference_for_operator(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "  - Referencia técnica:" in out
    assert "INV_" in out or "PYME_" in out or "LIQ_" in out
    assert "_" in out.split("  - Referencia técnica:")[1] if "  - Referencia técnica:" in out else False


def test_vertical_slice_next_question_does_not_expose_formula_id_as_primary_owner_text(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    lines = out.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.startswith("## Próxima pregunta"):
            idx = i
            break
    assert idx is not None
    for j in range(idx + 1, len(lines)):
        line = lines[j]
        if line.startswith("- ") and not line.startswith("  - "):
            q = line[2:].strip()
            for code in ["INV_001", "LIQ_001", "REN_001", "PYME_033", "PYME_011"]:
                assert code not in q, f"Owner question exposes internal code {code}: {q}"
            break


def test_vertical_slice_next_question_does_not_diagnose_or_prescribe(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    lines = out.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.startswith("## Próxima pregunta"):
            idx = i
            break
    assert idx is not None
    for j in range(idx + 1, len(lines)):
        line = lines[j]
        if line.startswith("- ") and not line.startswith("  - "):
            q = line[2:].strip()
            for bad in ["tu margen", "estás ganando", "deberías", "tienes que", "diagnóstico"]:
                assert bad not in q.lower(), f"Question contains diagnostic: {q}"
            for action in ["subí", "aumentá", "reducí", "comprá", "vende", "contratá"]:
                assert action not in q.lower(), f"Question prescribes action: {q}"
            break


def test_vertical_slice_report_preserves_candidate_status_and_warnings(tmp_path: Path, capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DELIVERED_CANDIDATE" in out
    assert "No inferir diagnóstico" in out
    assert "no diagnostica sin evidencia" in out.lower()
    assert "No es canal productivo" in out or "no es canal productivo" in out.lower()
    assert "resultado candidato" in out.lower()


def test_vertical_slice_cli_aligns_owner_question_when_misaligned(tmp_path: Path, monkeypatch, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])

    def mock_build(*args, **kwargs):
        return {
            "status": "available",
            "computed_variables_count": 0,
            "computed_variable_names": [],
            "tables_count": 0,
            "table_sheets": [],
            "case_id": "test",
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "catalog_reconciliation": [{
                "formula_id": "INV_001",
                "pathology_code": "INV_001",
                "status": "MISSING_INPUTS",
                "available_evidence": [],
                "missing_evidence": ["lead_time_proveedor"],
                "matched_sources": [],
                "required_evidence": [],
                "required_variables": [],
                "next_audit_questions": ["¿Podés compartir los tiempos de reposición de proveedores?"]
            }]
        }
    monkeypatch.setattr(vertical_slice, "build_structured_summary", mock_build)

    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "no me cierra la caja, me falta plata",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Entiendo que tu preocupación principal parece ser caja/liquidez" in out
    assert "Antes de avanzar con una pregunta técnica sobre stock" in out
    assert "reconducción_axis_caja_liquidez" in out
    assert "tiempos de reposición" not in out
