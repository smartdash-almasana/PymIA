from __future__ import annotations

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core.evidence_sufficiency import (
    build_evidence_gate_decisions_for_status,
)
from pymia.diagnostic_core.models import EvidenceGateDecision

from .investigation import (
    INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    InvestigationRecord,
)


def build_evidence_gate_decisions_for_investigation(
    investigation: InvestigationRecord,
    evidence: StructuredEvidence,
    *,
    formula_ids: list[str],
) -> list[EvidenceGateDecision]:
    if not isinstance(investigation, InvestigationRecord):
        raise ValueError("investigation must be an InvestigationRecord")

    return build_evidence_gate_decisions_for_status(
        investigation.status,
        evidence,
        ready_status=INVESTIGATION_STATUS_READY_FOR_CONTRAST,
        case_id=investigation.intake_id,
        tenant_id=investigation.tenant_id,
        formula_ids=formula_ids,
    )
