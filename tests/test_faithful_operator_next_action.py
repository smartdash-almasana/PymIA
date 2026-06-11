from pymia.faithful_operator import OperatorPhase, OperatorState
from pymia.faithful_operator_next_action import OperatorNextAction, build_operator_next_action


def _base_state(**overrides: object) -> OperatorState:
    values = {
        "tenant_id": "tenant_demo",
        "intake_id": "intake_demo",
        "owner_message": "Vendo mas pero no me queda plata.",
        "current_state": OperatorPhase.EVIDENCE_REQUESTED,
        "problem_summary": "Vendo mas pero no me queda plata.",
        "evidence_requested": ["ventas", "costos", "productos", "periodo"],
        "next_question": "Necesito evidencia minima: ventas, costos, productos y periodo.",
    }
    values.update(overrides)
    return OperatorState(**values)


def _assert_complete_next_action(action: OperatorNextAction) -> None:
    assert action.owner_question
    assert action.required_evidence
    assert action.operator_decision
    assert action.stop_condition


def test_owner_confirmation_pending_returns_semantic_confirmation_action() -> None:
    state = _base_state(
        current_state=OperatorPhase.OWNER_CONFIRMATION_PENDING,
        next_question="¿Estas columnas representan ventas, costos, productos y periodo?",
    )

    action = build_operator_next_action(state)

    _assert_complete_next_action(action)
    assert action.owner_question == state.next_question
    assert "confirmación semántica" in action.required_evidence
    assert "confirmación" in action.operator_decision
    assert "incertidumbre semántica" in action.stop_condition


def test_closed_confirmed_candidate_asks_focus_choice() -> None:
    state = _base_state(
        current_state=OperatorPhase.CLOSED,
        owner_confirmation_status="candidate_confirmed",
    )

    action = build_operator_next_action(state)

    _assert_complete_next_action(action)
    assert "margen por producto" in action.owner_question
    assert "caja por período" in action.owner_question
    assert "costos directos" in action.owner_question
    assert action.required_evidence == "NONE hasta que el dueño elija foco operativo"
    assert "MARGEN_PRODUCTO" in action.operator_decision


def test_blocked_does_not_advance_and_preserves_stop_condition() -> None:
    state = _base_state(
        current_state=OperatorPhase.BLOCKED,
        next_question="Necesito una confirmación clara para continuar.",
        blocked_reason="owner_uncertain_about_business_semantics",
    )

    action = build_operator_next_action(state)

    _assert_complete_next_action(action)
    assert action.owner_question == state.next_question
    assert action.operator_decision == "no avanzar hasta resolver el bloqueo"
    assert action.stop_condition == "owner_uncertain_about_business_semantics"


def test_evidence_requested_asks_concrete_evidence() -> None:
    state = _base_state(current_state=OperatorPhase.EVIDENCE_REQUESTED)

    action = build_operator_next_action(state)

    _assert_complete_next_action(action)
    assert action.owner_question == state.next_question
    assert action.required_evidence == "ventas, costos, productos, periodo"
    assert "esperar evidencia" in action.operator_decision
    assert "no diagnosticar" in action.stop_condition


def test_unknown_state_still_returns_required_shape() -> None:
    state = _base_state(current_state=OperatorPhase.PROCESSING)

    action = build_operator_next_action(state)

    _assert_complete_next_action(action)
    assert action.operator_decision == "no inventar el próximo paso; pedir precisión al dueño"
