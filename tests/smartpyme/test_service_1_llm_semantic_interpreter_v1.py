from __future__ import annotations

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    PROPOSAL_SCHEMA_VERSION,
    Service1LLMSemanticContractErrorV1,
    build_service_1_llm_semantic_context_v1,
    parse_service_1_llm_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_llm_semantic_interpreter_v1 import (
    BLOCK_PROVIDER_FAILED,
    BLOCK_PROVIDER_OUTPUT_INVALID,
    BLOCK_PROVIDER_OUTPUT_NOT_MAPPING,
    STATUS_BLOCKED,
    STATUS_READY,
    interpret_service_1_semantics_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    build_service_1_workbook_profile_v1,
)


def _profile() -> dict:
    ingestion_output = {
        "case_id": "case-sem2",
        "filename": "cafeteria.xlsx",
        "source_file_ref": "cafeteria.xlsx",
        "workbook_context": {
            "case_id": "case-sem2",
            "source_artifact_ref": "artifact:case-sem2",
            "workbook_ref": "workbook:case-sem2",
            "ingestion_scope": "all_sheets",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        },
        "provenance": {
            "source_kind": "xlsx",
            "source_artifact_ref": "artifact:case-sem2",
            "source_file_ref": "workbook:case-sem2",
            "workbook_ref": "workbook:case-sem2",
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
        ],
        "normalized_tables": [
            {
                "schema_version": "1.0",
                "service_name": "SERVICE_1",
                "status": "OK",
                "source_kind": "xlsx",
                "source_path": "cafeteria.xlsx",
                "sheet_name": "Ventas",
                "headers": ["ProductoID", "Cantidad"],
                "normalized_headers": ["productoid", "cantidad"],
                "rows": [
                    {"productoid": "P001", "cantidad": "1"},
                    {"productoid": "P002", "cantidad": "2"},
                    {"productoid": "P001", "cantidad": "3"},
                ],
                "header_row_number": 1,
                "source_row_numbers": [2, 3, 4],
                "row_count": 3,
                "column_count": 2,
                "warnings": [],
                "blocking_errors": [],
                "runtime_authorized": False,
            },
            {
                "schema_version": "1.0",
                "service_name": "SERVICE_1",
                "status": "OK",
                "source_kind": "xlsx",
                "source_path": "cafeteria.xlsx",
                "sheet_name": "Productos",
                "headers": ["ProductoID"],
                "normalized_headers": ["productoid"],
                "rows": [
                    {"productoid": "P001"},
                    {"productoid": "P002"},
                ],
                "header_row_number": 1,
                "source_row_numbers": [2, 3],
                "row_count": 2,
                "column_count": 1,
                "warnings": [],
                "blocking_errors": [],
                "runtime_authorized": False,
            },
        ],
        "runtime_authorized": False,
    }
    return build_service_1_workbook_profile_v1(ingestion_output=ingestion_output)


def _context():
    return build_service_1_llm_semantic_context_v1(
        case_id="case-sem2",
        requested_capability="net_margin_real",
        workbook_profile=_profile(),
        deterministic_hypotheses=(
            {
                "column_ref": "Ventas.Cantidad",
                "candidate_roles": ["quantity"],
                "confidence": 0.95,
            },
        ),
        allowed_semantic_roles=("quantity", "product_id", "unit_sale_price"),
        capability_relevant_roles=("quantity", "product_id"),
        compatible_tenant_memory_hints=(),
    )


def _valid_payload() -> dict:
    return {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "concept_proposals": [
            {
                "proposal_id": "p-quantity",
                "target_column_refs": ["Ventas.Cantidad"],
                "semantic_role": "quantity",
                "variable_name": "volume_sold",
                "confidence": 0.97,
                "rationale": "Numeric transaction quantity.",
                "evidence_refs": ["ev:column:Ventas.Cantidad:type"],
            }
        ],
        "relationship_proposals": [
            {
                "relationship_id": "r-product",
                "left_column_ref": "Ventas.ProductoID",
                "right_column_ref": "Productos.ProductoID",
                "relationship_type": "MANY_TO_ONE",
                "confidence": 0.99,
                "rationale": "Transaction values map to unique product ids.",
                "evidence_refs": [
                    "ev:relationship:Ventas.ProductoID->Productos.ProductoID:overlap"
                ],
            }
        ],
        "duplicate_semantics": [],
        "irrelevant_refs": [],
        "material_ambiguities": [],
    }


def test_sem2_provider_neutral_adapter_accepts_closed_structured_proposal() -> None:
    captured = {}

    def provider(payload):
        captured.update(payload)
        return _valid_payload()

    result = interpret_service_1_semantics_v1(context=_context(), provider=provider)

    assert result["status"] == STATUS_READY
    assert result["proposal"].concept_proposals[0].semantic_role == "quantity"
    assert result["proposal"].relationship_proposals[0].relationship_type == "MANY_TO_ONE"
    assert captured["case_id"] == "case-sem2"
    assert "workbook_profile" in captured
    assert "evidence_registry" in captured
    assert all(result[flag] is False for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    ))


def test_sem2_context_supports_workbook_first_without_fake_capability() -> None:
    context = build_service_1_llm_semantic_context_v1(
        case_id="case-sem2",
        requested_capability=None,
        workbook_profile=_profile(),
        deterministic_hypotheses=(
            {
                "column_ref": "Ventas.Cantidad",
                "candidate_roles": ["quantity"],
                "confidence": 0.95,
            },
        ),
        allowed_semantic_roles=("quantity", "product_id", "unit_sale_price"),
        capability_relevant_roles=("quantity", "product_id", "unit_sale_price"),
        compatible_tenant_memory_hints=(),
    )

    result = interpret_service_1_semantics_v1(
        context=context,
        provider=lambda payload: _valid_payload(),
    )

    assert context.requested_capability is None
    assert context.to_provider_payload()["requested_capability"] is None
    assert all(
        result[flag] is False
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    )


def test_sem2_contract_rejects_forbidden_authority_field_anywhere() -> None:
    payload = _valid_payload()
    payload["concept_proposals"][0]["runtime_authorized"] = True
    try:
        parse_service_1_llm_semantic_proposal_v1(payload)
    except Service1LLMSemanticContractErrorV1 as exc:
        assert exc.code == "FORBIDDEN_AUTHORITY_FIELD"
    else:
        raise AssertionError("authority field must fail closed")


def test_sem2_contract_rejects_unknown_field() -> None:
    payload = _valid_payload()
    payload["concept_proposals"][0]["surprise"] = "not allowed"
    result = interpret_service_1_semantics_v1(context=_context(), provider=lambda _ctx: payload)
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_PROVIDER_OUTPUT_INVALID
    assert result["detail"]["contract_error"] == "UNKNOWN_FIELD"


def test_sem2_does_not_validate_evidence_existence_yet() -> None:
    payload = _valid_payload()
    payload["concept_proposals"][0]["evidence_refs"] = ["ev:invented:not-real"]
    result = interpret_service_1_semantics_v1(context=_context(), provider=lambda _ctx: payload)
    assert result["status"] == STATUS_READY
    assert result["proposal"].concept_proposals[0].evidence_refs == ("ev:invented:not-real",)


def test_sem2_provider_exception_fails_closed_without_exception_text() -> None:
    def provider(_payload):
        raise RuntimeError("secret provider details")

    result = interpret_service_1_semantics_v1(context=_context(), provider=provider)
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_PROVIDER_FAILED
    assert result["detail"] == "RuntimeError"
    assert "secret" not in str(result)


def test_sem2_provider_non_mapping_fails_closed() -> None:
    result = interpret_service_1_semantics_v1(context=_context(), provider=lambda _ctx: "text")
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_PROVIDER_OUTPUT_NOT_MAPPING


def test_sem2_context_rejects_authority_inside_memory_hint() -> None:
    try:
        build_service_1_llm_semantic_context_v1(
            case_id="case-sem2",
            requested_capability="net_margin_real",
            workbook_profile=_profile(),
            deterministic_hypotheses=(),
            allowed_semantic_roles=("quantity",),
            compatible_tenant_memory_hints=(
                {"column_ref": "Ventas.Cantidad", "runtime_authorized": True},
            ),
        )
    except Service1LLMSemanticContractErrorV1 as exc:
        assert exc.code == "FORBIDDEN_AUTHORITY_FIELD"
    else:
        raise AssertionError("memory hint authority must fail closed")
