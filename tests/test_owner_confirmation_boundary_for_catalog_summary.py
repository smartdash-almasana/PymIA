from pathlib import Path
import pytest
from pymia.faithful_operator import (
    handle_owner_confirmation,
    build_confirmed_candidate_next_actions,
    OperatorPhase,
    OperatorState,
)

def _state_with_catalog() -> OperatorState:
    return OperatorState(
        tenant_id="tenant_demo",
        intake_id="intake_demo_001",
        owner_message="Tengo un problema operativo.",
        current_state=OperatorPhase.OWNER_CONFIRMATION_PENDING,
        problem_summary="Tengo un problema operativo.",
        evidence_requested=["ventas", "costos"],
        next_question="Síntesis...",
        evidence_id="evidence_demo",
        evidence_hash="evidence_hash_demo",
        run_id="run_demo",
        output_hash="output_hash_demo",
        candidate_response="Resultado candidato.",
        limit="No declara verdad final.",
        owner_confirmation_status="pending",
        catalog_reconciliation=[
            {
                "formula_id": "REN_001_margen_neto_real",
                "pathology_code": "REN_001",
                "status": "pending_data",
                "missing_evidence": ["impuestos_y_comisiones"]
            }
        ]
    )

def test_confirmed_with_catalog_reconciliation():
    state = _state_with_catalog()
    new_state = handle_owner_confirmation(state, "sí, correcto representa el negocio")
    
    # 1. Confirmación explícita con catalog_reconciliation marca:
    # - owner_confirmation_status = catalog_summary_confirmed
    # - no contiene diagnóstico final (es decir, aclara que NO es diagnóstico)
    # - no ejecuta próximos pasos operativos definitivos
    assert new_state.current_state == OperatorPhase.CLOSED
    assert new_state.owner_confirmation_status == "catalog_summary_confirmed"
    assert "no se declara diagnóstico final" in new_state.next_question.lower()
    
    # build_confirmed_candidate_next_actions should block and not execute
    next_actions = build_confirmed_candidate_next_actions(new_state)
    assert next_actions.startswith("BLOQUEADO")
    assert "no hay candidato confirmado" in next_actions

def test_correction_requested_with_catalog_reconciliation():
    state = _state_with_catalog()
    new_state = handle_owner_confirmation(state, "no representa la realidad, está mal")
    
    # 2. Corrección explícita con catalog_reconciliation marca:
    # - owner_confirmation_status = catalog_summary_correction_requested
    # - pide corrección concreta o nueva evidencia
    assert new_state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert new_state.owner_confirmation_status == "catalog_summary_correction_requested"
    assert "corrección concreta o nueva evidencia" in new_state.next_question.lower()

def test_new_evidence_assimilated_to_correction():
    state = _state_with_catalog()
    new_state = handle_owner_confirmation(state, "te paso otro archivo con los datos reales")
    
    # 3. Nueva evidencia se asimila a correction_requested:
    # - owner_confirmation_status = catalog_summary_correction_requested
    # - no reprocesa automáticamente (next_question solicita la corrección/evidencia)
    assert new_state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert new_state.owner_confirmation_status == "catalog_summary_correction_requested"
    assert "corrección concreta o nueva evidencia" in new_state.next_question.lower()

def test_owner_uncertainty_blocks_with_catalog_reconciliation():
    state = _state_with_catalog()
    new_state = handle_owner_confirmation(state, "no se, no estoy seguro")
    
    # 4. Incertidumbre del dueño bloquea:
    # - current_state = BLOCKED
    # - owner_confirmation_status = catalog_summary_owner_uncertain
    # - blocked_reason = owner_uncertain_about_catalog_summary
    assert new_state.current_state == OperatorPhase.BLOCKED
    assert new_state.owner_confirmation_status == "catalog_summary_owner_uncertain"
    assert new_state.blocked_reason == "owner_uncertain_about_catalog_summary"
    assert "validación del dueño o evidencia adicional" in new_state.next_question.lower()

def test_unclear_confirmation_blocks_with_catalog_reconciliation():
    state = _state_with_catalog()
    new_state = handle_owner_confirmation(state, "no entiendo a qué te referís con eso")
    
    # 5. Respuesta ambigua bloquea:
    # - current_state = BLOCKED
    # - owner_confirmation_status = catalog_summary_unclear_confirmation
    # - blocked_reason = unclear_catalog_summary_confirmation
    assert new_state.current_state == OperatorPhase.BLOCKED
    assert new_state.owner_confirmation_status == "catalog_summary_unclear_confirmation"
    assert new_state.blocked_reason == "unclear_catalog_summary_confirmation"
    assert "confirmación clara, una corrección concreta" in new_state.next_question.lower()

def test_catalog_reconciliation_is_not_mutated():
    # 6. No se modifica catalog_reconciliation al procesar la respuesta.
    state = _state_with_catalog()
    initial_reconciliation = list(state.catalog_reconciliation)
    
    new_state = handle_owner_confirmation(state, "sí, correcto")
    assert new_state.catalog_reconciliation == initial_reconciliation

def test_no_catalog_reconciliation_uses_standard_behavior():
    # 7. Sin catalog_reconciliation, se conserva comportamiento estándar existente:
    # - confirmación normal sigue usando candidate_confirmed
    # - no usa prefijo catalog_summary_
    state = OperatorState(
        tenant_id="tenant_demo",
        intake_id="intake_demo_001",
        owner_message="Mensaje.",
        current_state=OperatorPhase.OWNER_CONFIRMATION_PENDING,
        problem_summary="Problema.",
        evidence_requested=["ventas"],
        next_question="...",
        owner_confirmation_status="pending",
        catalog_reconciliation=[]
    )
    new_state = handle_owner_confirmation(state, "sí, correcto")
    assert new_state.owner_confirmation_status == "candidate_confirmed"
    assert "catalog_summary" not in new_state.owner_confirmation_status

def test_static_checks_no_cafeteria():
    # 9. Test estático: no hay imports ni referencias a cafeteria_margin_focus ni margin_evidence_request
    operator_path = Path(__file__).parent.parent / "pymia" / "faithful_operator.py"
    content = operator_path.read_text(encoding="utf-8")
    
    term1 = "cafeteria" + "_margin_focus"
    term2 = "margin" + "_evidence" + "_request"
    
    assert term1 not in content
    assert term2 not in content
