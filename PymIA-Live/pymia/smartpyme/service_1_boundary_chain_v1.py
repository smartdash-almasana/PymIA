from __future__ import annotations

from typing import TypedDict

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import FileIntakeResult
from pymia.smartpyme.service_1_fsm_decision_patch_v1 import (
    Service1FSMDecisionPatch,
    derive_fsm_decision_patch_from_taskspec,
)
from pymia.smartpyme.service_1_taskspec_contract_v1 import (
    Service1TaskSpec,
    build_minimal_service_1_taskspec,
)


class Service1BoundaryChainResult(TypedDict):
    service_name: str
    task_spec: Service1TaskSpec
    fsm_decision_patch: Service1FSMDecisionPatch


def derive_service_1_boundary_chain_from_file_intake(
    *,
    task_id: str,
    owner_problem: str,
    file_intake: FileIntakeResult,
) -> Service1BoundaryChainResult:
    taskspec_patch = derive_taskspec_patch_from_file_intake(file_intake)
    task_spec = build_minimal_service_1_taskspec(
        task_id=task_id,
        owner_problem=owner_problem,
        source_channel=file_intake["source_channel"],
        blocking_state=taskspec_patch["blocking_state"],
        next_allowed_action=taskspec_patch["next_allowed_action"],
    )
    task_spec["input_assets"] = taskspec_patch["input_assets"]
    task_spec["evidence_received"] = taskspec_patch["evidence_received"]
    task_spec["missing_evidence"] = taskspec_patch["missing_evidence"]
    task_spec["column_confirmation_required"] = taskspec_patch["column_confirmation_required"]
    task_spec["column_confirmation_fields"] = taskspec_patch["column_confirmation_fields"]
    task_spec["runtime_authorized"] = False
    task_spec["notes"] = taskspec_patch["notes"]

    return {
        "service_name": "SERVICE_1",
        "task_spec": task_spec,
        "fsm_decision_patch": derive_fsm_decision_patch_from_taskspec(task_spec),
    }
