from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.column_confirmation_v1 import (
    ConfirmationStatus,
    SemanticRectificationStatus,
)
from pymia.smartpyme.service_1_xlsx_structure_extraction_to_adapter_chain_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    build_service_1_xlsx_structure_extraction_to_adapter_chain_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1


TESTS_DIR = Path(__file__).resolve().parent.parent
PYMIA_LIVE = TESTS_DIR.parent
REPO_ROOT = PYMIA_LIVE.parent


@pytest.fixture
def real_xlsx_path() -> str:
    fixture = REPO_ROOT / "prueba_excels" / "cafeteria_abc.xlsx"
    if not fixture.exists():
        pytest.skip(f"Fixture not found: {fixture}")
    return str(fixture)


def _build_extracted_structure(*, file_name: str, sheet_name: str, headers: list[object], sample_rows=None) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "source_path_basename": file_name,
        "workbook": {
            "sheet_count": 1,
            "sheets": [
                {
                    "name": sheet_name,
                    "max_row": 10,
                    "max_column": len(headers),
                    "headers": headers,
                    "empty_header_count": 0,
                    "sample_rows_count": 9,
                    "sample_rows": sample_rows or [],
                }
            ],
        },
        "warnings": [],
        "runtime_authorized": False,
    }


def test_chain_accepts_real_extracted_structure_and_produces_matrix_and_prompts(real_xlsx_path: str) -> None:
    extracted = read_service_1_xlsx_structure_v1(real_xlsx_path)

    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=extracted,
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.extracted_file_name == extracted["source_path_basename"]
    assert result.adapter_input["file_name"] == extracted["source_path_basename"]
    assert len(result.column_confirmation_result.matrix.entries) > 0
    assert result.column_confirmation_result.owner_prompt_batch.has_prompts is True
    assert result.column_confirmation_result.owner_prompt_batch.actionable_entries_count == len(
        result.column_confirmation_result.matrix.entries
    )
    assert all(entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION for entry in result.column_confirmation_result.matrix.entries)
    assert all(entry.suggested_semantic_role == "unknown" for entry in result.column_confirmation_result.matrix.entries)
    assert all(entry.owner_rectified_function is None for entry in result.column_confirmation_result.matrix.entries)
    assert all(entry.owner_confirmed_role is None for entry in result.column_confirmation_result.matrix.entries)
    assert all(entry.semantic_rectification_status == SemanticRectificationStatus.INFERRED_NOT_RECTIFIED for entry in result.column_confirmation_result.matrix.entries)
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.column_confirmation_result.runtime_authorized is False
    assert result.column_confirmation_result.tool_execution_authorized is False
    assert result.column_confirmation_result.delivery_authorized is False
    assert result.column_confirmation_result.diagnosis_generated is False


def test_chain_does_not_depend_on_filename_or_sheet_name() -> None:
    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=_build_extracted_structure(
            file_name="archivo_totalmente_ajeno.xlsx",
            sheet_name="HojaRara",
            headers=["X1", "Y2", "Z3"],
            sample_rows=[["a", "b", "c"]],
        )
    )

    assert result.extracted_file_name == "archivo_totalmente_ajeno.xlsx"
    assert result.adapter_input["sheets"][0]["sheet_name"] == "HojaRara"
    assert len(result.column_confirmation_result.matrix.entries) == 3
    assert all(entry.suggested_semantic_role == "unknown" for entry in result.column_confirmation_result.matrix.entries)
    assert all(entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION for entry in result.column_confirmation_result.matrix.entries)


def test_chain_preserves_sample_rows_when_present_in_fixture_structure() -> None:
    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=_build_extracted_structure(
            file_name="muestras.xlsx",
            sheet_name="Datos",
            headers=["fecha", "importe"],
            sample_rows=[
                ["2026-01-01", 100],
                ["2026-01-02", 200],
            ],
        )
    )

    entries = result.column_confirmation_result.matrix.entries
    assert entries[0].sample_values == ["2026-01-01", "2026-01-02"]
    assert entries[1].sample_values == [100, 200]


def test_chain_with_empty_headers_stays_safe() -> None:
    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=_build_extracted_structure(
            file_name="sin_headers.xlsx",
            sheet_name="Datos",
            headers=[],
        )
    )

    assert result.column_confirmation_result.matrix.entries == []
    assert result.column_confirmation_result.owner_prompt_batch.has_prompts is False
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False


def test_chain_rejects_invalid_structure_shapes() -> None:
    with pytest.raises(ValueError, match="workbook"):
        build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
            extracted_structure={"source_path_basename": "a.xlsx"},
        )
