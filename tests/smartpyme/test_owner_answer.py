from __future__ import annotations

import pytest

from pymia.smartpyme.owner_answer import (
    ANSWER_KIND_CLARIFICATION,
    ANSWER_KIND_PENDING_QUESTION,
    create_owner_answer_record,
)


def test_create_owner_answer_record_defaults_to_pending_question() -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="missing_input:ventas",
        raw_owner_answer="Las ventas están en la hoja Ventas.",
    )

    payload = record.to_dict()

    assert record.answer_id.startswith("answer_")
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["anamnesis_id"] == "anamnesis_demo"
    assert payload["investigation_id"] == "investigation_demo"
    assert payload["question_ref"] == "missing_input:ventas"
    assert payload["raw_owner_answer"] == "Las ventas están en la hoja Ventas."
    assert payload["answer_kind"] == ANSWER_KIND_PENDING_QUESTION
    assert payload["metadata"] == {}


def test_create_owner_answer_record_accepts_kind_and_metadata() -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="owner_question:001",
        raw_owner_answer="Aclaro que el canal principal es mayorista.",
        answer_kind=ANSWER_KIND_CLARIFICATION,
        metadata={"source": "owner_chat"},
    )

    payload = record.to_dict()

    assert payload["answer_kind"] == ANSWER_KIND_CLARIFICATION
    assert payload["metadata"] == {"source": "owner_chat"}


def test_create_owner_answer_record_rejects_empty_tenant_id() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        create_owner_answer_record(
            tenant_id="",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
        )


def test_create_owner_answer_record_rejects_empty_intake_id() -> None:
    with pytest.raises(ValueError, match="intake_id"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
        )


def test_create_owner_answer_record_rejects_empty_anamnesis_id() -> None:
    with pytest.raises(ValueError, match="anamnesis_id"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
        )


def test_create_owner_answer_record_rejects_empty_investigation_id() -> None:
    with pytest.raises(ValueError, match="investigation_id"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
        )


def test_create_owner_answer_record_rejects_empty_question_ref() -> None:
    with pytest.raises(ValueError, match="question_ref"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="",
            raw_owner_answer="Respuesta.",
        )


def test_create_owner_answer_record_rejects_empty_raw_owner_answer() -> None:
    with pytest.raises(ValueError, match="raw_owner_answer"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="",
        )


def test_create_owner_answer_record_rejects_invalid_answer_kind() -> None:
    with pytest.raises(ValueError, match="answer_kind"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
            answer_kind="INVALID",
        )


def test_create_owner_answer_record_rejects_non_dict_metadata() -> None:
    with pytest.raises(ValueError, match="metadata"):
        create_owner_answer_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            anamnesis_id="anamnesis_demo",
            investigation_id="investigation_demo",
            question_ref="q1",
            raw_owner_answer="Respuesta.",
            metadata="owner_chat",  # type: ignore[arg-type]
        )
