from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.formula_contract import SUPPORTED_FORMULAS

from .evidence_binding import build_diagnostic_core_input_from_structured_evidence


class EvidenceSufficiencyStatus(StrEnum):
    READY = "READY"
    MISSING_INPUTS = "MISSING_INPUTS"


class FormulaEvidenceSufficiency(BaseModel):
    formula_id: str
    required_variables: list[str] = Field(default_factory=list)
    available_variables: list[str] = Field(default_factory=list)
    missing_variables: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    status: EvidenceSufficiencyStatus


def build_evidence_sufficiency_report_from_structured_evidence(
    evidence: StructuredEvidence,
    *,
    case_id: str,
    tenant_id: str,
    formula_ids: list[str],
) -> list[FormulaEvidenceSufficiency]:
    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id=case_id,
        tenant_id=tenant_id,
        formula_ids=formula_ids,
        hypothesis_codes=[],
    )

    report: list[FormulaEvidenceSufficiency] = []
    for formula_id in formula_ids:
        if formula_id not in SUPPORTED_FORMULAS:
            raise KeyError(f"Unsupported formula_id: {formula_id}")

        required_variables = list(SUPPORTED_FORMULAS[formula_id].required_inputs)
        available_variables = [name for name in required_variables if name in core_input.variables]
        missing_variables = [name for name in required_variables if name not in core_input.variables]
        source_refs = _collect_formula_source_refs(core_input.evidence_refs, available_variables)

        report.append(
            FormulaEvidenceSufficiency(
                formula_id=formula_id,
                required_variables=required_variables,
                available_variables=available_variables,
                missing_variables=missing_variables,
                source_refs=source_refs,
                status=(
                    EvidenceSufficiencyStatus.READY
                    if not missing_variables
                    else EvidenceSufficiencyStatus.MISSING_INPUTS
                ),
            )
        )

    return report


def _collect_formula_source_refs(
    evidence_refs: dict[str, list[str]],
    available_variables: list[str],
) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()

    for variable_name in available_variables:
        for ref in evidence_refs.get(variable_name, []):
            if ref in seen:
                continue
            seen.add(ref)
            refs.append(ref)

    return refs
