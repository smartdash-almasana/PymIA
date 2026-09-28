"""Servicio 1 — F7 deterministic semantic compression.

Compresses validated V2 semantic concept decisions into traceable business
review units. It does not call an LLM, does not confirm owner evidence, does not
change semantic meaning and grants no runtime, mathematical or delivery
authority.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    DECISION_CONFLICTING_EVIDENCE,
    DECISION_IRRELEVANT_FOR_CAPABILITY,
    DECISION_MATERIAL_AMBIGUOUS,
    SCHEMA_VERSION as VALIDATOR_SCHEMA_VERSION,
    STATUS_READY as VALIDATOR_READY,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_COMPRESSION_V1"
STATUS_READY: Final[str] = "SEMANTIC_COMPRESSION_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"
AUTHORITY: Final[str] = "CONTEXT_ONLY"


def build_service_1_semantic_compression_v1(*, validated_packet: Any) -> dict[str, Any]:
    if not isinstance(validated_packet, Mapping):
        return _blocked("VALIDATED_PACKET_INVALID")
    if validated_packet.get("schema_version") != VALIDATOR_SCHEMA_VERSION or validated_packet.get("status") != VALIDATOR_READY:
        return _blocked("VALIDATED_PACKET_INVALID")
    if any(bool(validated_packet.get(flag)) for flag in (
        "runtime_authorized", "tool_execution_authorized", "product_ready",
        "delivery_authorized", "diagnosis_generated",
    )):
        return _blocked("VALIDATED_PACKET_AUTHORITY_FORBIDDEN")

    decisions = [dict(item) for item in (validated_packet.get("decisions") or []) if isinstance(item, Mapping)]
    concept_items: list[dict[str, Any]] = []
    uncompressed_ids: list[str] = []

    for item in decisions:
        decision_id = str(item.get("decision_id") or "").strip()
        if not decision_id:
            return _blocked("DECISION_ID_REQUIRED")
        if item.get("source_kind") != "CONCEPT":
            uncompressed_ids.append(decision_id)
            continue
        if item.get("status") in {
            DECISION_MATERIAL_AMBIGUOUS,
            DECISION_CONFLICTING_EVIDENCE,
            DECISION_IRRELEVANT_FOR_CAPABILITY,
        }:
            uncompressed_ids.append(decision_id)
            continue
        semantic = item.get("compositional_semantic")
        if not isinstance(semantic, Mapping):
            uncompressed_ids.append(decision_id)
            continue
        concept_items.append(item)

    groups: dict[str, list[dict[str, Any]]] = {}
    group_order: list[str] = []
    for item in concept_items:
        key = _compression_key(item)
        if key is None:
            uncompressed_ids.append(str(item.get("decision_id") or ""))
            continue
        if key not in groups:
            groups[key] = []
            group_order.append(key)
        groups[key].append(item)

    units: list[dict[str, Any]] = []
    for index, key in enumerate(group_order, start=1):
        members = groups[key]
        proposal_refs = _ordered_unique(str(item.get("decision_id") or "") for item in members)
        column_refs = _ordered_unique(
            str(ref)
            for item in members
            for ref in (item.get("target_refs") or [])
            if str(ref).strip()
        )
        evidence_refs = _ordered_unique(
            str(ref)
            for item in members
            for ref in (item.get("evidence_refs") or [])
            if str(ref).strip()
        )
        logical_table_refs = _ordered_unique(
            str(ref)
            for item in members
            for ref in (item.get("logical_table_refs") or [])
            if str(ref).strip()
        )
        grain_refs = _ordered_unique(
            str(ref)
            for item in members
            for ref in (item.get("grain_refs") or [])
            if str(ref).strip()
        )
        relationship_context_refs = _ordered_unique(
            str(ref)
            for item in members
            for ref in (item.get("relationship_context_refs") or [])
            if str(ref).strip()
        )
        axes = _shared_and_variable_axes(members)
        units.append(
            {
                "semantic_unit_id": f"semantic-unit:{index}",
                "business_key": key,
                "proposal_refs": list(proposal_refs),
                "column_refs": list(column_refs),
                "evidence_refs": list(evidence_refs),
                "logical_table_refs": list(logical_table_refs),
                "grain_refs": list(grain_refs),
                "relationship_context_refs": list(relationship_context_refs),
                "member_count": len(members),
                "shared_axes": axes["shared_axes"],
                "variable_axes": axes["variable_axes"],
                "traceability_complete": bool(proposal_refs and column_refs),
                "authority": AUTHORITY,
            }
        )

    input_count = len(concept_items)
    unit_count = len(units)
    compression_ratio = 1.0 if input_count == 0 else round(unit_count / input_count, 6)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": validated_packet.get("case_id"),
        "authority": AUTHORITY,
        "semantic_units": units,
        "input_concept_count": input_count,
        "semantic_unit_count": unit_count,
        "compression_ratio": compression_ratio,
        "uncompressed_decision_ids": list(_ordered_unique(uncompressed_ids)),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _compression_key(item: Mapping[str, Any]) -> str | None:
    semantic = item.get("compositional_semantic")
    if not isinstance(semantic, Mapping):
        return None

    table_refs = _ordered_unique(str(ref) for ref in (item.get("logical_table_refs") or []) if str(ref).strip())
    grain_refs = _ordered_unique(str(ref) for ref in (item.get("grain_refs") or []) if str(ref).strip())
    if len(table_refs) > 1 or len(grain_refs) > 1:
        return None

    refs = _ordered_unique(str(ref) for ref in (item.get("target_refs") or []) if str(ref).strip())
    sheets = _ordered_unique(ref.split(".", 1)[0] for ref in refs if "." in ref)
    containment = (
        f"table:{table_refs[0]}" if len(table_refs) == 1
        else f"sheet:{sheets[0]}" if len(sheets) == 1
        else None
    )
    if containment is None:
        return None

    grain = f"grain:{grain_refs[0]}" if len(grain_refs) == 1 else "grain:unknown"
    entity = str(semantic.get("entity") or "").strip()
    identity = str(semantic.get("identity") or "").strip()
    process = str(semantic.get("process") or "").strip()
    object_ref = str(semantic.get("object") or "").strip()

    if entity and identity:
        business = f"entity:{entity}"
    elif process and object_ref:
        business = f"process-object:{process}:{object_ref}"
    elif process and entity:
        business = f"process-entity:{process}:{entity}"
    elif object_ref:
        business = f"object:{object_ref}"
    elif entity:
        business = f"entity:{entity}"
    else:
        return None
    return "|".join((containment, grain, business))


def _shared_and_variable_axes(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    axes = (
        "entity", "object", "process", "measure", "state", "grain", "scope",
        "time", "identity", "relation", "unit", "aggregation",
    )
    shared: dict[str, str] = {}
    variable: dict[str, list[str]] = {}
    for axis in axes:
        values = _ordered_unique(
            str((item.get("compositional_semantic") or {}).get(axis) or "")
            for item in items
            if isinstance(item.get("compositional_semantic"), Mapping)
            and str((item.get("compositional_semantic") or {}).get(axis) or "").strip()
        )
        if len(values) == 1:
            shared[axis] = values[0]
        elif len(values) > 1:
            variable[axis] = list(values)
    return {"shared_axes": shared, "variable_axes": variable}


def _ordered_unique(values: Any) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": None,
        "authority": AUTHORITY,
        "semantic_units": [],
        "input_concept_count": 0,
        "semantic_unit_count": 0,
        "compression_ratio": 1.0,
        "uncompressed_decision_ids": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "AUTHORITY", "SCHEMA_VERSION", "STATUS_BLOCKED", "STATUS_READY",
    "build_service_1_semantic_compression_v1",
]
