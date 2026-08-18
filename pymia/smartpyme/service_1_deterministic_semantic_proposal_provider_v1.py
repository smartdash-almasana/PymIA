"""Deterministic baseline semantic proposal provider for Servicio 1.

Projects already-governed deterministic column hypotheses and workbook structural
relationships into the closed SEM-2 provider payload shape. It introduces no new
semantic rules, performs no I/O/LLM calls, creates no owner evidence, and grants
no authority. A real LLM provider may be injected at the same boundary later.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pymia.smartpyme.service_1_derived_evidence_v1 import (
    service_1_derived_evidence_relevant_column_refs_v1,
)
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import PROPOSAL_SCHEMA_VERSION

def build_service_1_deterministic_semantic_proposal_v1(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("semantic provider payload must be a mapping")
    hypotheses = payload.get("deterministic_hypotheses")
    profile = payload.get("workbook_profile")
    if not isinstance(hypotheses, list) or not isinstance(profile, Mapping):
        raise ValueError("deterministic hypotheses and workbook profile are required")

    relevant_roles = {
        str(role).strip()
        for role in (payload.get("capability_relevant_roles") or [])
        if str(role).strip()
    }
    evidence_registry = payload.get("evidence_registry")
    if not isinstance(evidence_registry, Mapping):
        raise ValueError("evidence registry is required")
    capability = str(payload.get("requested_capability") or "").strip()
    derived_relevant_refs = set(
        service_1_derived_evidence_relevant_column_refs_v1(
            requested_capability=capability,
            deterministic_hypotheses=hypotheses,
        )
    )

    concepts: list[dict[str, Any]] = []
    concept_role_by_ref: dict[str, str] = {}
    all_column_refs = {
        str(item.get("column_ref") or "").strip()
        for item in (profile.get("columns") or [])
        if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
    }

    for index, hypothesis in enumerate(hypotheses, start=1):
        if not isinstance(hypothesis, Mapping):
            continue
        sheet = str(hypothesis.get("sheet_name") or "").strip()
        column = str(hypothesis.get("column_name") or "").strip()
        column_ref = f"{sheet}.{column}" if sheet and column else ""
        if not column_ref or column_ref not in all_column_refs:
            continue
        if derived_relevant_refs and column_ref not in derived_relevant_refs:
            continue
        candidates = [
            item
            for item in (hypothesis.get("candidate_meanings") or [])
            if isinstance(item, Mapping)
            and str(item.get("semantic_role") or "").strip()
            and str(item.get("variable_name") or "").strip()
        ]
        primary = hypothesis.get("primary_hypothesis")
        primary = primary if isinstance(primary, Mapping) else None
        chosen: Mapping[str, Any] | None = None
        confidence = 0.0
        if primary is not None:
            primary_role = str(primary.get("semantic_role") or "").strip()
            primary_variable = str(primary.get("variable_name") or "").strip()
            if primary_role and primary_variable and (not relevant_roles or primary_role in relevant_roles):
                confidence = float(hypothesis.get("confidence") or primary.get("score") or 0.0)
                if confidence >= 0.60:
                    chosen = primary
        if chosen is None:
            continue
        role = str(chosen.get("semantic_role") or "").strip()
        variable = str(chosen.get("variable_name") or "").strip()
        confidence = max(0.0, min(1.0, confidence))
        evidence_refs = [f"ev:column:{column_ref}:type"]
        range_ref = f"ev:column:{column_ref}:range"
        if range_ref in evidence_registry:
            evidence_refs.append(range_ref)
        concepts.append(
            {
                "proposal_id": f"baseline:concept:{index}:{column_ref}",
                "target_column_refs": [column_ref],
                "semantic_role": role,
                "variable_name": variable,
                "confidence": confidence,
                "rationale": "Projection of the highest-scoring governed deterministic hypothesis relevant to the requested capability.",
                "evidence_refs": evidence_refs,
            }
        )
        concept_role_by_ref[column_ref] = role

    relationships: list[dict[str, Any]] = []
    for index, relation in enumerate(profile.get("relationships") or [], start=1):
        if not isinstance(relation, Mapping):
            continue
        left = str(relation.get("left_column_ref") or "").strip()
        right = str(relation.get("right_column_ref") or "").strip()
        kind = str(relation.get("relationship_kind") or "").strip()
        left_role = concept_role_by_ref.get(left)
        right_role = concept_role_by_ref.get(right)
        if (
            not left
            or not right
            or not kind
            or not left_role
            or not right_role
            or left_role != right_role
            or not left_role.endswith("_identifier")
        ):
            continue
        evidence_ref = f"ev:relationship:{left}->{right}:overlap"
        if evidence_ref not in evidence_registry:
            continue
        relationships.append(
            {
                "relationship_id": f"baseline:relationship:{index}:{left}->{right}",
                "left_column_ref": left,
                "right_column_ref": right,
                "relationship_type": kind,
                "confidence": 1.0,
                "rationale": "WorkbookProfilerV1 structural relationship projected for explicit owner confirmation.",
                "evidence_refs": [evidence_ref],
            }
        )

    relevant_refs = set(concept_role_by_ref)
    irrelevant_refs = sorted(all_column_refs - relevant_refs)
    return {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "concept_proposals": concepts,
        "relationship_proposals": relationships,
        "duplicate_semantics": [],
        "irrelevant_refs": irrelevant_refs,
        "material_ambiguities": [],
    }


__all__ = ["build_service_1_deterministic_semantic_proposal_v1"]
