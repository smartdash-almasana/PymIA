from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.intake import ALLOWED_INTAKE_STATES, create_intake_record
from pymia.smartpyme.storage import (
    load_intake_record_by_id,
    load_intake_records,
    save_intake_record,
)


def test_save_intake_record_persists_jsonl_and_snapshot(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_a",
        raw_text="vendo mucho pero no me queda plata",
    )

    paths = save_intake_record(tmp_path, record)

    assert paths["intakes_jsonl"].exists()
    assert paths["intake_record_json"].exists()
    assert paths["intake_record_json"].name == "intake_record.json"
    assert paths["intake_record_json"].parent.name == "results"

    lines = paths["intakes_jsonl"].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["tenant_id"] == "tenant_a"
    assert obj["intake_id"] == record.intake_id
    assert obj["intake_state"] in ALLOWED_INTAKE_STATES


def test_load_intake_records_returns_records_for_tenant(tmp_path: Path) -> None:
    first = create_intake_record(tenant_id="tenant_b", raw_text="no me cierra la plata")
    second = create_intake_record(tenant_id="tenant_b", raw_text="tengo proveedores duplicados")
    save_intake_record(tmp_path, first)
    save_intake_record(tmp_path, second)

    records = load_intake_records(tmp_path, "tenant_b")
    assert [r.intake_id for r in records] == [first.intake_id, second.intake_id]
    assert all(r.tenant_id == "tenant_b" for r in records)


def test_load_intake_record_by_id_found_and_missing(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_c", raw_text="copio de excel a excel")
    save_intake_record(tmp_path, record)

    found = load_intake_record_by_id(tmp_path, "tenant_c", record.intake_id)
    assert found is not None
    assert found.intake_id == record.intake_id

    missing = load_intake_record_by_id(tmp_path, "tenant_c", "intake_missing")
    assert missing is None
