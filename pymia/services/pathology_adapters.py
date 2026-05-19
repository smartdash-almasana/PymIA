from __future__ import annotations

from pymia.contracts.diagnostic_report_contract import FindingRecord
from pymia.contracts.pathology_contract import PathologyFinding, PathologySeverity, PathologyStatus


class PathologyAdapterError(ValueError):
    """Error fail-closed para adaptaciones patología → hallazgo."""


def pathology_finding_to_finding_record(finding: PathologyFinding) -> FindingRecord:
    """Convierte un PathologyFinding trazable en FindingRecord diagnóstico.

    No fabrica evidencia. Si no hay source_refs o severidad, bloquea.
    """

    if finding.status != PathologyStatus.ACTIVE:
        raise PathologyAdapterError("ONLY_ACTIVE_PATHOLOGIES_CAN_BECOME_FINDINGS")

    if not finding.source_refs:
        raise PathologyAdapterError("SOURCE_REFS_REQUIRED")

    if finding.severity is None:
        raise PathologyAdapterError("SEVERITY_REQUIRED")

    measured_difference = finding.metadata.get("measured_difference")
    if not measured_difference:
        measured_difference = {
            "pathology_status": finding.status.value,
            "formula_id": finding.formula_id,
            "formula_result_id": finding.formula_result_id,
        }

    severity = finding.severity
    if not isinstance(severity, PathologySeverity):
        severity = PathologySeverity(str(severity))

    return FindingRecord(
        entity=finding.cliente_id,
        finding_type=finding.pathology_id,
        measured_difference=measured_difference,
        compared_sources=list(finding.source_refs),
        evidence_used=list(finding.source_refs),
        severity=severity,
        recommendation=finding.suggested_action,
        explanation=finding.explanation,
        metadata={
            **finding.metadata,
            "formula_id": finding.formula_id,
            "formula_result_id": finding.formula_result_id,
        },
    )
