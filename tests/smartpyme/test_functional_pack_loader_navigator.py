from pathlib import Path
from copy import deepcopy

from pymia.smartpyme.functional_pack_loader_navigator import (
    validate_functional_pack,
    navigate_single_cycle,
)


def _minimal_valid_pack() -> dict:
    return {
        "pack_id": "CASH_LIQUIDITY_GRAPH_V1",
        "pack_version": "1.0.0",
        "nodes": [
            {"node_id": "cash"},
            {"node_id": "sales"},
            {"node_id": "collections"},
        ],
        "formula_references": [
            {"formula_id": "ratio_cobranza"},
        ],
        "signal_routes": [
            {
                "signal_family": "SALES_CASH_GAP",
                "dominant_node": "cash",
                "active_subgraph": ["sales", "collections", "cash"],
                "formula_reference": "ratio_cobranza",
                "current_unknown": "cobranzas_del_periodo",
                "minimal_evidence_candidate": ["cobranzas_del_periodo"],
                "reason_code": "SALES_CASH_SYMPTOM_REQUIRES_COLLECTIONS_UNKNOWN_FIRST",
            }
        ],
        "unknowns": [
            {"unknown_id": "cobranzas_del_periodo"},
        ],
        "evidence_candidates": [
            {"evidence_id": "cobranzas_del_periodo"},
        ],
    }


def _minimal_valid_signal() -> dict:
    return {
        "signal_id": "sig_001",
        "signal_family": "SALES_CASH_GAP",
        "source": "owner_symptom_normalized",
    }


# --- validate_functional_pack ---

def test_validate_pack_passes_with_minimal_valid_pack():
    result = validate_functional_pack(_minimal_valid_pack())
    assert result["status"] == "PACK_VALIDATED"
    assert result["boundary_check"]["validated_anatomy"] is True


def test_validate_pack_blocked_when_missing_pack_id():
    pack = _minimal_valid_pack()
    del pack["pack_id"]
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_INVALID_PACK"


def test_validate_pack_blocked_when_missing_pack_version():
    pack = _minimal_valid_pack()
    del pack["pack_version"]
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_INVALID_PACK"


def test_validate_pack_blocked_when_subgraph_refers_missing_node():
    pack = _minimal_valid_pack()
    pack["signal_routes"][0]["active_subgraph"] = ["nonexistent_node"]
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_NODE"


def test_validate_pack_blocked_when_dominant_node_missing():
    pack = _minimal_valid_pack()
    pack["signal_routes"][0]["dominant_node"] = "nonexistent_node"
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_NODE"


def test_validate_pack_blocked_when_signal_routes_empty():
    pack = _minimal_valid_pack()
    pack["signal_routes"] = []
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_ROUTE"


def test_validate_pack_blocked_when_signal_family_duplicated():
    pack = _minimal_valid_pack()
    pack["signal_routes"].append(dict(pack["signal_routes"][0]))
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_ROUTE"


def test_validate_pack_blocked_when_current_unknown_is_list():
    pack = _minimal_valid_pack()
    pack["signal_routes"][0]["current_unknown"] = ["unknown_a", "unknown_b"]
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_CONTRACT_BOUNDARY"


def test_validate_pack_blocked_when_current_unknown_not_in_unknowns():
    pack = _minimal_valid_pack()
    pack["signal_routes"][0]["current_unknown"] = "nonexistent_unknown"
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_UNKNOWN"


def test_validate_pack_blocked_when_evidence_candidate_not_in_candidates():
    pack = _minimal_valid_pack()
    pack["signal_routes"][0]["minimal_evidence_candidate"] = ["nonexistent_evidence"]
    result = validate_functional_pack(pack)
    assert result["status"] == "BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE"


def test_validate_pack_does_not_mutate_input():
    original = _minimal_valid_pack()
    pack_copy = deepcopy(original)
    validate_functional_pack(pack_copy)
    assert pack_copy == original


def test_validate_pack_does_not_emit_confidence_or_scoring():
    result = validate_functional_pack(_minimal_valid_pack())
    assert "confidence_label" not in result
    assert "confidence" not in result
    assert "score" not in result


# --- navigate_single_cycle ---

def test_navigate_passes_with_valid_signal_and_pack():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    assert result["status"] == "SINGLE_CYCLE_ROUTE_CANDIDATE"
    assert result["dominant_node"] == "cash"
    assert result["current_unknown"] == "cobranzas_del_periodo"


def test_navigate_needs_normalized_signal_when_missing_signal_family():
    signal = _minimal_valid_signal()
    del signal["signal_family"]
    result = navigate_single_cycle(signal, _minimal_valid_pack())
    assert result["status"] == "NEEDS_NORMALIZED_SIGNAL"


def test_navigate_needs_normalized_signal_when_missing_signal_id():
    signal = _minimal_valid_signal()
    del signal["signal_id"]
    result = navigate_single_cycle(signal, _minimal_valid_pack())
    assert result["status"] == "NEEDS_NORMALIZED_SIGNAL"


def test_navigate_needs_normalized_signal_when_missing_source():
    signal = _minimal_valid_signal()
    del signal["source"]
    result = navigate_single_cycle(signal, _minimal_valid_pack())
    assert result["status"] == "NEEDS_NORMALIZED_SIGNAL"


def test_navigate_blocked_when_no_route_for_signal_family():
    signal = _minimal_valid_signal()
    signal["signal_family"] = "UNKNOWN_FAMILY"
    result = navigate_single_cycle(signal, _minimal_valid_pack())
    assert result["status"] == "BLOCKED_BY_MISSING_ROUTE"


def test_navigate_blocked_when_duplicate_route_for_signal_family():
    pack = _minimal_valid_pack()
    pack["signal_routes"].append(dict(pack["signal_routes"][0]))
    result = navigate_single_cycle(_minimal_valid_signal(), pack)
    assert result["status"] == "BLOCKED_BY_MISSING_ROUTE"


def test_navigate_copies_active_subgraph_without_calculating_distance():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    assert result["active_subgraph"] == ["sales", "collections", "cash"]


def test_navigate_emits_single_current_unknown():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    assert isinstance(result["current_unknown"], str)
    assert result["current_unknown"] == "cobranzas_del_periodo"


def test_navigate_preserves_formula_reference_as_reference():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    assert result["current_formula_reference"] == "ratio_cobranza"


def test_navigate_preserves_minimal_evidence_candidate_without_certifying():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    assert result["minimal_evidence_candidate"] == ["cobranzas_del_periodo"]
    assert result["boundary_check"]["certified_evidence_sufficiency"] is False


def test_navigate_preserves_full_boundary_check():
    result = navigate_single_cycle(_minimal_valid_signal(), _minimal_valid_pack())
    bc = result["boundary_check"]
    assert bc["calculated_formula"] is False
    assert bc["diagnosed_pathology"] is False
    assert bc["interpreted_pathology"] is False
    assert bc["certified_evidence_sufficiency"] is False
    assert bc["selected_treatment"] is False
    assert bc["rendered_owner_message"] is False
    assert bc["executed_runtime"] is False
    assert bc["became_orchestrator"] is False


def test_navigate_does_not_use_text_ref_for_inference():
    signal = _minimal_valid_signal()
    signal["text_ref"] = "some free text that should not be used"
    result = navigate_single_cycle(signal, _minimal_valid_pack())
    assert result["status"] == "SINGLE_CYCLE_ROUTE_CANDIDATE"
    assert result["dominant_node"] == "cash"


def test_navigate_does_not_mutate_signal_or_pack():
    original_signal = _minimal_valid_signal()
    original_pack = _minimal_valid_pack()
    signal_copy = deepcopy(original_signal)
    pack_copy = deepcopy(original_pack)
    navigate_single_cycle(signal_copy, pack_copy)
    assert signal_copy == original_signal
    assert pack_copy == original_pack


# --- imports / frontera ---

def test_module_does_not_import_forbidden_services():
    source = Path("pymia/smartpyme/functional_pack_loader_navigator.py").read_text(encoding="utf-8")
    assert "pymia.services.formula_engine_service" not in source
    assert "pymia.diagnostic_core" not in source
    assert "pymia.audit_result.core_delivery_bridge" not in source
    assert "pymia.smartpyme.owner_questions_builder" not in source
    assert "pymia.smartpyme.owner_answers_evaluator" not in source
    assert "pymia.smartpyme.owner_action_pipeline" not in source
    assert "pymia.orchestration.graph" not in source


def test_module_does_not_import_owner_contracts():
    source = Path("pymia/smartpyme/functional_pack_loader_navigator.py").read_text(encoding="utf-8")
    assert "pymia.contracts.owner_questions" not in source
    assert "pymia.contracts.owner_answers" not in source
    assert "pymia.contracts.owner_evaluation" not in source
    assert "pymia.contracts.owner_actions" not in source
    assert "pymia.contracts.owner_resolved_actions" not in source


def test_module_does_not_import_forbidden_libraries():
    source = Path("pymia/smartpyme/functional_pack_loader_navigator.py").read_text(encoding="utf-8")
    assert "openai" not in source
    assert "langchain" not in source
    assert "langgraph" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "pandas" not in source
    assert "polars" not in source
    assert "sqlite3" not in source
    assert "sqlalchemy" not in source
    assert "subprocess" not in source
