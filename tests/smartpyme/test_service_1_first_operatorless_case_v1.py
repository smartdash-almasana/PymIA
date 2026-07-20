from __future__ import annotations

import json
from pathlib import Path

from pymia.cli import service_1_product as cli


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _case_record() -> dict:
    return json.loads(
        (_repo_root() / "docs" / "service_1_first_operatorless_case.v1.json").read_text(
            encoding="utf-8"
        )
    )


def test_operatorless_case_record_is_pass_and_uses_official_cli_only() -> None:
    root = _repo_root()
    record = _case_record()

    assert record["schema_version"] == "SERVICE_1_FIRST_OPERATORLESS_CASE_V1"
    assert record["status"] == "PASS_OPERATORLESS_CASE_RUN"
    assert record["operatorless_constraints"]["official_cli_only"] == (
        "python -m pymia.cli.service_1_product"
    )
    assert record["operatorless_constraints"]["no_free_text_semantic_reentry"] is True
    assert record["operatorless_constraints"]["explicit_tool_request_only"] is True
    assert not (root / "pymia" / "cli" / "service_1_operator.py").exists()
    assert not (root / "pymia" / "cli" / "service_1_xlsx_runtime_bridge.py").exists()


def test_operatorless_case_doc_is_listed_as_current_authority() -> None:
    root = _repo_root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    status = (root / "docs" / "current" / "SERVICE_1_STATUS.md").read_text(
        encoding="utf-8"
    )

    assert "SERVICE_1_FIRST_OPERATORLESS_CASE.md" in readme


def test_operatorless_case_replays_from_cli_without_internal_runtime(tmp_path: Path) -> None:
    root = _repo_root()
    xlsx = root / "prueba_excels" / "cafeteria_abc.xlsx"
    output_dir = tmp_path / "output"
    output_dir.mkdir()

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

    semantic_answers = {}
    for question in first["product_pipeline"]["owner_questions"]:
        allowed = question["allowed_option_ids"]
        semantic_answers[question["column_name"]] = next(
            option_id
            for option_id in allowed
            if option_id not in {"OTHER", "IGNORE", "IGNORED_NOT_RELEVANT"}
        )

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


def test_operatorless_case_record_matches_replay_contract() -> None:
    record = _case_record()
    criteria = record["pass_criteria"]

    assert criteria["first_pass_status"] == "NEEDS_OWNER_CONFIRMATION"
    assert criteria["first_pass_tools_executed"] is False
    assert criteria["semantic_answers_are_allowed_option_ids"] is True
    assert criteria["final_pass_status"] == "PRODUCT_PIPELINE_READY"
    assert criteria["semantic_bindings_confirmed"] is True
    assert criteria["tools_executed"] is True
    assert criteria["executed_tool_refs"] == ["precio_margen_basico"]
    assert criteria["xlsx_output_exists"] is True
