from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import service_1_product as cli
from pymia.contracts.column_confirmation_v1 import ColumnConfirmationMatrix
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    WorkbookSemanticStartRequestV1,
)


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
    def _product(request, *, dependencies):
        assert isinstance(request, WorkbookSemanticStartRequestV1)
        calls.append("product")
        return {
            "status": "PRODUCT_PIPELINE_READY",
            "blocked_reason": None,
        }
    monkeypatch.setattr(cli, "run_service_1_product_pipeline_v1", _product)

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={"fecha": "operation_date"},
        semantic_owner_answers={"fecha": "operation_date"},
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
        output_dir=tmp_path,
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "OWNER_ANSWER_REQUIRED"


def test_main_accepts_utf8_bom_and_serializes_domain_records(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner_answers = tmp_path / "owner.json"
    owner_answers.write_text('{"Fecha": "fecha de venta"}', encoding="utf-8-sig")
    output_dir = tmp_path / "output"
    result_json = tmp_path / "result.json"
    candidate = Service1ColumnSemanticCandidateV1(
        source_column_name="Fecha",
        normalized_column_name="fecha",
        sheet_name="Ventas",
        observed_data_type="date",
        sample_values=("2026-07-01",),
        candidate_semantic_roles=("operation_date",),
        candidate_variable_names=("business_period",),
        confidence=0.9,
        ambiguity_reason=None,
        owner_confirmation_required=False,
    )
    monkeypatch.setattr(
        cli,
        "run_service_1_product_entrypoint_v1",
        lambda **_: {
            "status": "NEEDS_OWNER_CONFIRMATION",
            "product_pipeline": {
                "semantic_run": {
                    "bridge_packet": {
                        "column_candidates": (candidate,),
                        "confirmation_matrix": ColumnConfirmationMatrix(
                            file_name="case.xlsx",
                            entries=[],
                        ),
                    }
                }
            },
        },
    )

    exit_code = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers),
            "--requested-capability",
            "sold_vs_collected_gap",
            "--output-dir",
            str(output_dir),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 2
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    serialized = payload["product_pipeline"]["semantic_run"]["bridge_packet"][
        "column_candidates"
    ][0]
    assert serialized["source_column_name"] == "Fecha"
    assert serialized["candidate_semantic_roles"] == ["operation_date"]
    matrix = payload["product_pipeline"]["semantic_run"]["bridge_packet"][
        "confirmation_matrix"
    ]
    assert matrix == {"file_name": "case.xlsx", "entries": []}


def test_product_entrypoint_forwards_plan_only_capability(tmp_path: Path, monkeypatch) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    received: dict = {}
    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        lambda **_: {"status": "NEEDS_OWNER_CONFIRMATION"},
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: {
            "status": "INGESTION_OUTPUT_READY",
            "ingestion_output": {
                "case_id": "case_plan_cli",
                "columns": ["fecha"],
                "input_values": {"fecha": "operation_date"},
            },
        },
    )

    def _product(request, *, dependencies):
        assert isinstance(request, WorkbookSemanticStartRequestV1)
        received["request"] = request
        return {"status": "COMPUTATION_PLAN_READY", "blocked_reason": None}

    monkeypatch.setattr(cli, "run_service_1_product_pipeline_v1", _product)

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={"fecha": "operation_date"},
        semantic_owner_answers=None,
        output_dir=tmp_path / "out",
        requested_capability="sold_vs_collected_gap",
    )

    assert result["status"] == "COMPUTATION_PLAN_READY"
    assert received["request"].requested_capability == "sold_vs_collected_gap"


def test_main_accepts_requested_capability_without_delivery(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner_answers = tmp_path / "owner.json"
    owner_answers.write_text('{"Fecha": "fecha de venta"}', encoding="utf-8")
    result_json = tmp_path / "plan.json"
    received: dict = {}

    def _entrypoint(**kwargs):
        received.update(kwargs)
        return {
            "status": "COMPUTATION_PLAN_READY",
            "blocked_reason": None,
            "product_pipeline": {
                "tools_executed": False,
                "computation_plan": {
                    "status": "READY_FOR_COMPUTATION",
                    "formula_id": "LIQ_001_vendido_cobrado",
                },
            },
        }

    monkeypatch.setattr(cli, "run_service_1_product_entrypoint_v1", _entrypoint)

    exit_code = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers),
            "--requested-capability",
            "sold_vs_collected_gap",
            "--output-dir",
            str(tmp_path / "output"),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 0
    assert received["requested_capability"] == "sold_vs_collected_gap"
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["product_pipeline"]["tools_executed"] is False


def test_real_xlsx_entrypoint_builds_liq_001_plan_without_delivery(tmp_path: Path) -> None:
    import openpyxl

    xlsx = tmp_path / "ventas_cobros.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["fecha", "venta_total", "cobrado"])
    sheet.append(["2026-06-01", 1000, 800])
    sheet.append(["2026-06-02", 2000, 1500])
    workbook.save(xlsx)

    owner_answers = {
        "fecha": "fecha de la operación",
        "venta_total": "importe total vendido",
        "cobrado": "importe efectivamente cobrado",
    }
    output_dir = tmp_path / "output"
    entrypoint_kwargs = {
        "xlsx_path": xlsx,
        "owner_column_answers": owner_answers,
        "output_dir": output_dir,
        "sheet_name": "Ventas",
        "requested_capability": "sold_vs_collected_gap",
        "semantic_owner_actor_id": "owner-cli",
        "semantic_owner_actor_role": "owner",
    }

    first = cli.run_service_1_product_entrypoint_v1(
        semantic_owner_answers=None,
        **entrypoint_kwargs,
    )
    questions = first["product_pipeline"]["owner_questions"]
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert questions
    assert not list(output_dir.glob("*.xlsx"))

    semantic_answers = {
        question["decision_id"]: {"action": "ACCEPT"}
        for question in questions
    }
    final = cli.run_service_1_product_entrypoint_v1(
        semantic_owner_answers=semantic_answers,
        **entrypoint_kwargs,
    )
    product = final["product_pipeline"]
    governed = product["governed_computation_input"]

    assert final["status"] == "COMPUTATION_PLAN_READY"
    assert product["semantic_bindings_confirmed"] is True
    assert product["tools_executed"] is False
    assert product["physical_run"] is None
    assert governed["schema_version"] == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"
    assert governed["family_id"] == "CASH_COLLECTIONS"
    assert governed["formula_id"] == "LIQ_001_vendido_cobrado"
    assert governed["source_bindings"] == {
        "sold_amount": "venta_total",
        "collected_amount": "cobrado",
    }
    assert governed["runtime_authorized"] is False
    assert governed["tool_execution_authorized"] is False
    assert product["computation_executed"] is True
    assert not list(output_dir.glob("*.xlsx"))


def test_product_entrypoint_surfaces_boundary_sheet_selection_block(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    captured: dict[str, object] = {}

    def fake_boundary(**kwargs):
        captured.update(kwargs)
        return {"status": "BLOCKED", "blocked_reason": "SHEET_SELECTION_CONFLICT"}

    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        fake_boundary,
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: (_ for _ in ()).throw(AssertionError("connector must not run")),
    )

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={},
        semantic_owner_answers=None,
        output_dir=tmp_path / "out",
        sheet_name="Ventas",
        include_all_sheets=True,
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "SHEET_SELECTION_CONFLICT"
    assert result["connector"] is None
    assert captured["sheet_name"] == "Ventas"
    assert captured["include_all_sheets"] is True


def test_main_repeated_sheet_name_routes_selected_multisheet(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner_answers = tmp_path / "owner.json"
    owner_answers.write_text("{}", encoding="utf-8")
    result_json = tmp_path / "result.json"
    captured: dict[str, object] = {}

    def fake_entrypoint(**kwargs):
        captured.update(kwargs)
        return {"status": cli.STATUS_READY, "blocked_reason": None}

    monkeypatch.setattr(cli, "run_service_1_product_entrypoint_v1", fake_entrypoint)

    exit_code = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers),
            "--requested-capability",
            "sold_vs_collected_gap",
            "--output-dir",
            str(tmp_path / "out"),
            "--sheet-name",
            "Ventas",
            "--sheet-name",
            "Cobros",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 0
    assert captured["sheet_name"] is None
    assert captured["sheet_names"] == ("Ventas", "Cobros")
    assert captured["include_all_sheets"] is False


def test_main_all_sheets_routes_explicit_workbook_scope(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner_answers = tmp_path / "owner.json"
    owner_answers.write_text("{}", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_entrypoint(**kwargs):
        captured.update(kwargs)
        return {"status": cli.STATUS_READY, "blocked_reason": None}

    monkeypatch.setattr(cli, "run_service_1_product_entrypoint_v1", fake_entrypoint)

    exit_code = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers),
            "--requested-capability",
            "sold_vs_collected_gap",
            "--output-dir",
            str(tmp_path / "out"),
            "--all-sheets",
        ]
    )

    assert exit_code == 0
    assert captured["sheet_name"] is None
    assert captured["sheet_names"] is None
    assert captured["include_all_sheets"] is True


def test_product_entrypoint_empty_column_answers_emits_intake_questions(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    boundary = {
        "status": "NEEDS_OWNER_CONFIRMATION",
        "question_count": 2,
        "owner_questions": [
            {
                "question_id": "col_confirm_001",
                "field_id": "col_confirm_001",
                "sheet_name": "Ventas",
                "column_name": "monto",
            },
            {
                "question_id": "col_confirm_002",
                "field_id": "col_confirm_002",
                "sheet_name": "Cobros",
                "column_name": "monto",
            },
        ],
    }

    monkeypatch.setattr(
        cli,
        "build_service_1_web_column_confirmation_intake_boundary_v1",
        lambda **_: boundary,
    )
    monkeypatch.setattr(
        cli,
        "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        lambda **_: (_ for _ in ()).throw(AssertionError("connector must not run")),
    )

    result = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers={},
        semantic_owner_answers=None,
        output_dir=tmp_path / "out",
        include_all_sheets=True,
    )

    assert result["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert result["blocked_reason"] is None
    assert result["boundary"] == boundary
    assert result["connector"] is None
    assert result["product_pipeline"] is None
