from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_synthetic_controlled_case_candidate_chain_composition_v1 import (
    build_service_1_synthetic_controlled_case_candidate_chain_composition_v1,
)
from pymia.smartpyme.service_1_synthetic_controlled_case_candidate_model_v1 import (
    build_service_1_synthetic_controlled_case_candidate_model_v1,
)


CASE_REF = "S1_SYNTHETIC_CONTROLLED_CASE_001"
OPERATOR_REF = "synthetic_operator_ref_001"

DANGEROUS_FLAGS = (
    "business_files_used",
    "cli_executed",
    "execution_executed",
    "runtime_executed",
    "runtime_authorized",
    "data_processed",
    "artifacts_generated",
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "notification_sent",
    "owner_delivery_executed",
    "rollback_executed",
    "service_2_opened",
    "phase_j_opened",
)


def _safe_flags() -> dict[str, bool]:
    return {
        "business_files_used": False,
        "cli_executed": False,
        "execution_executed": False,
        "runtime_executed": False,
        "runtime_authorized": False,
        "data_processed": False,
        "artifacts_generated": False,
        "delivery_executed": False,
        "publish_executed": False,
        "notification_executed": False,
        "notification_sent": False,
        "owner_delivery_executed": False,
        "rollback_executed": False,
        "handoff_executed": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "service_2_opened": False,
        "phase_j_opened": False,
    }


def _synthetic_case_instance() -> dict[str, object]:
    return {
        "case_ref": CASE_REF,
        "case_name": "PyME Mayorista Alfa — Excel readiness and margin first-aid triage",
        "case_type": "SYNTHETIC_CONTROLLED_CASE",
        "operator_ref": OPERATOR_REF,
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
        ],
        "expected_columns": {
            "sales": ["sale_date", "sku", "quantity", "unit_price"],
            "costs": ["sku", "supplier_ref", "unit_cost"],
            "inventory": ["sku", "stock_units", "warehouse_ref"],
        },
        "known_gaps": [
            "product names are not normalized across spreadsheets",
            "discount policy is not fully declared",
        ],
        **_safe_flags(),
    }


def _pre_run_gate_closeout() -> dict[str, object]:
    return {
        "pre_run_gate_closed": True,
        "run_request_model_ready": True,
        "negative_variants_blocked": True,
        "execution_candidate_alignment": True,
        "full_chain_dry_binding": True,
        **_safe_flags(),
    }


def _synthetic_candidate_model_result() -> dict[str, object]:
    return build_service_1_synthetic_controlled_case_candidate_model_v1(
        synthetic_case_instance=_synthetic_case_instance(),
        pre_run_gate_closeout=_pre_run_gate_closeout(),
        operator_ref=OPERATOR_REF,
    )


def _execution_result() -> dict[str, object]:
    inner = {
        "candidate_kind": "CONTROLLED_EXECUTION_CANDIDATE",
        "status": "CONTROLLED_EXECUTION_CANDIDATE_READY",
        "ready": True,
        "execution_authorized": True,
        "operator_ref": OPERATOR_REF,
        "case_ref": CASE_REF,
        **_safe_flags(),
    }
    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE",
        "status": "CONTROLLED_EXECUTION_CANDIDATE_READY",
        "ready": True,
        "controlled_execution_candidate": inner,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _run_result() -> dict[str, object]:
    inner = {
        "candidate_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY",
        "ready": True,
        "run_recorded": True,
        "operator_ref": OPERATOR_REF,
        "case_ref": CASE_REF,
        **_safe_flags(),
    }
    return {
        "contract_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY",
        "ready": True,
        "supervised_cli_run_result_candidate": inner,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _abort_result() -> dict[str, object]:
    inner = {
        "candidate_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": "ABORT_ROLLBACK_RESULT_CANDIDATE_READY",
        "ready": True,
        "rollback_recorded": True,
        "operator_ref": OPERATOR_REF,
        "case_ref": CASE_REF,
        **_safe_flags(),
    }
    return {
        "contract_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": "ABORT_ROLLBACK_RESULT_CANDIDATE_READY",
        "ready": True,
        "abort_rollback_result_candidate": inner,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _delivery_result() -> dict[str, object]:
    inner = {
        "candidate_kind": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE",
        "status": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY",
        "ready": True,
        "delivery_review_recorded": True,
        "operator_ref": OPERATOR_REF,
        "case_ref": CASE_REF,
        **_safe_flags(),
    }
    return {
        "contract_kind": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE",
        "status": "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY",
        "ready": True,
        "controlled_delivery_review_candidate": inner,
        "blocked_reasons": [],
        **_safe_flags(),
    }


def _build(
    *,
    synthetic_candidate_model_result: dict[str, object] | None = None,
    controlled_execution_candidate_result: dict[str, object] | None = None,
    supervised_run_result_candidate_result: dict[str, object] | None = None,
    abort_rollback_result_candidate_result: dict[str, object] | None = None,
    controlled_delivery_review_candidate_result: dict[str, object] | None = None,
    operator_ref: str = OPERATOR_REF,
) -> dict[str, object]:
    return build_service_1_synthetic_controlled_case_candidate_chain_composition_v1(
        synthetic_candidate_model_result=synthetic_candidate_model_result or _synthetic_candidate_model_result(),
        controlled_execution_candidate_result=controlled_execution_candidate_result or _execution_result(),
        supervised_run_result_candidate_result=supervised_run_result_candidate_result or _run_result(),
        abort_rollback_result_candidate_result=abort_rollback_result_candidate_result or _abort_result(),
        controlled_delivery_review_candidate_result=controlled_delivery_review_candidate_result or _delivery_result(),
        operator_ref=operator_ref,
    )


def test_ready_path_composes_synthetic_case_with_phase_i_chain() -> None:
    result = _build()

    assert result["contract_kind"] == "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION"
    assert result["status"] == "SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION_READY"
    assert result["ready"] is True
    assert result["blocked_reasons"] == []

    composition = result["synthetic_controlled_case_candidate_chain_composition"]
    assert composition is not None
    assert composition["candidate_kind"] == "SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION"
    assert composition["case_ref"] == CASE_REF
    assert composition["operator_ref"] == OPERATOR_REF
    assert composition["full_chain_bound"] is True
    assert composition["run_result_binding"] == "CANDIDATE_READY_NOT_CLI_EXECUTED"
    assert composition["abort_rollback_binding"] == "CANDIDATE_READY_NOT_ROLLBACK_EXECUTED"
    assert composition["delivery_review_binding"] == "CANDIDATE_READY_NOT_DELIVERED"


def test_ready_path_forces_all_dangerous_flags_false() -> None:
    result = _build()
    composition = result["synthetic_controlled_case_candidate_chain_composition"]
    assert composition is not None

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False
        assert composition[flag] is False


def test_non_mapping_input_blocks() -> None:
    result = build_service_1_synthetic_controlled_case_candidate_chain_composition_v1(
        synthetic_candidate_model_result=None,
        controlled_execution_candidate_result=_execution_result(),
        supervised_run_result_candidate_result=_run_result(),
        abort_rollback_result_candidate_result=_abort_result(),
        controlled_delivery_review_candidate_result=_delivery_result(),
        operator_ref=OPERATOR_REF,
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False


def test_invalid_synthetic_model_blocks() -> None:
    synthetic = _synthetic_candidate_model_result()
    synthetic["status"] = "BLOCKED"
    synthetic["ready"] = False

    result = _build(synthetic_candidate_model_result=synthetic)

    assert result["status"] == "BLOCKED_INVALID_SYNTHETIC_MODEL"
    assert result["ready"] is False


def test_synthetic_model_not_service_1_blocks() -> None:
    synthetic = _synthetic_candidate_model_result()
    model = synthetic["synthetic_controlled_case_candidate_model"]
    assert isinstance(model, dict)
    model["service_family"] = "SERVICE_2"

    result = _build(synthetic_candidate_model_result=synthetic)

    assert result["status"] == "BLOCKED_INVALID_SYNTHETIC_MODEL"
    assert result["ready"] is False


def test_invalid_execution_candidate_blocks() -> None:
    execution = _execution_result()
    execution["status"] = "BLOCKED"

    result = _build(controlled_execution_candidate_result=execution)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_invalid_run_result_candidate_blocks() -> None:
    run = _run_result()
    run["ready"] = False

    result = _build(supervised_run_result_candidate_result=run)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_invalid_abort_candidate_blocks() -> None:
    abort = _abort_result()
    abort["abort_rollback_result_candidate"] = None

    result = _build(abort_rollback_result_candidate_result=abort)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_invalid_delivery_candidate_blocks() -> None:
    delivery = _delivery_result()
    delivery["contract_kind"] = "OTHER"

    result = _build(controlled_delivery_review_candidate_result=delivery)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_case_mismatch_blocks() -> None:
    run = _run_result()
    inner = run["supervised_cli_run_result_candidate"]
    assert isinstance(inner, dict)
    inner["case_ref"] = "other-case"

    result = _build(supervised_run_result_candidate_result=run)

    assert result["status"] == "BLOCKED_CASE_MISMATCH"
    assert result["ready"] is False


def test_operator_mismatch_blocks() -> None:
    delivery = _delivery_result()
    inner = delivery["controlled_delivery_review_candidate"]
    assert isinstance(inner, dict)
    inner["operator_ref"] = "other-operator"

    result = _build(controlled_delivery_review_candidate_result=delivery)

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_explicit_operator_mismatch_blocks() -> None:
    result = _build(operator_ref="other-operator")

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_unsafe_top_level_flag_blocks() -> None:
    execution = _execution_result()
    execution["runtime_authorized"] = True

    result = _build(controlled_execution_candidate_result=execution)

    assert result["status"] == "BLOCKED_UNSAFE_EXECUTION_FLAGS"
    assert result["ready"] is False
    assert any("runtime_authorized" in reason for reason in result["blocked_reasons"])


def test_unsafe_nested_flag_blocks() -> None:
    delivery = _delivery_result()
    inner = delivery["controlled_delivery_review_candidate"]
    assert isinstance(inner, dict)
    inner["delivery_executed"] = True

    result = _build(controlled_delivery_review_candidate_result=delivery)

    assert result["status"] == "BLOCKED_UNSAFE_EXECUTION_FLAGS"
    assert result["ready"] is False
    assert any("delivery_executed" in reason for reason in result["blocked_reasons"])


def test_execution_candidate_must_authorize_only_as_candidate_data() -> None:
    execution = _execution_result()
    inner = execution["controlled_execution_candidate"]
    assert isinstance(inner, dict)
    inner["execution_authorized"] = False

    result = _build(controlled_execution_candidate_result=execution)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_run_result_must_be_recorded_as_candidate_data() -> None:
    run = _run_result()
    inner = run["supervised_cli_run_result_candidate"]
    assert isinstance(inner, dict)
    inner["run_recorded"] = False

    result = _build(supervised_run_result_candidate_result=run)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_abort_candidate_must_be_recorded_as_candidate_data() -> None:
    abort = _abort_result()
    inner = abort["abort_rollback_result_candidate"]
    assert isinstance(inner, dict)
    inner["rollback_recorded"] = False

    result = _build(abort_rollback_result_candidate_result=abort)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_delivery_review_must_be_recorded_as_candidate_data() -> None:
    delivery = _delivery_result()
    inner = delivery["controlled_delivery_review_candidate"]
    assert isinstance(inner, dict)
    inner["delivery_review_recorded"] = False

    result = _build(controlled_delivery_review_candidate_result=delivery)

    assert result["status"] == "BLOCKED_INVALID_PHASE_I_CHAIN"
    assert result["ready"] is False


def test_inputs_are_not_mutated() -> None:
    synthetic = _synthetic_candidate_model_result()
    execution = _execution_result()
    run = _run_result()
    abort = _abort_result()
    delivery = _delivery_result()
    before = deepcopy((synthetic, execution, run, abort, delivery))

    _build(
        synthetic_candidate_model_result=synthetic,
        controlled_execution_candidate_result=execution,
        supervised_run_result_candidate_result=run,
        abort_rollback_result_candidate_result=abort,
        controlled_delivery_review_candidate_result=delivery,
    )

    assert (synthetic, execution, run, abort, delivery) == before


def test_same_inputs_are_deterministic() -> None:
    synthetic = _synthetic_candidate_model_result()
    execution = _execution_result()
    run = _run_result()
    abort = _abort_result()
    delivery = _delivery_result()

    first = _build(
        synthetic_candidate_model_result=synthetic,
        controlled_execution_candidate_result=execution,
        supervised_run_result_candidate_result=run,
        abort_rollback_result_candidate_result=abort,
        controlled_delivery_review_candidate_result=delivery,
    )
    second = _build(
        synthetic_candidate_model_result=synthetic,
        controlled_execution_candidate_result=execution,
        supervised_run_result_candidate_result=run,
        abort_rollback_result_candidate_result=abort,
        controlled_delivery_review_candidate_result=delivery,
    )

    assert first == second
