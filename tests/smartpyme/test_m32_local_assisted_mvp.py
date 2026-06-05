from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.local_assisted_mvp import main, run_local_assisted_mvp


ROOT = Path(__file__).resolve().parents[2]
SIMPLE_XLSX = ROOT / "prueba_excels" / "simple_bem_test.xlsx"
TEXTIL_XLSX = ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def test_m32_local_assisted_mvp_generates_minimum_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "m32-simple"

    summary = run_local_assisted_mvp(
        excel_path=SIMPLE_XLSX,
        tenant_id="m32-simple-demo",
        output_dir=out,
    )

    assert summary["ok"] is True
    assert summary["status"] in {"DELIVERED", "PARTIAL"}
    assert summary["tenant_id"] == "m32-simple-demo"
    assert summary["elapsed_seconds"] >= 0

    expected_files = [
        "run_summary.json",
        "report.md",
        "evidence.json",
        "curation.json",
        "narrative_report.json",
        "grounding.json",
    ]
    for filename in expected_files:
        assert (out / filename).exists(), filename

    report = (out / "report.md").read_text(encoding="utf-8")
    assert "SmartPyme" in report
    assert "Qué se pudo observar" in report
    assert "No-promesas" in report

    run_summary = json.loads((out / "run_summary.json").read_text(encoding="utf-8"))
    assert run_summary["ok"] is True
    assert run_summary["artifacts"]["report_md"].endswith("report.md")


def test_m32_local_assisted_mvp_handles_missing_file(tmp_path: Path) -> None:
    out = tmp_path / "missing"

    summary = run_local_assisted_mvp(
        excel_path=tmp_path / "missing.xlsx",
        tenant_id="m32-missing-demo",
        output_dir=out,
    )

    assert summary["ok"] is False
    assert summary["status"] == "FILE_NOT_FOUND"
    assert "Excel file not found" in summary["error"]
    assert (out / "run_summary.json").exists()


def test_m32_local_assisted_mvp_cli_returns_zero_for_valid_fixture(tmp_path: Path) -> None:
    out = tmp_path / "m32-cli"

    ret = main(
        [
            "--excel",
            str(TEXTIL_XLSX),
            "--tenant-id",
            "m32-cli-demo",
            "--out",
            str(out),
        ]
    )

    assert ret == 0
    assert (out / "report.md").exists()
    assert (out / "run_summary.json").exists()
