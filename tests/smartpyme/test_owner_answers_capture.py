from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle


def _build_questions_bundle() -> OwnerQuestionsBundle:
    return OwnerQuestionsBundle(
        bundle_id="questions-bundle",
        questions=[
            OwnerQuestion(
                question_id="q-1",
                question_text="¿Qué período cubre esta planilla?",
                reason="next_question",
                source_ref="render_contract://next_questions/0",
                expected_answer_type="period",
            ),
            OwnerQuestion(
                question_id="q-2",
                question_text="¿Podés adjuntar el respaldo?",
                reason="missing_evidence",
                source_ref="operational_audit_result://missing_evidence/0",
                expected_answer_type="document",
            ),
        ],
    )


def test_capture_owner_answers_from_structured_payload_captures_answer_text() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[{"question_id": "q-1", "answer_text": "Enero 2026"}],
        source_ref="operator_assisted_capture",
    )

    assert bundle.answers[0].answer_text == "Enero 2026"
    assert bundle.answers[0].question_text == "¿Qué período cubre esta planilla?"


def test_capture_owner_answers_from_structured_payload_captures_structured_answer_without_text() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[
            {"question_id": "q-2", "structured_answer": {"document_ref": "files://backup.pdf"}}
        ],
        source_ref="operator_assisted_capture",
    )

    assert bundle.answers[0].answer_text is None
    assert bundle.answers[0].structured_answer["document_ref"] == "files://backup.pdf"


def test_capture_owner_answers_from_structured_payload_uses_contractual_question_text() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[
            {
                "question_id": "q-1",
                "question_text": "¿Qué período cubre esta planilla?",
                "answer_text": "Enero 2026",
            }
        ],
        source_ref="operator_assisted_capture",
    )

    assert bundle.answers[0].question_text == "¿Qué período cubre esta planilla?"


def test_capture_owner_answers_from_structured_payload_fails_on_different_question_text() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[
                {
                    "question_id": "q-1",
                    "question_text": "Pregunta inventada",
                    "answer_text": "Enero 2026",
                }
            ],
            source_ref="operator_assisted_capture",
        )

    assert "payload question_text does not match" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_fails_if_question_id_missing() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"answer_text": "Enero 2026"}],
            source_ref="operator_assisted_capture",
        )

    assert "question_id is required" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_fails_if_question_id_unknown() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"question_id": "q-missing", "answer_text": "Enero 2026"}],
            source_ref="operator_assisted_capture",
        )

    assert "unknown question_id" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_fails_if_content_missing() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"question_id": "q-1"}],
            source_ref="operator_assisted_capture",
        )

    assert "answer_text or structured_answer is required" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_fails_if_source_ref_empty() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"question_id": "q-1", "answer_text": "Enero 2026"}],
            source_ref="   ",
        )

    assert "source_ref must be non-empty" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_uses_expected_answer_type_when_missing() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[{"question_id": "q-1", "answer_text": "Enero 2026"}],
        source_ref="operator_assisted_capture",
    )

    assert bundle.answers[0].answer_type == "period"


def test_capture_owner_answers_from_structured_payload_accepts_valid_payload_answer_type() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[{"question_id": "q-1", "answer_text": "30", "answer_type": "number"}],
        source_ref="operator_assisted_capture",
    )

    assert bundle.answers[0].answer_type == "number"


def test_capture_owner_answers_from_structured_payload_rejects_invalid_answer_type() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    with pytest.raises(ValueError) as exc:
        capture_owner_answers_from_structured_payload(
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"question_id": "q-1", "answer_text": "30", "answer_type": "invalid"}],
            source_ref="operator_assisted_capture",
        )

    assert "invalid answer_type" in str(exc.value)


def test_capture_owner_answers_from_structured_payload_generates_deterministic_ids_and_metadata() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[{"question_id": "q-1", "answer_text": "Enero 2026"}],
        source_ref="operator_assisted_capture",
        tenant_id="tenant-1",
    )

    assert bundle.bundle_id == "questions-bundle:answers"
    assert bundle.answers[0].answer_id == "questions-bundle:answer:0:q-1"
    assert bundle.metadata["source_questions_bundle_id"] == "questions-bundle"
    assert bundle.metadata["tenant_id"] == "tenant-1"
    assert bundle.metadata["capture_mode"] == "structured_payload"


def test_capture_owner_answers_from_structured_payload_does_not_mutate_inputs() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    questions_bundle = _build_questions_bundle()
    answers_payload = [
        {
            "question_id": "q-1",
            "answer_text": "Enero 2026",
            "metadata": {"origin": "operator"},
            "source_ref": "payload_source",
        }
    ]
    questions_before = questions_bundle.model_dump(mode="json")
    payload_before = deepcopy(answers_payload)

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref="param_source",
    )

    assert questions_bundle.model_dump(mode="json") == questions_before
    assert answers_payload == payload_before
    assert bundle.answers[0].source_ref == "param_source"


def test_capture_owner_answers_from_structured_payload_preserves_semantic_confirmation_metadata() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[
            {
                "question_id": "q-1",
                "answer_text": "Sí, revisemos margen y precios primero.",
                "metadata": {
                    "semantic_confirmation_status": "CONFIRMED_BY_OWNER",
                    "proposed_interpretation": "revisar margen/precios por suba de insumos",
                    "related_missing_keys": ["own_price", "average_stock", "dso"],
                },
            }
        ],
        source_ref="operator_assisted_capture",
    )

    answer_metadata = bundle.answers[0].metadata
    assert answer_metadata["semantic_confirmation_status"] == "CONFIRMED_BY_OWNER"
    assert (
        answer_metadata["proposed_interpretation"]
        == "revisar margen/precios por suba de insumos"
    )
    assert answer_metadata["related_missing_keys"] == ["own_price", "average_stock", "dso"]


def test_capture_owner_answers_from_structured_payload_keeps_semantic_confirmation_as_metadata_only() -> None:
    from pymia.smartpyme.owner_answers_capture import (
        capture_owner_answers_from_structured_payload,
    )

    bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=_build_questions_bundle(),
        answers_payload=[
            {
                "question_id": "q-1",
                "answer_text": "Sí, confirmo esa lectura.",
                "metadata": {
                    "semantic_confirmation_status": "CONFIRMED_BY_OWNER",
                    "proposed_interpretation": "revisar precios propios",
                },
            }
        ],
        source_ref="operator_assisted_capture",
    )

    answer = bundle.answers[0]
    assert answer.structured_answer == {}
    assert "evidence" not in answer.metadata
    assert "evidence_candidate" not in answer.metadata
    assert "computed_variables" not in answer.metadata


def test_owner_answers_capture_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_answers_capture.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "graph",
        "state",
        "conversation_adapter",
        "core_delivery_bridge",
        "owner_action_pipeline",
        "owner_answers_evaluator",
        "owner_facing_report",
        "diagnosticcore",
        "diagnostic_core",
        "telegram",
        "hermes",
        "fastapi",
        "runtime",
        "parser",
        "llm",
        "learningmemory",
    ]

    for token in forbidden_tokens:
        assert f"import {token}" not in lowered
        assert f"from {token} import" not in lowered
