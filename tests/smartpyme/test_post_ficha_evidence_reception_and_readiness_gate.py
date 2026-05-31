from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
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


def test_evidence_input_creates_evidence_record_linked_to_request() -> None:
    context = _complete_initial_profile("T_EVID_1", "S_EVID_1")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_1",
            session_id="S_EVID_1",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )

    records = output.updated_progressive_context.get("evidence_records", [])
    assert isinstance(records, list) and len(records) == 1
    row = records[0]
    assert row["intake_id"] == output.updated_progressive_context["post_ficha_routing"]["intake_id"]
    assert row["evidence_type"] == expected_type
    assert row["source_kind"] == "uploaded_file"
    assert row["source_ref"] == "ventas_abril.xlsx"
    assert row.get("request_id")


def test_evidence_input_updates_matching_request_to_received() -> None:
    context = _complete_initial_profile("T_EVID_2", "S_EVID_2")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_2",
            session_id="S_EVID_2",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )

    requests = output.updated_progressive_context["post_ficha_routing"]["evidence_requests"]
    match = [r for r in requests if r.get("evidence_type") == expected_type]
    assert match
    assert all(r.get("status") == "RECEIVED" for r in match)


def test_readiness_remains_needs_evidence_when_blocking_requests_missing() -> None:
    context = _complete_initial_profile("T_EVID_3", "S_EVID_3")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_3",
            session_id="S_EVID_3",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )

    readiness = output.updated_progressive_context["post_ficha_readiness"]
    assert readiness["readiness_state"] == "NEEDS_EVIDENCE"
    assert readiness["ready_for_analysis"] is False
    assert len(readiness["missing_evidence_types"]) >= 1


def test_readiness_becomes_ready_for_analysis_when_all_blocking_requests_received() -> None:
    context = _complete_initial_profile("T_EVID_4", "S_EVID_4")
    current_context = context
    requests = context["post_ficha_routing"]["evidence_requests"]
    for idx, req in enumerate(requests, start=1):
        evidence_type = req["evidence_type"]
        output = run_anamnesis_turn(
            AnamnesisTurnInput(
                tenant_id="T_EVID_4",
                session_id="S_EVID_4",
                message_text=f"EVIDENCE::uploaded_file::{evidence_type}::evidencia_{idx}.dat",
                previous_progressive_context=current_context,
            )
        )
        current_context = output.updated_progressive_context

    readiness = current_context["post_ficha_readiness"]
    assert readiness["readiness_state"] == "READY_FOR_ANALYSIS"
    assert readiness["ready_for_analysis"] is True
    assert readiness["missing_evidence_types"] == []


def test_evidence_reception_is_idempotent_for_same_evidence() -> None:
    context = _complete_initial_profile("T_EVID_5", "S_EVID_5")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    first = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_5",
            session_id="S_EVID_5",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )
    second = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_5",
            session_id="S_EVID_5",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=first.updated_progressive_context,
        )
    )

    assert len(first.updated_progressive_context["evidence_records"]) == 1
    assert len(second.updated_progressive_context["evidence_records"]) == 1
    assert (
        second.updated_progressive_context["evidence_records"][0]["evidence_id"]
        == first.updated_progressive_context["evidence_records"][0]["evidence_id"]
    )


def test_invalid_source_kind_is_rejected_fail_closed() -> None:
    context = _complete_initial_profile("T_EVID_6", "S_EVID_6")
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_6",
            session_id="S_EVID_6",
            message_text="EVIDENCE::magic_portal::sales_records::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )
    assert "source_kind" in output.reply_text


def test_missing_post_ficha_routing_is_rejected_fail_closed() -> None:
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_7",
            session_id="S_EVID_7",
            message_text="EVIDENCE::uploaded_file::sales_records::ventas_abril.xlsx",
            previous_progressive_context={},
        )
    )
    assert "post_ficha_routing" in output.reply_text


def test_reply_never_diagnoses_or_executes_analysis() -> None:
    context = _complete_initial_profile("T_EVID_8", "S_EVID_8")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_8",
            session_id="S_EVID_8",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )
    text = output.reply_text.lower()
    forbidden = [
        "diagnóstico",
        "tu margen es",
        "la causa es",
        "confirmado",
        "resultado",
        "fórmula ejecutada",
    ]
    for term in forbidden:
        assert term not in text


def test_no_heavy_intake_objects_are_persisted() -> None:
    context = _complete_initial_profile("T_EVID_9", "S_EVID_9")
    expected_type = context["post_ficha_routing"]["evidence_requests"][0]["evidence_type"]
    output = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id="T_EVID_9",
            session_id="S_EVID_9",
            message_text=f"EVIDENCE::uploaded_file::{expected_type}::ventas_abril.xlsx",
            previous_progressive_context=context,
        )
    )

    ctx = output.updated_progressive_context
    routing = ctx["post_ficha_routing"]
    assert "interrogation_result" not in routing
    assert "tank_selection_result" not in routing
    assert "audit_notes" not in routing
    assert "selected_tanks" not in routing
    assert "candidate_tanks" not in routing
    assert "suspended_tanks" not in routing
    assert "rejected_tanks" not in routing
