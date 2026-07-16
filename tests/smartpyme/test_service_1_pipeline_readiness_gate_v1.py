"""
SERVICE_1_PIPELINE_READINESS_GATE_TESTS_V1

Test-only suite for the future pipeline readiness gate.

The gate implementation does not exist yet. Per task rules, tests import
the future module via importorskip and build synthetic upstream layer
outputs. When the gate module is implemented, these tests become live
without modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Gate implementation not yet created: skip entire module until present.
gate = pytest.importorskip(
    "pymia.smartpyme.service_1_pipeline_readiness_gate_v1"
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
            ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION if ready
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
            HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING if ready
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


def test_gate_blocks_when_catalog_not_ready():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(ready=False), _adapter(), _handoff(), _owner()
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_CATALOG


def test_gate_blocks_when_adapter_not_ready():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(ready=False), _handoff(), _owner()
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_ADAPTER


def test_gate_blocks_when_handoff_not_ready():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(ready=False), _owner()
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_HANDOFF


def test_gate_blocks_when_owner_not_confirmed():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(), _owner(confirmed=False)
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_OWNER_CONFIRMATION


def test_gate_blocks_when_required_evidence_missing():
    catalog = _catalog()
    object.__setattr__(catalog, "required_evidence", ())
    result = gate.build_pipeline_readiness_gate_result_v1(
        catalog, _adapter(), _handoff(), _owner()
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_EVIDENCE


def test_gate_blocks_on_policy_violation():
    catalog = _catalog()
    object.__setattr__(catalog, "metadata", {"policy_violation": True})
    result = gate.build_pipeline_readiness_gate_result_v1(
        catalog, _adapter(), _handoff(), _owner()
    )
    assert result.gate_status == gate.PIPELINE_BLOCKED_BY_POLICY


def test_gate_ready_when_all_layers_ready():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(), _owner()
    )
    assert result.gate_status == gate.PIPELINE_READY_FOR_SEMANTIC_BINDING


def test_gate_preserves_runtime_allowed_false():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(), _owner()
    )
    assert result.runtime_allowed is False


def test_gate_preserves_phase_5_allowed_false():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(), _owner()
    )
    assert result.phase_5_allowed is False


def test_gate_output_shape_is_complete():
    result = gate.build_pipeline_readiness_gate_result_v1(
        _catalog(), _adapter(), _handoff(), _owner()
    )
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "gate_status",
        "catalog_binding_status",
        "adapter_status",
        "handoff_status",
        "owner_confirmation_status",
        "blocking_layer",
        "blocking_reasons",
        "runtime_allowed",
        "phase_5_allowed",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_gate_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_pipeline_readiness_gate_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_gate_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_pipeline_readiness_gate_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
