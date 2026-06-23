from __future__ import annotations

from pymia.smartpyme.service_1_microservice_activation_contract_v1 import (
    build_service_1_microservice_activation_contract_v1,
)
from pymia.smartpyme.service_1_microservice_registry_contract_v1 import (
    build_service_1_microservice_registry_contract_v1,
)
from pymia.smartpyme.service_1_operator_harness_v2_contract import (
    build_service_1_operator_harness_v2_contract,
)


def _activation_input(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "microservice_id": "xlsx_delivery",
        "requested_capability": "operational_xlsx_draft",
        "runtime_requested": False,
        "human_review_present": True,
    }
    data.update(overrides)
    return data


def _harness_input(operator_requested_action: str = "deliver_operational_draft") -> dict[str, object]:
    return {
        "case_folder_manifest_status": "READY_FOR_QA",
        "delivery_manifest_audit_status": "PASS_READY_FOR_DELIVERY",
        "operator_requested_action": operator_requested_action,
        "human_reviewer_present": True,
        "human_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_allowed_by_audit": True,
    }


def test_chain_allows_safe_xlsx_delivery_activation_then_harness_delivery() -> None:
    registry = build_service_1_microservice_registry_contract_v1({"microservice_id": "xlsx_delivery"})
    activation = build_service_1_microservice_activation_contract_v1(_activation_input())
    harness = build_service_1_operator_harness_v2_contract(_harness_input())

    assert registry["status"] == "VALID"
    assert activation["status"] == "ACTIVATION_ALLOWED"
    assert activation["activation_allowed"] is True
    assert harness["status"] == "READY_FOR_OPERATIONAL_DRAFT_DELIVERY"
    assert harness["delivery_allowed"] is True


def test_chain_safe_human_review_action_stops_before_delivery() -> None:
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(microservice_id="accounting_contracts", requested_capability="contract_review_report")
    )
    harness = build_service_1_operator_harness_v2_contract(_harness_input("send_to_human_review"))

    assert activation["status"] == "ACTIVATION_ALLOWED"
    assert activation["human_review_required"] is True
    assert harness["status"] == "READY_FOR_HUMAN_REVIEW"
    assert harness["delivery_allowed"] is False
    assert harness["blocked_operator_actions"] == ["deliver_operational_draft"]


def test_chain_blocks_chatbot_before_harness() -> None:
    registry = build_service_1_microservice_registry_contract_v1({"microservice_id": "chatbot"})
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(microservice_id="chatbot", requested_capability="free_chat")
    )

    assert registry["status"] == "BLOCKED_MICROSERVICE"
    assert activation["status"] == "BLOCKED_BY_REGISTRY"
    assert activation["activation_allowed"] is False


def test_chain_blocks_runtime_request_before_harness() -> None:
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(runtime_requested=True)
    )

    assert activation["status"] == "BLOCKED_BY_RUNTIME_REQUEST"
    assert activation["activation_allowed"] is False
    assert activation["runtime_authorized"] is False


def test_chain_blocks_final_reconciliation_before_harness() -> None:
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="bank_reconciliation_basic",
            requested_capability="conciliacion_bancaria_cerrada",
            human_review_present=True,
        )
    )

    assert activation["status"] == "BLOCKED_BY_FORBIDDEN_CAPABILITY"
    assert activation["activation_allowed"] is False
    assert activation["activated_microservice"] is None


def test_chain_blocks_missing_dependencies_before_harness() -> None:
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="mercado_pago_reconciliation_basic",
            requested_capability="collection_scope_summary",
            human_review_present=True,
            available_microservices=["file_intake"],
        )
    )

    assert activation["status"] == "BLOCKED_BY_DEPENDENCIES"
    assert activation["activation_allowed"] is False
    assert "accounting_contracts" in activation["blocked_reason"]
    assert "xlsx_delivery" in activation["blocked_reason"]


def test_chain_blocks_missing_human_review_before_harness() -> None:
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(human_review_present=False)
    )

    assert activation["status"] == "BLOCKED_BY_MISSING_HUMAN_REVIEW"
    assert activation["activation_allowed"] is False
    assert activation["required_human_actions"] == ["assign_human_review"]


def test_chain_blocks_service_2_before_harness() -> None:
    registry = build_service_1_microservice_registry_contract_v1({"microservice_id": "servicio_2_diagnostic"})
    activation = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="servicio_2_diagnostic",
            requested_capability="diagnostico_integral_pyme",
            human_review_present=True,
        )
    )

    assert registry["status"] == "BLOCKED_MICROSERVICE"
    assert activation["status"] == "BLOCKED_BY_REGISTRY"
    assert activation["activation_allowed"] is False


def test_chain_harness_still_blocks_forbidden_operator_action_after_allowed_activation() -> None:
    activation = build_service_1_microservice_activation_contract_v1(_activation_input())
    harness = build_service_1_operator_harness_v2_contract(_harness_input("run_autonomous_chatbot"))

    assert activation["status"] == "ACTIVATION_ALLOWED"
    assert harness["status"] == "BLOCKED_BY_FORBIDDEN_ACTION"
    assert harness["delivery_allowed"] is False


def test_chain_harness_still_blocks_late_stop_condition_after_allowed_activation() -> None:
    activation = build_service_1_microservice_activation_contract_v1(_activation_input())
    harness_input = _harness_input()
    harness_input["stop_conditions"] = "FINAL_RECONCILIATION_REQUESTED"
    harness = build_service_1_operator_harness_v2_contract(harness_input)

    assert activation["status"] == "ACTIVATION_ALLOWED"
    assert harness["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert harness["delivery_allowed"] is False
