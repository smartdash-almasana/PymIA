from __future__ import annotations

import json

import pytest

from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    Service1ColumnConfirmationOwnerPromptBatchV1,
)
from pymia.smartpyme.service_1_owner_prompt_batch_display_model_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    build_service_1_owner_prompt_batch_display_model_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_extraction_to_adapter_chain_v1 import (
    build_service_1_xlsx_structure_extraction_to_adapter_chain_v1,
)


def _build_owner_prompt_batch() -> Service1ColumnConfirmationOwnerPromptBatchV1:
    chain = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure={
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "source_path_basename": "cafeteria_abc.xlsx",
            "workbook": {
                "sheet_count": 1,
                "sheets": [
                    {
                        "name": "OPERACION",
                        "max_row": 5,
                        "max_column": 3,
                        "headers": ["fecha", "cliente", "margen"],
                        "empty_header_count": 0,
                        "sample_rows_count": 4,
                        "sample_rows": [
                            ["2026-01-01", "Cliente A", 1200],
                            ["2026-01-02", "Cliente B", 900],
                        ],
                    }
                ],
            },
            "warnings": [],
            "runtime_authorized": False,
        }
    )
    return chain.column_confirmation_result.owner_prompt_batch


def test_builds_serializable_owner_facing_display_packet() -> None:
    owner_prompt_batch = _build_owner_prompt_batch()

    display = build_service_1_owner_prompt_batch_display_model_v1(
        owner_prompt_batch=owner_prompt_batch,
    )

    assert display.schema_version == SCHEMA_VERSION
    assert display.service_name == SERVICE_NAME
    assert display.file_name == "cafeteria_abc.xlsx"
    assert display.total_questions == 3
    assert display.has_questions is True
    assert len(display.questions) == 3
    assert display.questions[0].file_name == "cafeteria_abc.xlsx"
    assert display.questions[0].sheet_name == "OPERACION"
    assert display.questions[0].column_name == "fecha"
    assert "Dueño, revisé tu Excel" in display.questions[0].prompt_text
    assert display.questions[0].allowed_owner_responses == ("SÍ", "NO", "TU_RESPUESTA")
    assert display.runtime_authorized is False
    assert display.tool_execution_authorized is False
    assert display.delivery_authorized is False
    assert display.diagnosis_generated is False


def test_serialized_display_packet_does_not_expose_internal_terms() -> None:
    owner_prompt_batch = _build_owner_prompt_batch()

    display = build_service_1_owner_prompt_batch_display_model_v1(
        owner_prompt_batch=owner_prompt_batch,
    )

    rendered = json.dumps(display.to_dict(), ensure_ascii=False)
    assert "venta_total" not in rendered
    assert "computed_variables" not in rendered
    assert "margen_bruto" not in rendered
    assert "suggested_semantic_role" not in rendered
    assert "owner_rectified_function" not in rendered
    assert "calculation_relevance" not in rendered


def test_empty_batch_returns_safe_display_packet_without_questions() -> None:
    owner_prompt_batch = _build_owner_prompt_batch()
    empty_batch = Service1ColumnConfirmationOwnerPromptBatchV1(
        schema_version=owner_prompt_batch.schema_version,
        service_name=owner_prompt_batch.service_name,
        file_name=owner_prompt_batch.file_name,
        matrix_status=owner_prompt_batch.matrix_status,
        total_entries=0,
        actionable_entries_count=0,
        prompts=(),
        has_prompts=False,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        persistence_authorized=False,
        created_at=owner_prompt_batch.created_at,
        metadata={"case_id": "case-empty"},
    )

    display = build_service_1_owner_prompt_batch_display_model_v1(
        owner_prompt_batch=empty_batch,
    )

    assert display.total_questions == 0
    assert display.has_questions is False
    assert display.questions == ()
    assert display.runtime_authorized is False
    assert display.tool_execution_authorized is False
    assert display.delivery_authorized is False
    assert display.diagnosis_generated is False


def test_rejects_invalid_input_type() -> None:
    with pytest.raises(ValueError, match="owner_prompt_batch"):
        build_service_1_owner_prompt_batch_display_model_v1(
            owner_prompt_batch="bad",  # type: ignore[arg-type]
        )


def test_rejects_invalid_metadata_type() -> None:
    owner_prompt_batch = _build_owner_prompt_batch()

    with pytest.raises(ValueError, match="metadata"):
        build_service_1_owner_prompt_batch_display_model_v1(
            owner_prompt_batch=owner_prompt_batch,
            metadata="bad",  # type: ignore[arg-type]
        )
