from __future__ import annotations

from pymia.smartpyme.service_1_owner_semantic_dialogue_v1 import (
    ACTION_ACCEPT,
    ACTION_CORRECT,
    ACTION_REJECT,
    DECISION_KIND_RELATIONSHIP,
    DECISION_KIND_SEMANTIC_GROUP,
    RESPONSE_GROUP_CONFIRMED,
    RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION,
    RESPONSE_NEEDS_GRANULAR_CONFIRMATION,
    RESPONSE_RELATIONSHIP_CONFIRMED,
    RESPONSE_TARGETED_CORRECTION_PROPOSED,
    STATUS_READY,
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
        "case_id": "case-sem4",
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
            {
                "decision_id": "irrelevant-channel",
                "source_kind": "IRRELEVANT_REF",
                "status": "IRRELEVANT_FOR_CAPABILITY",
                "target_refs": ["Ventas.CanalVenta"],
                "semantic_role": None,
                "variable_name": None,
                "relationship_type": None,
                "confidence": 1.0,
                "evidence_refs": [],
                "rationale": None,
                "reason": "not relevant",
            },
        ],
        "decision_count": 7,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def test_sem4_groups_material_concepts_and_asks_relationship_once() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())

    assert plan["status"] == STATUS_READY
    assert plan["question_count"] == 2
    assert plan["zero_duplicate_questions"] is True
    assert plan["zero_irrelevant_questions"] is True
    assert plan["all_material_ambiguities_surfaced"] is True
    assert plan["suppressed_irrelevant_refs"] == ["Ventas.CanalVenta"]

    by_kind = {item["decision_kind"]: item for item in plan["decisions"]}
    relationship = by_kind[DECISION_KIND_RELATIONSHIP]
    group = by_kind[DECISION_KIND_SEMANTIC_GROUP]

    assert relationship["relationship_refs"] == [
        "Ventas.ProductoID->Productos.ProductoID"
    ]
    assert set(relationship["proposal_refs"]) == {
        "r-product",
        "p-sales-id",
        "p-product-id",
    }
    assert set(group["proposal_refs"]) == {"p-qty", "p-price", "p-cost"}
    assert "Ventas.CanalVenta" not in group["column_refs"]


def test_sem4_group_rejection_decomposes_to_atomic_without_fabricating_rejections() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())
    group = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP)

    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=group["decision_id"],
        action=ACTION_REJECT,
    )

    assert response["status"] == RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION
    assert {item["proposal_ref"] for item in response["atomic_decisions"]} == {
        "p-qty",
        "p-price",
        "p-cost",
    }
    assert response["confirmed_by_owner"] is False


def test_sem4_group_accept_is_dialogue_state_not_owner_evidence() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())
    group = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP)

    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=group["decision_id"],
        action=ACTION_ACCEPT,
    )

    assert response["status"] == RESPONSE_GROUP_CONFIRMED
    assert response["confirmed_by_owner"] is False
    assert response["runtime_authorized"] is False
    assert response["delivery_authorized"] is False


def test_sem4_relationship_accept_is_single_relationship_confirmation_state() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())
    relation = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_RELATIONSHIP)

    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=relation["decision_id"],
        action=ACTION_ACCEPT,
    )

    assert response["status"] == RESPONSE_RELATIONSHIP_CONFIRMED
    assert response["relationship_refs"] == [
        "Ventas.ProductoID->Productos.ProductoID"
    ]


def test_sem4_targeted_correction_stays_proposal_not_confirmation() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())
    group = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP)

    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=group["decision_id"],
        action=ACTION_CORRECT,
        correction_text="PrecioUnitario es el precio realmente cobrado.",
        targeted_refs=["Ventas.PrecioUnitario"],
    )

    assert response["status"] == RESPONSE_TARGETED_CORRECTION_PROPOSED
    assert response["targeted_refs"] == ["Ventas.PrecioUnitario"]
    assert response["confirmed_by_owner"] is False


def test_sem4_ambiguous_correction_degrades_to_granular() -> None:
    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=_validated_packet())
    group = next(item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_SEMANTIC_GROUP)

    response = apply_service_1_owner_dialogue_response_v1(
        dialogue_plan=plan,
        decision_id=group["decision_id"],
        action=ACTION_CORRECT,
        correction_text="No, hay algo mal.",
    )

    assert response["status"] == RESPONSE_NEEDS_GRANULAR_CONFIRMATION
    assert len(response["atomic_decisions"]) == 3


def test_sem4_surfaces_material_ambiguity_exactly_once() -> None:
    packet = _validated_packet()
    packet["decisions"].append(
        {
            "decision_id": "amb-discount",
            "source_kind": "MATERIAL_AMBIGUITY",
            "status": "MATERIAL_AMBIGUOUS",
            "target_refs": ["Ventas.Descuento"],
            "semantic_role": None,
            "variable_name": None,
            "relationship_type": None,
            "confidence": 0.5,
            "evidence_refs": ["ev:column:Ventas.Descuento:range"],
            "rationale": None,
            "reason": "No está claro si 0.10 significa 10% o un importe unitario.",
        }
    )

    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)

    assert plan["status"] == STATUS_READY
    surfaced = [
        item
        for item in plan["decisions"]
        if "amb-discount" in item["proposal_refs"]
    ]
    assert len(surfaced) == 1
    assert plan["all_material_ambiguities_surfaced"] is True


def test_sem4_rejects_upstream_authority_true() -> None:
    packet = _validated_packet()
    packet["runtime_authorized"] = True
    result = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)
    assert result["status"] == "BLOCKED"
    assert result["question_count"] == 0


def test_sem4_surfaces_ambiguous_relationship_exactly_once() -> None:
    packet = _validated_packet()
    relationship = next(
        item for item in packet["decisions"] if item["decision_id"] == "r-product"
    )
    relationship["status"] = "MATERIAL_AMBIGUOUS"
    relationship["confidence"] = 0.8
    relationship["reason"] = "La relación material requiere confirmación del owner."

    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)

    assert plan["status"] == STATUS_READY
    surfaced = [
        item
        for item in plan["decisions"]
        if "r-product" in item["proposal_refs"]
    ]
    assert len(surfaced) == 1
    assert surfaced[0]["decision_kind"] == "RELATIONSHIP"
    assert plan["zero_duplicate_questions"] is True


def test_sem4_deduplicates_confident_mirror_relationships_and_absorbs_concepts_once() -> None:
    packet = _validated_packet()
    mirror = dict(next(item for item in packet["decisions"] if item["decision_id"] == "r-product"))
    mirror["decision_id"] = "r-product-mirror"
    mirror["target_refs"] = ["Productos.ProductoID", "Ventas.ProductoID"]
    mirror["evidence_refs"] = ["ev:relationship:Productos.ProductoID->Ventas.ProductoID:overlap"]
    packet["decisions"].append(mirror)

    plan = build_service_1_owner_dialogue_plan_v1(validated_packet=packet)

    assert plan["status"] == STATUS_READY
    relation_questions = [
        item for item in plan["decisions"] if item["decision_kind"] == DECISION_KIND_RELATIONSHIP
    ]
    assert len(relation_questions) == 1
    proposals = relation_questions[0]["proposal_refs"]
    assert "r-product" in proposals
    assert "r-product-mirror" in proposals
    assert proposals.count("p-sales-id") == 1
    assert proposals.count("p-product-id") == 1
    assert plan["zero_duplicate_questions"] is True
