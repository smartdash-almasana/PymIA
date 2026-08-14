from __future__ import annotations

from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    Service1OwnerRelationshipConfirmationEventV1,
)
from pymia.smartpyme.service_1_owner_semantic_answer_projection_v1 import (
    BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED,
    BLOCK_CASE_MISMATCH,
    BLOCK_DIALOGUE_RESPONSE_INVALID,
    STATUS_BLOCKED,
    STATUS_READY,
    project_service_1_owner_semantic_answer_v1,
)
from pymia.smartpyme.service_1_owner_semantic_dialogue_v1 import (
    ACTION_ACCEPT,
    ACTION_CORRECT,
    ACTION_REJECT,
    DECISION_KIND_RELATIONSHIP,
    DECISION_KIND_SEMANTIC_GROUP,
    apply_service_1_owner_dialogue_response_v1,
    build_service_1_owner_dialogue_plan_v1,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    SCHEMA_VERSION as VALIDATOR_SCHEMA_VERSION,
    STATUS_READY as VALIDATOR_READY,
)


def _validated_packet() -> dict:
    return {
        "schema_version": VALIDATOR_SCHEMA_VERSION,
        "status": VALIDATOR_READY,
        "blocked_reason": None,
        "case_id": "case-sem5",
        "requested_capability": "net_margin_real",
        "decisions": [
            {
                "decision_id": "p-qty",
                "source_kind": "CONCEPT",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Ventas.Cantidad"],
                "semantic_role": "quantity",
                "variable_name": "volume_sold",
                "relationship_type": None,
                "confidence": 0.97,
                "evidence_refs": ["ev:column:Ventas.Cantidad:type"],
                "rationale": "numeric quantity",
                "reason": None,
            },
            {
                "decision_id": "p-price",
                "source_kind": "CONCEPT",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Ventas.PrecioUnitario"],
                "semantic_role": "unit_sale_price",
                "variable_name": "sale_price",
                "relationship_type": None,
                "confidence": 0.95,
                "evidence_refs": ["ev:column:Ventas.PrecioUnitario:type"],
                "rationale": "numeric sale price",
                "reason": None,
            },
            {
                "decision_id": "p-cost",
                "source_kind": "CONCEPT",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Productos.Costo"],
                "semantic_role": "unit_cost_candidate",
                "variable_name": "cost",
                "relationship_type": None,
                "confidence": 0.96,
                "evidence_refs": ["ev:column:Productos.Costo:type"],
                "rationale": "numeric cost",
                "reason": None,
            },
            {
                "decision_id": "p-sales-id",
                "source_kind": "CONCEPT",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Ventas.ProductoID"],
                "semantic_role": "product_id",
                "variable_name": "product_id",
                "relationship_type": None,
                "confidence": 0.99,
                "evidence_refs": ["ev:column:Ventas.ProductoID:type"],
                "rationale": "identifier",
                "reason": None,
            },
            {
                "decision_id": "p-product-id",
                "source_kind": "CONCEPT",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Productos.ProductoID"],
                "semantic_role": "product_id",
                "variable_name": "product_id",
                "relationship_type": None,
                "confidence": 0.99,
                "evidence_refs": ["ev:column:Productos.ProductoID:type"],
                "rationale": "identifier",
                "reason": None,
            },
            {
                "decision_id": "r-product",
                "source_kind": "RELATIONSHIP",
                "status": "MATERIAL_CONFIDENT",
                "target_refs": ["Ventas.ProductoID", "Productos.ProductoID"],
                "semantic_role": None,
                "variable_name": None,
                "relationship_type": "MANY_TO_ONE",
                "confidence": 0.99,
                "evidence_refs": ["ev:relationship:Ventas.ProductoID->Productos.ProductoID:overlap"],
                "rationale": "structural relationship",
                "reason": None,
            },
        ],
        "decision_count": 6,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _response(kind: str, action: str = ACTION_ACCEPT) -> tuple[dict, dict]:
    packet = _validated_packet()
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)
    decision = next(item for item in plan["decisions"] if item["decision_kind"] == kind)
    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=decision["decision_id"],
        action=action,
    )
    return packet, response


def _project(packet: dict, response: dict) -> dict:
    return project_service_1_owner_semantic_answer_v1(
        dialogue_response=response,
        validated_packet=packet,
        case_id="case-sem5",
        file_ref="cafeteria.xlsx",
        owner_actor_id="owner-1",
        owner_actor_role="OWNER",
        timestamp="2026-08-14T14:00:00+00:00",
    )


def test_sem5_group_accept_projects_three_canonical_column_events() -> None:
    packet, response = _response(DECISION_KIND_SEMANTIC_GROUP)
    result = _project(packet, response)

    assert result["status"] == STATUS_READY
    assert result["owner_confirmation_event_count"] == 3
    assert result["owner_relationship_confirmation_event_count"] == 0
    events = result["owner_confirmation_events"]
    assert {(item["sheet_ref"], item["column_ref"], item["confirmed_role"]) for item in events} == {
        ("Ventas", "Cantidad", "quantity"),
        ("Ventas", "PrecioUnitario", "unit_sale_price"),
        ("Productos", "Costo", "unit_cost_candidate"),
    }
    assert all(item["confirmed_by_owner"] is True for item in events)
    assert all(item["confirmation_scope"] == "SEMANTIC_ROLE" for item in events)
    assert all(item["runtime_authorized"] is False for item in events)
    assert all(item["delivery_authorized"] is False for item in events)


def test_sem5_relationship_accept_projects_one_relation_and_absorbed_endpoint_events() -> None:
    packet, response = _response(DECISION_KIND_RELATIONSHIP)
    result = _project(packet, response)

    assert result["status"] == STATUS_READY
    assert result["owner_confirmation_event_count"] == 2
    assert result["owner_relationship_confirmation_event_count"] == 1
    assert {(item["sheet_ref"], item["column_ref"]) for item in result["owner_confirmation_events"]} == {
        ("Ventas", "ProductoID"),
        ("Productos", "ProductoID"),
    }
    relation = result["owner_relationship_confirmation_events"][0]
    assert relation["left_sheet_ref"] == "Ventas"
    assert relation["left_column_ref"] == "ProductoID"
    assert relation["right_sheet_ref"] == "Productos"
    assert relation["right_column_ref"] == "ProductoID"
    assert relation["relationship_kind"] == "MANY_TO_ONE"
    assert relation["confirmed_by_owner"] is True
    assert relation["runtime_authorized"] is False
    assert relation["delivery_authorized"] is False


def test_sem5_reject_never_creates_owner_confirmation_evidence() -> None:
    packet, response = _response(DECISION_KIND_SEMANTIC_GROUP, ACTION_REJECT)
    result = _project(packet, response)

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_DIALOGUE_RESPONSE_INVALID
    assert result["owner_confirmation_events"] == []
    assert result["owner_relationship_confirmation_events"] == []


def test_sem5_correction_never_creates_owner_confirmation_evidence() -> None:
    packet = _validated_packet()
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)
    group = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP)
    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=group["decision_id"],
        action=ACTION_CORRECT,
        correction_text="PrecioUnitario es el precio realmente cobrado.",
        targeted_refs=["Ventas.PrecioUnitario"],
    )
    result = _project(packet, response)

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_DIALOGUE_RESPONSE_INVALID
    assert result["owner_confirmation_event_count"] == 0


def test_sem5_case_mismatch_fails_closed() -> None:
    packet, response = _response(DECISION_KIND_SEMANTIC_GROUP)
    result = project_service_1_owner_semantic_answer_v1(
        dialogue_response=response,
        validated_packet=packet,
        case_id="different-case",
        file_ref="cafeteria.xlsx",
        owner_actor_id="owner-1",
        owner_actor_role="OWNER",
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_CASE_MISMATCH


def test_sem5_generic_accepted_ambiguity_cannot_fabricate_semantic_evidence() -> None:
    packet = _validated_packet()
    packet["decisions"] = [
        {
            "decision_id": "amb-1",
            "source_kind": "MATERIAL_AMBIGUITY",
            "status": "MATERIAL_AMBIGUOUS",
            "target_refs": ["Ventas.Descuento"],
            "semantic_role": None,
            "variable_name": None,
            "relationship_type": None,
            "confidence": 0.5,
            "evidence_refs": ["ev:column:Ventas.Descuento:range"],
            "rationale": None,
            "reason": "unit ambiguous",
        }
    ]
    packet["decision_count"] = 1
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)
    decision = plan["decisions"][0]
    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=decision["decision_id"],
        action=ACTION_ACCEPT,
    )
    result = _project(packet, response)

    assert result["status"] == STATUS_BLOCKED
    assert result["blocked_reason"] == BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED
    assert result["owner_confirmation_event_count"] == 0


def test_relationship_event_contract_rejects_authority_in_provenance() -> None:
    try:
        Service1OwnerRelationshipConfirmationEventV1(
            case_id="case-1",
            file_ref="x.xlsx",
            left_sheet_ref="Ventas",
            left_column_ref="ProductoID",
            right_sheet_ref="Productos",
            right_column_ref="ProductoID",
            relationship_kind="MANY_TO_ONE",
            owner_answer="ACCEPT",
            confirmed_by_owner=True,
            question_ref="q-1",
            timestamp="2026-08-14T14:00:00+00:00",
            provenance={"runtime_authorized": False},
        )
    except ValueError as exc:
        assert "authority fields" in str(exc)
    else:
        raise AssertionError("relationship event accepted authority provenance")
