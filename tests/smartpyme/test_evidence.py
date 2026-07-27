"""Tests para el contrato mínimo de EvidenceRecord (SMARTPYME_EVIDENCE_RECORD_MINIMAL)."""
from __future__ import annotations

import json

import pytest

from pymia.smartpyme.evidence import (
    ALLOWED_EVIDENCE_STATUSES,
    ALLOWED_SOURCE_KINDS,
    EVIDENCE_STATUS_LINKED,
    EVIDENCE_STATUS_RECEIVED,
    EVIDENCE_STATUS_REGISTERED,
    EVIDENCE_STATUS_REJECTED,
    EVIDENCE_STATUS_SUPERSEDED,
    EvidenceRecord,
    SOURCE_KIND_EXTERNAL_REF,
    SOURCE_KIND_GENERATED,
    SOURCE_KIND_MANUAL_TEXT,
    SOURCE_KIND_UNKNOWN,
    SOURCE_KIND_UPLOADED_FILE,
    create_evidence_record,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _minimal_kwargs(**overrides) -> dict:
    base = dict(
        tenant_id="t-001",
        intake_id="intake-abc",
        evidence_type="excel_proveedores",
        source_kind=SOURCE_KIND_UPLOADED_FILE,
        source_ref="/tmp/proveedores.xlsx",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. create_evidence_record minimal
# ---------------------------------------------------------------------------
def test_create_evidence_record_minimal():
    record = create_evidence_record(**_minimal_kwargs())

    assert isinstance(record, EvidenceRecord)
    assert record.evidence_id.startswith("evidence_")
    assert len(record.evidence_id) > len("evidence_")
    assert record.tenant_id == "t-001"
    assert record.intake_id == "intake-abc"
    assert record.evidence_type == "excel_proveedores"
    assert record.source_kind == SOURCE_KIND_UPLOADED_FILE
    assert record.source_ref == "/tmp/proveedores.xlsx"
    # default
    assert record.status == EVIDENCE_STATUS_RECEIVED
    assert record.request_id is None
    assert record.original_filename is None
    assert record.mime_type is None
    assert record.size_bytes is None
    assert record.content_hash is None
    assert record.notes == []
    assert record.metadata == {}
    assert isinstance(record.received_at, str) and len(record.received_at) > 0


# ---------------------------------------------------------------------------
# 2. to_dict serializable
# ---------------------------------------------------------------------------
def test_to_dict_is_json_serializable():
    record = create_evidence_record(
        **_minimal_kwargs(
            notes=["nota1", "nota2"],
            metadata={"k": "v", "n": 1, "nested": {"a": True}},
        )
    )
    d = record.to_dict()
    assert isinstance(d, dict)
    # JSON-serializable sin encoder custom
    serialized = json.dumps(d)
    roundtrip = json.loads(serialized)
    assert roundtrip["tenant_id"] == "t-001"
    assert roundtrip["notes"] == ["nota1", "nota2"]
    assert roundtrip["metadata"]["nested"]["a"] is True


# ---------------------------------------------------------------------------
# 3-7. Validaciones fail-closed de campos requeridos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "field_name,bad_value",
    [
        ("tenant_id", ""),
        ("tenant_id", "   "),
        ("intake_id", ""),
        ("intake_id", "   "),
        ("evidence_type", ""),
        ("source_kind", ""),
        ("source_ref", ""),
    ],
)
def test_empty_required_fields_raise(field_name, bad_value):
    kwargs = _minimal_kwargs(**{field_name: bad_value})
    with pytest.raises(ValueError):
        create_evidence_record(**kwargs)


def test_empty_tenant_id_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(tenant_id=""))


def test_empty_intake_id_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(intake_id=""))


def test_empty_evidence_type_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(evidence_type=""))


def test_empty_source_kind_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(source_kind=""))


def test_empty_source_ref_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(source_ref=""))


# ---------------------------------------------------------------------------
# 8. source_kind inválido
# ---------------------------------------------------------------------------
def test_invalid_source_kind_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(source_kind="magic_portal"))


# ---------------------------------------------------------------------------
# 9. status inválido
# ---------------------------------------------------------------------------
def test_invalid_status_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(status="MAGICAL"))


# ---------------------------------------------------------------------------
# 10. size_bytes negativo
# ---------------------------------------------------------------------------
def test_negative_size_bytes_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(size_bytes=-1))


def test_zero_size_bytes_allowed():
    record = create_evidence_record(**_minimal_kwargs(size_bytes=0))
    assert record.size_bytes == 0


def test_non_int_size_bytes_raises():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(size_bytes="1024"))


def test_bool_size_bytes_raises():
    # bool es subclase de int pero no debe aceptarse como size
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(size_bytes=True))


# ---------------------------------------------------------------------------
# 11. notes debe ser list
# ---------------------------------------------------------------------------
def test_notes_must_be_list():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(notes="nota suelta"))

    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(notes={"k": "v"}))


# ---------------------------------------------------------------------------
# 12. metadata debe ser dict
# ---------------------------------------------------------------------------
def test_metadata_must_be_dict():
    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(metadata=["no"]))

    with pytest.raises(ValueError):
        create_evidence_record(**_minimal_kwargs(metadata="k=v"))


# ---------------------------------------------------------------------------
# 13. notes are copied, not mutated
# ---------------------------------------------------------------------------
def test_notes_are_copied_not_mutated():
    original = ["nota inicial"]
    record = create_evidence_record(**_minimal_kwargs(notes=original))

    assert record.notes == ["nota inicial"]
    assert record.notes is not original

    # mutar la entrada no afecta al record
    original.append("extra")
    assert record.notes == ["nota inicial"]

    # mutar el record no afecta a la entrada original
    record.notes.append("intruso")
    assert original == ["nota inicial", "extra"]


# ---------------------------------------------------------------------------
# 14. metadata is copied, not mutated
# ---------------------------------------------------------------------------
def test_metadata_is_copied_not_mutated():
    original = {"a": 1}
    record = create_evidence_record(**_minimal_kwargs(metadata=original))

    assert record.metadata == {"a": 1}
    assert record.metadata is not original

    original["b"] = 2
    assert "b" not in record.metadata

    record.metadata["c"] = 3
    assert "c" not in original


# ---------------------------------------------------------------------------
# 15. request_id optional
# ---------------------------------------------------------------------------
def test_request_id_optional():
    without = create_evidence_record(**_minimal_kwargs())
    assert without.request_id is None

    with_id = create_evidence_record(**_minimal_kwargs(request_id="req-42"))
    assert with_id.request_id == "req-42"


# ---------------------------------------------------------------------------
# 16. file metadata optional
# ---------------------------------------------------------------------------
def test_file_metadata_optional():
    record = create_evidence_record(**_minimal_kwargs())
    assert record.original_filename is None
    assert record.mime_type is None
    assert record.size_bytes is None
    assert record.content_hash is None

    full = create_evidence_record(
        **_minimal_kwargs(
            original_filename="proveedores.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size_bytes=12345,
            content_hash="sha256:abc123",
        )
    )
    assert full.original_filename == "proveedores.xlsx"
    assert full.size_bytes == 12345
    assert full.content_hash == "sha256:abc123"


# ---------------------------------------------------------------------------
# 17-19. Source kinds permitidos
# ---------------------------------------------------------------------------
def test_uploaded_file_source_kind_allowed():
    record = create_evidence_record(**_minimal_kwargs(source_kind=SOURCE_KIND_UPLOADED_FILE))
    assert record.source_kind == SOURCE_KIND_UPLOADED_FILE


def test_manual_text_source_kind_allowed():
    record = create_evidence_record(
        **_minimal_kwargs(
            source_kind=SOURCE_KIND_MANUAL_TEXT,
            source_ref="inline://usuario-mensaje-123",
        )
    )
    assert record.source_kind == SOURCE_KIND_MANUAL_TEXT


def test_external_ref_source_kind_allowed():
    record = create_evidence_record(
        **_minimal_kwargs(
            source_kind=SOURCE_KIND_EXTERNAL_REF,
            source_ref="https://drive.example.com/file/xyz",
        )
    )
    assert record.source_kind == SOURCE_KIND_EXTERNAL_REF


def test_generated_source_kind_allowed():
    record = create_evidence_record(
        **_minimal_kwargs(
            source_kind=SOURCE_KIND_GENERATED,
            source_ref="generated://diagnostic_report.json",
        )
    )
    assert record.source_kind == SOURCE_KIND_GENERATED


def test_unknown_source_kind_allowed():
    record = create_evidence_record(**_minimal_kwargs(source_kind=SOURCE_KIND_UNKNOWN))
    assert record.source_kind == SOURCE_KIND_UNKNOWN


# ---------------------------------------------------------------------------
# 20. Import smoke
# ---------------------------------------------------------------------------
def test_import_smoke():
    from pymia.smartpyme.evidence import EvidenceRecord, create_evidence_record  # noqa: F401


# ---------------------------------------------------------------------------
# Cobertura extra: estados y constantes
# ---------------------------------------------------------------------------
def test_allowed_statuses_cover_all_exports():
    assert EVIDENCE_STATUS_RECEIVED in ALLOWED_EVIDENCE_STATUSES
    assert EVIDENCE_STATUS_REGISTERED in ALLOWED_EVIDENCE_STATUSES
    assert EVIDENCE_STATUS_REJECTED in ALLOWED_EVIDENCE_STATUSES
    assert EVIDENCE_STATUS_LINKED in ALLOWED_EVIDENCE_STATUSES
    assert EVIDENCE_STATUS_SUPERSEDED in ALLOWED_EVIDENCE_STATUSES
    assert len(ALLOWED_EVIDENCE_STATUSES) == 5


def test_allowed_source_kinds_cover_all_exports():
    for kind in (
        SOURCE_KIND_UPLOADED_FILE,
        SOURCE_KIND_MANUAL_TEXT,
        SOURCE_KIND_EXTERNAL_REF,
        SOURCE_KIND_GENERATED,
        SOURCE_KIND_UNKNOWN,
    ):
        assert kind in ALLOWED_SOURCE_KINDS
    assert len(ALLOWED_SOURCE_KINDS) == 5


def test_status_can_be_overridden_to_registered():
    record = create_evidence_record(**_minimal_kwargs(status=EVIDENCE_STATUS_REGISTERED))
    assert record.status == EVIDENCE_STATUS_REGISTERED


def test_evidence_id_is_unique_per_call():
    a = create_evidence_record(**_minimal_kwargs())
    b = create_evidence_record(**_minimal_kwargs())
    assert a.evidence_id != b.evidence_id
    assert a.evidence_id.startswith("evidence_")
    assert b.evidence_id.startswith("evidence_")


def test_received_at_is_iso_format():
    record = create_evidence_record(**_minimal_kwargs())
    # ISO-8601 con timezone incluye '+' o 'Z' o formato estándar de datetime
    assert "T" in record.received_at
    # Debe ser parseable como datetime ISO
    from datetime import datetime
    parsed = datetime.fromisoformat(record.received_at)
    assert parsed.tzinfo is not None
