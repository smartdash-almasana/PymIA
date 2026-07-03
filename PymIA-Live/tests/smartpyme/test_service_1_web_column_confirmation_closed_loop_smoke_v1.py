from __future__ import annotations

import json

import pytest

from pymia.smartpyme.service_1_web_column_confirmation_closed_loop_smoke_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_AWAITING_OWNER,
    STATUS_BLOCKED_INVALID_OWNER_ANSWER,
    STATUS_NEEDS_OWNER_FOLLOWUP,
    STATUS_OWNER_RESPONSES_CAPTURED,
    build_service_1_web_column_confirmation_closed_loop_smoke_v1,
)


def _extracted_structure() -> dict[str, object]:
    return {
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


def _all_yes_answers() -> list[dict[str, str]]:
    return [
        {"sheet_name": "OPERACION", "column_name": "fecha", "owner_response": "SÍ"},
        {"sheet_name": "OPERACION", "column_name": "cliente", "owner_response": "SÍ"},
        {"sheet_name": "OPERACION", "column_name": "margen", "owner_response": "SÍ"},
    ]


def test_closed_loop_without_answers_returns_owner_display_and_awaiting_owner() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_AWAITING_OWNER
    assert result.file_name == "cafeteria_abc.xlsx"
    assert result.display_model.total_questions == 3
    assert result.display_model.has_questions is True
    assert result.answer_results == ()
    assert result.summary.total_questions == 3
    assert result.summary.total_answers == 0
    assert result.summary.pending_answer_count == 3
    assert result.summary.ready_for_semantic_normalization is False
    assert result.summary.ready_for_matrix_application is False
    assert result.summary.ready_for_evidence_profile is False
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    assert result.evidence_profile_generated is False
    assert result.matrix_application_authorized is False


def test_closed_loop_with_all_yes_answers_captures_answers_but_still_does_not_unlock_runtime() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
        owner_answers=_all_yes_answers(),
    )

    assert result.status == STATUS_OWNER_RESPONSES_CAPTURED
    assert len(result.answer_results) == 3
    assert result.summary.total_questions == 3
    assert result.summary.total_answers == 3
    assert result.summary.accepted_unknown_count == 3
    assert result.summary.rejected_count == 0
    assert result.summary.needs_normalization_count == 0
    assert result.summary.pending_answer_count == 0
    assert result.summary.ready_for_matrix_application is False
    assert result.summary.ready_for_evidence_profile is False
    assert all(answer_result.answer.confirmed_role is None for answer_result in result.answer_results)
    assert all(answer_result.answer.unlocks_computation() is False for answer_result in result.answer_results)
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False


def test_closed_loop_with_owner_free_text_routes_to_followup_without_normalizing_semantics() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
        owner_answers=[
            {"sheet_name": "OPERACION", "column_name": "fecha", "owner_response": "SÍ"},
            {"sheet_name": "OPERACION", "column_name": "cliente", "owner_response": "SÍ"},
            {
                "sheet_name": "OPERACION",
                "column_name": "margen",
                "owner_response": "TU_RESPUESTA",
                "owner_free_text": "Es una observación interna, no margen.",
            },
        ],
    )

    assert result.status == STATUS_NEEDS_OWNER_FOLLOWUP
    assert result.summary.total_answers == 3
    assert result.summary.accepted_unknown_count == 2
    assert result.summary.needs_normalization_count == 1
    assert result.summary.insufficient_count == 1
    assert result.summary.pending_answer_count == 0
    assert result.summary.ready_for_semantic_normalization is True
    assert result.summary.ready_for_matrix_application is False
    assert result.summary.ready_for_evidence_profile is False
    free_text_answer = result.answer_results[2].answer
    assert free_text_answer.confirmed_role is None
    assert free_text_answer.unblocks_variable_names == []
    assert free_text_answer.unlocks_computation() is False


def test_closed_loop_with_rejection_routes_to_followup_without_evidence_profile() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
        owner_answers=[
            {"sheet_name": "OPERACION", "column_name": "fecha", "owner_response": "SÍ"},
            {"sheet_name": "OPERACION", "column_name": "cliente", "owner_response": "NO"},
            {"sheet_name": "OPERACION", "column_name": "margen", "owner_response": "SÍ"},
        ],
    )

    assert result.status == STATUS_NEEDS_OWNER_FOLLOWUP
    assert result.summary.accepted_unknown_count == 2
    assert result.summary.rejected_count == 1
    assert result.summary.pending_answer_count == 0
    assert result.evidence_profile_generated is False
    assert result.matrix_application_authorized is False


def test_closed_loop_with_conflicting_answer_blocks_invalid_owner_answer() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
        owner_answers=[
            {
                "sheet_name": "OPERACION",
                "column_name": "fecha",
                "owner_response": "SÍ",
                "owner_free_text": "Pero no es fecha.",
            },
        ],
    )

    assert result.status == STATUS_BLOCKED_INVALID_OWNER_ANSWER
    assert result.summary.conflicting_count == 1
    assert result.summary.pending_answer_count == 2
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False


def test_closed_loop_serialization_is_safe_for_web_smoke() -> None:
    result = build_service_1_web_column_confirmation_closed_loop_smoke_v1(
        extracted_structure=_extracted_structure(),
        owner_answers=_all_yes_answers(),
    )

    rendered = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "cafeteria_abc.xlsx" in rendered
    assert "Dueño, revisé tu Excel" in rendered
    assert "venta_total" not in rendered
    assert "computed_variables" not in rendered
    assert "margen_bruto" not in rendered
    assert "owner_rectified_function" not in rendered
    assert "suggested_semantic_role" not in rendered
    assert result.diagnosis_generated is False
    assert result.evidence_profile_generated is False
    assert result.matrix_application_authorized is False


def test_closed_loop_rejects_bad_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="extracted_structure"):
        build_service_1_web_column_confirmation_closed_loop_smoke_v1(
            extracted_structure="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="owner_answers"):
        build_service_1_web_column_confirmation_closed_loop_smoke_v1(
            extracted_structure=_extracted_structure(),
            owner_answers="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="each owner answer"):
        build_service_1_web_column_confirmation_closed_loop_smoke_v1(
            extracted_structure=_extracted_structure(),
            owner_answers=["bad"],  # type: ignore[list-item]
        )

    with pytest.raises(ValueError, match="display question not found"):
        build_service_1_web_column_confirmation_closed_loop_smoke_v1(
            extracted_structure=_extracted_structure(),
            owner_answers=[{"sheet_name": "OTRA", "column_name": "fecha", "owner_response": "SÍ"}],
        )
