from __future__ import annotations

from pathlib import Path

from pymia.cli import service_1_product as cli


def test_product_entrypoint_routes_through_canonical_root(tmp_path: Path, monkeypatch) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    calls: list[str] = []

    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        lambda **_: calls.append("boundary") or {"status": "NEEDS_OWNER_CONFIRMATION"},
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: calls.append("connector") or {
            "status": "INGESTION_OUTPUT_READY",
            "ingestion_output": {"columns": ["fecha"], "input_values": {"fecha": "operation_date"}},
        },
    )
    monkeypatch.setattr(
        cli,
        "run_service_1_product_pipeline_v1",
        lambda **_: calls.append("product") or {
            "status": "PRODUCT_PIPELINE_READY",
            "blocked_reason": None,
        },
    )

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={"fecha": "operation_date"},
        semantic_owner_answers={"fecha": "operation_date"},
        tool_requests=[{"tool_ref": "gastos_triage", "inputs": {}}],
        output_dir=tmp_path / "out",
        sheet_name="Ventas",
    )

    assert result["status"] == "PRODUCT_PIPELINE_READY"
    assert calls == ["boundary", "connector", "product"]


def test_product_entrypoint_blocks_before_root_when_connector_blocks(tmp_path: Path, monkeypatch) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        lambda **_: {"status": "NEEDS_OWNER_CONFIRMATION"},
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: {"status": "BLOCKED", "blocked_reason": "OWNER_ANSWER_REQUIRED"},
    )
    monkeypatch.setattr(
        cli,
        "run_service_1_product_pipeline_v1",
        lambda **_: (_ for _ in ()).throw(AssertionError("must not run")),
    )

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={},
        semantic_owner_answers=None,
        tool_requests=[{"tool_ref": "gastos_triage", "inputs": {}}],
        output_dir=tmp_path,
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "OWNER_ANSWER_REQUIRED"
