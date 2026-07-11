"""
Service 1 Owner Authorized Plan -> Controlled Dry Run Result V1

Fail-closed, deterministic DRY-RUN result for the Servicio 1 assisted flow.

Flow position:

    owner_authorization_dialogue (ACCEPTED) -> controlled DRY-RUN result (this module)

The module takes an ACCEPTED owner authorization dialogue and produces a
controlled, auditable dry-run result. It performs ONLY an internal,
deterministic simulation of the plan's steps (validate_column /
prepare_computation). It NEVER executes external tools, NEVER writes files,
NEVER creates delivery, and NEVER authorizes runtime/product/delivery/diagnosis.

By contract:
- ``dry_run_executed`` is True (the simulation ran),
- ``execution_executed`` is False (no real/external execution),
- ``delivery_created`` / ``product_ready`` / ``delivery_authorized`` /
  ``diagnosis_generated`` / ``runtime_authorized`` / ``tool_execution_authorized``
  are all False.
"""

from __future__ import annotations

from typing import Any, Final, Optional

from pymia.smartpyme.service_1_plan_packet_to_owner_authorization_dialogue_v1 import (
    STATUS_ACCEPTED as DIALOGUE_STATUS_ACCEPTED,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_AUTHORIZED_PLAN_TO_CONTROLLED_DRY_RUN_RESULT_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "OWNER_AUTHORIZED_PLAN_TO_CONTROLLED_DRY_RUN_RESULT"

STATUS_READY = "CONTROLLED_DRY_RUN_RESULT_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_INPUT_NOT_DICT = "DIALOGUE_PACKET_NOT_DICT"
BLOCK_INPUT_FLAGS_FORBIDDEN = "DIALOGUE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_NOT_ACCEPTED = "DIALOGUE_NOT_ACCEPTED"
BLOCK_MISSING_PLANNED_STEPS = "MISSING_PLANNED_STEPS"
BLOCK_INVALID_STEP = "INVALID_STEP"

_REQUEST_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)

_INPUT_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)

_VALID_ACTIONS: Final[set[str]] = {"validate_column", "prepare_computation"}


def build_service_1_owner_authorized_plan_to_controlled_dry_run_result_v1(
    *,
    owner_authorization_dialogue_packet: Any,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Run a controlled dry-run simulation from an ACCEPTED authorization dialogue.

    Returns:
        A dry-run result packet dict. Status is CONTROLLED_DRY_RUN_RESULT_READY
        or BLOCKED (with ``blocked_reason``).
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(owner_authorization_dialogue_packet, dict) or not owner_authorization_dialogue_packet:
        return _blocked(BLOCK_INPUT_NOT_DICT)

    if any(owner_authorization_dialogue_packet.get(flag) for flag in _INPUT_FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_INPUT_FLAGS_FORBIDDEN,
            case_id=owner_authorization_dialogue_packet.get("case_id"),
            source_kind=owner_authorization_dialogue_packet.get("source_kind"),
            filename=owner_authorization_dialogue_packet.get("filename"),
        )

    # Only an explicit ACCEPT enables the dry run.
    if owner_authorization_dialogue_packet.get("status") != DIALOGUE_STATUS_ACCEPTED:
        return _blocked(
            BLOCK_NOT_ACCEPTED,
            case_id=owner_authorization_dialogue_packet.get("case_id"),
            source_kind=owner_authorization_dialogue_packet.get("source_kind"),
            filename=owner_authorization_dialogue_packet.get("filename"),
        )

    planned_steps = owner_authorization_dialogue_packet.get("planned_steps")
    if not isinstance(planned_steps, (list, tuple)) or not planned_steps:
        return _blocked(
            BLOCK_MISSING_PLANNED_STEPS,
            case_id=owner_authorization_dialogue_packet.get("case_id"),
            source_kind=owner_authorization_dialogue_packet.get("source_kind"),
            filename=owner_authorization_dialogue_packet.get("filename"),
        )

    simulation_results: list[dict[str, Any]] = []
    for index, step in enumerate(planned_steps):
        if not isinstance(step, dict) or "action" not in step:
            return _blocked(
                BLOCK_INVALID_STEP,
                case_id=owner_authorization_dialogue_packet.get("case_id"),
                source_kind=owner_authorization_dialogue_packet.get("source_kind"),
                filename=owner_authorization_dialogue_packet.get("filename"),
            )
        action = str(step.get("action"))
        if action not in _VALID_ACTIONS:
            return _blocked(
                BLOCK_INVALID_STEP,
                case_id=owner_authorization_dialogue_packet.get("case_id"),
                source_kind=owner_authorization_dialogue_packet.get("source_kind"),
                filename=owner_authorization_dialogue_packet.get("filename"),
            )
        simulation_results.append(
            _simulate_step(step_index=index, step=step)
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": owner_authorization_dialogue_packet.get("case_id"),
        "source_kind": owner_authorization_dialogue_packet.get("source_kind"),
        "filename": owner_authorization_dialogue_packet.get("filename"),
        "step_count": len(simulation_results),
        "roles": list(owner_authorization_dialogue_packet.get("roles") or []),
        "results": simulation_results,
        "dry_run_executed": True,
        "execution_executed": False,
        "delivery_created": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
    }


def _simulate_step(*, step_index: int, step: dict[str, Any]) -> dict[str, Any]:
    """Deterministic internal simulation of a single planned step.

    No files are written; no external tool is invoked. The simulation is a pure
    function of the step's action/target.
    """
    action = str(step.get("action"))
    target = step.get("target")
    if action == "validate_column":
        outcome = "column_validated"
        detail = f"column '{target}' schema-validated (no external read)"
    elif action == "prepare_computation":
        outcome = "computation_prepared"
        detail = f"computation for role '{target}' staged (not executed)"
    else:  # pragma: no cover - guarded by caller
        outcome = "unhandled"
        detail = f"unknown action '{action}'"

    return {
        "step": step_index + 1,
        "action": action,
        "target": target,
        "dry_run_outcome": outcome,
        "detail": detail,
        "dry_run_executed": True,
        "execution_executed": False,
        "delivery_created": False,
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
        "step_count": 0,
        "roles": [],
        "results": [],
        "dry_run_executed": False,
        "execution_executed": False,
        "delivery_created": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_INPUT_NOT_DICT",
    "BLOCK_INPUT_FLAGS_FORBIDDEN",
    "BLOCK_NOT_ACCEPTED",
    "BLOCK_MISSING_PLANNED_STEPS",
    "BLOCK_INVALID_STEP",
    "build_service_1_owner_authorized_plan_to_controlled_dry_run_result_v1",
]
