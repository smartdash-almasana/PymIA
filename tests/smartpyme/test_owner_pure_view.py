from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.owner_pure_view import (
    SAFE_LIMIT_WARNING,
    build_owner_pure_view,
)


def test_delivered_candidate_returns_plain_owner_view() -> None:
    view = build_owner_pure_view(
        report={
            "status": "DELIVERED_CANDIDATE",
            "file_name": "ventas_junio.xlsx",
            "rows": 25,
            "columns": 4,
            "headers": ["fecha", "producto", "ventas", "costo"],
            "table_sheets": [{"name": "Ventas", "rows": 24, "columns": 4}],
            "next_questions": ["¿Confirmás que este archivo corresponde a junio?"],
        }
    )

    assert view["schema_version"] == "OWNER_PURE_VIEW_V1"
    assert view["status"] == "DELIVERED_CANDIDATE"
    assert view["title"] == "Primera lectura lista para revisar."
    assert "primera lectura" in view["owner_summary"]
    assert "Archivo recibido: ventas_junio.xlsx." in view["what_we_could_read"]
    assert "La planilla tiene 25 filas y 4 columnas visibles." in view["what_we_could_read"]
    assert "Columnas detectadas: fecha, producto, ventas, costo." in view["what_we_could_read"]
    assert "Hojas con tablas detectadas: Ventas." in view["what_we_could_read"]
    assert view["what_is_missing"] == []
    assert view["next_question"] == "¿Confirmás que este archivo corresponde a junio?"
    assert view["next_step"] == "Revisar esta primera lectura con el dueño antes de tomarla como diagnóstico."
    assert view["limits"] == [SAFE_LIMIT_WARNING]


def test_blocked_view_translates_missing_evidence_to_actionable_owner_language() -> None:
    view = build_owner_pure_view(
        report={
            "status": "BLOCKED",
            "file_name": "archivo.xlsx",
            "rows": 2,
            "columns": 1,
            "headers": ["columna_a"],
            "missing_evidence": ["columnas_operativas", "filas_de_datos"],
            "next_questions": [],
        }
    )

    assert view["status"] == "BLOCKED"
    assert view["title"] == "Necesito un dato más para avanzar con seguridad."
    assert view["what_is_missing"] == [
        "Faltan columnas operativas como fecha, producto, ventas, precio, costo, cantidad o SKU.",
        "Faltan filas de datos además de los encabezados.",
    ]
    assert view["next_question"] == "¿Podés completar o confirmar la evidencia faltante para seguir?"
    assert view["next_step"] == "Completar la evidencia faltante antes de calcular o diagnosticar."
    assert SAFE_LIMIT_WARNING in view["limits"]


def test_rejects_technical_leak_in_owner_summary() -> None:
    with pytest.raises(ValueError, match="technical term"):
        build_owner_pure_view(
            report={
                "status": "DELIVERED_CANDIDATE",
                "owner_summary": "structured_evidence listo para formula_ids",
            }
        )


def test_rejects_technical_leak_in_next_question() -> None:
    with pytest.raises(ValueError, match="technical term"):
        build_owner_pure_view(
            report={
                "status": "BLOCKED",
                "next_questions": ["¿Confirmás el runtime_authorized?"],
            }
        )


def test_rejects_unsupported_status() -> None:
    with pytest.raises(ValueError, match="only accepts"):
        build_owner_pure_view(report={"status": "PROCESSING"})


def test_owner_pure_view_module_has_no_io_pipeline_llm_or_runtime_dependencies() -> None:
    import pymia.smartpyme.owner_pure_view as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert "Path(" not in source
    assert "openpyxl" not in source
    assert "vertical_pipeline" not in source.replace('"vertical_pipeline",', "")
    assert "document_ingestion" not in source.replace('"document_ingestion",', "")
    assert "openai" not in source.lower()
    assert "langchain" not in source.lower()
    assert "requests" not in source.lower()
    assert "httpx" not in source.lower()
    assert "runtime_authorized" not in source.replace('"runtime_authorized",', "")
