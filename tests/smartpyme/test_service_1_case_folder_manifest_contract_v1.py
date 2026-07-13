from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_case_folder_manifest_contract_v1 import (
    REQUIRED_SERVICE_1_CASE_FOLDER_MANIFEST_FIELDS,
    build_service_1_case_folder_manifest_contract_v1,
)


def _valid_manifest() -> dict[str, object]:
    return {
        "case_id": "S1-CASE-001",
        "client_alias": "cliente_demo",
        "case_family": "ACCOUNTING_XLSX_WORKPAPER",
        "period": "2026-04",
        "operator": "operator_001",
        "human_reviewer": "reviewer_001",
        "intake_status": "ACCEPTED",
        "accepted_scope": "Servicio 1: microservicio asistido bajo revision humana",
        "input_files": ["ventas_abril.xlsx"],
        "human_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_status": "PENDING_QA",
        "next_safe_action": "SEND_TO_QA",
    }


def test_valid_manifest_returns_ready_for_qa_and_allows_delivery() -> None:
    result = build_service_1_case_folder_manifest_contract_v1(_valid_manifest())

    assert result == {
        "status": "READY_FOR_QA",
        "missing_fields": [],
        "active_stop_conditions": [],
        "human_review_required": False,
        "forbidden_claims_check_status": "PASSED",
        "delivery_allowed": True,
        "next_allowed_action": "send_to_qa",
    }


def test_non_dict_input_returns_invalid_input() -> None:
    result = build_service_1_case_folder_manifest_contract_v1("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["missing_fields"] == list(REQUIRED_SERVICE_1_CASE_FOLDER_MANIFEST_FIELDS)
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "fix_manifest_input"


def test_missing_required_fields_blocks_delivery() -> None:
    manifest = _valid_manifest()
    del manifest["case_id"]
    del manifest["period"]

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["missing_fields"] == ["case_id", "period"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "complete_required_fields"


def test_blank_human_reviewer_blocks_delivery() -> None:
    manifest = _valid_manifest()
    manifest["human_reviewer"] = ""

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["missing_fields"] == ["human_reviewer"]
    assert result["human_review_required"] is True
    assert result["delivery_allowed"] is False


def test_invalid_human_review_status_blocks_delivery() -> None:
    manifest = _valid_manifest()
    manifest["human_review_status"] = "NOT_REQUIRED"

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "BLOCKED_BY_MISSING_HUMAN_REVIEWER"
    assert result["missing_fields"] == []
    assert result["human_review_required"] is True
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "assign_human_reviewer"


def test_active_stop_condition_blocks_delivery() -> None:
    manifest = _valid_manifest()
    manifest["stop_conditions"] = "CLIENT_REQUESTS_TAX_VALIDATION"

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert result["active_stop_conditions"] == ["CLIENT_REQUESTS_TAX_VALIDATION"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "resolve_stop_conditions"


def test_forbidden_claims_check_not_passed_blocks_delivery() -> None:
    manifest = _valid_manifest()
    manifest["forbidden_claims_check"] = "FAILED"

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK"
    assert result["forbidden_claims_check_status"] == "FAILED"
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "run_forbidden_claims_check"


def test_empty_input_files_counts_as_missing_required_field() -> None:
    manifest = _valid_manifest()
    manifest["input_files"] = []

    result = build_service_1_case_folder_manifest_contract_v1(manifest)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["missing_fields"] == ["input_files"]
    assert result["delivery_allowed"] is False


def test_contract_module_does_not_import_openpyxl_or_perform_file_io() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_case_folder_manifest_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    forbidden_fragments = (
        "openpyxl",
        "pandas",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "from pathlib",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_vertical_slice_was_not_imported_or_referenced() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_case_folder_manifest_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
