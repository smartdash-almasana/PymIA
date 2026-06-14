from __future__ import annotations

import json

import pytest

from pymia.smartpyme.owner_answer import create_owner_answer_record
from pymia.smartpyme.storage import ensure_tenant_storage, save_owner_answer_record


def test_ensure_tenant_storage_creates_owner_answers_jsonl(tmp_path) -> None:
    paths = ensure_tenant_storage(tmp_path, "tenant_demo")

    assert paths["owner_answers_jsonl"].exists()
    assert paths["owner_answers_jsonl"].read_text(encoding="utf-8") == ""


def test_save_owner_answer_record_persists_jsonl_line(tmp_path) -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="missing_input:ventas",
        raw_owner_answer="Las ventas están en la hoja Ventas.",
    )

    target = save_owner_answer_record("tenant_demo", record, base_dir=tmp_path)

    assert target.name == "owner_answers.jsonl"
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["answer_id"] == record.answer_id
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["anamnesis_id"] == "anamnesis_demo"
    assert payload["investigation_id"] == "investigation_demo"
    assert payload["question_ref"] == "missing_input:ventas"
    assert payload["raw_owner_answer"] == "Las ventas están en la hoja Ventas."


def test_save_owner_answer_record_rejects_empty_tenant_id(tmp_path) -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="q1",
        raw_owner_answer="Respuesta.",
    )

    with pytest.raises(ValueError, match="tenant_id is required"):
        save_owner_answer_record("", record, base_dir=tmp_path)


def test_save_owner_answer_record_rejects_tenant_mismatch(tmp_path) -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_a",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="q1",
        raw_owner_answer="Respuesta.",
    )

    with pytest.raises(ValueError, match="does not match"):
        save_owner_answer_record("tenant_b", record, base_dir=tmp_path)


def test_save_owner_answer_record_rejects_missing_required_field(tmp_path) -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="q1",
        raw_owner_answer="Respuesta.",
    ).to_dict()
    record.pop("question_ref")

    with pytest.raises(ValueError, match="question_ref"):
        save_owner_answer_record("tenant_demo", record, base_dir=tmp_path)


def test_save_owner_answer_record_rejects_non_dict_metadata(tmp_path) -> None:
    record = create_owner_answer_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        question_ref="q1",
        raw_owner_answer="Respuesta.",
    ).to_dict()
    record["metadata"] = "owner_chat"

    with pytest.raises(ValueError, match="metadata"):
        save_owner_answer_record("tenant_demo", record, base_dir=tmp_path)
