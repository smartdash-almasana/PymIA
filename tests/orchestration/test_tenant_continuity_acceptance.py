from __future__ import annotations

from pathlib import Path

from pymia.orchestration.graph import run_pymia_graph
from pymia.orchestration.state import PymIAEvent
from pymia.orchestration.state_storage import (
    find_conversations_by_tenant,
    load_state,
)


def test_tenant_continuity_acceptance(tmp_path: Path) -> None:
    tenant_a = "tenant_a_continuity"
    tenant_b = "tenant_b_continuity"
    chat_a = "chat_a01"
    chat_b = "chat_b01"

    # --- Turno 1: tenant_a inicia una demanda operativa ---
    response_a1 = run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_a,
            chat_id=chat_a,
            conversation_id="conv_a01",
            text="fabrico ropa y vendo por mayor",
        ),
        base_dir=tmp_path,
    )
    assert response_a1, "tenant_a debe recibir respuesta en turno 1"

    state_a1 = load_state(tenant_a, chat_a, tmp_path)
    assert state_a1 is not None, "tenant_a debe tener estado persistido tras turno 1"
    assert state_a1.progressive_context, "tenant_a debe tener progressive_context tras turno 1"
    assert state_a1.phase != "FAILED", "tenant_a no debe fallar en turno 1"

    # --- Turno 2: tenant_b inicia una demanda independiente ---
    response_b1 = run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_b,
            chat_id=chat_b,
            conversation_id="conv_b01",
            text="revisame los proveedores duplicados",
        ),
        base_dir=tmp_path,
    )
    assert response_b1, "tenant_b debe recibir respuesta en turno 1"

    state_b1 = load_state(tenant_b, chat_b, tmp_path)
    assert state_b1 is not None, "tenant_b debe tener estado persistido tras turno 1"
    assert state_b1.progressive_context, "tenant_b debe tener progressive_context tras turno 1"
    assert state_b1.phase != "FAILED", "tenant_b no debe fallar en turno 1"

    # --- Verificación 1: progressive_context de tenant_a y tenant_b son independientes ---
    assert state_a1.progressive_context != state_b1.progressive_context, (
        "tenant_a y tenant_b deben tener progressive_context diferentes "
        "(independencia de contexto)"
    )

    # --- Turno 3: tenant_a vuelve con segunda interacción ---
    state_a_before = load_state(tenant_a, chat_a, tmp_path)
    assert state_a_before is not None
    previous_context = dict(state_a_before.progressive_context)

    response_a2 = run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_a,
            chat_id=chat_a,
            conversation_id="conv_a01",
            text="mi nombre es Juan",
        ),
        base_dir=tmp_path,
    )
    assert response_a2, "tenant_a debe recibir respuesta en turno 2"

    state_a2 = load_state(tenant_a, chat_a, tmp_path)
    assert state_a2 is not None, "tenant_a debe tener estado persistido tras turno 2"
    assert state_a2.phase != "FAILED", "tenant_a no debe fallar en turno 2"

    # --- Verificación 2: tenant_a recuperó contexto previo (continuidad) ---
    assert state_a2.progressive_context, (
        "tenant_a debe mantener progressive_context tras segunda interacción"
    )
    assert state_a2.progressive_context != previous_context, (
        "progressive_context de tenant_a debe evolucionar "
        "(no ser idéntico al del turno 1)"
    )

    # --- Verificación 3: storage de tenant_a y tenant_b no se mezclan ---
    convs_a = find_conversations_by_tenant(tenant_a, tmp_path)
    convs_b = find_conversations_by_tenant(tenant_b, tmp_path)

    assert len(convs_a) > 0, "tenant_a debe tener conversaciones registradas"
    assert len(convs_b) > 0, "tenant_b debe tener conversaciones registradas"

    for conv in convs_a:
        assert conv["chat_id"] == chat_a, (
            f"Conversación de tenant_a no debe referenciar chat de tenant_b "
            f"(got chat_id={conv['chat_id']})"
        )

    for conv in convs_b:
        assert conv["chat_id"] == chat_b, (
            f"Conversación de tenant_b no debe referenciar chat de tenant_a "
            f"(got chat_id={conv['chat_id']})"
        )
