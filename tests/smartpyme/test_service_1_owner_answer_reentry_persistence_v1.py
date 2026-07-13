from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1 import (
    PERSISTENCE_BLOCK_OWNER_ANSWER_RECORD_MISSING,
    PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED,
    PERSISTENCE_STATUS_BLOCKED,
    PERSISTENCE_STATUS_PERSISTED,
    SCHEMA_VERSION,
    Service1OwnerAnswerReentryPersistenceV1,
    persist_service_1_owner_answer_reentry_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    REENTRY_STATUS_BLOCKED,
    Service1OwnerAnswerReentryV1,
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _accepted_reentry_packet():
    bundle = build_service_1_question_bundle_v1(
        case_id="case_1",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_1",
        report={
            "owner_question": "Confirmas el objetivo principal?",
            "owner_question_technical_reference": "owner_axis:cash",
        },
    )
    assert bundle.selected_next_question_ref is not None
    return bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=bundle.selected_next_question_ref,
        raw_owner_answer="Quiero ordenar caja primero.",
        anamnesis_id="anamnesis_1",
        investigation_id="investigation_1",
    )


def test_persists_accepted_reentry_owner_answer_record(tmp_path: Path) -> None:
    reentry_packet = _accepted_reentry_packet()

    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=reentry_packet,
        storage_dir=tmp_path,
    )

    assert persistence.schema_version == SCHEMA_VERSION
    assert persistence.status == PERSISTENCE_STATUS_PERSISTED
    assert persistence.blocked_reason is None
    assert persistence.answer_id == reentry_packet.owner_answer_record.answer_id
    assert persistence.runtime_authorized is False
    assert persistence.owner_confirmation_required is True
    assert persistence.reexecution_authorized is False
    assert persistence.recalculation_authorized is False

    persisted_path = Path(persistence.persisted_path)
    assert persisted_path.name == "owner_answers.jsonl"
    assert persisted_path.exists()

    lines = persisted_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["answer_id"] == persistence.answer_id
    assert payload["question_ref"] == reentry_packet.question_ref
    assert payload["raw_owner_answer"] == "Quiero ordenar caja primero."
    assert payload["metadata"]["owner_answer_validation_status"] == "DECLARED_NOT_VALIDATED"
    assert payload["metadata"]["reexecution_authorized"] is False
    assert payload["metadata"]["recalculation_authorized"] is False


def test_persistence_packet_is_serializable(tmp_path: Path) -> None:
    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=_accepted_reentry_packet(),
        storage_dir=tmp_path,
        metadata={"operator_note": "persisted_by_slice_test"},
    )

    data = persistence.to_dict()

    assert data["status"] == PERSISTENCE_STATUS_PERSISTED
    assert data["metadata"]["operator_note"] == "persisted_by_slice_test"
    assert data["metadata"]["persisted_record_type"] == "OwnerAnswerRecord"


def test_blocks_reentry_packet_that_was_not_accepted(tmp_path: Path) -> None:
    accepted = _accepted_reentry_packet()
    blocked_reentry = Service1OwnerAnswerReentryV1(
        schema_version=accepted.schema_version,
        service_name=accepted.service_name,
        status=REENTRY_STATUS_BLOCKED,
        case_id=accepted.case_id,
        tenant_id=accepted.tenant_id,
        intake_id=accepted.intake_id,
        source_run_id=accepted.source_run_id,
        question_ref=accepted.question_ref,
        owner_answer_record=accepted.owner_answer_record,
        selected_question=accepted.selected_question,
        blocked_reason="TEST_BLOCK",
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=accepted.created_at,
        metadata={},
    )

    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=blocked_reentry,
        storage_dir=tmp_path,
    )

    assert persistence.status == PERSISTENCE_STATUS_BLOCKED
    assert persistence.blocked_reason == PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED
    assert persistence.persisted_path is None
    assert not (tmp_path / "tenant_1" / "owner_answers.jsonl").exists()


def test_blocks_accepted_packet_without_owner_answer_record(tmp_path: Path) -> None:
    accepted = _accepted_reentry_packet()
    broken_reentry = Service1OwnerAnswerReentryV1(
        schema_version=accepted.schema_version,
        service_name=accepted.service_name,
        status=accepted.status,
        case_id=accepted.case_id,
        tenant_id=accepted.tenant_id,
        intake_id=accepted.intake_id,
        source_run_id=accepted.source_run_id,
        question_ref=accepted.question_ref,
        owner_answer_record=None,
        selected_question=accepted.selected_question,
        blocked_reason=None,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=accepted.created_at,
        metadata={},
    )

    persistence = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=broken_reentry,
        storage_dir=tmp_path,
    )

    assert persistence.status == PERSISTENCE_STATUS_BLOCKED
    assert persistence.blocked_reason == PERSISTENCE_BLOCK_OWNER_ANSWER_RECORD_MISSING
    assert persistence.persisted_path is None


def test_rejects_wrong_packet_type(tmp_path: Path) -> None:
    try:
        persist_service_1_owner_answer_reentry_v1(
            reentry_packet={"status": "ACCEPTED_FOR_REENTRY"},
            storage_dir=tmp_path,
        )
    except ValueError as exc:
        assert "Service1OwnerAnswerReentryV1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_persistence_dataclass_allows_blocked_packet_serialization() -> None:
    packet = Service1OwnerAnswerReentryPersistenceV1(
        schema_version=SCHEMA_VERSION,
        service_name="SERVICE_1",
        status=PERSISTENCE_STATUS_BLOCKED,
        case_id="case",
        tenant_id="tenant",
        intake_id="intake",
        source_run_id="run",
        question_ref="question",
        answer_id=None,
        persisted_path=None,
        blocked_reason=PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at="2026-01-01T00:00:00+00:00",
    )

    data = packet.to_dict()

    assert data["blocked_reason"] == PERSISTENCE_BLOCK_REENTRY_NOT_ACCEPTED
    assert data["runtime_authorized"] is False
