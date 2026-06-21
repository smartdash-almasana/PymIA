from __future__ import annotations

from typing import Any, Literal, TypedDict

from pymia.smartpyme.service_1_taskspec_vocabulary_v1 import (
    TaskSpecBlockingState,
    TaskSpecNextAllowedAction,
)

TaskSpecSchemaVersion = Literal["1.0"]
TaskSpecServiceName = Literal["SERVICE_1"]
TaskSpecServiceDepth = Literal["FIRST_AID", "DETERMINISTIC_DIAGNOSIS", "ORGANIZATIONAL_LAB", "UNKNOWN"]
TaskSpecSourceChannel = Literal["cli", "chat", "upload", "api", "unknown"]


class Service1TaskSpecAssetRef(TypedDict, total=False):
    asset_id: str
    file_intake_id: str
    filename: str | None
    detected_file_type: str
    support_status: str
    reason_code: str
    risk_flags: list[str]


class Service1TaskSpecExpectedOutput(TypedDict, total=False):
    output_type: str
    downloadable_file_expected: bool
    owner_facing_summary_expected: bool
    technical_annex_expected: bool
    limitations_required: bool


class Service1TaskSpec(TypedDict):
    task_id: str
    schema_version: TaskSpecSchemaVersion
    service_name: TaskSpecServiceName
    service_depth: TaskSpecServiceDepth
    task_type: str
    owner_problem: str
    owner_requested_output: str | None
    source_channel: TaskSpecSourceChannel
    input_assets: list[Service1TaskSpecAssetRef]
    candidate_capability: str | None
    candidate_tool_ref: str | None
    evidence_required: list[str]
    evidence_received: list[Any]
    missing_evidence: list[str]
    column_confirmation_required: bool
    column_confirmation_fields: list[str]
    requested_formula_refs: list[str]
    requested_claims: list[str]
    forbidden_claims: list[str]
    blocking_state: TaskSpecBlockingState | None
    next_allowed_action: TaskSpecNextAllowedAction
    expected_output: Service1TaskSpecExpectedOutput
    runtime_authorized: bool
    notes: list[str]


def build_minimal_service_1_taskspec(
    *,
    task_id: str,
    owner_problem: str,
    task_type: str = "UNKNOWN",
    service_depth: TaskSpecServiceDepth = "UNKNOWN",
    source_channel: TaskSpecSourceChannel = "unknown",
    next_allowed_action: TaskSpecNextAllowedAction = "block_runtime_until_supported",
    blocking_state: TaskSpecBlockingState | None = "BLOCKED_RUNTIME_NOT_AUTHORIZED",
    notes: list[str] | None = None,
) -> Service1TaskSpec:
    return {
        "task_id": task_id,
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "service_depth": service_depth,
        "task_type": task_type,
        "owner_problem": owner_problem,
        "owner_requested_output": None,
        "source_channel": source_channel,
        "input_assets": [],
        "candidate_capability": None,
        "candidate_tool_ref": None,
        "evidence_required": [],
        "evidence_received": [],
        "missing_evidence": [],
        "column_confirmation_required": False,
        "column_confirmation_fields": [],
        "requested_formula_refs": [],
        "requested_claims": [],
        "forbidden_claims": [],
        "blocking_state": blocking_state,
        "next_allowed_action": next_allowed_action,
        "expected_output": {
            "output_type": "blocked_notice",
            "downloadable_file_expected": False,
            "owner_facing_summary_expected": True,
            "technical_annex_expected": False,
            "limitations_required": True,
        },
        "runtime_authorized": False,
        "notes": list(notes or []),
    }
