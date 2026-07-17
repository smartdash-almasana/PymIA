from __future__ import annotations
import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _record() -> dict:
    return json.loads((_root() / "docs" / "service_1_pilot_004_distribuidora_mayorista.v1.json").read_text(encoding="utf-8"))


def test_pilot_004_distribuidora_recorded_as_pass() -> None:
    record = _record()
    assert record["schema_version"] == "SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA_RUN_V1"
    assert record["cycle"] == "CYCLE_034_RUN_S1_PILOT_004_DISTRIBUIDORA_MAYORISTA"
    assert record["status"] == "PASS"
    assert record["fixture"] == "prueba_excels/distribuidora_mayorista_compleja.xlsx"
    assert record["sheet_name"] == "OPERACION"


def test_pilot_004_blocks_first_then_executes_after_semantic_reentry() -> None:
    record = _record()
    assert record["first_pass"]["returncode"] == 2
    assert record["first_pass"]["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert record["first_pass"]["owner_questions_count"] == 3
    assert record["first_pass"]["tools_executed"] is False
    assert record["final_pass"]["returncode"] == 0
    assert record["final_pass"]["status"] == "PRODUCT_PIPELINE_READY"
    assert record["final_pass"]["semantic_bindings_confirmed"] is True
    assert record["final_pass"]["tools_executed"] is True
    assert record["final_pass"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert record["final_pass"]["xlsx_outputs"]


def test_pilot_004_semantic_answers_are_allowed_ids_not_free_text() -> None:
    semantic = _record()["semantic_owner_answers"]
    assert semantic["count"] == 3
    assert set(semantic["selected"]) == {"cliente", "ruta", "margen"}
    for column, selected in semantic["selected"].items():
        assert selected in semantic["allowed_option_sources"][column]
    assert "no free text" in semantic["source_rule"]


def test_pilot_004_preserves_limits() -> None:
    limits = "\n".join(_record()["limits"])
    assert "explicit tool request" in limits
    assert "not full route profitability diagnosis" in limits
    assert "advanced analysis remains a future governed capability" in limits


def test_pilot_004_current_docs_are_indexed() -> None:
    root = _root()
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md").exists()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md" in readme
