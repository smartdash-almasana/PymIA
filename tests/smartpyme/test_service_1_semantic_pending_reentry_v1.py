from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)


def test_semantic_blocked_page_does_not_claim_owner_review_is_pending() -> None:
    app = Service1SemanticReceptionWebApplicationV1()
    page = app._semantic_blocked_page("BLOCK_SEMANTIC_COORDINATE_INVALID")
    assert "Interpretación bloqueada" in page
    assert "No pude completar la lectura del negocio" in page
    assert "No hay una respuesta tuya pendiente" in page
    assert 'href="/review-pending"' not in page
    assert "BLOCK_SEMANTIC_COORDINATE_INVALID" in page


def test_review_pending_reenters_same_in_session_question() -> None:
    app = Service1SemanticReceptionWebApplicationV1()
    state = app.session("pending-reentry")
    state.ingestion_output = {"case_id": "case-pending"}
    state.semantic_assistance_state = {"status": "OWNER_DIALOGUE_REQUIRED"}
    state.semantic_questions = [
        {
            "decision_id": "dialogue:atomic:margin-labor",
            "proposal_refs": ["proposal:margin-labor"],
            "column_refs": ["ORDENES_TRABAJO.margen_mano_obra"],
            "relationship_refs": [],
            "presentation_text": "Revisá margen_mano_obra.",
            "materiality_reason": "El significado es material para el análisis.",
        }
    ]

    status, page = app.review_pending(session_id="pending-reentry")

    assert status == 200
    assert state.ingestion_output == {"case_id": "case-pending"}
    assert state.semantic_questions[0]["decision_id"] == "dialogue:atomic:margin-labor"
    assert "margen_mano_obra" in page
