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
