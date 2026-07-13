from __future__ import annotations

from pymia.smartpyme.service_1_taskspec_contract_v1 import build_minimal_service_1_taskspec
from pymia.smartpyme.service_1_taskspec_vocabulary_v1 import (
    SERVICE_1_TASKSPEC_ALLOWED_BLOCKING_STATES,
    SERVICE_1_TASKSPEC_ALLOWED_NEXT_ACTIONS,
)


def test_build_minimal_service_1_taskspec_defaults_to_service_1_contract() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_001",
        owner_problem="Necesito revisar un archivo operativo.",
    )

    assert task_spec["task_id"] == "task_001"
    assert task_spec["schema_version"] == "1.0"
    assert task_spec["service_name"] == "SERVICE_1"
    assert task_spec["service_depth"] == "UNKNOWN"
    assert task_spec["task_type"] == "UNKNOWN"
    assert task_spec["owner_problem"] == "Necesito revisar un archivo operativo."
    assert task_spec["source_channel"] == "unknown"
    assert task_spec["runtime_authorized"] is False


def test_build_minimal_service_1_taskspec_uses_canonical_vocabulary() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_002",
        owner_problem="Subí una planilla.",
        blocking_state="BLOCKED_COLUMN_CONFIRMATION",
        next_allowed_action="ask_owner_to_confirm_columns_after_curation",
    )

    assert task_spec["blocking_state"] in SERVICE_1_TASKSPEC_ALLOWED_BLOCKING_STATES
    assert task_spec["next_allowed_action"] in SERVICE_1_TASKSPEC_ALLOWED_NEXT_ACTIONS


def test_build_minimal_service_1_taskspec_starts_without_assets_or_runtime_outputs() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_003",
        owner_problem="No me cierra la caja.",
        service_depth="FIRST_AID",
        task_type="FIRST_AID_DAILY_CASH",
        source_channel="chat",
    )

    assert task_spec["input_assets"] == []
    assert task_spec["evidence_required"] == []
    assert task_spec["evidence_received"] == []
    assert task_spec["missing_evidence"] == []
    assert task_spec["column_confirmation_required"] is False
    assert task_spec["column_confirmation_fields"] == []
    assert task_spec["requested_formula_refs"] == []
    assert task_spec["requested_claims"] == []
    assert task_spec["forbidden_claims"] == []
    assert task_spec["expected_output"]["downloadable_file_expected"] is False
    assert task_spec["expected_output"]["limitations_required"] is True
    assert task_spec["runtime_authorized"] is False
