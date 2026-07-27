import pytest

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


def test_reentry_without_explicit_semantic_confirmation_does_not_apply_projection():
    report = _blocked_owner_report()
    projected = project_semantic_confirmation_reentry_to_owner_facing(
        owner_answer={"answer_text": "Sí, primero margen y precios.", "metadata": {}},
        owner_facing_report=report,
        missing_keys=["own_price", "average_stock", "dso"],
        source_ref="owner_answer_reentry_test",
    )

    assert projected["semantic_confirmation_reentry_projection"] == {
        "applied": False,
        "reason": "missing_explicit_semantic_confirmation_status",
    }
    assert projected["next_questions"] == report["next_questions"]
    assert "semantic_request_projection" not in projected


def test_confirmed_semantic_reentry_projects_blocked_actionable_without_touching_evidence():
    report = _blocked_owner_report()
    projected = project_semantic_confirmation_reentry_to_owner_facing(
        owner_answer={
            "answer_text": "Sí, primero margen y precios.",
            "metadata": {
                "semantic_confirmation_status": "CONFIRMED_BY_OWNER",
                "proposed_interpretation": "revisar margen/precios por suba de tela",
                "related_missing_keys": ["own_price", "average_stock", "dso"],
            },
        },
        owner_facing_report=report,
        missing_keys=["own_price", "average_stock", "dso"],
        source_ref="owner_answer_reentry_test",
    )

    assert projected["status"] == report["status"]
    assert projected["evidence_used"] == report["evidence_used"]
    assert projected["missing_evidence"] == report["missing_evidence"]
    assert "findings" not in projected

    reentry_projection = projected["semantic_confirmation_reentry_projection"]
    assert reentry_projection["applied"] is True
    assert reentry_projection["confirmation_status"] == "CONFIRMED_BY_OWNER"
    assert reentry_projection["flow_status"] == "BLOCKED_ACTIONABLE"
    assert reentry_projection["requests_count"] == 3
    assert reentry_projection["does_resolve_structural_input"] is False
    assert reentry_projection["produces_findings"] is False

    semantic_projection = projected["semantic_request_projection"]
    assert semantic_projection["flow_status"] == "BLOCKED_ACTIONABLE"
    assert semantic_projection["requests_count"] == 3

    questions = "\n".join(projected["next_questions"])
    assert "precios de venta por producto/SKU" in questions
    assert "stock inicial y stock final" in questions
    assert "cliente, importe, fecha de factura o venta" in questions


def test_rejected_semantic_reentry_requests_reinterpretation_without_final_evidence_questions():
    report = _blocked_owner_report()
    projected = project_semantic_confirmation_reentry_to_owner_facing(
        owner_answer={
            "answer_text": "No, eso no es lo principal.",
            "metadata": {
                "semantic_confirmation_status": "REJECTED_BY_OWNER",
                "proposed_interpretation": "revisar margen/precios por suba de tela",
                "related_missing_keys": ["own_price", "average_stock", "dso"],
            },
        },
        owner_facing_report=report,
        missing_keys=["own_price", "average_stock", "dso"],
        source_ref="owner_answer_reentry_test",
    )

    assert projected["semantic_confirmation_reentry_projection"]["flow_status"] == "NEEDS_REINTERPRETATION"
    assert projected["semantic_request_projection"]["requests_count"] == 0
    questions = "\n".join(projected["next_questions"])
    assert "precios de venta por producto/SKU" not in questions
    steps = "\n".join(projected["next_steps"])
    assert "reformular la interpretación" in steps


def test_corrected_semantic_reentry_uses_corrected_interpretation_for_actionable_request():
    projected = project_semantic_confirmation_reentry_to_owner_facing(
        owner_answer={
            "answer_text": "No es margen, es cobranza.",
            "metadata": {
                "semantic_confirmation_status": "CORRECTED_BY_OWNER",
                "proposed_interpretation": "margen",
                "corrected_interpretation": "el problema principal es cobranzas",
                "related_missing_keys": ["dso"],
            },
        },
        owner_facing_report=_blocked_owner_report(),
        missing_keys=["dso"],
        source_ref="owner_answer_reentry_test",
    )

    assert projected["semantic_confirmation_reentry_projection"]["flow_status"] == "BLOCKED_ACTIONABLE"
    assert projected["semantic_confirmation_reentry_projection"]["requests_count"] == 1
    questions = "\n".join(projected["next_questions"])
    assert "cliente, importe, fecha de factura o venta" in questions


def test_explicit_semantic_confirmation_requires_non_empty_source_ref():
    with pytest.raises(ValueError, match="source_ref must be non-empty"):
        project_semantic_confirmation_reentry_to_owner_facing(
            owner_answer={
                "answer_text": "Sí.",
                "metadata": {
                    "semantic_confirmation_status": "CONFIRMED_BY_OWNER",
                    "proposed_interpretation": "revisar margen/precios por suba de tela",
                },
            },
            owner_facing_report=_blocked_owner_report(),
            missing_keys=["own_price"],
            source_ref="",
        )
