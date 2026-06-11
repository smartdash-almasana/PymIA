from pymia.faithful_operator import (
    OperatorPhase,
    OperatorState,
    build_confirmed_candidate_next_actions,
    handle_owner_confirmation,
    run_local_operator_flow,
)


def _pending_state() -> OperatorState:
    return OperatorState(
        tenant_id="tenant_demo",
        intake_id="intake_demo_001",
        owner_message="Vendo más pero no me queda plata.",
        current_state=OperatorPhase.OWNER_CONFIRMATION_PENDING,
        problem_summary="Vendo más pero no me queda plata.",
        evidence_requested=["ventas", "costos", "productos", "periodo"],
        next_question="¿Estas columnas representan ventas, costos, productos y período?",
        evidence_id="evidence_demo",
        evidence_hash="evidence_hash_demo",
        run_id="run_demo",
        output_hash="output_hash_demo",
        candidate_response="Resultado candidato con límites.",
        limit="No declara verdad final sin confirmación del dueño.",
        owner_confirmation_status="pending",
    )


def test_owner_confirmation_closes_candidate_without_final_diagnosis() -> None:
    state = handle_owner_confirmation(_pending_state(), "Sí, correcto, representa mis ventas y costos.")

    assert state.current_state == OperatorPhase.CLOSED
    assert state.owner_confirmation_status == "candidate_confirmed"
    assert state.evidence_id == "evidence_demo"
    assert state.run_id == "run_demo"
    assert state.output_hash == "output_hash_demo"
    assert "diagnóstico final automático" in state.next_question


def test_owner_correction_returns_to_evidence_request() -> None:
    state = handle_owner_confirmation(_pending_state(), "No representa costos directos, mezcla gastos fijos.")

    assert state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert state.owner_confirmation_status == "correction_requested"
    assert "correccion_semantica" in state.evidence_requested
    assert state.run_id == "run_demo"


def test_owner_uncertainty_blocks_honestly() -> None:
    state = handle_owner_confirmation(_pending_state(), "No se, no estoy seguro.")

    assert state.current_state == OperatorPhase.BLOCKED
    assert state.owner_confirmation_status == "blocked_by_owner_uncertainty"
    assert state.blocked_reason == "owner_uncertain_about_business_semantics"


def test_new_evidence_preserves_traceability_and_requests_reprocess() -> None:
    state = handle_owner_confirmation(
        _pending_state(),
        "Te paso otro Excel con costos corregidos.",
        new_evidence_path="costos_corregidos.xlsx",
    )

    assert state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert state.owner_confirmation_status == "new_evidence_provided"
    assert state.evidence_path == "costos_corregidos.xlsx"
    assert state.evidence_id == "evidence_demo"
    assert state.run_id == "run_demo"
    assert state.output_hash == "output_hash_demo"


def test_confirmation_before_candidate_blocks() -> None:
    state = _pending_state().model_copy(update={"current_state": OperatorPhase.EVIDENCE_REQUESTED})
    result = handle_owner_confirmation(state, "Sí")

    assert result.current_state == OperatorPhase.BLOCKED
    assert result.blocked_reason == "confirmation_not_expected"


def _confirmed_state() -> OperatorState:
    return handle_owner_confirmation(_pending_state(), "Sí, correcto.")


def test_confirmed_candidate_next_actions_are_operational_and_traceable() -> None:
    response = build_confirmed_candidate_next_actions(_confirmed_state())

    assert "Caso: Vendo más pero no me queda plata." in response
    assert "Evidencia usada: evidence_demo" in response
    assert "Run ID: run_demo" in response
    assert "Output hash: output_hash_demo" in response
    assert "Límite:" in response
    assert "Pregunta de seguimiento:" in response


def test_confirmed_candidate_next_actions_have_exactly_three_steps() -> None:
    response = build_confirmed_candidate_next_actions(_confirmed_state())

    assert response.count("\n1. ") == 1
    assert response.count("\n2. ") == 1
    assert response.count("\n3. ") == 1
    assert "\n4. " not in response


def test_confirmed_candidate_next_actions_block_without_confirmation() -> None:
    response = build_confirmed_candidate_next_actions(_pending_state())

    assert response.startswith("BLOQUEADO")
    assert "candidato confirmado" in response


def test_confirmed_candidate_next_actions_do_not_overpromise() -> None:
    response = build_confirmed_candidate_next_actions(_confirmed_state()).lower()

    forbidden_terms = ["causa definitiva", "automatizado", "garantizado"]
    for term in forbidden_terms:
        assert term not in response
    assert "no declara verdad final" in response


def test_local_operator_flow_without_excel_stops_at_evidence_request() -> None:
    result = run_local_operator_flow("Vendo más pero no me queda plata.", tenant_id="tenant_demo")

    assert result["status"] == OperatorPhase.EVIDENCE_REQUESTED.value
    assert len(result["states"]) == 1
    assert "evidencia mínima" in result["response"]


def test_local_operator_flow_with_blank_message_blocks() -> None:
    result = run_local_operator_flow("   ", tenant_id="tenant_demo")

    assert result["status"] == OperatorPhase.BLOCKED.value
    assert result["state"].blocked_reason == "empty_owner_message"


def test_local_operator_flow_with_missing_excel_blocks_after_evidence_request() -> None:
    result = run_local_operator_flow(
        "Vendo más pero no me queda plata.",
        excel_path="archivo_inexistente.xlsx",
        tenant_id="tenant_demo",
    )

    assert result["status"] == OperatorPhase.BLOCKED.value
    assert len(result["states"]) == 2
    assert result["state"].blocked_reason == "evidence_file_not_found"
