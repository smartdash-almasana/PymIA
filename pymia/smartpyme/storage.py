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
    for d in (tenant_root, evidence_dir, reports_dir, results_dir):
        d.mkdir(parents=True, exist_ok=True)
    for jsonl in (receptions_jsonl, intakes_jsonl):
        if not jsonl.exists():
            jsonl.write_text("", encoding="utf-8")
    return {
        "tenant_root": tenant_root,
        "evidence_dir": evidence_dir,
        "reports_dir": reports_dir,
        "results_dir": results_dir,
        "receptions_jsonl": receptions_jsonl,
        "intakes_jsonl": intakes_jsonl,
    }


def _write_jsonl_line(target: Path, payload: dict[str, Any]) -> Path:
    line = json.dumps(payload, ensure_ascii=False)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return target


def append_reception_jsonl(base_dir: str | Path, record: ReceptionRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    return _write_jsonl_line(paths["receptions_jsonl"], asdict(record))


def append_intake_jsonl(base_dir: str | Path, record: IntakeRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    return _write_jsonl_line(paths["intakes_jsonl"], record.to_dict())


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
