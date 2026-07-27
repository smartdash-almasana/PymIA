from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    _build_post_ficha_reply,
    run_anamnesis_turn,
)


def _complete_initial_profile(tenant_id: str, session_id: str) -> dict:
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id=tenant_id,
            session_id=session_id,
            message_text="vendo mucho pero no se si gano plata",
            previous_progressive_context=None,
        )
    )
    context = output.updated_progressive_context

    answers = [
        "Alejandro Arab",
        "dueno",
        "11 1234 5678",
        "alejandro@email.com",
        "SmartPyme Test SRL",
        "1",
        "ferreteria",
        "compro y revendo",
        "1,5",
        "2",
        "no tengo",
        "2",
        "2",
        "1",
        "1",
        "1",
        "1,3",
    ]

    for answer in answers:
        output = run_anamnesis_turn(
            AnamnesisTurnInput(
                tenant_id=tenant_id,
                session_id=session_id,
                message_text=answer,
                previous_progressive_context=context,
            )
        )
        context = output.updated_progressive_context

    return context


def test_post_ficha_routing_created_when_profile_completes() -> None:
    context = _complete_initial_profile("T_POSTFICHA_1", "S_POSTFICHA_1")
    assert "post_ficha_routing" in context
    routing = context["post_ficha_routing"]
    assert routing.get("intake_id")
    assert "intake_state" in routing
    assert "suggested_next_state" in routing
    assert "candidate_symptoms" in routing
    assert "evidence_requests" in routing
    assert "hypotheses" in routing


def test_post_ficha_routing_projection_is_lightweight() -> None:
    context = _complete_initial_profile("T_POSTFICHA_2", "S_POSTFICHA_2")
    routing = context["post_ficha_routing"]
    forbidden_keys = {
        "interrogation_result",
        "tank_selection_result",
        "audit_notes",
        "selected_tanks",
        "candidate_tanks",
        "suspended_tanks",
        "rejected_tanks",
    }
    assert not any(key in routing for key in forbidden_keys)


def test_post_ficha_routing_hypotheses_projection_is_lightweight() -> None:
    context = _complete_initial_profile("T_POSTFICHA_2B", "S_POSTFICHA_2B")
    routing = context["post_ficha_routing"]
    assert routing["hypotheses"]
    for hypothesis in routing["hypotheses"]:
        assert set(hypothesis) == {
            "hypothesis_id",
            "formulation",
            "domain",
            "candidate_pathology_codes",
            "candidate_formula_ids",
            "status",
        }
        assert isinstance(hypothesis["candidate_pathology_codes"], list)
        assert isinstance(hypothesis["candidate_formula_ids"], list)
        assert len(hypothesis["candidate_formula_ids"]) > 1
        assert "pathology_code" not in hypothesis
        assert "formula_id" not in hypothesis
        assert "candidate_formulas" not in hypothesis


def test_post_ficha_routing_evidence_requests_link_to_hypothesis() -> None:
    context = _complete_initial_profile("T_POSTFICHA_2C", "S_POSTFICHA_2C")
    routing = context["post_ficha_routing"]
    hypothesis_ids = {h["hypothesis_id"] for h in routing["hypotheses"]}
    assert hypothesis_ids
    assert routing["evidence_requests"]
    assert all(
        request.get("hypothesis_id") in hypothesis_ids
        for request in routing["evidence_requests"]
    )


def test_post_ficha_routing_evidence_requests_preserve_lightweight_contract() -> None:
    context = _complete_initial_profile("T_POSTFICHA_2D", "S_POSTFICHA_2D")
    requests = context["post_ficha_routing"]["evidence_requests"]
    assert requests
    assert sum(bool(request["blocks_analysis"]) for request in requests) <= 3
    for request in requests:
        assert "formula_id" in request
        assert isinstance(request["formula_ids"], list)
        assert isinstance(request["blocks_analysis"], bool)
        assert isinstance(request["required_fields"], list)


def test_post_ficha_reply_communicates_every_blocking_request() -> None:
    routing = {
        "evidence_requests": [
            {"description": "Ventas", "blocks_analysis": True},
            {"description": "Costos", "blocks_analysis": True},
            {"description": "Comisiones", "blocks_analysis": True},
            {"description": "Deseable", "blocks_analysis": False},
        ]
    }
    reply = _build_post_ficha_reply(routing)
    assert "Ventas" in reply
    assert "Costos" in reply
    assert "Comisiones" in reply
    assert "Deseable" not in reply


def test_post_ficha_routing_is_idempotent() -> None:
    context = _complete_initial_profile("T_POSTFICHA_3", "S_POSTFICHA_3")
    first_intake_id = context["post_ficha_routing"]["intake_id"]

    next_output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_POSTFICHA_3",
            session_id="S_POSTFICHA_3",
            message_text="fabrico y vendo",
            previous_progressive_context=context,
        )
    )
    assert next_output.updated_progressive_context["post_ficha_routing"]["intake_id"] == first_intake_id


def test_post_ficha_reply_requests_evidence_without_diagnosis() -> None:
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_POSTFICHA_4",
            session_id="S_POSTFICHA_4",
            message_text="vendo mucho pero no se si gano plata",
            previous_progressive_context=None,
        )
    )
    context = output.updated_progressive_context
    for answer in [
        "Alejandro Arab",
        "dueno",
        "11 1234 5678",
        "alejandro@email.com",
        "SmartPyme Test SRL",
        "1",
        "ferreteria",
        "compro y revendo",
        "1,5",
        "2",
        "no tengo",
        "2",
        "2",
        "1",
        "1",
        "1",
        "1,3",
    ]:
        output = run_anamnesis_turn(
            AnamnesisTurnInput(
                tenant_id="T_POSTFICHA_4",
                session_id="S_POSTFICHA_4",
                message_text=answer,
                previous_progressive_context=context,
            )
        )
        context = output.updated_progressive_context

    reply_lower = output.reply_text.lower()
    assert "evidencia" in reply_lower or "documentos" in reply_lower
    forbidden_terms = [
        "diagnóstico",
        "tu margen es",
        "la causa es",
        "confirmado",
        "resultado",
        "fórmula ejecutada",
    ]
    for term in forbidden_terms:
        assert term not in reply_lower
