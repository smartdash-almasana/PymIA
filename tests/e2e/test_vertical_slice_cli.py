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
    rc = vertical_slice.main(["--excel", str(excel), "--message", "vendo mas pero no me queda plata"])
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
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(
        excel,
        "vendo mas pero no me queda plata",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
    )
    assert report["status"] == "DELIVERED_CANDIDATE"
    assert report["tenant_id"] == "tenant_textil_001"
    assert report["intake_id"] == "intake_textil_001"
    assert report["evidence_used"] == ["excel_file_readable"]
    assert report["missing_evidence"] == []
    assert any("No inferir diagnóstico" in warning for warning in report["limit_warnings"])


def test_vertical_slice_cli_outputs_blocked_actionable_without_operational_columns(tmp_path: Path, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["columna_a"], ["dato"]])
    rc = vertical_slice.main(["--excel", str(excel), "--message", "hola"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "BLOCKED" in out
    assert "## Evidencia faltante" in out
    assert "- columnas_operativas" in out
    assert "## Próxima pregunta" in out


def test_vertical_slice_cli_uses_real_textile_fixture(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil y no me cierra la caja"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Reporte owner-facing local" in out
    assert "la_textil_cosida_srl_mar_abr_may_2026.xlsx" in out
    assert "Filas:" in out
    assert "Columnas:" in out
    assert "## Evidencia estructurada" in out
    assert "Variables computables:" in out
    assert "no diagnostica" in out.lower()


def test_vertical_slice_cli_reports_evidence_sufficiency_for_requested_formula(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil y no me cierra la caja",
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


def test_vertical_slice_cli_reports_unsupported_formula_without_crashing(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main([
        "--excel",
        str(fixture),
        "--message",
        "tengo una textil y no me cierra la caja",
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
    assert "Case ID: intake_demo_001" in text


def test_vertical_slice_cli_rejects_missing_excel(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        vertical_slice.main(["--excel", str(tmp_path / "faltante.xlsx"), "--message", "hola"])


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


def test_vertical_slice_report_shows_computed_variable_names(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Variables computables:" in out
    indented = [l for l in out.splitlines() if l.startswith("  - ")]
    assert len(indented) > 0, "Variable names should be listed as indented items"


def test_vertical_slice_report_uses_language_corpus_for_known_variable_labels(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ventas brutas (ventas_total)" in out
    assert "costo de mercaderia vendida (costos_total)" in out


def test_vertical_slice_report_shows_table_sheet_names(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
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


def test_vertical_slice_next_question_specific_not_diagnosing(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
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
    rc = vertical_slice.main(["--excel", str(excel), "--message", "test"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Variables computables:" in out
    assert "no diagnostica" in out.lower()


# --- Owner-facing language for next question ---


def test_vertical_slice_next_question_uses_owner_language(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
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
            # Owner language: starts with "Falta información" not "Falta evidencia"
            assert "información sobre" in q, f"Expected owner language, got: {q}"
            # No raw formula IDs
            assert "INV_" not in q.split(" ")[0] if q.startswith("Falta") else True
            assert "PYME_" not in q, f"Question should not contain formula IDs: {q}"
            # No snake_case in owner question
            assert "_" not in q.replace("¿", "").replace("?", ""), f"Question has snake_case: {q}"
            break


def test_vertical_slice_next_question_keeps_technical_reference_for_operator(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "  - Referencia técnica:" in out
    # Should contain formula_id
    assert "INV_" in out or "PYME_" in out or "LIQ_" in out
    # Should contain original snake_case field names
    assert "_" in out.split("  - Referencia técnica:")[1] if "  - Referencia técnica:" in out else False


def test_vertical_slice_next_question_does_not_expose_formula_id_as_primary_owner_text(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
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
            # The primary question line must not contain internal codes
            for code in ["INV_001", "LIQ_001", "REN_001", "PYME_033", "PYME_011"]:
                assert code not in q, f"Owner question exposes internal code {code}: {q}"
            break


def test_vertical_slice_next_question_does_not_diagnose_or_prescribe(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
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
            # Should not prescribe concrete actions
            for action in ["subí", "aumentá", "reducí", "comprá", "vende", "contratá"]:
                assert action not in q.lower(), f"Question prescribes action: {q}"
            break


def test_vertical_slice_report_preserves_candidate_status_and_warnings(capsys):
    fixture = Path("prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx")
    assert fixture.exists()
    rc = vertical_slice.main(["--excel", str(fixture), "--message", "tengo una textil"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DELIVERED_CANDIDATE" in out
    assert "No inferir diagnóstico" in out
    assert "no diagnostica sin evidencia" in out.lower()
    assert "No es canal productivo" in out or "no es canal productivo" in out.lower()
    assert "resultado candidato" in out.lower()
