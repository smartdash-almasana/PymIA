from __future__ import annotations

import json

import pytest

from pymia.contracts.column_confirmation_v1 import OwnerColumnConfirmationAnswer, OwnerColumnConfirmationOutcome
from pymia.smartpyme.service_1_owner_column_confirmation_answer_intake_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_ANSWER_CAPTURED,
    STATUS_ANSWER_REJECTED,
    UNKNOWN_PROPOSED_ROLE,
    build_service_1_owner_column_confirmation_answer_intake_v1,
)
from pymia.smartpyme.service_1_owner_prompt_batch_display_model_v1 import (
    Service1OwnerPromptBatchDisplayModelV1,
    build_service_1_owner_prompt_batch_display_model_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_extraction_to_adapter_chain_v1 import (
    build_service_1_xlsx_structure_extraction_to_adapter_chain_v1,
)


def _build_display_model() -> Service1OwnerPromptBatchDisplayModelV1:
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
    return build_service_1_owner_prompt_batch_display_model_v1(
        owner_prompt_batch=chain.column_confirmation_result.owner_prompt_batch,
    )


def test_si_answer_is_captured_without_operational_rectification() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="fecha",
        owner_response="SÍ",
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_ANSWER_CAPTURED
    assert result.file_name == "cafeteria_abc.xlsx"
    assert result.sheet_name == "OPERACION"
    assert result.column_name == "fecha"
    assert isinstance(result.answer, OwnerColumnConfirmationAnswer)
    assert result.answer.sheet_name == "OPERACION"
    assert result.answer.column_name == "fecha"
    assert result.answer.owner_answer_text == "SÍ"
    assert result.answer.proposed_role == UNKNOWN_PROPOSED_ROLE
    assert result.answer.confirmed_role is None
    assert result.answer.outcome == OwnerColumnConfirmationOutcome.OWNER_UNKNOWN
    assert result.answer.unblocks_variable_names == []
    assert result.answer.unlocks_computation() is False
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.evidence_profile_generated is False
    assert result.owner_rectification_created is False


def test_no_answer_rejects_displayed_interpretation_without_unlocking_computation() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="cliente",
        owner_response="NO",
    )

    assert result.status == STATUS_ANSWER_CAPTURED
    assert result.answer.owner_answer_text == "NO"
    assert result.answer.outcome == OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING
    assert result.answer.confirmed_role is None
    assert result.answer.proposed_role == UNKNOWN_PROPOSED_ROLE
    assert result.answer.unlocks_computation() is False
    assert result.owner_rectification_created is False
    assert result.evidence_profile_generated is False


def test_tu_respuesta_with_free_text_is_captured_but_requires_later_normalization() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="margen",
        owner_response="TU_RESPUESTA",
        owner_free_text="Esta columna es una observación interna, no margen.",
    )

    assert result.status == STATUS_ANSWER_REJECTED
    assert result.answer.owner_answer_text == "TU_RESPUESTA: Esta columna es una observación interna, no margen."
    assert result.answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
    assert result.answer.confirmed_role is None
    assert result.answer.unblocks_variable_names == []
    assert result.answer.unlocks_computation() is False
    assert result.owner_rectification_created is False
    assert result.evidence_profile_generated is False


def test_tu_respuesta_without_free_text_is_rejected_fail_closed() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="margen",
        owner_response="TU_RESPUESTA",
    )

    assert result.status == STATUS_ANSWER_REJECTED
    assert result.answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
    assert result.answer.confirmed_role is None
    assert result.answer.unlocks_computation() is False


def test_conflicting_answer_is_rejected_fail_closed() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="fecha",
        owner_response="SÍ",
        owner_free_text="En realidad es otra cosa.",
    )

    assert result.status == STATUS_ANSWER_REJECTED
    assert result.answer.outcome == OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER
    assert result.answer.confirmed_role is None
    assert result.answer.unlocks_computation() is False
    assert result.owner_rectification_created is False


def test_serialized_intake_result_does_not_expose_or_create_internal_evidence_terms() -> None:
    display_model = _build_display_model()

    result = build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name="OPERACION",
        column_name="fecha",
        owner_response="SÍ",
    )

    rendered = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "venta_total" not in rendered
    assert "computed_variables" not in rendered
    assert "margen_bruto" not in rendered
    assert "owner_rectified_function" not in rendered
    assert "suggested_semantic_role" not in rendered
    assert "EvidenceProfile" not in rendered
    assert result.diagnosis_generated is False


def test_rejects_unknown_display_question() -> None:
    display_model = _build_display_model()

    with pytest.raises(ValueError, match="display question not found"):
        build_service_1_owner_column_confirmation_answer_intake_v1(
            display_model=display_model,
            sheet_name="OTRA",
            column_name="fecha",
            owner_response="SÍ",
        )


def test_rejects_invalid_input_types_and_invalid_response() -> None:
    display_model = _build_display_model()

    with pytest.raises(ValueError, match="display_model"):
        build_service_1_owner_column_confirmation_answer_intake_v1(
            display_model="bad",  # type: ignore[arg-type]
            sheet_name="OPERACION",
            column_name="fecha",
            owner_response="SÍ",
        )

    with pytest.raises(ValueError, match="metadata"):
        build_service_1_owner_column_confirmation_answer_intake_v1(
            display_model=display_model,
            sheet_name="OPERACION",
            column_name="fecha",
            owner_response="SÍ",
            metadata="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="owner_response"):
        build_service_1_owner_column_confirmation_answer_intake_v1(
            display_model=display_model,
            sheet_name="OPERACION",
            column_name="fecha",
            owner_response="QUIZAS",
        )
