"""Tests para persistencia de EvidenceRecord en storage.py.

Contrato aprobado:
    save_evidence_record(tenant_id, record, *, base_dir=None) -> Path
    load_evidence_records(tenant_id, *, base_dir=None) -> list[dict]
    load_evidence_records_by_intake_id(tenant_id, intake_id, *, base_dir=None) -> list[dict]
    load_evidence_record_by_id(tenant_id, evidence_id, *, base_dir=None) -> dict | None

Este slice SOLO persiste metadata de evidencia.
NO lee archivos, NO calcula hash, NO valida contenido documental.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from pymia.smartpyme.evidence import create_evidence_record, EvidenceRecord
from pymia.smartpyme.storage import (
    save_evidence_record,
    load_evidence_records,
    load_evidence_records_by_intake_id,
    load_evidence_record_by_id,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_evidence(
    *,
    tenant_id: str = "tenant_evidence_01",
    intake_id: str = "intake_001",
    evidence_type: str = "excel_proveedores",
    source_kind: str = "uploaded_file",
    source_ref: str = "/tmp/proveedores.xlsx",
    request_id: str | None = None,
) -> EvidenceRecord:
    return create_evidence_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        evidence_type=evidence_type,
        source_kind=source_kind,
        source_ref=source_ref,
        request_id=request_id,
    )


# ---------------------------------------------------------------------------
# 1. Import smoke
# ---------------------------------------------------------------------------
def test_import_smoke():
    """Confirma que las 4 funciones públicas son importables."""
    from pymia.smartpyme.storage import (
        save_evidence_record,
        load_evidence_records,
        load_evidence_records_by_intake_id,
        load_evidence_record_by_id,
    )
    assert callable(save_evidence_record)
    assert callable(load_evidence_records)
    assert callable(load_evidence_records_by_intake_id)
    assert callable(load_evidence_record_by_id)


# ---------------------------------------------------------------------------
# 2. Signature verification
# ---------------------------------------------------------------------------
def test_save_evidence_record_signature():
    sig = inspect.signature(save_evidence_record)
    params = list(sig.parameters.keys())
    assert params[0] == "tenant_id"
    assert params[1] == "record"
    assert "base_dir" in sig.parameters
    assert sig.parameters["base_dir"].kind == inspect.Parameter.KEYWORD_ONLY


def test_load_evidence_records_signature():
    sig = inspect.signature(load_evidence_records)
    params = list(sig.parameters.keys())
    assert params[0] == "tenant_id"
    assert "base_dir" in sig.parameters
    assert sig.parameters["base_dir"].kind == inspect.Parameter.KEYWORD_ONLY


def test_load_evidence_records_by_intake_id_signature():
    sig = inspect.signature(load_evidence_records_by_intake_id)
    params = list(sig.parameters.keys())
    assert params == ["tenant_id", "intake_id", "base_dir"]
    assert sig.parameters["base_dir"].kind == inspect.Parameter.KEYWORD_ONLY


def test_load_evidence_record_by_id_signature():
    sig = inspect.signature(load_evidence_record_by_id)
    params = list(sig.parameters.keys())
    assert params == ["tenant_id", "evidence_id", "base_dir"]
    assert sig.parameters["base_dir"].kind == inspect.Parameter.KEYWORD_ONLY


# ---------------------------------------------------------------------------
# 3. Load missing returns []
# ---------------------------------------------------------------------------
def test_load_missing_evidences_returns_empty_list(tmp_path):
    records = load_evidence_records("tenant_missing", base_dir=tmp_path)
    assert records == []


# ---------------------------------------------------------------------------
# 4. Save creates evidences.jsonl
# ---------------------------------------------------------------------------
def test_save_evidence_record_creates_evidences_jsonl(tmp_path):
    record = _make_evidence(tenant_id="tenant_01")
    save_evidence_record("tenant_01", record, base_dir=tmp_path)

    jsonl_path = tmp_path / "tenant_01" / "evidences.jsonl"
    assert jsonl_path.exists()
    content = jsonl_path.read_text(encoding="utf-8").strip()
    assert content  # no vacío


# ---------------------------------------------------------------------------
# 5. Save returns Path
# ---------------------------------------------------------------------------
def test_save_returns_path(tmp_path):
    record = _make_evidence(tenant_id="tenant_ret")
    result = save_evidence_record("tenant_ret", record, base_dir=tmp_path)
    assert isinstance(result, Path)
    assert result.name == "evidences.jsonl"


# ---------------------------------------------------------------------------
# 6. Save accepts EvidenceRecord instance
# ---------------------------------------------------------------------------
def test_save_accepts_evidence_record_instance(tmp_path):
    record = _make_evidence(tenant_id="tenant_02")
    save_evidence_record("tenant_02", record, base_dir=tmp_path)

    loaded = load_evidence_records("tenant_02", base_dir=tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["evidence_id"] == record.evidence_id


# ---------------------------------------------------------------------------
# 7. Save accepts plain dict
# ---------------------------------------------------------------------------
def test_save_accepts_plain_dict(tmp_path):
    record = _make_evidence(tenant_id="tenant_03")
    record_dict = record.to_dict()
    save_evidence_record("tenant_03", record_dict, base_dir=tmp_path)

    loaded = load_evidence_records("tenant_03", base_dir=tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["evidence_id"] == record.evidence_id


# ---------------------------------------------------------------------------
# 8. Load preserves insertion order
# ---------------------------------------------------------------------------
def test_load_preserves_insertion_order(tmp_path):
    tenant = "tenant_order"
    rec_a = _make_evidence(tenant_id=tenant)
    rec_b = _make_evidence(tenant_id=tenant)
    save_evidence_record(tenant, rec_a, base_dir=tmp_path)
    save_evidence_record(tenant, rec_b, base_dir=tmp_path)

    loaded = load_evidence_records(tenant, base_dir=tmp_path)
    assert [r["evidence_id"] for r in loaded] == [
        rec_a.evidence_id,
        rec_b.evidence_id,
    ]


# ---------------------------------------------------------------------------
# 9. Load returns list[dict]
# ---------------------------------------------------------------------------
def test_load_returns_list_of_dicts(tmp_path):
    tenant = "tenant_dict"
    save_evidence_record(tenant, _make_evidence(tenant_id=tenant), base_dir=tmp_path)
    loaded = load_evidence_records(tenant, base_dir=tmp_path)
    assert isinstance(loaded, list)
    assert all(isinstance(r, dict) for r in loaded)


# ---------------------------------------------------------------------------
# 10. load_evidence_records_by_intake_id returns matching
# ---------------------------------------------------------------------------
def test_load_evidence_records_by_intake_id_returns_matching_records(tmp_path):
    tenant = "tenant_filter"
    rec_a = _make_evidence(tenant_id=tenant, intake_id="intake_A")
    rec_b = _make_evidence(tenant_id=tenant, intake_id="intake_B")
    rec_c = _make_evidence(tenant_id=tenant, intake_id="intake_A")
    save_evidence_record(tenant, rec_a, base_dir=tmp_path)
    save_evidence_record(tenant, rec_b, base_dir=tmp_path)
    save_evidence_record(tenant, rec_c, base_dir=tmp_path)

    result = load_evidence_records_by_intake_id(tenant, "intake_A", base_dir=tmp_path)
    assert len(result) == 2
    assert {r["evidence_id"] for r in result} == {rec_a.evidence_id, rec_c.evidence_id}


def test_load_evidence_records_by_intake_id_returns_empty_when_absent(tmp_path):
    tenant = "tenant_filter_empty"
    save_evidence_record(
        tenant, _make_evidence(tenant_id=tenant, intake_id="intake_X"), base_dir=tmp_path
    )
    result = load_evidence_records_by_intake_id(
        tenant, "intake_NONEXISTENT", base_dir=tmp_path
    )
    assert result == []


# ---------------------------------------------------------------------------
# 11. load_evidence_record_by_id
# ---------------------------------------------------------------------------
def test_load_evidence_record_by_id_returns_matching_record(tmp_path):
    tenant = "tenant_lookup"
    rec = _make_evidence(tenant_id=tenant)
    save_evidence_record(tenant, rec, base_dir=tmp_path)

    found = load_evidence_record_by_id(tenant, rec.evidence_id, base_dir=tmp_path)
    assert found is not None
    assert found["evidence_id"] == rec.evidence_id


def test_load_evidence_record_by_id_returns_none_when_absent(tmp_path):
    tenant = "tenant_lookup_miss"
    save_evidence_record(tenant, _make_evidence(tenant_id=tenant), base_dir=tmp_path)
    found = load_evidence_record_by_id(
        tenant, "evidence_nonexistent", base_dir=tmp_path
    )
    assert found is None


# ---------------------------------------------------------------------------
# 12. Empty tenant_id raises
# ---------------------------------------------------------------------------
def test_empty_tenant_id_raises_on_save(tmp_path):
    record = _make_evidence()
    with pytest.raises(ValueError, match="tenant_id is required"):
        save_evidence_record("", record, base_dir=tmp_path)


def test_empty_tenant_id_raises_on_load(tmp_path):
    with pytest.raises(ValueError, match="tenant_id is required"):
        load_evidence_records("", base_dir=tmp_path)


def test_whitespace_tenant_id_raises_on_save(tmp_path):
    record = _make_evidence()
    with pytest.raises(ValueError, match="tenant_id is required"):
        save_evidence_record("   ", record, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 13. Empty intake_id raises on load_by_intake_id
# ---------------------------------------------------------------------------
def test_empty_intake_id_raises_on_load_by_intake_id(tmp_path):
    with pytest.raises(ValueError, match="intake_id is required"):
        load_evidence_records_by_intake_id("t", "", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 14. Empty evidence_id raises on lookup
# ---------------------------------------------------------------------------
def test_empty_evidence_id_raises_on_lookup(tmp_path):
    with pytest.raises(ValueError, match="evidence_id is required"):
        load_evidence_record_by_id("t", "", base_dir=tmp_path)


def test_whitespace_evidence_id_raises_on_lookup(tmp_path):
    with pytest.raises(ValueError, match="evidence_id is required"):
        load_evidence_record_by_id("t", "   ", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 15. Tenant mismatch raises
# ---------------------------------------------------------------------------
def test_tenant_mismatch_raises(tmp_path):
    record = _make_evidence(tenant_id="tenant_A")
    with pytest.raises(ValueError, match="does not match"):
        save_evidence_record("tenant_B", record, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 16. Missing required field raises
# ---------------------------------------------------------------------------
def test_missing_required_field_raises(tmp_path):
    tenant = "tenant_missing_field"
    record = _make_evidence(tenant_id=tenant)
    record_dict = record.to_dict()
    del record_dict["evidence_type"]
    with pytest.raises(ValueError, match="missing required field"):
        save_evidence_record(tenant, record_dict, base_dir=tmp_path)


def test_record_missing_tenant_id_field_raises(tmp_path):
    record = _make_evidence()
    record_dict = record.to_dict()
    del record_dict["tenant_id"]
    with pytest.raises(ValueError, match="missing tenant_id field"):
        save_evidence_record("some_tenant", record_dict, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 17. Malformed JSON line raises
# ---------------------------------------------------------------------------
def test_malformed_json_line_raises(tmp_path):
    tenant = "tenant_malformed"
    paths = (tmp_path / tenant)
    paths.mkdir(parents=True)
    jsonl = paths / "evidences.jsonl"
    jsonl.write_text("{not valid json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="malformed JSON"):
        load_evidence_records(tenant, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 18. Non-dict JSON line raises
# ---------------------------------------------------------------------------
def test_non_dict_json_line_raises(tmp_path):
    tenant = "tenant_non_dict"
    paths = (tmp_path / tenant)
    paths.mkdir(parents=True)
    jsonl = paths / "evidences.jsonl"
    jsonl.write_text("[1, 2, 3]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not a dict"):
        load_evidence_records(tenant, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 19. JSON line is valid JSON
# ---------------------------------------------------------------------------
def test_json_line_is_valid_json(tmp_path):
    tenant = "tenant_valid_json"
    record = _make_evidence(tenant_id=tenant)
    save_evidence_record(tenant, record, base_dir=tmp_path)

    jsonl = tmp_path / tenant / "evidences.jsonl"
    content = jsonl.read_text(encoding="utf-8").strip()
    for line in content.splitlines():
        if line.strip():
            obj = json.loads(line)
            assert isinstance(obj, dict)


# ---------------------------------------------------------------------------
# 20. No cross-tenant reads
# ---------------------------------------------------------------------------
def test_no_cross_tenant_reads(tmp_path):
    tenant_a = "tenant_A"
    tenant_b = "tenant_B"
    save_evidence_record(
        tenant_a, _make_evidence(tenant_id=tenant_a), base_dir=tmp_path
    )
    loaded_b = load_evidence_records(tenant_b, base_dir=tmp_path)
    assert loaded_b == []


# ---------------------------------------------------------------------------
# 21. Record is not mutated
# ---------------------------------------------------------------------------
def test_record_is_not_mutated(tmp_path):
    tenant = "tenant_immut"
    record = _make_evidence(tenant_id=tenant)
    record_dict = record.to_dict()
    original_keys = set(record_dict.keys())

    save_evidence_record(tenant, record_dict, base_dir=tmp_path)

    assert set(record_dict.keys()) == original_keys


# ---------------------------------------------------------------------------
# 22. Existing intake storage not broken
# ---------------------------------------------------------------------------
def test_existing_intake_storage_not_broken(tmp_path):
    """Smoke test: save_intake_record y load_intake_records siguen funcionando."""
    from pymia.smartpyme.storage import save_intake_record, load_intake_records
    from pymia.smartpyme.intake import create_intake_record

    tenant = "tenant_compat"
    ir = create_intake_record(tenant_id=tenant, raw_text="Tengo proveedores repetidos")
    save_intake_record(tenant, ir, base_dir=tmp_path)
    loaded = load_intake_records(tenant, base_dir=tmp_path)
    assert len(loaded) == 1


# ---------------------------------------------------------------------------
# 23. base_dir required
# ---------------------------------------------------------------------------
def test_base_dir_required_on_save():
    record = _make_evidence()
    with pytest.raises(ValueError, match="base_dir is required"):
        save_evidence_record("t", record)


def test_base_dir_required_on_load():
    with pytest.raises(ValueError, match="base_dir is required"):
        load_evidence_records("t")


def test_base_dir_required_on_load_by_id():
    with pytest.raises(ValueError, match="base_dir is required"):
        load_evidence_record_by_id("t", "e")


def test_base_dir_required_on_load_by_intake_id():
    with pytest.raises(ValueError, match="base_dir is required"):
        load_evidence_records_by_intake_id("t", "i")


# ---------------------------------------------------------------------------
# Extra: notes and metadata type validation
# ---------------------------------------------------------------------------
def test_notes_must_be_list(tmp_path):
    tenant = "tenant_notes"
    record = _make_evidence(tenant_id=tenant)
    record_dict = record.to_dict()
    record_dict["notes"] = "not a list"
    with pytest.raises(ValueError, match="notes must be list"):
        save_evidence_record(tenant, record_dict, base_dir=tmp_path)


def test_metadata_must_be_dict(tmp_path):
    tenant = "tenant_meta"
    record = _make_evidence(tenant_id=tenant)
    record_dict = record.to_dict()
    record_dict["metadata"] = ["not", "a", "dict"]
    with pytest.raises(ValueError, match="metadata must be dict"):
        save_evidence_record(tenant, record_dict, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# Extra: size_bytes type validation
# ---------------------------------------------------------------------------
def test_size_bytes_must_be_int_or_none(tmp_path):
    tenant = "tenant_size"
    record = _make_evidence(tenant_id=tenant)
    record_dict = record.to_dict()
    record_dict["size_bytes"] = "not_int"
    with pytest.raises(ValueError, match="size_bytes must be int"):
        save_evidence_record(tenant, record_dict, base_dir=tmp_path)
