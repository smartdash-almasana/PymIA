from pymia.contracts.owner_semantic_confirmation import OwnerSemanticConfirmationGate
from pymia.smartpyme.owner_confirmed_semantic_request_flow import (
    build_owner_confirmed_semantic_request_flow,
)
from pymia.smartpyme.owner_confirmed_semantic_request_projection import (
    project_confirmed_semantic_requests_to_owner_facing,
)


def test_assisted_simulated_pilot_002_bis_projects_blocked_actionable_owner_report():
    owner_report = {
        "status": "BLOCKED",
        "delivery_status": "BLOCKED",
        "operational_status": "pending_data",
        "summary": "Falta evidencia para avanzar.",
        "blocked_message": "Falta evidencia para avanzar al resultado operativo entregable.",
        "evidence_used": [],
        "missing_evidence": ["own_price", "average_stock", "dso", "taxes"],
        "next_questions": ["¿Podés aportar el dato, archivo o aclaración que falta para avanzar?"],
        "next_steps": [],
        "limit_warnings": ["Estado bloqueado o incompleto: falta evidencia para avanzar."],
    }

    gate = OwnerSemanticConfirmationGate(
        gate_id="gate_002_bis_margin_prices",
        target_type="SEMANTIC_INTERPRETATION",
        proposed_interpretation=(
            "revisar margen/precios por suba de tela y cambios de precio durante el período"
        ),
        confirmation_question="¿Confirmás que primero revisemos margen y precios?",
        status="CONFIRMED_BY_OWNER",
        owner_response_text="Sí, primero margen y precios.",
        related_missing_keys=["own_price", "average_stock", "dso"],
        source_ref="assisted_simulated_pilot_002_bis",
    )

    flow_result = build_owner_confirmed_semantic_request_flow(
        confirmation_gate=gate,
        missing_keys=["own_price", "average_stock", "dso"],
        source_ref="assisted_simulated_pilot_002_bis",
    )

    assert flow_result.flow_status == "BLOCKED_ACTIONABLE"
    assert len(flow_result.semantic_evidence_requests) == 3
    assert all(
        request.does_resolve_structural_input is False
        for request in flow_result.semantic_evidence_requests
    )

    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=owner_report,
        flow_result=flow_result,
    )

    assert projected["status"] == owner_report["status"]
    assert projected["delivery_status"] == owner_report["delivery_status"]
    assert projected["operational_status"] == owner_report["operational_status"]
    assert projected["evidence_used"] == owner_report["evidence_used"]
    assert projected["missing_evidence"] == owner_report["missing_evidence"]
    assert "findings" not in projected

    projection = projected["semantic_request_projection"]
    assert projection["flow_status"] == "BLOCKED_ACTIONABLE"
    assert projection["requests_count"] == 3
    assert projection["does_resolve_structural_input"] is False
    assert projection["produces_findings"] is False

    questions = "\n".join(projected["next_questions"])
    assert "precios de venta por producto/SKU" in questions
    assert "stock inicial y stock final" in questions
    assert "cliente, importe, fecha de factura o venta" in questions

    warnings = "\n".join(projected["limit_warnings"])
    assert "confirmada o corregida por el dueño" in warnings
    assert "no reemplaza evidencia estructural" in warnings

    steps = "\n".join(projected["next_steps"])
    assert "eje semántico confirmado" in steps
    assert "evidencia concreta" in steps
    assert "no habilita diagnóstico" in steps
