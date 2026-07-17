from __future__ import annotations
import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _evidence() -> dict:
    return json.loads((_root() / "docs" / "service_1_pilot_007_constructora.v1.json").read_text(encoding="utf-8"))


def test_pilot_007_constructora_passed_product_path() -> None:
    evidence = _evidence()
    assert evidence["schema_version"] == "SERVICE_1_PILOT_007_CONSTRUCTORA_RUN_V1"
    assert evidence["status"] == "PASS"
    assert evidence["fixture"] == "prueba_excels/constructora_nueva_era_srl.xlsx"
    assert evidence["sheet_name"] == "OBRAS"
    assert evidence["first_pass"]["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert evidence["first_pass"]["owner_questions_count"] == 16
    assert evidence["first_pass"]["tools_executed"] is False
    assert evidence["final_pass"]["status"] == "PRODUCT_PIPELINE_READY"
    assert evidence["final_pass"]["semantic_bindings_confirmed"] is True
    assert evidence["final_pass"]["tools_executed"] is True
    assert evidence["final_pass"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert evidence["final_pass"]["xlsx_outputs"] == ["first_aid_001_precio_margen_basico.xlsx"]


def test_pilot_007_semantic_answers_are_canonical_options_only() -> None:
    evidence = _evidence()
    selected = evidence["semantic_owner_answers"]["selected"]
    allowed = evidence["semantic_owner_answers"]["allowed_option_sources"]
    assert len(selected) == 16
    assert set(selected) == set(allowed)
    for column, value in selected.items():
        assert value in allowed[column]
        assert value != "OTHER"
        assert value != "IGNORE"


def test_pilot_007_limits_do_not_claim_advanced_diagnosis() -> None:
    limits = "\n".join(_evidence()["limits"])
    assert "explicit tool request" in limits
    assert "does not claim automatic tool selection" in limits
    assert "not full construction project diagnosis" in limits
    assert "advanced analysis remains a future governed capability" in limits


def test_current_readme_lists_pilot_007_doc() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_007_CONSTRUCTORA.md" in readme
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_007_CONSTRUCTORA.md").exists()
