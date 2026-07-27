from __future__ import annotations

import pytest


def test_owner_question_contract_accepts_explicit_question() -> None:
    from pymia.contracts.owner_questions import OwnerQuestion

    question = OwnerQuestion(
        question_id="q-1",
        question_text="¿Qué período cubre esta planilla?",
        reason="next_question",
        missing_key="periodo",
        source_ref="render_contract://next_questions/0",
        expected_answer_type="period",
        required=True,
        metadata={"origin": "render_contract"},
    )

    assert question.question_id == "q-1"
    assert question.missing_key == "periodo"
    assert question.expected_answer_type == "period"
    assert question.required is True


def test_owner_question_contract_serializes_stably() -> None:
    from pymia.contracts.owner_questions import OwnerQuestion

    payload = OwnerQuestion(
        question_id="q-2",
        question_text="¿Podés subir el extracto bancario faltante?",
        reason="missing_evidence",
        missing_key="extracto_bancario",
        source_ref="operational_audit_result://missing_evidence/0",
        expected_answer_type="document",
        required=True,
    ).model_dump(mode="json")

    assert payload["question_id"] == "q-2"
    assert payload["reason"] == "missing_evidence"
    assert payload["source_ref"] == "operational_audit_result://missing_evidence/0"
    assert payload["expected_answer_type"] == "document"


def test_owner_questions_bundle_contract_supports_list_of_questions() -> None:
    from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle

    bundle = OwnerQuestionsBundle(
        bundle_id="bundle-1",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Qué período cubre esta planilla?",
                reason="next_question",
                missing_key="periodo",
                source_ref="render_contract://next_questions/0",
                expected_answer_type="period",
            ),
            OwnerQuestion(
                question_id="q-2",
                question_text="El caso está bloqueado: ¿podés aclarar qué significa la columna saldo?",
                reason="blocked_message",
                missing_key=None,
                source_ref="render_contract://blocked_message",
                expected_answer_type="text",
                required=False,
            ),
        ],
        metadata={"tenant_id": "tenant-1"},
    )

    assert bundle.bundle_id == "bundle-1"
    assert len(bundle.questions) == 2
    assert bundle.questions[1].missing_key is None
    assert bundle.metadata["tenant_id"] == "tenant-1"


def test_owner_question_contract_preserves_missing_key_none() -> None:
    from pymia.contracts.owner_questions import OwnerQuestion

    question = OwnerQuestion(
        question_id="q-3",
        question_text="¿Qué significa la columna ajuste?",
        reason="blocked_message",
        missing_key=None,
        source_ref="render_contract://blocked_message",
        expected_answer_type="text",
    )

    assert question.missing_key is None


@pytest.mark.parametrize(
    ("field_name", "payload"),
    [
        (
            "question_text",
            {
                "question_id": "q-invalid-1",
                "question_text": "   ",
                "reason": "next_question",
                "missing_key": "periodo",
                "source_ref": "render_contract://next_questions/0",
                "expected_answer_type": "text",
            },
        ),
        (
            "source_ref",
            {
                "question_id": "q-invalid-2",
                "question_text": "¿Qué período cubre esta planilla?",
                "reason": "next_question",
                "missing_key": "periodo",
                "source_ref": "   ",
                "expected_answer_type": "text",
            },
        ),
    ],
)
def test_owner_question_contract_rejects_missing_required_text_fields(
    field_name: str,
    payload: dict,
) -> None:
    from pymia.contracts.owner_questions import OwnerQuestion

    with pytest.raises(ValueError) as exc:
        OwnerQuestion(**payload)

    assert "non-empty" in str(exc.value)
