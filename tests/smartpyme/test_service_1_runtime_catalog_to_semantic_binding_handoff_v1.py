"""
SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_TESTS_V1

Test-only suite for the future handoff layer between
Service1RuntimeCatalogBindingAdapterContextV1 and a semantic evidence
binding consideration context.

The handoff implementation does not exist yet. Per task rules, tests
import the future module via importorskip and build synthetic adapter
contexts. When the handoff module is implemented, these tests become
live without modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Handoff implementation not yet created: skip entire module until present.
handoff = pytest.importorskip(
    "pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1"
)

from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (  # noqa: E402
    ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION,
    ADAPTER_BLOCKED_BY_POLICY,
    Service1RuntimeCatalogBindingAdapterContextV1,
)
from pymia.smartpyme.service_1_runtime_catalog_binding_adapter_v1 import (  # noqa: E402
    ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED,
)


READY_ADAPTER_STATUS = ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION


def _make_adapter_context(
    *,
    adapter_status: str = READY_ADAPTER_STATUS,
    formula_refs: tuple[str, ...] = ("F001",),
    required_variables: tuple[str, ...] = ("v_unit_price",),
    required_evidence: tuple[str, ...] = ("E001",),
    owner_confirmation_required: bool = False,
) -> Service1RuntimeCatalogBindingAdapterContextV1:
    return Service1RuntimeCatalogBindingAdapterContextV1(
        pathology_code="PATH_001",
        upstream_readiness_status="CATALOG_BINDING_READY_CANDIDATE",
        adapter_status=adapter_status,
        formula_refs=formula_refs,
        resolved_formula_ids=formula_refs,
        required_variables=required_variables,
        resolved_variables=required_variables,
        required_evidence=required_evidence,
        minimum_semantic_bindings=("b1",),
        owner_confirmation_required=owner_confirmation_required,
    )


def test_handoff_blocks_when_adapter_status_not_ready():
    ctx = _make_adapter_context(adapter_status=ADAPTER_BLOCKED_BY_POLICY)
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_BLOCKED_BY_ADAPTER_STATUS


def test_handoff_blocks_when_owner_confirmation_required():
    ctx = _make_adapter_context(owner_confirmation_required=True)
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED


def test_handoff_blocks_when_empty_formula_refs():
    ctx = _make_adapter_context(formula_refs=())
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS


def test_handoff_blocks_when_empty_required_variables():
    ctx = _make_adapter_context(required_variables=())
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES


def test_handoff_blocks_when_empty_required_evidence():
    ctx = _make_adapter_context(required_evidence=())
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE


def test_handoff_ready_when_adapter_ready_and_complete():
    ctx = _make_adapter_context()
    result = handoff.build_handoff_context_v1(ctx)
    assert result.handoff_status == handoff.HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING
    assert result.semantic_evidence_binding_allowed is True


def test_handoff_preserves_runtime_allowed_false():
    ctx = _make_adapter_context()
    result = handoff.build_handoff_context_v1(ctx)
    assert result.runtime_allowed is False


def test_handoff_preserves_phase_5_allowed_false():
    ctx = _make_adapter_context()
    result = handoff.build_handoff_context_v1(ctx)
    assert result.phase_5_allowed is False


def test_handoff_allows_semantic_binding_does_not_mean_runtime():
    ctx = _make_adapter_context()
    result = handoff.build_handoff_context_v1(ctx)
    assert result.semantic_evidence_binding_allowed is True
    assert result.runtime_allowed is False


def test_handoff_blocks_when_upstream_runtime_allowed_true():
    ctx = _make_adapter_context()
    object.__setattr__(ctx, "runtime_allowed", True)
    with pytest.raises(ValueError):
        handoff.build_handoff_context_v1(ctx)


def test_handoff_blocks_when_upstream_phase_5_allowed_true():
    ctx = _make_adapter_context()
    object.__setattr__(ctx, "phase_5_allowed", True)
    with pytest.raises(ValueError):
        handoff.build_handoff_context_v1(ctx)


def test_handoff_output_shape_is_complete():
    ctx = _make_adapter_context()
    result = handoff.build_handoff_context_v1(ctx)
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "upstream_adapter_status",
        "handoff_status",
        "formula_refs",
        "resolved_formula_ids",
        "required_variables",
        "resolved_variables",
        "required_evidence",
        "minimum_semantic_bindings",
        "owner_confirmation_required",
        "semantic_evidence_binding_allowed",
        "semantic_binding_blocking_reasons",
        "runtime_allowed",
        "phase_5_allowed",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_handoff_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_handoff_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_runtime_catalog_to_semantic_binding_handoff_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
