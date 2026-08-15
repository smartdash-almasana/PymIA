"""Canonical deterministic semantic composition root for Servicio 1.

Composes existing ingestion-to-semantic, owner-confirmation and semantic gate
components. It contains no parsing, semantic rules, catalog logic, tool
execution, delivery or frontend behavior.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

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
from pymia.smartpyme.service_1_computability_v1 import (
    build_service_1_computability_decision_v1,
)

SCHEMA_VERSION = "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1"
STATUS_CONFIRMED_BINDINGS = "CONFIRMED_BINDINGS"
STATUS_OWNER_QUESTIONS = "OWNER_QUESTIONS"
STATUS_OWNER_FOLLOWUP = "OWNER_FOLLOWUP_REQUIRED"
STATUS_BLOCKED_PIPELINE = "BLOCKED"


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
        loop = build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1(
            gate_packet=gate,
            owner_answers=None,
        )
        if loop.get("status") != "OWNER_CONFIRMATION_REQUIRED":
            return _packet(
                status=STATUS_BLOCKED_PIPELINE,
                blocked_reason=loop.get("blocked_reason") or "OWNER_QUESTION_COMPOSITION_BLOCKED",
                bridge_packet=bridge,
                gate_packet=gate,
                owner_loop_packet=loop,
            )
        return _packet(
            status=STATUS_OWNER_QUESTIONS,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=loop,
            owner_questions=list(loop.get("owner_questions") or []),
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
        followup_loop = build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1(
            gate_packet=reinjected,
            owner_answers=None,
        )
        if followup_loop.get("status") != "OWNER_CONFIRMATION_REQUIRED":
            return _packet(
                status=STATUS_BLOCKED_PIPELINE,
                blocked_reason=followup_loop.get("blocked_reason") or "OWNER_QUESTION_COMPOSITION_BLOCKED",
                bridge_packet=bridge,
                gate_packet=gate,
                owner_loop_packet=followup_loop,
                reentry_packet=reinjected,
            )
        return _packet(
            status=STATUS_OWNER_QUESTIONS,
            bridge_packet=bridge,
            gate_packet=gate,
            owner_loop_packet=followup_loop,
            reentry_packet=reinjected,
            owner_questions=list(followup_loop.get("owner_questions") or []),
        )
    return _packet(
        status=STATUS_BLOCKED_PIPELINE,
        blocked_reason=reinjected.get("blocked_reason") or "OWNER_REENTRY_BLOCKED",
        bridge_packet=bridge,
        gate_packet=gate,
        owner_loop_packet=loop,
        reentry_packet=reinjected,
    )



def build_computability_decision_from_confirmed_bindings_v1(
    *,
    confirmed_bindings: Any,
    requested_capability: str,
    derived_evidence_packet: Mapping[str, Any] | None = None,
    formula_catalog_path: str | Path | None = None,
    pathology_catalog_path: str | Path | None = None,
    evidence_matrix_path: str | Path | None = None,
) -> Any:
    """Build canonical P8 decision from an already-confirmed semantic run."""
    if not isinstance(confirmed_bindings, dict):
        raise ValueError("confirmed_bindings must be a dict")
    if confirmed_bindings.get("schema_version") != SCHEMA_VERSION or confirmed_bindings.get("status") != STATUS_CONFIRMED_BINDINGS:
        raise ValueError("confirmed bindings are required")
    capability = str(requested_capability or "").strip()
    if not capability:
        raise ValueError("requested_capability is required")
    evidence = _confirmed_evidence_packet(confirmed_bindings)
    if evidence is None:
        raise ValueError("confirmed evidence packet is missing")
    case_id = str(evidence.get("case_id") or (confirmed_bindings.get("bridge_packet") or {}).get("case_id") or "").strip()
    if not case_id:
        raise ValueError("case_id is required")
    return build_service_1_computability_decision_v1(
        case_id=case_id,
        requested_capability=capability,
        p6_decisions=list(evidence.get("p6_decisions") or []),
        requirement_matches=list(evidence.get("requirement_matches") or []),
        derived_evidence_packet=derived_evidence_packet,
        formula_catalog_path=formula_catalog_path,
        pathology_catalog_path=pathology_catalog_path,
        evidence_matrix_path=evidence_matrix_path,
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
        merged["p6_decisions"] = gate.get("p6_decisions", [])
        merged["requirement_matches"] = gate.get("requirement_matches", [])
        return merged
    return None



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
    "run_initial_pass",
    "run_owner_reentry",
    "build_computability_decision_from_confirmed_bindings_v1",
]
