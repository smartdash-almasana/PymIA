from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_case_reentry_read_model_v1 import (
    load_service_1_case_reentry_read_model_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1 import (
    persist_service_1_owner_answer_reentry_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    Service1QuestionBundleV1,
    build_service_1_question_bundle_v1,
    create_service_1_question_v1,
)
from pymia.smartpyme.service_1_reentry_projection_v1 import (
    PROJECTION_BLOCK_CASE_MISMATCH,
    PROJECTION_STATUS_BLOCKED,
    PROJECTION_STATUS_COMPLETE,
    PROJECTION_STATUS_NO_ANSWERS,
    PROJECTION_STATUS_NO_QUESTIONS,
    PROJECTION_STATUS_PARTIAL,
    SCHEMA_VERSION,
    project_service_1_reentry_v1,
)


def _two_question_bundle() -> Service1QuestionBundleV1:
    return build_service_1_question_bundle_v1(
        case_id="case_1",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_1",
        report={
            "next_questions": [
                {"text": "Confirmas el objetivo principal?", "target_ref": "owner_axis:cash"},
                {"text": "Que periodo cubre el archivo?", "target_ref": "missing:period"},
            ]
        },
    )


def _persist_answer_for_question(tmp_path: Path, bundle: Service1QuestionBundleV1, question_ref: str, answer: str) -> None:
    reentry = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer=answer,
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )
    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=reentry,
        storage_dir=tmp_path,
    )
    assert persistence.status == "PERSISTED"


def test_projects_no_answers_as_all_pending(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.schema_version == SCHEMA_VERSION
    assert projection.status == PROJECTION_STATUS_NO_ANSWERS
    assert projection.total_questions == 2
    assert projection.answered_count == 0
    assert projection.pending_count == 2
    assert projection.answered_question_refs == ()
    assert projection.pending_question_refs == tuple(question.question_ref for question in bundle.questions)
    assert projection.selected_next_pending_question_ref == bundle.questions[0].question_ref
    assert projection.runtime_authorized is False
    assert projection.owner_confirmation_required is True
    assert projection.reexecution_authorized is False
    assert projection.recalculation_authorized is False


def test_projects_partial_answers_and_selects_next_pending(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    first_ref = bundle.questions[0].question_ref
    second_ref = bundle.questions[1].question_ref
    _persist_answer_for_question(tmp_path, bundle, first_ref, "Caja primero.")
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.status == PROJECTION_STATUS_PARTIAL
    assert projection.answered_count == 1
    assert projection.pending_count == 1
    assert projection.answered_question_refs == (first_ref,)
    assert projection.pending_question_refs == (second_ref,)
    assert projection.selected_next_pending_question_ref == second_ref
    assert projection.answered_questions[0].latest_raw_owner_answer == "Caja primero."
    assert projection.answered_questions[0].owner_answer_validation_status == "DECLARED_NOT_VALIDATED"
    assert projection.pending_questions[0].question_ref == second_ref


def test_projects_complete_when_all_questions_answered(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    for index, question in enumerate(bundle.questions, start=1):
        _persist_answer_for_question(tmp_path, bundle, question.question_ref, f"Respuesta {index}")
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.status == PROJECTION_STATUS_COMPLETE
    assert projection.answered_count == 2
    assert projection.pending_count == 0
    assert projection.selected_next_pending_question_ref is None
    assert projection.pending_questions == ()


def test_projection_with_empty_bundle_has_no_questions(tmp_path: Path) -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_empty",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_empty",
    )
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.status == PROJECTION_STATUS_NO_QUESTIONS
    assert projection.total_questions == 0
    assert projection.selected_next_pending_question_ref is None


def test_projection_blocks_case_mismatch(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="other_intake",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.status == PROJECTION_STATUS_BLOCKED
    assert projection.blocked_reason == PROJECTION_BLOCK_CASE_MISMATCH
    assert projection.pending_count == 2
    assert projection.answered_count == 0
    assert projection.selected_next_pending_question_ref == bundle.selected_next_question_ref


def test_projection_uses_latest_answer_for_duplicate_question_ref(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    question_ref = bundle.questions[0].question_ref
    _persist_answer_for_question(tmp_path, bundle, question_ref, "Primera respuesta")
    _persist_answer_for_question(tmp_path, bundle, question_ref, "Respuesta corregida")
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.status == PROJECTION_STATUS_PARTIAL
    assert projection.answered_questions[0].latest_raw_owner_answer == "Respuesta corregida"


def test_projection_is_serializable(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    _persist_answer_for_question(tmp_path, bundle, bundle.questions[0].question_ref, "Caja primero.")
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(
        question_bundle=bundle,
        read_model=read_model,
        metadata={"operator_note": "projection_test"},
    )
    data = projection.to_dict()

    assert data["status"] == PROJECTION_STATUS_PARTIAL
    assert data["metadata"]["operator_note"] == "projection_test"
    assert data["answered_questions"][0]["projection_status"] == "ANSWERED"
    assert data["pending_questions"][0]["projection_status"] == "PENDING"
    assert data["runtime_authorized"] is False


def test_rejects_wrong_bundle_type(tmp_path: Path) -> None:
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    with pytest.raises(ValueError, match="Service1QuestionBundleV1"):
        project_service_1_reentry_v1(question_bundle={"bad": True}, read_model=read_model)


def test_rejects_wrong_read_model_type() -> None:
    bundle = _two_question_bundle()

    with pytest.raises(ValueError, match="Service1CaseReentryReadModelV1"):
        project_service_1_reentry_v1(question_bundle=bundle, read_model={"bad": True})


def test_projection_respects_manual_question_status_but_does_not_mutate_it(tmp_path: Path) -> None:
    question = create_service_1_question_v1(
        source="owner_question",
        text="Pregunta pendiente",
        target_ref="owner:manual",
    )
    bundle = build_service_1_question_bundle_v1(
        case_id="case_manual",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_manual",
    )
    bundle = Service1QuestionBundleV1(
        schema_version=bundle.schema_version,
        service_name=bundle.service_name,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        run_id=bundle.run_id,
        questions=(question,),
        selected_next_question_ref=question.question_ref,
        runtime_authorized=False,
        owner_confirmation_required=True,
        created_at=bundle.created_at,
        metadata={},
    )
    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=tmp_path,
        tenant_id="tenant_1",
        intake_id="intake_1",
    )

    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)

    assert projection.pending_questions[0].original_status == question.status
    assert question.status == "PENDING"
