from __future__ import annotations

from pymia.smartpyme.owner_semantic_gate_builder import (
    build_pending_owner_semantic_confirmation_gate_from_translation,
)
from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle
from pymia.smartpyme.owner_answers_capture import (
    capture_owner_answers_from_structured_payload,
)
from pymia.smartpyme.owner_semantic_confirmation_reentry_projection import (
    project_semantic_confirmation_reentry_to_owner_facing,
)


def _blocked_owner_report() -> dict:
    return {
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


def test_owner_semantic_confirmation_loop_sandbox() -> None:
    # 1. Crear structured_semantic_translation_payload
    payload = {
        "proposed_interpretation": "revisar margen/precios por suba de tela",
        "target_type": "SEMANTIC_INTERPRETATION",
        "source_ref": "semantic_loop_sandbox",
        "related_missing_keys": ["own_price", "average_stock", "dso"],
    }

    # 2. Builder crea gate pendiente
    gate = build_pending_owner_semantic_confirmation_gate_from_translation(payload)
    assert gate.status == "PENDING_OWNER_CONFIRMATION"

    # 3. Proyectar gate.to_owner_question_metadata()
    question_metadata = gate.to_owner_question_metadata()
    assert question_metadata["expects_semantic_confirmation"] is True
    assert "semantic_confirmation_status" not in question_metadata

    # 4. Crear OwnerQuestionsBundle
    questions_bundle = build_owner_questions_bundle(
        source_ref="semantic_loop_sandbox",
        next_questions=[gate.confirmation_question],
        metadata=question_metadata,
    )
    assert len(questions_bundle.questions) == 1
    question = questions_bundle.questions[0]

    # 5. Simular respuesta del dueño
    answers_payload = [
        {
            "question_id": question.question_id,
            "answer_text": "Sí, primero margen y precios.",
            "metadata": {
                "semantic_confirmation_status": "CONFIRMED_BY_OWNER",
                "proposed_interpretation": "revisar margen/precios por suba de tela",
                "related_missing_keys": ["own_price", "average_stock", "dso"],
                "gate_id": gate.gate_id,
                "target_type": gate.target_type,
                "semantic_confirmation_source_ref": "semantic_loop_sandbox",
            },
        }
    ]

    # 6. Capturar OwnerAnswersBundle
    answers_bundle = capture_owner_answers_from_structured_payload(
        questions_bundle=questions_bundle,
        answers_payload=answers_payload,
        source_ref="semantic_loop_sandbox",
    )
    assert len(answers_bundle.answers) == 1
    owner_answer = answers_bundle.answers[0]

    # 7. Pasar la primera respuesta a project_semantic_confirmation_reentry_to_owner_facing(...)
    report = _blocked_owner_report()
    projected = project_semantic_confirmation_reentry_to_owner_facing(
        owner_answer=owner_answer,
        owner_facing_report=report,
        missing_keys=["own_price", "average_stock", "dso"],
        source_ref="semantic_loop_sandbox",
    )

    # 8. Verificar
    reentry_projection = projected["semantic_confirmation_reentry_projection"]
    assert reentry_projection["applied"] is True
    assert reentry_projection["flow_status"] == "BLOCKED_ACTIONABLE"
    assert reentry_projection["requests_count"] == 3
    assert reentry_projection["does_resolve_structural_input"] is False
    assert reentry_projection["produces_findings"] is False

    # Verificar que next_questions contiene los textos de los pedidos semánticos
    questions_str = "\n".join(projected["next_questions"])
    assert "precios de venta por producto/SKU" in questions_str
    assert "stock inicial y stock final" in questions_str
    assert "cliente, importe, fecha de factura o venta" in questions_str

    # Verificar que no hay findings
    assert "findings" not in projected

    # Verificar que evidence_used no cambia
    assert projected["evidence_used"] == report["evidence_used"]

    # Verificar que missing_evidence no cambia
    assert projected["missing_evidence"] == report["missing_evidence"]
