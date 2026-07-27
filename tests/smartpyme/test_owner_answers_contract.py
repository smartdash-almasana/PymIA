from __future__ import annotations

import pytest


def test_owner_answer_contract_accepts_explicit_answer() -> None:
    from pymia.contracts.owner_answers import OwnerAnswer

    answer = OwnerAnswer(
        answer_id="a-1",
        question_id="q-1",
        question_text="¿Qué período cubre esta planilla?",
        answer_text="Corresponde a enero de 2026.",
        answer_type="period",
        capture_status="provided",
        source_ref="owner_reply://message/1",
        metadata={"channel": "replay"},
    )

    assert answer.answer_id == "a-1"
    assert answer.question_id == "q-1"
    assert answer.answer_type == "period"
    assert answer.capture_status == "provided"


def test_owner_answer_contract_serializes_stably() -> None:
    from pymia.contracts.owner_answers import OwnerAnswer

    payload = OwnerAnswer(
        answer_id="a-2",
        question_id="q-2",
        question_text="¿Podés adjuntar el comprobante de impuestos?",
        answer_text=None,
        structured_answer={"document_ref": "files://taxes.pdf"},
        answer_type="document",
        capture_status="provided",
        source_ref="owner_reply://attachment/1",
    ).model_dump(mode="json")

    assert payload["answer_id"] == "a-2"
    assert payload["question_id"] == "q-2"
    assert payload["answer_type"] == "document"
    assert payload["structured_answer"]["document_ref"] == "files://taxes.pdf"


def test_owner_answers_bundle_contract_supports_list_of_answers() -> None:
    from pymia.contracts.owner_answers import OwnerAnswer, OwnerAnswersBundle

    bundle = OwnerAnswersBundle(
        bundle_id="answers-1",
        answers=[
            OwnerAnswer(
                answer_id="a-1",
                question_id="q-1",
                question_text="¿Qué período cubre esta planilla?",
                answer_text="Enero 2026.",
                answer_type="period",
                capture_status="provided",
                source_ref="owner_reply://message/1",
            ),
            OwnerAnswer(
                answer_id="a-2",
                question_id="q-2",
                question_text="¿Podés subir el extracto bancario faltante?",
                answer_text="Todavía no lo tengo.",
                answer_type="text",
                capture_status="declined",
                source_ref="owner_reply://message/2",
            ),
        ],
        metadata={"tenant_id": "tenant-1"},
    )

    assert bundle.bundle_id == "answers-1"
    assert len(bundle.answers) == 2
    assert bundle.answers[1].capture_status == "declined"
    assert bundle.metadata["tenant_id"] == "tenant-1"


def test_owner_answer_contract_normalizes_blank_answer_text_to_none() -> None:
    from pymia.contracts.owner_answers import OwnerAnswer

    answer = OwnerAnswer(
        answer_id="a-3",
        question_id="q-3",
        question_text="¿Qué significa la columna ajuste?",
        answer_text="   ",
        structured_answer={"clarification": "ajuste manual"},
        answer_type="text",
        capture_status="provided",
        source_ref="owner_reply://message/3",
    )

    assert answer.answer_text is None


@pytest.mark.parametrize(
    ("field_name", "payload"),
    [
        (
            "question_id",
            {
                "answer_id": "a-invalid-1",
                "question_id": "   ",
                "question_text": "¿Qué período cubre esta planilla?",
                "answer_text": "Enero 2026.",
                "answer_type": "period",
                "capture_status": "provided",
                "source_ref": "owner_reply://message/4",
            },
        ),
        (
            "source_ref",
            {
                "answer_id": "a-invalid-2",
                "question_id": "q-2",
                "question_text": "¿Podés adjuntar el comprobante de impuestos?",
                "answer_text": "Sí, lo adjunto.",
                "answer_type": "document",
                "capture_status": "provided",
                "source_ref": "   ",
            },
        ),
    ],
)
def test_owner_answer_contract_rejects_missing_required_text_fields(
    field_name: str,
    payload: dict,
) -> None:
    from pymia.contracts.owner_answers import OwnerAnswer

    with pytest.raises(ValueError) as exc:
        OwnerAnswer(**payload)

    assert field_name
    assert "non-empty" in str(exc.value)


def test_owner_answer_contract_rejects_provided_answer_without_content() -> None:
    from pymia.contracts.owner_answers import OwnerAnswer

    with pytest.raises(ValueError) as exc:
        OwnerAnswer(
            answer_id="a-invalid-3",
            question_id="q-3",
            question_text="¿Qué período cubre esta planilla?",
            answer_text="   ",
            structured_answer={},
            answer_type="period",
            capture_status="provided",
            source_ref="owner_reply://message/5",
        )

    assert "provided answer must include" in str(exc.value)
