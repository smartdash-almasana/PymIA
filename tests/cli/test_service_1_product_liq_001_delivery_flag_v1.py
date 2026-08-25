from __future__ import annotations

from pathlib import Path

from pymia.cli import service_1_product as cli
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    WorkbookSemanticStartRequestV1,
)


def test_entrypoint_forwards_explicit_delivery_request(tmp_path: Path, monkeypatch) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    received: dict = {}

    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        lambda **_: {
            "status": "NEEDS_OWNER_CONFIRMATION",
            "owner_questions": [],
            "normalized_tables": [{"sheet_name": "Ventas", "rows": []}],
        },
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: {
            "status": "INGESTION_OUTPUT_READY",
            "ingestion_output": {
                "columns": ["venta_total", "cobrado"],
                "normalized_tables": [{"sheet_name": "Ventas", "rows": []}],
            },
        },
    )

    def _root(request, *, dependencies):
        assert isinstance(request, WorkbookSemanticStartRequestV1)
        received["request"] = request
        return {
            "status": "COMPUTATION_PLAN_READY",
            "blocked_reason": None,
            "delivery_generated": True,
        }

    monkeypatch.setattr(cli, "run_service_1_product_pipeline_v1", _root)

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={"venta_total": "vendido", "cobrado": "cobrado"},
        semantic_owner_answers=None,
        output_dir=tmp_path,
        requested_capability="sold_vs_collected_gap",
        deliver_result=True,
    )

    assert result["status"] == "COMPUTATION_PLAN_READY"
    assert received["request"].requested_capability == "sold_vs_collected_gap"
    assert received["request"].deliver_result is True
    assert received["request"].ingestion_output["normalized_tables"]


def test_main_rejects_delivery_without_requested_capability(tmp_path: Path, capsys) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner = tmp_path / "owner.json"
    owner.write_text("{}", encoding="utf-8")
    exit_code = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner),
            "--deliver-result",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )

    assert exit_code == 2
    assert "--requested-capability is required" in capsys.readouterr().out
