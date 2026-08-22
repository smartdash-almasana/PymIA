"""Servicio 1 — deterministic semantic proposal validator V1.

ADR-029 / SEM-3. Validates one closed LLM semantic proposal against the exact
SEM-2 context and SEM-1 workbook profile. No provider calls, no persistence,
no owner confirmation, no calculation and no runtime/delivery authority.

Hard identity/evidence/ontology violations invalidate the whole pass. Semantic
or structural disagreements that still reference real evidence are preserved as
explicit decisions for the later owner-dialogue planner.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Final

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    Service1LLMConceptProposalV1,
    Service1LLMDuplicateSemanticProposalV1,
    Service1LLMMaterialAmbiguityV1,
    Service1LLMRelationshipProposalV1,
    Service1LLMSemanticContextV1,
    Service1LLMSemanticProposalV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_PROPOSAL_VALIDATOR_V1"
STATUS_READY: Final[str] = "VALIDATED_SEMANTIC_PROPOSAL_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

DECISION_MATERIAL_CONFIDENT: Final[str] = "MATERIAL_CONFIDENT"
DECISION_MATERIAL_AMBIGUOUS: Final[str] = "MATERIAL_AMBIGUOUS"
DECISION_IRRELEVANT_FOR_CAPABILITY: Final[str] = "IRRELEVANT_FOR_CAPABILITY"
DECISION_CONFLICTING_EVIDENCE: Final[str] = "CONFLICTING_EVIDENCE"

BLOCK_CONTEXT_INVALID: Final[str] = "BLOCKED_CONTEXT_INVALID"
BLOCK_PROPOSAL_INVALID: Final[str] = "BLOCKED_PROPOSAL_INVALID"
BLOCK_COLUMN_REF_NOT_FOUND: Final[str] = "BLOCKED_COLUMN_REF_NOT_FOUND"
BLOCK_EVIDENCE_REF_NOT_FOUND: Final[str] = "BLOCKED_EVIDENCE_REF_NOT_FOUND"
BLOCK_SEMANTIC_ROLE_NOT_ALLOWED: Final[str] = "BLOCKED_SEMANTIC_ROLE_NOT_ALLOWED"
BLOCK_VARIABLE_NAME_INCOMPATIBLE: Final[str] = "BLOCKED_VARIABLE_NAME_INCOMPATIBLE"
BLOCK_RELATIONSHIP_REF_NOT_FOUND: Final[str] = "BLOCKED_RELATIONSHIP_REF_NOT_FOUND"
BLOCK_RELATIONSHIP_TYPE_INCOMPATIBLE: Final[str] = "BLOCKED_RELATIONSHIP_TYPE_INCOMPATIBLE"
BLOCK_LOGICAL_TABLE_SCOPE_UNRESOLVED: Final[str] = "BLOCKED_LOGICAL_TABLE_SCOPE_UNRESOLVED"
BLOCK_LOGICAL_TABLE_SCOPE_INCOMPATIBLE: Final[str] = "BLOCKED_LOGICAL_TABLE_SCOPE_INCOMPATIBLE"

CONFIDENT_THRESHOLD: Final[float] = 0.80


@dataclass(frozen=True)
class Service1ValidatedSemanticDecisionV1:
    decision_id: str
    source_kind: str
    status: str
    target_refs: tuple[str, ...]
    semantic_role: str | None
    variable_name: str | None
    relationship_type: str | None
    confidence: float
    evidence_refs: tuple[str, ...]
    rationale: str | None
    reason: str | None
    logical_table_refs: tuple[str, ...] = ()
    region_refs: tuple[str, ...] = ()
    grain_refs: tuple[str, ...] = ()
    grain_states: tuple[str, ...] = ()
    relationship_context_refs: tuple[str, ...] = ()
    scope_conflict_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_service_1_semantic_proposal_v1(
    *,
    context: Any,
    proposal: Any,
) -> dict[str, Any]:
    if not isinstance(context, Service1LLMSemanticContextV1):
        return _blocked(BLOCK_CONTEXT_INVALID)
    if not isinstance(proposal, Service1LLMSemanticProposalV1):
        return _blocked(BLOCK_PROPOSAL_INVALID, case_id=context.case_id)

    profile = dict(context.workbook_profile)
    columns = {
        str(item.get("column_ref") or "").strip(): item
        for item in profile.get("columns") or []
        if isinstance(item, dict) and str(item.get("column_ref") or "").strip()
    }
    relationships = {
        (
            str(item.get("left_column_ref") or "").strip(),
            str(item.get("right_column_ref") or "").strip(),
        ): item
        for item in profile.get("relationships") or []
        if isinstance(item, dict)
        and str(item.get("left_column_ref") or "").strip()
        and str(item.get("right_column_ref") or "").strip()
    }
    evidence_registry = dict(context.evidence_registry)
    allowed_roles = set(context.allowed_semantic_roles)
    relevant_roles = set(context.capability_relevant_roles)
    deterministic_pairs = _deterministic_role_variable_pairs(context)
    scope_index = _semantic_scope_index(profile)

    hard_error = _hard_validate_refs_and_evidence(
        proposal=proposal,
        columns=columns,
        evidence_registry=evidence_registry,
        allowed_roles=allowed_roles,
        deterministic_pairs=deterministic_pairs,
        relationships=relationships,
        scope_index=scope_index,
    )
    if hard_error is not None:
        return _blocked(hard_error[0], case_id=context.case_id, detail=hard_error[1])

    decisions: list[Service1ValidatedSemanticDecisionV1] = []
    for item in proposal.concept_proposals:
        decisions.append(
            _concept_decision(
                item=item,
                relevant_roles=relevant_roles,
                deterministic_pairs=deterministic_pairs,
                scope_index=scope_index,
            )
        )
    for item in proposal.relationship_proposals:
        decisions.append(
            _relationship_decision(item=item, relationships=relationships, scope_index=scope_index)
        )
    for item in proposal.duplicate_semantics:
        decisions.append(
            _duplicate_decision(item=item, relevant_roles=relevant_roles, scope_index=scope_index)
        )
    for ref in proposal.irrelevant_refs:
        decisions.append(
            Service1ValidatedSemanticDecisionV1(
                decision_id=f"irrelevant:{ref}",
                source_kind="IRRELEVANT_REF",
                status=DECISION_IRRELEVANT_FOR_CAPABILITY,
                target_refs=(ref,),
                semantic_role=None,
                variable_name=None,
                relationship_type=None,
                confidence=1.0,
                evidence_refs=(),
                rationale=None,
                reason="LLM marked real column as irrelevant for requested capability.",
            )
        )
    for item in proposal.material_ambiguities:
        decisions.append(_ambiguity_decision(item, scope_index=scope_index))

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "detail": None,
        "case_id": context.case_id,
        "requested_capability": context.requested_capability,
        "decisions": [item.to_dict() for item in decisions],
        "decision_count": len(decisions),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _hard_validate_refs_and_evidence(
    *,
    proposal: Service1LLMSemanticProposalV1,
    columns: dict[str, dict[str, Any]],
    evidence_registry: dict[str, Any],
    allowed_roles: set[str],
    deterministic_pairs: set[tuple[str, str]],
    relationships: dict[tuple[str, str], dict[str, Any]],
    scope_index: dict[str, dict[str, Any]],
) -> tuple[str, Any] | None:
    real_refs = set(columns)

    for item in proposal.concept_proposals:
        missing = set(item.target_column_refs) - real_refs
        if missing:
            return BLOCK_COLUMN_REF_NOT_FOUND, sorted(missing)
        missing_evidence = set(item.evidence_refs) - set(evidence_registry)
        if missing_evidence:
            return BLOCK_EVIDENCE_REF_NOT_FOUND, sorted(missing_evidence)
        if item.semantic_role not in allowed_roles:
            return BLOCK_SEMANTIC_ROLE_NOT_ALLOWED, item.semantic_role
        if deterministic_pairs and (item.semantic_role, item.variable_name) not in deterministic_pairs:
            return BLOCK_VARIABLE_NAME_INCOMPATIBLE, {
                "semantic_role": item.semantic_role,
                "variable_name": item.variable_name,
            }
        if scope_index:
            scopes = [scope_index.get(ref) for ref in item.target_column_refs]
            if any(scope is None or scope.get("scope_state") != "RESOLVED" for scope in scopes):
                return BLOCK_LOGICAL_TABLE_SCOPE_UNRESOLVED, list(item.target_column_refs)
            tables = {str(scope.get("logical_table_ref") or "") for scope in scopes if scope is not None}
            resolved_grains = {
                str(scope.get("grain_ref") or "")
                for scope in scopes
                if scope is not None and scope.get("grain_state") == "RESOLVED" and scope.get("grain_ref")
            }
            if len(tables) != 1 or len(resolved_grains) > 1:
                return BLOCK_LOGICAL_TABLE_SCOPE_INCOMPATIBLE, {
                    "target_refs": list(item.target_column_refs),
                    "logical_table_refs": sorted(tables),
                    "grain_refs": sorted(resolved_grains),
                }

    for item in proposal.relationship_proposals:
        missing = {item.left_column_ref, item.right_column_ref} - real_refs
        if missing:
            return BLOCK_COLUMN_REF_NOT_FOUND, sorted(missing)
        missing_evidence = set(item.evidence_refs) - set(evidence_registry)
        if missing_evidence:
            return BLOCK_EVIDENCE_REF_NOT_FOUND, sorted(missing_evidence)
        structural = relationships.get((item.left_column_ref, item.right_column_ref))
        if structural is None:
            return BLOCK_RELATIONSHIP_REF_NOT_FOUND, {
                "left": item.left_column_ref,
                "right": item.right_column_ref,
            }
        expected = str(structural.get("relationship_kind") or "").strip()
        if expected and item.relationship_type != expected:
            return BLOCK_RELATIONSHIP_TYPE_INCOMPATIBLE, {
                "proposed": item.relationship_type,
                "structural": expected,
            }

    for item in proposal.duplicate_semantics:
        missing = set(item.column_refs) - real_refs
        if missing:
            return BLOCK_COLUMN_REF_NOT_FOUND, sorted(missing)
        missing_evidence = set(item.evidence_refs) - set(evidence_registry)
        if missing_evidence:
            return BLOCK_EVIDENCE_REF_NOT_FOUND, sorted(missing_evidence)
        if item.proposed_shared_role not in allowed_roles:
            return BLOCK_SEMANTIC_ROLE_NOT_ALLOWED, item.proposed_shared_role

    missing_irrelevant = set(proposal.irrelevant_refs) - real_refs
    if missing_irrelevant:
        return BLOCK_COLUMN_REF_NOT_FOUND, sorted(missing_irrelevant)

    for item in proposal.material_ambiguities:
        missing = set(item.target_refs) - real_refs - {
            relationship_ref
            for relationship_ref in _relationship_refs(relationships)
        }
        if missing:
            return BLOCK_COLUMN_REF_NOT_FOUND, sorted(missing)
        missing_evidence = set(item.evidence_refs) - set(evidence_registry)
        if missing_evidence:
            return BLOCK_EVIDENCE_REF_NOT_FOUND, sorted(missing_evidence)

    return None


def _concept_decision(
    *,
    item: Service1LLMConceptProposalV1,
    relevant_roles: set[str],
    deterministic_pairs: set[tuple[str, str]],
    scope_index: dict[str, dict[str, Any]],
) -> Service1ValidatedSemanticDecisionV1:
    relevant = not relevant_roles or item.semantic_role in relevant_roles
    if not relevant:
        status = DECISION_IRRELEVANT_FOR_CAPABILITY
        reason = "Role is valid but not relevant to requested capability."
    elif item.confidence >= CONFIDENT_THRESHOLD:
        status = DECISION_MATERIAL_CONFIDENT
        reason = None
    else:
        status = DECISION_MATERIAL_AMBIGUOUS
        reason = "Proposal confidence is below deterministic confidence threshold."
    if deterministic_pairs and (item.semantic_role, item.variable_name) not in deterministic_pairs:
        status = DECISION_CONFLICTING_EVIDENCE
        reason = "Semantic role and variable pair conflicts with deterministic hypotheses."
    scope = _decision_scope(tuple(item.target_column_refs), scope_index)
    return Service1ValidatedSemanticDecisionV1(
        decision_id=item.proposal_id,
        source_kind="CONCEPT",
        status=status,
        target_refs=tuple(item.target_column_refs),
        semantic_role=item.semantic_role,
        variable_name=item.variable_name,
        relationship_type=None,
        confidence=item.confidence,
        evidence_refs=tuple(item.evidence_refs),
        rationale=item.rationale,
        reason=reason,
        logical_table_refs=scope["logical_table_refs"],
        region_refs=scope["region_refs"],
        grain_refs=scope["grain_refs"],
        grain_states=scope["grain_states"],
        relationship_context_refs=scope["relationship_context_refs"],
        scope_conflict_reason=scope["scope_conflict_reason"],
    )


def _relationship_decision(
    *,
    item: Service1LLMRelationshipProposalV1,
    relationships: dict[tuple[str, str], dict[str, Any]],
    scope_index: dict[str, dict[str, Any]],
) -> Service1ValidatedSemanticDecisionV1:
    structural = relationships[(item.left_column_ref, item.right_column_ref)]
    structural_kind = str(structural.get("relationship_kind") or "").strip()
    status = (
        DECISION_MATERIAL_CONFIDENT
        if item.confidence >= CONFIDENT_THRESHOLD and item.relationship_type == structural_kind
        else DECISION_MATERIAL_AMBIGUOUS
    )
    scope = _decision_scope((item.left_column_ref, item.right_column_ref), scope_index)
    return Service1ValidatedSemanticDecisionV1(
        decision_id=item.relationship_id,
        source_kind="RELATIONSHIP",
        status=status,
        target_refs=(item.left_column_ref, item.right_column_ref),
        semantic_role=None,
        variable_name=None,
        relationship_type=item.relationship_type,
        confidence=item.confidence,
        evidence_refs=tuple(item.evidence_refs),
        rationale=item.rationale,
        reason=None if status == DECISION_MATERIAL_CONFIDENT else "Relationship needs owner confirmation.",
        logical_table_refs=scope["logical_table_refs"],
        region_refs=scope["region_refs"],
        grain_refs=scope["grain_refs"],
        grain_states=scope["grain_states"],
        relationship_context_refs=scope["relationship_context_refs"],
        scope_conflict_reason=scope["scope_conflict_reason"],
    )


def _duplicate_decision(
    *,
    item: Service1LLMDuplicateSemanticProposalV1,
    relevant_roles: set[str],
    scope_index: dict[str, dict[str, Any]],
) -> Service1ValidatedSemanticDecisionV1:
    if relevant_roles and item.proposed_shared_role not in relevant_roles:
        status = DECISION_IRRELEVANT_FOR_CAPABILITY
        reason = "Shared role is valid but not relevant to requested capability."
    else:
        status = (
            DECISION_MATERIAL_CONFIDENT
            if item.confidence >= CONFIDENT_THRESHOLD
            else DECISION_MATERIAL_AMBIGUOUS
        )
        reason = None if status == DECISION_MATERIAL_CONFIDENT else "Duplicate semantic proposal needs owner confirmation."
    scope = _decision_scope(tuple(item.column_refs), scope_index)
    if scope["scope_conflict_reason"] is not None:
        status = DECISION_CONFLICTING_EVIDENCE
        reason = scope["scope_conflict_reason"]
    return Service1ValidatedSemanticDecisionV1(
        decision_id=item.duplicate_id,
        source_kind="DUPLICATE_SEMANTICS",
        status=status,
        target_refs=tuple(item.column_refs),
        semantic_role=item.proposed_shared_role,
        variable_name=None,
        relationship_type=None,
        confidence=item.confidence,
        evidence_refs=tuple(item.evidence_refs),
        rationale=item.rationale,
        reason=reason,
        logical_table_refs=scope["logical_table_refs"],
        region_refs=scope["region_refs"],
        grain_refs=scope["grain_refs"],
        grain_states=scope["grain_states"],
        relationship_context_refs=scope["relationship_context_refs"],
        scope_conflict_reason=scope["scope_conflict_reason"],
    )


def _ambiguity_decision(
    item: Service1LLMMaterialAmbiguityV1,
    *,
    scope_index: dict[str, dict[str, Any]],
) -> Service1ValidatedSemanticDecisionV1:
    scope = _decision_scope(tuple(item.target_refs), scope_index)
    return Service1ValidatedSemanticDecisionV1(
        decision_id=item.ambiguity_id,
        source_kind="MATERIAL_AMBIGUITY",
        status=DECISION_MATERIAL_AMBIGUOUS,
        target_refs=tuple(item.target_refs),
        semantic_role=None,
        variable_name=None,
        relationship_type=None,
        confidence=item.confidence,
        evidence_refs=tuple(item.evidence_refs),
        rationale=None,
        reason=item.reason,
        logical_table_refs=scope["logical_table_refs"],
        region_refs=scope["region_refs"],
        grain_refs=scope["grain_refs"],
        grain_states=scope["grain_states"],
        relationship_context_refs=scope["relationship_context_refs"],
        scope_conflict_reason=scope["scope_conflict_reason"],
    )


def _semantic_scope_index(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scopes = [
        dict(item)
        for item in profile.get("logical_table_scopes") or ()
        if isinstance(item, dict)
    ]
    if not scopes:
        return {}
    result: dict[str, dict[str, Any]] = {}
    by_identity: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for scope in scopes:
        direct = str(scope.get("column_ref") or "").strip()
        if direct:
            result[direct] = scope
        identity = (
            str(scope.get("sheet_ref") or "").strip(),
            _normalize_scope_header(scope.get("normalized_header")),
        )
        if all(identity):
            by_identity.setdefault(identity, []).append(scope)
    for column in profile.get("columns") or ():
        if not isinstance(column, dict):
            continue
        ref = str(column.get("column_ref") or "").strip()
        identity = (
            str(column.get("sheet_name") or column.get("sheet_ref") or "").strip(),
            _normalize_scope_header(
                column.get("normalized_header")
                or column.get("normalized_column_name")
                or column.get("column_name")
            ),
        )
        matches = by_identity.get(identity, [])
        if ref and len(matches) == 1:
            result[ref] = matches[0]
    return result


def _decision_scope(
    target_refs: tuple[str, ...],
    scope_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scopes = [scope_index[ref] for ref in target_refs if ref in scope_index]
    tables = tuple(dict.fromkeys(
        str(scope.get("logical_table_ref") or "").strip()
        for scope in scopes
        if str(scope.get("logical_table_ref") or "").strip()
    ))
    regions = tuple(dict.fromkeys(
        str(ref).strip()
        for scope in scopes
        for ref in (scope.get("region_refs") or ())
        if str(ref).strip()
    ))
    grain_refs = tuple(dict.fromkeys(
        str(scope.get("grain_ref") or "").strip()
        for scope in scopes
        if str(scope.get("grain_ref") or "").strip()
    ))
    grain_states = tuple(dict.fromkeys(
        str(scope.get("grain_state") or "UNRESOLVED").strip()
        for scope in scopes
    ))
    relationship_refs = tuple(dict.fromkeys(
        str(ref).strip()
        for scope in scopes
        for ref in (scope.get("relationship_context_refs") or ())
        if str(ref).strip()
    ))
    conflict: str | None = None
    if scope_index and len(scopes) != len(target_refs):
        conflict = "LOGICAL_TABLE_SCOPE_UNRESOLVED"
    elif len(tables) > 1:
        conflict = "CROSS_TABLE_SCOPE_CONFLICT"
    elif len(grain_refs) > 1:
        conflict = "CROSS_GRAIN_SCOPE_CONFLICT"
    elif any(scope.get("scope_state") != "RESOLVED" for scope in scopes):
        conflict = "LOGICAL_TABLE_SCOPE_UNRESOLVED"
    return {
        "logical_table_refs": tables,
        "region_refs": regions,
        "grain_refs": grain_refs,
        "grain_states": grain_states,
        "relationship_context_refs": relationship_refs,
        "scope_conflict_reason": conflict,
    }


def _normalize_scope_header(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _deterministic_role_variable_pairs(context: Service1LLMSemanticContextV1) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for hypothesis in context.deterministic_hypotheses:
        role = str(hypothesis.get("semantic_role") or hypothesis.get("primary_semantic_role") or "").strip()
        variable = str(hypothesis.get("variable_name") or hypothesis.get("primary_variable_name") or "").strip()
        if role and variable:
            result.add((role, variable))
        candidates = hypothesis.get("candidate_meanings")
        if isinstance(candidates, (list, tuple)):
            for raw in candidates:
                if not isinstance(raw, dict):
                    continue
                candidate_role = str(raw.get("semantic_role") or "").strip()
                candidate_variable = str(raw.get("variable_name") or "").strip()
                if candidate_role and candidate_variable:
                    result.add((candidate_role, candidate_variable))
    return result


def _relationship_refs(relationships: dict[tuple[str, str], dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for item in relationships.values():
        ref = str(item.get("relationship_ref") or "").strip()
        if ref:
            refs.add(ref)
    return refs


def _blocked(reason: str, *, case_id: str | None = None, detail: Any = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "case_id": case_id,
        "requested_capability": None,
        "decisions": [],
        "decision_count": 0,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "DECISION_MATERIAL_CONFIDENT",
    "DECISION_MATERIAL_AMBIGUOUS",
    "DECISION_IRRELEVANT_FOR_CAPABILITY",
    "DECISION_CONFLICTING_EVIDENCE",
    "BLOCK_CONTEXT_INVALID",
    "BLOCK_PROPOSAL_INVALID",
    "BLOCK_COLUMN_REF_NOT_FOUND",
    "BLOCK_EVIDENCE_REF_NOT_FOUND",
    "BLOCK_SEMANTIC_ROLE_NOT_ALLOWED",
    "BLOCK_VARIABLE_NAME_INCOMPATIBLE",
    "BLOCK_RELATIONSHIP_REF_NOT_FOUND",
    "BLOCK_RELATIONSHIP_TYPE_INCOMPATIBLE",
    "BLOCK_LOGICAL_TABLE_SCOPE_UNRESOLVED",
    "BLOCK_LOGICAL_TABLE_SCOPE_INCOMPATIBLE",
    "CONFIDENT_THRESHOLD",
    "Service1ValidatedSemanticDecisionV1",
    "validate_service_1_semantic_proposal_v1",
]
