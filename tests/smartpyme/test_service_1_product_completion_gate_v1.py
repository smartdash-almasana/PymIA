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
    assert "F0_F13: CLOSED_COMMITTED" in status
    assert "SERVICE_1_RELEASE_CANDIDATE_ACCEPTED: NO" in status


def test_product_completion_gate_counts_and_legacy_absence() -> None:
    root = _repo_root()
    gate = _json("docs/service_1_product_completion_gate.v1.json")
    registry = _json("docs/service_1_module_disposition.v1.json")
    counts = registry["counts"]

    historical = gate["registry_expected_counts"]
    assert registry["total_modules"] >= historical["total_modules"]
    assert counts.get("PRODUCTIVE", 0) >= historical["PRODUCTIVE"]
    assert counts.get("SUPPORT_NECESSARY", 0) >= historical["SUPPORT_NECESSARY"]
    assert counts.get("EXPERIMENTAL_FROZEN", 0) == historical["EXPERIMENTAL_FROZEN"]

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
    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    first = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=None,
        output_dir=output_dir,
        sheet_name="Ventas",
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert first["product_pipeline"]["tools_executed"] is False
    assert not list(output_dir.glob("*.xlsx"))

    semantic_answers = {
        question["decision_id"]: {"action": "ACCEPT"}
        for question in first["product_pipeline"]["owner_questions"]
    }
    assert semantic_answers

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=semantic_answers,
        output_dir=output_dir,
        sheet_name="Ventas",
        requested_capability="sales_total",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    product = final["product_pipeline"]
    # sales_total is a discovery analysis, not a P8-governed capability yet.
    assert final["status"] == "BLOCKED"
    assert final["blocked_reason"] == "CAPABILITY_NOT_GOVERNED"
    assert product["semantic_bindings_confirmed"] is True
    assert product["computation_executed"] is False
    assert product["tools_executed"] is False
    assert product["physical_run"] is None
    assert not list(output_dir.glob("*.xlsx"))


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
        requested_capability="sold_vs_collected_gap",
        output_dir=output_dir,
        sheet_name="Ventas",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"

    semantic_answers = {
        question["decision_id"]: {"action": "ACCEPT"}
        for question in first["product_pipeline"]["owner_questions"]
    }

    final = cli.run_service_1_product_entrypoint_v1(
        xlsx_path=xlsx,
        owner_column_answers=owner_answers,
        semantic_owner_answers=semantic_answers,
        requested_capability="sold_vs_collected_gap",
        output_dir=output_dir,
        sheet_name="Ventas",
        semantic_owner_actor_id="owner-cli",
        semantic_owner_actor_role="owner",
    )
    product = final["product_pipeline"]
    governed = product["governed_computation_input"]

    assert final["status"] == "COMPUTATION_PLAN_READY"
    assert product["tools_executed"] is False
    assert product["physical_run"] is None
    assert "computation_plan" not in product
    assert governed["schema_version"] == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"
    assert governed["formula_id"] == "LIQ_001_vendido_cobrado"
    assert governed["runtime_authorized"] is False
    assert governed["tool_execution_authorized"] is False
    assert product["computation_executed"] is True
    assert not list(output_dir.glob("*.xlsx"))
