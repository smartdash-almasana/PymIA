"""Canonical deterministic semantic composition root for Servicio 1.

Composes existing ingestion-to-semantic, owner-confirmation and semantic gate
components. It contains no parsing, semantic rules, catalog logic, tool
execution, delivery or frontend behavior.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as BRIDGE_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_BLOCKED,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY as GATE_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
    STATUS_OWNER_FOLLOWUP_REQUIRED as LOOP_STATUS_OWNER_FOLLOWUP_REQUIRED,
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_reinjection_to_semantic_gate_v1 import (
    build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1,
)
from pymia.smartpyme.service_1_semantic_catalog_loader_v1 import (
    STATUS_CATALOGS_LOADED,
    STATUS_CATALOGS_PARTIALLY_LOADED,
    build_service_1_semantic_catalog_load_result_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    BINDING_STATUS_BOUND_CANDIDATE,
    BINDING_STATUS_BOUND_CONFIRMED,
    BINDING_STATUS_MISSING_REQUIRED_COLUMN,
    BINDING_STATUS_NEEDS_OWNER_CONFIRMATION,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_engine_v1 import (
    build_service_1_semantic_evidence_binding_result_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    STATUS_MISSING_REQUIRED_ROLES as FAMILY_MISSING_REQUIRED_ROLES,
    STATUS_NEEDS_OWNER_CONFIRMATION as FAMILY_NEEDS_OWNER_CONFIRMATION,
    STATUS_NOT_OBSERVED as FAMILY_NOT_OBSERVED,
    STATUS_READY as FAMILY_READY,
    VARIABLE_FAMILY_DEFINITIONS,
)

SCHEMA_VERSION = "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1"
STATUS_CONFIRMED_BINDINGS = "CONFIRMED_BINDINGS"
STATUS_OWNER_QUESTIONS = "OWNER_QUESTIONS"
STATUS_OWNER_FOLLOWUP = "OWNER_FOLLOWUP_REQUIRED"
STATUS_BLOCKED_PIPELINE = "BLOCKED"

COMPUTATION_PLAN_SCHEMA_VERSION = "SERVICE_1_COMPUTATION_PLAN_V1"
STATUS_READY_FOR_COMPUTATION = "READY_FOR_COMPUTATION"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_NEEDS_OWNER_CONFIRMATION_PLAN = "NEEDS_OWNER_CONFIRMATION"
STATUS_UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
STATUS_BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
STATUS_COMPUTATION_PLAN_BLOCKED = "BLOCKED"

_ALLOWED_CATALOG_LOAD_STATUSES = {
    STATUS_CATALOGS_LOADED,
    STATUS_CATALOGS_PARTIALLY_LOADED,
}


def run_initial_pass(
    *, ingestion_output: Any, sheet_name: str = "sheet1"
) -> dict[str, Any]:
    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=ingestion_output,
        sheet_name=sheet_name,
    )
    if bridge.get("status") != BRIDGE_READY:
        return _packet(
            status=STATUS_BLOCKED_PIPELINE,
            blocked_reason=bridge.get("blocked_reason") or "SEMANTIC_BRIDGE_BLOCKED",
            bridge_packet=bridge,
        )

    gate = build_service_1_controlled_execution_gate_from_semantic_bridge_v1(
        semantic_bridge_packet=bridge
    )
    if gate.get("status") == STATUS_NEEDS_OWNER_CONFIRMATION:
        return _packet(
            status=STATUS_OWNER_QUESTIONS,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_questions=list(gate.get("owner_questions") or []),
        )
    if gate.get("status") == GATE_READY:
        return _packet(
            status=STATUS_CONFIRMED_BINDINGS,
            bridge_packet=bridge,
            gate_packet=gate,
            confirmed_candidate=gate.get("controlled_execution_candidate"),
        )
    return _packet(
        status=STATUS_BLOCKED_PIPELINE,
        blocked_reason=gate.get("blocked_reason") or "SEMANTIC_GATE_BLOCKED",
        bridge_packet=bridge,
        gate_packet=gate,
    )


def run_owner_reentry(
    *, previous_run: Any, owner_answers: Any
) -> dict[str, Any]:
    if not isinstance(previous_run, dict) or previous_run.get("schema_version") != SCHEMA_VERSION:
        return _packet(status=STATUS_BLOCKED_PIPELINE, blocked_reason="INVALID_PREVIOUS_RUN")
    if previous_run.get("status") != STATUS_OWNER_QUESTIONS:
        return _packet(status=STATUS_BLOCKED_PIPELINE, blocked_reason="PREVIOUS_RUN_NOT_WAITING_OWNER")
    bridge = previous_run.get("bridge_packet")
    gate = previous_run.get("gate_packet")
    if not isinstance(bridge, dict) or not isinstance(gate, dict):
        return _packet(status=STATUS_BLOCKED_PIPELINE, blocked_reason="MISSING_PIPELINE_PACKETS")
    if not isinstance(owner_answers, dict) or not owner_answers:
        return _packet(status=STATUS_BLOCKED_PIPELINE, blocked_reason="OWNER_ANSWERS_REQUIRED")

    loop = build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1(
        gate_packet=gate,
        owner_answers=owner_answers,
    )
    if loop.get("status") == LOOP_STATUS_OWNER_FOLLOWUP_REQUIRED:
        return _packet(
            status=STATUS_OWNER_FOLLOWUP,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=loop,
            owner_questions=list(loop.get("owner_questions") or []),
            owner_followup=list(loop.get("owner_followup") or []),
        )
    if loop.get("status") != STATUS_OWNER_CONFIRMATION_RECHECK_READY:
        return _packet(
            status=STATUS_BLOCKED_PIPELINE,
            blocked_reason=loop.get("blocked_reason")
            or "OWNER_CONFIRMATION_LOOP_BLOCKED",
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=loop,
            owner_questions=list(previous_run.get("owner_questions") or []),
        )

    reinjected = build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1(
        semantic_bridge_packet=bridge,
        owner_confirmation_loop_packet=loop,
    )
    if reinjected.get("status") == GATE_READY:
        return _packet(
            status=STATUS_CONFIRMED_BINDINGS,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=loop,
            reentry_packet=reinjected,
            confirmed_candidate=reinjected.get("controlled_execution_candidate"),
        )
    if reinjected.get("status") == STATUS_NEEDS_OWNER_CONFIRMATION:
        return _packet(
            status=STATUS_OWNER_QUESTIONS,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=loop,
            reentry_packet=reinjected,
            owner_questions=list(reinjected.get("owner_questions") or []),
        )
    return _packet(
        status=STATUS_BLOCKED_PIPELINE,
        blocked_reason=reinjected.get("blocked_reason") or "OWNER_REENTRY_BLOCKED",
        bridge_packet=bridge,
        gate_packet=gate,
        owner_loop_packet=loop,
        reentry_packet=reinjected,
    )



def build_computation_plan(
    *,
    confirmed_bindings: Any,
    requested_capability: str,
    formula_catalog_path: str | Path | None = None,
    pathology_catalog_path: str | Path | None = None,
    evidence_matrix_path: str | Path | None = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Build the governed P7/P8 computation plan without executing anything.

    The function consumes only a CONFIRMED_BINDINGS packet produced by this
    composition root. It matches one requested business capability against a
    ready variable family, the governed formula/pathology matrix and the
    retained semantic evidence binding engine. READY_FOR_COMPUTATION means that
    one specific formula candidate has confirmed inputs; it never authorizes
    runtime, a tool, product readiness, delivery or diagnosis.
    """
    if any(
        (
            runtime_authorized,
            tool_execution_authorized,
            product_ready,
            delivery_authorized,
            diagnosis_generated,
        )
    ):
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="REQUEST_SAFETY_FLAGS_FORBIDDEN",
            requested_capability=requested_capability,
        )

    capability = str(requested_capability or "").strip()
    if not capability:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="REQUESTED_CAPABILITY_REQUIRED",
        )
    if (
        not isinstance(confirmed_bindings, dict)
        or confirmed_bindings.get("schema_version") != SCHEMA_VERSION
        or confirmed_bindings.get("status") != STATUS_CONFIRMED_BINDINGS
    ):
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="CONFIRMED_BINDINGS_REQUIRED",
            requested_capability=capability,
        )
    if any(
        confirmed_bindings.get(flag)
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    ):
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="CONFIRMED_BINDINGS_SAFETY_FLAGS_FORBIDDEN",
            requested_capability=capability,
        )

    evidence = _confirmed_evidence_packet(confirmed_bindings)
    if evidence is None:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="CONFIRMED_EVIDENCE_PACKET_MISSING",
            requested_capability=capability,
        )
    candidates = tuple(evidence.get("column_candidates") or ())
    family_bindings = tuple(evidence.get("variable_family_bindings") or ())
    if not candidates or not family_bindings:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="CONFIRMED_EVIDENCE_INCOMPLETE",
            requested_capability=capability,
        )

    family_definition = next(
        (
            definition
            for definition in VARIABLE_FAMILY_DEFINITIONS
            if capability in definition.target_capabilities
        ),
        None,
    )
    if family_definition is None:
        return _computation_plan_packet(
            status=STATUS_UNSUPPORTED_CAPABILITY,
            blocked_reason="CAPABILITY_NOT_GOVERNED",
            requested_capability=capability,
        )
    family_binding = next(
        (
            binding
            for binding in family_bindings
            if getattr(binding, "family_id", None) == family_definition.family_id
        ),
        None,
    )
    if family_binding is None:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="VARIABLE_FAMILY_BINDING_MISSING",
            requested_capability=capability,
            family_id=family_definition.family_id,
        )

    family_status = str(getattr(family_binding, "status", ""))
    missing_role_groups = [
        list(group) for group in getattr(family_binding, "missing_role_groups", ())
    ]
    ambiguous_role_groups = [
        list(group) for group in getattr(family_binding, "ambiguous_role_groups", ())
    ]
    if family_status == FAMILY_NEEDS_OWNER_CONFIRMATION:
        return _computation_plan_packet(
            status=STATUS_NEEDS_OWNER_CONFIRMATION_PLAN,
            blocked_reason="VARIABLE_FAMILY_NEEDS_OWNER_CONFIRMATION",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            missing_role_groups=missing_role_groups,
            ambiguous_role_groups=ambiguous_role_groups,
        )
    if family_status in {FAMILY_MISSING_REQUIRED_ROLES, FAMILY_NOT_OBSERVED}:
        return _computation_plan_packet(
            status=STATUS_NEEDS_EVIDENCE,
            blocked_reason="VARIABLE_FAMILY_NOT_READY",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            missing_role_groups=missing_role_groups,
            ambiguous_role_groups=ambiguous_role_groups,
        )
    if family_status != FAMILY_READY:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="UNSUPPORTED_VARIABLE_FAMILY_STATUS",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
        )

    paths = _catalog_paths(
        formula_catalog_path=formula_catalog_path,
        pathology_catalog_path=pathology_catalog_path,
        evidence_matrix_path=evidence_matrix_path,
    )
    try:
        matrix_payload = _load_json_object(paths["evidence_matrix"])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason=f"EVIDENCE_MATRIX_INVALID:{exc}",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
        )
    if matrix_payload.get("computation_candidate_planning_allowed") is not True:
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="MATRIX_COMPUTATION_PLANNING_NOT_ALLOWED",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
        )
    matrix_entries = [
        entry
        for entry in matrix_payload.get("entries", [])
        if isinstance(entry, dict)
        and capability in tuple(entry.get("capability_refs") or ())
    ]
    if not matrix_entries:
        return _computation_plan_packet(
            status=STATUS_UNSUPPORTED_CAPABILITY,
            blocked_reason="CAPABILITY_HAS_NO_GOVERNED_FORMULA_MAPPING",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
        )
    if len(matrix_entries) != 1:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="AMBIGUOUS_CAPABILITY_FORMULA_MAPPING",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
        )
    matrix_entry = matrix_entries[0]
    if (
        matrix_entry.get("semantic_binding_candidate_allowed") is not True
        or matrix_entry.get("computation_candidate_allowed") is not True
    ):
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="COMPUTATION_CANDIDATE_NOT_ALLOWED",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=str(matrix_entry.get("pathology_code") or "") or None,
        )

    formula_refs = tuple(
        str(value).strip()
        for value in matrix_entry.get("formula_refs", [])
        if str(value).strip()
    )
    pathology_code = str(matrix_entry.get("pathology_code") or "").strip()
    if len(formula_refs) != 1 or not pathology_code:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="MATRIX_MAPPING_MUST_RESOLVE_ONE_FORMULA",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code or None,
        )

    catalog_result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=paths["formula_catalog"],
        pathology_catalog_path=paths["pathology_catalog"],
        metadata={"requested_capability": capability},
    )
    if catalog_result.status not in _ALLOWED_CATALOG_LOAD_STATUSES:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason=f"CATALOG_LOAD_BLOCKED:{catalog_result.status}",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula_refs[0],
        )

    formulas = tuple(
        entry
        for entry in catalog_result.formula_entries
        if entry.formula_id == formula_refs[0]
        and entry.pathology_code == pathology_code
    )
    pathologies = tuple(
        entry
        for entry in catalog_result.pathology_entries
        if entry.pathology_code == pathology_code
    )
    if len(formulas) != 1 or len(pathologies) != 1:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="GOVERNED_FORMULA_OR_PATHOLOGY_MISSING",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula_refs[0],
        )
    formula = formulas[0]
    required_variables = tuple(
        str(value).strip()
        for value in matrix_entry.get("required_variables", [])
        if str(value).strip()
    )
    if required_variables != formula.required_variables:
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="MATRIX_FORMULA_VARIABLE_DRIFT",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
            required_variables=list(formula.required_variables),
        )
    if not set(formula.required_variables).issubset(
        set(family_definition.target_variable_names)
    ):
        return _computation_plan_packet(
            status=STATUS_BLOCKED_BY_POLICY,
            blocked_reason="FORMULA_OUTSIDE_VARIABLE_FAMILY_SCOPE",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
            required_variables=list(formula.required_variables),
        )
    if formula.calculation_state != "CALCULABLE":
        return _computation_plan_packet(
            status=STATUS_NEEDS_EVIDENCE,
            blocked_reason="FORMULA_REQUIRES_ADDITIONAL_ASSUMPTIONS",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
            required_variables=list(formula.required_variables),
        )

    case_id = str(
        evidence.get("case_id")
        or (confirmed_bindings.get("bridge_packet") or {}).get("case_id")
        or ""
    ).strip()
    if not case_id:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="CASE_ID_REQUIRED_FOR_COMPUTATION_PLAN",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
        )

    binding_result = build_service_1_semantic_evidence_binding_result_v1(
        case_id=case_id,
        column_candidates=candidates,
        formula_entries=formulas,
        pathology_entries=pathologies,
        metadata={
            "requested_capability": capability,
            "variable_family_id": family_definition.family_id,
            "matrix_catalog_version": matrix_payload.get("catalog_version"),
        },
    )
    formula_candidate = next(
        (
            candidate
            for candidate in binding_result.pathology_formula_candidates
            if candidate.formula_id == formula.formula_id
        ),
        None,
    )
    bindings = tuple(
        binding
        for binding in binding_result.bindings
        if binding.formula_id == formula.formula_id
    )
    source_bindings = {
        binding.variable_name: binding.source_column_name
        for binding in bindings
        if binding.binding_status
        in {BINDING_STATUS_BOUND_CONFIRMED, BINDING_STATUS_BOUND_CANDIDATE}
    }
    pending_variables = [
        binding.variable_name
        for binding in bindings
        if binding.binding_status == BINDING_STATUS_NEEDS_OWNER_CONFIRMATION
    ]
    missing_variables = [
        binding.variable_name
        for binding in bindings
        if binding.binding_status == BINDING_STATUS_MISSING_REQUIRED_COLUMN
    ]
    if pending_variables:
        return _computation_plan_packet(
            status=STATUS_NEEDS_OWNER_CONFIRMATION_PLAN,
            blocked_reason="FORMULA_BINDINGS_NEED_OWNER_CONFIRMATION",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
            required_variables=list(formula.required_variables),
            pending_variables=pending_variables,
            source_bindings=source_bindings,
            semantic_binding_result=binding_result.to_dict(),
            catalog_versions=_catalog_versions(paths, matrix_payload),
        )
    if missing_variables or formula.formula_id not in binding_result.ready_formula_ids:
        return _computation_plan_packet(
            status=STATUS_NEEDS_EVIDENCE,
            blocked_reason="FORMULA_INPUTS_NOT_READY",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
            required_variables=list(formula.required_variables),
            missing_variables=missing_variables,
            source_bindings=source_bindings,
            semantic_binding_result=binding_result.to_dict(),
            catalog_versions=_catalog_versions(paths, matrix_payload),
        )
    if formula_candidate is None:
        return _computation_plan_packet(
            status=STATUS_COMPUTATION_PLAN_BLOCKED,
            blocked_reason="FORMULA_CANDIDATE_MISSING",
            requested_capability=capability,
            family_id=family_definition.family_id,
            family_status=family_status,
            pathology_code=pathology_code,
            formula_id=formula.formula_id,
        )

    return _computation_plan_packet(
        status=STATUS_READY_FOR_COMPUTATION,
        blocked_reason=None,
        requested_capability=capability,
        family_id=family_definition.family_id,
        family_status=family_status,
        pathology_code=pathology_code,
        formula_id=formula.formula_id,
        formula_expression=formula.expression,
        calculation_state=formula.calculation_state,
        required_variables=list(formula.required_variables),
        required_evidence=list(formula.required_evidence),
        source_bindings=source_bindings,
        semantic_binding_result=binding_result.to_dict(),
        catalog_versions=_catalog_versions(paths, matrix_payload),
        computation_candidate_ready=True,
    )


def _confirmed_evidence_packet(confirmed_bindings: dict[str, Any]) -> dict[str, Any] | None:
    reentry = confirmed_bindings.get("reentry_packet")
    if isinstance(reentry, dict) and reentry.get("column_candidates"):
        return reentry
    bridge = confirmed_bindings.get("bridge_packet")
    gate = confirmed_bindings.get("gate_packet")
    if isinstance(bridge, dict) and isinstance(gate, dict):
        merged = dict(bridge)
        merged["variable_family_bindings"] = gate.get("variable_family_bindings", ())
        merged["ready_variable_family_ids"] = gate.get("ready_variable_family_ids", [])
        return merged
    return None


def _catalog_paths(
    *,
    formula_catalog_path: str | Path | None,
    pathology_catalog_path: str | Path | None,
    evidence_matrix_path: str | Path | None,
) -> dict[str, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    docs_root = repo_root / "docs"
    return {
        "formula_catalog": Path(formula_catalog_path) if formula_catalog_path else docs_root / "formula_catalog.v1.json",
        "pathology_catalog": Path(pathology_catalog_path) if pathology_catalog_path else docs_root / "pathology_catalog.enriched.v1.json",
        "evidence_matrix": Path(evidence_matrix_path) if evidence_matrix_path else docs_root / "service_1_formula_pathology_evidence_matrix.v1.json",
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise OSError(f"file_not_found:{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_root_not_object:{path}")
    return payload


def _catalog_versions(paths: dict[str, Path], matrix_payload: dict[str, Any]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {
        "formula_catalog": None,
        "pathology_catalog": None,
        "evidence_matrix": str(matrix_payload.get("catalog_version") or "") or None,
    }
    for key in ("formula_catalog", "pathology_catalog"):
        try:
            versions[key] = str(_load_json_object(paths[key]).get("catalog_version") or "") or None
        except (OSError, ValueError, json.JSONDecodeError):
            versions[key] = None
    return versions


def _computation_plan_packet(
    *,
    status: str,
    blocked_reason: str | None,
    requested_capability: str | None = None,
    family_id: str | None = None,
    family_status: str | None = None,
    pathology_code: str | None = None,
    formula_id: str | None = None,
    formula_expression: str | None = None,
    calculation_state: str | None = None,
    required_variables: list[str] | None = None,
    required_evidence: list[str] | None = None,
    missing_role_groups: list[list[str]] | None = None,
    ambiguous_role_groups: list[list[str]] | None = None,
    missing_variables: list[str] | None = None,
    pending_variables: list[str] | None = None,
    source_bindings: dict[str, str] | None = None,
    semantic_binding_result: dict[str, Any] | None = None,
    catalog_versions: dict[str, str | None] | None = None,
    computation_candidate_ready: bool = False,
) -> dict[str, Any]:
    return {
        "schema_version": COMPUTATION_PLAN_SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "packet_type": "COMPUTATION_PLAN",
        "status": status,
        "blocked_reason": blocked_reason,
        "requested_capability": requested_capability,
        "family_id": family_id,
        "family_status": family_status,
        "pathology_code": pathology_code,
        "formula_id": formula_id,
        "formula_expression": formula_expression,
        "calculation_state": calculation_state,
        "required_variables": list(required_variables or []),
        "required_evidence": list(required_evidence or []),
        "missing_role_groups": list(missing_role_groups or []),
        "ambiguous_role_groups": list(ambiguous_role_groups or []),
        "missing_variables": list(missing_variables or []),
        "pending_variables": list(pending_variables or []),
        "source_bindings": dict(source_bindings or {}),
        "semantic_binding_result": semantic_binding_result,
        "catalog_versions": dict(catalog_versions or {}),
        "computation_candidate_ready": bool(computation_candidate_ready),
        "computation_executed": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }



def _packet(
    *,
    status: str,
    blocked_reason: str | None = None,
    bridge_packet: Any = None,
    gate_packet: Any = None,
    owner_loop_packet: Any = None,
    reentry_packet: Any = None,
    owner_questions: list[dict[str, Any]] | None = None,
    owner_followup: list[dict[str, Any]] | None = None,
    confirmed_candidate: Any = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "status": status,
        "blocked_reason": blocked_reason,
        "bridge_packet": bridge_packet,
        "gate_packet": gate_packet,
        "owner_loop_packet": owner_loop_packet,
        "reentry_packet": reentry_packet,
        "owner_questions": list(owner_questions or []),
        "owner_followup": [dict(item) for item in (owner_followup or [])],
        "confirmed_candidate": confirmed_candidate,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_CONFIRMED_BINDINGS",
    "STATUS_OWNER_QUESTIONS",
    "STATUS_OWNER_FOLLOWUP",
    "STATUS_BLOCKED_PIPELINE",
    "COMPUTATION_PLAN_SCHEMA_VERSION",
    "STATUS_READY_FOR_COMPUTATION",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_NEEDS_OWNER_CONFIRMATION_PLAN",
    "STATUS_UNSUPPORTED_CAPABILITY",
    "STATUS_BLOCKED_BY_POLICY",
    "STATUS_COMPUTATION_PLAN_BLOCKED",
    "run_initial_pass",
    "run_owner_reentry",
    "build_computation_plan",
]
