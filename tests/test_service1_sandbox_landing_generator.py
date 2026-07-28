from __future__ import annotations

from pathlib import Path

from landing.build_service1_sandbox_html import SERVICE1_SANDBOX_HTML, build_service1_sandbox_html


def test_service1_sandbox_html_declares_safety_boundaries() -> None:
    assert "SANDBOX" in SERVICE1_SANDBOX_HTML
    assert "NO PRODUCCIÓN" in SERVICE1_SANDBOX_HTML
    assert "REVISIÓN HUMANA" in SERVICE1_SANDBOX_HTML
    assert "No envía archivos a un servidor" in SERVICE1_SANDBOX_HTML
    assert "no diagnostica" in SERVICE1_SANDBOX_HTML
    assert "no concilia" in SERVICE1_SANDBOX_HTML
    assert "no produce resultados contables finales" in SERVICE1_SANDBOX_HTML


def test_service1_sandbox_html_contains_xlsx_preview_owner_questions_and_txt_export() -> None:
    assert "xlsx.full.min.js" in SERVICE1_SANDBOX_HTML
    assert "sheet_to_json" in SERVICE1_SANDBOX_HTML
    assert "renderTabs" in SERVICE1_SANDBOX_HTML
    assert "renderActiveSheet" in SERVICE1_SANDBOX_HTML
    assert "¿Qué representa este archivo?" in SERVICE1_SANDBOX_HTML
    assert "¿Qué período cubre?" in SERVICE1_SANDBOX_HTML
    assert "¿Qué querés revisar primero?" in SERVICE1_SANDBOX_HTML
    assert "Exportar respuestas TXT" in SERVICE1_SANDBOX_HTML
    assert "PYMIA_SERVICIO_1_XLSX_SANDBOX_OWNER_ANSWERS_V1" in SERVICE1_SANDBOX_HTML


def test_service1_sandbox_html_blocks_sensitive_real_data_copy() -> None:
    assert "No subir datos reales sensibles" in SERVICE1_SANDBOX_HTML
    assert "Confirmo que no usaré datos reales sensibles" in SERVICE1_SANDBOX_HTML
    assert "sandbox y no producción" in SERVICE1_SANDBOX_HTML
    assert "real_client_claim: false" in SERVICE1_SANDBOX_HTML
    assert "runtime_authorized: false" in SERVICE1_SANDBOX_HTML
    assert "production_allowed: false" in SERVICE1_SANDBOX_HTML
    assert "human_review_required: true" in SERVICE1_SANDBOX_HTML


def test_service1_sandbox_html_has_no_backend_api_or_diagnostic_endpoint() -> None:
    forbidden_fragments = (
        "POST /api/curate",
        "fetch('/api/curate'",
        'fetch("/api/curate"',
        "Aprobar diagnóstico final",
        "Generar diagnóstico final",
        "conciliación definitiva aprobada",
        "Mercado Pago API habilitada",
        "Servicio 2 habilitado",
    )

    for fragment in forbidden_fragments:
        assert fragment not in SERVICE1_SANDBOX_HTML


def test_build_service1_sandbox_html_writes_expected_file(tmp_path: Path) -> None:
    output_file = tmp_path / "servicio1-sandbox.html"

    result = build_service1_sandbox_html(output_file)

    assert result == output_file
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert content == SERVICE1_SANDBOX_HTML
    assert "PymIA Servicio 1 — Sandbox XLSX" in content
