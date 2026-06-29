from __future__ import annotations

from pymia.smartpyme.service_1_owner_reentry_closed_loop_v1 import (
    STATUS_PARTIAL_OWNER_ANSWERS,
    STATUS_READY_FOR_OPERATOR_RERUN,
    build_service_1_question_bundle_from_column_confirmation_packet_v1,
    run_service_1_owner_reentry_minimal_closed_loop_v1,
)


def _packet() -> dict:
    return {
        "asset": {"asset_id": "asset_1", "filename": "ventas.xlsx"},
        "file_intake": {"file_intake_id": "intake_1"},
        "case_delivery_manifest": {"case_id": "case_asset_1"},
        "column_confirmation_packet": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "packet_type": "COLUMN_CONFIRMATION",
            "runtime_authorized": False,
            "status": "NEEDS_OWNER_CONFIRMATION",
            "questions": [
                {
                    "question_id": "col_confirm_001",
                    "sheet_name": "Ventas",
                    "column_name": "MetodoPago",
                    "question": "Que representa MetodoPago?",
                    "answer_type": "owner_text",
                    "required": True,
                },
                {
                    "question_id": "col_confirm_002",
                    "sheet_name": "Ventas",
                    "column_name": "Importe",
                    "question": "Que representa Importe?",
                    "answer_type": "owner_text",
                    "required": True,
                },
            ],
        },
        "runtime_authorized": False,
    }


def test_builds_question_bundle_from_cli_column_confirmation_packet() -> None:
    bundle, mapping = build_service_1_question_bundle_from_column_confirmation_packet_v1(packet=_packet())

    assert bundle.case_id == "case_asset_1"
    assert bundle.tenant_id == "local_operator"
    assert bundle.intake_id == "intake_1"
    assert len(bundle.questions) == 2
    assert set(mapping) == {"col_confirm_001", "col_confirm_002"}
    assert bundle.runtime_authorized is False
    assert bundle.human_review_required is True


def test_closed_loop_projects_partial_owner_answers(tmp_path) -> None:
    result = run_service_1_owner_reentry_minimal_closed_loop_v1(
        packet=_packet(),
        owner_answers={"answers": {"col_confirm_001": "Forma de pago."}},
        storage_dir=tmp_path,
    )

    assert result.status == STATUS_PARTIAL_OWNER_ANSWERS
    assert result.question_count == 2
    assert result.answered_count == 1
    assert result.pending_count == 1
    assert result.persisted_answer_count == 1
    assert result.operator_rerun_required is False
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.confirmed_columns_patch["status"] == "DECLARED_NOT_VALIDATED"
    assert result.confirmed_columns_patch["columns"][0]["question_id"] == "col_confirm_001"


def test_closed_loop_ready_for_operator_rerun_when_all_answers_present(tmp_path) -> None:
    result = run_service_1_owner_reentry_minimal_closed_loop_v1(
        packet=_packet(),
        owner_answers={
            "answers": {
                "col_confirm_001": "Forma de pago.",
                "col_confirm_002": "Importe vendido.",
            }
        },
        storage_dir=tmp_path,
    )

    assert result.status == STATUS_READY_FOR_OPERATOR_RERUN
    assert result.answered_count == 2
    assert result.pending_count == 0
    assert result.persisted_answer_count == 2
    assert result.operator_rerun_required is True
    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.metadata["does_not_reopen_full_assisted_v1_closure"] is True
