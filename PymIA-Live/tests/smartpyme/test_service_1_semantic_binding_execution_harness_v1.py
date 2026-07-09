"""
SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_TESTS_V1

Test-only suite for the future semantic binding execution harness.

The harness implementation does not exist yet. Per task rules, tests import
the future module via importorskip and build synthetic activation outputs.
When the harness module is implemented, these tests become live without
modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Harness implementation not yet created: skip entire module until present.
harness = pytest.importorskip(
    "pymia.smartpyme.service_1_semantic_binding_execution_harness_v1"
)

from pymia.smartpyme.service_1_semantic_binding_activation_v1 import (  # noqa: E402
    SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE,
    Service1SemanticBindingActivationResultV1,
)


def _activation(
    ready: bool = True,
    activation_allowed: bool | None = None,
    execution_allowed: bool = False,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    policy_violation: bool = False,
) -> Service1SemanticBindingActivationResultV1:
    if activation_allowed is None:
        activation_allowed = ready
    return Service1SemanticBindingActivationResultV1(
        pathology_code="PATH_001",
        activation_status=(
            SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
            if ready
            else "SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION"
        ),
        composition_status="COMPOSITION_READY_FOR_SEMANTIC_BINDING",
        semantic_binding_activation_allowed=activation_allowed,
        semantic_binding_execution_allowed=execution_allowed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        blocking_layer=None if ready else "composition",
        blocking_reasons=() if ready else ("composition_not_ready",),
        metadata={"policy_violation": True} if policy_violation else {},
    )


def _build(activation_result=None):
    return harness.build_semantic_binding_execution_harness_result_v1(
        activation_result or _activation()
    )


def test_harness_blocks_when_activation_status_not_ready():
    result = _build(_activation(ready=False))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
    )
    assert result.semantic_binding_request_prepared is False
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False


def test_harness_blocks_when_activation_candidacy_not_allowed():
    result = _build(_activation(ready=True, activation_allowed=False))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
    )
    assert result.semantic_binding_request_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_harness_blocks_on_policy_violation():
    result = _build(_activation(policy_violation=True))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY
    )
    assert result.blocking_layer == "policy"
    assert result.semantic_binding_request_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_harness_blocks_if_execution_guard_is_open_upstream():
    result = _build(_activation(execution_allowed=True))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD
    )
    assert result.blocking_layer == "execution_guard"
    assert result.semantic_binding_request_prepared is False
    assert result.semantic_binding_execution_allowed is False


def test_harness_blocks_if_runtime_guard_is_open_upstream():
    result = _build(_activation(runtime_allowed=True))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD
    )
    assert result.blocking_layer == "runtime_guard"
    assert result.semantic_binding_request_prepared is False
    assert result.runtime_allowed is False


def test_harness_blocks_if_phase_5_guard_is_open_upstream():
    result = _build(_activation(phase_5_allowed=True))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD
    )
    assert result.blocking_layer == "phase_5_guard"
    assert result.semantic_binding_request_prepared is False
    assert result.phase_5_allowed is False


def test_harness_blocks_if_product_ready_guard_is_open_upstream():
    result = _build(_activation(product_ready=True))
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD
    )
    assert result.blocking_layer == "product_ready_guard"
    assert result.semantic_binding_request_prepared is False
    assert result.product_ready is False


def test_harness_ready_request_candidate_only_when_activation_ready_and_guards_closed():
    result = _build(_activation())
    assert result.harness_status == (
        harness.SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE
    )
    assert result.semantic_binding_request_prepared is True
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.blocking_layer is None
    assert result.blocking_reasons == ()


@pytest.mark.parametrize(
    "activation_result",
    [
        pytest.param(_activation(), id="ready"),
        pytest.param(_activation(ready=False), id="activation_blocked"),
        pytest.param(_activation(ready=True, activation_allowed=False), id="candidacy_blocked"),
        pytest.param(_activation(policy_violation=True), id="policy_blocked"),
        pytest.param(_activation(execution_allowed=True), id="execution_guard"),
        pytest.param(_activation(runtime_allowed=True), id="runtime_guard"),
        pytest.param(_activation(phase_5_allowed=True), id="phase_5_guard"),
        pytest.param(_activation(product_ready=True), id="product_ready_guard"),
    ],
)
def test_harness_never_allows_execution_runtime_phase_5_or_product_ready(
    activation_result,
):
    result = _build(activation_result)
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False


def test_request_prepared_only_on_ready_request_candidate_path():
    assert _build(_activation()).semantic_binding_request_prepared is True
    assert _build(_activation(ready=False)).semantic_binding_request_prepared is False
    assert _build(_activation(ready=True, activation_allowed=False)).semantic_binding_request_prepared is False
    assert _build(_activation(policy_violation=True)).semantic_binding_request_prepared is False
    assert _build(_activation(execution_allowed=True)).semantic_binding_request_prepared is False
    assert _build(_activation(runtime_allowed=True)).semantic_binding_request_prepared is False
    assert _build(_activation(phase_5_allowed=True)).semantic_binding_request_prepared is False
    assert _build(_activation(product_ready=True)).semantic_binding_request_prepared is False


def test_harness_output_shape_is_complete():
    result = _build(_activation())
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "harness_status",
        "activation_status",
        "semantic_binding_request_prepared",
        "semantic_binding_execution_allowed",
        "runtime_allowed",
        "phase_5_allowed",
        "product_ready",
        "blocking_layer",
        "blocking_reasons",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_harness_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_execution_harness_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_harness_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_execution_harness_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
