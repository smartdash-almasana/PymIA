from __future__ import annotations

from pathlib import Path

from landing.build_service1_excel_ingestion_chat_web import (
    SERVICE1_EXCEL_INGESTION_CHAT_HTML,
    build_service1_excel_ingestion_chat_web,
)


def test_web_is_excel_ingestion_with_right_chat() -> None:
    assert "PymIA · Servicio 1 · Ingesta Excel + Chat" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "Excel cargado" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "Chat con el dueño" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "grid-template-columns:minmax(0,1fr) 430px" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "ownerInput" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "Enviar respuesta" in SERVICE1_EXCEL_INGESTION_CHAT_HTML


def test_web_reads_real_excel_structure_with_sheetjs() -> None:
    assert "xlsx.full.min.js" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "XLSX.read" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "sheet_to_json" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "workbook.SheetNames" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "profileWorkbook" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "profileSheet" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "findHeaderRow" in SERVICE1_EXCEL_INGESTION_CHAT_HTML


def test_web_questions_are_based_on_visible_structure_not_fake_business_classification() -> None:
    assert "hojas, filas, columnas y encabezados reales" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "¿Qué representa este archivo?" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "¿Qué período o fecha cubre este archivo?" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "¿Cuál querés revisar primero?" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "¿Qué contiene esta hoja?" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "¿Qué significan los principales?" in SERVICE1_EXCEL_INGESTION_CHAT_HTML


def test_web_has_no_simulation_backend_or_hardcoded_business_signals() -> None:
    forbidden = (
        "Registros procesados",
        "Total facturado",
        "Lectura completada",
        "Math.random",
        "fetch(",
        "/api/curate",
        "detectSignals",
        "ventas_junio.xlsx",
        "Textil Perales",
        "Mercado Pago API",
        "diagnóstico aprobado",
        "conciliación final",
    )
    for item in forbidden:
        assert item not in SERVICE1_EXCEL_INGESTION_CHAT_HTML


def test_web_export_is_json_conversation_payload_with_safe_flags() -> None:
    assert "PYMIA_SERVICE_1_EXCEL_INGESTION_CHAT_V1" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "file_profile:state.profile" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "answers:state.answers" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "runtime_authorized:false" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "production_allowed:false" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "final_diagnosis:false" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "final_accounting_result:false" in SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "application/json" in SERVICE1_EXCEL_INGESTION_CHAT_HTML


def test_build_web_writes_html(tmp_path: Path) -> None:
    output = tmp_path / "servicio1-excel-ingestion-chat.html"

    result = build_service1_excel_ingestion_chat_web(output)

    assert result == output
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert content == SERVICE1_EXCEL_INGESTION_CHAT_HTML
    assert "PymIA · Ingesta Excel + Chat" in content
