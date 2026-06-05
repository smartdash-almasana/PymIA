from __future__ import annotations

from pathlib import Path


PROTOCOL = Path("docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_PROTOCOL.md")
PLAN = Path("docs/roadmap/M31_SERVICIO_ASISTIDO_REPETIBLE_PLAN.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_m31_protocol_document_exists_and_declares_non_product_scope() -> None:
    text = _read(PROTOCOL)

    assert "M31" in text
    assert "Servicio asistido repetible" in text
    assert "no declara producto final" in text.lower()
    assert "no declara autonomía end-to-end" in text.lower()
    assert "no declara servicio comercial validado" in text.lower()


def test_m31_protocol_contains_entry_block_delivery_continuity_measurement_and_learning() -> None:
    text = _read(PROTOCOL).lower()

    required_terms = [
        "criterio de entrada",
        "criterio de bloqueo",
        "checklist de ejecución",
        "intake",
        "evidencia",
        "análisis",
        "reporte",
        "continuidad",
        "medición",
        "aprendizaje pymia",
        "criterio de repetibilidad",
        "criterio de no repetibilidad",
    ]

    for term in required_terms:
        assert term in text


def test_m31_protocol_defines_pilot_record_template_and_decision_metrics() -> None:
    text = _read(PROTOCOL).lower()

    required_fields = [
        "pilot_id",
        "tenant_id",
        "case_id",
        "problema_declarado",
        "archivos_recibidos",
        "estado_evidencia",
        "hallazgos",
        "reporte_ref",
        "proximo_paso",
        "min_total",
        "bloqueos",
        "aprendizajes",
        "casos_totales",
        "casos_entregados",
        "casos_bloqueados",
        "tiempo_promedio_total",
        "se_puede_repetir_sin_improvisar",
    ]

    for field in required_fields:
        assert field in text


def test_m31_plan_and_protocol_preserve_scope_boundaries() -> None:
    combined = (_read(PLAN) + "\n" + _read(PROTOCOL)).lower()

    required_boundaries = [
        "registry/capabilities.yaml",
        "dispatcher",
        "telegram/pdf/html/ui",
        "erp/odoo/dolibarr",
        "llm/red",
        "producto final",
    ]

    for boundary in required_boundaries:
        assert boundary in combined
