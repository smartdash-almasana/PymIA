from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import service_1_product as cli
from pymia.contracts.column_confirmation_v1 import ColumnConfirmationMatrix
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
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


def test_main_accepts_utf8_bom_and_serializes_domain_records(
    tmp_path: Path, monkeypatch
) -> None:
    xlsx = tmp_path / "case.xlsx"
    xlsx.write_bytes(b"xlsx")
    owner_answers = tmp_path / "owner.json"
    owner_answers.write_text('{"Fecha": "fecha de venta"}', encoding="utf-8-sig")
    tool_requests = tmp_path / "tools.json"
    tool_requests.write_text(
        '[{"tool_ref": "precio_margen_basico", "inputs": {"precio_venta": 1200, "costo_unitario": 800}}]',
        encoding="utf-8-sig",
    )
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
            "--tool-requests",
            str(tool_requests),
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


def test_real_cafeteria_xlsx_cli_blocks_then_executes_after_canonical_reentry(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    xlsx = repo_root / "prueba_excels" / "cafeteria_abc.xlsx"
    assert xlsx.exists()

    owner_answers_path = tmp_path / "owner_column_answers.json"
    tool_requests_path = tmp_path / "tool_requests.json"
    first_result_path = tmp_path / "first_pass.json"
    semantic_answers_path = tmp_path / "semantic_owner_answers.json"
    final_result_path = tmp_path / "final_pass.json"
    output_dir = tmp_path / "output"

    owner_answers = {
        "VentaID": "identificador único de la venta",
        "Fecha": "fecha en que se realizó la venta",
        "Hora": "hora en que se realizó la venta",
        "SucursalID": "identificador de la sucursal",
        "ProductoID": "identificador del producto vendido",
        "Cantidad": "cantidad de unidades vendidas",
        "PrecioUnitario": "precio de venta por unidad",
        "MetodoPago": "medio de pago utilizado",
        "CanalVenta": "canal por el que se realizó la venta",
        "Descuento": "descuento aplicado a la venta",
        "Empleado": "empleado que registró o realizó la venta",
    }
    owner_answers_path.write_text(
        json.dumps(owner_answers, ensure_ascii=False), encoding="utf-8"
    )
    tool_requests_path.write_text(
        json.dumps(
            [
                {
                    "tool_ref": "precio_margen_basico",
                    "inputs": {"precio_venta": 1200, "costo_unitario": 800},
                }
            ]
        ),
        encoding="utf-8",
    )

    first_exit = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers_path),
            "--tool-requests",
            str(tool_requests_path),
            "--output-dir",
            str(output_dir),
            "--sheet-name",
            "Ventas",
            "--result-json",
            str(first_result_path),
        ]
    )
    first = json.loads(first_result_path.read_text(encoding="utf-8"))
    first_product = first["product_pipeline"]

    assert first_exit == 2
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert first_product["tools_executed"] is False
    assert not list(output_dir.glob("*.xlsx"))

    semantic_answers = {
        question["column_name"]: question["allowed_answers"][0]
        for question in first_product["owner_questions"]
    }
    assert semantic_answers
    assert all(value != "unknown" for value in semantic_answers.values())
    semantic_answers_path.write_text(
        json.dumps(semantic_answers, ensure_ascii=False), encoding="utf-8"
    )

    final_exit = cli.main(
        [
            "--xlsx",
            str(xlsx),
            "--owner-column-answers",
            str(owner_answers_path),
            "--semantic-owner-answers",
            str(semantic_answers_path),
            "--tool-requests",
            str(tool_requests_path),
            "--output-dir",
            str(output_dir),
            "--sheet-name",
            "Ventas",
            "--result-json",
            str(final_result_path),
        ]
    )
    final = json.loads(final_result_path.read_text(encoding="utf-8"))
    final_product = final["product_pipeline"]

    assert final_exit == 0
    assert final["status"] == "PRODUCT_PIPELINE_READY"
    assert final_product["semantic_bindings_confirmed"] is True
    assert final_product["tools_executed"] is True
    assert final_product["physical_run"]["executed_tool_refs"] == [
        "precio_margen_basico"
    ]
    assert list(output_dir.glob("*.xlsx"))


def test_real_cafeteria_xlsx_rejects_free_text_semantic_reentry(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    xlsx = repo_root / "prueba_excels" / "cafeteria_abc.xlsx"
    owner_answers = {
        "VentaID": "identificador único de la venta",
        "Fecha": "fecha de venta",
        "Hora": "hora de venta",
        "SucursalID": "identificador de sucursal",
        "ProductoID": "identificador de producto",
        "Cantidad": "cantidad vendida",
        "PrecioUnitario": "precio unitario",
        "MetodoPago": "medio de pago",
        "CanalVenta": "canal de venta",
        "Descuento": "descuento",
        "Empleado": "empleado",
    }
    tool_requests = [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {"precio_venta": 1200, "costo_unitario": 800},
        }
    ]

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=None,
        tool_requests=tool_requests,
        output_dir=tmp_path,
        sheet_name="Ventas",
    )
    questions = first["product_pipeline"]["owner_questions"]
    invalid_answers = {
        question["column_name"]: "texto libre no canónico" for question in questions
    }

    blocked = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=invalid_answers,
        tool_requests=tool_requests,
        output_dir=tmp_path,
        sheet_name="Ventas",
    )

    assert blocked["status"] == "BLOCKED"
    assert blocked["blocked_reason"] == "INVALID_OWNER_SEMANTIC_ANSWERS"
    assert blocked["product_pipeline"]["tools_executed"] is False
    assert not list(tmp_path.glob("*.xlsx"))
