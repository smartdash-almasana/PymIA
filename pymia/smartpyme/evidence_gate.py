"""
Evidence Sufficiency Gate (SMARTPYME_EVIDENCE_SUFFICIENCY_GATE)

Pure, deterministic module that evaluates whether the evidence
records registered for an intake satisfy the IntakeEvidenceRequest
list embedded in the IntakeRecord.

This module does NOT:
- load from storage
- persist anything
- open files
- calculate hashes
- infer MIME
- inspect document content
- execute analysis
- dispatch microservices
- modify intake_state

It only compares metadata and produces an EvidenceSufficiencyResult
that downstream slices can use to decide state transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Assessment statuses
# ---------------------------------------------------------------------------

ASSESSMENT_SATISFIED = "SATISFIED"
ASSESSMENT_MISSING = "MISSING"
ASSESSMENT_PARTIAL = "PARTIAL"
ASSESSMENT_WAIVED = "WAIVED"
ASSESSMENT_BLOCKED = "BLOCKED"

ALLOWED_ASSESSMENT_STATUSES: tuple[str, ...] = (
    ASSESSMENT_SATISFIED,
    ASSESSMENT_MISSING,
    ASSESSMENT_PARTIAL,
    ASSESSMENT_WAIVED,
    ASSESSMENT_BLOCKED,
)

# ---------------------------------------------------------------------------
# Sufficiency statuses
# ---------------------------------------------------------------------------

SUFFICIENCY_READY = "READY"
SUFFICIENCY_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
SUFFICIENCY_BLOCKED = "BLOCKED"
SUFFICIENCY_UNSUPPORTED = "UNSUPPORTED"

ALLOWED_SUFFICIENCY_STATUSES: tuple[str, ...] = (
    SUFFICIENCY_READY,
    SUFFICIENCY_NEEDS_MORE_EVIDENCE,
    SUFFICIENCY_BLOCKED,
    SUFFICIENCY_UNSUPPORTED,
)

# ---------------------------------------------------------------------------
# Suggested next states
# ---------------------------------------------------------------------------

SUGGESTED_READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
SUGGESTED_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
SUGGESTED_BLOCKED = "BLOCKED"
SUGGESTED_UNSUPPORTED = "UNSUPPORTED"

# ---------------------------------------------------------------------------
# Acceptable / rejected evidence statuses
# ---------------------------------------------------------------------------

_ACCEPTABLE_EVIDENCE_STATUSES: tuple[str, ...] = (
    "RECEIVED",
    "REGISTERED",
    "LINKED",
)

_REJECTED_EVIDENCE_STATUSES: tuple[str, ...] = (
    "REJECTED",
    "SUPERSEDED",
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class EvidenceRequestAssessment:
    """Assessment of a single IntakeEvidenceRequest against available evidence."""

    request_id: str
    evidence_type: str
    source_tank: str | None
    required: bool
    blocking: bool
    matched_evidence_ids: list[str]
    status: str
    reason: str
    missing_fields: list[str]
    notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvidenceSufficiencyResult:
    """Aggregate result of evidence sufficiency evaluation for an intake."""

    tenant_id: str
    intake_id: str
    status: str
    suggested_next_state: str
    assessments: list[EvidenceRequestAssessment] = field(default_factory=list)
    matched_evidence_ids: list[str] = field(default_factory=list)
    missing_request_ids: list[str] = field(default_factory=list)
    blocking_request_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    audit_notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "intake_id": self.intake_id,
            "status": self.status,
            "suggested_next_state": self.suggested_next_state,
            "assessments": [a.to_dict() for a in self.assessments],
            "matched_evidence_ids": list(self.matched_evidence_ids),
            "missing_request_ids": list(self.missing_request_ids),
            "blocking_request_ids": list(self.blocking_request_ids),
            "warnings": list(self.warnings),
            "audit_notes": list(self.audit_notes),
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_dict(obj: Any, *, label: str) -> dict:
    """Convert IntakeRecord/EvidenceRecord/dict to dict without mutating."""
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        result = obj.to_dict()
        if not isinstance(result, dict):
            raise ValueError(f"{label}.to_dict() did not return a dict")
        return dict(result)
    raise ValueError(f"{label} must be a dict or have to_dict() method")


def _require_field(data: dict, key: str, *, label: str) -> None:
    if key not in data:
        raise ValueError(f"{label} is missing required field: {key}")


def _extract_request_id(req: dict) -> str:
    """Return a stable identifier for a request, falling back to evidence_type."""
    rid = req.get("request_id")
    if rid:
        return str(rid)
    et = req.get("evidence_type")
    if et:
        return f"auto:{et}"
    raise ValueError("IntakeEvidenceRequest must have request_id or evidence_type")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_evidence_sufficiency(
    intake_record: Any,
    evidence_records: list,
) -> EvidenceSufficiencyResult:
    """
    Evaluate whether evidence_records satisfy the IntakeEvidenceRequests
    declared in intake_record.

    Parameters
    ----------
    intake_record : IntakeRecord or dict
        Must contain tenant_id, intake_id, evidence_requests.
    evidence_records : list
        List of EvidenceRecord instances or dicts.

    Returns
    -------
    EvidenceSufficiencyResult
        Pure, JSON-serializable result. Does NOT mutate inputs.

    Raises
    ------
    ValueError
        If inputs violate the contract.
    """
    # --- Input validation ------------------------------------------------
    if not isinstance(evidence_records, list):
        raise ValueError("evidence_records must be a list")

    intake = _as_dict(intake_record, label="intake_record")
    _require_field(intake, "tenant_id", label="intake_record")
    _require_field(intake, "intake_id", label="intake_record")
    _require_field(intake, "evidence_requests", label="intake_record")

    tenant_id = str(intake["tenant_id"])
    intake_id = str(intake["intake_id"])
    requests = intake["evidence_requests"]

    if not isinstance(requests, list):
        raise ValueError("intake_record.evidence_requests must be a list")

    # Validate each evidence record
    ev_dicts: list[dict] = []
    for idx, ev in enumerate(evidence_records):
        d = _as_dict(ev, label=f"evidence_records[{idx}]")
        _require_field(d, "tenant_id", label=f"evidence_records[{idx}]")
        _require_field(d, "intake_id", label=f"evidence_records[{idx}]")
        _require_field(d, "evidence_id", label=f"evidence_records[{idx}]")
        _require_field(d, "evidence_type", label=f"evidence_records[{idx}]")
        _require_field(d, "status", label=f"evidence_records[{idx}]")
        ev_dicts.append(d)

    # --- Early exit: blocked intake --------------------------------------
    intake_state = intake.get("intake_state")
    if intake_state == "BLOCKED":
        return EvidenceSufficiencyResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=SUFFICIENCY_BLOCKED,
            suggested_next_state=SUGGESTED_BLOCKED,
            assessments=[],
            matched_evidence_ids=[],
            missing_request_ids=[],
            blocking_request_ids=[],
            warnings=[],
            audit_notes=["Intake state is BLOCKED; sufficiency gate short-circuited."],
        )

    # --- Early exit: no requests -----------------------------------------
    if not requests:
        return EvidenceSufficiencyResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=SUFFICIENCY_READY,
            suggested_next_state=SUGGESTED_READY_FOR_ANALYSIS,
            assessments=[],
            matched_evidence_ids=[],
            missing_request_ids=[],
            blocking_request_ids=[],
            warnings=["No evidence requests were present."],
            audit_notes=[],
        )

    # --- Per-request assessment ------------------------------------------
    assessments: list[EvidenceRequestAssessment] = []
    all_matched: list[str] = []
    missing_ids: list[str] = []
    blocking_ids: list[str] = []
    any_blocking_missing = False
    any_blocking_partial = False

    for req in requests:
        if not isinstance(req, dict):
            raise ValueError("Each evidence_request in intake must be a dict")

        req_id = _extract_request_id(req)
        evidence_type = req.get("evidence_type") or ""
        source_tank = req.get("source_tank")
        blocking = bool(req.get("blocks_analysis", False))
        required = bool(req.get("required", blocking))
        required_fields = req.get("required_fields") or []
        if not isinstance(required_fields, list):
            required_fields = []

        if blocking and req_id not in blocking_ids:
            blocking_ids.append(req_id)

        # Find matching evidence
        matched_ids: list[str] = []
        matched_evs: list[dict] = []

        for ev in ev_dicts:
            if str(ev["tenant_id"]) != tenant_id:
                continue
            if str(ev["intake_id"]) != intake_id:
                continue
            if ev["status"] not in _ACCEPTABLE_EVIDENCE_STATUSES:
                continue

            # Strong match: request_id on both sides
            ev_req_id = ev.get("request_id")
            if req.get("request_id") and ev_req_id and str(req["request_id"]) == str(ev_req_id):
                matched_ids.append(str(ev["evidence_id"]))
                matched_evs.append(ev)
                continue

            # Fallback: evidence_type match
            if evidence_type and str(ev.get("evidence_type", "")) == str(evidence_type):
                matched_ids.append(str(ev["evidence_id"]))
                matched_evs.append(ev)

        # Deduplicate matched ids
        seen: set[str] = set()
        dedup_ids: list[str] = []
        for mid in matched_ids:
            if mid not in seen:
                seen.add(mid)
                dedup_ids.append(mid)
        matched_ids = dedup_ids

        # Determine status
        if not matched_ids:
            status = ASSESSMENT_MISSING
            reason = "No acceptable evidence matched this request."
            missing_f: list[str] = []
            notes: list[str] = []
            if blocking:
                any_blocking_missing = True
        else:
            # Check required fields against evidence metadata
            missing_f = []
            if required_fields:
                for ev in matched_evs:
                    meta = ev.get("metadata") or {}
                    if not isinstance(meta, dict):
                        meta = {}
                    for rf in required_fields:
                        if rf not in meta and rf not in missing_f:
                            missing_f.append(rf)

            if missing_f:
                status = ASSESSMENT_PARTIAL
                reason = f"Evidence matched but missing required fields: {missing_f}"
                notes = [f"Missing fields in metadata: {missing_f}"]
                if blocking:
                    any_blocking_partial = True
            else:
                status = ASSESSMENT_SATISFIED
                reason = "Evidence matched and required fields present."
                notes = []
                all_matched.extend(matched_ids)

        if status in (ASSESSMENT_MISSING, ASSESSMENT_PARTIAL):
            if req_id not in missing_ids:
                missing_ids.append(req_id)

        assessments.append(EvidenceRequestAssessment(
            request_id=req_id,
            evidence_type=evidence_type,
            source_tank=source_tank,
            required=required,
            blocking=blocking,
            matched_evidence_ids=matched_ids,
            status=status,
            reason=reason,
            missing_fields=missing_f,
            notes=notes,
        ))

    # --- Aggregate result ------------------------------------------------
    # Deduplicate matched ids at result level
    seen_all: set[str] = set()
    dedup_all: list[str] = []
    for mid in all_matched:
        if mid not in seen_all:
            seen_all.add(mid)
            dedup_all.append(mid)
    all_matched = dedup_all

    if any_blocking_missing or any_blocking_partial:
        final_status = SUFFICIENCY_NEEDS_MORE_EVIDENCE
        suggested = SUGGESTED_NEEDS_EVIDENCE
    else:
        final_status = SUFFICIENCY_READY
        suggested = SUGGESTED_READY_FOR_ANALYSIS

    return EvidenceSufficiencyResult(
        tenant_id=tenant_id,
        intake_id=intake_id,
        status=final_status,
        suggested_next_state=suggested,
        assessments=assessments,
        matched_evidence_ids=all_matched,
        missing_request_ids=missing_ids,
        blocking_request_ids=blocking_ids,
        warnings=[],
        audit_notes=[
            f"Evaluated {len(requests)} requests against {len(ev_dicts)} evidence records."
        ],
    )


__all__ = [
    "ASSESSMENT_SATISFIED",
    "ASSESSMENT_MISSING",
    "ASSESSMENT_PARTIAL",
    "ASSESSMENT_WAIVED",
    "ASSESSMENT_BLOCKED",
    "ALLOWED_ASSESSMENT_STATUSES",
    "SUFFICIENCY_READY",
    "SUFFICIENCY_NEEDS_MORE_EVIDENCE",
    "SUFFICIENCY_BLOCKED",
    "SUFFICIENCY_UNSUPPORTED",
    "ALLOWED_SUFFICIENCY_STATUSES",
    "SUGGESTED_READY_FOR_ANALYSIS",
    "SUGGESTED_NEEDS_EVIDENCE",
    "SUGGESTED_BLOCKED",
    "SUGGESTED_UNSUPPORTED",
    "EvidenceRequestAssessment",
    "EvidenceSufficiencyResult",
    "evaluate_evidence_sufficiency",
]
