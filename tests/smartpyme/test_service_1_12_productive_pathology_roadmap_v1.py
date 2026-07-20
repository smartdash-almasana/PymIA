from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROADMAP_JSON = ROOT / "docs" / "service_1_12_productive_pathology_roadmap.v1.json"
ROADMAP_MD = ROOT / "docs" / "current" / "SERVICE_1_12_PRODUCTIVE_PATHOLOGY_ROADMAP.md"

EXPECTED_ORDER = [
    "LIQ_001",
    "REN_001",
    "LIQ_002",
    "PYME_011",
    "PYME_013",
    "INV_001",
    "INV_002",
    "PYME_024",
    "PYME_033",
    "REN_002",
    "PYME_027",
    "PYME_026",
]


def _roadmap() -> dict[str, object]:
    return json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))


def test_cycle_041_selects_exactly_twelve_unique_pathologies() -> None:
    roadmap = _roadmap()
    selected = [
        *(item["pathology_code"] for item in roadmap["already_productive"]),
        *(item["pathology_code"] for item in roadmap["roadmap"]),
    ]
    assert selected == EXPECTED_ORDER
    assert len(selected) == 12
    assert len(set(selected)) == 12
    assert roadmap["target_productive_pathology_count"] == 12


def test_cycle_041_keeps_existing_productive_baseline_first() -> None:
    roadmap = _roadmap()
    baseline = roadmap["already_productive"]
    assert baseline[0]["pathology_code"] == "LIQ_001"
    assert baseline[0]["capability_ref"] == "sold_vs_collected_gap"
    assert baseline[1]["pathology_code"] == "REN_001"
    assert baseline[1]["capability_ref"] == "net_margin_real"


def test_cycle_041_requires_complete_contract_fields_for_new_pathologies() -> None:
    roadmap = _roadmap()
    for item in roadmap["roadmap"]:
        assert item["formula_id"]
        assert item["expression"]
        assert item["required_variables"]
        assert item["required_evidence"]
        assert item["calculation_state"] in {"CALCULABLE", "CALCULABLE_CON_SUPUESTOS"}


def test_cycle_041_authorizes_only_liq_002_next() -> None:
    roadmap = _roadmap()
    assert roadmap["next_cycle"] == "CYCLE_042_CONNECT_LIQ_002_TO_PRODUCTIVE_ROOT"
    assert roadmap["roadmap"][0]["pathology_code"] == "LIQ_002"
    assert roadmap["roadmap"][0]["implementation_cycle"] == roadmap["next_cycle"]
    assert all("implementation_cycle" not in item for item in roadmap["roadmap"][1:])


def test_cycle_041_guards_prevent_batch_implementation_and_scope_drift() -> None:
    guards = _roadmap()["global_guards"]
    assert guards == {
        "one_pathology_per_cycle": True,
        "explicit_capability_request_required": True,
        "automatic_capability_selection": False,
        "causal_diagnosis_authorized": False,
        "scrap_oee_included": False,
        "llm_runtime_authorized": False,
    }


def test_cycle_041_current_document_states_limits_and_next_cycle() -> None:
    content = ROADMAP_MD.read_text(encoding="utf-8")
    assert "CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP" in content
    assert "CYCLE_042_CONNECT_LIQ_002_TO_PRODUCTIVE_ROOT" in content
    assert "Scrap y OEE quedan fuera" in content
    assert "No se implementan las diez patologías en este ciclo" in content
