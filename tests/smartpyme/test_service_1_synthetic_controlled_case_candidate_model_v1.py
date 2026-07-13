from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_synthetic_controlled_case_candidate_model_v1 import (
    build_service_1_synthetic_controlled_case_candidate_model_v1,
)


DANGEROUS_FLAGS = (
    "business_files_used",
    "cli_executed",
    "runtime_executed",
    "data_processed",
    "artifacts_generated",
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "owner_delivery_executed",
    "service_2_opened",
    "phase_j_opened",
)


def _valid_synthetic_case_instance() -> dict[str, object]:
    return {
        "case_ref": "S1_SYNTHETIC_CONTROLLED_CASE_001",
        "case_name": "PyME Mayorista Alfa — Excel readiness and margin first-aid triage",
        "case_type": "SYNTHETIC_CONTROLLED_CASE",
        "operator_ref": "synthetic_operator_ref_001",
        "tenant_ref": "synthetic_tenant_wholesale_alfa",
        "owner_ref": "synthetic_owner_wholesale_alfa",
        "packet_ref": "synthetic_packet_wholesale_alfa_001",
        "input_set_ref": "synthetic_run_input_set_wholesale_alfa_001",
        "service_family": "SERVICE_1",
        "synthetic_only": True,
        "scope_service_1_only": True,
        "evidence_categories": [
            "sales spreadsheet description",
            "product cost spreadsheet description",
            "inventory spreadsheet description",
            "owner business question",
        ],
        "expected_columns": {
            "sales": ["sale_date", "sku", "quantity", "unit_price", "discount"],
            "costs": ["sku", "supplier_ref", "unit_cost", "last_cost_update"],
            "inventory": ["sku", "stock_units", "warehouse_ref", "last_movement_date"],
        },
        "known_gaps": [
            "product names are not normalized across spreadsheets",
            "discount policy is not fully declared",
            "some cost updates may be stale",
        ],
        "business_files_used": False,
        "cli_executed": False,
        "runtime_executed": False,
        "data_processed": False,
        "artifacts_generated": False,
        "delivery_executed": False,
        "publish_executed": False,
        "notification_executed": False,
        "owner_delivery_executed": False,
        "service_2_opened": False,
        "phase_j_opened": False,
    }


def _valid_pre_run_gate_closeout() -> dict[str, object]:
    return {
        "pre_run_gate_closed": True,
        "run_request_model_ready": True,
        "negative_variants_blocked": True,
        "execution_candidate_alignment": True,
        "full_chain_dry_binding": True,
        "business_files_used": False,
        "cli_executed": False,
        "runtime_executed": False,
        "data_processed": False,
        "artifacts_generated": False,
        "delivery_executed": False,
        "publish_executed": False,
        "notification_executed": False,
        "owner_delivery_executed": False,
        "service_2_opened": False,
        "phase_j_opened": False,
    }


def _build(
    *,
    synthetic_case_instance: dict[str, object] | None = None,
    pre_run_gate_closeout: dict[str, object] | None = None,
    operator_ref: str = "synthetic_operator_ref_001",
) -> dict[str, object]:
    return build_service_1_synthetic_controlled_case_candidate_model_v1(
        synthetic_case_instance=synthetic_case_instance or _valid_synthetic_case_instance(),
        pre_run_gate_closeout=pre_run_gate_closeout or _valid_pre_run_gate_closeout(),
        operator_ref=operator_ref,
    )


def test_ready_path_builds_synthetic_controlled_case_candidate_model() -> None:
    result = _build()

    assert result["contract_kind"] == "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL"
    assert result["status"] == "SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL_READY"
    assert result["ready"] is True
    assert result["blocked_reasons"] == []

    candidate = result["synthetic_controlled_case_candidate_model"]
    assert candidate is not None
    assert candidate["candidate_kind"] == "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL"
    assert candidate["case_ref"] == "S1_SYNTHETIC_CONTROLLED_CASE_001"
    assert candidate["case_type"] == "SYNTHETIC_CONTROLLED_CASE"
    assert candidate["service_family"] == "SERVICE_1"
    assert candidate["synthetic_only"] is True
    assert candidate["scope_service_1_only"] is True
    assert candidate["pre_run_gate_closed"] is True
    assert candidate["run_request_model_ready"] is True
    assert candidate["negative_variants_blocked"] is True
    assert candidate["execution_candidate_alignment"] is True
    assert candidate["full_chain_dry_binding"]["run_result_bound"] == "DRY_PLACEHOLDER_ONLY"
    assert candidate["full_chain_dry_binding"]["delivery_review_bound"] == "DRY_BOUNDARY_ONLY"


def test_ready_path_forces_all_execution_and_runtime_flags_false() -> None:
    result = _build()
    candidate = result["synthetic_controlled_case_candidate_model"]
    assert candidate is not None

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False
        assert candidate[flag] is False


def test_non_mapping_synthetic_case_blocks() -> None:
    result = build_service_1_synthetic_controlled_case_candidate_model_v1(
        synthetic_case_instance=None,
        pre_run_gate_closeout=_valid_pre_run_gate_closeout(),
        operator_ref="synthetic_operator_ref_001",
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False
    assert result["synthetic_controlled_case_candidate_model"] is None


def test_non_mapping_pre_run_gate_blocks() -> None:
    result = build_service_1_synthetic_controlled_case_candidate_model_v1(
        synthetic_case_instance=_valid_synthetic_case_instance(),
        pre_run_gate_closeout=None,
        operator_ref="synthetic_operator_ref_001",
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False


def test_missing_required_case_ref_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["packet_ref"] = ""

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_MISSING_REQUIRED_REF"
    assert result["ready"] is False


def test_operator_mismatch_blocks() -> None:
    result = _build(operator_ref="other_operator")

    assert result["status"] == "BLOCKED_MISSING_REQUIRED_REF"
    assert result["ready"] is False


def test_not_synthetic_case_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["case_type"] = "REAL_CLIENT_CASE"

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_NOT_SYNTHETIC"
    assert result["ready"] is False


def test_synthetic_only_false_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["synthetic_only"] = False

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_NOT_SYNTHETIC"
    assert result["ready"] is False


def test_non_service_1_family_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["service_family"] = "SERVICE_2"

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_SCOPE_NOT_SERVICE_1"
    assert result["ready"] is False


def test_scope_not_service_1_only_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["scope_service_1_only"] = False

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_SCOPE_NOT_SERVICE_1"
    assert result["ready"] is False


def test_missing_evidence_categories_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["evidence_categories"] = []

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_MISSING_EVIDENCE"
    assert result["ready"] is False


def test_invalid_expected_columns_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["expected_columns"] = {"sales": []}

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_MISSING_EVIDENCE"
    assert result["ready"] is False


def test_missing_known_gaps_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["known_gaps"] = []

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_MISSING_KNOWN_GAPS"
    assert result["ready"] is False


def test_pre_run_gate_not_closed_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["pre_run_gate_closed"] = False

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_PRE_RUN_NOT_READY"
    assert result["ready"] is False


def test_run_request_model_not_ready_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["run_request_model_ready"] = False

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_PRE_RUN_NOT_READY"
    assert result["ready"] is False


def test_negative_variants_not_blocked_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["negative_variants_blocked"] = False

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_NEGATIVE_VARIANTS_NOT_BLOCKED"
    assert result["ready"] is False


def test_execution_candidate_alignment_missing_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["execution_candidate_alignment"] = False

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_PRE_RUN_NOT_READY"
    assert result["ready"] is False


def test_full_chain_dry_binding_missing_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["full_chain_dry_binding"] = False

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_PRE_RUN_NOT_READY"
    assert result["ready"] is False


def test_unsafe_flag_in_case_blocks() -> None:
    case = _valid_synthetic_case_instance()
    case["cli_executed"] = True

    result = _build(synthetic_case_instance=case)

    assert result["status"] == "BLOCKED_UNSAFE_EXECUTION_FLAGS"
    assert result["ready"] is False
    assert any("cli_executed" in reason for reason in result["blocked_reasons"])


def test_unsafe_flag_in_gate_blocks() -> None:
    gate = _valid_pre_run_gate_closeout()
    gate["runtime_executed"] = True

    result = _build(pre_run_gate_closeout=gate)

    assert result["status"] == "BLOCKED_UNSAFE_EXECUTION_FLAGS"
    assert result["ready"] is False
    assert any("runtime_executed" in reason for reason in result["blocked_reasons"])


def test_inputs_are_not_mutated() -> None:
    case = _valid_synthetic_case_instance()
    gate = _valid_pre_run_gate_closeout()
    case_before = deepcopy(case)
    gate_before = deepcopy(gate)

    _build(synthetic_case_instance=case, pre_run_gate_closeout=gate)

    assert case == case_before
    assert gate == gate_before


def test_same_inputs_are_deterministic() -> None:
    case = _valid_synthetic_case_instance()
    gate = _valid_pre_run_gate_closeout()

    first = _build(synthetic_case_instance=case, pre_run_gate_closeout=gate)
    second = _build(synthetic_case_instance=case, pre_run_gate_closeout=gate)

    assert first == second
