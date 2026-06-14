from __future__ import annotations

import json

import pytest

from pymia.smartpyme.investigation import create_investigation_record
from pymia.smartpyme.storage import ensure_tenant_storage, save_investigation_record


def test_ensure_tenant_storage_creates_investigations_jsonl(tmp_path) -> None:
    paths = ensure_tenant_storage(tmp_path, "tenant_demo")

    assert paths["investigations_jsonl"].exists()
    assert paths["investigations_jsonl"].read_text(encoding="utf-8") == ""


def test_save_investigation_record_persists_jsonl_line(tmp_path) -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Quiero saber si mi negocio deja margen.",
        investigation_axis="margen",
        evidence_required=["ventas", "costos"],
    )

    target = save_investigation_record("tenant_demo", record, base_dir=tmp_path)

    assert target.name == "investigations.jsonl"
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["investigation_id"] == record.investigation_id
    assert payload["tenant_id"] == "tenant_demo"
    assert payload["intake_id"] == "intake_demo"
    assert payload["anamnesis_id"] == "anamnesis_demo"
    assert payload["owner_prompt"] == "Quiero saber si mi negocio deja margen."
    assert payload["evidence_required"] == ["ventas", "costos"]


def test_save_investigation_record_rejects_empty_tenant_id(tmp_path) -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Necesito revisar margen.",
    )

    with pytest.raises(ValueError, match="tenant_id is required"):
        save_investigation_record("", record, base_dir=tmp_path)


def test_save_investigation_record_rejects_tenant_mismatch(tmp_path) -> None:
    record = create_investigation_record(
        tenant_id="tenant_a",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Necesito revisar margen.",
    )

    with pytest.raises(ValueError, match="does not match"):
        save_investigation_record("tenant_b", record, base_dir=tmp_path)


def test_save_investigation_record_rejects_missing_required_field(tmp_path) -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Necesito revisar margen.",
    ).to_dict()
    record.pop("anamnesis_id")

    with pytest.raises(ValueError, match="anamnesis_id"):
        save_investigation_record("tenant_demo", record, base_dir=tmp_path)


def test_save_investigation_record_rejects_non_list_candidates(tmp_path) -> None:
    record = create_investigation_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        anamnesis_id="anamnesis_demo",
        owner_prompt="Necesito revisar margen.",
    ).to_dict()
    record["formula_candidates"] = "PYME_026_flujo_operativo"

    with pytest.raises(ValueError, match="formula_candidates"):
        save_investigation_record("tenant_demo", record, base_dir=tmp_path)
