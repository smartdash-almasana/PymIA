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


def save_intake_record(base_dir: str | Path, record: IntakeRecord) -> dict[str, Path]:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    append_intake_jsonl(base_dir, record)
    intake_result_path = write_result_intake(base_dir, record)
    return {
        "intakes_jsonl": paths["intakes_jsonl"],
        "intake_record_json": intake_result_path,
    }


def _intake_record_from_dict(payload: dict[str, Any]) -> IntakeRecord:
    evidence_requests = [
        IntakeEvidenceRequest(**e)
        for e in payload.get("evidence_requests", [])
    ]
    return IntakeRecord(
        intake_id=payload["intake_id"],
        tenant_id=payload["tenant_id"],
        raw_input=payload["raw_input"],
        structured_selectors=payload.get("structured_selectors", {}),
        interrogation_result=payload.get("interrogation_result", {}),
        tank_selection_result=payload.get("tank_selection_result", {}),
        evidence_requests=evidence_requests,
        intake_state=payload["intake_state"],
        suggested_next_state=payload["suggested_next_state"],
        warnings=payload.get("warnings", []),
        audit_notes=payload.get("audit_notes", []),
        created_at=payload["created_at"],
    )


def load_intake_records(base_dir: str | Path, tenant_id: str) -> list[IntakeRecord]:
    paths = ensure_tenant_storage(base_dir, tenant_id)
    rows = paths["intakes_jsonl"].read_text(encoding="utf-8").splitlines()
    if not rows:
        return []
    return [_intake_record_from_dict(json.loads(row)) for row in rows if row.strip()]


def load_intake_record_by_id(base_dir: str | Path, tenant_id: str, intake_id: str) -> IntakeRecord | None:
    if not intake_id.strip():
        raise ValueError("intake_id is required")
    records = load_intake_records(base_dir, tenant_id)
    for record in records:
        if record.intake_id == intake_id:
            return record
    return None


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
