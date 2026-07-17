from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _summary() -> dict:
    return json.loads((_root() / "docs" / "service_1_pilot_006_taller_mecanico.v1.json").read_text(encoding="utf-8"))


def test_pilot_006_taller_mecanico_passed_with_official_cli() -> None:
    data = _summary()
    assert data["schema_version"] == "SERVICE_1_PILOT_006_TALLER_MECANICO_RUN_V1"
    assert data["cycle"] == "CYCLE_035_RUN_S1_PILOT_006_TALLER_MECANICO"
    assert data["status"] == "PASS"
    assert data["official_cli"] == "python -m pymia.cli.service_1_product"
    assert data["fixture"] == "prueba_excels/taller_mecanico_lubricar_srl.xlsx"
    assert data["sheet_name"] == "ORDENES_TRABAJO"


def test_pilot_006_blocked_before_semantic_owner_reentry() -> None:
    first = _summary()["first_pass"]
    assert first["returncode"] == 2
    assert first["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert first["owner_questions_count"] == 9
    assert first["tools_executed"] is False


def test_pilot_006_semantic_answers_are_allowed_ids_not_free_text() -> None:
    semantic = _summary()["semantic_owner_answers"]
    assert semantic["count"] == 9
    assert "no free text" in semantic["source_rule"]
    for column, selected in semantic["selected"].items():
        assert selected in semantic["allowed_option_sources"][column]
        assert selected not in {"OTHER", "IGNORE"}


def test_pilot_006_final_pass_executes_only_explicit_tool() -> None:
    final = _summary()["final_pass"]
    assert final["returncode"] == 0
    assert final["status"] == "PRODUCT_PIPELINE_READY"
    assert final["semantic_bindings_confirmed"] is True
    assert final["tools_executed"] is True
    assert final["executed_tool_refs"] == ["precio_margen_basico"]
    assert final["xlsx_outputs"] == ["first_aid_001_precio_margen_basico.xlsx"]


def test_pilot_006_limits_prevent_scope_inflation() -> None:
    limits = "\n".join(_summary()["limits"])
    assert "does not claim automatic tool selection" in limits
    assert "not full workshop profitability diagnosis" in limits
    assert "future governed capability" in limits


def test_current_readme_lists_pilot_006_doc() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_006_TALLER_MECANICO.md" in readme
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_006_TALLER_MECANICO.md").exists()
