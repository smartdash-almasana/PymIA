"""Canonical deterministic semantic composition root for Servicio 1.

Composes existing ingestion-to-semantic, owner-confirmation and semantic gate
components. It contains no parsing, semantic rules, catalog logic, tool
execution, delivery or frontend behavior.
"""
from __future__ import annotations

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
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_reinjection_to_semantic_gate_v1 import (
    build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1,
)

SCHEMA_VERSION = "SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1"
STATUS_CONFIRMED_BINDINGS = "CONFIRMED_BINDINGS"
STATUS_OWNER_QUESTIONS = "OWNER_QUESTIONS"
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


def _packet(
    *,
    status: str,
    blocked_reason: str | None = None,
    bridge_packet: Any = None,
    gate_packet: Any = None,
    owner_loop_packet: Any = None,
    reentry_packet: Any = None,
    owner_questions: list[dict[str, Any]] | None = None,
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
    "STATUS_BLOCKED_PIPELINE",
    "run_initial_pass",
    "run_owner_reentry",
]
