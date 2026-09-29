"""Runtime formula execution for diagnostic gate decisions."""

from __future__ import annotations

from pymia.contracts.formula_contract import (
    SUPPORTED_FORMULAS,
    FormulaInput,
    FormulaResult,
    FormulaStatus,
)
from pymia.diagnostic_core.models import (
    DiagnosticCoreInput,
    EvidenceGateDecision,
    EvidenceGateDecisionStatus,
)
from pymia.services.formula_engine_service import FormulaEngineService


def execute_allowed_formulas_from_gate_decisions(
    core_input: DiagnosticCoreInput,
    gate_decisions: list[EvidenceGateDecision],
) -> list[FormulaResult]:
    """Execute only formulas explicitly allowed by the diagnostic evidence gate."""
    if not isinstance(core_input, DiagnosticCoreInput):
        raise ValueError("core_input must be a DiagnosticCoreInput")
    if not isinstance(gate_decisions, list):
        raise ValueError("gate_decisions must be a list")

    service = FormulaEngineService()
    results: list[FormulaResult] = []
    for decision in gate_decisions:
        if not isinstance(decision, EvidenceGateDecision):
            raise ValueError("gate_decisions items must be EvidenceGateDecision")
        if decision.decision != EvidenceGateDecisionStatus.ALLOW_EXECUTION:
            results.append(
                FormulaResult(
                    formula_id=decision.formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs={},
                    source_refs=[],
                    blocking_reason=f"GATE_BLOCKED: {','.join(decision.missing_variables)}",
                )
            )
            continue

        rule = SUPPORTED_FORMULAS.get(decision.formula_id)
        if rule is None:
            results.append(
                FormulaResult(
                    formula_id=decision.formula_id,
                    status=FormulaStatus.BLOCKED,
                    value=None,
                    inputs={},
                    source_refs=[],
                    blocking_reason="FORMULA_NOT_SUPPORTED",
                )
            )
            continue

        inputs = [
            FormulaInput(
                name=name,
                value=core_input.variables.get(name),
                source_refs=core_input.evidence_refs.get(name, []),
            )
            for name in rule.required_inputs
        ]
        results.append(service.calculate(decision.formula_id, inputs))
    return results


__all__ = ["execute_allowed_formulas_from_gate_decisions"]
