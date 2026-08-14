from __future__ import annotations

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as BRIDGE_READY,
)
from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_owner_relationship_confirmation_event_v1,
)
from pymia.smartpyme.service_1_owner_semantic_answer_projection_v1 import (
    SCHEMA_VERSION as SEM5_SCHEMA_VERSION,
    STATUS_READY as SEM5_READY,
)
from pymia.smartpyme.service_1_owner_semantic_evidence_reentry_v1 import (
    BLOCK_AUTHORITY_FORBIDDEN,
    BLOCK_OWNER_EVENT_ROLE_NOT_AVAILABLE,
    BLOCK_REENTRY_EVIDENCE_INCOMPLETE,
    BLOCK_RELATIONSHIP_ENDPOINT_NOT_FOUND,
    STATUS_READY,
    build_service_1_owner_semantic_evidence_reentry_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)


def _candidate(
    *,
    sheet: str,
    column: str,
    ref_id: str,
    role: str,
    variable: str,
) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name=column,
        normalized_column_name=column.lower(),
        sheet_name=sheet,
        observed_data_type="number" if role != "product_id" else "text",
        sample_values=("1", "2") if role != "product_id" else ("P001", "P002"),
        candidate_semantic_roles=(role,),
        candidate_variable_names=(variable,),
        confidence=0.95,
        ambiguity_reason="owner confirmation required",
        owner_confirmation_required=True,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={
            "column_ref_id": ref_id,
            "question_id": ref_id,
            "primary_semantic_role": role,
            "primary_variable_name": variable,
        },
    )


def _bridge(*candidates: Service1ColumnSemanticCandidateV1) -> dict:
    return {
        "schema_version": "SERVICE_1_CANONICAL_INGESTION_OUTPUT_TO_SEMANTIC_BRIDGE_V1",
        "service_name": "SERVICE_1",
        "packet_type": "CANONICAL_INGESTION_OUTPUT_TO_SEMANTIC_BRIDGE",
        "status": BRIDGE_READY,
        "case_id": "case-sem6",
        "source_kind": "uploaded_bytes",
        "filename": "sem6.xlsx",
        "column_candidates": tuple(candidates),
        "column_candidate_count": len(candidates),
        "semantic_candidate_count": len(candidates),
        "column_refs": [],
        "column_understandings": (),
        "owner_question_views": (),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _column_event(
    *,
    sheet: str,
    column: str,
    role: str,
    variable: str,
    question_ref: str,
) -> dict:
    return build_service_1_owner_confirmation_event_v1(
        case_id="case-sem6",
        file_ref="sem6.xlsx",
        region_ref=None,
        sheet_ref=sheet,
        column_ref=column,
        question_ref=question_ref,
        owner_answer="ACCEPT",
        confirmation_scope="SEMANTIC_ROLE",
        proposed_role=role,
        proposed_variable=variable,
        confirmed_role=role,
        timestamp="2026-08-14T14:00:00+00:00",
        provenance={"producer": "SEM5_TEST"},
    ).to_dict()


def _sem5_packet(*, column_events: list[dict], relationship_events: list[dict] | None = None) -> dict:
    return {
        "schema_version": SEM5_SCHEMA_VERSION,
        "status": SEM5_READY,
        "blocked_reason": None,
        "case_id": "case-sem6",
        "owner_confirmation_events": list(column_events),
        "owner_relationship_confirmation_events": list(relationship_events or []),
        "owner_confirmation_event_count": len(column_events),
        "owner_relationship_confirmation_event_count": len(relationship_events or []),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def test_sem6_grouped_question_ref_reenters_existing_p6_by_physical_identity() -> None:
    candidates = (
        _candidate(sheet="Ventas", column="Cantidad", ref_id="q-qty", role="quantity", variable="volume_sold"),
        _candidate(sheet="Ventas", column="PrecioUnitario", ref_id="q-price", role="unit_sale_price", variable="sale_price"),
        _candidate(sheet="Productos", column="Costo", ref_id="q-cost", role="unit_cost_candidate", variable="cost"),
    )
    grouped_question = "dialogue:semantic-group:p-qty+p-price+p-cost"
    events = [
        _column_event(sheet="Ventas", column="Cantidad", role="quantity", variable="volume_sold", question_ref=grouped_question),
        _column_event(sheet="Ventas", column="PrecioUnitario", role="unit_sale_price", variable="sale_price", question_ref=grouped_question),
        _column_event(sheet="Productos", column="Costo", role="unit_cost_candidate", variable="cost", question_ref=grouped_question),
    ]

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(*candidates),
        owner_semantic_evidence_packet=_sem5_packet(column_events=events),
    )

    assert result["status"] == STATUS_READY
    assert result["confirmed_candidate"] is not None
    assert {item["status"] for item in result["p6_decisions"]} == {"APPROVED"}
    assert {item["owner_confirmation_question_ref"] for item in result["p6_decisions"]} == {
        grouped_question
    }
    assert sorted(result["reentry_packet"]["reinjected_columns"]) == ["q-cost", "q-price", "q-qty"]
    assert all(result[flag] is False for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
    ))


def test_sem6_preserves_relationship_evidence_separately_from_column_bindings() -> None:
    sales_id = _candidate(
        sheet="Ventas",
        column="ProductoID",
        ref_id="q-sales-product",
        role="product_id",
        variable="product_id",
    )
    master_id = _candidate(
        sheet="Productos",
        column="ProductoID",
        ref_id="q-master-product",
        role="product_id",
        variable="product_id",
    )
    question_ref = "dialogue:relationship:r-product"
    events = [
        _column_event(sheet="Ventas", column="ProductoID", role="product_id", variable="product_id", question_ref=question_ref),
        _column_event(sheet="Productos", column="ProductoID", role="product_id", variable="product_id", question_ref=question_ref),
    ]
    relationship = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-sem6",
        file_ref="sem6.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="ProductoID",
        right_sheet_ref="Productos",
        right_column_ref="ProductoID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="ACCEPT",
        question_ref=question_ref,
        timestamp="2026-08-14T14:00:00+00:00",
        provenance={"producer": "SEM5_TEST"},
    ).to_dict()

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(sales_id, master_id),
        owner_semantic_evidence_packet=_sem5_packet(
            column_events=events,
            relationship_events=[relationship],
        ),
    )

    assert result["status"] == STATUS_READY
    assert len(result["confirmed_relationships"]) == 1
    assert result["confirmed_relationships"][0]["relationship_kind"] == "MANY_TO_ONE"
    assert result["confirmed_relationships"][0]["question_ref"] == question_ref
    assert {item["approved_role"] for item in result["p6_decisions"]} == {"product_id"}


def test_sem6_maps_suppressed_irrelevant_physical_ref_to_existing_scope_exclusion() -> None:
    qty = _candidate(sheet="Ventas", column="Cantidad", ref_id="q-qty", role="quantity", variable="volume_sold")
    channel = _candidate(sheet="Ventas", column="CanalVenta", ref_id="q-channel", role="segment", variable="segment")
    event = _column_event(
        sheet="Ventas",
        column="Cantidad",
        role="quantity",
        variable="volume_sold",
        question_ref="dialogue:semantic-group:p-qty",
    )

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(qty, channel),
        owner_semantic_evidence_packet=_sem5_packet(column_events=[event]),
        suppressed_irrelevant_refs=["Ventas.CanalVenta"],
    )

    assert result["status"] == STATUS_READY
    assert result["system_scope_exclusions"] == ["q-channel"]
    assert result["confirmed_candidate"]["candidate_columns"] == ["Cantidad"]


def test_sem6_fails_closed_when_a_candidate_is_neither_confirmed_nor_suppressed() -> None:
    qty = _candidate(sheet="Ventas", column="Cantidad", ref_id="q-qty", role="quantity", variable="volume_sold")
    price = _candidate(sheet="Ventas", column="PrecioUnitario", ref_id="q-price", role="unit_sale_price", variable="sale_price")
    event = _column_event(
        sheet="Ventas",
        column="Cantidad",
        role="quantity",
        variable="volume_sold",
        question_ref="dialogue:semantic-group:p-qty",
    )

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(qty, price),
        owner_semantic_evidence_packet=_sem5_packet(column_events=[event]),
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_REENTRY_EVIDENCE_INCOMPLETE
    assert result["detail"] == ["q-price"]


def test_sem6_rejects_owner_role_outside_existing_candidate_hypothesis() -> None:
    qty = _candidate(sheet="Ventas", column="Cantidad", ref_id="q-qty", role="quantity", variable="volume_sold")
    bad_event = _column_event(
        sheet="Ventas",
        column="Cantidad",
        role="unit_sale_price",
        variable="sale_price",
        question_ref="dialogue:semantic-group:p-qty",
    )

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(qty),
        owner_semantic_evidence_packet=_sem5_packet(column_events=[bad_event]),
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_OWNER_EVENT_ROLE_NOT_AVAILABLE


def test_sem6_rejects_relationship_endpoint_not_present_in_bridge() -> None:
    sales_id = _candidate(
        sheet="Ventas",
        column="ProductoID",
        ref_id="q-sales-product",
        role="product_id",
        variable="product_id",
    )
    event = _column_event(
        sheet="Ventas",
        column="ProductoID",
        role="product_id",
        variable="product_id",
        question_ref="dialogue:relationship:r-product",
    )
    relationship = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-sem6",
        file_ref="sem6.xlsx",
        left_sheet_ref="Ventas",
        left_column_ref="ProductoID",
        right_sheet_ref="Productos",
        right_column_ref="ProductoID",
        relationship_kind="MANY_TO_ONE",
        owner_answer="ACCEPT",
        question_ref="dialogue:relationship:r-product",
        timestamp="2026-08-14T14:00:00+00:00",
        provenance={"producer": "SEM5_TEST"},
    ).to_dict()

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(sales_id),
        owner_semantic_evidence_packet=_sem5_packet(
            column_events=[event],
            relationship_events=[relationship],
        ),
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_RELATIONSHIP_ENDPOINT_NOT_FOUND


def test_sem6_rejects_authority_true_in_sem5_packet() -> None:
    qty = _candidate(sheet="Ventas", column="Cantidad", ref_id="q-qty", role="quantity", variable="volume_sold")
    event = _column_event(
        sheet="Ventas",
        column="Cantidad",
        role="quantity",
        variable="volume_sold",
        question_ref="dialogue:semantic-group:p-qty",
    )
    packet = _sem5_packet(column_events=[event])
    packet["runtime_authorized"] = True

    result = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=_bridge(qty),
        owner_semantic_evidence_packet=packet,
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_AUTHORITY_FORBIDDEN
