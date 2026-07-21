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


def test_roadmap_has_unique_pathology_codes_and_four_productive_entries() -> None:
    payload = _load(ROADMAP_JSON)
    productive = payload["already_productive"]
    remaining = payload["roadmap"]
    codes = [item["pathology_code"] for item in productive + remaining]

    assert len(productive) == 4
    assert {item["pathology_code"] for item in productive} == {
        "LIQ_001",
        "REN_001",
        "LIQ_002",
        "PYME_011",
    }
    assert len(codes) == len(set(codes)) == 12


def test_roadmap_authorizes_architecture_cycle_and_defers_pyme_013() -> None:
    payload = _load(ROADMAP_JSON)
    transition = payload["architecture_transition"]
    pyme_013 = next(item for item in payload["roadmap"] if item["pathology_code"] == "PYME_013")

    assert payload["next_cycle"] == "CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE"
    assert transition == {
        "previous_authorization": "CYCLE_044_CONNECT_PYME_013_TO_PRODUCTIVE_ROOT",
        "previous_authorization_status": "SUSPENDED_BY_ARCHITECTURAL_DECISION",
        "authorized_cycle": "CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE",
        "pyme_013_status": "DEFERRED_AS_FIRST_COMPOSITE_CAPABILITY",
    }
    assert pyme_013["calculation_state"] == "DEFERRED_AS_FIRST_COMPOSITE_CAPABILITY"


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


def test_human_documents_do_not_duplicate_pyme_013_and_match_status() -> None:
    roadmap_text = ROADMAP_MD.read_text(encoding="utf-8")
    status_text = STATUS_MD.read_text(encoding="utf-8")

    assert roadmap_text.count("| 5 | `PYME_013` |") == 1
    assert "CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE" in roadmap_text
    assert "CYCLE_044_CONNECT_PYME_013_TO_PRODUCTIVE_ROOT: SUSPENDED_BY_ARCHITECTURAL_DECISION" in status_text
    assert "PATOLOGÍAS PRODUCTIVAS ACTUALES: 4 DE 12" in status_text
    assert "NO_PRODUCTIVE_CODE" in status_text
