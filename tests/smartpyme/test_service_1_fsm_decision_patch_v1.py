from __future__ import annotations

from pymia.smartpyme.service_1_fsm_decision_patch_v1 import (
    FREEZE_REASON,
    FREEZE_STATUS,
    derive_fsm_decision_patch_from_taskspec,
)
from pymia.smartpyme.service_1_taskspec_contract_v1 import build_minimal_service_1_taskspec


def test_fsm_decision_patch_module_is_explicitly_frozen() -> None:
    assert FREEZE_STATUS == "EXPERIMENTAL_FROZEN"
    assert "do not expand before Service 1 product boundary" in FREEZE_REASON


def test_missing_evidence_requests_evidence_without_runtime() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_missing",
        owner_problem="Necesito revisar caja.",
        next_allowed_action="ask_owner_for_clearer_file",
        blocking_state="BLOCKED_MISSING_EVIDENCE",
    )
    task_spec["missing_evidence"] = ["xlsx_file"]

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "EVIDENCE_REQUESTED"
    assert decision["decision_reason"] == "MISSING_EVIDENCE"
    assert decision["blocking_state"] == "BLOCKED_MISSING_EVIDENCE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_column_confirmation_required_maps_to_confirmation_required() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_columns",
        owner_problem="Subí un Excel.",
        next_allowed_action="ask_owner_to_confirm_columns_after_curation",
        blocking_state="BLOCKED_COLUMN_CONFIRMATION",
    )
    task_spec["column_confirmation_required"] = True

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "CONFIRMATION_REQUIRED"
    assert decision["decision_reason"] == "COLUMN_CONFIRMATION_REQUIRED"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_unsupported_file_type_maps_to_blocked() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_unsupported",
        owner_problem="Subí un PDF.",
        next_allowed_action="ask_owner_to_upload_xlsx",
        blocking_state="BLOCKED_UNSUPPORTED_FILE_TYPE",
    )

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "BLOCKED"
    assert decision["decision_reason"] == "UNSUPPORTED_FILE_TYPE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_unknown_file_type_maps_to_blocked() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_unknown",
        owner_problem="Subí un archivo desconocido.",
        next_allowed_action="ask_owner_for_clearer_file",
        blocking_state="BLOCKED_UNKNOWN_FILE_TYPE",
    )

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "BLOCKED"
    assert decision["decision_reason"] == "UNKNOWN_FILE_TYPE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_unsafe_file_maps_to_blocked() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_unsafe",
        owner_problem="Subí un archivo inseguro.",
        next_allowed_action="ask_owner_for_clearer_file",
        blocking_state="BLOCKED_UNSAFE_FILE",
    )

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "BLOCKED"
    assert decision["decision_reason"] == "UNSAFE_FILE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_runtime_not_authorized_maps_to_blocked() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_runtime",
        owner_problem="Quiero procesar.",
        next_allowed_action="block_runtime_until_supported",
        blocking_state="BLOCKED_RUNTIME_NOT_AUTHORIZED",
    )

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "BLOCKED"
    assert decision["decision_reason"] == "RUNTIME_NOT_AUTHORIZED"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_ready_without_blocker_is_held_without_runtime() -> None:
    task_spec = build_minimal_service_1_taskspec(
        task_id="task_ready",
        owner_problem="Tengo evidencia inicial.",
        next_allowed_action="block_runtime_until_supported",
        blocking_state=None,
    )

    decision = derive_fsm_decision_patch_from_taskspec(task_spec)

    assert decision["next_state"] == "EVIDENCE_RECEIVED"
    assert decision["decision_reason"] == "READY_BUT_HELD"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False
