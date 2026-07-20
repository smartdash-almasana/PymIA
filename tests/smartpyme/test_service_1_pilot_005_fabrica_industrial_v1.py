from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _evidence() -> dict:
    return json.loads(
        (_root() / "docs" / "service_1_pilot_005_fabrica_industrial.v1.json").read_text(
            encoding="utf-8"
        )
    )


def test_pilot_005_fabrica_industrial_passed_product_path() -> None:
    evidence = _evidence()
    assert evidence["schema_version"] == "SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL_RUN_V1"
    assert evidence["cycle"] == "CYCLE_038_RUN_S1_PILOT_005_FABRICA_INDUSTRIAL"
    assert evidence["status"] == "PASS"
    assert evidence["fixture"] == "prueba_excels/fabrica_industrial_compleja.xlsx"
    assert evidence["sheet_name"] == "PRODUCCION"
    assert evidence["first_pass"]["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert evidence["first_pass"]["owner_questions_count"] == 7
    assert evidence["first_pass"]["tools_executed"] is False
    assert evidence["final_pass"]["status"] == "PRODUCT_PIPELINE_READY"
    assert evidence["final_pass"]["semantic_bindings_confirmed"] is True
    assert evidence["final_pass"]["tools_executed"] is True
    assert evidence["final_pass"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert evidence["final_pass"]["xlsx_outputs"] == [
        "first_aid_001_precio_margen_basico.xlsx"
    ]


def test_pilot_005_preserves_industrial_limits() -> None:
    limits = "\n".join(_evidence()["limits"]).lower()
    assert "explicit tool request" in limits
    assert "does not claim automatic tool selection" in limits
    assert "does not claim full industrial diagnosis" in limits
    assert "scrap" in limits
    assert "oee" in limits
    assert "unsupported" in limits
    assert "no new formula" in limits


def test_current_readme_lists_pilot_005_doc() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md" in readme
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md").exists()
