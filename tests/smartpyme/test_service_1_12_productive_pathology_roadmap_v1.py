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
        assert item["calculation_state"] in {
            "CALCULABLE",
            "CALCULABLE_CON_SUPUESTOS",
            "DEFERRED_AS_FIRST_COMPOSITE_CAPABILITY",
        }


def test_cycle_053_completes_twelve_pathologies_and_next_cycle_is_pending() -> None:
    roadmap = _roadmap()
    transition = roadmap["architecture_transition"]

    assert roadmap["next_cycle"] == "PENDING_ASSIGNMENT"
    assert not roadmap["roadmap"]
    assert len(roadmap["already_productive"]) == 12
    assert transition["previous_authorization"] == "CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE"
    assert transition["previous_authorization_status"] == "COMPLETED"


def test_cycle_041_guards_prevent_batch_implementation_and_scope_drift() -> None:
    guards = _roadmap()["global_guards"]
    assert guards == {
        "one_pathology_per_cycle": True,
        "explicit_capability_request_required": True,
        "automatic_capability_selection": False,
        "causal_diagnosis_authorized": False,
        "scrap_oee_included": False,
        "llm_runtime_authorized": False,
        "second_productive_root_authorized": False,
    }


def test_cycle_053_document_completed_twelve_pathologies() -> None:
    content = ROADMAP_MD.read_text(encoding="utf-8")
    assert "CYCLE_053_GLOBAL_12_PATHOLOGY_CLOSURE" in content
    assert "12 patologías productivas conectadas" in content or "12/12" in content
    assert "PENDIENTE DE ASIGNACIÓN" in content
    assert "Scrap y OEE no soportados" in content
    assert "entrega no autorizada" in content.lower() or "no autorizada" in content
