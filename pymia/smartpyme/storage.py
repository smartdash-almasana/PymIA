from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

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
    for d in (tenant_root, evidence_dir, reports_dir, results_dir):
        d.mkdir(parents=True, exist_ok=True)
    if not receptions_jsonl.exists():
        receptions_jsonl.write_text("", encoding="utf-8")
    return {
        "tenant_root": tenant_root,
        "evidence_dir": evidence_dir,
        "reports_dir": reports_dir,
        "results_dir": results_dir,
        "receptions_jsonl": receptions_jsonl,
    }


def append_reception_jsonl(base_dir: str | Path, record: ReceptionRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    line = json.dumps(asdict(record), ensure_ascii=False)
    with paths["receptions_jsonl"].open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return paths["receptions_jsonl"]


def write_result_reception(base_dir: str | Path, record: ReceptionRecord) -> Path:
    paths = ensure_tenant_storage(base_dir, record.tenant_id)
    target = paths["results_dir"] / "reception_record.json"
    target.write_text(json.dumps(asdict(record), indent=2, ensure_ascii=False), encoding="utf-8")
    return target
