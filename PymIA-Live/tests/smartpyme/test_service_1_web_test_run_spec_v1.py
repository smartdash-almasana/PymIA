from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_web_test_run_spec_v1 import (
    REQUIRED_WEB_TEST_RUN_SPEC_FIELDS,
    build_service_1_web_test_run_spec_v1,
    close_service_1_web_test_run_spec_v1,
)


def test_builds_ready_run_spec_for_allowed_route() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {
            "run_id": "run_001",
            "route_id": "excel_treatment_lab_sandbox",
            "data_mode": "SYNTHETIC_FIXTURE",
            "operator_label": "operator_a",
            "case_label": "excel_lab_demo",
        }
    )

    assert result["status"] == "READY_FOR_SANDBOX_REHEARSAL"
    assert result["run_id"] == "run_001"
    assert result["route_id"] == "excel_treatment_lab_sandbox"
    assert result["route_label"] == "Excel Treatment Lab Sandbox"
    assert result["state"] == "OPERATOR_REVIEW_REQUIRED"
    assert result["review_decision"] == "PENDING_REVIEW"
    assert result["blocked_reason"] == ""
    assert "excel_treatment_lab_review_packet.xlsx" in result["expected_artifacts"]


def test_run_spec_has_required_fields_in_stable_order() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_002", "route_id": "invoice_collection_matching_sandbox"}
    )

    assert tuple(result.keys()) == REQUIRED_WEB_TEST_RUN_SPEC_FIELDS


def test_defaults_to_synthetic_fixture_internal_operator_and_sandbox_case() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_003", "route_id": "bank_reconciliation_sandbox"}
    )

    assert result["status"] == "READY_FOR_SANDBOX_REHEARSAL"
    assert result["data_mode"] == "SYNTHETIC_FIXTURE"
    assert result["operator_label"] == "internal_operator"
    assert result["case_label"] == "sandbox_rehearsal_case"


def test_every_ready_run_is_safe_by_default() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_004", "route_id": "accounting_workpaper_draft_sandbox"}
    )

    assert result["human_review_required"] is True
    assert result["runtime_authorized"] is False
    assert result["production_allowed"] is False
    assert result["forbidden_claims"]


def test_invalid_input_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["state"] == "BLOCKED"
    assert result["blocked_reason"] == "run_input_must_be_dict"
    assert result["runtime_authorized"] is False
    assert result["production_allowed"] is False


def test_missing_run_id_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1({"route_id": "excel_treatment_lab_sandbox"})

    assert result["status"] == "INVALID_INPUT"
    assert result["blocked_reason"] == "missing_run_id"
    assert result["next_allowed_action"] == "provide_run_id"


def test_missing_route_id_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1({"run_id": "run_005"})

    assert result["status"] == "INVALID_INPUT"
    assert result["run_id"] == "run_005"
    assert result["blocked_reason"] == "missing_route_id"
    assert result["next_allowed_action"] == "select_allowed_route_id"


def test_unknown_route_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_006", "route_id": "unknown_route"}
    )

    assert result["status"] == "BLOCKED_ROUTE"
    assert result["state"] == "BLOCKED"
    assert result["route_id"] == "unknown_route"
    assert result["blocked_reason"] == "blocked_or_unknown_route"


def test_mercado_pago_route_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_007", "route_id": "mercado_pago_reconciliation_sandbox"}
    )

    assert result["status"] == "BLOCKED_ROUTE"
    assert result["blocked_reason"] == "blocked_or_unknown_route"


def test_servicio_2_route_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_008", "route_id": "servicio_2_diagnostic"}
    )

    assert result["status"] == "BLOCKED_ROUTE"
    assert result["blocked_reason"] == "blocked_or_unknown_route"


def test_real_client_data_mode_is_blocked() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {
            "run_id": "run_009",
            "route_id": "excel_treatment_lab_sandbox",
            "data_mode": "REAL_CLIENT_DATA",
        }
    )

    assert result["status"] == "BLOCKED_DATA_MODE"
    assert result["state"] == "BLOCKED"
    assert result["data_mode"] == "REAL_CLIENT_DATA"
    assert result["blocked_reason"] == "data_mode_not_allowed_for_route"
    assert "real_workbook_normalized" in result["forbidden_claims"]


def test_first_aid_blocks_anonymized_rehearsal_candidate_mode() -> None:
    result = build_service_1_web_test_run_spec_v1(
        {
            "run_id": "run_010",
            "route_id": "first_aid_synthetic_delivery_rehearsal",
            "data_mode": "ANONYMIZED_REHEARSAL_CANDIDATE",
        }
    )

    assert result["status"] == "BLOCKED_DATA_MODE"
    assert result["blocked_reason"] == "data_mode_not_allowed_for_route"


def test_closes_ready_run_only_as_sandbox_rehearsal() -> None:
    run_spec = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_011", "route_id": "excel_treatment_lab_sandbox"}
    )

    closed = close_service_1_web_test_run_spec_v1(
        run_spec,
        review_decision="CLOSE_SANDBOX_REHEARSAL",
    )

    assert closed["state"] == "CLOSED_AS_SANDBOX_REHEARSAL"
    assert closed["review_decision"] == "CLOSE_SANDBOX_REHEARSAL"
    assert closed["next_allowed_action"] == "archive_sandbox_rehearsal_evidence"
    assert closed["production_allowed"] is False


def test_operator_can_block_ready_run() -> None:
    run_spec = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_012", "route_id": "bank_reconciliation_sandbox"}
    )

    blocked = close_service_1_web_test_run_spec_v1(run_spec, review_decision="BLOCK_RUN")

    assert blocked["state"] == "BLOCKED"
    assert blocked["review_decision"] == "BLOCK_RUN"
    assert blocked["blocked_reason"] == "operator_blocked_run"
    assert blocked["next_allowed_action"] == "record_block_reason_and_stop"


def test_operator_can_request_more_evidence_without_closing() -> None:
    run_spec = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_013", "route_id": "invoice_collection_matching_sandbox"}
    )

    pending = close_service_1_web_test_run_spec_v1(
        run_spec,
        review_decision="REQUEST_MORE_EVIDENCE",
    )

    assert pending["state"] == "OPERATOR_REVIEW_REQUIRED"
    assert pending["blocked_reason"] == "more_evidence_required"
    assert pending["next_allowed_action"] == "request_more_evidence_before_closing"


def test_blocked_run_cannot_be_closed_as_success() -> None:
    run_spec = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_014", "route_id": "unknown_route"}
    )

    closed = close_service_1_web_test_run_spec_v1(
        run_spec,
        review_decision="CLOSE_SANDBOX_REHEARSAL",
    )

    assert closed["state"] == "BLOCKED"
    assert closed["next_allowed_action"] == "fix_blocked_run_before_review"


def test_unsupported_review_decision_is_rejected() -> None:
    run_spec = build_service_1_web_test_run_spec_v1(
        {"run_id": "run_015", "route_id": "excel_treatment_lab_sandbox"}
    )

    with pytest.raises(ValueError, match="Unsupported review decision"):
        close_service_1_web_test_run_spec_v1(run_spec, review_decision="APPROVE_FINAL_DELIVERY")  # type: ignore[arg-type]


def test_run_spec_module_has_no_io_web_runtime_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_web_test_run_spec_v1.py"
    source = module_path.read_text(encoding="utf-8")

    forbidden_fragments = (
        "openpyxl",
        "pandas",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "from pathlib",
        "requests",
        "httpx",
        "FastAPI",
        "flask",
        "django",
        "streamlit",
        "subprocess",
        "import openai",
        "from openai",
        "import langchain",
        "from langchain",
        "vertical_slice",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
