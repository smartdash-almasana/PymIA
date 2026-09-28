from __future__ import annotations

from io import BytesIO
from openpyxl import Workbook

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    build_service_1_llm_semantic_context_v1,
    parse_service_1_llm_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    BLOCK_COLUMN_REF_NOT_FOUND,
    BLOCK_EVIDENCE_REF_NOT_FOUND,
    BLOCK_RELATIONSHIP_REF_NOT_FOUND,
    BLOCK_RELATIONSHIP_TYPE_INCOMPATIBLE,
    BLOCK_SEMANTIC_ROLE_NOT_ALLOWED,
    BLOCK_VARIABLE_NAME_INCOMPATIBLE,
    DECISION_IRRELEVANT_FOR_CAPABILITY,
    DECISION_MATERIAL_AMBIGUOUS,
    DECISION_MATERIAL_CONFIDENT,
    STATUS_BLOCKED,
    STATUS_READY,
    validate_service_1_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import build_service_1_workbook_profile_v1
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)


def _profile() -> dict:
    stream = BytesIO()
    workbook = Workbook()
    ventas = workbook.active
    ventas.title = "Ventas"
    ventas.append(["ProductoID", "Cantidad"])
    ventas.append(["P001", 1])
    ventas.append(["P002", 2])
    ventas.append(["P001", 3])
    productos = workbook.create_sheet("Productos")
    productos.append(["ProductoID", "Costo"])
    productos.append(["P001", 10])
    productos.append(["P002", 15])
    workbook.save(stream)

    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=stream.getvalue(),
        uploaded_filename="cafeteria.xlsx",
        include_all_sheets=True,
    )
    assert intake["status"] != "BLOCKED", intake
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    assert canonical["status"] != "BLOCKED", canonical
    profile = build_service_1_workbook_profile_v1(
        ingestion_output=canonical["ingestion_output"],
    )
    assert profile["status"] != "BLOCKED", profile
    return profile


def _context():
    profile = _profile()
    return build_service_1_llm_semantic_context_v1(
        case_id=str(profile.get("case_id") or ""),
        requested_capability="net_margin_real",
        workbook_profile=profile,
        deterministic_hypotheses=[
            {"semantic_role": "quantity", "variable_name": "volume_sold"},
            {"semantic_role": "unit_cost_candidate", "variable_name": "cost"},
            {"semantic_role": "product_identifier", "variable_name": "product_id"},
        ],
        allowed_semantic_roles=["quantity", "unit_cost_candidate", "product_identifier", "product_name"],
        capability_relevant_roles=["quantity", "unit_cost_candidate", "product_identifier"],
    )


def _payload() -> dict:
    return {
        "schema_version": "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1",
        "concept_proposals": [
            {
                "proposal_id": "p_quantity",
                "target_column_refs": ["Ventas.Cantidad"],
                "semantic_role": "quantity",
                "variable_name": "volume_sold",
                "confidence": 0.95,
                "rationale": "numeric quantity column",
                "evidence_refs": ["ev:column:Ventas.Cantidad:type"],
            },
            {
                "proposal_id": "p_cost",
                "target_column_refs": ["Productos.Costo"],
                "semantic_role": "unit_cost_candidate",
                "variable_name": "cost",
                "confidence": 0.60,
                "rationale": "cost-looking field",
                "evidence_refs": ["ev:column:Productos.Costo:type"],
            },
        ],
        "relationship_proposals": [
            {
                "relationship_id": "rel_product",
                "left_column_ref": "Ventas.ProductoID",
                "right_column_ref": "Productos.ProductoID",
                "relationship_type": "MANY_TO_ONE",
                "confidence": 0.98,
                "rationale": "structural key relation",
                "evidence_refs": [
                    "ev:relationship:Ventas.ProductoID->Productos.ProductoID:overlap"
                ],
            }
        ],
        "duplicate_semantics": [],
        "irrelevant_refs": [],
        "material_ambiguities": [],
    }


def _proposal(payload: dict | None = None):
    return parse_service_1_llm_semantic_proposal_v1(payload or _payload())


def test_sem3_validates_real_columns_evidence_roles_and_relationships() -> None:
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal())

    assert result["status"] == STATUS_READY
    decisions = {item["decision_id"]: item for item in result["decisions"]}
    assert decisions["p_quantity"]["status"] == DECISION_MATERIAL_CONFIDENT
    assert decisions["p_cost"]["status"] == DECISION_MATERIAL_AMBIGUOUS
    assert decisions["rel_product"]["status"] == DECISION_MATERIAL_CONFIDENT
    assert all(result[flag] is False for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    ))


def test_sem3_blocks_nonexistent_column_ref() -> None:
    payload = _payload()
    payload["concept_proposals"][0]["target_column_refs"] = ["Ventas.Inventada"]
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_COLUMN_REF_NOT_FOUND


def test_sem3_blocks_hallucinated_evidence_ref() -> None:
    payload = _payload()
    payload["concept_proposals"][0]["evidence_refs"] = ["ev:invented:not-real"]
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_EVIDENCE_REF_NOT_FOUND


def test_sem3_blocks_role_outside_allowed_ontology() -> None:
    payload = _payload()
    payload["concept_proposals"][0]["semantic_role"] = "magic_profit"
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_SEMANTIC_ROLE_NOT_ALLOWED


def test_sem3_blocks_incompatible_role_variable_pair() -> None:
    payload = _payload()
    payload["concept_proposals"][0]["variable_name"] = "cost"
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_VARIABLE_NAME_INCOMPATIBLE


def test_sem3_blocks_relationship_not_present_in_structural_profile() -> None:
    payload = _payload()
    payload["relationship_proposals"][0]["left_column_ref"] = "Ventas.Cantidad"
    payload["relationship_proposals"][0]["evidence_refs"] = ["ev:column:Ventas.Cantidad:type"]
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_RELATIONSHIP_REF_NOT_FOUND


def test_sem3_blocks_relationship_type_incompatible_with_structural_profile() -> None:
    payload = _payload()
    payload["relationship_proposals"][0]["relationship_type"] = "ONE_TO_ONE"
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_RELATIONSHIP_TYPE_INCOMPATIBLE


def test_sem3_marks_valid_but_capability_irrelevant_role_without_blocking() -> None:
    profile = _profile()
    context = build_service_1_llm_semantic_context_v1(
        case_id=str(profile.get("case_id") or ""),
        requested_capability="net_margin_real",
        workbook_profile=profile,
        deterministic_hypotheses=[
            {"semantic_role": "product_name", "variable_name": "product"},
        ],
        allowed_semantic_roles=["product_name"],
        capability_relevant_roles=[],
    )
    payload = {
        "schema_version": "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1",
        "concept_proposals": [
            {
                "proposal_id": "p_name",
                "target_column_refs": ["Productos.Costo"],
                "semantic_role": "product_name",
                "variable_name": "product",
                "confidence": 0.99,
                "rationale": None,
                "evidence_refs": ["ev:column:Productos.Costo:type"],
            }
        ],
        "relationship_proposals": [],
        "duplicate_semantics": [],
        "irrelevant_refs": [],
        "material_ambiguities": [],
    }
    result = validate_service_1_semantic_proposal_v1(context=context, proposal=_proposal(payload))
    assert result["status"] == STATUS_READY
    assert result["decisions"][0]["status"] == DECISION_MATERIAL_CONFIDENT


def test_sem3_explicit_irrelevant_real_ref_is_preserved_for_sem4() -> None:
    payload = _payload()
    payload["irrelevant_refs"] = ["Productos.Costo"]
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))
    decisions = {item["decision_id"]: item for item in result["decisions"]}
    assert decisions["irrelevant:Productos.Costo"]["status"] == DECISION_IRRELEVANT_FOR_CAPABILITY


def _v2_payload() -> dict:
    payload = _payload()
    payload["concept_proposals"] = [
        {
            "proposal_id": "p_v2_quantity",
            "target_column_refs": ["Ventas.Cantidad"],
            "semantic_role": None,
            "variable_name": None,
            "confidence": 0.95,
            "rationale": "quantity measured on a sales line",
            "evidence_refs": ["ev:column:Ventas.Cantidad:type"],
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
                "evidence": ["ev:column:Ventas.Cantidad:type"],
                "source": "LLM_C2_PROPOSAL",
            },
        }
    ]
    payload["relationship_proposals"] = []
    return payload


def test_f6_blocks_v2_descriptor_bound_to_different_real_column() -> None:
    from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
        BLOCK_COMPOSITIONAL_FIELD_REF_MISMATCH,
    )

    payload = _v2_payload()
    payload["concept_proposals"][0]["compositional_semantic"]["field_ref"] = "Productos.Costo"
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_COMPOSITIONAL_FIELD_REF_MISMATCH


def test_f6_blocks_v2_descriptor_whose_internal_evidence_differs_from_proposal_evidence() -> None:
    from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
        BLOCK_COMPOSITIONAL_EVIDENCE_MISMATCH,
    )

    payload = _v2_payload()
    payload["concept_proposals"][0]["compositional_semantic"]["evidence"] = []
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_COMPOSITIONAL_EVIDENCE_MISMATCH


def test_f6_blocks_relationship_supported_by_real_but_unrelated_evidence() -> None:
    from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
        BLOCK_RELATIONSHIP_EVIDENCE_MISMATCH,
    )

    payload = _payload()
    payload["relationship_proposals"][0]["evidence_refs"] = ["ev:column:Ventas.Cantidad:type"]
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(payload))

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_RELATIONSHIP_EVIDENCE_MISMATCH


def test_f6_accepts_v2_descriptor_only_when_ref_and_evidence_are_bound() -> None:
    result = validate_service_1_semantic_proposal_v1(context=_context(), proposal=_proposal(_v2_payload()))

    assert result["status"] == STATUS_READY, result
    decision = result["decisions"][0]
    assert decision["compositional_semantic"]["field_ref"] == "Ventas.Cantidad"
    assert decision["compositional_semantic"]["evidence"] == ("ev:column:Ventas.Cantidad:type",)


def test_semantic_context_allows_zero_legacy_roles_for_v2_governance() -> None:
    profile = _profile()
    context = build_service_1_llm_semantic_context_v1(
        case_id=str(profile.get("case_id") or ""),
        requested_capability=None,
        workbook_profile=profile,
        deterministic_hypotheses=(),
        allowed_semantic_roles=(),
        capability_relevant_roles=(),
    )

    payload = context.to_provider_payload()
    assert payload["allowed_semantic_roles"] == []
    assert payload["capability_relevant_roles"] == []
    assert payload["compositional_semantic_catalogs"]
    assert set(payload["compositional_semantic_catalogs"]) == {
        "entity",
        "object",
        "process",
        "measure",
        "state",
        "grain",
        "scope",
        "time",
        "identity",
        "relation",
        "unit",
        "aggregation",
    }
