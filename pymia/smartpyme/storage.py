from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pymia.smartpyme.intake import IntakeEvidenceRequest, IntakeRecord
from pymia.smartpyme.reception import ReceptionRecord


def _safe_join(base_dir: Path, tenant_id: str) -> Path:
    if not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if ".." in tenant_id or "/" in tenant_id or "\\" in tenant_id:
        raise ValueError("tenant_id contains invalid path traversal markers")
    target = (base_dir / tenant_id).resolve()
    base = base_dir.resolve()
    if base not in target.parents and target != base:
        raise ValueError("resolved path escapes base_dir")
    return target


def ensure_tenant_storage(base_dir: str | Path, tenant_id: str) -> dict[str, Path]:
    base = Path(base_dir).resolve()
    tenant_root = _safe_join(base, tenant_id)
    evidence_dir = tenant_root / "evidence"
    reports_dir = tenant_root / "reports"
    results_dir = tenant_root / "results"
    receptions_jsonl = tenant_root / "receptions.jsonl"
    intakes_jsonl = tenant_root / "intakes.jsonl"
    anamnesis_jsonl = tenant_root / "anamnesis.jsonl"
    investigations_jsonl = tenant_root / "investigations.jsonl"
    owner_answers_jsonl = tenant_root / "owner_answers.jsonl"
    evidence_requests_jsonl = tenant_root / "evidence_requests.jsonl"
    evidences_jsonl = tenant_root / "evidences.jsonl"
    for d in (tenant_root, evidence_dir, reports_dir, results_dir):
        d.mkdir(parents=True, exist_ok=True)
    for jsonl in (
        receptions_jsonl,
        intakes_jsonl,
        anamnesis_jsonl,
        investigations_jsonl,
        owner_answers_jsonl,
        evidence_requests_jsonl,
        evidences_jsonl,
    ):
        if not jsonl.exists():
            jsonl.write_text("", encoding="utf-8")
    return {
        "tenant_root": tenant_root,
        "evidence_dir": evidence_dir,
        "reports_dir": reports_dir,
        "results_dir": results_dir,
        "receptions_jsonl": receptions_jsonl,
        "intakes_jsonl": intakes_jsonl,
        "anamnesis_jsonl": anamnesis_jsonl,
        "investigations_jsonl": investigations_jsonl,
        "owner_answers_jsonl": owner_answers_jsonl,
        "evidence_requests_jsonl": evidence_requests_jsonl,
        "evidences_jsonl": evidences_jsonl,
    }


def _write_jsonl_line(target: Path, payload: dict[str, Any]) -> Path:
    line = json.dumps(payload, ensure_ascii=False)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return target


def _record_to_dict(record: Any, *, record_name: str) -> dict[str, Any]:
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    if isinstance(record, dict):
        return record.copy()
    raise ValueError(f"{record_name} must be a supported record or dict")


def append_reception_jsonl(base_dir: str | Path, record: ReceptionRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    return _write_jsonl_line(paths["receptions_jsonl"], asdict(record))


def append_intake_jsonl(base_dir: str | Path, record: IntakeRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    return _write_jsonl_line(paths["intakes_jsonl"], record.to_dict())


def _save_record_jsonl(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None,
    target_key: str,
    required_fields: tuple[str, ...],
    list_fields: tuple[str, ...] = (),
    dict_fields: tuple[str, ...] = ("metadata",),
) -> Path:
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")
    if base_dir is None:
        raise ValueError("base_dir is required")
    record_dict = _record_to_dict(record, record_name="record")
    if record_dict.get("tenant_id") != tenant_id:
        if "tenant_id" not in record_dict:
            raise ValueError("record missing tenant_id field")
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match argument tenant_id ({tenant_id})"
        )
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")
    for field in list_fields:
        if not isinstance(record_dict[field], list):
            raise ValueError(f"field {field} must be list")
    for field in dict_fields:
        if not isinstance(record_dict[field], dict):
            raise ValueError(f"field {field} must be dict")
    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths[target_key], record_dict)


def save_anamnesis_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    return _save_record_jsonl(
        tenant_id,
        record,
        base_dir=base_dir,
        target_key="anamnesis_jsonl",
        required_fields=(
            "anamnesis_id", "tenant_id", "intake_id", "raw_owner_message",
            "business_taxonomy", "declared_pains", "owner_hypotheses",
            "declared_documents", "requested_documents", "status", "created_at", "metadata",
        ),
        list_fields=("declared_pains", "owner_hypotheses", "declared_documents", "requested_documents"),
        dict_fields=("business_taxonomy", "metadata"),
    )


def save_investigation_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    return _save_record_jsonl(
        tenant_id,
        record,
        base_dir=base_dir,
        target_key="investigations_jsonl",
        required_fields=(
            "investigation_id", "tenant_id", "intake_id", "anamnesis_id", "owner_prompt",
            "investigation_axis", "declared_question", "status", "evidence_required",
            "pathology_candidates", "formula_candidates", "created_at", "metadata",
        ),
        list_fields=("evidence_required", "pathology_candidates", "formula_candidates"),
    )


def save_owner_answer_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    return _save_record_jsonl(
        tenant_id,
        record,
        base_dir=base_dir,
        target_key="owner_answers_jsonl",
        required_fields=(
            "answer_id", "tenant_id", "intake_id", "anamnesis_id", "investigation_id",
            "question_ref", "raw_owner_answer", "answer_kind", "created_at", "metadata",
        ),
    )


def save_evidence_request_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    record_dict = _record_to_dict(record, record_name="record")
    if record_dict.get("owner_answer_id") is not None and not isinstance(record_dict["owner_answer_id"], str):
        raise ValueError("field owner_answer_id must be str or None")
    return _save_record_jsonl(
        tenant_id,
        record_dict,
        base_dir=base_dir,
        target_key="evidence_requests_jsonl",
        required_fields=(
            "request_id", "tenant_id", "intake_id", "anamnesis_id", "investigation_id",
            "owner_answer_id", "requested_evidence", "request_reason", "status", "created_at", "metadata",
        ),
        list_fields=("requested_evidence",),
    )


# ---------------------------------------------------------------------------
# Contrato aprobado: save_intake_record
# ---------------------------------------------------------------------------
def save_intake_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un IntakeRecord o dict en <base_dir>/<tenant_id>/intakes.jsonl.

    Contrato aprobado:
        save_intake_record(tenant_id, record, *, base_dir=None) -> Path

    Validaciones fail-closed:
        - tenant_id no vacío
        - record es IntakeRecord (con to_dict()) o dict
        - record["tenant_id"] existe
        - record["tenant_id"] == tenant_id
        - campos core requeridos presentes
        - tipos de campos core correctos
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if base_dir is None:
        raise ValueError("base_dir is required")

    # Convertir record a dict
    if hasattr(record, "to_dict") and callable(record.to_dict):
        record_dict = record.to_dict()
    elif isinstance(record, dict):
        record_dict = record.copy()
    else:
        raise ValueError("record must be IntakeRecord or dict")

    # Validar tenant_id en record
    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    # Validar campos core requeridos
    required_fields = [
        "intake_id",
        "tenant_id",
        "raw_input",
        "structured_selectors",
        "interrogation_result",
        "tank_selection_result",
        "evidence_requests",
        "intake_state",
        "suggested_next_state",
        "warnings",
        "audit_notes",
        "created_at",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    # Validar tipos de campos core
    dict_fields = ["structured_selectors", "interrogation_result", "tank_selection_result"]
    for field in dict_fields:
        if not isinstance(record_dict[field], dict):
            raise ValueError(f"field {field} must be dict")

    list_fields = ["evidence_requests", "warnings", "audit_notes"]
    for field in list_fields:
        if not isinstance(record_dict[field], list):
            raise ValueError(f"field {field} must be list")

    # Escribir JSONL
    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["intakes_jsonl"], record_dict)


# ---------------------------------------------------------------------------
# Contrato aprobado: load_intake_records
# ---------------------------------------------------------------------------
def load_intake_records(
    tenant_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]:
    """Carga todos los IntakeRecords de un tenant como list[dict].

    Contrato aprobado:
        load_intake_records(tenant_id, *, base_dir=None) -> list[dict]

    Comportamiento:
        - valida tenant_id no vacío
        - retorna [] si intakes.jsonl no existe
        - retorna list[dict] (no IntakeRecord)
        - preserva orden de inserción
        - ValueError en JSON malformado
        - ValueError en línea que no es dict
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if base_dir is None:
        raise ValueError("base_dir is required")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    intakes_jsonl = paths["intakes_jsonl"]

    if not intakes_jsonl.exists():
        return []

    content = intakes_jsonl.read_text(encoding="utf-8").strip()
    if not content:
        return []

    records: list[dict] = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"malformed JSON at line {line_num}") from e

        if not isinstance(obj, dict):
            raise ValueError(f"line {line_num} is not a dict")

        records.append(obj)

    return records


# ---------------------------------------------------------------------------
# Contrato aprobado: load_intake_record_by_id
# ---------------------------------------------------------------------------
def load_intake_record_by_id(
    tenant_id: str,
    intake_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict | None:
    """Busca un IntakeRecord por intake_id dentro de un tenant.

    Contrato aprobado:
        load_intake_record_by_id(tenant_id, intake_id, *, base_dir=None) -> dict | None

    Comportamiento:
        - valida tenant_id no vacío
        - valida intake_id no vacío
        - retorna dict si existe
        - retorna None si no existe
        - no cruza boundaries de tenant
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if not intake_id or not intake_id.strip():
        raise ValueError("intake_id is required")

    records = load_intake_records(tenant_id, base_dir=base_dir)
    for record in records:
        if record.get("intake_id") == intake_id:
            return record

    return None


# ---------------------------------------------------------------------------
# Contrato aprobado: save_evidence_record
# ---------------------------------------------------------------------------
def save_evidence_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
    """Persiste un EvidenceRecord o dict en <base_dir>/<tenant_id>/evidences.jsonl.

    Contrato aprobado:
        save_evidence_record(tenant_id, record, *, base_dir=None) -> Path

    Validaciones fail-closed:
        - tenant_id no vacío
        - record es EvidenceRecord (con to_dict()) o dict
        - record["tenant_id"] existe
        - record["tenant_id"] == tenant_id
        - campos core requeridos presentes
        - tipos de campos core correctos
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if base_dir is None:
        raise ValueError("base_dir is required")

    # Convertir record a dict
    if hasattr(record, "to_dict") and callable(record.to_dict):
        record_dict = record.to_dict()
    elif isinstance(record, dict):
        record_dict = record.copy()
    else:
        raise ValueError("record must be EvidenceRecord or dict")

    # Validar tenant_id en record
    if "tenant_id" not in record_dict:
        raise ValueError("record missing tenant_id field")
    if record_dict["tenant_id"] != tenant_id:
        raise ValueError(
            f"record tenant_id ({record_dict['tenant_id']}) does not match "
            f"argument tenant_id ({tenant_id})"
        )

    # Validar campos core requeridos
    required_fields = [
        "evidence_id",
        "tenant_id",
        "intake_id",
        "request_id",
        "evidence_type",
        "source_kind",
        "source_ref",
        "original_filename",
        "mime_type",
        "size_bytes",
        "content_hash",
        "status",
        "received_at",
        "notes",
        "metadata",
    ]
    for field in required_fields:
        if field not in record_dict:
            raise ValueError(f"record missing required field: {field}")

    # Validar tipos de campos core
    # notes: list, metadata: dict
    if not isinstance(record_dict["notes"], list):
        raise ValueError("field notes must be list")
    if not isinstance(record_dict["metadata"], dict):
        raise ValueError("field metadata must be dict")

    # size_bytes: int | None
    if record_dict["size_bytes"] is not None:
        if not isinstance(record_dict["size_bytes"], int) or isinstance(
            record_dict["size_bytes"], bool
        ):
            raise ValueError("field size_bytes must be int or None")

    # request_id, original_filename, mime_type, content_hash: str | None
    nullable_str_fields = [
        "request_id",
        "original_filename",
        "mime_type",
        "content_hash",
    ]
    for field in nullable_str_fields:
        if record_dict[field] is not None and not isinstance(record_dict[field], str):
            raise ValueError(f"field {field} must be str or None")

    # Escribir JSONL
    paths = ensure_tenant_storage(base_dir, tenant_id)
    return _write_jsonl_line(paths["evidences_jsonl"], record_dict)


# ---------------------------------------------------------------------------
# Contrato aprobado: load_evidence_records
# ---------------------------------------------------------------------------
def load_evidence_records(
    tenant_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]:
    """Carga todos los EvidenceRecords de un tenant como list[dict].

    Contrato aprobado:
        load_evidence_records(tenant_id, *, base_dir=None) -> list[dict]

    Comportamiento:
        - valida tenant_id no vacío
        - retorna [] si evidences.jsonl no existe
        - retorna list[dict] (no EvidenceRecord)
        - preserva orden de inserción
        - ValueError en JSON malformado
        - ValueError en línea que no es dict
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if base_dir is None:
        raise ValueError("base_dir is required")

    paths = ensure_tenant_storage(base_dir, tenant_id)
    evidences_jsonl = paths["evidences_jsonl"]

    if not evidences_jsonl.exists():
        return []

    content = evidences_jsonl.read_text(encoding="utf-8").strip()
    if not content:
        return []

    records: list[dict] = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"malformed JSON at line {line_num}") from e

        if not isinstance(obj, dict):
            raise ValueError(f"line {line_num} is not a dict")

        records.append(obj)

    return records


# ---------------------------------------------------------------------------
# Contrato aprobado: load_evidence_records_by_intake_id
# ---------------------------------------------------------------------------
def load_evidence_records_by_intake_id(
    tenant_id: str,
    intake_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]:
    """Filtra EvidenceRecords de un tenant por intake_id.

    Contrato aprobado:
        load_evidence_records_by_intake_id(tenant_id, intake_id, *, base_dir=None) -> list[dict]

    Comportamiento:
        - valida tenant_id no vacío
        - valida intake_id no vacío
        - retorna list[dict] filtrado
        - preserva orden
        - retorna [] si no hay matches
        - no cruza boundaries de tenant
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if not intake_id or not intake_id.strip():
        raise ValueError("intake_id is required")

    records = load_evidence_records(tenant_id, base_dir=base_dir)
    return [r for r in records if r.get("intake_id") == intake_id]


# ---------------------------------------------------------------------------
# Contrato aprobado: load_evidence_record_by_id
# ---------------------------------------------------------------------------
def load_evidence_record_by_id(
    tenant_id: str,
    evidence_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict | None:
    """Busca un EvidenceRecord por evidence_id dentro de un tenant.

    Contrato aprobado:
        load_evidence_record_by_id(tenant_id, evidence_id, *, base_dir=None) -> dict | None

    Comportamiento:
        - valida tenant_id no vacío
        - valida evidence_id no vacío
        - retorna dict si existe
        - retorna None si no existe
        - no cruza boundaries de tenant
    """
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required")

    if not evidence_id or not evidence_id.strip():
        raise ValueError("evidence_id is required")

    records = load_evidence_records(tenant_id, base_dir=base_dir)
    for record in records:
        if record.get("evidence_id") == evidence_id:
            return record

    return None


# ---------------------------------------------------------------------------
# Legacy functions (mantener compatibilidad)
# ---------------------------------------------------------------------------
def write_result_reception(base_dir: str | Path, record: ReceptionRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    target = paths["results_dir"] / "reception_record.json"
    target.write_text(json.dumps(asdict(record), indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def write_result_intake(base_dir: str | Path, record: IntakeRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    target = paths["results_dir"] / "intake_record.json"
    target.write_text(json.dumps(record.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return target
