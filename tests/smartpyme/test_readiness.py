"""
Tests for SMARTPYME_READY_FOR_ANALYSIS_GATE.

Validates the pure, deterministic AnalysisReadinessResult gate.

Coverage:
- import smoke
- runtime classification resolution (excel_diagnostic, supplier_duplicate_check)
- sufficiency status propagation (READY, NEEDS_MORE_EVIDENCE, BLOCKED, UNSUPPORTED)
- intake_state BLOCKED short-circuit
- ambiguity handling (both classifications enabled)
- input validation (dict/dataclass, tenant/intake mismatch, unknown status)
- no mutation of inputs
- JSON-serializable output
- no import of runtime modules (excel_diagnostic/supplier_duplicate_check)
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

def test_import_smoke():
    from pymia.smartpyme.readiness import (  # noqa: F401
        evaluate_analysis_readiness,
        AnalysisReadinessResult,
        READINESS_READY_FOR_ANALYSIS,
        READINESS_NEEDS_EVIDENCE,
        READINESS_BLOCKED,
        READINESS_UNSUPPORTED,
        ALLOWED_READINESS_STATUSES,
        RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC,
        RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
        ALLOWED_RUNTIME_CLASSIFICATIONS,
    )


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_intake(
    *,
    tenant_id: str = "t1",
    intake_id: str = "intake_001",
    intake_state: str = "NEEDS_EVIDENCE",
    evidence_requests: list | None = None,
    tank_selection_result: dict | None = None,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "raw_input": "algún relato",
        "structured_selectors": {},
        "interrogation_result": {},
        "tank_selection_result": tank_selection_result or {},
        "evidence_requests": evidence_requests if evidence_requests is not None else [],
        "intake_state": intake_state,
        "suggested_next_state": "NEEDS_EVIDENCE",
        "warnings": [],
        "audit_notes": [],
        "created_at": "2026-05-25T00:00:00+00:00",
    }


def _make_sufficiency(
    *,
    tenant_id: str = "t1",
    intake_id: str = "intake_001",
    status: str = "READY",
    missing_request_ids: list | None = None,
    matched_evidence_ids: list | None = None,
    warnings: list | None = None,
    audit_notes: list | None = None,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "status": status,
        "suggested_next_state": "READY_FOR_ANALYSIS" if status == "READY" else status,
        "assessments": [],
        "matched_evidence_ids": matched_evidence_ids or [],
        "missing_request_ids": missing_request_ids or [],
        "blocking_request_ids": [],
        "warnings": warnings or [],
        "audit_notes": audit_notes or [],
        "created_at": "2026-05-25T00:00:00+00:00",
    }


def _excel_request(req_id: str = "req_excel_1") -> dict:
    return {
        "request_id": req_id,
        "evidence_type": "excel_ventas_costos",
        "description": "Excel de ventas y costos",
        "required_fields": ["producto", "precio", "costo"],
        "reason": "Evaluar margen",
        "blocks_analysis": True,
        "enables_classification": "excel_diagnostic",
        "source_tank": "SMARTPYME_EVIDENCE_AND_FORMULA_TANK",
        "status": "REQUESTED",
    }


def _supplier_request(req_id: str = "req_supplier_1") -> dict:
    return {
        "request_id": req_id,
        "evidence_type": "excel_proveedores",
        "description": "Excel de proveedores",
        "required_fields": ["proveedor", "cuit", "razon_social"],
        "reason": "Detectar duplicados",
        "blocks_analysis": True,
        "enables_classification": "supplier_duplicate_check",
        "source_tank": "SMARTPYME_OPERATIONAL_PATHOLOGY_TANK",
        "status": "REQUESTED",
    }


# ---------------------------------------------------------------------------
# Rule 1: blocked intake
# ---------------------------------------------------------------------------

class TestBlockedIntake:
    def test_blocked_intake_returns_blocked(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_BLOCKED,
            SUGGESTED_BLOCKED,
        )
        intake = _make_intake(intake_state="BLOCKED")
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_BLOCKED
        assert r.suggested_next_state == SUGGESTED_BLOCKED
        assert r.can_execute is False
        assert "Intake is blocked." in r.blocking_reasons


# ---------------------------------------------------------------------------
# Rule 2: blocked sufficiency
# ---------------------------------------------------------------------------

class TestBlockedSufficiency:
    def test_blocked_sufficiency_returns_blocked(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_BLOCKED,
        )
        intake = _make_intake(intake_state="NEEDS_EVIDENCE")
        suff = _make_sufficiency(status="BLOCKED")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_BLOCKED
        assert r.can_execute is False


# ---------------------------------------------------------------------------
# Rule 3: needs more evidence
# ---------------------------------------------------------------------------

class TestNeedsMoreEvidence:
    def test_needs_more_evidence_returns_needs_evidence(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_NEEDS_EVIDENCE,
            SUGGESTED_NEEDS_EVIDENCE,
        )
        intake = _make_intake(
            evidence_requests=[_excel_request()],
        )
        suff = _make_sufficiency(
            status="NEEDS_MORE_EVIDENCE",
            missing_request_ids=["req_excel_1"],
        )
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_NEEDS_EVIDENCE
        assert r.suggested_next_state == SUGGESTED_NEEDS_EVIDENCE
        assert r.can_execute is False
        assert r.missing_request_ids == ["req_excel_1"]


# ---------------------------------------------------------------------------
# Rule 4: unsupported sufficiency
# ---------------------------------------------------------------------------

class TestUnsupportedSufficiency:
    def test_unsupported_sufficiency_returns_unsupported(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_UNSUPPORTED,
        )
        intake = _make_intake()
        suff = _make_sufficiency(status="UNSUPPORTED")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_UNSUPPORTED
        assert r.can_execute is False


# ---------------------------------------------------------------------------
# Rule 5/6: READY sufficiency + runtime classification
# ---------------------------------------------------------------------------

class TestReadyWithRuntime:
    def test_ready_sufficiency_with_excel_runtime_returns_ready(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_READY_FOR_ANALYSIS,
            SUGGESTED_READY_FOR_ANALYSIS,
            RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC,
        )
        intake = _make_intake(evidence_requests=[_excel_request()])
        suff = _make_sufficiency(status="READY", matched_evidence_ids=["ev_1"])
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_READY_FOR_ANALYSIS
        assert r.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
        assert r.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC
        assert r.can_execute is True

    def test_ready_sufficiency_with_supplier_runtime_returns_ready(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_READY_FOR_ANALYSIS,
            RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
        )
        intake = _make_intake(evidence_requests=[_supplier_request()])
        suff = _make_sufficiency(status="READY", matched_evidence_ids=["ev_2"])
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_READY_FOR_ANALYSIS
        assert r.runtime_classification == RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
        assert r.can_execute is True

    def test_ready_without_supported_runtime_returns_unsupported(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_UNSUPPORTED,
        )
        # Request without enables_classification
        req = {
            "request_id": "req_x",
            "evidence_type": "algo",
            "blocks_analysis": True,
            "enables_classification": None,
        }
        intake = _make_intake(evidence_requests=[req])
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_UNSUPPORTED
        assert r.can_execute is False
        assert any("No supported runtime classification" in br for br in r.blocking_reasons)

    def test_runtime_classification_from_evidence_request(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(evidence_requests=[_supplier_request()])
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.runtime_classification == "supplier_duplicate_check"


class TestAmbiguousRuntime:
    def test_ambiguous_runtime_returns_unsupported_with_warning(self):
        from pymia.smartpyme.readiness import (
            evaluate_analysis_readiness,
            READINESS_UNSUPPORTED,
        )
        intake = _make_intake(
            evidence_requests=[_excel_request(), _supplier_request()]
        )
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == READINESS_UNSUPPORTED
        assert r.can_execute is False
        assert any("Ambiguous" in w for w in r.warnings)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_tenant_mismatch_raises(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(tenant_id="t1")
        suff = _make_sufficiency(tenant_id="t2")
        with pytest.raises(ValueError, match="tenant_id mismatch"):
            evaluate_analysis_readiness(intake, suff)

    def test_intake_id_mismatch_raises(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(intake_id="i1")
        suff = _make_sufficiency(intake_id="i2")
        with pytest.raises(ValueError, match="intake_id mismatch"):
            evaluate_analysis_readiness(intake, suff)

    def test_invalid_intake_raises(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        suff = _make_sufficiency()
        with pytest.raises(ValueError):
            evaluate_analysis_readiness("not a dict", suff)

    def test_invalid_sufficiency_raises(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake()
        with pytest.raises(ValueError):
            evaluate_analysis_readiness(intake, 42)

    def test_unknown_sufficiency_status_raises(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake()
        suff = _make_sufficiency(status="MAGICAL_STATE")
        with pytest.raises(ValueError, match="not recognized"):
            evaluate_analysis_readiness(intake, suff)

    def test_evidence_requests_must_be_list(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake()
        intake["evidence_requests"] = "not a list"
        suff = _make_sufficiency(status="READY")
        with pytest.raises(ValueError, match="evidence_requests must be a list"):
            evaluate_analysis_readiness(intake, suff)


# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------

class TestInputHandling:
    def test_accepts_dict_inputs(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(evidence_requests=[_excel_request()])
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == "READY_FOR_ANALYSIS"

    def test_accepts_dataclass_like_inputs_with_to_dict(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness

        class _FakeIntake:
            def to_dict(self):
                return _make_intake(evidence_requests=[_excel_request()])

        class _FakeSufficiency:
            def to_dict(self):
                return _make_sufficiency(status="READY")

        r = evaluate_analysis_readiness(_FakeIntake(), _FakeSufficiency())
        assert r.status == "READY_FOR_ANALYSIS"

    def test_inputs_not_mutated(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(
            evidence_requests=[_excel_request()],
        )
        suff = _make_sufficiency(
            status="READY",
            matched_evidence_ids=["ev_1"],
            missing_request_ids=[],
        )
        intake_copy = json.loads(json.dumps(intake))
        suff_copy = json.loads(json.dumps(suff))

        evaluate_analysis_readiness(intake, suff)

        assert intake == intake_copy
        assert suff == suff_copy


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------

class TestOutputContract:
    def test_to_dict_json_serializable(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(evidence_requests=[_excel_request()])
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        d = r.to_dict()
        s = json.dumps(d, sort_keys=True)
        assert isinstance(s, str)
        assert "READY_FOR_ANALYSIS" in s

    def test_missing_request_ids_preserved(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(evidence_requests=[_excel_request()])
        suff = _make_sufficiency(
            status="NEEDS_MORE_EVIDENCE",
            missing_request_ids=["req_excel_1", "req_x"],
        )
        r = evaluate_analysis_readiness(intake, suff)
        assert r.missing_request_ids == ["req_excel_1", "req_x"]

    def test_matched_evidence_ids_preserved(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake(evidence_requests=[_excel_request()])
        suff = _make_sufficiency(
            status="READY",
            matched_evidence_ids=["ev_1", "ev_2"],
        )
        r = evaluate_analysis_readiness(intake, suff)
        assert r.matched_evidence_ids == ["ev_1", "ev_2"]

    def test_warnings_are_lists(self):
        from pymia.smartpyme.readiness import evaluate_analysis_readiness
        intake = _make_intake()
        suff = _make_sufficiency(status="READY")
        r = evaluate_analysis_readiness(intake, suff)
        assert isinstance(r.warnings, list)
        assert isinstance(r.blocking_reasons, list)
        assert isinstance(r.audit_notes, list)


# ---------------------------------------------------------------------------
# Runtime isolation
# ---------------------------------------------------------------------------

class TestRuntimeIsolation:
    def test_does_not_import_runtime_modules(self):
        """readiness.py must not import excel_diagnostic or supplier_duplicate_check."""
        here = Path(__file__).resolve()
        readiness_path = here.parent.parent / "pymia" / "smartpyme" / "readiness.py"
        src = readiness_path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "excel_diagnostic" not in alias.name
                    assert "supplier_duplicate_check" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "excel_diagnostic" not in node.module
                    assert "supplier_duplicate_check" not in node.module


# ---------------------------------------------------------------------------
# Integration with real dataclasses (optional)
# ---------------------------------------------------------------------------

class TestWithDataclasses:
    def test_accepts_evidence_sufficiency_result_dataclass(self):
        """Integration: use real EvidenceSufficiencyResult dataclass."""
        from pymia.smartpyme.evidence_gate import EvidenceSufficiencyResult
        from pymia.smartpyme.readiness import evaluate_analysis_readiness

        suff = EvidenceSufficiencyResult(
            tenant_id="t1",
            intake_id="intake_001",
            status="READY",
            suggested_next_state="READY_FOR_ANALYSIS",
            matched_evidence_ids=["ev_1"],
        )
        intake = _make_intake(evidence_requests=[_excel_request()])
        r = evaluate_analysis_readiness(intake, suff)
        assert r.status == "READY_FOR_ANALYSIS"
        assert r.runtime_classification == "excel_diagnostic"
