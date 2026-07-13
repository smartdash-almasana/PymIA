"""Focal tests for SERVICE_1_RUNTIME_AUTHORIZATION_GATE_V1."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pymia.smartpyme.service_1_runtime_release_gate_v1 import (
    AUTHORIZATION_DECISION,
    AUTHORIZATION_SCOPE,
    STATUS_BLOCKED_BY_COMPOSITION,
    STATUS_BLOCKED_BY_GUARD,
    STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION,
    STATUS_BLOCKED_BY_OWNER_CONFIRMATION,
    STATUS_BLOCKED_BY_POLICY,
    STATUS_BLOCKED_BY_SCOPE,
    STATUS_RUNTIME_AUTHORIZED,
    Service1RuntimeAuthorizationGateResultV1,
    build_service_1_runtime_authorization_gate_v1,
)
from pymia.smartpyme.service_1_semantic_plan_to_xlsx_bridge_composition_v1 import (
    STATUS_BLOCKED_BY_SEMANTIC_PLAN,
    STATUS_COMPOSITION_CANDIDATE_READY,
    Service1SemanticPlanToXlsxBridgeCompositionV1,
)


def _composition(*, ready: bool = True) -> Service1SemanticPlanToXlsxBridgeCompositionV1:
    return Service1SemanticPlanToXlsxBridgeCompositionV1(
        composition_status=STATUS_COMPOSITION_CANDIDATE_READY if ready else STATUS_BLOCKED_BY_SEMANTIC_PLAN,
        pathology_code="REN_001",
        case_id="case_s1_001",
        tenant_id="tenant_demo",
        intake_id="intake_001",
        run_id="run_001",
        owner_ref="owner_demo",
        semantic_plan_status="SERVICE_1_SEMANTIC_RUNTIME_PLAN_READY_CANDIDATE",
        xlsx_bridge_status="BRIDGE_PACKAGE_CANDIDATE_READY",
        owner_confirmation_status="OWNER_CONFIRMED" if ready else "OWNER_CONFIRMATION_REQUIRED",
        allowed_computation_ref="first_aid_precio_margen_basico_v1",
        bridge_allowed_computation_ref="first_aid_precio_margen_basico_v1",
        package_candidate_ref="pkg_001",
        composition_candidate_prepared=ready,
        semantic_plan_ready=ready,
        xlsx_bridge_ready=ready,
        owner_confirmed=ready,
        owner_confirmation_required=not ready,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        product_ready=False,
        blocking_layer=None if ready else "semantic_plan",
        blocking_reasons=() if ready else ("semantic_plan_not_ready",),
        metadata={"rule": "ready" if ready else "semantic_plan_not_ready"},
    )


def _packet(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "operator_ref": "operator_001",
        "authorization_decision": AUTHORIZATION_DECISION,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "authorized_case_id": "case_s1_001",
        "authorized_run_id": "run_001",
        "authorized_owner_ref": "owner_demo",
        "allowed_computation_ref": "first_aid_precio_margen_basico_v1",
        "human_review_completed": True,
        "owner_confirmation_seen": True,
        "controlled_runtime_session_ref": "runtime_session_001",
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "product_ready": False,
        "publish_authorized": False,
        "notification_authorized": False,
        "service_2_opened": False,
        "phase_j_opened": False,
        "llm_authorized": False,
        "api_exposed": False,
    }
    packet.update(overrides)
    return packet


def _build(
    *,
    composition: Service1SemanticPlanToXlsxBridgeCompositionV1 | None = None,
    packet: dict[str, object] | None = None,
) -> Service1RuntimeAuthorizationGateResultV1:
    return build_service_1_runtime_authorization_gate_v1(
        composition=composition or _composition(),
        operator_authorization_packet=_packet() if packet is None else packet,
    )


def _assert_delivery_closed(result: Service1RuntimeAuthorizationGateResultV1) -> None:
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.autonomous_delivery_authorized is False
    assert result.product_ready is False
    assert result.execution_done is False


def test_ready_composition_and_operator_packet_authorize_controlled_runtime_only() -> None:
    result = _build()

    assert result.gate_status == STATUS_RUNTIME_AUTHORIZED
    assert result.runtime_authorization_candidate_prepared is True
    assert result.runtime_authorized is True
    assert result.runtime_execution_authorized is True
    assert result.pipeline_execution_authorized is True
    assert result.operator_ref == "operator_001"
    assert result.controlled_runtime_session_ref == "runtime_session_001"
    assert result.next_required_action == "RUN_CONTROLLED_SERVICE_1_RUNTIME"
    _assert_delivery_closed(result)


def test_blocked_composition_cannot_authorize_runtime() -> None:
    result = _build(composition=_composition(ready=False))

    assert result.gate_status == STATUS_BLOCKED_BY_COMPOSITION
    assert result.runtime_authorized is False
    assert result.blocking_layer == "composition"
    assert result.blocking_reasons == ("composition_candidate_not_ready",)
    _assert_delivery_closed(result)


def test_owner_confirmation_required_blocks_runtime() -> None:
    composition = replace(
        _composition(),
        owner_confirmed=False,
        owner_confirmation_required=True,
    )
    result = _build(composition=composition)

    assert result.gate_status == STATUS_BLOCKED_BY_OWNER_CONFIRMATION
    assert result.runtime_authorized is False
    assert result.next_required_action == "REQUEST_OWNER_CONFIRMATION"
    assert result.blocking_reasons == ("owner_confirmation_required",)
    _assert_delivery_closed(result)


def test_missing_operator_packet_blocks_runtime() -> None:
    result = _build(packet={})

    assert result.gate_status == STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION
    assert result.runtime_authorized is False
    assert result.next_required_action == "REQUEST_OPERATOR_AUTHORIZATION"
    assert result.blocking_reasons == ("operator_authorization_packet_required",)
    _assert_delivery_closed(result)


def test_wrong_authorization_scope_blocks_runtime() -> None:
    result = _build(packet=_packet(authorization_scope="SERVICE_1_DELIVERY"))

    assert result.gate_status == STATUS_BLOCKED_BY_SCOPE
    assert result.runtime_authorized is False
    assert result.operator_ref == "operator_001"
    assert result.blocking_reasons == ("authorization_scope_must_be_service_1_xlsx_runtime_only",)
    _assert_delivery_closed(result)


def test_reference_mismatch_blocks_runtime() -> None:
    result = _build(packet=_packet(authorized_run_id="other_run"))

    assert result.gate_status == STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION
    assert result.runtime_authorized is False
    assert result.blocking_layer == "operator_authorization_refs"
    assert result.blocking_reasons == ("run_id_mismatch",)
    _assert_delivery_closed(result)


def test_human_review_is_required() -> None:
    result = _build(packet=_packet(human_review_completed=False))

    assert result.gate_status == STATUS_BLOCKED_BY_OPERATOR_AUTHORIZATION
    assert result.runtime_authorized is False
    assert result.blocking_reasons == ("human_review_completed_required",)
    _assert_delivery_closed(result)


def test_operator_delivery_flag_blocks_runtime() -> None:
    result = _build(packet=_packet(delivery_authorized=True))

    assert result.gate_status == STATUS_BLOCKED_BY_GUARD
    assert result.runtime_authorized is False
    assert result.blocking_layer == "operator_authorization_guard"
    assert result.blocking_reasons == ("operator_delivery_authorized_must_be_false",)
    _assert_delivery_closed(result)


def test_policy_violation_blocks_runtime() -> None:
    result = _build(packet=_packet(policy_violation=True))

    assert result.gate_status == STATUS_BLOCKED_BY_POLICY
    assert result.runtime_authorized is False
    assert result.blocking_layer == "policy"
    assert result.blocking_reasons == ("policy_violation",)
    _assert_delivery_closed(result)


def test_upstream_runtime_open_blocks_before_authorization() -> None:
    result = _build(composition=replace(_composition(), runtime_authorized=True))

    assert result.gate_status == STATUS_BLOCKED_BY_GUARD
    assert result.runtime_authorized is False
    assert result.blocking_layer == "composition_guard"
    assert result.blocking_reasons == ("composition_runtime_authorized_must_enter_gate_false",)
    _assert_delivery_closed(result)


def test_product_module_has_no_cli_parser_or_delivery_paths() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_runtime_release_gate_v1.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "pymia.cli",
        "document_ingestion",
        "xlsx_to_normalized",
        "excel_lab_ingestion",
        "service_1_xlsx_runtime_bridge_contract_v1",
        "delivery_authorized=True",
        "autonomous_delivery_authorized=True",
        "product_ready=True",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in content
