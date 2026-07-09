"""
SERVICE_1_SEMANTIC_BINDING_BOUNDED_INVOCATION_TESTS_V1

Test-only suite for the future semantic binding bounded invocation boundary.

The bounded invocation implementation does not exist yet. Per task rules, tests
import the future module via importorskip and build synthetic harness outputs.
When the bounded invocation module is implemented, these tests become live
without modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Bounded invocation implementation not yet created: skip entire module until present.
invocation = pytest.importorskip(
    "pymia.smartpyme.service_1_semantic_binding_bounded_invocation_v1"
)

from pymia.smartpyme.service_1_semantic_binding_execution_harness_v1 import (  # noqa: E402
    SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE,
    Service1SemanticBindingExecutionHarnessResultV1,
)


def _harness(
    ready: bool = True,
    request_prepared: bool | None = None,
    execution_allowed: bool = False,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    policy_violation: bool = False,
    delivery_allowed: bool = False,
) -> Service1SemanticBindingExecutionHarnessResultV1:
    if request_prepared is None:
        request_prepared = ready
    metadata = {"policy_violation": True} if policy_violation else {}
    if delivery_allowed:
        metadata["delivery_allowed"] = True
    return Service1SemanticBindingExecutionHarnessResultV1(
        pathology_code="PATH_001",
        harness_status=(
            SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE
            if ready
            else "SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION"
        ),
        activation_status=(
            "SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE"
            if ready
            else "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION"
        ),
        semantic_binding_request_prepared=request_prepared,
        semantic_binding_execution_allowed=execution_allowed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        blocking_layer=None if ready else "activation",
        blocking_reasons=() if ready else ("activation_not_ready",),
        metadata=metadata,
    )


def _build(harness_result=None):
    return invocation.build_semantic_binding_bounded_invocation_result_v1(
        harness_result or _harness()
    )


def test_bounded_invocation_blocks_when_harness_status_not_ready():
    result = _build(_harness(ready=False))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS
    )
    assert result.semantic_binding_invocation_prepared is False
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False


def test_bounded_invocation_blocks_when_harness_request_is_not_prepared():
    result = _build(_harness(ready=True, request_prepared=False))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_HARNESS
    )
    assert result.blocking_layer == "harness"
    assert result.semantic_binding_invocation_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_bounded_invocation_blocks_on_policy_violation():
    result = _build(_harness(policy_violation=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_POLICY
    )
    assert result.blocking_layer == "policy"
    assert result.semantic_binding_invocation_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_bounded_invocation_blocks_if_execution_guard_is_open_upstream():
    result = _build(_harness(execution_allowed=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_EXECUTION_GUARD
    )
    assert result.blocking_layer == "execution_guard"
    assert result.semantic_binding_invocation_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_bounded_invocation_blocks_if_runtime_guard_is_open_upstream():
    result = _build(_harness(runtime_allowed=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_RUNTIME_GUARD
    )
    assert result.blocking_layer == "runtime_guard"
    assert result.semantic_binding_invocation_prepared is False
    assert result.runtime_allowed is False


def test_bounded_invocation_blocks_if_phase_5_guard_is_open_upstream():
    result = _build(_harness(phase_5_allowed=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PHASE_5_GUARD
    )
    assert result.blocking_layer == "phase_5_guard"
    assert result.semantic_binding_invocation_prepared is False
    assert result.phase_5_allowed is False


def test_bounded_invocation_blocks_if_product_ready_guard_is_open_upstream():
    result = _build(_harness(product_ready=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_PRODUCT_READY_GUARD
    )
    assert result.blocking_layer == "product_ready_guard"
    assert result.semantic_binding_invocation_prepared is False
    assert result.product_ready is False


def test_bounded_invocation_blocks_if_delivery_guard_is_open_upstream():
    result = _build(_harness(delivery_allowed=True))
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_BLOCKED_BY_DELIVERY_GUARD
    )
    assert result.blocking_layer == "delivery_guard"
    assert result.semantic_binding_invocation_prepared is False
    assert result.delivery_allowed is False


def test_bounded_invocation_ready_candidate_only_when_harness_ready_and_guards_closed():
    result = _build(_harness())
    assert result.invocation_status == (
        invocation.SEMANTIC_BINDING_BOUNDED_INVOCATION_READY_CANDIDATE
    )
    assert result.semantic_binding_invocation_prepared is True
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False
    assert result.blocking_layer is None
    assert result.blocking_reasons == ()


@pytest.mark.parametrize(
    "harness_result",
    [
        pytest.param(_harness(), id="ready"),
        pytest.param(_harness(ready=False), id="harness_blocked"),
        pytest.param(_harness(ready=True, request_prepared=False), id="request_not_prepared"),
        pytest.param(_harness(policy_violation=True), id="policy_blocked"),
        pytest.param(_harness(execution_allowed=True), id="execution_guard"),
        pytest.param(_harness(runtime_allowed=True), id="runtime_guard"),
        pytest.param(_harness(phase_5_allowed=True), id="phase_5_guard"),
        pytest.param(_harness(product_ready=True), id="product_ready_guard"),
        pytest.param(_harness(delivery_allowed=True), id="delivery_guard"),
    ],
)
def test_bounded_invocation_never_allows_execution_runtime_phase_5_product_ready_or_delivery(
    harness_result,
):
    result = _build(harness_result)
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.delivery_allowed is False


def test_invocation_prepared_only_on_ready_candidate_path():
    assert _build(_harness()).semantic_binding_invocation_prepared is True
    assert _build(_harness(ready=False)).semantic_binding_invocation_prepared is False
    assert _build(
        _harness(ready=True, request_prepared=False)
    ).semantic_binding_invocation_prepared is False
    assert _build(_harness(policy_violation=True)).semantic_binding_invocation_prepared is False
    assert _build(_harness(execution_allowed=True)).semantic_binding_invocation_prepared is False
    assert _build(_harness(runtime_allowed=True)).semantic_binding_invocation_prepared is False
    assert _build(_harness(phase_5_allowed=True)).semantic_binding_invocation_prepared is False
    assert _build(_harness(product_ready=True)).semantic_binding_invocation_prepared is False
    assert _build(_harness(delivery_allowed=True)).semantic_binding_invocation_prepared is False


def test_bounded_invocation_output_shape_is_complete():
    result = _build(_harness())
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "invocation_status",
        "harness_status",
        "semantic_binding_invocation_prepared",
        "semantic_binding_execution_allowed",
        "runtime_allowed",
        "phase_5_allowed",
        "product_ready",
        "delivery_allowed",
        "blocking_layer",
        "blocking_reasons",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_bounded_invocation_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_bounded_invocation_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_bounded_invocation_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_bounded_invocation_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
