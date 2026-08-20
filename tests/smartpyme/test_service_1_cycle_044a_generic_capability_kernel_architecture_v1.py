from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROADMAP_JSON = REPO_ROOT / "docs" / "service_1_12_productive_pathology_roadmap.v1.json"
BRIEF_JSON = REPO_ROOT / "docs" / "service_1_cycle_044a_generic_capability_kernel_architecture_brief.v1.json"
STATUS_MD = REPO_ROOT / "docs" / "current" / "SERVICE_1_STATUS.md"
ROADMAP_MD = REPO_ROOT / "docs" / "current" / "SERVICE_1_12_PRODUCTIVE_PATHOLOGY_ROADMAP.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_roadmap_completed_twelve_productive_entries() -> None:
    payload = _load(ROADMAP_JSON)
    productive = payload["already_productive"]
    remaining = payload["roadmap"]
    codes = [item["pathology_code"] for item in productive]

    assert len(productive) == 12
    assert len(remaining) == 0
    assert len(codes) == len(set(codes)) == 12


def test_roadmap_transition_is_completed_and_no_deferred_capabilities() -> None:
    payload = _load(ROADMAP_JSON)
    transition = payload["architecture_transition"]

    assert payload["next_cycle"] == "PENDING_ASSIGNMENT"
    assert transition["previous_authorization"] == "CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE"
    assert transition["previous_authorization_status"] == "COMPLETED"


def test_kernel_boundary_and_exclusions_are_explicit() -> None:
    brief = _load(BRIEF_JSON)
    boundary = brief["kernel_boundary"]

    assert boundary["starts_after"] == "GOVERNED_COMPUTATION_PLAN"
    assert boundary["ends_before"] == "PHYSICAL_DELIVERY"
    assert set(boundary["includes"]) == {
        "evidence_resolution",
        "governed_aggregation",
        "mathematical_domain_validation",
        "safe_formula_execution",
        "classification",
        "bounded_outcome",
    }
    assert {
        "ingestion",
        "owner_dialogue",
        "case_fsm",
        "cli",
        "capability_selection",
        "xlsx_pdf_delivery",
        "external_connectors",
        "llm_runtime",
    }.issubset(set(boundary["excludes"]))


def test_atomic_composite_migration_states_and_pilots_are_fixed() -> None:
    brief = _load(BRIEF_JSON)

    assert brief["capability_types"] == ["ATOMIC", "COMPOSITE"]
    assert brief["migration_states"] == [
        "LEGACY_ACTIVE",
        "GENERIC_SHADOW",
        "GENERIC_PRIMARY",
        "RETIRED",
    ]
    assert brief["pilot_pathologies"] == ["LIQ_002", "PYME_011"]
    assert brief["aggregation_strategies_initial"] == ["SUM", "SINGLE_VALUE"]
    assert brief["single_value_cardinality"] == "EXACTLY_ONE"


def test_pyme_013_is_composite_and_does_not_claim_full_ccc() -> None:
    brief = _load(BRIEF_JSON)
    composite = brief["composite_first_candidate"]

    assert composite["pathology_code"] == "PYME_013"
    assert composite["must_consume_governed_results"] == ["dso", "dpo"]
    assert composite["implicit_reconstruction_allowed"] is False
    assert composite["full_cash_conversion_cycle_claim_allowed"] is False


def test_safety_prohibitions_remain_closed() -> None:
    brief = _load(BRIEF_JSON)
    principles = brief["principles"]
    authorizations = brief["cycle_044a_authorizations"]

    assert principles["eval_allowed"] is False
    assert principles["automatic_capability_selection"] is False
    assert principles["causal_diagnosis_authorized"] is False
    assert principles["second_productive_root_authorized"] is False
    assert all(value is False for value in authorizations.values())


def test_human_documents_reflect_twelve_productive_pathologies() -> None:
    roadmap_text = ROADMAP_MD.read_text(encoding="utf-8")
    status_text = STATUS_MD.read_text(encoding="utf-8")

    assert "CYCLE_053_GLOBAL_12_PATHOLOGY_CLOSURE" in roadmap_text or "CYCLE_053" in roadmap_text
    assert "12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS" in status_text
    assert "NO_LLM_RUNTIME_AUTHORITY" in status_text
    assert "EXTERNAL_LLM_RUNTIME_ACTIVATION_CURRENT_RC: NOT_PROVEN" in status_text
    assert "SIN DIAGNÓSTICO CAUSAL" in status_text
