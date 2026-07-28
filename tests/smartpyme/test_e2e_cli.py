from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pymia.smartpyme.e2e_cli import run_e2e


def test_e2e_cli_flow_writes_outputs_and_storage(tmp_path: Path) -> None:
    input_file = tmp_path / "ventas.xlsx"
    out_dir = tmp_path / "out"
    storage_dir = tmp_path / "storage"

    df = pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 95},
            {"producto": "B", "ventas": 120, "costo": None},
        ]
    )
    df.to_excel(input_file, index=False)

    result = run_e2e(
        tenant_id="tenant_demo",
        message="No sé si vendo con margen",
        classification="margen",
        input_path=str(input_file),
        out_dir=str(out_dir),
        storage_dir=str(storage_dir),
    )

    assert result["tenant_id"] == "tenant_demo"
    assert result["status"] == "DELIVERED"
    assert result["findings_count"] >= 1

    report = out_dir / "diagnostic_report.md"
    diag_json = out_dir / "diagnostic_result.json"
    reception_json = out_dir / "reception_record.json"
    jsonl = storage_dir / "tenant_demo" / "receptions.jsonl"
    stored_reception = storage_dir / "tenant_demo" / "results" / "reception_record.json"

    assert report.exists()
    assert diag_json.exists()
    assert reception_json.exists()
    assert jsonl.exists()
    assert stored_reception.exists()

    reception = json.loads(reception_json.read_text(encoding="utf-8"))
    assert reception["tenant_id"] == "tenant_demo"
    assert reception["status"] == "DELIVERED"
