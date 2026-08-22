from __future__ import annotations

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    Service1LLMConceptProposalV1,
    Service1LLMDuplicateSemanticProposalV1,
    Service1LLMSemanticProposalV1,
    build_service_1_llm_semantic_context_v1,
)
from pymia.smartpyme.service_1_owner_semantic_dialogue_v1 import (
    DECISION_KIND_SEMANTIC_GROUP,
    DECISION_KIND_UNIT_MEANING,
    STATUS_READY as DIALOGUE_READY,
    build_service_1_owner_dialogue_plan_v1,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    BLOCK_LOGICAL_TABLE_SCOPE_INCOMPATIBLE,
    DECISION_CONFLICTING_EVIDENCE,
    STATUS_BLOCKED as VALIDATOR_BLOCKED,
    validate_service_1_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_table_scoped_semantic_context_v1 import (
    SCOPE_RESOLVED,
    SCOPE_UNRESOLVED,
    STATUS_PARTIAL,
    STATUS_READY,
    build_service_1_table_scoped_semantic_context_v1,
    enrich_service_1_deterministic_hypotheses_with_table_scope_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    build_service_1_workbook_profile_v1,
)


def _candidate(
    ref: str,
    *,
    sheet: str,
    region: str,
    columns: list[str],
    grain_key: str,
) -> dict:
    return {
        "candidate_id": ref,
        "logical_table_id": ref,
        "workbook_ref": "book.xlsx",
        "source_region_refs": [region],
        "source_sheet_refs": [sheet],
        "structural_signature": f"sig:{ref}",
        "grain_state": "RESOLVED",
        "grain_candidate": {
            "kind": "ROW_KEYED_BY_CANDIDATE",
            "key_refs": [f"{region}.{grain_key}"],
            "authoritative": False,
        },
        "primary_key_candidates": [],
        "unique_key_candidates": [],
        "provenance": {
            "structural_payload": {
                "columns": [
                    {"normalized_header": column, "inferred_type": "text"}
                    for column in columns
                ]
            }
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _column(field_id: str, sheet: str, column: str) -> dict:
    return {
        "field_id": field_id,
        "question_id": field_id,
        "sheet_name": sheet,
        "column_name": column,
        "normalized_column_name": column.casefold(),
    }


def test_d5_resolves_two_logical_tables_inside_same_sheet() -> None:
    refs = [_column("q-a", "Mixta", "fecha_a"), _column("q-b", "Mixta", "fecha_b")]
    candidates = [
        _candidate("table:a", sheet="Mixta", region="r1", columns=["fecha_a", "id_a"], grain_key="id_a"),
        _candidate("table:b", sheet="Mixta", region="r2", columns=["fecha_b", "id_b"], grain_key="id_b"),
    ]

    result = build_service_1_table_scoped_semantic_context_v1(
        column_refs=refs,
        logical_table_candidates=candidates,
        logical_relationship_graph={
            "relationships": [
                {
                    "relationship_ref": "rel:a-b",
                    "left_logical_table_ref": "table:a",
                    "right_logical_table_ref": "table:b",
                }
            ]
        },
    )

    assert result["status"] == STATUS_READY
    scopes = {item["column_ref"]: item for item in result["column_scopes"]}
    assert scopes["q-a"]["logical_table_ref"] == "table:a"
    assert scopes["q-b"]["logical_table_ref"] == "table:b"
    assert tuple(scopes["q-a"]["relationship_context_refs"]) == ("rel:a-b",)
    assert tuple(scopes["q-b"]["relationship_context_refs"]) == ("rel:a-b",)
    assert all(item["scope_state"] == SCOPE_RESOLVED for item in scopes.values())


def test_d5_same_sheet_same_header_ambiguous_mapping_fails_closed() -> None:
    refs = [_column("q-date", "Mixta", "fecha")]
    candidates = [
        _candidate("table:a", sheet="Mixta", region="r1", columns=["fecha", "id_a"], grain_key="id_a"),
        _candidate("table:b", sheet="Mixta", region="r2", columns=["fecha", "id_b"], grain_key="id_b"),
    ]

    result = build_service_1_table_scoped_semantic_context_v1(
        column_refs=refs,
        logical_table_candidates=candidates,
    )

    assert result["status"] == STATUS_PARTIAL
    assert result["column_scopes"][0]["scope_state"] == SCOPE_UNRESOLVED
    assert result["column_scopes"][0]["unresolved_reason"] == "LOGICAL_TABLE_ENDPOINT_AMBIGUOUS"


def test_d5_enriches_existing_hypotheses_without_changing_semantic_hypothesis() -> None:
    refs = [_column("q-date", "Ventas", "fecha")]
    candidates = [
        _candidate("table:ventas", sheet="Ventas", region="r1", columns=["fecha", "venta"], grain_key="fecha")
    ]
    scope = build_service_1_table_scoped_semantic_context_v1(
        column_refs=refs,
        logical_table_candidates=candidates,
    )
    hypotheses = ({
        "column_name": "fecha",
        "sheet_name": "Ventas",
        "normalized_header": "fecha",
        "primary_semantic_role": "operation_date",
        "primary_variable_name": "business_period",
    },)

    enriched = enrich_service_1_deterministic_hypotheses_with_table_scope_v1(
        deterministic_hypotheses=hypotheses,
        column_refs=refs,
        semantic_scope_packet=scope,
    )

    assert enriched[0]["primary_semantic_role"] == "operation_date"
    assert enriched[0]["logical_table_ref"] == "table:ventas"
    assert enriched[0]["grain_state"] == "RESOLVED"
    assert enriched[0]["grain_ref"].startswith("grain_")


def _validated_decision(
    decision_id: str,
    ref: str,
    *,
    table: str,
    grain: str,
    role: str = "operation_date",
) -> dict:
    return {
        "decision_id": decision_id,
        "source_kind": "CONCEPT",
        "status": "MATERIAL_CONFIDENT",
        "target_refs": [ref],
        "semantic_role": role,
        "variable_name": "business_period",
        "relationship_type": None,
        "confidence": 0.95,
        "evidence_refs": [],
        "rationale": "bounded semantic proposal",
        "reason": None,
        "logical_table_refs": [table],
        "region_refs": [f"region:{table}"],
        "grain_refs": [grain],
        "grain_states": ["RESOLVED"],
        "relationship_context_refs": [],
        "scope_conflict_reason": None,
    }


def _validated_packet(decisions: list[dict]) -> dict:
    return {
        "schema_version": "SERVICE_1_SEMANTIC_PROPOSAL_VALIDATOR_V1",
        "status": "VALIDATED_SEMANTIC_PROPOSAL_READY",
        "blocked_reason": None,
        "case_id": "d5",
        "requested_capability": None,
        "decisions": decisions,
        "decision_count": len(decisions),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def test_d5_owner_groups_only_same_logical_table_and_grain() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(
        validated_packet=_validated_packet([
            _validated_decision("a1", "Mixta.fecha_a", table="table:a", grain="grain:a"),
            _validated_decision("a2", "Mixta.importe_a", table="table:a", grain="grain:a", role="sales_amount"),
            _validated_decision("b1", "Mixta.fecha_b", table="table:b", grain="grain:b"),
        ])
    )

    assert plan["status"] == DIALOGUE_READY
    groups = [item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP]
    assert len(groups) == 1
    assert tuple(groups[0]["proposal_refs"]) == ("a1", "a2")
    atomic = [item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_UNIT_MEANING]
    assert {tuple(item["proposal_refs"]) for item in atomic} == {("b1",)}
    assert all("logical:" not in item["presentation_text"] for item in groups + atomic)
    assert all("dialogue:" not in item["presentation_text"] for item in groups + atomic)


def test_d5_same_table_different_grain_is_not_grouped() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(
        validated_packet=_validated_packet([
            _validated_decision("a1", "Mixta.fecha", table="table:a", grain="grain:daily"),
            _validated_decision("a2", "Mixta.total", table="table:a", grain="grain:monthly", role="sales_amount"),
        ])
    )

    assert plan["status"] == DIALOGUE_READY
    assert not [item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP]
    atomic = [item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_UNIT_MEANING]
    assert {tuple(item["proposal_refs"]) for item in atomic} == {("a1",), ("a2",)}


def _profile_with_scopes() -> dict:
    ingestion = {
        "case_id": "d5-validator",
        "filename": "same.xlsx",
        "source_file_ref": "same.xlsx",
        "column_refs": [
            _column("q-a", "Mixta", "fecha_a"),
            _column("q-b", "Mixta", "fecha_b"),
        ],
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Mixta",
                "headers": ["fecha_a", "fecha_b"],
                "normalized_headers": ["fecha_a", "fecha_b"],
                "rows": [{"fecha_a": "2026-01-01", "fecha_b": "2026-02-01"}],
            }
        ],
        "runtime_authorized": False,
    }
    profile = build_service_1_workbook_profile_v1(ingestion_output=ingestion)
    profile["logical_table_scopes"] = [
        {
            "column_ref": "q-a",
            "sheet_ref": "Mixta",
            "normalized_header": "fecha_a",
            "logical_table_ref": "table:a",
            "region_refs": ["r1"],
            "grain_state": "RESOLVED",
            "grain_ref": "grain:a",
            "relationship_context_refs": [],
            "scope_state": "RESOLVED",
        },
        {
            "column_ref": "q-b",
            "sheet_ref": "Mixta",
            "normalized_header": "fecha_b",
            "logical_table_ref": "table:b",
            "region_refs": ["r2"],
            "grain_state": "RESOLVED",
            "grain_ref": "grain:b",
            "relationship_context_refs": [],
            "scope_state": "RESOLVED",
        },
    ]
    return profile


def test_d5_validator_blocks_one_concept_spanning_two_logical_tables() -> None:
    profile = _profile_with_scopes()
    context = build_service_1_llm_semantic_context_v1(
        case_id="d5-validator",
        requested_capability=None,
        workbook_profile=profile,
        deterministic_hypotheses=[
            {"semantic_role": "operation_date", "variable_name": "business_period"},
        ],
        allowed_semantic_roles=["operation_date"],
    )
    proposal = Service1LLMSemanticProposalV1(
        concept_proposals=(
            Service1LLMConceptProposalV1(
                proposal_id="cross-table",
                target_column_refs=("Mixta.fecha_a", "Mixta.fecha_b"),
                semantic_role="operation_date",
                variable_name="business_period",
                confidence=0.95,
                rationale="incorrect cross-table proposal",
                evidence_refs=(
                    "ev:column:Mixta.fecha_a:type",
                    "ev:column:Mixta.fecha_b:type",
                ),
            ),
        )
    )

    result = validate_service_1_semantic_proposal_v1(context=context, proposal=proposal)

    assert result["status"] == VALIDATOR_BLOCKED
    assert result["blocked_reason"] == BLOCK_LOGICAL_TABLE_SCOPE_INCOMPATIBLE


def test_d5_cross_table_duplicate_semantics_is_explicit_conflict() -> None:
    profile = _profile_with_scopes()
    context = build_service_1_llm_semantic_context_v1(
        case_id="d5-validator",
        requested_capability=None,
        workbook_profile=profile,
        deterministic_hypotheses=[
            {"semantic_role": "operation_date", "variable_name": "business_period"},
        ],
        allowed_semantic_roles=["operation_date"],
    )
    proposal = Service1LLMSemanticProposalV1(
        duplicate_semantics=(
            Service1LLMDuplicateSemanticProposalV1(
                duplicate_id="cross-table-duplicate",
                column_refs=("Mixta.fecha_a", "Mixta.fecha_b"),
                proposed_shared_role="operation_date",
                confidence=0.95,
                rationale="same header family but distinct logical tables",
                evidence_refs=(
                    "ev:column:Mixta.fecha_a:type",
                    "ev:column:Mixta.fecha_b:type",
                ),
            ),
        )
    )

    result = validate_service_1_semantic_proposal_v1(context=context, proposal=proposal)

    assert result["status"] != VALIDATOR_BLOCKED
    decision = result["decisions"][0]
    assert decision["status"] == DECISION_CONFLICTING_EVIDENCE
    assert decision["scope_conflict_reason"] == "CROSS_TABLE_SCOPE_CONFLICT"
    assert set(decision["logical_table_refs"]) == {"table:a", "table:b"}
