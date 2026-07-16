"""
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TESTS_V1

Test-only suite for the future runtime catalog pipeline composition layer.

The composition implementation does not exist yet. Per task rules, tests import
the future module via importorskip and build synthetic upstream governed outputs.
When the composition module is implemented, these tests become live without
modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Composition implementation not yet created: skip entire module until present.
composition = pytest.importorskip(
    "pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1"
)

from pymia.smartpyme.service_1_runtime_catalog_binding_contract_v1 import (  # noqa: E402
    CATALOG_BINDING_READY_CANDIDATE,
    Service1RuntimeCatalogBindingResultV1,
)
from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (  # noqa: E402
    ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
    Service1RuntimeCatalogBindingAdapterContextV1,
)
from pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1 import (  # noqa: E402
    HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING,
    Service1SemanticBindingConsiderationContextV1,
)
from pymia.smartpyme.service_1_owner_confirmation_boundary_v1 import (  # noqa: E402
    OWNER_CONFIRMED,
    Service1OwnerConfirmationResultV1,
)
from pymia.smartpyme.service_1_pipeline_readiness_gate_v1 import (  # noqa: E402
    PIPELINE_READY_FOR_SEMANTIC_BINDING,
    Service1PipelineReadinessGateResultV1,
)


def _catalog(ready: bool = True) -> Service1RuntimeCatalogBindingResultV1:
    return Service1RuntimeCatalogBindingResultV1(
        pathology_code="PATH_001",
        readiness_status=(
            CATALOG_BINDING_READY_CANDIDATE if ready else "MISSING_FORMULA_REFS"
        ),
        formula_refs=("F001",) if ready else (),
        required_variables=("v1",) if ready else (),
        required_evidence=("E001",) if ready else (),
    )


def _adapter(ready: bool = True) -> Service1RuntimeCatalogBindingAdapterContextV1:
    return Service1RuntimeCatalogBindingAdapterContextV1(
        pathology_code="PATH_001",
        upstream_readiness_status=CATALOG_BINDING_READY_CANDIDATE,
        adapter_status=(
            ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION
            if ready
            else "ADAPTER_BLOCKED_BY_POLICY"
        ),
        formula_refs=("F001",),
        resolved_formula_ids=("F001",),
        required_variables=("v1",),
        resolved_variables=("v1",),
        required_evidence=("E001",),
        minimum_semantic_bindings=("b1",),
    )


def _handoff(ready: bool = True) -> Service1SemanticBindingConsiderationContextV1:
    return Service1SemanticBindingConsiderationContextV1(
        pathology_code="PATH_001",
        upstream_adapter_status=ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
        handoff_status=(
            HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING
            if ready
            else "HANDOFF_BLOCKED_BY_POLICY"
        ),
        formula_refs=("F001",),
        resolved_formula_ids=("F001",),
        required_variables=("v1",),
        resolved_variables=("v1",),
        required_evidence=("E001",),
        minimum_semantic_bindings=("b1",),
        semantic_evidence_binding_allowed=ready,
    )


def _owner(confirmed: bool = True) -> Service1OwnerConfirmationResultV1:
    return Service1OwnerConfirmationResultV1(
        pathology_code="PATH_001",
        confirmation_status=OWNER_CONFIRMED if confirmed else "OWNER_CONFIRMATION_REQUIRED",
        confirmed_evidence=("E001",) if confirmed else (),
        confirmed_semantic_bindings=("b1",) if confirmed else (),
    )


def _gate(ready: bool = True) -> Service1PipelineReadinessGateResultV1:
    return Service1PipelineReadinessGateResultV1(
        pathology_code="PATH_001",
        gate_status=(
            PIPELINE_READY_FOR_SEMANTIC_BINDING
            if ready
            else "PIPELINE_BLOCKED_BY_HANDOFF"
        ),
        catalog_binding_status=CATALOG_BINDING_READY_CANDIDATE,
        adapter_status=ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
        handoff_status=HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING,
        owner_confirmation_status=OWNER_CONFIRMED,
        blocking_layer=None if ready else "handoff",
        blocking_reasons=() if ready else ("handoff_not_ready",),
    )


def _build(catalog=None, adapter=None, handoff=None, owner=None, gate=None):
    return composition.build_runtime_catalog_pipeline_composition_result_v1(
        catalog or _catalog(),
        adapter or _adapter(),
        handoff or _handoff(),
        owner or _owner(),
        gate or _gate(),
    )


def test_composition_blocks_when_catalog_not_ready():
    result = _build(catalog=_catalog(ready=False))
    assert result.composition_status == composition.COMPOSITION_BLOCKED_BY_CATALOG
    assert result.blocking_layer == "catalog"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_blocks_when_adapter_not_ready():
    result = _build(adapter=_adapter(ready=False))
    assert result.composition_status == composition.COMPOSITION_BLOCKED_BY_ADAPTER
    assert result.blocking_layer == "adapter"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_blocks_when_handoff_not_ready():
    result = _build(handoff=_handoff(ready=False))
    assert result.composition_status == composition.COMPOSITION_BLOCKED_BY_HANDOFF
    assert result.blocking_layer == "handoff"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_blocks_when_owner_not_confirmed():
    result = _build(owner=_owner(confirmed=False))
    assert result.composition_status == (
        composition.COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION
    )
    assert result.blocking_layer == "owner_confirmation"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_blocks_when_gate_not_ready():
    result = _build(gate=_gate(ready=False))
    assert result.composition_status == composition.COMPOSITION_BLOCKED_BY_GATE
    assert result.blocking_layer == "readiness_gate"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_blocks_on_policy_violation():
    catalog = _catalog()
    object.__setattr__(catalog, "metadata", {"policy_violation": True})
    result = _build(catalog=catalog)
    assert result.composition_status == composition.COMPOSITION_BLOCKED_BY_POLICY
    assert result.blocking_layer == "policy"
    assert result.semantic_binding_consideration_allowed is False


def test_composition_ready_when_all_layers_and_gate_ready():
    result = _build()
    assert result.composition_status == composition.COMPOSITION_READY_FOR_SEMANTIC_BINDING
    assert result.blocking_layer is None
    assert result.blocking_reasons == ()
    assert result.semantic_binding_consideration_allowed is True


@pytest.mark.parametrize(
    "result",
    [
        pytest.param(_build, id="ready"),
        pytest.param(lambda: _build(catalog=_catalog(False)), id="catalog_blocked"),
        pytest.param(lambda: _build(adapter=_adapter(False)), id="adapter_blocked"),
        pytest.param(lambda: _build(handoff=_handoff(False)), id="handoff_blocked"),
        pytest.param(lambda: _build(owner=_owner(False)), id="owner_blocked"),
        pytest.param(lambda: _build(gate=_gate(False)), id="gate_blocked"),
    ],
)
def test_composition_never_allows_runtime_phase_5_or_product_ready(result):
    output = result()
    assert output.runtime_allowed is False
    assert output.phase_5_allowed is False
    assert output.product_ready is False


def test_semantic_binding_consideration_allowed_only_when_all_ready():
    assert _build().semantic_binding_consideration_allowed is True
    assert _build(catalog=_catalog(False)).semantic_binding_consideration_allowed is False
    assert _build(adapter=_adapter(False)).semantic_binding_consideration_allowed is False
    assert _build(handoff=_handoff(False)).semantic_binding_consideration_allowed is False
    assert _build(owner=_owner(False)).semantic_binding_consideration_allowed is False
    assert _build(gate=_gate(False)).semantic_binding_consideration_allowed is False


def test_composition_output_shape_is_complete():
    result = _build()
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "composition_status",
        "catalog_binding_status",
        "adapter_status",
        "handoff_status",
        "owner_confirmation_status",
        "gate_status",
        "blocking_layer",
        "blocking_reasons",
        "semantic_binding_consideration_allowed",
        "runtime_allowed",
        "phase_5_allowed",
        "product_ready",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_composition_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_composition_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
