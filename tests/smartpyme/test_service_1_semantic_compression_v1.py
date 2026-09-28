from pymia.smartpyme.service_1_semantic_compression_v1 import (
    AUTHORITY,
    STATUS_READY,
    build_service_1_semantic_compression_v1,
)


def _semantic(field_ref: str, **axes):
    payload = {
        "field_ref": field_ref,
        "entity": None,
        "object": None,
        "process": None,
        "measure": None,
        "state": None,
        "grain": None,
        "scope": None,
        "time": None,
        "identity": None,
        "relation": None,
        "unit": None,
        "aggregation": None,
        "confidence": 0.95,
        "evidence": [f"ev:column:{field_ref}:type"],
        "source": "LLM_C2_PROPOSAL",
    }
    payload.update(axes)
    return payload


def _decision(decision_id: str, ref: str, semantic: dict):
    return {
        "decision_id": decision_id,
        "source_kind": "CONCEPT",
        "status": "MATERIAL_CONFIDENT",
        "target_refs": [ref],
        "semantic_role": None,
        "variable_name": None,
        "relationship_type": None,
        "confidence": 0.95,
        "evidence_refs": [f"ev:column:{ref}:type"],
        "rationale": "structured V2 meaning",
        "reason": None,
        "logical_table_refs": ["lt_ordenes"],
        "region_refs": ["region_ordenes"],
        "grain_refs": ["g_work_order"],
        "grain_states": ["RESOLVED"],
        "relationship_context_refs": [],
        "scope_conflict_reason": None,
        "compositional_semantic": semantic,
    }


def test_f7_compresses_coherent_labor_metrics_without_losing_traceability() -> None:
    decisions = [
        _decision(
            "p_hours",
            "ORDENES_TRABAJO.horas_mano_obra",
            _semantic(
                "ORDENES_TRABAJO.horas_mano_obra",
                object="labor",
                process="service_delivery",
                measure="duration",
                grain="work_order",
                scope="event",
                unit="hours",
            ),
        ),
        _decision(
            "p_cost",
            "ORDENES_TRABAJO.costo_mano_obra",
            _semantic(
                "ORDENES_TRABAJO.costo_mano_obra",
                object="labor",
                process="service_delivery",
                measure="cost",
                grain="work_order",
                scope="event",
                unit="currency",
            ),
        ),
        _decision(
            "p_margin",
            "ORDENES_TRABAJO.margen_mano_obra",
            _semantic(
                "ORDENES_TRABAJO.margen_mano_obra",
                object="labor",
                process="service_delivery",
                measure="margin",
                grain="work_order",
                scope="event",
                unit="currency",
            ),
        ),
        _decision(
            "p_order_id",
            "ORDENES_TRABAJO.orden_id",
            _semantic(
                "ORDENES_TRABAJO.orden_id",
                entity="work_order",
                identity="identifier",
                grain="work_order",
            ),
        ),
    ]
    packet = {
        "schema_version": "SERVICE_1_SEMANTIC_PROPOSAL_VALIDATOR_V1",
        "status": "VALIDATED_SEMANTIC_PROPOSAL_READY",
        "case_id": "taller-case",
        "decisions": decisions,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }

    result = build_service_1_semantic_compression_v1(validated_packet=packet)

    assert result["status"] == STATUS_READY
    assert result["authority"] == AUTHORITY
    assert result["input_concept_count"] == 4
    assert result["semantic_unit_count"] == 2
    assert result["compression_ratio"] == 0.5
    labor = next(unit for unit in result["semantic_units"] if "process-object:service_delivery:labor" in unit["business_key"])
    assert labor["proposal_refs"] == ["p_hours", "p_cost", "p_margin"]
    assert labor["column_refs"] == [
        "ORDENES_TRABAJO.horas_mano_obra",
        "ORDENES_TRABAJO.costo_mano_obra",
        "ORDENES_TRABAJO.margen_mano_obra",
    ]
    assert labor["shared_axes"]["object"] == "labor"
    assert labor["shared_axes"]["process"] == "service_delivery"
    assert set(labor["variable_axes"]["measure"]) == {"duration", "cost", "margin"}
    assert labor["traceability_complete"] is True
    assert labor["authority"] == "CONTEXT_ONLY"
    assert result["runtime_authorized"] is False


def test_f7_never_compresses_material_ambiguity_into_a_confident_unit() -> None:
    ambiguous = _decision(
        "p_ambiguous",
        "ORDENES_TRABAJO.valor_hora",
        _semantic(
            "ORDENES_TRABAJO.valor_hora",
            object="labor",
            process="service_delivery",
            measure="price",
            grain="work_order",
            unit="currency",
        ),
    )
    ambiguous["status"] = "MATERIAL_AMBIGUOUS"
    packet = {
        "schema_version": "SERVICE_1_SEMANTIC_PROPOSAL_VALIDATOR_V1",
        "status": "VALIDATED_SEMANTIC_PROPOSAL_READY",
        "case_id": "taller-case",
        "decisions": [ambiguous],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }

    result = build_service_1_semantic_compression_v1(validated_packet=packet)

    assert result["status"] == STATUS_READY
    assert result["semantic_units"] == []
    assert result["uncompressed_decision_ids"] == ["p_ambiguous"]
