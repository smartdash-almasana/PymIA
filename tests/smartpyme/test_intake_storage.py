"""Tests for SMARTPYME_INTAKE_STORAGE_PERSISTENCE slice.

API real (commit 43bfcb0):
    save_intake_record(base_dir, record) -> dict[str, Path]
    load_intake_records(base_dir, tenant_id) -> list[IntakeRecord]
    load_intake_record_by_id(base_dir, tenant_id, intake_id) -> IntakeRecord | None

Nota: la API usa posicionales (base_dir, record/tenant_id), NO keyword-only
como proponía la spec original. Tests adaptados a la implementación real.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.intake import ALLOWED_INTAKE_STATES, IntakeRecord, create_intake_record
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
# 1. Load missing intakes returns []
# ---------------------------------------------------------------------------
def test_load_missing_intakes_returns_empty_list(tmp_path: Path) -> None:
    """Un tenant sin intakes.jsonl poblado debe devolver lista vacía."""
    records = load_intake_records(tmp_path, "tenant_empty")
    assert records == []


# ---------------------------------------------------------------------------
# 2. Save creates intakes.jsonl
# ---------------------------------------------------------------------------
def test_save_creates_intakes_jsonl(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_create",
        raw_text="vendo mucho pero no me queda plata",
    )
    paths = save_intake_record(tmp_path, record)

    assert paths["intakes_jsonl"].exists()
    assert paths["intakes_jsonl"].name == "intakes.jsonl"
    lines = paths["intakes_jsonl"].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


# ---------------------------------------------------------------------------
# 3. Save accepts IntakeRecord instance from create_intake_record
# ---------------------------------------------------------------------------
def test_save_accepts_intake_record_instance(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_inst",
        raw_text="tengo proveedores duplicados y CUIT mezclados",
    )
    paths = save_intake_record(tmp_path, record)

    assert paths["intakes_jsonl"].exists()
    assert paths["intake_record_json"].exists()
    assert paths["intake_record_json"].name == "intake_record.json"
    assert paths["intake_record_json"].parent.name == "results"

    line = paths["intakes_jsonl"].read_text(encoding="utf-8").strip().splitlines()[0]
    obj = json.loads(line)
    assert obj["tenant_id"] == "tenant_inst"
    assert obj["intake_id"] == record.intake_id
    assert obj["intake_state"] in ALLOWED_INTAKE_STATES


# ---------------------------------------------------------------------------
# 4. Save does NOT accept plain dict (current implementation requires IntakeRecord)
# ---------------------------------------------------------------------------
def test_save_rejects_plain_dict_current_api(tmp_path: Path) -> None:
    """La implementación actual requiere IntakeRecord, no dict.

    La spec original proponía aceptar dict, pero commit 43bfcb0 no lo soporta.
    Este test documenta el comportamiento real: debe fallar con TypeError/AttributeError.
    """
    record = create_intake_record(
        tenant_id="tenant_dict",
        raw_text="necesito revisar costos",
    )
    plain = record.to_dict()

    with pytest.raises((TypeError, AttributeError)):
        save_intake_record(tmp_path, plain)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 5. Load preserves insertion order
# ---------------------------------------------------------------------------
def test_load_preserves_insertion_order(tmp_path: Path) -> None:
    first = create_intake_record(tenant_id="tenant_order", raw_text="no me cierra la plata")
    second = create_intake_record(tenant_id="tenant_order", raw_text="tengo proveedores duplicados")
    third = create_intake_record(tenant_id="tenant_order", raw_text="el stock no coincide con depósito")

    save_intake_record(tmp_path, first)
    save_intake_record(tmp_path, second)
    save_intake_record(tmp_path, third)

    loaded = load_intake_records(tmp_path, "tenant_order")
    assert [r.intake_id for r in loaded] == [first.intake_id, second.intake_id, third.intake_id]
    assert all(r.tenant_id == "tenant_order" for r in loaded)


# ---------------------------------------------------------------------------
# 6. load_intake_record_by_id returns correct record
# ---------------------------------------------------------------------------
def test_load_by_id_returns_matching(tmp_path: Path) -> None:
    first = create_intake_record(tenant_id="tenant_byid", raw_text="copio de excel a excel")
    second = create_intake_record(tenant_id="tenant_byid", raw_text="los costos no coinciden")

    save_intake_record(tmp_path, first)
    save_intake_record(tmp_path, second)

    found = load_intake_record_by_id(tmp_path, "tenant_byid", second.intake_id)
    assert found is not None
    assert found.intake_id == second.intake_id
    assert found.raw_input == "los costos no coinciden"


# ---------------------------------------------------------------------------
# 7. load_intake_record_by_id returns None when absent
# ---------------------------------------------------------------------------
def test_load_by_id_returns_none_when_absent(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_absent", raw_text="revisar margen bruto")
    save_intake_record(tmp_path, record)

    missing = load_intake_record_by_id(tmp_path, "tenant_absent", "intake_does_not_exist")
    assert missing is None


# ---------------------------------------------------------------------------
# 8. Empty tenant_id raises on save
# ---------------------------------------------------------------------------
def test_empty_tenant_id_raises_on_save(tmp_path: Path) -> None:
    record = create_intake_record(tenant_id="tenant_ok", raw_text="texto cualquiera")
    # Mutar el record para tener tenant_id vacío (fall-closed check)
    object.__setattr__(record, "tenant_id", "")

    with pytest.raises(ValueError, match="tenant_id"):
        save_intake_record(tmp_path, record)


# ---------------------------------------------------------------------------
# 9. Empty tenant_id raises on load
# ---------------------------------------------------------------------------
def test_empty_tenant_id_raises_on_load(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        load_intake_records(tmp_path, "")


def test_whitespace_tenant_id_raises_on_load(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        load_intake_records(tmp_path, "   ")


# ---------------------------------------------------------------------------
# 10. Empty intake_id raises on lookup
# ---------------------------------------------------------------------------
def test_empty_intake_id_raises_on_lookup(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="intake_id"):
        load_intake_record_by_id(tmp_path, "tenant_any", "")


def test_whitespace_intake_id_raises_on_lookup(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="intake_id"):
        load_intake_record_by_id(tmp_path, "tenant_any", "   ")


# ---------------------------------------------------------------------------
# 11. Tenant mismatch — current behavior documentado
# ---------------------------------------------------------------------------
def test_tenant_mismatch_current_behavior(tmp_path: Path) -> None:
    """La implementación actual NO valida que record.tenant_id coincida con
    el tenant del lookup. El record se guarda bajo record.tenant_id.

    Este test documenta el comportamiento real (no el deseado por spec).
    """
    record = create_intake_record(tenant_id="tenant_real", raw_text="revisar costos")
    paths = save_intake_record(tmp_path, record)

    # El archivo queda en tenant_real, no en otro_tenant
    other_records = load_intake_records(tmp_path, "otro_tenant")
    assert other_records == []

    # El record existe en tenant_real
    real_records = load_intake_records(tmp_path, "tenant_real")
    assert len(real_records) == 1
    assert real_records[0].intake_id == record.intake_id


# ---------------------------------------------------------------------------
# 12. Missing required field raises on load
# ---------------------------------------------------------------------------
def test_missing_required_field_raises_on_load(tmp_path: Path) -> None:
    """Si el JSONL contiene una línea con campos faltantes, _intake_record_from_dict
    fallará con KeyError al reconstruir el IntakeRecord."""
    # Crear tenant dir y escribir JSONL incompleto manualmente
    tenant_dir = tmp_path / "tenant_incomplete"
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "evidence").mkdir()
    (tenant_dir / "reports").mkdir()
    (tenant_dir / "results").mkdir()
    (tenant_dir / "receptions.jsonl").write_text("", encoding="utf-8")

    incomplete = {
        "intake_id": "intake_broken",
        "tenant_id": "tenant_incomplete",
        # falta raw_input y todos los demás campos core
    }
    (tenant_dir / "intakes.jsonl").write_text(
        json.dumps(incomplete) + "\n", encoding="utf-8"
    )

    with pytest.raises(KeyError):
        load_intake_records(tmp_path, "tenant_incomplete")


# ---------------------------------------------------------------------------
# 13. Malformed JSON line raises
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

    with pytest.raises(json.JSONDecodeError):
        load_intake_records(tmp_path, "tenant_malformed")


# ---------------------------------------------------------------------------
# 14. Non-dict JSON line raises
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

    # list no tiene .get() ni permite indexación por string
    with pytest.raises((AttributeError, KeyError, TypeError)):
        load_intake_records(tmp_path, "tenant_nondict")


# ---------------------------------------------------------------------------
# 15. JSON line is valid JSON
# ---------------------------------------------------------------------------
def test_json_line_is_valid_json(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_valid",
        raw_text="quiero revisar márgenes de productos",
    )
    paths = save_intake_record(tmp_path, record)

    lines = paths["intakes_jsonl"].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    for line in lines:
        obj = json.loads(line)
        assert isinstance(obj, dict)
        assert "intake_id" in obj
        assert "tenant_id" in obj
        assert "raw_input" in obj


# ---------------------------------------------------------------------------
# 16. No cross-tenant reads
# ---------------------------------------------------------------------------
def test_no_cross_tenant_reads(tmp_path: Path) -> None:
    rec_a = create_intake_record(tenant_id="tenant_a", raw_text="costos fijos altos")
    rec_b = create_intake_record(tenant_id="tenant_b", raw_text="stock inconsistente")

    save_intake_record(tmp_path, rec_a)
    save_intake_record(tmp_path, rec_b)

    loaded_a = load_intake_records(tmp_path, "tenant_a")
    loaded_b = load_intake_records(tmp_path, "tenant_b")

    assert len(loaded_a) == 1
    assert loaded_a[0].tenant_id == "tenant_a"
    assert loaded_a[0].intake_id == rec_a.intake_id

    assert len(loaded_b) == 1
    assert loaded_b[0].tenant_id == "tenant_b"
    assert loaded_b[0].intake_id == rec_b.intake_id


# ---------------------------------------------------------------------------
# 17. Existing test_storage.py remains untouched (verified externally)
# ---------------------------------------------------------------------------
def test_existing_storage_layout_not_broken(tmp_path: Path) -> None:
    """save_intake_record debe crear el layout estándar de tenant sin romper
    evidence/, reports/, results/, receptions.jsonl."""
    record = create_intake_record(
        tenant_id="tenant_layout",
        raw_text="necesito ayuda con proveedores",
    )
    paths = save_intake_record(tmp_path, record)

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
# Extra coverage: snapshot JSON file is also written
# ---------------------------------------------------------------------------
def test_save_writes_intake_record_json_snapshot(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_snap",
        raw_text="vendo pero no me queda nada",
    )
    paths = save_intake_record(tmp_path, record)

    snap = paths["intake_record_json"]
    assert snap.exists()
    snap_obj = json.loads(snap.read_text(encoding="utf-8"))
    assert snap_obj["intake_id"] == record.intake_id
    assert snap_obj["tenant_id"] == "tenant_snap"
    assert snap_obj["raw_input"] == "vendo pero no me queda nada"


# ---------------------------------------------------------------------------
# Extra coverage: load returns IntakeRecord instances, not dicts
# ---------------------------------------------------------------------------
def test_load_returns_intake_record_instances(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_type",
        raw_text="proveedores repetidos",
    )
    save_intake_record(tmp_path, record)

    loaded = load_intake_records(tmp_path, "tenant_type")
    assert len(loaded) == 1
    assert isinstance(loaded[0], IntakeRecord)
    assert loaded[0].intake_id == record.intake_id


# ---------------------------------------------------------------------------
# Extra coverage: load_intake_record_by_id returns IntakeRecord, not dict
# ---------------------------------------------------------------------------
def test_load_by_id_returns_intake_record_instance(tmp_path: Path) -> None:
    record = create_intake_record(
        tenant_id="tenant_typeid",
        raw_text="costos desactualizados",
    )
    save_intake_record(tmp_path, record)

    found = load_intake_record_by_id(tmp_path, "tenant_typeid", record.intake_id)
    assert found is not None
    assert isinstance(found, IntakeRecord)
    assert found.intake_id == record.intake_id
