from pymia.smartpyme.anamnesis_fsm_integration import AnamnesisTurnInput, run_anamnesis_turn


def test_domain_core_v1_consumption_smoke_from_smartpyme_boundary() -> None:
    input_data = AnamnesisTurnInput(
        tenant_id='T_M18_SMOKE',
        session_id='S_M18_SMOKE',
        message_text='fabrico ropa y vendo por mayor',
        previous_progressive_context=None,
    )

    output = run_anamnesis_turn(input_data)

    assert output.updated_progressive_context is not None
    assert output.updated_progressive_context['tenant_id'] == 'T_M18_SMOKE'
    assert output.updated_progressive_context['phase'] == 'FICHA_PYME_INICIAL'
    assert output.updated_progressive_context['has_taxonomy'] is False
    assert output.updated_progressive_context['has_preliminary_taxonomy'] is True
    assert output.updated_progressive_context['has_confirmed_taxonomy'] is False
    assert output.updated_progressive_context['has_hypotheses'] is False
    assert output.updated_progressive_context['has_evidence_requests'] is False

    fsm_state = output.updated_progressive_context['fsm_state']
    assert fsm_state['profile_step'] == 'ASK_CONTACT_NAME'
    assert fsm_state['profile_data']['raw_first_message'] == 'fabrico ropa y vendo por mayor'
    assert fsm_state['taxonomy'] is None
    assert fsm_state['preliminary_taxonomy'] is not None
    assert fsm_state['preliminary_taxonomy']['status'] == 'PRELIMINARY'
    assert fsm_state['preliminary_taxonomy']['source'] == 'raw_first_message'
    assert fsm_state['hypotheses'] == []
    assert fsm_state['evidence_requests'] == []
