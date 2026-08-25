from __future__ import annotations

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


def _profile() -> dict:
    ingestion = {
        "case_id": "case-sem3",
        "filename": "cafeteria.xlsx",
        "source_file_ref": "cafeteria.xlsx",
        "workbook_context": {
            "case_id": "case-sem3",
            "source_artifact_ref": "artifact:case-sem3",
            "workbook_ref": "workbook:case-sem3",
            "ingestion_scope": "all_sheets",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        },
        "provenance": {
            "source_kind": "xlsx",
            "source_artifact_ref": "artifact:case-sem3",
            "source_file_ref": "workbook:case-sem3",
            "workbook_ref": "workbook:case-sem3",
            "filename": "cafeteria.xlsx",
            "sheet_names": ["Ventas", "Productos"],
            "sheet_refs": [],
        },
        "column_refs": [
            {
                "question_id": "q1",
                "field_id": "q1",
                "sheet_name": "Ventas",
                "column_name": "ProductoID",
                "normalized_column_name": "productoid",
            },
            {
                "question_id": "q2",
                "field_id": "q2",
                "sheet_name": "Ventas",
                "column_name": "Cantidad",
                "normalized_column_name": "cantidad",
            },
            {
                "question_id": "q3",
                "field_id": "q3",
                "sheet_name": "Productos",
                "column_name": "ProductoID",
                "normalized_column_name": "productoid",
            },
            {
                "question_id": "q4",
                "field_id": "q4",
                "sheet_name": "Productos",
                "column_name": "Costo",
                "normalized_column_name": "costo",
            },
        ],
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["ProductoID", "Cantidad"],
                "normalized_headers": ["productoid", "cantidad"],
                "rows": [
                    {"productoid": "P001", "cantidad": "1"},
                    {"productoid": "P002", "cantidad": "2"},
                    {"productoid": "P001", "cantidad": "3"},
                ],
            },
            {
                "status": "OK",
                "sheet_name": "Productos",
                "headers": ["ProductoID", "Costo"],
                "normalized_headers": ["productoid", "costo"],
                "rows": [
                    {"productoid": "P001", "costo": "10"},
                    {"productoid": "P002", "costo": "15"},
                ],
            },
        ],
        "runtime_authorized": False,
    }
    profile = build_service_1_workbook_profile_v1(ingestion_output=ingestion)
    assert profile["status"] != "BLOCKED"
    return profile


def _context():
    return build_service_1_llm_semantic_context_v1(
        case_id="case-sem3",
        requested_capability="net_margin_real",
        workbook_profile=_profile(),
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
    context = build_service_1_llm_semantic_context_v1(
        case_id="case-sem3",
        requested_capability="net_margin_real",
        workbook_profile=_profile(),
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
