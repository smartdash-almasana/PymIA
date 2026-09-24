from __future__ import annotations

from datetime import date
from io import BytesIO

from openpyxl import Workbook

from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    BLOCK_OWNER_CORRECTION_INVALID,
    STATUS_BLOCKED,
    STATUS_CONFIRMED,
    run_service_1_assisted_semantic_initial_v1,
    revise_service_1_assisted_semantic_decision_v1,
)
from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _ingestion() -> dict:
    stream = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ordenes"
    sheet.append(["fecha"])
    sheet.append([date(2026, 1, 1)])
    workbook.save(stream)

    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=stream.getvalue(),
        uploaded_filename="owner_correction.xlsx",
        include_all_sheets=True,
    )
    assert intake["status"] != "BLOCKED", intake
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    assert canonical["status"] != "BLOCKED", canonical
    return canonical["ingestion_output"]


def _initial() -> dict:
    return run_service_1_assisted_semantic_initial_v1(
        ingestion_output=_ingestion(),
        requested_capability=None,
        provider=build_service_1_deterministic_semantic_proposal_v1,
    )


def _v2_date_correction(*, entity: str = "work_order") -> dict[str, object]:
    return {
        "entity": entity,
        "object": None,
        "process": "service_delivery",
        "measure": None,
        "state": None,
        "grain": "work_order",
        "scope": "event",
        "time": "event_date",
        "identity": None,
        "relation": None,
        "unit": None,
        "aggregation": None,
        "confidence": 0.9,
    }


class _CorrectionAssistant:
    def __init__(self, coordinates: dict[str, object]) -> None:
        self.coordinates = coordinates
        self.semantic_provider_calls = 0

    def __call__(self, _payload: dict) -> dict:
        self.semantic_provider_calls += 1
        raise AssertionError("semantic classification must not rerun during correction/reentry")

    def assist(self, payload: dict) -> dict:
        assert payload["interaction_mode"] == "CORRECTION"
        return {
            "response_text": "Es la fecha de la orden de trabajo.",
            "suggested_compositional_semantic": self.coordinates,
            "suggestion_reason": "Owner supplied the business meaning.",
        }


def test_owner_correction_reenters_as_v2_and_requires_explicit_confirmation() -> None:
    initial = _initial()
    assert initial["status"] == "OWNER_DIALOGUE_REQUIRED"
    question = initial["owner_questions"][0]
    decision_id = question["decision_id"]

    assistant = _CorrectionAssistant(_v2_date_correction())
    app = Service1SemanticReceptionWebApplicationV1(semantic_provider=assistant)
    state = app.session("owner-correction-v2")
    state.ingestion_output = _ingestion()
    state.semantic_assistance_state = initial
    state.semantic_questions = [question]

    status, _ = app.semantic_assist(
        session_id="owner-correction-v2",
        fields={
            "decision_id": decision_id,
            "assistant_message": "Es la fecha de la orden de trabajo.",
            "correction_mode": "1",
        },
    )
    assert status == 200
    assert state.semantic_chat_suggestions[decision_id]["compositional_semantic"] == _v2_date_correction()

    status, _ = app.semantic_revise(
        session_id="owner-correction-v2",
        fields={"decision_id": decision_id},
    )
    assert status == 200
    revised = state.semantic_assistance_state
    assert revised["status"] == "OWNER_DIALOGUE_REQUIRED"
    assert revised["owner_evidence_packet"] is None
    assert revised["semantic_run"] is None
    proposal_ref = question["proposal_refs"][0]
    decision = next(item for item in revised["validated_packet"]["decisions"] if item["decision_id"] == proposal_ref)
    assert decision["semantic_role"] is None
    assert decision["variable_name"] is None
    assert decision["compositional_semantic"]["time"] == "event_date"
    assert revised["runtime_authorized"] is False

    status, _ = app.confirm_meanings(
        session_id="owner-correction-v2",
        fields={f"action_{decision_id}": "ACCEPT"},
    )
    assert status == 200
    assert state.last_review_result["status"] == STATUS_CONFIRMED
    events = state.last_review_result["owner_evidence_packet"]["owner_confirmation_events"]
    assert events and events[0]["confirmation_scope"] == "COMPOSITIONAL_SEMANTIC"
    assert events[0]["confirmed_role"] is None
    assert assistant.semantic_provider_calls == 0


def test_owner_correction_outside_v2_taxonomy_fails_closed() -> None:
    initial = _initial()
    question = initial["owner_questions"][0]
    revised = revise_service_1_assisted_semantic_decision_v1(
        previous_state=initial,
        decision_id=question["decision_id"],
        compositional_semantic=_v2_date_correction(entity="invented_entity"),
        owner_correction_text="Es una fecha de orden.",
    )
    assert revised["status"] == STATUS_BLOCKED
    assert revised["blocked_reason"] == BLOCK_OWNER_CORRECTION_INVALID
    assert revised["owner_evidence_packet"] is None
    assert revised["semantic_run"] is None

