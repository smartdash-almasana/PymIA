from __future__ import annotations

import json

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ConfirmationStatus,
    SemanticRectificationStatus,
)
from pymia.smartpyme.service_1_xlsx_structure_to_column_confirmation_v1 import (
    MAX_SAMPLE_VALUES_PER_COLUMN,
    STATUS_COLUMN_CONFIRMATION_READY,
    STATUS_NEEDS_HEADER_REVIEW,
    STATUS_NO_COLUMNS_DETECTED,
    build_service_1_xlsx_structure_to_column_confirmation_v1,
)


def _build_result(xlsx_structure: dict[str, object]):
    return build_service_1_xlsx_structure_to_column_confirmation_v1(
        xlsx_structure=xlsx_structure,
    )


def _strip_created_at(value):
    if isinstance(value, dict):
        return {
            key: _strip_created_at(item)
            for key, item in value.items()
            if key != "created_at"
        }
    if isinstance(value, list):
        return [_strip_created_at(item) for item in value]
    return value


def test_base_operacion_case_builds_matrix_and_owner_prompt_batch() -> None:
    result = _build_result(
        {
            "file_name": "distribuidora_mayorista_compleja.xlsx",
            "sheets": [
                {
                    "sheet_name": "OPERACION",
                    "headers": ["fecha", "cliente", "ruta", "sku", "cantidad", "venta", "costo", "margen"],
                    "sample_rows": [
                        ["2026-01-01", "Cliente A", "Ruta 1", "SKU-1", 10, 1000, 700, 300],
                    ],
                },
            ],
        }
    )

    assert result.status == STATUS_COLUMN_CONFIRMATION_READY
    assert result.matrix.file_name == "distribuidora_mayorista_compleja.xlsx"
    assert len(result.matrix.entries) == 8
    assert all(entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION for entry in result.matrix.entries)
    assert all(entry.owner_confirmed_role is None for entry in result.matrix.entries)
    assert all(entry.owner_rectified_function is None for entry in result.matrix.entries)
    assert all(entry.semantic_rectification_status == SemanticRectificationStatus.INFERRED_NOT_RECTIFIED for entry in result.matrix.entries)
    assert all(entry.suggested_semantic_role == "unknown" for entry in result.matrix.entries)
    assert all(entry.confidence == "unknown" for entry in result.matrix.entries)
    assert all(entry.calculation_relevance == CalculationRelevance.INFORMATIONAL for entry in result.matrix.entries)
    assert result.owner_prompt_batch.has_prompts is True
    assert result.owner_prompt_batch.actionable_entries_count == 8
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_anti_hardcode_does_not_depend_on_file_or_sheet_name() -> None:
    result = _build_result(
        {
            "file_name": "otro_archivo.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["columna_x", "importe_total", "observacion"],
                    "sample_rows": [
                        ["A", 1500, "nota"],
                    ],
                },
            ],
        }
    )

    assert result.status == STATUS_COLUMN_CONFIRMATION_READY
    assert result.file_name == "otro_archivo.xlsx"
    assert len(result.matrix.entries) == 3
    assert [entry.original_column_name for entry in result.matrix.entries] == ["columna_x", "importe_total", "observacion"]
    assert all(entry.sheet_name == "Datos" for entry in result.matrix.entries)
    assert all(entry.suggested_semantic_role == "unknown" for entry in result.matrix.entries)


def test_unknown_column_stays_unknown_and_pending_owner_confirmation() -> None:
    result = _build_result(
        {
            "file_name": "raro.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["XQZ_17"],
                    "sample_rows": [["valor extraño"]],
                },
            ],
        }
    )

    entry = result.matrix.entries[0]
    assert entry.suggested_semantic_role == "unknown"
    assert entry.confidence == "unknown"
    assert entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert result.owner_prompt_batch.has_prompts is True
    assert result.owner_prompt_batch.prompts[0].owner_label == "Rol no reconocido"


def test_preserves_sample_values_per_column_up_to_five_values() -> None:
    result = _build_result(
        {
            "file_name": "muestras.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["codigo", "importe"],
                    "sample_rows": [
                        ["A1", 10],
                        ["A2", 20],
                        ["A3", 30],
                        ["A4", 40],
                        ["A5", 50],
                        ["A6", 60],
                    ],
                },
            ],
        }
    )

    codigo, importe = result.matrix.entries
    assert codigo.sample_values == ["A1", "A2", "A3", "A4", "A5"]
    assert importe.sample_values == [10, 20, 30, 40, 50]
    assert len(codigo.sample_values) == MAX_SAMPLE_VALUES_PER_COLUMN
    assert len(importe.sample_values) == MAX_SAMPLE_VALUES_PER_COLUMN


def test_no_owner_rectification_is_created() -> None:
    result = _build_result(
        {
            "file_name": "sin_rectificacion.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["col_a", "col_b"],
                    "sample_rows": [["x", "y"]],
                },
            ],
        }
    )

    assert all(entry.owner_rectified_function is None for entry in result.matrix.entries)
    assert all(entry.owner_confirmed_role is None for entry in result.matrix.entries)


def test_no_runtime_no_tool_no_delivery_flags_anywhere() -> None:
    result = _build_result(
        {
            "file_name": "flags.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["col_a"],
                    "sample_rows": [["x"]],
                },
            ],
        }
    )

    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.owner_prompt_batch.runtime_authorized is False
    assert result.owner_prompt_batch.reexecution_authorized is False
    assert result.owner_prompt_batch.recalculation_authorized is False
    assert result.owner_prompt_batch.persistence_authorized is False


def test_owner_prompt_batch_to_dict_stays_owner_facing() -> None:
    result = _build_result(
        {
            "file_name": "owner_facing.xlsx",
            "sheets": [
                {
                    "sheet_name": "Datos",
                    "headers": ["venta", "margen"],
                    "sample_rows": [[100, 20]],
                },
            ],
        }
    )

    rendered = json.dumps(result.owner_prompt_batch.to_dict(), ensure_ascii=False)
    assert "computed_variables" not in rendered
    assert "venta_total" not in rendered
    assert "precio_venta" not in rendered
    assert "margen_bruto" not in rendered
    assert "owner_rectified_function" not in rendered
    assert "semantic_rectification_status" not in rendered


def test_empty_headers_returns_safe_status_without_crashing() -> None:
    result = _build_result(
        {
            "file_name": "sin_headers.xlsx",
            "sheets": [
                {
                    "sheet_name": "OPERACION",
                    "headers": [],
                    "sample_rows": [
                        ["2026-01-01", "Cliente A", 1000],
                    ],
                },
            ],
        }
    )

    assert result.status in {STATUS_NEEDS_HEADER_REVIEW, STATUS_NO_COLUMNS_DETECTED}
    assert result.matrix.entries == []
    assert result.owner_prompt_batch.has_prompts is False


def test_blank_headers_return_needs_header_review() -> None:
    result = _build_result(
        {
            "file_name": "blanco.xlsx",
            "sheets": [
                {
                    "sheet_name": "OPERACION",
                    "headers": ["", " ", None],
                    "sample_rows": [[1, 2, 3]],
                },
            ],
        }
    )

    assert result.status == STATUS_NEEDS_HEADER_REVIEW
    assert result.matrix.entries == []


def test_builder_is_deterministic_except_for_timestamps() -> None:
    xlsx_structure = {
        "file_name": "determinista.xlsx",
        "sheets": [
            {
                "sheet_name": "Datos",
                "headers": ["fecha", "cliente", "importe"],
                "sample_rows": [
                    ["2026-01-01", "Cliente A", 100],
                    ["2026-01-02", "Cliente B", 200],
                ],
            },
        ],
    }

    first = _build_result(xlsx_structure)
    second = _build_result(xlsx_structure)

    assert first.matrix.model_dump() == second.matrix.model_dump()
    assert _strip_created_at(first.owner_prompt_batch.to_dict()) == _strip_created_at(second.owner_prompt_batch.to_dict())
