from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.reception import create_reception
from pymia.smartpyme.storage import append_reception_jsonl, ensure_tenant_storage


def test_storage_layout_and_jsonl_append(tmp_path: Path) -> None:
    paths = ensure_tenant_storage(tmp_path, "tenant_a")
    assert paths["evidence_dir"].exists()
    assert paths["reports_dir"].exists()
    assert paths["results_dir"].exists()
    assert paths["receptions_jsonl"].exists()

    rec = create_reception(
        tenant_id="tenant_a",
        message="m",
        classification="margen",
        status="DELIVERED",
        evidence_refs=["in.xlsx"],
        output_refs=["out.md"],
    )
    jsonl = append_reception_jsonl(tmp_path, rec)
    lines = jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["tenant_id"] == "tenant_a"
    assert obj["status"] == "DELIVERED"


def test_storage_blocks_path_traversal(tmp_path: Path) -> None:
    try:
        ensure_tenant_storage(tmp_path, "../escape")
    except ValueError as exc:
        assert "path traversal" in str(exc) or "invalid" in str(exc)
    else:
        raise AssertionError("ValueError expected")
