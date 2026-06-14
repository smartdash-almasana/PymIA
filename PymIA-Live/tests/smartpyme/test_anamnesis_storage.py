from __future__ import annotations

import json

import pytest

from pymia.smartpyme.anamnesis import create_anamnesis_record
from pymia.smartpyme.storage import ensure_tenant_storage, save_anamnesis_record


def test_ensure_tenant_storage_creates_anamnesis_jsonl(tmp_path) -> None:
    paths = ensure_tenant_storage(tmp_path, "tenant_demo")

    assert paths["anamnesis_jsonl"].exists()
    assert paths["anamnesis_jsonl"].read_text(encoding="utf-8") == ""


def test_save_anamnesis_record_persists_jsonl_line(tmp_path) -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="Quiero entender si mi negocio deja margen.",
        declared_pains=["incertidumbre de margen"],
        requested_documents=["ventas", "costos"],
    )

    target = save_anamnesis_record("tenant_demo", record, base_dir=tmp_path)

    assert target.name == "anamnesis.jsonl"
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["anamnesis_id"] == record.anamnesis_id
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["declared_pains"] == ["incertidumbre de margen"]
    assert payload["requested_documents"] == ["ventas", "costos"]


def test_save_anamnesis_record_rejects_empty_tenant_id(tmp_path) -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="Necesito ordenar mi empresa.",
    )

    with pytest.raises(ValueError, match="tenant_id is required"):
        save_anamnesis_record("", record, base_dir=tmp_path)


def test_save_anamnesis_record_rejects_tenant_mismatch(tmp_path) -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_a",
        intake_id="intake_demo",
        raw_owner_message="Necesito ordenar mi empresa.",
    )

    with pytest.raises(ValueError, match="does not match"):
        save_anamnesis_record("tenant_b", record, base_dir=tmp_path)


def test_save_anamnesis_record_rejects_missing_required_field(tmp_path) -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="Necesito ordenar mi empresa.",
    ).to_dict()
    record.pop("business_taxonomy")

    with pytest.raises(ValueError, match="business_taxonomy"):
        save_anamnesis_record("tenant_demo", record, base_dir=tmp_path)
