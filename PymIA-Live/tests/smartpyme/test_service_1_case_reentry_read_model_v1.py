from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_case_reentry_read_model_v1 import (
    OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED,
    READ_MODEL_STATUS_EMPTY,
    READ_MODEL_STATUS_READY,
    READ_MODEL_STATUS_STORAGE_MISSING,
    SCHEMA_VERSION,
    load_service_1_case_reentry_read_model_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1 import (
    persist_service_1_owner_answer_reentry_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _persist_answer(tmp_path: Path, *, tenant_id: str = "tenant_1", intake_id: str = "intake_1", answer: str = "Caja primero."):
    bundle = build_service_1_question_bundle_v1(
        case_id="case_1",
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id="run_1",
        report={
            "owner_question": "Confirmas el objetivo principal?",
            "owner_question_technical_reference": "owner_axis:cash",
        },
    )
    assert bundle.selected_next_question_ref is not None
    reentry = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=bundle.selected_next_question_ref,
        raw_owner_answer=answer,
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )
    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=reentry,
        storage_dir=tmp_path,
    )
    return bundle, reentry, persistence


def test_loads_persisted_service_1_reentry_answers(tmp_path: Path) -> None:
    bundle, reentry, persistence = _persist_answer(tmp_path)

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    assert read_model.schema_version == SCHEMA_VERSION
    assert read_model.status == READ_MODEL_STATUS_READY
    assert read_model.case_id == "case_1"
    assert read_model.answers_count == 1
    assert read_model.answered_question_refs == (bundle.selected_next_question_ref,)
    assert read_model.latest_answer is not None
    assert read_model.latest_answer.answer_id == persistence.answer_id
    assert read_model.latest_answer.question_ref == reentry.question_ref
    assert read_model.latest_answer.raw_owner_answer == "Caja primero."
    assert read_model.latest_answer.owner_answer_validation_status == OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED
    assert read_model.runtime_authorized is False
    assert read_model.human_review_required is True
    assert read_model.reexecution_authorized is False
    assert read_model.recalculation_authorized is False


def test_loads_only_matching_tenant_and_intake(tmp_path: Path) -> None:
    _persist_answer(tmp_path, tenant_id="tenant_1", intake_id="intake_1", answer="Respuesta correcta")
    _persist_answer(tmp_path, tenant_id="tenant_1", intake_id="intake_2", answer="Otra intake")
    _persist_answer(tmp_path, tenant_id="tenant_2", intake_id="intake_1", answer="Otro tenant")

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    assert read_model.status == READ_MODEL_STATUS_READY
    assert read_model.answers_count == 1
    assert read_model.answers[0].raw_owner_answer == "Respuesta correcta"


def test_ignores_non_service_1_owner_answers(tmp_path: Path) -> None:
    tenant_dir = tmp_path / "tenant_1"
    tenant_dir.mkdir(parents=True)
    owner_answers = tenant_dir / "owner_answers.jsonl"
    owner_answers.write_text(
        json.dumps(
            {
                "answer_id": "answer_plain",
                "tenant_id": "tenant_1",
                "intake_id": "intake_1",
                "anamnesis_id": "anamnesis_1",
                "investigation_id": "investigation_1",
                "question_ref": "plain:q1",
                "raw_owner_answer": "No viene de Service 1 reentry",
                "answer_kind": "ANSWER_TO_PENDING_QUESTION",
                "created_at": "2026-01-01T00:00:00+00:00",
                "metadata": {"registered_by": "vertical_pipeline"},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    assert read_model.status == READ_MODEL_STATUS_EMPTY
    assert read_model.answers_count == 0
    assert read_model.answers == ()


def test_returns_storage_missing_when_owner_answers_jsonl_does_not_exist(tmp_path: Path) -> None:
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    assert read_model.status == READ_MODEL_STATUS_STORAGE_MISSING
    assert read_model.answers_count == 0
    assert read_model.storage_path.endswith("owner_answers.jsonl")


def test_returns_empty_when_file_exists_but_no_matching_service_1_answers(tmp_path: Path) -> None:
    tenant_dir = tmp_path / "tenant_1"
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "owner_answers.jsonl").write_text("", encoding="utf-8")

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    assert read_model.status == READ_MODEL_STATUS_EMPTY
    assert read_model.answers_count == 0


def test_read_model_is_serializable(tmp_path: Path) -> None:
    _persist_answer(tmp_path)

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
        metadata={"operator_note": "read_model_test"},
    )
    data = read_model.to_dict()

    assert data["status"] == READ_MODEL_STATUS_READY
    assert data["answers_count"] == 1
    assert data["metadata"]["operator_note"] == "read_model_test"
    assert data["latest_answer"]["question_ref"] == data["answered_question_refs"][0]
    assert data["answers"][0]["owner_answer_validation_status"] == OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED


def test_invalid_tenant_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="path traversal"):
        load_service_1_case_reentry_read_model_v1(
            storage_dir=tmp_path,
            tenant_id="../tenant",
            intake_id="intake_1",
        )


def test_invalid_jsonl_raises_clear_error(tmp_path: Path) -> None:
    tenant_dir = tmp_path / "tenant_1"
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "owner_answers.jsonl").write_text("{bad-json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSONL"):
        load_service_1_case_reentry_read_model_v1(
            storage_dir=tmp_path,
            tenant_id="tenant_1",
            intake_id="intake_1",
        )
