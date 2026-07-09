"""
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TESTS_V1

Test-only suite for the future semantic binding activation boundary.

The activation implementation does not exist yet. Per task rules, tests import
the future module via importorskip and build synthetic composition outputs.
When the activation module is implemented, these tests become live without
modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Activation implementation not yet created: skip entire module until present.
activation = pytest.importorskip(
    "pymia.smartpyme.service_1_semantic_binding_activation_v1"
)

from pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1 import (  # noqa: E402
    COMPOSITION_READY_FOR_SEMANTIC_BINDING,
    Service1RuntimeCatalogPipelineCompositionResultV1,
)


def _composition(
    ready: bool = True,
    consideration_allowed: bool | None = None,
    runtime_allowed: bool = False,
    phase_5_allowed: bool = False,
    product_ready: bool = False,
    policy_violation: bool = False,
) -> Service1RuntimeCatalogPipelineCompositionResultV1:
    if consideration_allowed is None:
        consideration_allowed = ready
    return Service1RuntimeCatalogPipelineCompositionResultV1(
        pathology_code="PATH_001",
        composition_status=(
            COMPOSITION_READY_FOR_SEMANTIC_BINDING
            if ready
            else "COMPOSITION_BLOCKED_BY_GATE"
        ),
        catalog_binding_status="CATALOG_BINDING_READY_CANDIDATE",
        adapter_status="ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION",
        handoff_status="HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING",
        owner_confirmation_status="OWNER_CONFIRMED",
        gate_status="PIPELINE_READY_FOR_SEMANTIC_BINDING",
        blocking_layer=None if ready else "readiness_gate",
        blocking_reasons=() if ready else ("gate_not_ready",),
        semantic_binding_consideration_allowed=consideration_allowed,
        runtime_allowed=runtime_allowed,
        phase_5_allowed=phase_5_allowed,
        product_ready=product_ready,
        metadata={"policy_violation": True} if policy_violation else {},
    )


def _build(composition_result=None):
    return activation.build_semantic_binding_activation_result_v1(
        composition_result or _composition()
    )


def test_activation_blocks_when_composition_status_not_ready():
    result = _build(_composition(ready=False))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
    )
    assert result.semantic_binding_activation_allowed is False
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False


def test_activation_blocks_when_semantic_binding_consideration_not_allowed():
    result = _build(_composition(ready=True, consideration_allowed=False))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
    )
    assert result.semantic_binding_activation_allowed is False
    assert result.semantic_binding_execution_allowed is False


def test_activation_blocks_on_policy_violation():
    result = _build(_composition(policy_violation=True))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY
    )
    assert result.blocking_layer == "policy"
    assert result.semantic_binding_activation_allowed is False
    assert result.semantic_binding_execution_allowed is False


def test_activation_blocks_if_runtime_guard_is_open_upstream():
    result = _build(_composition(runtime_allowed=True))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD
    )
    assert result.blocking_layer == "runtime_guard"
    assert result.runtime_allowed is False
    assert result.semantic_binding_activation_allowed is False


def test_activation_blocks_if_phase_5_guard_is_open_upstream():
    result = _build(_composition(phase_5_allowed=True))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD
    )
    assert result.blocking_layer == "phase_5_guard"
    assert result.phase_5_allowed is False
    assert result.semantic_binding_activation_allowed is False


def test_activation_blocks_if_product_ready_guard_is_open_upstream():
    result = _build(_composition(product_ready=True))
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD
    )
    assert result.blocking_layer == "product_ready_guard"
    assert result.product_ready is False
    assert result.semantic_binding_activation_allowed is False


def test_activation_ready_candidate_only_when_composition_ready_and_guards_closed():
    result = _build(_composition())
    assert result.activation_status == (
        activation.SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
    )
    assert result.semantic_binding_activation_allowed is True
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False
    assert result.blocking_layer is None
    assert result.blocking_reasons == ()


@pytest.mark.parametrize(
    "composition_result",
    [
        pytest.param(_composition(), id="ready"),
        pytest.param(_composition(ready=False), id="composition_blocked"),
        pytest.param(
            _composition(ready=True, consideration_allowed=False),
            id="consideration_blocked",
        ),
        pytest.param(_composition(policy_violation=True), id="policy_blocked"),
        pytest.param(_composition(runtime_allowed=True), id="runtime_guard"),
        pytest.param(_composition(phase_5_allowed=True), id="phase_5_guard"),
        pytest.param(_composition(product_ready=True), id="product_ready_guard"),
    ],
)
def test_activation_never_allows_execution_runtime_phase_5_or_product_ready(
    composition_result,
):
    result = _build(composition_result)
    assert result.semantic_binding_execution_allowed is False
    assert result.runtime_allowed is False
    assert result.phase_5_allowed is False
    assert result.product_ready is False


def test_activation_allowed_only_on_ready_candidate_path():
    assert _build(_composition()).semantic_binding_activation_allowed is True
    assert _build(_composition(ready=False)).semantic_binding_activation_allowed is False
    assert _build(
        _composition(ready=True, consideration_allowed=False)
    ).semantic_binding_activation_allowed is False
    assert _build(_composition(policy_violation=True)).semantic_binding_activation_allowed is False
    assert _build(_composition(runtime_allowed=True)).semantic_binding_activation_allowed is False
    assert _build(_composition(phase_5_allowed=True)).semantic_binding_activation_allowed is False
    assert _build(_composition(product_ready=True)).semantic_binding_activation_allowed is False


def test_activation_output_shape_is_complete():
    result = _build(_composition())
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "activation_status",
        "composition_status",
        "semantic_binding_activation_allowed",
        "semantic_binding_execution_allowed",
        "runtime_allowed",
        "phase_5_allowed",
        "product_ready",
        "blocking_layer",
        "blocking_reasons",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_activation_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_activation_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_activation_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_semantic_binding_activation_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
