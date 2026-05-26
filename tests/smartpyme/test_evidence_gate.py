"""
Tests for SMARTPYME_EVIDENCE_SUFFICIENCY_GATE.

Covers:
- Pure deterministic matching
- Fail-closed validation
- Blocking logic
- Partial / required fields
- Integration with IntakeRecord and EvidenceRecord dataclasses
"""

from __future__ import annotations

import json
import copy

import pytest

from pymia.smartpyme.evidence_gate import (
    ASSESSMENT_BLOCKED,
    ASSESSMENT_MISSING,
    ASSESSMENT_PARTIAL,
    ASSESSMENT_SATISFIED,
    ALLOWED_ASSESSMENT_STATUSES,
    ALLOWED_SUFFICIENCY_STATUSES,
    SUFFICIENCY_BLOCKED,
    SUFFICIENCY_NEEDS_MORE_EVIDENCE,
    SUFFICIENCY_READY,
    SUFFICIENCY_UNSUPPORTED,
    SUGGESTED_BLOCKED,
    SUGGESTED_NEEDS_EVIDENCE,
    SUGGESTED_READY_FOR_ANALYSIS,
    SUGGESTED_UNSUPPORTED,
    EvidenceRequestAssessment,
    EvidenceSufficiencyResult,
    evaluate_evidence_sufficiency,
)
from pymia.smartpyme.intake import create_intake_record
from pymia.smartpyme.evidence import create_evidence_record


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_intake(
    *,
    tenant_id: str = "t1",
    intake_id: str = "intake_1",
    evidence_requests: list | None = None,
    intake_state: str = "NEEDS_EVIDENCE",
) -> dict:
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "raw_input": "test",
        "structured_selectors": {},
        "interrogation_result": {},
        "tank_selection_result": {},
        "evidence_requests": evidence_requests if evidence_requests is not None else [],
        "intake_state": intake_state,
        "suggested_next_state": "NEEDS_EVIDENCE",
        "warnings": [],
        "audit_notes": [],
        "created_at": "2026-05-26T00:00:00+00:00",
    }


def _make_evidence(
    *,
    tenant_id: str = "t1",
    intake_id: str = "intake_1",
    evidence_id: str = "ev_1",
    evidence_type: str = "excel_proveedores",
    request_id: str | None = None,
    status: str = "RECEIVED",
    metadata: dict | None = None,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "evidence_id": evidence_id,
        "request_id": request_id,
        "evidence_type": evidence_type,
        "source_kind": "uploaded_file",
        "source_ref": "file.xlsx",
        "original_filename": "file.xlsx",
        "mime_type": "application/vnd.ms-excel",
        "size_bytes": 1024,
        "content_hash": None,
        "status": status,
        "received_at": "2026-05-26T00:00:00+00:00",
        "notes": [],
        "metadata": metadata if metadata is not None else {},
    }


def _req(
    *,
    request_id: str = "req_1",
    evidence_type: str = "excel_proveedores",
    blocks_analysis: bool = True,
    required_fields: list[str] | None = None,
) -> dict:
    return {
        "request_id": request_id,
        "evidence_type": evidence_type,
        "blocks_analysis": blocks_analysis,
        "required_fields": required_fields or [],
        "source_tank": None,
    }


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

class TestImportSmoke:
    def test_import_smoke(self):
        from pymia.smartpyme.evidence_gate import (
            evaluate_evidence_sufficiency,
            EvidenceSufficiencyResult,
        )
        assert callable(evaluate_evidence_sufficiency)
        assert EvidenceSufficiencyResult is not None


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------

class TestCoreMatching:
    def test_no_evidence_requests_returns_ready(self):
        intake = _make_intake(evidence_requests=[])
        result = evaluate_evidence_sufficiency(intake, [])
        assert result.status == SUFFICIENCY_READY
        assert result.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
        assert any("No evidence" in w for w in result.warnings)

    def test_blocking_request_missing_returns_needs_more_evidence(self):
        intake = _make_intake(evidence_requests=[_req(request_id="r1")])
        result = evaluate_evidence_sufficiency(intake, [])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert result.suggested_next_state == SUGGESTED_NEEDS_EVIDENCE
        assert "r1" in result.missing_request_ids

    def test_matching_evidence_by_request_id_satisfies_request(self):
        intake = _make_intake(
            evidence_requests=[_req(request_id="r1", evidence_type="excel_proveedores")]
        )
        ev = _make_evidence(request_id="r1", evidence_type="excel_proveedores")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_READY
        assert result.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
        assert result.assessments[0].status == ASSESSMENT_SATISFIED
        assert "ev_1" in result.matched_evidence_ids

    def test_matching_evidence_by_evidence_type_fallback_satisfies_request(self):
        intake = _make_intake(
            evidence_requests=[_req(request_id="r1", evidence_type="excel_proveedores")]
        )
        # Evidence has no request_id, only evidence_type
        ev = _make_evidence(
            request_id=None,
            evidence_type="excel_proveedores",
        )
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_READY
        assert result.assessments[0].status == ASSESSMENT_SATISFIED

    def test_wrong_tenant_evidence_does_not_match(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(tenant_id="OTHER_TENANT")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert result.assessments[0].status == ASSESSMENT_MISSING

    def test_wrong_intake_evidence_does_not_match(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(intake_id="OTHER_INTAKE")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert result.assessments[0].status == ASSESSMENT_MISSING

    def test_rejected_evidence_does_not_match(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(status="REJECTED")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert result.assessments[0].status == ASSESSMENT_MISSING

    def test_superseded_evidence_does_not_match(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(status="SUPERSEDED")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert result.assessments[0].status == ASSESSMENT_MISSING

    def test_received_evidence_matches(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(status="RECEIVED")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_SATISFIED

    def test_registered_evidence_matches(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(status="REGISTERED")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_SATISFIED

    def test_linked_evidence_matches(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence(status="LINKED")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_SATISFIED


# ---------------------------------------------------------------------------
# Required fields / partial
# ---------------------------------------------------------------------------

class TestRequiredFields:
    def test_required_fields_missing_returns_partial(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r1", required_fields=["period", "amount"])
            ]
        )
        ev = _make_evidence(
            request_id="r1",
            metadata={"period": "2026-01"},
        )
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_PARTIAL
        assert "amount" in result.assessments[0].missing_fields
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE

    def test_required_fields_present_returns_satisfied(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r1", required_fields=["period", "amount"])
            ]
        )
        ev = _make_evidence(
            request_id="r1",
            metadata={"period": "2026-01", "amount": 1000},
        )
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_SATISFIED
        assert result.assessments[0].missing_fields == []

    def test_non_blocking_missing_request_does_not_block_ready(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r1", blocks_analysis=False),
            ]
        )
        result = evaluate_evidence_sufficiency(intake, [])
        # Non-blocking missing: result is READY (blocking logic only)
        assert result.status == SUFFICIENCY_READY
        assert result.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
        # But assessment is still MISSING
        assert result.assessments[0].status == ASSESSMENT_MISSING


# ---------------------------------------------------------------------------
# Blocked intake
# ---------------------------------------------------------------------------

class TestBlockedIntake:
    def test_blocked_intake_returns_blocked(self):
        intake = _make_intake(
            intake_state="BLOCKED",
            evidence_requests=[_req()],
        )
        result = evaluate_evidence_sufficiency(intake, [])
        assert result.status == SUFFICIENCY_BLOCKED
        assert result.suggested_next_state == SUGGESTED_BLOCKED


# ---------------------------------------------------------------------------
# Multiple requests / aggregation
# ---------------------------------------------------------------------------

class TestMultipleRequests:
    def test_multiple_requests_one_missing_blocking_returns_needs_more_evidence(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r1"),
                _req(request_id="r2"),
            ]
        )
        ev = _make_evidence(request_id="r1")
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.status == SUFFICIENCY_NEEDS_MORE_EVIDENCE
        assert "r2" in result.missing_request_ids
        assert "r1" not in result.missing_request_ids

    def test_all_blocking_requests_satisfied_returns_ready(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r1"),
                _req(request_id="r2"),
            ]
        )
        ev1 = _make_evidence(request_id="r1", evidence_id="ev_1")
        ev2 = _make_evidence(request_id="r2", evidence_id="ev_2")
        result = evaluate_evidence_sufficiency(intake, [ev1, ev2])
        assert result.status == SUFFICIENCY_READY
        assert result.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_result_to_dict_json_serializable(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence()
        result = evaluate_evidence_sufficiency(intake, [ev])
        d = result.to_dict()
        s = json.dumps(d)
        assert isinstance(s, str)
        back = json.loads(s)
        assert back["tenant_id"] == "t1"
        assert back["status"] in ALLOWED_SUFFICIENCY_STATUSES

    def test_assessment_to_dict_json_serializable(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence()
        result = evaluate_evidence_sufficiency(intake, [ev])
        a = result.assessments[0]
        d = a.to_dict()
        s = json.dumps(d)
        assert isinstance(s, str)
        back = json.loads(s)
        assert back["status"] in ALLOWED_ASSESSMENT_STATUSES


# ---------------------------------------------------------------------------
# Accepts IntakeRecord / EvidenceRecord instances
# ---------------------------------------------------------------------------

class TestInstanceInputs:
    def test_accepts_intake_record_instance(self):
        # create_intake_record produces a real IntakeRecord with to_dict()
        ir = create_intake_record(
            tenant_id="t_inst",
            raw_text="tengo proveedores duplicados y cuit mezclados",
        )
        # Mutate evidence_requests for this test (instance is already created)
        # We need to build a new intake with our requests
        d = ir.to_dict()
        d["evidence_requests"] = [_req(request_id="r1", evidence_type="excel_proveedores")]
        ev = _make_evidence(
            tenant_id="t_inst",
            intake_id=d["intake_id"],
            request_id="r1",
            evidence_type="excel_proveedores",
        )
        result = evaluate_evidence_sufficiency(d, [ev])
        assert result.status in ALLOWED_SUFFICIENCY_STATUSES
        assert result.tenant_id == "t_inst"

    def test_accepts_evidence_record_instance(self):
        intake = _make_intake(
            evidence_requests=[_req(request_id="r1", evidence_type="excel_proveedores")]
        )
        ev = create_evidence_record(
            tenant_id="t1",
            intake_id="intake_1",
            evidence_type="excel_proveedores",
            source_kind="uploaded_file",
            source_ref="file.xlsx",
            request_id="r1",
        )
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert result.assessments[0].status == ASSESSMENT_SATISFIED

    def test_plain_dict_inputs_supported(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence()
        result = evaluate_evidence_sufficiency(intake, [ev])
        assert isinstance(result, EvidenceSufficiencyResult)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_invalid_intake_raises(self):
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency("not a dict", [])

    def test_intake_missing_tenant_id_raises(self):
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency({"intake_id": "x", "evidence_requests": []}, [])

    def test_intake_missing_intake_id_raises(self):
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency({"tenant_id": "x", "evidence_requests": []}, [])

    def test_intake_missing_evidence_requests_raises(self):
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency({"tenant_id": "x", "intake_id": "y"}, [])

    def test_evidence_records_must_be_list(self):
        intake = _make_intake()
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency(intake, "not a list")

    def test_invalid_evidence_raises(self):
        intake = _make_intake()
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency(intake, ["not a dict"])

    def test_evidence_missing_tenant_id_raises(self):
        intake = _make_intake()
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency(intake, [{"intake_id": "x", "evidence_id": "e",
                                                    "evidence_type": "t", "status": "RECEIVED"}])

    def test_evidence_missing_status_raises(self):
        intake = _make_intake()
        with pytest.raises(ValueError):
            evaluate_evidence_sufficiency(intake, [{
                "tenant_id": "t1", "intake_id": "x", "evidence_id": "e",
                "evidence_type": "t",
            }])


# ---------------------------------------------------------------------------
# Non-mutation
# ---------------------------------------------------------------------------

class TestNonMutation:
    def test_inputs_not_mutated(self):
        intake = _make_intake(evidence_requests=[_req()])
        ev = _make_evidence()
        intake_copy = copy.deepcopy(intake)
        ev_copy = copy.deepcopy(ev)
        evaluate_evidence_sufficiency(intake, [ev])
        assert intake == intake_copy
        assert ev == ev_copy


# ---------------------------------------------------------------------------
# Deduplication / ordering
# ---------------------------------------------------------------------------

class TestDedupAndOrder:
    def test_matched_evidence_ids_are_deduplicated(self):
        intake = _make_intake(
            evidence_requests=[_req(request_id="r1", evidence_type="excel_proveedores")]
        )
        # Two evidence records matching the same request (both by type fallback)
        ev1 = _make_evidence(evidence_id="ev_1", evidence_type="excel_proveedores")
        ev2 = _make_evidence(evidence_id="ev_2", evidence_type="excel_proveedores")
        result = evaluate_evidence_sufficiency(intake, [ev1, ev2])
        # Should have both ids, no duplicates
        ids = result.matched_evidence_ids
        assert len(ids) == len(set(ids))
        assert set(ids) == {"ev_1", "ev_2"}

    def test_missing_request_ids_preserve_order(self):
        intake = _make_intake(
            evidence_requests=[
                _req(request_id="r_a"),
                _req(request_id="r_b"),
                _req(request_id="r_c"),
            ]
        )
        result = evaluate_evidence_sufficiency(intake, [])
        assert result.missing_request_ids == ["r_a", "r_b", "r_c"]


# ---------------------------------------------------------------------------
# Constants coverage
# ---------------------------------------------------------------------------

class TestConstants:
    def test_allowed_statuses_are_tuples(self):
        assert isinstance(ALLOWED_ASSESSMENT_STATUSES, tuple)
        assert isinstance(ALLOWED_SUFFICIENCY_STATUSES, tuple)
        assert ASSESSMENT_SATISFIED in ALLOWED_ASSESSMENT_STATUSES
        assert SUFFICIENCY_READY in ALLOWED_SUFFICIENCY_STATUSES

    def test_suggested_constants_exist(self):
        assert SUGGESTED_READY_FOR_ANALYSIS == "READY_FOR_ANALYSIS"
        assert SUGGESTED_NEEDS_EVIDENCE == "NEEDS_EVIDENCE"
        assert SUGGESTED_BLOCKED == "BLOCKED"
        assert SUGGESTED_UNSUPPORTED == "UNSUPPORTED"
