"""
Service 1 Controlled Execution Ready -> Plan Packet V1

Auditable, NOT-executed plan packet for the Servicio 1 assisted flow.

Flow position:

    controlled execution gate output (READY) -> execution PLAN packet (this module)

The module takes a gate packet with status CONTROLLED_EXECUTION_CANDIDATE_READY
and emits a deterministic, auditable ``execution_plan_packet`` describing the
steps that COULD be executed. It NEVER executes tools, NEVER creates delivery,
and NEVER authorizes runtime/product/delivery/diagnosis. ``execution_executed``
and ``delivery_created`` are always False.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_READY as GATE_STATUS_READY,
)

SCHEMA_VERSION = "SERVICE_1_CONTROLLED_EXECUTION_READY_TO_PLAN_PACKET_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "CONTROLLED_EXECUTION_READY_TO_PLAN_PACKET"

STATUS_PLAN_READY = "EXECUTION_PLAN_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_GATE_NOT_DICT = "GATE_PACKET_NOT_DICT"
BLOCK_GATE_WRONG_STATUS = "GATE_WRONG_STATUS"
BLOCK_GATE_FLAGS_FORBIDDEN = "GATE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_MISSING_CANDIDATE = "MISSING_CONTROLLED_EXECUTION_CANDIDATE"
BLOCK_NO_CANDIDATES = "NO_CANDIDATES"
BLOCK_NO_ROLES = "NO_ROLES"

_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_controlled_execution_plan_packet_v1(
    *,
    gate_packet: Any,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Build an auditable (never executed) execution plan packet from a READY gate.

    Returns:
        An ``execution_plan_packet`` dict. Status is EXECUTION_PLAN_READY or
        BLOCKED (with ``blocked_reason``).
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(gate_packet, dict) or not gate_packet:
        return _blocked(BLOCK_GATE_NOT_DICT)

    if any(gate_packet.get(flag) for flag in _FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_GATE_FLAGS_FORBIDDEN,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    if gate_packet.get("status") != GATE_STATUS_READY:
        return _blocked(
            BLOCK_GATE_WRONG_STATUS,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    candidate = gate_packet.get("controlled_execution_candidate")
    if not isinstance(candidate, dict) or not candidate:
        return _blocked(
            BLOCK_MISSING_CANDIDATE,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    candidate_columns = list(candidate.get("candidate_columns") or [])
    if not candidate_columns:
        return _blocked(
            BLOCK_NO_CANDIDATES,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    roles = list(candidate.get("candidate_roles") or gate_packet.get("candidate_roles") or [])
    if not roles:
        return _blocked(
            BLOCK_NO_ROLES,
            case_id=gate_packet.get("case_id"),
            source_kind=gate_packet.get("source_kind"),
            filename=gate_packet.get("filename"),
        )

    planned_steps = _build_steps(candidate_columns, roles)

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_PLAN_READY,
        "blocked_reason": None,
        "case_id": gate_packet.get("case_id"),
        "source_kind": gate_packet.get("source_kind"),
        "filename": gate_packet.get("filename"),
        "candidate_count": len(candidate_columns),
        "roles": list(roles),
        "planned_steps": planned_steps,
        "execution_executed": False,
        "delivery_created": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _build_steps(columns: list[str], roles: list[str]) -> list[dict[str, Any]]:
    """Deterministic planned steps derived from the candidate columns/roles."""
    steps: list[dict[str, Any]] = []
    step_index = 0
    for column in columns:
        step_index += 1
        steps.append(
            {
                "step": step_index,
                "action": "validate_column",
                "target": column,
                "execution_executed": False,
                "delivery_created": False,
            }
        )
    matched_roles = [role for role in roles if role in _KNOWN_EXECUTION_ROLES]
    for role in matched_roles:
        step_index += 1
        steps.append(
            {
                "step": step_index,
                "action": "prepare_computation",
                "target": role,
                "execution_executed": False,
                "delivery_created": False,
            }
        )
    return steps


# Roles that correspond to real computation steps in the controlled execution.
_KNOWN_EXECUTION_ROLES = {
    "venta_total",
    "costo_unitario",
    "costo_total",
    "margen",
    "cantidad",
    "stock",
    "pago",
    "cobro",
    "ingreso",
    "egreso",
    "saldo",
    "gasto",
    "impuesto",
    "descuento",
}


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "candidate_count": 0,
        "roles": [],
        "planned_steps": [],
        "execution_executed": False,
        "delivery_created": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_PLAN_READY",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_GATE_NOT_DICT",
    "BLOCK_GATE_WRONG_STATUS",
    "BLOCK_GATE_FLAGS_FORBIDDEN",
    "BLOCK_MISSING_CANDIDATE",
    "BLOCK_NO_CANDIDATES",
    "BLOCK_NO_ROLES",
    "build_service_1_controlled_execution_plan_packet_v1",
]
