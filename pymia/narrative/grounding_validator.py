from __future__ import annotations

from .models import EvidenceItem, NarrativeReport, ValidationResult


def validate_grounding(report: NarrativeReport, evidence_pool: list[EvidenceItem]) -> ValidationResult:
    valid_ids = {item.id for item in evidence_pool}
    by_id = {item.id: item for item in evidence_pool}

    errors: list[str] = []
    for section in report.sections:
        for claim in section.claims:
            if not claim.evidence_ids:
                errors.append(f"Section '{section.title}' has claim without evidence id")
                continue
            for evidence_id in claim.evidence_ids:
                if evidence_id not in valid_ids:
                    errors.append(f"Section '{section.title}' references missing evidence id: {evidence_id}")
                    continue

                item = by_id[evidence_id]
                if claim.expected_metric and claim.expected_metric != item.metric:
                    errors.append(
                        f"Section '{section.title}' claim metric mismatch for {evidence_id}: expected {claim.expected_metric}, found {item.metric}"
                    )
                if claim.expected_value is not None:
                    val = item.value
                    if not isinstance(val, (int, float)):
                        errors.append(f"Section '{section.title}' expected numeric value for {evidence_id}")
                    elif abs(float(val) - float(claim.expected_value)) > 1e-6:
                        errors.append(
                            f"Section '{section.title}' claim value mismatch for {evidence_id}: expected {claim.expected_value}, found {val}"
                        )

    return ValidationResult(ok=not errors, errors=errors)
