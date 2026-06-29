from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pymia.smartpyme.service_1_case_truth_integration_model_v1 import (
    STATUS_BLOCKED_BY_PYMIA_GATE,
    STATUS_CONFLICT_OWNER_DATA,
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY_FOR_TOOL_PLANNING,
    STATUS_UNKNOWN,
    Service1CaseTruthIntegrationInputV1,
    build_service_1_case_truth_integration_model_v1,
)


def _ready_input() -> Service1CaseTruthIntegrationInputV1:
    return Service1CaseTruthIntegrationInputV1(
        owner_intent_present=True,
        owner_axis_confirmed=True,
        owner_axis="precio_margen",
        data_available=True,
        normalized_data_status="OK",
        column_confirmation_status="CONFIRMED",
        evidence_sufficiency_status="SUFFICIENT",
        supported_family="precio_margen_basico",
        pymia_gate_status="PASS",
        detected_data_axis="precio_margen",
        missing_evidence_refs=[],
        blockers=[],
    )


def test_blocker_produces_blocked_by_pymia_gate() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), blockers=["unsupported_family"])
    )

    assert result.status == STATUS_BLOCKED_BY_PYMIA_GATE
    assert result.ready_for_tool_planning is False
    assert result.safe_next_action == "stop_and_resolve_pymia_gate"
    assert result.blocked_reason == "unsupported_family"


def test_pymia_gate_block_status_produces_blocked_by_pymia_gate() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), pymia_gate_status="BLOCKED")
    )

    assert result.status == STATUS_BLOCKED_BY_PYMIA_GATE
    assert result.blocked_reason == "PymIA gate status blocks planning: BLOCKED"


def test_owner_axis_not_confirmed_produces_needs_owner_confirmation() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), owner_axis_confirmed=False)
    )

    assert result.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert result.ready_for_tool_planning is False
    assert result.owner_question_if_needed is not None


def test_missing_owner_intent_produces_needs_owner_confirmation() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), owner_intent_present=False)
    )

    assert result.status == STATUS_NEEDS_OWNER_CONFIRMATION


def test_pending_column_confirmation_produces_needs_owner_confirmation() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), column_confirmation_status="NEEDS_OWNER_CONFIRMATION")
    )

    assert result.status == STATUS_NEEDS_OWNER_CONFIRMATION


def test_missing_evidence_produces_needs_evidence() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), missing_evidence_refs=["column:costo_unitario"])
    )

    assert result.status == STATUS_NEEDS_EVIDENCE
    assert result.ready_for_tool_planning is False
    assert result.missing_evidence_refs == ("column:costo_unitario",)
    assert result.safe_next_action == "request_missing_evidence"


def test_unavailable_data_produces_needs_evidence() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), data_available=False)
    )

    assert result.status == STATUS_NEEDS_EVIDENCE


def test_owner_data_axis_conflict_produces_conflict_owner_data() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), detected_data_axis="stock")
    )

    assert result.status == STATUS_CONFLICT_OWNER_DATA
    assert result.ready_for_tool_planning is False
    assert result.conflict_reason == "owner_axis='precio_margen' conflicts with detected_data_axis='stock'"
    assert result.owner_question_if_needed is not None


def test_all_sufficient_produces_ready_for_tool_planning() -> None:
    result = build_service_1_case_truth_integration_model_v1(_ready_input())

    assert result.status == STATUS_READY_FOR_TOOL_PLANNING
    assert result.ready_for_tool_planning is True
    assert result.safe_next_action == "continue_to_auto_tool_selection_and_mapping"
    assert result.owner_question_if_needed is None
    assert result.blocked_reason is None
    assert result.conflict_reason is None


def test_ambiguous_input_produces_unknown() -> None:
    result = build_service_1_case_truth_integration_model_v1(
        replace(_ready_input(), column_confirmation_status="UNCLASSIFIED")
    )

    assert result.status == STATUS_UNKNOWN
    assert result.ready_for_tool_planning is False
    assert result.safe_next_action == "manual_review_required"


def test_runtime_and_autonomous_delivery_are_never_authorized() -> None:
    cases = [
        replace(_ready_input(), blockers=["gate"]),
        replace(_ready_input(), owner_axis_confirmed=False),
        replace(_ready_input(), missing_evidence_refs=["x"]),
        replace(_ready_input(), detected_data_axis="stock"),
        _ready_input(),
        replace(_ready_input(), column_confirmation_status="UNCLASSIFIED"),
    ]

    for case in cases:
        result = build_service_1_case_truth_integration_model_v1(case)
        assert result.runtime_authorized is False
        assert result.autonomous_delivery_authorized is False
        assert result.to_dict()["runtime_authorized"] is False
        assert result.to_dict()["autonomous_delivery_authorized"] is False


def test_module_has_no_pipeline_tools_delivery_llm_or_chatbot_dependency() -> None:
    source = Path("pymia/smartpyme/service_1_case_truth_integration_model_v1.py").read_text(
        encoding="utf-8"
    )

    assert "from pymia" not in source
    assert "import pymia" not in source
    assert "service_1_pipeline" not in source
    assert "service_1_case_delivery" not in source
    assert "pymia.cli" not in source
    assert "first_aid" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_function_does_not_mutate_input() -> None:
    missing_evidence_refs = ["column:costo_unitario"]
    blockers = ["gate"]
    integration_input = replace(
        _ready_input(),
        missing_evidence_refs=missing_evidence_refs,
        blockers=blockers,
    )

    before_missing = list(missing_evidence_refs)
    before_blockers = list(blockers)

    build_service_1_case_truth_integration_model_v1(integration_input)

    assert missing_evidence_refs == before_missing
    assert blockers == before_blockers
    assert integration_input.missing_evidence_refs is missing_evidence_refs
    assert integration_input.blockers is blockers
