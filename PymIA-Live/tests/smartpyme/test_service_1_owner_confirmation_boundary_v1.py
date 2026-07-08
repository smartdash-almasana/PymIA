"""
SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_TESTS_V1

Test-only suite for the future owner confirmation boundary.

The boundary implementation does not exist yet. Per task rules, tests
import the future module via importorskip and build synthetic inputs.
When the boundary module is implemented, these tests become live without
modification.

Mode: TEST ONLY
"""
from __future__ import annotations

import pytest

# Boundary implementation not yet created: skip entire module until present.
boundary = pytest.importorskip(
    "pymia.smartpyme.service_1_owner_confirmation_boundary_v1"
)


REQUIRED_EVIDENCE = ("E001", "E002")
MINIMUM_BINDINGS = ("b1", "b2")


def _packet(
    *,
    confirmed_evidence: tuple[str, ...] = (),
    confirmed_bindings: tuple[str, ...] = (),
    conflict: bool = False,
) -> dict:
    return {
        "pathology_code": "PATH_001",
        "confirmed_evidence": confirmed_evidence,
        "confirmed_semantic_bindings": confirmed_bindings,
        "owner_id": "owner-1",
        "confirmation_timestamp": "2026-07-08T00:00:00Z",
        "notes": None,
        "conflict": conflict,
    }


def test_confirmation_all_required_evidence_and_bindings_confirmed():
    pkt = _packet(
        confirmed_evidence=REQUIRED_EVIDENCE,
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMED


def test_confirmation_requested_but_incomplete():
    pkt = _packet(
        confirmed_evidence=("E001",),
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMATION_REQUIRED


def test_confirmation_no_packet_available():
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=None,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMATION_PENDING


def test_confirmation_conflicting_evidence():
    pkt = _packet(conflict=True)
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMATION_CONFLICT


def test_confirmation_missing_required_evidence():
    pkt = _packet(
        confirmed_evidence=(),
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMATION_INSUFFICIENT


def test_confirmation_blocked_by_policy():
    pkt = _packet(
        confirmed_evidence=REQUIRED_EVIDENCE,
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    pkt["policy_violation"] = True
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.confirmation_status == boundary.OWNER_CONFIRMATION_BLOCKED_BY_POLICY


def test_confirmation_preserves_runtime_allowed_false():
    pkt = _packet(
        confirmed_evidence=REQUIRED_EVIDENCE,
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.runtime_allowed is False


def test_confirmation_preserves_phase_5_allowed_false():
    pkt = _packet(
        confirmed_evidence=REQUIRED_EVIDENCE,
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    assert result.phase_5_allowed is False


def test_confirmation_output_shape_is_complete():
    pkt = _packet(
        confirmed_evidence=REQUIRED_EVIDENCE,
        confirmed_bindings=MINIMUM_BINDINGS,
    )
    result = boundary.build_owner_confirmation_result_v1(
        pathology_code="PATH_001",
        required_evidence=REQUIRED_EVIDENCE,
        minimum_semantic_bindings=MINIMUM_BINDINGS,
        owner_confirmation_packet=pkt,
    )
    for field in (
        "schema_version",
        "service_name",
        "pathology_code",
        "confirmation_status",
        "confirmed_evidence",
        "missing_confirmed_evidence",
        "confirmed_semantic_bindings",
        "missing_semantic_bindings",
        "conflict_evidence",
        "runtime_allowed",
        "phase_5_allowed",
        "metadata",
    ):
        assert hasattr(result, field), f"missing field: {field}"


def test_confirmation_has_no_forbidden_imports():
    import importlib

    forbidden = {
        "service_1_xlsx_first_product_entrypoint_v1",
        "service_1_column_semantic_mapper_v1",
        "service_1_semantic_evidence_binding_engine_v1",
        "service_1_pathology_to_allowed_computation_candidate_v1",
        "pymia.cli",
    }
    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_owner_confirmation_boundary_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    for mod in forbidden:
        assert mod not in content, f"forbidden import present: {mod}"


def test_confirmation_has_no_case_001_dependency():
    import importlib

    source = importlib.util.find_spec(
        "pymia.smartpyme.service_1_owner_confirmation_boundary_v1"
    )
    assert source is not None
    path = source.origin
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert "CASE_001" not in content
