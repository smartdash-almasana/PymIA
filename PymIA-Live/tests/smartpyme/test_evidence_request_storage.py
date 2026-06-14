from __future__ import annotations

import json

import pytest

from pymia.smartpyme.evidence_request import create_evidence_request_record
from pymia.smartpyme.storage import ensure_tenant_storage, save_evidence_request_record


def test_ensure_tenant_storage_creates_evidence_requests_jsonl(tmp_path) -> None:
    paths = ensure_tenant_storage(tmp_path, "tenant_demo")

    assert paths["evidence_requests_jsonl"].exists()
    assert paths["evidence_requests_jsonl"].read_text(encoding="utf-8") == ""


def test_save_evidence_request_record_persists_jsonl_line(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        owner_answer_id="answer_demo",
        requested_evidence=["ventas_del_periodo", "costos_directos"],
        request_reason="Faltan datos para contrastar margen.",
    )

    target = save_evidence_request_record("tenant_demo", record, base_dir=tmp_path)

    assert target.name == "evidence_requests.jsonl"
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["request_id"] == record.request_id
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["anamnesis_id"] == "anamnesis_demo"
    assert payload["investigation_id"] == "investigation_demo"
    assert payload["owner_answer_id"] == "answer_demo"
    assert payload["requested_evidence"] == ["ventas_del_periodo", "costos_directos"]
    assert payload["request_reason"] == "Faltan datos para contrastar margen."


def test_save_evidence_request_record_rejects_empty_tenant_id(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas"],
        request_reason="Falta ventas.",
    )

    with pytest.raises(ValueError, match="tenant_id is required"):
        save_evidence_request_record("", record, base_dir=tmp_path)


def test_save_evidence_request_record_rejects_tenant_mismatch(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_a",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas"],
        request_reason="Falta ventas.",
    )

    with pytest.raises(ValueError, match="does not match"):
        save_evidence_request_record("tenant_b", record, base_dir=tmp_path)


def test_save_evidence_request_record_rejects_missing_required_field(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas"],
        request_reason="Falta ventas.",
    ).to_dict()
    record.pop("requested_evidence")

    with pytest.raises(ValueError, match="requested_evidence"):
        save_evidence_request_record("tenant_demo", record, base_dir=tmp_path)


def test_save_evidence_request_record_rejects_non_list_requested_evidence(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas"],
        request_reason="Falta ventas.",
    ).to_dict()
    record["requested_evidence"] = "ventas"

    with pytest.raises(ValueError, match="requested_evidence"):
        save_evidence_request_record("tenant_demo", record, base_dir=tmp_path)


def test_save_evidence_request_record_rejects_non_dict_metadata(tmp_path) -> None:
    record = create_evidence_request_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        investigation_id="investigation_demo",
        requested_evidence=["ventas"],
        request_reason="Falta ventas.",
    ).to_dict()
    record["metadata"] = "operator"

    with pytest.raises(ValueError, match="metadata"):
        save_evidence_request_record("tenant_demo", record, base_dir=tmp_path)
