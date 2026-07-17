from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import service_1_product as cli


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json(path: str) -> dict:
    return json.loads((_repo_root() / path).read_text(encoding="utf-8"))


def test_product_completion_gate_schema_and_docs_are_current() -> None:
    root = _repo_root()
    gate = _json("docs/service_1_product_completion_gate.v1.json")
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    status = (root / "docs" / "current" / "SERVICE_1_STATUS.md").read_text(encoding="utf-8")

    assert gate["schema_version"] == "SERVICE_1_PRODUCT_COMPLETION_GATE_V1"
    assert gate["status"] == "PASS_PRODUCT_MVP_COMPLETE"
    assert gate["cycle"] == "CYCLE_029_SERVICE_1_PRODUCT_COMPLETION_GATE"
    assert "SERVICE_1_PRODUCT_COMPLETION_GATE.md" in readme
    assert "SERVICE_1_PRODUCT_COMPLETION_GATE: PASS" in status
    assert "SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO" in status


def test_product_completion_gate_counts_and_legacy_absence() -> None:
    root = _repo_root()
    gate = _json("docs/service_1_product_completion_gate.v1.json")
    registry = _json("docs/service_1_module_disposition.v1.json")
    counts = registry["counts"]

    assert registry["total_modules"] == gate["registry_expected_counts"]["total_modules"]
    assert counts.get("PRODUCTIVE") == gate["registry_expected_counts"]["PRODUCTIVE"]
    assert counts.get("SUPPORT_NECESSARY") == gate["registry_expected_counts"]["SUPPORT_NECESSARY"]
    assert counts.get("EXPERIMENTAL_FROZEN", 0) == 0

    assert (root / gate["official_entrypoint"]["path"]).exists()
    assert (root / gate["canonical_product_root"]["path"]).exists()
    for path in (
        gate["required_guards"]["legacy_operator_cli_absent"],
        gate["required_guards"]["runtime_bridge_cli_absent"],
        gate["required_guards"]["legacy_runtime_bridge_absent"],
        gate["required_guards"]["legacy_exceland_absent"],
    ):
        assert not (root / path).exists(), path


def test_product_completion_gate_real_cafeteria_acceptance(tmp_path: Path) -> None:
    root = _repo_root()
    xlsx = root / "prueba_excels" / "cafeteria_abc.xlsx"
    assert xlsx.exists()

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
    tool_requests = [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {"precio_venta": 1200, "costo_unitario": 800},
        }
    ]

    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=None,
        tool_requests=tool_requests,
        output_dir=output_dir,
        sheet_name="Ventas",
    )
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert first["product_pipeline"]["tools_executed"] is False
    assert not list(output_dir.glob("*.xlsx"))

    semantic_answers = {
        question["column_name"]: next(
            option_id
            for option_id in question["allowed_option_ids"]
            if option_id not in {"OTHER", "IGNORE"}
        )
        for question in first["product_pipeline"]["owner_questions"]
    }
    assert semantic_answers

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=semantic_answers,
        tool_requests=tool_requests,
        output_dir=output_dir,
        sheet_name="Ventas",
    )
    product = final["product_pipeline"]
    assert final["status"] == "PRODUCT_PIPELINE_READY"
    assert product["semantic_bindings_confirmed"] is True
    assert product["tools_executed"] is True
    assert product["physical_run"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert list(output_dir.glob("*.xlsx"))


def test_product_completion_gate_plan_only_liq_001_acceptance(tmp_path: Path) -> None:
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
    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=None,
        tool_requests=[],
        requested_capability="sold_vs_collected_gap",
        output_dir=output_dir,
        sheet_name="Ventas",
    )
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"

    semantic_answers = {}
    for question in first["product_pipeline"]["owner_questions"]:
        if question["column_name"] == "cobrado":
            semantic_answers[question["column_name"]] = next(
                option["option_id"]
                for option in question["options"]
                if option["label"] == "Importe cobrado"
            )
        else:
            semantic_answers[question["column_name"]] = next(
                option_id
                for option_id in question["allowed_option_ids"]
                if option_id not in {"OTHER", "IGNORE"}
            )

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=semantic_answers,
        tool_requests=[],
        requested_capability="sold_vs_collected_gap",
        output_dir=output_dir,
        sheet_name="Ventas",
    )
    product = final["product_pipeline"]
    plan = product["computation_plan"]

    assert final["status"] == "COMPUTATION_PLAN_READY"
    assert product["tools_executed"] is False
    assert product["physical_run"] is None
    assert plan["status"] == "READY_FOR_COMPUTATION"
    assert plan["formula_id"] == "LIQ_001_vendido_cobrado"
    assert plan["runtime_authorized"] is False
    assert plan["tool_execution_authorized"] is False
    assert plan["computation_executed"] is False
    assert not list(output_dir.glob("*.xlsx"))
