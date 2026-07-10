"""
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_IMPLEMENTATION_TESTS_V1

Focal tests for the pure fail-closed bounded semantic engine boundary.
"""
from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_bounded_semantic_engine_contract_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE,
    Service1BoundedSemanticEngineContractResultV1,
)
from pymia.smartpyme.service_1_bounded_semantic_engine_implementation_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_DELIVERY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_EXECUTION_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PHASE_5_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_POLICY,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PRODUCT_READY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_RUNTIME_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE,
    Service1BoundedSemanticEngineResultV1,
    build_bounded_semantic_engine_result_v1,
)


def _contract(
    ready: bool = True,
    prepared: bool | None = None,
    execution_allowed: bool = False,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    delivery_allowed: bool = False,
    policy_violation: bool = False,
) -> Service1BoundedSemanticEngineContractResultV1:
    if prepared is None:
        prepared = ready
    metadata: dict[str, object] = {}
    if policy_violation:
        metadata["policy_violation"] = True
    if execution_allowed:
        metadata["bounded_semantic_engine_execution_allowed"] = True
    if delivery_allowed:
        metadata["delivery_allowed"] = True
    return Service1BoundedSemanticEngineContractResultV1(
        pathology_code="PATH_001",
        contract_status=(
            SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_READY_CANDIDATE
            if ready
            else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_CONTRACT_BLOCKED_BY_PORT"
        ),
        port_status=(
            "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE"
            if ready
            else "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION"
        ),
        bounded_semantic_engine_contract_prepared=prepared,
        bounded_semantic_engine_execution_allowed=execution_allowed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        delivery_allowed=delivery_allowed,
        blocking_layer=None if ready else "invocation_port",
        blocking_reasons=() if ready else ("invocation_port_not_ready",),
        metadata=metadata,
    )


def _build(contract_result=None):
    return build_bounded_semantic_engine_result_v1(contract_result or _contract())


def _assert_closed(result: Service1BoundedSemanticEngineResultV1) -> None:
    assert result.bounded_semantic_engine_execution_allowed is False
    assert result.execution_performed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False


def test_ready_contract_prepares_engine_candidate_but_never_executes():
    result = _build()
    assert result.schema_version == "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_IMPLEMENTATION_V1"
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE
    assert result.bounded_semantic_engine_candidate_prepared is True
    assert result.pathology_code == "PATH_001"
    assert result.blocking_layer is None
    _assert_closed(result)


def test_blocks_when_contract_status_not_ready():
    result = _build(_contract(ready=False))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT
    assert result.blocking_layer == "engine_contract"
    assert result.bounded_semantic_engine_candidate_prepared is False
    _assert_closed(result)


def test_blocks_when_contract_not_prepared():
    result = _build(_contract(ready=True, prepared=False))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_CONTRACT
    assert result.blocking_reasons == ("engine_contract_not_prepared",)
    _assert_closed(result)


def test_blocks_policy_violation():
    result = _build(_contract(policy_violation=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_POLICY
    assert result.blocking_layer == "policy"
    _assert_closed(result)


def test_blocks_execution_guard():
    result = _build(_contract(execution_allowed=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_EXECUTION_GUARD
    assert result.blocking_layer == "execution_guard"
    _assert_closed(result)


def test_blocks_runtime_guard():
    result = _build(_contract(runtime_allowed=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_RUNTIME_GUARD
    assert result.blocking_layer == "runtime_guard"
    _assert_closed(result)


def test_blocks_phase_5_guard():
    result = _build(_contract(phase_5_allowed=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PHASE_5_GUARD
    assert result.blocking_layer == "phase_5_guard"
    _assert_closed(result)


def test_blocks_product_ready_guard():
    result = _build(_contract(product_ready=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_PRODUCT_READY_GUARD
    assert result.blocking_layer == "product_ready_guard"
    _assert_closed(result)


def test_blocks_delivery_guard():
    result = _build(_contract(delivery_allowed=True))
    assert result.engine_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_BLOCKED_BY_DELIVERY_GUARD
    assert result.blocking_layer == "delivery_guard"
    _assert_closed(result)


def test_candidate_prepared_true_only_for_ready_contract():
    ready = _build()
    blocked = [
        _build(_contract(ready=False)),
        _build(_contract(ready=True, prepared=False)),
        _build(_contract(policy_violation=True)),
        _build(_contract(execution_allowed=True)),
        _build(_contract(runtime_allowed=True)),
        _build(_contract(phase_5_allowed=True)),
        _build(_contract(product_ready=True)),
        _build(_contract(delivery_allowed=True)),
    ]
    assert ready.bounded_semantic_engine_candidate_prepared is True
    for result in blocked:
        assert result.bounded_semantic_engine_candidate_prepared is False
        assert result.engine_status != SERVICE_1_BOUNDED_SEMANTIC_ENGINE_READY_CANDIDATE
        _assert_closed(result)


def test_product_module_has_no_forbidden_runtime_paths():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_bounded_semantic_engine_implementation_v1.py"
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
