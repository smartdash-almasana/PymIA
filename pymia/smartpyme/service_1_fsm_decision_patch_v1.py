from __future__ import annotations
"""EXPERIMENTAL_FROZEN boundary for Service 1 FSM decision projection.

This module is not a runtime FSM, not an active Service 1 delivery lane, and
must not be expanded until a vendible Service 1 contract is closed first.
It is preserved only as an audited experimental boundary for traceability.
"""

from typing import Literal, TypedDict

from pymia.smartpyme.service_1_taskspec_contract_v1 import Service1TaskSpec
from pymia.smartpyme.service_1_taskspec_vocabulary_v1 import TaskSpecBlockingState, TaskSpecNextAllowedAction

FREEZE_STATUS = "EXPERIMENTAL_FROZEN"
FREEZE_REASON = "Scope drift audit: keep for traceability, do not expand before Service 1 product boundary."

Service1FSMState = Literal[
    "TASK_CLASSIFIED",
    "EVIDENCE_REQUESTED",
    "EVIDENCE_RECEIVED",
    "CONFIRMATION_REQUIRED",
    "BLOCKED",
]

Service1FSMDecisionReason = Literal[
    "MISSING_EVIDENCE",
    "COLUMN_CONFIRMATION_REQUIRED",
    "UNSUPPORTED_FILE_TYPE",
    "UNKNOWN_FILE_TYPE",
    "UNSAFE_FILE",
    "RUNTIME_NOT_AUTHORIZED",
    "READY_BUT_HELD",
]


class Service1FSMDecisionPatch(TypedDict):
    service_name: str
    current_state: Service1FSMState
    next_state: Service1FSMState
    decision_reason: Service1FSMDecisionReason
    blocking_state: TaskSpecBlockingState | None
    next_allowed_action: TaskSpecNextAllowedAction
    runtime_authorized: bool
    allowed_to_process: bool
    notes: list[str]


def derive_fsm_decision_patch_from_taskspec(task_spec: Service1TaskSpec) -> Service1FSMDecisionPatch:
    blocking_state = task_spec["blocking_state"]
    next_allowed_action = task_spec["next_allowed_action"]

    if task_spec["missing_evidence"]:
        return _decision("EVIDENCE_REQUESTED", "MISSING_EVIDENCE", "BLOCKED_MISSING_EVIDENCE", next_allowed_action)

    if task_spec["column_confirmation_required"] or blocking_state == "BLOCKED_COLUMN_CONFIRMATION":
        return _decision("CONFIRMATION_REQUIRED", "COLUMN_CONFIRMATION_REQUIRED", "BLOCKED_COLUMN_CONFIRMATION", next_allowed_action)

    if blocking_state == "BLOCKED_UNSUPPORTED_FILE_TYPE":
        return _decision("BLOCKED", "UNSUPPORTED_FILE_TYPE", blocking_state, next_allowed_action)

    if blocking_state == "BLOCKED_UNKNOWN_FILE_TYPE":
        return _decision("BLOCKED", "UNKNOWN_FILE_TYPE", blocking_state, next_allowed_action)

    if blocking_state == "BLOCKED_UNSAFE_FILE":
        return _decision("BLOCKED", "UNSAFE_FILE", blocking_state, next_allowed_action)

    if blocking_state == "BLOCKED_RUNTIME_NOT_AUTHORIZED":
        return _decision("BLOCKED", "RUNTIME_NOT_AUTHORIZED", blocking_state, next_allowed_action)

    return _decision("EVIDENCE_RECEIVED", "READY_BUT_HELD", blocking_state, next_allowed_action)


def _decision(
    next_state: Service1FSMState,
    reason: Service1FSMDecisionReason,
    blocking_state: TaskSpecBlockingState | None,
    next_allowed_action: TaskSpecNextAllowedAction,
) -> Service1FSMDecisionPatch:
    return {
        "service_name": "SERVICE_1",
        "current_state": "TASK_CLASSIFIED",
        "next_state": next_state,
        "decision_reason": reason,
        "blocking_state": blocking_state,
        "next_allowed_action": next_allowed_action,
        "runtime_authorized": False,
        "allowed_to_process": False,
        "notes": [],
    }
