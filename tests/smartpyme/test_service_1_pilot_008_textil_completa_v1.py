from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _evidence() -> dict:
    return json.loads(
        (_root() / "docs" / "service_1_pilot_008_textil_completa.v1.json").read_text(
            encoding="utf-8"
        )
    )


def test_pilot_008_textil_completa_passed_product_path() -> None:
    evidence = _evidence()
    assert evidence["schema_version"] == "SERVICE_1_PILOT_008_TEXTIL_COMPLETA_RUN_V1"
    assert evidence["cycle"] == "CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA"
    assert evidence["status"] == "PASS"
    assert evidence["fixture"] == "prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx"
    assert evidence["sheet_name"] == "ventas"
    assert evidence["first_pass"]["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert evidence["first_pass"]["owner_questions_count"] == 4
    assert evidence["first_pass"]["tools_executed"] is False
    assert evidence["final_pass"]["status"] == "PRODUCT_PIPELINE_READY"
    assert evidence["final_pass"]["blocked_reason"] is None
    assert evidence["final_pass"]["semantic_bindings_confirmed"] is True
    assert evidence["final_pass"]["tools_executed"] is True
    assert evidence["final_pass"]["executed_tool_refs"] == ["precio_margen_basico"]
    assert evidence["final_pass"]["xlsx_outputs"] == [
        "first_aid_001_precio_margen_basico.xlsx"
    ]


def test_pilot_008_owner_answers_are_canonical_and_bounded() -> None:
    evidence = _evidence()
    answers = evidence["semantic_owner_answers"]
    assert answers["count"] == 4
    assert set(answers["selected"]) == {
        "cliente",
        "descuento_pct",
        "medio_cobro",
        "plazo_cobro_dias",
    }
    assert set(answers["selected"].values()) == {"A"}
    assert "allowed_option_ids" in answers["source_rule"]
    assert "no free text" in answers["source_rule"]


def test_pilot_008_limits_do_not_expand_product_authority() -> None:
    limits = "\n".join(_evidence()["limits"])
    assert "explicit tool request" in limits
    assert "does not claim automatic tool selection" in limits
    assert "does not claim full textile diagnosis" in limits
    assert "No new formula" in limits
    assert "REN_001 remains an isolated SUPPORT_NECESSARY evaluator" in limits


def test_current_readme_lists_pilot_008_doc() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    assert "SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md" in readme
    assert (root / "docs" / "current" / "SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md").exists()
