from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _evidence() -> dict:
    path = _root() / "docs" / "service_1_pilot_003_textil_compleja.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_pilot_003_textil_evidence_is_pass_and_uses_active_fixture() -> None:
    evidence = _evidence()
    assert evidence["schema_version"] == "SERVICE_1_PILOT_003_TEXTIL_COMPLEJA_RUN_V1"
    assert evidence["cycle"] == "CYCLE_033_RUN_S1_PILOT_003_TEXTIL_COMPLEJA"
    assert evidence["status"] == "PASS"
    assert evidence["fixture"] == "prueba_excels/pyme_textil_compleja.xlsx"
    assert evidence["sheet_name"] == "VENTAS"
    assert "simple_bem_test" not in evidence["fixture"]


def test_pilot_003_blocks_before_semantic_reentry() -> None:
    evidence = _evidence()
    assert evidence["first_pass"]["returncode"] == 2
    assert evidence["first_pass"]["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert evidence["first_pass"]["owner_questions_count"] == 2
    assert evidence["first_pass"]["tools_executed"] is False


def test_pilot_003_semantic_answers_come_from_allowed_options() -> None:
    evidence = _evidence()
    assert evidence["semantic_owner_answers"]["count"] == 2
    selected = evidence["semantic_owner_answers"]["selected"]
    sources = evidence["semantic_owner_answers"]["allowed_option_sources"]
    assert selected == {"descuento": "A", "margen": "A"}
    for column, option_id in selected.items():
        assert option_id in sources[column]
        assert option_id not in {"OTHER", "IGNORE"}


def test_pilot_003_final_pass_executes_only_explicit_tool() -> None:
    evidence = _evidence()
    final = evidence["final_pass"]
    assert final["returncode"] == 0
    assert final["status"] == "PRODUCT_PIPELINE_READY"
    assert final["semantic_bindings_confirmed"] is True
    assert final["tools_executed"] is True
    assert final["executed_tool_refs"] == ["precio_margen_basico"]
    assert final["xlsx_outputs"] == ["first_aid_001_precio_margen_basico.xlsx"]


def test_pilot_003_declares_limits_and_does_not_claim_auto_tool_selection() -> None:
    evidence = _evidence()
    limits = "\n".join(evidence["limits"])
    assert "explicit tool request" in limits
    assert "does not claim automatic tool selection" in limits
    assert "not full textil diagnosis" in limits
    assert "future governed capability" in limits


def test_pilot_003_current_doc_is_indexed() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md" in readme
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md").exists()
