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
    assert (storage_dir / "tenant_textil_001" / "evidence_requests.jsonl").exists()
    assert report["evidence_used"] == ["excel_file_readable"]
    assert report["missing_evidence"] == []
    assert any("No inferir diagnóstico" in warning for warning in report["limit_warnings"])


def test_vertical_slice_build_report_includes_owner_simple_view(tmp_path: Path):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = vertical_slice.inspect_excel(excel)

    report = vertical_slice.build_report(
        excel,
        "no me cierra la caja, me falta plata",
        profile,
        storage_dir=tmp_path / "storage",
    )

    owner_simple = report["owner_simple"]
    assert set(owner_simple) == {
        "que_entendimos",
        "que_pudimos_leer",
        "que_todavia_no_podemos_afirmar",
        "proxima_pregunta",
        "limites",
    }
    assert "caja y liquidez" in owner_simple["que_entendimos"].lower()
    assert "La planilla contiene información de" in owner_simple["que_pudimos_leer"]
    assert owner_simple["que_todavia_no_podemos_afirmar"] == "Todavía no hay evidencia suficiente para identificar una causa raíz."
    assert owner_simple["proxima_pregunta"] in report["next_questions"] or owner_simple["proxima_pregunta"]
    assert owner_simple["limites"][-1] == "No diagnostica sin evidencia suficiente ni confirmación del dueño."
    assert "diagnóstico confirmado" not in owner_simple["que_todavia_no_podemos_afirmar"].lower()


def test_vertical_slice_cli_renders_owner_simple_sections(tmp_path: Path, capsys):
    excel = tmp_path / "caso.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])

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
    assert "Qué entendimos:" in out
    assert "Qué pudimos leer:" in out
    assert "Qué todavía no podemos afirmar:" in out
    assert "Próxima pregunta:" in out
    assert "Límites:" in out
    assert "Todavía no hay evidencia suficiente para identificar una causa raíz." in out
    assert "No inferir diagnóstico" in out
    assert "diagnóstico confirmado" not in out.lower()


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


def test_vertical_slice_build_report_binds_evidence_request_when_missing_inputs(tmp_path: Path, monkeypatch):
    excel = tmp_path / "caso.xlsx"
    storage_dir = tmp_path / "storage"
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
                "formula_id": "LIQ_001",
                "pathology_code": "LIQ_001",
                "status": "MISSING_INPUTS",
                "available_evidence": [],
                "missing_evidence": ["cobranzas_del_periodo"],
                "matched_sources": [],
                "required_evidence": [],
                "required_variables": [],
                "next_audit_questions": ["¿Podés compartir cobranzas del período?"]
            }]
        }

    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build)
    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(
        excel,
        "no me cierra la caja",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
        storage_dir=storage_dir,
    )

    request = report["evidence_request_record"]
    assert request["request_id"].startswith("evidence_request_")
    assert request["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert request["investigation_id"] == report["investigation_record"]["investigation_id"]
    assert request["requested_evidence"] == ["cobranzas_del_periodo"]
    assert report["evidence_record"]["request_id"] == request["request_id"]
    assert report["pipeline_run_record"]["metadata"]["evidence_request_id"] == request["request_id"]
    assert (storage_dir / "tenant_textil_001" / "evidence_requests.jsonl").read_text(encoding="utf-8")


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


def test_vertical_slice_cli_renders_evidence_request_when_missing_inputs(tmp_path: Path, monkeypatch, capsys):
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
                "formula_id": "LIQ_001",
                "pathology_code": "LIQ_001",
                "status": "MISSING_INPUTS",
                "available_evidence": [],
                "missing_evidence": ["cobranzas_del_periodo"],
                "matched_sources": [],
                "required_evidence": [],
                "required_variables": [],
                "next_audit_questions": ["¿Podés compartir cobranzas del período?"]
            }]
        }

    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build)
    rc = vertical_slice.main([
        "--excel",
        str(excel),
        "--message",
        "no me cierra la caja",
        "--storage-dir",
        str(tmp_path / "storage"),
    ])
    out = capsys.readouterr().out

    assert rc == 0
    assert "Evidence Request ID: evidence_request_" in out
    assert "## Solicitud de evidencia" in out
    assert "cobranzas del período" in out


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


def test_build_report_injects_serialized_diagnostic_result(tmp_path: Path, monkeypatch):
    excel = tmp_path / "diagnostic.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo", "impuestos"], ["2026-06-01", "A", 1000, 900, 200]])

    def mock_build_summary(*args, **kwargs):
        return {
            "status": "available",
            "computed_variables_count": 3,
            "computed_variable_names": ["costos_total", "impuestos_total", "ventas_total"],
            "tables_count": 1,
            "table_sheets": [{"name": "Sheet", "columns": 5, "rows": 1}],
            "case_id": "case-1",
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "catalog_reconciliation": [{
                "formula_id": "REN_001_margen_neto_real",
                "pathology_code": "REN_001",
                "status": "calculable",
                "available_evidence": ["ventas_del_periodo", "costos_directos", "impuestos_y_comisiones"],
                "missing_evidence": [],
                "matched_sources": ["sheet:ventas", "sheet:costos", "sheet:impuestos"],
                "required_evidence": ["ventas_del_periodo", "costos_directos", "impuestos_y_comisiones"],
                "required_variables": ["sale_price", "costs", "taxes"],
                "next_audit_questions": [],
            }],
        }

    def mock_context(*args, **kwargs):
        return {
            "structured_evidence": {
                "tenant_id": "tenant_textil_001",
                "document_type": "xlsx_operational_evidence",
                "source": "xlsx_upload",
                "file_name": "diagnostic.xlsx",
                "tables": [],
                "computed_variables": {
                    "ventas_total": 1000.0,
                    "costos_total": 900.0,
                    "impuestos_total": 200.0,
                },
                "metadata": {
                    "variable_source_refs": {
                        "ventas_total": ["sheet:ventas"],
                        "costos_total": ["sheet:costos"],
                        "impuestos_total": ["sheet:impuestos"],
                    }
                },
            },
            "formula_ids": ["REN_001_margen_neto_real"],
        }

    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build_summary)
    monkeypatch.setattr(
        "pymia.smartpyme.structured_evidence_builder.build_structured_evidence_context",
        mock_context,
    )

    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(
        excel,
        "test diagnóstico interno",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="case-1",
        storage_dir=Path(tmp_path / "storage"),
    )

    diagnostic = report["diagnostic_pipeline_result"]
    assert diagnostic is not None
    assert isinstance(diagnostic, dict)
    assert diagnostic["report"]["diagnosis_status"] == "CONFIRMED"
    assert diagnostic["report"]["kernel_state"] == "PASS"
    assert diagnostic["pathology_findings"][0]["pathology_id"] == "REN_001"
    assert diagnostic["formula_results"][0]["formula_id"] == "REN_001_margen_neto_real"
    assert diagnostic["report"]["evidence_used"] == ["sheet:ventas", "sheet:costos", "sheet:impuestos"]
    assert "diagnostic_pipeline_result" not in report["pipeline_run_record"]
    assert "diagnostic_pipeline_result" not in report["pipeline_run_record"].get("metadata", {})


def test_build_pipeline_exposes_operator_diagnostic_summary_without_markdown(tmp_path: Path, monkeypatch):
    excel = tmp_path / "diagnostic.xlsx"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo", "impuestos"], ["2026-06-01", "A", 1000, 900, 200]])

    def mock_build_summary(*args, **kwargs):
        return {
            "status": "available",
            "computed_variables_count": 3,
            "computed_variable_names": ["costos_total", "impuestos_total", "ventas_total"],
            "tables_count": 1,
            "table_sheets": [{"name": "Sheet", "columns": 5, "rows": 1}],
            "case_id": "case-1",
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "catalog_reconciliation": [{
                "formula_id": "REN_001_margen_neto_real",
                "pathology_code": "REN_001",
                "status": "calculable",
                "available_evidence": ["ventas_del_periodo", "costos_directos", "impuestos_y_comisiones"],
                "missing_evidence": [],
                "matched_sources": ["sheet:ventas", "sheet:costos", "sheet:impuestos"],
                "required_evidence": ["ventas_del_periodo", "costos_directos", "impuestos_y_comisiones"],
                "required_variables": ["sale_price", "costs", "taxes"],
                "next_audit_questions": [],
            }],
        }

    def mock_context(*args, **kwargs):
        return {
            "structured_evidence": {
                "tenant_id": "tenant_textil_001",
                "document_type": "xlsx_operational_evidence",
                "source": "xlsx_upload",
                "file_name": "diagnostic.xlsx",
                "tables": [],
                "computed_variables": {
                    "ventas_total": 1000.0,
                    "costos_total": 900.0,
                    "impuestos_total": 200.0,
                },
                "metadata": {
                    "variable_source_refs": {
                        "ventas_total": ["sheet:ventas"],
                        "costos_total": ["sheet:costos"],
                        "impuestos_total": ["sheet:impuestos"],
                    }
                },
            },
            "formula_ids": ["REN_001_margen_neto_real"],
        }

    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build_summary)
    monkeypatch.setattr(
        "pymia.smartpyme.structured_evidence_builder.build_structured_evidence_context",
        mock_context,
    )

    pipeline = vertical_slice.build_pipeline(
        excel,
        "test diagnóstico interno",
        tenant_id="tenant_textil_001",
        intake_id="case-1",
        storage_dir=Path(tmp_path / "storage"),
    )

    summary = pipeline["diagnostic_operator_summary"]
    assert summary == {
        "status": "available",
        "diagnosis_status": "CONFIRMED",
        "kernel_state": "PASS",
        "blocking_reason": None,
        "finding_types": ["REN_001"],
        "formulas_used": ["REN_001_margen_neto_real"],
        "evidence_used": ["sheet:ventas", "sheet:costos", "sheet:impuestos"],
        "gate_status": "ready",
        "blocked_formulas": [],
        "missing_variables": {},
        "pending_pathologies": [],
        "unsupported_pathologies": [],
        "owner_safe_question_candidates": [],
        "suggested_operator_next_step": "Solicitar evidencia faltante antes de reintentar diagnóstico.",
    }
    assert "diagnostic_operator_summary" not in pipeline["markdown"]
    assert "REN_001" not in pipeline["markdown"]
    assert "margen_neto_real" not in pipeline["markdown"]


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
    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build)

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


def test_operator_summary_explains_gate_blocked_missing_inputs(tmp_path: Path, monkeypatch):
    excel = tmp_path / "caso_bloqueado.xlsx"
    _write_excel(excel, [["fecha", "ventas", "costo"], ["2026-06-01", "1000", "600"]])

    def mock_build_summary(*args, **kwargs):
        return {
            "status": "available",
            "computed_variables_count": 2,
            "computed_variable_names": ["costos_total", "ventas_total"],
            "tables_count": 1,
            "table_sheets": [{"name": "Sheet", "columns": 3, "rows": 1}],
            "case_id": "intake_textil_001",
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "catalog_reconciliation": [
                {
                    "formula_id": "LIQ_001_vendido_cobrado",
                    "pathology_code": "LIQ_001",
                    "status": "pending_data",
                    "available_evidence": ["ventas_del_periodo"],
                    "missing_evidence": ["cobranzas_del_periodo"],
                    "matched_sources": [],
                    "required_evidence": ["ventas_del_periodo", "cobranzas_del_periodo"],
                    "required_variables": ["sold_amount", "collected_amount"],
                    "next_audit_questions": ["¿Cuánto cobraste en el período?"],
                },
                {
                    "formula_id": "REN_001_margen_neto_real",
                    "pathology_code": "REN_001",
                    "status": "pending_data",
                    "available_evidence": ["ventas_del_periodo", "costos_directos"],
                    "missing_evidence": ["impuestos_y_comisiones"],
                    "matched_sources": [],
                    "required_evidence": ["ventas_del_periodo", "costos_directos", "impuestos_y_comisiones"],
                    "required_variables": ["sale_price", "costs", "taxes"],
                    "next_audit_questions": ["¿Cuánto pagaste en impuestos?"],
                },
                {
                    "formula_id": "INV_002_rotacion_stock",
                    "pathology_code": "INV_002",
                    "status": "pending_data",
                    "available_evidence": ["costos_directos"],
                    "missing_evidence": ["stock_promedio"],
                    "matched_sources": [],
                    "required_evidence": ["costos_directos", "stock_promedio"],
                    "required_variables": ["cost_of_goods_sold", "average_stock"],
                    "next_audit_questions": ["¿Cuál es tu stock promedio?"],
                },
            ],
        }

    def mock_context(*args, **kwargs):
        return {
            "structured_evidence": {
                "tenant_id": "tenant_textil_001",
                "document_type": "xlsx_operational_evidence",
                "source": "xlsx_upload",
                "file_name": "caso_bloqueado.xlsx",
                "tables": [],
                "computed_variables": {
                    "ventas_total": 1000.0,
                    "costos_total": 600.0,
                },
                "metadata": {
                    "variable_source_refs": {
                        "ventas_total": ["sheet:ventas"],
                        "costos_total": ["sheet:costos"],
                    }
                },
            },
            "formula_ids": ["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real", "INV_002_rotacion_stock"],
        }

    monkeypatch.setattr("pymia.application.vertical_pipeline.build_structured_summary", mock_build_summary)
    monkeypatch.setattr(
        "pymia.smartpyme.structured_evidence_builder.build_structured_evidence_context",
        mock_context,
    )

    pipeline = vertical_slice.build_pipeline(
        excel,
        "tengo una textil y no me cierra la caja",
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
        storage_dir=tmp_path / "storage",
    )

    summary = pipeline.get("diagnostic_operator_summary")
    assert summary is not None
    assert summary["status"] == "available"
    assert summary["diagnosis_status"] == "INSUFFICIENT_EVIDENCE"
    assert summary["kernel_state"] == "BLOCKED"
    assert summary["blocking_reason"] == "EVIDENCE_USED_REQUIRED"
    assert summary["gate_status"] == "blocked"

    assert "LIQ_001_vendido_cobrado" in summary["blocked_formulas"]
    assert "REN_001_margen_neto_real" in summary["blocked_formulas"]
    assert "INV_002_rotacion_stock" in summary["blocked_formulas"]

    assert "collected_amount" in summary["missing_variables"]["LIQ_001_vendido_cobrado"]
    assert "taxes" in summary["missing_variables"]["REN_001_margen_neto_real"]
    assert "average_stock" in summary["missing_variables"]["INV_002_rotacion_stock"]

    assert "LIQ_001" in summary["pending_pathologies"]
    assert "REN_001" in summary["pending_pathologies"]
    assert "INV_002" in summary["pending_pathologies"]

    assert "LIQ_001" in summary["unsupported_pathologies"]
    assert "REN_001" not in summary["unsupported_pathologies"]
    assert "INV_002" in summary["unsupported_pathologies"]

    assert len(summary["owner_safe_question_candidates"]) > 0

    markdown = pipeline["markdown"]
    assert "REN_001" not in markdown
    assert "unsupported_pathologies" not in markdown
    assert "BLOCK_MISSING_INPUTS" not in markdown
    assert "diagnostic_operator_summary" not in markdown
    assert "EVIDENCE_USED_REQUIRED" not in markdown
