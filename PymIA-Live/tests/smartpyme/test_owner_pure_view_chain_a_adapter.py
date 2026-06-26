from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.owner_pure_view import build_owner_pure_view
from pymia.smartpyme.owner_pure_view_chain_a_adapter import (
    SCHEMA_VERSION,
    adapt_chain_a_report_to_owner_pure_view_input,
)


def _chain_a_report(*, with_owner_question: bool = True) -> dict:
    report = {
        "status": "DELIVERED_CANDIDATE",
        "summary": "Pude leer la planilla y armar una primera lectura candidata.",
        "missing_evidence": [],
        "next_questions": [
            "¿Podés confirmar a qué período corresponde este archivo?"
        ],
        "owner_question": (
            "¿Confirmás que estos datos corresponden al segundo trimestre?"
            if with_owner_question
            else None
        ),
        "limit_warnings": [
            "Slice local; no es canal productivo.",
            "No inferir diagnóstico a partir de nombres de columnas.",
        ],
        "references": ["/tmp/operaciones/cafeteria_abc.xlsx"],
        "structured_evidence_summary": {
            "table_sheets": [
                {"name": "Ventas", "columns": 4, "rows": 24},
                {"name": "Sucursales", "columns": 2, "rows": 3},
            ],
            "computed_variable_names": ["ventas_total", "costos_total"],
        },
    }
    return report


def test_adapter_maps_summary_to_owner_summary() -> None:
    report = _chain_a_report()

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert adapter_output["owner_summary"] == report["summary"]


def test_adapter_prioritizes_owner_question_over_next_questions() -> None:
    report = _chain_a_report(with_owner_question=True)

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    # The owner_question must take precedence and become the single next question.
    assert adapter_output["next_questions"] == [report["owner_question"]]
    assert report["next_questions"][0] not in adapter_output["next_questions"]


def test_adapter_falls_back_to_next_questions_when_owner_question_missing() -> None:
    report = _chain_a_report(with_owner_question=False)

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert adapter_output["next_questions"] == report["next_questions"]


def test_adapter_extracts_table_sheets_from_structured_evidence_summary() -> None:
    report = _chain_a_report()

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert adapter_output["table_sheets"] == [
        {"name": "Ventas", "columns": 4, "rows": 24},
        {"name": "Sucursales", "columns": 2, "rows": 3},
    ]


def test_adapter_extracts_file_name_from_references_zero() -> None:
    report = _chain_a_report()

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert adapter_output["file_name"] == "cafeteria_abc.xlsx"


def test_adapter_filters_internal_warning_not_owner_facing() -> None:
    report = _chain_a_report()

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert "Slice local; no es canal productivo." not in adapter_output["limit_warnings"]
    assert adapter_output["limit_warnings"] == [
        "No inferir diagnóstico a partir de nombres de columnas.",
    ]


def test_adapter_plus_owner_pure_view_uses_real_info_not_generic() -> None:
    report = _chain_a_report()

    view = build_owner_pure_view(
        report=adapt_chain_a_report_to_owner_pure_view_input(report)
    )

    # The view must surface real, non-generic facts derived from the report.
    assert view["status"] == "DELIVERED_CANDIDATE"
    assert view["owner_summary"] == report["summary"]
    assert any("cafeteria_abc.xlsx" in fact for fact in view["what_we_could_read"])
    assert any("Ventas" in fact for fact in view["what_we_could_read"])
    # The resolved owner_question wins as the next_question.
    assert view["next_question"] == report["owner_question"]
    # The internal warning must not leak into the owner view limits.
    assert "Slice local; no es canal productivo." not in view["limits"]


def test_adapter_does_not_recompute_rows_columns_headers() -> None:
    report = _chain_a_report()
    # Even if a fake 'rows'/'columns'/'headers' existed, the adapter must not
    # forward them, because those are out of scope for this mapping.
    report["rows"] = 999
    report["columns"] = 999
    report["headers"] = ["no_deberia_pasar"]

    adapter_output = adapt_chain_a_report_to_owner_pure_view_input(report)

    assert "rows" not in adapter_output
    assert "columns" not in adapter_output
    assert "headers" not in adapter_output


def test_adapter_module_has_no_forbidden_runtime_dependencies() -> None:
    import pymia.smartpyme.owner_pure_view_chain_a_adapter as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert "Path(" not in source
    assert "openpyxl" not in source
    # Docstring references to Chain A origin must not count as dependencies.
    assert "vertical_pipeline" not in source.replace(
        "Chain A (vertical_pipeline.build_report)", ""
    )
    assert "document_ingestion" not in source
    assert "First Aid" not in source
    assert "first_aid" not in source
    assert "openai" not in source.lower()
    assert "langchain" not in source.lower()
    assert "requests" not in source.lower()
    assert "httpx" not in source.lower()
    assert "runtime_authorized" not in source
    assert SCHEMA_VERSION == "OWNER_PURE_VIEW_CHAIN_A_ADAPTER_V1"
