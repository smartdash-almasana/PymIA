from __future__ import annotations

import base64
import json
from io import BytesIO

from openpyxl import Workbook

from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_semantic_boundary_v1 import (
    INITIAL_REQUEST_SCHEMA,
    REENTRY_REQUEST_SCHEMA,
    RESPONSE_SCHEMA,
    Service1SemanticStateStoreV1,
    execute_service_1_semantic_initial_json_v1,
    execute_service_1_semantic_reentry_json_v1,
    parse_initial_request_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _ingestion() -> dict:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["Cantidad"])
    sheet.append([1])
    sheet.append([2])
    stream = BytesIO()
    workbook.save(stream)
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=stream.getvalue(), uploaded_filename="ventas.xlsx", include_all_sheets=True
    )
    return build_service_1_unconfirmed_canonical_ingestion_output_v1(owner_question_packet=intake)["ingestion_output"]


def test_initial_boundary_is_serialized_and_preserves_owner_dialogue() -> None:
    store = Service1SemanticStateStoreV1()
    packet = execute_service_1_semantic_initial_json_v1(
        {"schema_version": INITIAL_REQUEST_SCHEMA, "ingestion_output": _ingestion(), "requested_capability": None},
        provider=build_service_1_deterministic_semantic_proposal_v1,
        state_store=store,
    )
    assert packet["schema_version"] == RESPONSE_SCHEMA
    assert packet["status"] == "OWNER_DIALOGUE_REQUIRED"
    assert packet["semantic_state_ref"]
    assert packet["owner_questions"]
    json.dumps(packet)


def test_owner_reentry_returns_confirmed_binding_through_c2() -> None:
    store = Service1SemanticStateStoreV1()
    initial = execute_service_1_semantic_initial_json_v1(
        {"schema_version": INITIAL_REQUEST_SCHEMA, "ingestion_output": _ingestion()},
        provider=build_service_1_deterministic_semantic_proposal_v1,
        state_store=store,
    )
    confirmed = execute_service_1_semantic_reentry_json_v1(
        {
            "schema_version": REENTRY_REQUEST_SCHEMA,
            "semantic_state_ref": initial["semantic_state_ref"],
            "owner_responses": [
                {"decision_id": item["decision_id"], "action": "ACCEPT"}
                for item in initial["owner_questions"]
            ],
            "owner_actor_id": "owner-1",
            "owner_actor_role": "OWNER",
        },
        state_store=store,
    )
    assert confirmed["status"] == "CONFIRMED_BINDINGS"
    assert confirmed["confirmed_bindings"]["status"] == "CONFIRMED_BINDINGS"
    assert confirmed["semantic_state_ref"] is None


def test_invalid_boundary_request_fails_closed() -> None:
    _, blocked = parse_initial_request_v1({"schema_version": INITIAL_REQUEST_SCHEMA, "unknown": True})
    assert blocked is not None
    assert blocked["status"] == "BLOCKED"


def test_initial_boundary_can_canonically_ingest_uploaded_xlsx() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["Cantidad"])
    sheet.append([1])
    stream = BytesIO()
    workbook.save(stream)

    packet = execute_service_1_semantic_initial_json_v1(
        {
            "schema_version": INITIAL_REQUEST_SCHEMA,
            "uploaded_filename": "ventas.xlsx",
            "uploaded_xlsx_base64": base64.b64encode(stream.getvalue()).decode("ascii"),
        },
        provider=build_service_1_deterministic_semantic_proposal_v1,
        state_store=Service1SemanticStateStoreV1(),
    )

    assert packet["status"] == "OWNER_DIALOGUE_REQUIRED"
    assert packet["workbook_profile"]["status"] == "WORKBOOK_PROFILE_READY"
    assert packet["workbook_profile"]["sheet_names"] == ["Ventas"]
