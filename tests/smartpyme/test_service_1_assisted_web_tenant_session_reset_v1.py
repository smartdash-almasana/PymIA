from pathlib import Path

from pymia.smartpyme.service_1_assisted_web_v1 import AssistedWebApplicationV1, ConsorcioCaseContextV1


def test_identity_change_replaces_tenant_sensitive_session_state(tmp_path: Path) -> None:
    app = AssistedWebApplicationV1(output_dir=tmp_path)
    session_id = "tenant-switch"
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id="tenant-a",
        cliente_id="cliente-a",
        owner_actor_id="owner-a",
        owner_actor_role="OWNER",
    )
    state = app.session(session_id)
    state.ingestion_output = {"case_id": "case-a"}
    state.semantic_questions = [{"decision_id": "q-a"}]
    state.semantic_answers = {"q-a": "ACCEPT"}
    state.semantic_assistance_state = {"case_id": "case-a"}
    state.semantic_chat_messages = {"q-a": [{"role": "owner", "text": "secret-a"}]}
    state.owner_unit_confirmation_events = [{"event_ref": "event-a"}]
    state.tenant_identity_contract = {"tenant_id": "tenant-a"}
    state.reconciliation_result = {"tenant_id": "tenant-a"}
    state.consorcio_case_context = ConsorcioCaseContextV1(
        case_id="case-a",
        consorcio_id="consorcio-a",
        consorcio_name="A",
        period="2026-08",
    )
    state.consorcios_results = {"case-a": {"tenant_id": "tenant-a"}}
    state.consorcios_radar_events = {"case-a": [{"tenant_id": "tenant-a"}]}
    state.selected_launch_review = "net_margin_real"
    state.selected_launch_reviews = ["net_margin_real"]
    state.pending_launch_reviews = ["sales_total"]
    state.multi_review_results = {"sales_total": {"tenant_id": "tenant-a"}}
    state.last_review_result = {"tenant_id": "tenant-a"}

    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id="tenant-b",
        cliente_id="cliente-b",
        owner_actor_id="owner-b",
        owner_actor_role="OWNER",
    )

    rebound = app.session(session_id)
    assert rebound is not state
    assert (rebound.tenant_id, rebound.cliente_id, rebound.owner_actor_id, rebound.owner_actor_role) == (
        "tenant-b",
        "cliente-b",
        "owner-b",
        "OWNER",
    )
    assert rebound.tenant_identity_contract is None
    assert rebound.ingestion_output is None
    assert rebound.semantic_questions == []
    assert rebound.semantic_answers == {}
    assert rebound.semantic_assistance_state is None
    assert rebound.semantic_chat_messages == {}
    assert rebound.owner_unit_confirmation_events == []
    assert rebound.reconciliation_result is None
    assert rebound.consorcio_case_context is None
    assert rebound.consorcios_results == {}
    assert rebound.consorcios_radar_events == {}
    assert rebound.selected_launch_review is None
    assert rebound.selected_launch_reviews == []
    assert rebound.pending_launch_reviews == []
    assert rebound.multi_review_results == {}
    assert rebound.last_review_result is None


def test_same_identity_revalidation_preserves_current_session_state(tmp_path: Path) -> None:
    app = AssistedWebApplicationV1(output_dir=tmp_path)
    session_id = "same-tenant"
    identity = dict(
        session_id=session_id,
        tenant_id="tenant-a",
        cliente_id="cliente-a",
        owner_actor_id="owner-a",
        owner_actor_role="OWNER",
    )
    app.bind_tenant_identity(**identity)
    state = app.session(session_id)
    state.ingestion_output = {"case_id": "case-a"}
    state.semantic_questions = [{"decision_id": "q-a"}]

    app.bind_tenant_identity(**identity)

    assert app.session(session_id) is state
    assert state.ingestion_output == {"case_id": "case-a"}
    assert state.semantic_questions == [{"decision_id": "q-a"}]
