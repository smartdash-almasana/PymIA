from __future__ import annotations

from pathlib import Path

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.rendering.owner_markdown_renderer import render_markdown_from_report


def _minimal_report() -> dict:
    return {
        "status": "DELIVERED_CANDIDATE",
        "summary": "Resumen de prueba",
        "tenant_id": "tenant-test",
        "intake_id": "intake-test",
        "owner_simple": {
            "que_entendimos": "El dueño quiere revisar ventas.",
            "que_pudimos_leer": "Leímos una planilla de ventas.",
            "que_todavia_no_podemos_afirmar": "No podemos afirmar margen sin confirmar columnas.",
            "proxima_pregunta": "Confirmar columnas pendientes.",
            "limites": ["No diagnosticar sin evidencia confirmada."],
        },
        "anamnesis_record": {
            "anamnesis_id": "anamnesis-test",
            "business_taxonomy": {
                "empresa_tipo": "pyme",
                "industria": "gastronomia",
                "modelo_comercial": "venta directa",
                "canales_venta": ["mostrador"],
                "areas_criticas": ["ventas"],
            },
        },
        "investigation_record": {"investigation_id": "investigation-test"},
        "evidence_record": {"evidence_id": "evidence-test", "content_hash": "abc123"},
        "pipeline_run_record": {"run_id": "run-test"},
        "evidence_used": ["cafeteria_abc.xlsx"],
        "missing_evidence": [],
        "structured_evidence_summary": {
            "status": "available",
            "computed_variables_count": 0,
            "computed_variable_names": [],
            "tables_count": 1,
            "table_sheets": [{"name": "Ventas", "rows": 10, "columns": 3}],
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "case_id": "case-test",
        },
        "owner_question": "¿Podés confirmar estas columnas?",
        "limit_warnings": ["Los cálculos bloqueados no se presentan como resultados."],
    }


def _render(report: dict) -> str:
    return render_markdown_from_report(
        Path("cafeteria_abc.xlsx"),
        "Necesito revisar ventas",
        {"sheet": "Ventas", "rows": 10, "columns": 3},
        report,
        audience="owner",
    )


def test_owner_report_includes_column_confirmation_view_when_pending_columns_exist() -> None:
    report = _minimal_report()
    report["column_confirmation_matrix"] = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question='La columna "Total" representa el importe final de cada venta?',
            )
        ],
    )

    rendered = _render(report)

    assert "## Confirmación de columnas" in rendered
    assert "Columna: Total" in rendered
    assert "Relevancia: computacional" in rendered
    assert 'La columna "Total" representa el importe final de cada venta?' in rendered
    assert "Los cálculos bloqueados no se presentan como resultados." in rendered


def test_owner_report_does_not_include_column_confirmation_view_without_matrix() -> None:
    rendered = _render(_minimal_report())

    assert "## Confirmación de columnas" not in rendered
    assert "No hay confirmaciones de columnas pendientes" not in rendered


def test_owner_report_does_not_include_column_confirmation_view_when_no_pending_columns() -> None:
    report = _minimal_report()
    report["column_confirmation_matrix"] = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                owner_confirmed_role="venta_total",
                owner_question="No debe mostrarse",
            )
        ],
    )

    rendered = _render(report)

    assert "## Confirmación de columnas" not in rendered
    assert "No debe mostrarse" not in rendered
    assert "No hay confirmaciones de columnas pendientes" not in rendered


def test_owner_report_accepts_column_confirmation_matrix_as_dict() -> None:
    report = _minimal_report()
    report["column_confirmation_matrix"] = {
        "file_name": "cafeteria_abc.xlsx",
        "entries": [
            {
                "original_column_name": "MetodoPago",
                "sheet_name": "Ventas",
                "suggested_semantic_role": "payment_method",
                "calculation_relevance": "INFORMATIONAL",
                "confirmation_status": "PENDING_OWNER_CONFIRMATION",
                "owner_question": 'La columna "MetodoPago" indica la forma de pago?',
            }
        ],
    }

    rendered = _render(report)

    assert "## Confirmación de columnas" in rendered
    assert "Columna: MetodoPago" in rendered
    assert "Rol sugerido: metodo o forma de pago" in rendered
    assert "monto" not in rendered.lower()
    assert "importe" not in rendered.lower()
