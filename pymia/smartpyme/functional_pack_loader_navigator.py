from typing import Any
from copy import deepcopy


def _build_boundary_check(loaded: bool = False, validated: bool = False) -> dict:
    return {
        "loaded_pack": loaded,
        "validated_anatomy": validated,
        "calculated_formula": False,
        "diagnosed_pathology": False,
        "interpreted_pathology": False,
        "certified_evidence_sufficiency": False,
        "selected_treatment": False,
        "rendered_owner_message": False,
        "executed_runtime": False,
        "became_orchestrator": False,
    }


def _error_state(status: str, reason_code: str, **extra: Any) -> dict:
    state = {
        "status": status,
        "pack_id": None,
        "pack_version": None,
        "signal_id": None,
        "dominant_node": None,
        "active_subgraph": [],
        "current_formula_reference": None,
        "current_unknown": None,
        "minimal_evidence_candidate": [],
        "reason_code": reason_code,
        "boundary_check": _build_boundary_check(),
    }
    state.update(extra)
    return state


def _node_ids(pack: dict) -> set:
    return {n["node_id"] for n in pack.get("nodes", [])}


def _formula_ids(pack: dict) -> set:
    return {f["formula_id"] for f in pack.get("formula_references", [])}


def _unknown_ids(pack: dict) -> set:
    return {u["unknown_id"] for u in pack.get("unknowns", [])}


def _evidence_ids(pack: dict) -> set:
    return {e["evidence_id"] for e in pack.get("evidence_candidates", [])}


def validate_functional_pack(pack: dict) -> dict:
    if not isinstance(pack, dict):
        return _error_state("BLOCKED_BY_INVALID_PACK", "PACK_MUST_BE_DICT")

    if "pack_id" not in pack or not isinstance(pack["pack_id"], str) or not pack["pack_id"]:
        return _error_state("BLOCKED_BY_INVALID_PACK", "MISSING_PACK_ID")

    if "pack_version" not in pack or not isinstance(pack["pack_version"], str) or not pack["pack_version"]:
        return _error_state("BLOCKED_BY_INVALID_PACK", "MISSING_PACK_VERSION")

    if "nodes" not in pack or not isinstance(pack["nodes"], list):
        return _error_state("BLOCKED_BY_MISSING_NODE", "MISSING_NODES_SECTION")

    if not pack.get("formula_references"):
        return _error_state("BLOCKED_BY_MISSING_NODE", "MISSING_FORMULA_REFERENCES")

    if not pack.get("signal_routes"):
        return _error_state("BLOCKED_BY_MISSING_ROUTE", "MISSING_SIGNAL_ROUTES")

    if not pack.get("unknowns"):
        return _error_state("BLOCKED_BY_MISSING_UNKNOWN", "MISSING_UNKNOWNS_SECTION")

    if not pack.get("evidence_candidates"):
        return _error_state("BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE", "MISSING_EVIDENCE_CANDIDATES_SECTION")

    node_set = _node_ids(pack)
    formula_set = _formula_ids(pack)
    unknown_set = _unknown_ids(pack)
    evidence_set = _evidence_ids(pack)
    seen_families = {}

    for route in pack["signal_routes"]:
        if not isinstance(route, dict):
            return _error_state("BLOCKED_BY_INVALID_PACK", "ROUTE_MUST_BE_DICT")

        family = route.get("signal_family")
        if not family or not isinstance(family, str):
            return _error_state("BLOCKED_BY_MISSING_ROUTE", "ROUTE_MISSING_SIGNAL_FAMILY")

        if family in seen_families:
            return _error_state("BLOCKED_BY_MISSING_ROUTE", "DUPLICATE_SIGNAL_FAMILY")
        seen_families[family] = True

        dominant = route.get("dominant_node")
        if not dominant or not isinstance(dominant, str):
            return _error_state("BLOCKED_BY_MISSING_NODE", "ROUTE_MISSING_DOMINANT_NODE")

        if dominant not in node_set:
            return _error_state("BLOCKED_BY_MISSING_NODE", "DOMINANT_NODE_NOT_IN_NODES")

        subgraph = route.get("active_subgraph")
        if not subgraph or not isinstance(subgraph, list) or len(subgraph) == 0:
            return _error_state("BLOCKED_BY_MISSING_NODE", "ROUTE_MISSING_ACTIVE_SUBGRAPH")

        for node_id in subgraph:
            if node_id not in node_set:
                return _error_state("BLOCKED_BY_MISSING_NODE", f"SUBGRAPH_NODE_{node_id}_NOT_IN_NODES")

        formula_ref = route.get("formula_reference")
        if not formula_ref or not isinstance(formula_ref, str):
            return _error_state("BLOCKED_BY_MISSING_NODE", "ROUTE_MISSING_FORMULA_REFERENCE")

        if formula_ref not in formula_set:
            return _error_state("BLOCKED_BY_MISSING_NODE", "FORMULA_REFERENCE_NOT_IN_FORMULA_REFERENCES")

        unknown = route.get("current_unknown")
        if not unknown:
            return _error_state("BLOCKED_BY_MISSING_UNKNOWN", "ROUTE_MISSING_CURRENT_UNKNOWN")

        if isinstance(unknown, list):
            return _error_state("BLOCKED_BY_CONTRACT_BOUNDARY", "CURRENT_UNKNOWN_IS_LIST")

        if not isinstance(unknown, str):
            return _error_state("BLOCKED_BY_CONTRACT_BOUNDARY", "CURRENT_UNKNOWN_MUST_BE_STRING")

        if unknown not in unknown_set:
            return _error_state("BLOCKED_BY_MISSING_UNKNOWN", "CURRENT_UNKNOWN_NOT_IN_UNKNOWNS")

        evidence_list = route.get("minimal_evidence_candidate")
        if not evidence_list or not isinstance(evidence_list, list) or len(evidence_list) == 0:
            return _error_state("BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE", "ROUTE_MISSING_EVIDENCE_CANDIDATE")

        for ev_id in evidence_list:
            if ev_id not in evidence_set:
                return _error_state("BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE", f"EVIDENCE_{ev_id}_NOT_IN_CANDIDATES")

        if not route.get("reason_code"):
            return _error_state("BLOCKED_BY_CONTRACT_BOUNDARY", "ROUTE_MISSING_REASON_CODE")

    return {
        "status": "PACK_VALIDATED",
        "pack_id": pack["pack_id"],
        "pack_version": pack["pack_version"],
        "signal_id": None,
        "dominant_node": None,
        "active_subgraph": [],
        "current_formula_reference": None,
        "current_unknown": None,
        "minimal_evidence_candidate": [],
        "reason_code": "PACK_ANATOMY_VALIDATED",
        "boundary_check": _build_boundary_check(loaded=True, validated=True),
    }


def navigate_single_cycle(signal: dict, pack: dict) -> dict:
    if not isinstance(signal, dict):
        return _error_state("NEEDS_NORMALIZED_SIGNAL", "SIGNAL_MUST_BE_DICT")

    if "signal_id" not in signal or not signal["signal_id"]:
        return _error_state("NEEDS_NORMALIZED_SIGNAL", "MISSING_SIGNAL_ID")

    if "signal_family" not in signal or not signal["signal_family"]:
        return _error_state("NEEDS_NORMALIZED_SIGNAL", "MISSING_SIGNAL_FAMILY")

    if "source" not in signal or not signal["source"]:
        return _error_state("NEEDS_NORMALIZED_SIGNAL", "MISSING_SOURCE")

    validation = validate_functional_pack(pack)
    if validation["status"] != "PACK_VALIDATED":
        return validation

    routes = pack.get("signal_routes", [])
    matched = [r for r in routes if r.get("signal_family") == signal["signal_family"]]

    if len(matched) == 0:
        return _error_state("BLOCKED_BY_MISSING_ROUTE", "NO_ROUTE_FOR_SIGNAL_FAMILY",
                            pack_id=pack["pack_id"], pack_version=pack["pack_version"],
                            signal_id=signal["signal_id"])

    if len(matched) > 1:
        return _error_state("BLOCKED_BY_MISSING_ROUTE", "DUPLICATE_ROUTE_FOR_SIGNAL_FAMILY",
                            pack_id=pack["pack_id"], pack_version=pack["pack_version"],
                            signal_id=signal["signal_id"])

    route = matched[0]

    return {
        "status": "SINGLE_CYCLE_ROUTE_CANDIDATE",
        "pack_id": pack["pack_id"],
        "pack_version": pack["pack_version"],
        "signal_id": signal["signal_id"],
        "dominant_node": route["dominant_node"],
        "active_subgraph": list(route["active_subgraph"]),
        "current_formula_reference": route["formula_reference"],
        "current_unknown": route["current_unknown"],
        "minimal_evidence_candidate": list(route["minimal_evidence_candidate"]),
        "reason_code": route["reason_code"],
        "boundary_check": _build_boundary_check(loaded=True, validated=True),
    }
