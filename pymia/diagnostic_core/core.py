from __future__ import annotations

from pymia.contracts.formula_contract import SUPPORTED_FORMULAS, FormulaInput, FormulaStatus
from pymia.services.formula_engine_service import FormulaEngineService

from .models import (
    CoreDiagnosticResult,
    CoreDiagnosticStatus,
    CoreFinding,
    CoreFormulaResult,
    DiagnosticCoreInput,
    DiagnosticCoreResult,
    DiagnosticCoreStatus,
)


class DiagnosticCoreV1:
    def __init__(self, formula_engine: FormulaEngineService | None = None) -> None:
        self._formula_engine = formula_engine or FormulaEngineService()

    def run(self, core_input: DiagnosticCoreInput) -> DiagnosticCoreResult:
        formula_results: list[CoreFormulaResult] = []
        diagnostic_results: list[CoreDiagnosticResult] = []
        findings: list[CoreFinding] = []
        blocked_reasons: list[str] = []
        missing_evidence: list[str] = []

        for formula_id in core_input.formula_ids:
            formula_inputs = self._build_formula_inputs(core_input, formula_id)
            result = self._formula_engine.calculate(formula_id, formula_inputs)
            core_formula = CoreFormulaResult(
                formula_id=result.formula_id,
                status=str(result.status),
                value=result.value,
                source_refs=result.source_refs,
                blocking_reason=result.blocking_reason,
            )
            formula_results.append(core_formula)
            pathology_code = self._pathology_for_formula(core_input, formula_id)

            if result.status == FormulaStatus.OK:
                diagnostic_results.append(
                    CoreDiagnosticResult(
                        pathology_code=pathology_code,
                        status=CoreDiagnosticStatus.CANDIDATE,
                        formula_id=formula_id,
                        reason="FORMULA_CALCULATED_DIAGNOSTIC_NOT_CONFIRMED_IN_M34_S1",
                        evidence_refs=result.source_refs,
                    )
                )
                findings.append(
                    CoreFinding(
                        finding_id=f"finding:{pathology_code}:{formula_id}",
                        pathology_code=pathology_code,
                        formula_id=formula_id,
                        status="CANDIDATE",
                        summary="Formula calculated; diagnostic confirmation is outside M34-S1.",
                        evidence_refs=result.source_refs,
                    )
                )
                continue

            reason = result.blocking_reason or "FORMULA_BLOCKED"
            blocked_reasons.append(f"{formula_id}:{reason}")
            if reason.startswith("MISSING_INPUTS:"):
                missing_evidence.extend(self._missing_inputs_from_reason(reason))
            diagnostic_results.append(
                CoreDiagnosticResult(
                    pathology_code=pathology_code,
                    status=CoreDiagnosticStatus.BLOCKED,
                    formula_id=formula_id,
                    reason=reason,
                    evidence_refs=result.source_refs,
                )
            )

        return DiagnosticCoreResult(
            case_id=core_input.case_id,
            tenant_id=core_input.tenant_id,
            status=self._overall_status(formula_results),
            formula_results=formula_results,
            diagnostic_results=diagnostic_results,
            findings=findings,
            missing_evidence=sorted(set(missing_evidence)),
            blocked_reasons=blocked_reasons,
        )

    def _build_formula_inputs(
        self,
        core_input: DiagnosticCoreInput,
        formula_id: str,
    ) -> list[FormulaInput]:
        required_names = SUPPORTED_FORMULAS.get(formula_id).required_inputs if formula_id in SUPPORTED_FORMULAS else None
        names = required_names or list(core_input.variables.keys())
        return [
            FormulaInput(
                name=name,
                value=core_input.variables.get(name),
                source_refs=core_input.evidence_refs.get(name, []),
            )
            for name in names
        ]

    def _pathology_for_formula(self, core_input: DiagnosticCoreInput, formula_id: str) -> str:
        if formula_id.startswith("REN_001"):
            return "REN_001"
        if formula_id.startswith("LIQ_001"):
            return "LIQ_001"
        if core_input.hypothesis_codes:
            return core_input.hypothesis_codes[0]
        return "UNSPECIFIED"

    def _missing_inputs_from_reason(self, reason: str) -> list[str]:
        _, raw = reason.split(":", 1)
        return [item.strip() for item in raw.split(",") if item.strip()]

    def _overall_status(self, formula_results: list[CoreFormulaResult]) -> DiagnosticCoreStatus:
        if not formula_results:
            return DiagnosticCoreStatus.INSUFFICIENT
        if any(result.status == str(FormulaStatus.OK) for result in formula_results):
            return DiagnosticCoreStatus.PARTIAL
        return DiagnosticCoreStatus.BLOCKED
