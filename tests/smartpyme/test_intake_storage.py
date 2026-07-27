"""Tests for SMARTPYME_INTAKE_STORAGE_PERSISTENCE slice.

API aprobada (alineada con contrato):
    save_intake_record(tenant_id, record, *, base_dir=None) -> Path
    load_intake_records(tenant_id, *, base_dir=None) -> list[dict]
    load_intake_record_by_id(tenant_id, intake_id, *, base_dir=None) -> dict | None

Tests verifican el contrato aprobado, no la implementación divergente previa.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from pymia.smartpyme.intake import ALLOWED_INTAKE_STATES, IntakeRecord, create_intake_record
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
from pymia.smartpyme.storage import (
    load_intake_record_by_id,
    load_intake_records,
    save_intake_record,
)


# ---------------------------------------------------------------------------
# 18. Import smoke
# ---------------------------------------------------------------------------
def test_import_smoke() -> None:
    """Los tres símbolos públicos deben poder importarse sin errores."""
    from pymia.smartpyme.storage import (
        load_intake_record_by_id as _by_id,
        load_intake_records as _records,
        save_intake_record as _save,
    )
    assert callable(_save)
    assert callable(_records)
    assert callable(_by_id)


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------
def test_save_intake_record_signature() -> None:
    """save_intake_record debe tener tenant_id primero y base_dir keyword-only."""
    sig = inspect.signature(save_intake_record)
    params = list(sig.parameters.keys())
    assert params[0] == "tenant_id"
    assert params[1] == "record"
    assert "base_dir" in params
    # base_dir debe ser keyword-only
    base_dir_param = sig.parameters["base_dir"]
    assert base_dir_param.kind == inspect.Parameter.KEYWORD_ONLY


def test_load_intake_records_signature() -> None:
    """load_intake_records debe tener tenant_id primero y base_dir keyword-only."""
    sig = inspect.signature(load_intake_records)
    params = list(sig.parameters.keys())
    assert params[0] == "tenant_id"
    assert "base_dir" in params
    base_dir_param = sig.parameters["base_dir"]
    assert base_dir_param.kind == inspect.Parameter.KEYWORD_ONLY


def test_load_intake_record_by_id_signature() -> None:
    """load_intake_record_by_id debe tener tenant_id, intake_id, y base_dir keyword-only."""
    sig = inspect.signature(load_intake_record_by_id)
    params = list(sig.parameters.keys())
    assert params[0] == "tenant_id"
    assert params[1] == "intake_id"
    assert "base_dir" in params
    base_dir_param = sig.parameters["base_dir"]
    assert base_dir_param.kind == inspect.Parameter.KEYWORD_ONLY


# ---------------------------------------------------------------------------
# 1. Load missing intakes returns []
# ---------------------------------------------------------------------------
def test_load_missing_intakes_returns_empty_list(tmp_path: Path) -> None:
    """Un tenant sin intakes.jsonl poblado debe devolver lista vacía."""
    records = load_intake_records("tenant_empty", base_dir=tmp_path)
    assert records == []


# ---------------------------------------------------------------------------
# 2. Save creates intakes.jsonl
# ---------------------------------------------------------------------------
def test_save_creates_intakes_jsonl(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_create",
        raw_text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
    )
    result_path = save_intake_record("tenant_create", record, base_dir=tmp_path)

    assert result_path.exists()
    assert result_path.name == "intakes.jsonl"
    lines = result_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


# ---------------------------------------------------------------------------
# 3. Save accepts IntakeRecord instance from create_intake_record
# ---------------------------------------------------------------------------
def test_save_accepts_intake_record_instance(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_inst",
        raw_text="tengo proveedores duplicados y CUIT mezclados",
    )
    result_path = save_intake_record("tenant_inst", record, base_dir=tmp_path)

    assert result_path.exists()
    assert result_path.name == "intakes.jsonl"

    line = result_path.read_text(encoding="utf-8").strip().splitlines()[0]
    obj = json.loads(line)
    assert obj["tenant_id"] == "tenant_inst"
    assert obj["intake_id"] == record.intake_id
    assert obj["intake_state"] in ALLOWED_INTAKE_STATES


# ---------------------------------------------------------------------------
# 4. Save accepts plain dict
# ---------------------------------------------------------------------------
def test_save_accepts_plain_dict(tmp_path: Path) -> None:
    """save_intake_record debe aceptar dict plano (no solo IntakeRecord)."""
    record = create_intake_record(
        tenant_id="tenant_dict",
        raw_text="necesito revisar costos",
    )
    plain = record.to_dict()

    result_path = save_intake_record("tenant_dict", plain, base_dir=tmp_path)
    assert result_path.exists()

    loaded = load_intake_records("tenant_dict", base_dir=tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["intake_id"] == record.intake_id


# ---------------------------------------------------------------------------
# 5. Save returns Path
# ---------------------------------------------------------------------------
def test_save_returns_path(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_path",
        raw_text="revisar márgenes",
    )
    result = save_intake_record("tenant_path", record, base_dir=tmp_path)
    assert isinstance(result, Path)
    assert result.name == "intakes.jsonl"


# ---------------------------------------------------------------------------
# 6. Load preserves insertion order
# ---------------------------------------------------------------------------
def test_load_preserves_insertion_order(tmp_path: Path) -> None:
    first = create_intake_record(tenant_id="tenant_order", raw_text="no me cierra la plata")
    second = create_intake_record(tenant_id="tenant_order", raw_text="tengo proveedores duplicados")
    third = create_intake_record(tenant_id="tenant_order", raw_text="el stock no coincide con depósito")

    save_intake_record("tenant_order", first, base_dir=tmp_path)
    save_intake_record("tenant_order", second, base_dir=tmp_path)
    save_intake_record("tenant_order", third, base_dir=tmp_path)

    loaded = load_intake_records("tenant_order", base_dir=tmp_path)
    assert [r["intake_id"] for r in loaded] == [first.intake_id, second.intake_id, third.intake_id]
    assert all(r["tenant_id"] == "tenant_order" for r in loaded)


# ---------------------------------------------------------------------------
# 7. load_intake_records returns list[dict]
# ---------------------------------------------------------------------------
def test_load_returns_list_of_dicts(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_type",
        raw_text="proveedores repetidos",
    )
    save_intake_record("tenant_type", record, base_dir=tmp_path)

    loaded = load_intake_records("tenant_type", base_dir=tmp_path)
    assert len(loaded) == 1
    assert isinstance(loaded[0], dict)
    assert loaded[0]["intake_id"] == record.intake_id


# ---------------------------------------------------------------------------
# 8. load_intake_record_by_id returns correct dict
# ---------------------------------------------------------------------------
def test_load_by_id_returns_matching(tmp_path: Path) -> None:
    first = create_intake_record(tenant_id="tenant_byid", raw_text="copio de excel a excel")
    second = create_intake_record(tenant_id="tenant_byid", raw_text="los costos no coinciden")

    save_intake_record("tenant_byid", first, base_dir=tmp_path)
    save_intake_record("tenant_byid", second, base_dir=tmp_path)

    found = load_intake_record_by_id("tenant_byid", second.intake_id, base_dir=tmp_path)
    assert found is not None
    assert isinstance(found, dict)
    assert found["intake_id"] == second.intake_id
    assert found["raw_input"] == "los costos no coinciden"


# ---------------------------------------------------------------------------
# 9. load_intake_record_by_id returns None when absent
# ---------------------------------------------------------------------------
def test_load_by_id_returns_none_when_absent(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_absent", raw_text="revisar margen bruto")
    save_intake_record("tenant_absent", record, base_dir=tmp_path)

    missing = load_intake_record_by_id("tenant_absent", "intake_does_not_exist", base_dir=tmp_path)
    assert missing is None


# ---------------------------------------------------------------------------
# 10. Empty tenant_id raises on save
# ---------------------------------------------------------------------------
def test_empty_tenant_id_raises_on_save(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_ok", raw_text="texto cualquiera")

    with pytest.raises(ValueError, match="tenant_id"):
        save_intake_record("", record, base_dir=tmp_path)


def test_whitespace_tenant_id_raises_on_save(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_ok", raw_text="texto cualquiera")

    with pytest.raises(ValueError, match="tenant_id"):
        save_intake_record("   ", record, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 11. Empty tenant_id raises on load
# ---------------------------------------------------------------------------
def test_empty_tenant_id_raises_on_load(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        load_intake_records("", base_dir=tmp_path)


def test_whitespace_tenant_id_raises_on_load(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        load_intake_records("   ", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 12. Empty intake_id raises on lookup
# ---------------------------------------------------------------------------
def test_empty_intake_id_raises_on_lookup(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="intake_id"):
        load_intake_record_by_id("tenant_any", "", base_dir=tmp_path)


def test_whitespace_intake_id_raises_on_lookup(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="intake_id"):
        load_intake_record_by_id("tenant_any", "   ", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 13. Tenant mismatch raises
# ---------------------------------------------------------------------------
def test_tenant_mismatch_raises(tmp_path: Path) -> None:
    """save_intake_record debe validar que record.tenant_id == tenant_id argumento."""
    record = create_intake_record(tenant_id="tenant_real", raw_text="revisar costos")

    with pytest.raises(ValueError, match="does not match"):
        save_intake_record("otro_tenant", record, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 14. Missing required field raises
# ---------------------------------------------------------------------------
def test_missing_required_field_raises(tmp_path: Path) -> None:
    """save_intake_record debe validar campos core requeridos."""
    incomplete = {
        "intake_id": "intake_broken",
        "tenant_id": "tenant_incomplete",
        # falta raw_input y todos los demás campos core
    }

    with pytest.raises(ValueError, match="missing required field"):
        save_intake_record("tenant_incomplete", incomplete, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 15. Malformed JSON line raises
# ---------------------------------------------------------------------------
def test_malformed_json_line_raises(tmp_path: Path) -> None:
    tenant_dir = tmp_path / "tenant_malformed"
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "evidence").mkdir()
    (tenant_dir / "reports").mkdir()
    (tenant_dir / "results").mkdir()
    (tenant_dir / "receptions.jsonl").write_text("", encoding="utf-8")
    (tenant_dir / "intakes.jsonl").write_text(
        "{not valid json at all\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="malformed JSON"):
        load_intake_records("tenant_malformed", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 16. Non-dict JSON line raises
# ---------------------------------------------------------------------------
def test_non_dict_json_line_raises(tmp_path: Path) -> None:
    """Si una línea es JSON válido pero no dict (ej: lista), debe fallar."""
    tenant_dir = tmp_path / "tenant_nondict"
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "evidence").mkdir()
    (tenant_dir / "reports").mkdir()
    (tenant_dir / "results").mkdir()
    (tenant_dir / "receptions.jsonl").write_text("", encoding="utf-8")
    (tenant_dir / "intakes.jsonl").write_text(
        "[1, 2, 3]\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="not a dict"):
        load_intake_records("tenant_nondict", base_dir=tmp_path)


# ---------------------------------------------------------------------------
# 17. JSON line is valid JSON
# ---------------------------------------------------------------------------
def test_json_line_is_valid_json(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_valid",
        raw_text="quiero revisar márgenes de productos",
    )
    result_path = save_intake_record("tenant_valid", record, base_dir=tmp_path)

    lines = result_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    for line in lines:
        obj = json.loads(line)
        assert isinstance(obj, dict)
        assert "intake_id" in obj
        assert "tenant_id" in obj
        assert "raw_input" in obj


# ---------------------------------------------------------------------------
# 18. No cross-tenant reads
# ---------------------------------------------------------------------------
def test_no_cross_tenant_reads(tmp_path: Path) -> None:
    rec_a = create_intake_record(tenant_id="tenant_a", raw_text="costos fijos altos")
    rec_b = create_intake_record(tenant_id="tenant_b", raw_text="stock inconsistente")

    save_intake_record("tenant_a", rec_a, base_dir=tmp_path)
    save_intake_record("tenant_b", rec_b, base_dir=tmp_path)

    loaded_a = load_intake_records("tenant_a", base_dir=tmp_path)
    loaded_b = load_intake_records("tenant_b", base_dir=tmp_path)

    assert len(loaded_a) == 1
    assert loaded_a[0]["tenant_id"] == "tenant_a"
    assert loaded_a[0]["intake_id"] == rec_a.intake_id

    assert len(loaded_b) == 1
    assert loaded_b[0]["tenant_id"] == "tenant_b"
    assert loaded_b[0]["intake_id"] == rec_b.intake_id


# ---------------------------------------------------------------------------
# 19. Existing test_storage.py remains untouched (verified externally)
# ---------------------------------------------------------------------------
def test_existing_storage_layout_not_broken(tmp_path: Path) -> None:
    """save_intake_record debe crear el layout estándar de tenant sin romper
    evidence/, reports/, results/, receptions.jsonl."""
    record = create_intake_record(
        tenant_id="tenant_layout",
        raw_text="necesito ayuda con proveedores",
    )
    save_intake_record("tenant_layout", record, base_dir=tmp_path)

    tenant_root = tmp_path / "tenant_layout"
    assert tenant_root.is_dir()
    assert (tenant_root / "evidence").is_dir()
    assert (tenant_root / "reports").is_dir()
    assert (tenant_root / "results").is_dir()
    assert (tenant_root / "receptions.jsonl").exists()
    assert (tenant_root / "intakes.jsonl").exists()

    # receptions.jsonl debe seguir vacío (no escribimos reception)
    receptions_content = (tenant_root / "receptions.jsonl").read_text(encoding="utf-8")
    assert receptions_content.strip() == ""


# ---------------------------------------------------------------------------
# Extra: record missing tenant_id field
# ---------------------------------------------------------------------------
def test_record_missing_tenant_id_field_raises(tmp_path: Path) -> None:
    """save_intake_record debe validar que record tiene campo tenant_id."""
    incomplete = {
        "intake_id": "intake_no_tenant",
        # falta tenant_id
        "raw_input": "texto",
        "structured_selectors": {},
        "interrogation_result": {},
        "tank_selection_result": {},
        "evidence_requests": [],
        "intake_state": "RECEIVED",
        "suggested_next_state": "BLOCKED",
        "warnings": [],
        "audit_notes": [],
        "created_at": "2026-01-01T00:00:00Z",
    }

    with pytest.raises(ValueError, match="missing tenant_id field"):
        save_intake_record("tenant_any", incomplete, base_dir=tmp_path)


# ---------------------------------------------------------------------------
# Extra: base_dir is required
# ---------------------------------------------------------------------------
def test_base_dir_required_on_save(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_base", raw_text="texto")

    with pytest.raises(ValueError, match="base_dir is required"):
        save_intake_record("tenant_base", record, base_dir=None)


def test_base_dir_required_on_load(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="base_dir is required"):
        load_intake_records("tenant_base", base_dir=None)


def test_base_dir_required_on_load_by_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="base_dir is required"):
        load_intake_record_by_id("tenant_base", "intake_id", base_dir=None)
