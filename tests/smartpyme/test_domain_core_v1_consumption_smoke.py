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
    assert output.updated_progressive_context['phase'] == 'ANAMNESIS_TAXONOMIA'
    assert output.updated_progressive_context['has_taxonomy'] is True

    fsm_state = output.updated_progressive_context['fsm_state']
    taxonomy = fsm_state['taxonomy']
    assert taxonomy is not None
    assert taxonomy['organism_type'] == 'textil'
    assert taxonomy['jurisdiction'] == 'AR'
