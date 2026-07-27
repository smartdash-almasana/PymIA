"""
Analysis Readiness Gate (SMARTPYME_READY_FOR_ANALYSIS_GATE)

Pure, deterministic module that converts:
    IntakeRecord (or dict)
  + EvidenceSufficiencyResult (or dict)
  -> AnalysisReadinessResult

This module does NOT:
- load from storage
- persist anything
- open files
- read Excel/PDF
- calculate hashes
- infer MIME
- inspect document content
- execute analysis
- dispatch microservices
- call excel_diagnostic or supplier_duplicate_check
- change IntakeRecord.intake_state

It only decides whether an intake is ready for analysis based on
metadata and sufficiency state, and which runtime classification
would apply if executed.

See: docs/smartpyme/SMARTPYME_READY_FOR_ANALYSIS_GATE.md
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Readiness statuses
# ---------------------------------------------------------------------------

READINESS_READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
READINESS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
READINESS_BLOCKED = "BLOCKED"
READINESS_UNSUPPORTED = "UNSUPPORTED"

ALLOWED_READINESS_STATUSES: tuple[str, ...] = (
    READINESS_READY_FOR_ANALYSIS,
    READINESS_NEEDS_EVIDENCE,
    READINESS_BLOCKED,
    READINESS_UNSUPPORTED,
)

# ---------------------------------------------------------------------------
# Suggested next states (mirror intake states for clarity)
# ---------------------------------------------------------------------------

SUGGESTED_READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
SUGGESTED_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
SUGGESTED_BLOCKED = "BLOCKED"
SUGGESTED_UNSUPPORTED = "UNSUPPORTED"

# ---------------------------------------------------------------------------
# Runtime classifications (conservative, closed set)
# ---------------------------------------------------------------------------

RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC = "excel_diagnostic"
RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK = "supplier_duplicate_check"

ALLOWED_RUNTIME_CLASSIFICATIONS: tuple[str, ...] = (
    RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC,
    RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
)


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class AnalysisReadinessResult:
    """Pure result describing whether an intake is ready for analysis.

    This is a recommendation, not a mutation. It does not change any
    IntakeRecord state or persist anything.
    """

    tenant_id: str
    intake_id: str
    status: str
    suggested_next_state: str
    runtime_classification: str | None
    can_execute: bool
    blocking_reasons: list[str] = field(default_factory=list)
    missing_request_ids: list[str] = field(default_factory=list)
    matched_evidence_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    audit_notes: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "intake_id": self.intake_id,
            "status": self.status,
            "suggested_next_state": self.suggested_next_state,
            "runtime_classification": self.runtime_classification,
            "can_execute": self.can_execute,
            "blocking_reasons": list(self.blocking_reasons),
            "missing_request_ids": list(self.missing_request_ids),
            "matched_evidence_ids": list(self.matched_evidence_ids),
            "warnings": list(self.warnings),
            "audit_notes": list(self.audit_notes),
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_dict(obj: Any, *, label: str) -> dict:
    """Convert IntakeRecord/EvidenceSufficiencyResult/dict to dict."""
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


def _extract_evidence_requests(intake: dict) -> list[dict]:
    """Return evidence_requests as list[dict] or raise."""
    er = intake.get("evidence_requests")
    if er is None:
        # Some intakes legitimately have no requests (e.g. READY without requests)
        return []
    if not isinstance(er, list):
        raise ValueError("intake_record.evidence_requests must be a list")
    out: list[dict] = []
    for i, item in enumerate(er):
        if isinstance(item, dict):
            out.append(dict(item))
        elif hasattr(item, "to_dict") and callable(item.to_dict):
            d = item.to_dict()
            if not isinstance(d, dict):
                raise ValueError(
                    f"evidence_requests[{i}].to_dict() did not return a dict"
                )
            out.append(dict(d))
        else:
            raise ValueError(
                f"evidence_requests[{i}] must be a dict or have to_dict()"
            )
    return out


def _resolve_runtime_classification(
    evidence_requests: list[dict],
    tank_selection_result: dict | None,
) -> tuple[str | None, list[str]]:
    """Determine runtime classification from evidence_requests.

    Returns (classification, warnings).

    Conservative rule:
    - only excel_diagnostic enabled -> excel_diagnostic
    - only supplier_duplicate_check enabled -> supplier_duplicate_check
    - both enabled -> UNSUPPORTED + ambiguity warning
    - none enabled -> None (caller will set UNSUPPORTED)
    """
    enabled: set[str] = set()
    for req in evidence_requests:
        ec = req.get("enables_classification")
        if isinstance(ec, str) and ec in ALLOWED_RUNTIME_CLASSIFICATIONS:
            enabled.add(ec)

    warnings: list[str] = []

    if not enabled:
        return None, warnings

    if len(enabled) == 1:
        (only,) = enabled
        return only, warnings

    # Ambiguous: both classifications enabled
    # Try tie-break via tank_selection_result
    selected = None
    if isinstance(tank_selection_result, dict):
        selected_tanks = tank_selection_result.get("selected_tanks") or []
        if isinstance(selected_tanks, list) and len(selected_tanks) == 1:
            selected = str(selected_tanks[0])

    if selected and "supplier" in selected.lower() and "duplicate" in selected.lower():
        return RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK, warnings

    if selected and "excel" in selected.lower() and "diagnostic" in selected.lower():
        return RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC, warnings

    warnings.append(
        "Ambiguous runtime classification: multiple classifications enabled "
        f"({sorted(enabled)}). No clear tie-break available."
    )
    return None, warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_analysis_readiness(
    intake_record: Any,
    sufficiency_result: Any,
) -> AnalysisReadinessResult:
    """Decide whether an intake is ready for analysis.

    Parameters
    ----------
    intake_record : IntakeRecord or dict
        Must contain tenant_id, intake_id.
    sufficiency_result : EvidenceSufficiencyResult or dict
        Must contain tenant_id, intake_id, status.

    Returns
    -------
    AnalysisReadinessResult
        Pure, JSON-serializable result. Does NOT mutate inputs.

    Raises
    ------
    ValueError
        If inputs violate the contract.
    """
    # --- Input validation -----------------------------------------------
    intake = _as_dict(intake_record, label="intake_record")
    suff = _as_dict(sufficiency_result, label="sufficiency_result")

    _require_field(intake, "tenant_id", label="intake_record")
    _require_field(intake, "intake_id", label="intake_record")
    _require_field(suff, "tenant_id", label="sufficiency_result")
    _require_field(suff, "intake_id", label="sufficiency_result")
    _require_field(suff, "status", label="sufficiency_result")

    tenant_id = str(intake["tenant_id"])
    intake_id = str(intake["intake_id"])
    s_tenant = str(suff["tenant_id"])
    s_intake = str(suff["intake_id"])

    if tenant_id != s_tenant:
        raise ValueError(
            f"tenant_id mismatch: intake={tenant_id!r}, "
            f"sufficiency={s_tenant!r}"
        )
    if intake_id != s_intake:
        raise ValueError(
            f"intake_id mismatch: intake={intake_id!r}, "
            f"sufficiency={s_intake!r}"
        )

    suff_status = str(suff["status"])
    if suff_status not in (
        "READY",
        "NEEDS_MORE_EVIDENCE",
        "BLOCKED",
        "UNSUPPORTED",
    ):
        raise ValueError(
            f"sufficiency_result.status not recognized: {suff_status!r}"
        )

    # Common propagated fields
    missing_request_ids: list[str] = list(suff.get("missing_request_ids") or [])
    matched_evidence_ids: list[str] = list(suff.get("matched_evidence_ids") or [])
    suff_warnings: list[str] = list(suff.get("warnings") or [])
    suff_audit: list[str] = list(suff.get("audit_notes") or [])

    intake_state = intake.get("intake_state")

    # --- Rule 1: blocked intake -----------------------------------------
    if intake_state == "BLOCKED":
        return AnalysisReadinessResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=READINESS_BLOCKED,
            suggested_next_state=SUGGESTED_BLOCKED,
            runtime_classification=None,
            can_execute=False,
            blocking_reasons=["Intake is blocked."],
            missing_request_ids=missing_request_ids,
            matched_evidence_ids=matched_evidence_ids,
            warnings=suff_warnings,
            audit_notes=suff_audit + ["Short-circuit: intake_state=BLOCKED."],
        )

    # --- Rule 2: blocked sufficiency ------------------------------------
    if suff_status == "BLOCKED":
        return AnalysisReadinessResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=READINESS_BLOCKED,
            suggested_next_state=SUGGESTED_BLOCKED,
            runtime_classification=None,
            can_execute=False,
            blocking_reasons=["Sufficiency result is BLOCKED."],
            missing_request_ids=missing_request_ids,
            matched_evidence_ids=matched_evidence_ids,
            warnings=suff_warnings,
            audit_notes=suff_audit,
        )

    # --- Rule 3: needs more evidence ------------------------------------
    if suff_status == "NEEDS_MORE_EVIDENCE":
        return AnalysisReadinessResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=READINESS_NEEDS_EVIDENCE,
            suggested_next_state=SUGGESTED_NEEDS_EVIDENCE,
            runtime_classification=None,
            can_execute=False,
            blocking_reasons=["Evidence is insufficient for analysis."],
            missing_request_ids=missing_request_ids,
            matched_evidence_ids=matched_evidence_ids,
            warnings=suff_warnings,
            audit_notes=suff_audit,
        )

    # --- Rule 4: unsupported sufficiency --------------------------------
    if suff_status == "UNSUPPORTED":
        return AnalysisReadinessResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=READINESS_UNSUPPORTED,
            suggested_next_state=SUGGESTED_UNSUPPORTED,
            runtime_classification=None,
            can_execute=False,
            blocking_reasons=["Sufficiency result is UNSUPPORTED."],
            missing_request_ids=missing_request_ids,
            matched_evidence_ids=matched_evidence_ids,
            warnings=suff_warnings,
            audit_notes=suff_audit,
        )

    # --- Rule 5/6: sufficiency READY -> resolve runtime classification ----
    evidence_requests = _extract_evidence_requests(intake)
    tank_selection = intake.get("tank_selection_result")
    if isinstance(tank_selection, dict):
        tank_selection_dict: dict | None = dict(tank_selection)
    else:
        tank_selection_dict = None

    rt_class, rt_warnings = _resolve_runtime_classification(
        evidence_requests, tank_selection_dict
    )

    warnings_out = list(suff_warnings) + rt_warnings

    if rt_class is None:
        return AnalysisReadinessResult(
            tenant_id=tenant_id,
            intake_id=intake_id,
            status=READINESS_UNSUPPORTED,
            suggested_next_state=SUGGESTED_UNSUPPORTED,
            runtime_classification=None,
            can_execute=False,
            blocking_reasons=["No supported runtime classification found."],
            missing_request_ids=missing_request_ids,
            matched_evidence_ids=matched_evidence_ids,
            warnings=warnings_out,
            audit_notes=suff_audit + [
                "Sufficiency READY but no runtime classification could be resolved."
            ],
        )

    # Rule 6: sufficiency READY + runtime classification supported
    return AnalysisReadinessResult(
        tenant_id=tenant_id,
        intake_id=intake_id,
        status=READINESS_READY_FOR_ANALYSIS,
        suggested_next_state=SUGGESTED_READY_FOR_ANALYSIS,
        runtime_classification=rt_class,
        can_execute=True,
        blocking_reasons=[],
        missing_request_ids=missing_request_ids,
        matched_evidence_ids=matched_evidence_ids,
        warnings=warnings_out,
        audit_notes=suff_audit + [
            f"Readiness resolved: status=READY_FOR_ANALYSIS, "
            f"runtime_classification={rt_class}."
        ],
    )


__all__ = [
    "AnalysisReadinessResult",
    "evaluate_analysis_readiness",
    "READINESS_READY_FOR_ANALYSIS",
    "READINESS_NEEDS_EVIDENCE",
    "READINESS_BLOCKED",
    "READINESS_UNSUPPORTED",
    "ALLOWED_READINESS_STATUSES",
    "SUGGESTED_READY_FOR_ANALYSIS",
    "SUGGESTED_NEEDS_EVIDENCE",
    "SUGGESTED_BLOCKED",
    "SUGGESTED_UNSUPPORTED",
    "RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC",
    "RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK",
    "ALLOWED_RUNTIME_CLASSIFICATIONS",
]
