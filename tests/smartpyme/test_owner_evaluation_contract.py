from __future__ import annotations

from pathlib import Path

import pytest


def test_owner_answer_evaluation_contract_accepts_valid_evaluation() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    evaluation = OwnerAnswerEvaluation(
        evaluation_id="eval-1",
        source_answer_id="a-1",
        linked_question_id="q-1",
        verdict="accepted_as_declared",
        mapped_key="dias_periodo",
        normalized_value=30,
        notes=["Valor declarado por el dueño."],
    )

    assert evaluation.evaluation_id == "eval-1"
    assert evaluation.verdict == "accepted_as_declared"
    assert evaluation.mapped_key == "dias_periodo"
    assert evaluation.normalized_value == 30


def test_owner_answer_evaluation_bundle_contract_accepts_ordered_evaluations() -> None:
    from pymia.contracts.owner_evaluation import (
        OwnerAnswerEvaluation,
        OwnerAnswerEvaluationBundle,
    )

    bundle = OwnerAnswerEvaluationBundle(
        bundle_id="bundle-1",
        source_answers_bundle_id="answers-1",
        evaluations=[
            OwnerAnswerEvaluation(
                evaluation_id="eval-1",
                source_answer_id="a-1",
                linked_question_id="q-1",
                verdict="accepted_as_declared",
            ),
            OwnerAnswerEvaluation(
                evaluation_id="eval-2",
                source_answer_id="a-2",
                linked_question_id="q-2",
                verdict="needs_clarification",
                validation_errors=["No se entiende el período informado."],
            ),
        ],
    )

    assert bundle.source_answers_bundle_id == "answers-1"
    assert [item.evaluation_id for item in bundle.evaluations] == ["eval-1", "eval-2"]


def test_owner_answer_evaluation_contract_serializes_deterministically() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    payload = OwnerAnswerEvaluation(
        evaluation_id="eval-3",
        source_answer_id="a-3",
        linked_question_id="q-3",
        verdict="rejected",
        validation_errors=["Respuesta contradictoria."],
        warnings=["Falta respaldo documental."],
        notes=["No se promueve a evidencia."],
    ).model_dump(mode="json")

    assert list(payload.keys()) == [
        "evaluation_id",
        "source_answer_id",
        "linked_question_id",
        "verdict",
        "mapped_key",
        "normalized_value",
        "validation_errors",
        "warnings",
        "notes",
        "metadata",
    ]
    assert payload["validation_errors"] == ["Respuesta contradictoria."]


def test_owner_answer_evaluation_contract_rejects_invalid_verdict() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    with pytest.raises(ValueError):
        OwnerAnswerEvaluation(
            evaluation_id="eval-4",
            source_answer_id="a-4",
            linked_question_id="q-4",
            verdict="unsupported",
        )


def test_owner_answer_evaluation_contract_allows_needs_clarification_with_errors() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    evaluation = OwnerAnswerEvaluation(
        evaluation_id="eval-5",
        source_answer_id="a-5",
        linked_question_id="q-5",
        verdict="needs_clarification",
        validation_errors=["Respuesta incompleta."],
    )

    assert evaluation.verdict == "needs_clarification"
    assert evaluation.validation_errors == ["Respuesta incompleta."]


def test_owner_answer_evaluation_contract_allows_rejected_with_errors() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    evaluation = OwnerAnswerEvaluation(
        evaluation_id="eval-6",
        source_answer_id="a-6",
        linked_question_id="q-6",
        verdict="rejected",
        validation_errors=["Respuesta incompatible con la pregunta."],
    )

    assert evaluation.verdict == "rejected"
    assert evaluation.validation_errors == ["Respuesta incompatible con la pregunta."]


def test_owner_answer_evaluation_contract_allows_accepted_as_declared_without_evidence_candidate() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    payload = OwnerAnswerEvaluation(
        evaluation_id="eval-7",
        source_answer_id="a-7",
        linked_question_id="q-7",
        verdict="accepted_as_declared",
    ).model_dump(mode="json")

    assert "evidence_candidate" not in payload
    assert payload["verdict"] == "accepted_as_declared"


def test_owner_answer_evaluation_contract_verified_has_no_side_effects() -> None:
    from pymia.contracts.owner_evaluation import OwnerAnswerEvaluation

    evaluation = OwnerAnswerEvaluation(
        evaluation_id="eval-8",
        source_answer_id="a-8",
        linked_question_id="q-8",
        verdict="verified",
        normalized_value="2026-01",
    )

    assert evaluation.verdict == "verified"
    assert evaluation.normalized_value == "2026-01"


def test_owner_evaluation_contract_has_no_prohibited_imports() -> None:
    contract_path = Path("pymia/contracts/owner_evaluation.py")
    source = contract_path.read_text(encoding="utf-8")

    forbidden_tokens = [
        "graph",
        "runtime",
        "diagnostic_core",
        "telegram",
        "hermes",
    ]

    lowered_source = source.lower()
    for token in forbidden_tokens:
        assert f"import {token}" not in lowered_source
        assert f"from {token} import" not in lowered_source
