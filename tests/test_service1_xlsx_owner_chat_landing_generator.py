from __future__ import annotations

from pathlib import Path

from landing.build_service1_xlsx_owner_chat_html import (
    SERVICE1_XLSX_OWNER_CHAT_HTML,
    build_service1_xlsx_owner_chat_html,
)


def test_xlsx_owner_chat_declares_real_structure_driven_flow() -> None:
    assert "El Excel entra. PymIA pregunta. El dueño responde." in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "lee la estructura real del XLSX" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "SheetNames" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "buildProfile" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "buildQuestions" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "findHeaderRow" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "detectSignals" in SERVICE1_XLSX_OWNER_CHAT_HTML


def test_xlsx_owner_chat_has_right_side_chat_and_owner_answer_loop() -> None:
    assert "Chat de confirmación" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "ownerInput" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "sendAnswer" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "nextQuestion" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "Marcar como no sé" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "Dueño:" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "PymIA:" in SERVICE1_XLSX_OWNER_CHAT_HTML


def test_xlsx_owner_chat_loads_xlsx_in_browser_with_sheetjs_and_preview_tabs() -> None:
    assert "xlsx.full.min.js" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "XLSX.read" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "sheet_to_json" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "renderTabs" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "renderActiveSheet" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "preview 30 filas" in SERVICE1_XLSX_OWNER_CHAT_HTML


def test_xlsx_owner_chat_exports_case_transcript_txt() -> None:
    assert "PYMIA_SERVICE_1_XLSX_OWNER_CHAT_V1" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "[FILE_PROFILE]" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "[ANSWERS]" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "pymia_service1_xlsx_owner_chat_" in SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "human_review_required: true" in SERVICE1_XLSX_OWNER_CHAT_HTML


def test_xlsx_owner_chat_has_no_fake_metrics_backend_or_final_claims() -> None:
    forbidden_fragments = (
        "Registros procesados",
        "Total facturado",
        "Lectura completada",
        "fetch(",
        "/api/curate",
        "diagnóstico final aprobado",
        "conciliación final",
        "resultado contable final aprobado",
        "Mercado Pago API",
        "Servicio 2 habilitado",
    )
    for fragment in forbidden_fragments:
        assert fragment not in SERVICE1_XLSX_OWNER_CHAT_HTML


def test_build_service1_xlsx_owner_chat_html_writes_expected_file(tmp_path: Path) -> None:
    output_file = tmp_path / "servicio1-xlsx-owner-chat.html"

    result = build_service1_xlsx_owner_chat_html(output_file)

    assert result == output_file
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert content == SERVICE1_XLSX_OWNER_CHAT_HTML
    assert "PymIA Servicio 1 — XLSX Owner Chat" in content
