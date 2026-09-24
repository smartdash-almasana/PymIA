from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook

import pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 as wiring
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    BLOCK_VALIDATOR_FAILED,
    STATUS_BLOCKED,
    STATUS_OWNER_DIALOGUE_REQUIRED,
    run_service_1_assisted_semantic_initial_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    BLOCK_EVIDENCE_REF_NOT_FOUND,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _canonical_ingestion() -> dict:
    stream = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["Cantidad"])
    sheet.append([1])
    sheet.append([2])
    workbook.save(stream)

    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=stream.getvalue(),
        uploaded_filename="zero_legacy_v2.xlsx",
        include_all_sheets=True,
    )
    assert intake.get("status") != "BLOCKED", intake
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    assert canonical.get("status") != "BLOCKED", canonical
    return canonical["ingestion_output"]


def _proposal(*, evidence_ref: str) -> dict:
    return {
        "schema_version": "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1",
        "concept_proposals": [
            {
                "proposal_id": "zero-legacy-v2:ventas-cantidad",
                "target_column_refs": ["Ventas.Cantidad"],
                "semantic_role": None,
                "variable_name": None,
                "confidence": 0.95,
                "rationale": "V2 compositional proposal without legacy semantic roles.",
                "evidence_refs": [evidence_ref],
                "compositional_semantic": {
                    "field_ref": "Ventas.Cantidad",
                    "entity": "sale",
                    "object": "product",
                    "process": "sale",
                    "measure": "quantity",
                    "state": None,
                    "grain": "line_item",
                    "scope": "line",
                    "time": None,
                    "identity": None,
                    "relation": None,
                    "unit": "units",
                    "aggregation": "sum",
                    "confidence": 0.95,
                    "evidence": [evidence_ref],
                    "source": "LLM_C2_PROPOSAL",
                },
            }
        ],
        "relationship_proposals": [],
        "duplicate_semantics": [],
        "irrelevant_refs": [],
        "material_ambiguities": [],
    }


def test_zero_legacy_roles_reaches_v2_provider_and_validator(monkeypatch) -> None:
    ingestion = _canonical_ingestion()
    provider_calls = 0

    monkeypatch.setattr(wiring, "_deterministic_hypotheses", lambda _bridge: ())

    def provider(payload: dict) -> dict:
        nonlocal provider_calls
        provider_calls += 1
        assert payload["deterministic_hypotheses"] == []
        assert payload["allowed_semantic_roles"] == []
        assert payload["capability_relevant_roles"] == []
        assert payload["compositional_semantic_catalogs"]
        return _proposal(evidence_ref="ev:column:Ventas.Cantidad:type")

    result = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability=None,
        provider=provider,
    )

    assert provider_calls == 1
    assert result.get("status") == STATUS_OWNER_DIALOGUE_REQUIRED, result
    validated = result.get("validated_packet") or {}
    assert validated.get("status") == "VALIDATED_SEMANTIC_PROPOSAL_READY", validated
    assert validated.get("decisions"), validated
    assert validated["decisions"][0]["compositional_semantic"]["field_ref"] == "Ventas.Cantidad"


def test_zero_legacy_roles_invalid_v2_still_fails_closed_in_validator(monkeypatch) -> None:
    ingestion = _canonical_ingestion()
    provider_calls = 0

    monkeypatch.setattr(wiring, "_deterministic_hypotheses", lambda _bridge: ())

    def provider(payload: dict) -> dict:
        nonlocal provider_calls
        provider_calls += 1
        assert payload["allowed_semantic_roles"] == []
        return _proposal(evidence_ref="ev:invented:not-real")

    result = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability=None,
        provider=provider,
    )

    assert provider_calls == 1
    assert result.get("status") == STATUS_BLOCKED, result
    assert result.get("blocked_reason") == BLOCK_VALIDATOR_FAILED, result
    assert result.get("detail") == BLOCK_EVIDENCE_REF_NOT_FOUND, result
