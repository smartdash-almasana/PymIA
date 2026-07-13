"""Focal tests for SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_V1."""
from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_bounded_semantic_engine_invocation_port_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE,
    Service1BoundedSemanticEngineInvocationPortResultV1,
)
from pymia.smartpyme.service_1_bounded_semantic_engine_contract_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_DELIVERY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_EXECUTION_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PHASE_5_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_POLICY,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PRODUCT_READY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_RUNTIME_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE,
    build_bounded_semantic_engine_contract_result_v1,
)


def _port(
    *,
    ready: bool = True,
    prepared: bool | None = None,
    engine_execution: bool = False,
    runtime: bool = False,
    phase_5: bool = False,
    product_ready: bool = False,
    delivery: bool = False,
    policy: bool = False,
) -> Service1BoundedSemanticEngineInvocationPortResultV1:
    if prepared is None:
        prepared = ready
    metadata: dict[str, object] = {}
    if policy:
        metadata["policy_violation"] = True
    if engine_execution:
        metadata["bounded_engine_execution_allowed"] = True
    if delivery:
        metadata["delivery_allowed"] = True
    return Service1BoundedSemanticEngineInvocationPortResultV1(
        pathology_code="PATH_001",
        port_status=(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE
            if ready
            else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION"
        ),
        invocation_status="SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE",
        bounded_engine_invocation_port_prepared=prepared,
        bounded_engine_execution_allowed=engine_execution,
        runtime_allowed=runtime,
        phase_5_allowed=phase_5,
        product_ready=product_ready,
        delivery_allowed=delivery,
        metadata=metadata,
    )


def _build(port=None):
    return build_bounded_semantic_engine_contract_result_v1(port or _port())


def _assert_closed(result):
    assert result.bounded_semantic_engine_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False


def test_contract_ready_candidate_is_prepared_and_fail_closed():
    result = _build()
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE
    assert result.bounded_semantic_engine_contract_prepared is True
    assert result.pathology_code == "PATH_001"
    _assert_closed(result)


def test_contract_blocks_port_not_ready():
    result = _build(_port(ready=False))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT
    assert result.blocking_reasons == ("invocation_port_not_ready",)
    assert result.bounded_semantic_engine_contract_prepared is False
    _assert_closed(result)


def test_contract_blocks_port_not_prepared():
    result = _build(_port(ready=True, prepared=False))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT
    assert result.blocking_reasons == ("invocation_port_not_prepared",)
    _assert_closed(result)


def test_contract_blocks_policy_violation():
    result = _build(_port(policy=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_POLICY
    _assert_closed(result)


def test_contract_blocks_engine_execution_guard():
    result = _build(_port(engine_execution=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_EXECUTION_GUARD
    _assert_closed(result)


def test_contract_blocks_runtime_guard():
    result = _build(_port(runtime=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_RUNTIME_GUARD
    _assert_closed(result)


def test_contract_blocks_phase_5_guard():
    result = _build(_port(phase_5=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PHASE_5_GUARD
    _assert_closed(result)


def test_contract_blocks_product_ready_guard():
    result = _build(_port(product_ready=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PRODUCT_READY_GUARD
    _assert_closed(result)


def test_contract_blocks_delivery_guard():
    result = _build(_port(delivery=True))
    assert result.contract_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_DELIVERY_GUARD
    _assert_closed(result)


def test_prepared_true_only_for_ready_candidate():
    assert _build().bounded_semantic_engine_contract_prepared is True
    blocked = [
        _build(_port(ready=False)),
        _build(_port(ready=True, prepared=False)),
        _build(_port(policy=True)),
        _build(_port(engine_execution=True)),
        _build(_port(runtime=True)),
        _build(_port(phase_5=True)),
        _build(_port(product_ready=True)),
        _build(_port(delivery=True)),
    ]
    assert all(item.bounded_semantic_engine_contract_prepared is False for item in blocked)


def test_product_module_has_no_forbidden_paths():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_bounded_semantic_engine_contract_v1.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in content
