"""
SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_TESTS_V1

Focal tests for the fail-closed port between bounded semantic invocation and a
future bounded semantic engine. The port prepares a contract candidate only; it
must never execute or authorize engine/runtime/CLI/delivery/product-ready.
"""
from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_semantic_binding_bounded_invocation_v1 import (
    SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE,
    Service1SemanticBindingBoundedInvocationResultV1,
)
from pymia.smartpyme.service_1_bounded_semantic_engine_invocation_port_v1 import (
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_DELIVERY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_ENGINE_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_EXECUTION_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PHASE_5_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_POLICY,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PRODUCT_READY_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_RUNTIME_GUARD,
    SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE,
    Service1BoundedSemanticEngineInvocationPortResultV1,
    build_bounded_semantic_engine_invocation_port_result_v1,
)


def _invocation(
    ready: bool = True,
    invocation_prepared: bool | None = None,
    execution_allowed: bool = False,
    bounded_engine_execution_allowed: bool = False,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    delivery_allowed: bool = False,
    policy_violation: bool = False,
) -> Service1SemanticBindingBoundedInvocationResultV1:
    if invocation_prepared is None:
        invocation_prepared = ready
    metadata: dict[str, object] = {}
    if policy_violation:
        metadata["policy_violation"] = True
    if bounded_engine_execution_allowed:
        metadata["bounded_engine_execution_allowed"] = True
    if delivery_allowed:
        metadata["delivery_allowed"] = True

    return Service1SemanticBindingBoundedInvocationResultV1(
        pathology_code="PATH_001",
        invocation_status=(
            SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE
            if ready
            else "SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS"
        ),
        harness_status=(
            "SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE"
            if ready
            else "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION"
        ),
        semantic_binding_invocation_prepared=invocation_prepared,
        semantic_binding_execution_allowed=execution_allowed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        delivery_allowed=delivery_allowed,
        blocking_layer=None if ready else "harness",
        blocking_reasons=() if ready else ("harness_not_ready",),
        metadata=metadata,
    )


def _build(invocation_result=None):
    return build_bounded_semantic_engine_invocation_port_result_v1(
        invocation_result or _invocation()
    )


def _assert_fail_closed(result: Service1BoundedSemanticEngineInvocationPortResultV1):
    assert result.semantic_binding_execution_allowed is False
    assert result.bounded_engine_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False


def test_port_result_schema_is_stable_and_fail_closed():
    result = _build()
    assert result.schema_version == "SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_V1"
    assert result.service_name == "SERVICE_1"
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE
    assert result.bounded_engine_invocation_port_prepared is True
    _assert_fail_closed(result)


def test_port_blocks_when_bounded_invocation_status_not_ready():
    result = _build(_invocation(ready=False))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION
    assert result.blocking_layer == "bounded_invocation"
    assert result.bounded_engine_invocation_port_prepared is False
    _assert_fail_closed(result)


def test_port_blocks_when_invocation_not_prepared():
    result = _build(_invocation(ready=True, invocation_prepared=False))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_INVOCATION
    assert result.blocking_layer == "bounded_invocation"
    assert result.blocking_reasons == ("semantic_binding_invocation_not_prepared",)
    _assert_fail_closed(result)


def test_port_blocks_policy_violation_before_readiness():
    result = _build(_invocation(policy_violation=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_POLICY
    assert result.blocking_layer == "policy"
    _assert_fail_closed(result)


def test_port_blocks_semantic_execution_guard():
    result = _build(_invocation(execution_allowed=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_EXECUTION_GUARD
    assert result.blocking_layer == "execution_guard"
    _assert_fail_closed(result)


def test_port_blocks_bounded_engine_execution_guard_from_metadata():
    result = _build(_invocation(bounded_engine_execution_allowed=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_ENGINE_GUARD
    assert result.blocking_layer == "engine_guard"
    _assert_fail_closed(result)


def test_port_blocks_runtime_guard():
    result = _build(_invocation(runtime_allowed=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_RUNTIME_GUARD
    assert result.blocking_layer == "runtime_guard"
    _assert_fail_closed(result)


def test_port_blocks_phase_5_guard():
    result = _build(_invocation(phase_5_allowed=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PHASE_5_GUARD
    assert result.blocking_layer == "phase_5_guard"
    _assert_fail_closed(result)


def test_port_blocks_product_ready_guard():
    result = _build(_invocation(product_ready=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_PRODUCT_READY_GUARD
    assert result.blocking_layer == "product_ready_guard"
    _assert_fail_closed(result)


def test_port_blocks_delivery_guard_from_field():
    result = _build(_invocation(delivery_allowed=True))
    assert result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_BLOCKED_BY_DELIVERY_GUARD
    assert result.blocking_layer == "delivery_guard"
    _assert_fail_closed(result)


def test_ready_candidate_preserves_pathology_and_upstream_status():
    result = _build()
    assert result.pathology_code == "PATH_001"
    assert result.invocation_status == SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE
    assert result.blocking_layer is None
    assert result.blocking_reasons == ()
    assert result.metadata == {"rule": "ready"}


def test_blocked_candidate_preserves_pathology_and_reason():
    result = _build(_invocation(runtime_allowed=True))
    assert result.pathology_code == "PATH_001"
    assert result.blocking_reasons == ("runtime_guard_open",)
    assert result.metadata == {"rule": "runtime_guard_open"}


def test_port_prepared_true_only_for_ready_candidate():
    ready_result = _build()
    blocked_results = [
        _build(_invocation(ready=False)),
        _build(_invocation(ready=True, invocation_prepared=False)),
        _build(_invocation(execution_allowed=True)),
        _build(_invocation(bounded_engine_execution_allowed=True)),
        _build(_invocation(runtime_allowed=True)),
        _build(_invocation(phase_5_allowed=True)),
        _build(_invocation(product_ready=True)),
        _build(_invocation(delivery_allowed=True)),
        _build(_invocation(policy_violation=True)),
    ]
    assert ready_result.bounded_engine_invocation_port_prepared is True
    assert ready_result.port_status == SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE
    for result in blocked_results:
        assert result.bounded_engine_invocation_port_prepared is False
        assert result.port_status != SERVICE_1_BOUNDED_SEMANTIC_ENGINE_INVOCATION_PORT_READY_CANDIDATE


def test_product_module_does_not_reference_forbidden_runtime_paths():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_bounded_semantic_engine_invocation_port_v1.py"
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
