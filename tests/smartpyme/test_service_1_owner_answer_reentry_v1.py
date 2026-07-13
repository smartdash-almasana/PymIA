from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    REENTRY_BLOCK_BUNDLE_SCHEMA_UNSUPPORTED,
    REENTRY_BLOCK_QUESTION_NOT_FOUND,
    REENTRY_BLOCK_QUESTION_NOT_PENDING,
    REENTRY_STATUS_ACCEPTED,
    REENTRY_STATUS_BLOCKED,
    SCHEMA_VERSION,
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    QUESTION_STATUS_ANSWERED,
    QUESTION_STATUS_PENDING,
    build_service_1_question_bundle_v1,
    create_service_1_question_v1,
)


def _bundle():
    return build_service_1_question_bundle_v1(
        case_id="case_1",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_1",
        column_confirmation_matrix={
            "file_name": "ventas.xlsx",
            "entries": [
                {
                    "sheet_name": "Ventas",
                    "original_column_name": "MetodoPago",
                    "owner_question": "La columna MetodoPago indica forma de pago o importe?",
                }
            ],
        },
    )


def test_binds_owner_answer_to_pending_question_ref() -> None:
    bundle = _bundle()
    question_ref = bundle.selected_next_question_ref
    assert question_ref is not None

    packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer="Es forma de pago, no importe.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )

    assert packet.schema_version == SCHEMA_VERSION
    assert packet.status == REENTRY_STATUS_ACCEPTED
    assert packet.blocked_reason is None
    assert packet.owner_answer_record is not None
    assert packet.owner_answer_record.question_ref == question_ref
    assert packet.owner_answer_record.raw_owner_answer == "Es forma de pago, no importe."
    assert packet.owner_answer_record.metadata["case_id"] == "case_1"
    assert packet.owner_answer_record.metadata["source_run_id"] == "run_1"
    assert packet.owner_answer_record.metadata["question_target_ref"] == "file:ventas.xlsx:sheet:Ventas:column:MetodoPago"
    assert packet.owner_answer_record.metadata["owner_answer_validation_status"] == "DECLARED_NOT_VALIDATED"
    assert packet.runtime_authorized is False
    assert packet.owner_confirmation_required is True
    assert packet.reexecution_authorized is False
    assert packet.recalculation_authorized is False


def test_blocks_unknown_question_ref_without_creating_answer_record() -> None:
    packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=_bundle(),
        question_ref="service_1:missing:question",
        raw_owner_answer="Respuesta",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )

    assert packet.status == REENTRY_STATUS_BLOCKED
    assert packet.blocked_reason == REENTRY_BLOCK_QUESTION_NOT_FOUND
    assert packet.owner_answer_record is None
    assert packet.selected_question is None
    assert packet.reexecution_authorized is False


def test_blocks_non_pending_question_ref_without_creating_answer_record() -> None:
    answered_question = create_service_1_question_v1(
        source="owner_question",
        text="Pregunta ya contestada",
        target_ref="owner:answered",
        status=QUESTION_STATUS_ANSWERED,
    )
    bundle = build_service_1_question_bundle_v1(
        case_id="case_2",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_2",
    )
    bundle = type(bundle)(
        schema_version=bundle.schema_version,
        service_name=bundle.service_name,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        run_id=bundle.run_id,
        questions=(answered_question,),
        selected_next_question_ref=None,
        runtime_authorized=bundle.runtime_authorized,
        owner_confirmation_required=bundle.owner_confirmation_required,
        created_at=bundle.created_at,
        metadata=bundle.metadata,
    )

    packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=answered_question.question_ref,
        raw_owner_answer="Respuesta duplicada",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )

    assert packet.status == REENTRY_STATUS_BLOCKED
    assert packet.blocked_reason == REENTRY_BLOCK_QUESTION_NOT_PENDING
    assert packet.selected_question is not None
    assert packet.selected_question.status == QUESTION_STATUS_ANSWERED
    assert packet.owner_answer_record is None


def test_accepts_serialized_question_bundle_dict() -> None:
    bundle = _bundle().to_dict()
    question_ref = bundle["selected_next_question_ref"]

    packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer="Forma de pago.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        metadata={"operator_note": "captured_by_cli"},
    )

    assert packet.status == REENTRY_STATUS_ACCEPTED
    assert packet.owner_answer_record is not None
    assert packet.owner_answer_record.metadata["operator_note"] == "captured_by_cli"


def test_rejects_unsupported_bundle_schema() -> None:
    bundle = _bundle().to_dict()
    bundle["schema_version"] = "UNSUPPORTED"

    with pytest.raises(ValueError, match=REENTRY_BLOCK_BUNDLE_SCHEMA_UNSUPPORTED):
        bind_owner_answer_for_service_1_reentry_v1(
            question_bundle=bundle,
            question_ref="whatever",
            raw_owner_answer="Respuesta",
            anamnesis_id="anamnesis_1",
            investigation_id="investigation_1",
        )


def test_requires_non_empty_owner_answer() -> None:
    bundle = _bundle()
    question_ref = bundle.selected_next_question_ref
    assert question_ref is not None

    with pytest.raises(ValueError, match="raw_owner_answer"):
        bind_owner_answer_for_service_1_reentry_v1(
            question_bundle=bundle,
            question_ref=question_ref,
            raw_owner_answer="  ",
            anamnesis_id="anamnesis_1",
            investigation_id="investigation_1",
        )


def test_packet_serializes_without_authorizing_runtime() -> None:
    bundle = _bundle()
    question_ref = bundle.selected_next_question_ref
    assert question_ref is not None

    packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer="Forma de pago.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )
    data = packet.to_dict()

    assert data["status"] == REENTRY_STATUS_ACCEPTED
    assert data["owner_answer_record"]["question_ref"] == question_ref
    assert data["selected_question"]["status"] == QUESTION_STATUS_PENDING
    assert data["runtime_authorized"] is False
    assert data["reexecution_authorized"] is False
    assert data["recalculation_authorized"] is False
