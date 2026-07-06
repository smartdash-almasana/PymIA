from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_owner_reentry_bridge_v1 import (
    BRIDGE_STATUS_ACCEPTED_AND_PROJECTED,
    BRIDGE_STATUS_BLOCKED_REENTRY,
    SCHEMA_VERSION,
    run_service_1_owner_reentry_bridge_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    QUESTION_STATUS_ANSWERED,
    Service1QuestionBundleV1,
    build_service_1_question_bundle_v1,
    create_service_1_question_v1,
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


def _answered_bundle() -> Service1QuestionBundleV1:
    answered_question = create_service_1_question_v1(
        source="owner_question",
        text="Pregunta ya contestada",
        target_ref="owner:answered",
        status=QUESTION_STATUS_ANSWERED,
    )
    base = build_service_1_question_bundle_v1(
        case_id="case_2",
        tenant_id="tenant_1",
        intake_id="intake_2",
        run_id="run_2",
    )
    return Service1QuestionBundleV1(
        schema_version=base.schema_version,
        service_name=base.service_name,
        case_id=base.case_id,
        tenant_id=base.tenant_id,
        intake_id=base.intake_id,
        run_id=base.run_id,
        questions=(answered_question,),
        selected_next_question_ref=None,
        runtime_authorized=False,
        human_review_required=True,
        created_at=base.created_at,
        metadata={},
    )


def test_accepted_answer_persists_and_projects_partial(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    first_ref = bundle.questions[0].question_ref

    result = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle,
        question_ref=first_ref,
        raw_owner_answer="Caja primero.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.status == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED
    assert result.blocked_reason is None
    assert result.persistence_result is not None
    assert result.persistence_result.status == "PERSISTED"
    assert result.read_model is not None
    assert result.read_model.answers_count == 1
    assert result.projection is not None
    assert result.projection.status == "PARTIAL"
    assert result.projection.answered_count == 1
    assert result.projection.pending_count == 1
    assert result.selected_next_pending_question_ref == bundle.questions[1].question_ref
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_complete_projection_has_no_next_pending_question(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    for index, question in enumerate(bundle.questions, start=1):
        result = run_service_1_owner_reentry_bridge_v1(
            question_bundle=bundle,
            question_ref=question.question_ref,
            raw_owner_answer=f"Respuesta {index}",
            anamnesis_id="anamnesis_1",
            investigation_id="investigation_1",
            storage_dir=tmp_path,
        )
        assert result.status == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED

    assert result.projection is not None
    assert result.projection.status == "COMPLETE"
    assert result.projection.pending_count == 0
    assert result.selected_next_pending_question_ref is None


def test_unknown_question_ref_blocks_without_persistence(tmp_path: Path) -> None:
    result = run_service_1_owner_reentry_bridge_v1(
        question_bundle=_two_question_bundle(),
        question_ref="service_1:missing:question",
        raw_owner_answer="Respuesta",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )

    assert result.status == BRIDGE_STATUS_BLOCKED_REENTRY
    assert result.blocked_reason == "QUESTION_REF_NOT_FOUND"
    assert result.persistence_result is None
    assert result.read_model is None
    assert result.projection is None
    assert result.runtime_authorized is False
    assert result.delivery_authorized is False


def test_non_pending_question_blocks_without_persistence(tmp_path: Path) -> None:
    bundle = _answered_bundle()
    result = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle,
        question_ref=bundle.questions[0].question_ref,
        raw_owner_answer="Respuesta duplicada",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )

    assert result.status == BRIDGE_STATUS_BLOCKED_REENTRY
    assert result.blocked_reason == "QUESTION_NOT_PENDING"
    assert result.persistence_result is None
    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_empty_answer_fails_closed(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    with pytest.raises(ValueError, match="raw_owner_answer"):
        run_service_1_owner_reentry_bridge_v1(
            question_bundle=bundle,
            question_ref=bundle.questions[0].question_ref,
            raw_owner_answer="   ",
            anamnesis_id="anamnesis_1",
            investigation_id="investigation_1",
            storage_dir=tmp_path,
        )


def test_serialized_question_bundle_dict_is_accepted(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    result = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle.to_dict(),
        question_ref=bundle.questions[0].question_ref,
        raw_owner_answer="Caja primero.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )

    assert result.status == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED
    assert result.projection is not None
    assert result.projection.status == "PARTIAL"


def test_duplicate_answer_uses_latest_in_projection(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    question_ref = bundle.questions[0].question_ref

    first = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer="Primera respuesta",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )
    second = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer="Respuesta corregida",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
    )

    assert first.status == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED
    assert second.status == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED
    assert second.projection is not None
    assert second.projection.answered_questions[0].latest_raw_owner_answer == "Respuesta corregida"


def test_bridge_output_serializes_to_dict(tmp_path: Path) -> None:
    bundle = _two_question_bundle()
    result = run_service_1_owner_reentry_bridge_v1(
        question_bundle=bundle,
        question_ref=bundle.questions[0].question_ref,
        raw_owner_answer="Caja primero.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
        storage_dir=tmp_path,
        metadata={"capture_channel": "test"},
    )

    data = result.to_dict()
    json.dumps(data, ensure_ascii=False)

    assert data["status"] == BRIDGE_STATUS_ACCEPTED_AND_PROJECTED
    assert data["metadata"]["capture_channel"] == "test"
    assert data["reentry_packet"]["runtime_authorized"] is False
    assert data["projection"]["runtime_authorized"] is False
    assert data["delivery_authorized"] is False


def test_bridge_module_does_not_import_forbidden_runtime_dependencies() -> None:
    import pymia.smartpyme.service_1_owner_reentry_bridge_v1 as module

    source_names = set(module.__dict__)
    forbidden = {
        "openpyxl",
        "requests",
        "httpx",
        "run_service_1_pipeline_v1",
        "run_exceland_execution_flow_v1",
        "run_first_aid_minimal_v1",
    }

    assert source_names.isdisjoint(forbidden)
