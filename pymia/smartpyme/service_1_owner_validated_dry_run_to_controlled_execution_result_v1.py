"""
Service 1 Owner Validated Dry Run -> Controlled Execution Result V1

Fail-closed, in-memory controlled execution for the Servicio 1 assisted flow.

Flow position:

    owner_validation_dialogue (ACCEPTED) -> controlled EXECUTION result (this module)

The module takes a validated (OWNER_VALIDATION_ACCEPTED) dry-run candidate and
produces a controlled execution result. The execution runs ONLY in memory:
it replays the analysis steps (validate_column / prepare_computation) into an
executed state. It NEVER invokes external tools, NEVER runs the legacy CLI,
NEVER writes files, and NEVER creates delivery.

By contract:
- ``controlled_execution_executed`` is True (the controlled replay ran),
- ``execution_executed`` is True (the in-memory execution happened),
- ``delivery_created`` / ``product_ready`` / ``delivery_authorized`` /
  ``diagnosis_generated`` / ``runtime_authorized`` / ``tool_execution_authorized``
  are all False.
"""

from __future__ import annotations

from typing import Any, Final, Optional

from pymia.smartpyme.service_1_dry_run_candidate_to_owner_validation_dialogue_v1 import (
    STATUS_ACCEPTED as VALIDATION_STATUS_ACCEPTED,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_VALIDATED_DRY_RUN_TO_CONTROLLED_EXECUTION_RESULT_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "OWNER_VALIDATED_DRY_RUN_TO_CONTROLLED_EXECUTION_RESULT"

STATUS_READY = "CONTROLLED_EXECUTION_RESULT_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_INPUT_NOT_DICT = "VALIDATION_DIALOGUE_NOT_DICT"
BLOCK_INPUT_FLAGS_FORBIDDEN = "VALIDATION_DIALOGUE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_NOT_ACCEPTED = "VALIDATION_NOT_ACCEPTED"
BLOCK_MISSING_ANALYSIS = "MISSING_DRY_RUN_ANALYSIS"
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


def build_service_1_owner_validated_dry_run_to_controlled_execution_result_v1(
    *,
    owner_validation_dialogue_packet: Any,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Produce a controlled execution result from a validated dry-run candidate.

    Returns:
        A controlled execution result packet dict. Status is
        CONTROLLED_EXECUTION_RESULT_READY or BLOCKED (with ``blocked_reason``).
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(owner_validation_dialogue_packet, dict) or not owner_validation_dialogue_packet:
        return _blocked(BLOCK_INPUT_NOT_DICT)

    if any(owner_validation_dialogue_packet.get(flag) for flag in _INPUT_FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_INPUT_FLAGS_FORBIDDEN,
            case_id=owner_validation_dialogue_packet.get("case_id"),
            source_kind=owner_validation_dialogue_packet.get("source_kind"),
            filename=owner_validation_dialogue_packet.get("filename"),
        )

    # Only an explicit validation ACCEPT enables the controlled execution.
    if owner_validation_dialogue_packet.get("status") != VALIDATION_STATUS_ACCEPTED:
        return _blocked(
            BLOCK_NOT_ACCEPTED,
            case_id=owner_validation_dialogue_packet.get("case_id"),
            source_kind=owner_validation_dialogue_packet.get("source_kind"),
            filename=owner_validation_dialogue_packet.get("filename"),
        )

    # The upstream dry-run must have been evaluated and carry analysis steps.
    if not owner_validation_dialogue_packet.get("dry_run_evaluated"):
        return _blocked(
            BLOCK_MISSING_ANALYSIS,
            case_id=owner_validation_dialogue_packet.get("case_id"),
            source_kind=owner_validation_dialogue_packet.get("source_kind"),
            filename=owner_validation_dialogue_packet.get("filename"),
        )

    analysis = owner_validation_dialogue_packet.get("analysis")
    if not isinstance(analysis, (list, tuple)) or not analysis:
        return _blocked(
            BLOCK_MISSING_ANALYSIS,
            case_id=owner_validation_dialogue_packet.get("case_id"),
            source_kind=owner_validation_dialogue_packet.get("source_kind"),
            filename=owner_validation_dialogue_packet.get("filename"),
        )

    execution_results: list[dict[str, Any]] = []
    for index, step in enumerate(analysis):
        if not isinstance(step, dict) or "action" not in step:
            return _blocked(
                BLOCK_INVALID_STEP,
                case_id=owner_validation_dialogue_packet.get("case_id"),
                source_kind=owner_validation_dialogue_packet.get("source_kind"),
                filename=owner_validation_dialogue_packet.get("filename"),
            )
        action = str(step.get("action"))
        if action not in _VALID_ACTIONS:
            return _blocked(
                BLOCK_INVALID_STEP,
                case_id=owner_validation_dialogue_packet.get("case_id"),
                source_kind=owner_validation_dialogue_packet.get("source_kind"),
                filename=owner_validation_dialogue_packet.get("filename"),
            )
        execution_results.append(_execute_step(step_index=index, step=step))

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": owner_validation_dialogue_packet.get("case_id"),
        "source_kind": owner_validation_dialogue_packet.get("source_kind"),
        "filename": owner_validation_dialogue_packet.get("filename"),
        "step_count": len(execution_results),
        "roles": list(owner_validation_dialogue_packet.get("roles") or []),
        "results": execution_results,
        "controlled_execution_executed": True,
        "execution_executed": True,
        "delivery_created": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
    }


def _execute_step(*, step_index: int, step: dict[str, Any]) -> dict[str, Any]:
    """In-memory replay of a validated analysis step into an executed state.

    No files are written; no external tool is invoked. The result is a pure
    function of the step's action/target.
    """
    action = str(step.get("action"))
    target = step.get("target")
    if action == "validate_column":
        outcome = "column_validated_executed"
        detail = f"column '{target}' validated in-memory (no external read)"
    elif action == "prepare_computation":
        outcome = "computation_executed"
        detail = f"computation for role '{target}' prepared in-memory (no write)"
    else:  # pragma: no cover - guarded by caller
        outcome = "unhandled"
        detail = f"unknown action '{action}'"

    return {
        "step": step_index + 1,
        "action": action,
        "target": target,
        "execution_outcome": outcome,
        "detail": detail,
        "controlled_execution_executed": True,
        "execution_executed": True,
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
        "controlled_execution_executed": False,
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
    "BLOCK_MISSING_ANALYSIS",
    "BLOCK_INVALID_STEP",
    "build_service_1_owner_validated_dry_run_to_controlled_execution_result_v1",
]
