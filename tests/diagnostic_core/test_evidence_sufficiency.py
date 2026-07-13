import pytest

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.formula_contract import FormulaResult, FormulaStatus
from pymia.diagnostic_core.evidence_sufficiency import (
    EvidenceGateDecision,
    EvidenceGateDecisionStatus,
    build_evidence_gate_decisions_for_investigation,
    execute_allowed_formulas_from_gate_decisions,
)
from pymia.diagnostic_core.models import DiagnosticCoreInput
from pymia.smartpyme.investigation import (
    INVESTIGATION_STATUS_OPEN,
    INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    INVESTIGATION_STATUS_WAITING_EVIDENCE,
    InvestigationRecord,
)

_STRUCTURED_EVIDENCE_DUMMY = StructuredEvidence(
    tenant_id="tenant_test",
    document_type="xlsx_operacional",
    computed_variables={"ventas_total": 100.0, "cobranzas_total": 60.0},
)

_LIQ_FORMULA = "LIQ_001_vendido_cobrado"
_INV_FORMULA = "INV_001_punto_reposicion"


@pytest.fixture
def open_investigation() -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id="inv_001",
        tenant_id="tenant_test",
        intake_id="intake_test",
        anamnesis_id="anamnesis_test",
        owner_prompt="necesito ver los costos",
        investigation_axis="costos_proveedores",
        declared_question="¿Podés detallar los costos directos?",
        status=INVESTIGATION_STATUS_OPEN,
    )


@pytest.fixture
def waiting_evidence_investigation() -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id="inv_002",
        tenant_id="tenant_test",
        intake_id="intake_test",
        anamnesis_id="anamnesis_test",
        owner_prompt="necesito ver los costos",
        investigation_axis="costos_proveedores",
        declared_question="¿Podés detallar los costos directos?",
        status=INVESTIGATION_STATUS_WAITING_EVIDENCE,
    )


@pytest.fixture
def ready_investigation() -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id="inv_003",
        tenant_id="tenant_test",
        intake_id="intake_test",
        anamnesis_id="anamnesis_test",
        owner_prompt="necesito ver los costos",
        investigation_axis="costos_proveedores",
        declared_question="¿Podés detallar los costos directos?",
        status=INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    )


def _sort_key(d: EvidenceGateDecision) -> str:
    return d.formula_id


def test_open_investigation_blocks_all_formulas(open_investigation: InvestigationRecord):
    decisions = build_evidence_gate_decisions_for_investigation(
        open_investigation,
        _STRUCTURED_EVIDENCE_DUMMY,
        formula_ids=[_LIQ_FORMULA, _INV_FORMULA],
    )
    assert len(decisions) == 2
    for d in decisions:
        assert d.decision == EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS
        assert d.missing_variables == [f"investigation_status:{INVESTIGATION_STATUS_OPEN}"]


def test_waiting_evidence_investigation_blocks_all_formulas(waiting_evidence_investigation: InvestigationRecord):
    decisions = build_evidence_gate_decisions_for_investigation(
        waiting_evidence_investigation,
        _STRUCTURED_EVIDENCE_DUMMY,
        formula_ids=[_LIQ_FORMULA, _INV_FORMULA],
    )
    assert len(decisions) == 2
    for d in decisions:
        assert d.decision == EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS
        assert d.missing_variables == [f"investigation_status:{INVESTIGATION_STATUS_WAITING_EVIDENCE}"]


def test_ready_for_contrast_delegates_to_normal_gate(ready_investigation: InvestigationRecord):
    decisions = build_evidence_gate_decisions_for_investigation(
        ready_investigation,
        _STRUCTURED_EVIDENCE_DUMMY,
        formula_ids=[_LIQ_FORMULA, _INV_FORMULA],
    )
    assert len(decisions) == 2
    decisions_sorted = sorted(decisions, key=_sort_key)

    liq = [d for d in decisions_sorted if d.formula_id == _LIQ_FORMULA][0]
    assert liq.decision == EvidenceGateDecisionStatus.ALLOW_EXECUTION

    inv = [d for d in decisions_sorted if d.formula_id == _INV_FORMULA][0]
    assert inv.decision == EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS


def test_raises_on_non_investigation_record():
    with pytest.raises(ValueError, match="investigation must be an InvestigationRecord"):
        build_evidence_gate_decisions_for_investigation(
            "not_investigation",
            _STRUCTURED_EVIDENCE_DUMMY,
            formula_ids=[_LIQ_FORMULA],
        )


# -- execute_allowed_formulas_from_gate_decisions --

@pytest.fixture
def core_input() -> DiagnosticCoreInput:
    return DiagnosticCoreInput(
        case_id="intake_test",
        tenant_id="tenant_test",
        variables={"ventas": 100.0, "costos": 60.0},
        evidence_refs={
            "ventas": ["src_ventas"],
            "costos": ["src_costos"],
        },
    )


def test_allowed_formula_executes_service(core_input: DiagnosticCoreInput):
    gate_decisions = [
        EvidenceGateDecision(
            formula_id="ganancia_bruta",
            decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION,
        ),
    ]
    results = execute_allowed_formulas_from_gate_decisions(core_input, gate_decisions)
    assert len(results) == 1
    assert results[0].formula_id == "ganancia_bruta"
    assert results[0].status == FormulaStatus.OK
    assert results[0].value == 40.0
    assert results[0].inputs == {"ventas": 100.0, "costos": 60.0}
    assert "src_ventas" in results[0].source_refs
    assert "src_costos" in results[0].source_refs


def test_blocked_gate_returns_gate_blocked(core_input: DiagnosticCoreInput):
    gate_decisions = [
        EvidenceGateDecision(
            formula_id="ganancia_bruta",
            decision=EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS,
            missing_variables=["ventas"],
        ),
    ]
    results = execute_allowed_formulas_from_gate_decisions(core_input, gate_decisions)
    assert len(results) == 1
    assert results[0].formula_id == "ganancia_bruta"
    assert results[0].status == FormulaStatus.BLOCKED
    assert results[0].value is None
    assert results[0].blocking_reason == "GATE_BLOCKED: ventas"


def test_unsupported_formula_returns_not_supported(core_input: DiagnosticCoreInput):
    gate_decisions = [
        EvidenceGateDecision(
            formula_id="FORMULA_X",
            decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION,
        ),
    ]
    results = execute_allowed_formulas_from_gate_decisions(core_input, gate_decisions)
    assert len(results) == 1
    assert results[0].formula_id == "FORMULA_X"
    assert results[0].status == FormulaStatus.BLOCKED
    assert results[0].blocking_reason == "FORMULA_NOT_SUPPORTED"


def test_invalid_core_input_raises_value_error():
    with pytest.raises(ValueError, match="core_input must be a DiagnosticCoreInput"):
        execute_allowed_formulas_from_gate_decisions(
            "not_core_input",
            [EvidenceGateDecision(formula_id="x", decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION)],
        )


def test_gate_decisions_not_list_raises_value_error(core_input: DiagnosticCoreInput):
    with pytest.raises(ValueError, match="gate_decisions must be a list"):
        execute_allowed_formulas_from_gate_decisions(core_input, "not_list")


def test_gate_decisions_item_not_evidence_gate_decision_raises_value_error(core_input: DiagnosticCoreInput):
    with pytest.raises(ValueError, match="gate_decisions items must be EvidenceGateDecision"):
        execute_allowed_formulas_from_gate_decisions(core_input, ["not_a_decision"])
