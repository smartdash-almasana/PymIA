"""Servicio 1 — owner semantic dialogue planner V1.

ADR-029 / SEM-4. Converts a ready SEM-3 validated semantic proposal into a
minimal, traceable owner dialogue plan. No LLM calls, persistence, owner-event
creation, calculation or runtime/delivery authority live here.

Planning policy:
- irrelevant decisions generate zero owner questions;
- one validated relationship generates one relationship decision;
- confident concept decisions may be grouped;
- concept decisions already explained by a relationship are absorbed into that
  relationship decision to avoid duplicate questions;
- ambiguous/conflicting decisions remain explicit;
- group rejection decomposes to atomic decisions instead of blocking.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Final

from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    DECISION_CONFLICTING_EVIDENCE,
    DECISION_IRRELEVANT_FOR_CAPABILITY,
    DECISION_MATERIAL_AMBIGUOUS,
    DECISION_MATERIAL_CONFIDENT,
    SCHEMA_VERSION as VALIDATOR_SCHEMA_VERSION,
    STATUS_READY as VALIDATED_READY,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_OWNER_SEMANTIC_DIALOGUE_V1"
STATUS_READY: Final[str] = "OWNER_DIALOGUE_PLAN_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

DECISION_KIND_SEMANTIC_GROUP: Final[str] = "SEMANTIC_GROUP"
DECISION_KIND_RELATIONSHIP: Final[str] = "RELATIONSHIP"
DECISION_KIND_UNIT_MEANING: Final[str] = "UNIT_MEANING"
DECISION_KIND_CONFLICT: Final[str] = "CONFLICT"
DECISION_KIND_NOT_APPLICABLE: Final[str] = "NOT_APPLICABLE"

FALLBACK_DECOMPOSE_TO_ATOMIC: Final[str] = "DECOMPOSE_TO_ATOMIC"
FALLBACK_REQUIRE_TARGETED_CORRECTION: Final[str] = "REQUIRE_TARGETED_CORRECTION"
FALLBACK_BLOCK_IF_UNRESOLVABLE: Final[str] = "BLOCK_IF_UNRESOLVABLE"

ACTION_ACCEPT: Final[str] = "ACCEPT"
ACTION_REJECT: Final[str] = "REJECT"
ACTION_CORRECT: Final[str] = "CORRECT"

RESPONSE_GROUP_CONFIRMED: Final[str] = "GROUP_CONFIRMED"
RESPONSE_RELATIONSHIP_CONFIRMED: Final[str] = "RELATIONSHIP_CONFIRMED"
RESPONSE_DECISION_CONFIRMED: Final[str] = "DECISION_CONFIRMED"
RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION: Final[str] = "GROUP_REJECTED_REQUIRES_DECOMPOSITION"
RESPONSE_NEEDS_GRANULAR_CONFIRMATION: Final[str] = "NEEDS_GRANULAR_CONFIRMATION"
RESPONSE_TARGETED_CORRECTION_PROPOSED: Final[str] = "TARGETED_CORRECTION_PROPOSED"
RESPONSE_BLOCKED: Final[str] = "BLOCKED"

BLOCK_VALIDATED_PACKET_INVALID: Final[str] = "BLOCK_DIALOGUE_VALIDATED_PACKET_INVALID"
BLOCK_VALIDATED_PACKET_AUTHORITY_FORBIDDEN: Final[str] = "BLOCK_DIALOGUE_VALIDATED_PACKET_AUTHORITY_FORBIDDEN"
BLOCK_DUPLICATE_VALIDATED_DECISION: Final[str] = "BLOCK_DIALOGUE_DUPLICATE_VALIDATED_DECISION"
BLOCK_DIALOGUE_DECISION_NOT_FOUND: Final[str] = "BLOCK_DIALOGUE_DECISION_NOT_FOUND"
BLOCK_DIALOGUE_ACTION_INVALID: Final[str] = "BLOCK_DIALOGUE_ACTION_INVALID"
BLOCK_DIALOGUE_TARGETED_REFS_INVALID: Final[str] = "BLOCK_DIALOGUE_TARGETED_REFS_INVALID"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


@dataclass(frozen=True)
class Service1OwnerDialogueDecisionV1:
    decision_id: str
    decision_kind: str
    proposal_refs: tuple[str, ...]
    column_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    presentation_text: str
    materiality_reason: str
    accept_action: str
    reject_action: str
    correction_action: str
    fallback_strategy: str
    atomic_children: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_kind": self.decision_kind,
            "proposal_refs": list(self.proposal_refs),
            "column_refs": list(self.column_refs),
            "relationship_refs": list(self.relationship_refs),
            "presentation_text": self.presentation_text,
            "materiality_reason": self.materiality_reason,
            "accept_action": self.accept_action,
            "reject_action": self.reject_action,
            "correction_action": self.correction_action,
            "fallback_strategy": self.fallback_strategy,
            "atomic_children": [dict(item) for item in self.atomic_children],
        }


def build_service_1_owner_dialogue_plan_v1(
    *,
    validated_packet: Any,
    atomic_confirmation: bool = False,
) -> dict[str, Any]:
    """Build the owner dialogue plan from a SEM-3 ready packet.

    ``atomic_confirmation=True`` preserves one owner transaction per semantic
    concept instead of grouping confident concepts. This is the interactive
    Servicio 1 mode: one column, one confirmation/correction, then the next.
    The default remains grouped for backwards compatibility with existing
    consumers and tests.
    """
    if not _valid_validated_packet(validated_packet):
        return _blocked(BLOCK_VALIDATED_PACKET_INVALID)
    if any(bool(validated_packet.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(
            BLOCK_VALIDATED_PACKET_AUTHORITY_FORBIDDEN,
            case_id=validated_packet.get("case_id"),
        )

    raw_decisions = validated_packet.get("decisions") or []
    ids = [str(item.get("decision_id") or "").strip() for item in raw_decisions]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        return _blocked(
            BLOCK_DUPLICATE_VALIDATED_DECISION,
            case_id=validated_packet.get("case_id"),
        )

    active = [
        dict(item)
        for item in raw_decisions
        if item.get("status") != DECISION_IRRELEVANT_FOR_CAPABILITY
    ]
    suppressed_refs = _ordered_unique(
        ref
        for item in raw_decisions
        if item.get("status") == DECISION_IRRELEVANT_FOR_CAPABILITY
        for ref in item.get("target_refs") or []
    )

    ambiguous_refs = {
        str(ref)
        for item in active
        if item.get("status") in {DECISION_MATERIAL_AMBIGUOUS, DECISION_CONFLICTING_EVIDENCE}
        for ref in item.get("target_refs") or []
    }

    relation_items = _deduplicate_mirror_relationships(
        [item for item in active if item.get("source_kind") == "RELATIONSHIP"]
    )
    concept_items = [
        item
        for item in active
        if item.get("source_kind") in {"CONCEPT", "DUPLICATE_SEMANTICS"}
    ]
    ambiguity_items = [
        item
        for item in active
        if item.get("source_kind") != "RELATIONSHIP"
        and (
            item.get("source_kind") == "MATERIAL_AMBIGUITY"
            or item.get("status") in {DECISION_MATERIAL_AMBIGUOUS, DECISION_CONFLICTING_EVIDENCE}
        )
    ]

    planned: list[Service1OwnerDialogueDecisionV1] = []
    absorbed_proposal_ids: set[str] = set()

    for relation in relation_items:
        endpoints = tuple(str(ref) for ref in relation.get("target_refs") or ())
        absorbed = [
            item
            for item in concept_items
            if item.get("status") == DECISION_MATERIAL_CONFIDENT
            and set(str(ref) for ref in item.get("target_refs") or ()).issubset(set(endpoints))
            and not set(str(ref) for ref in item.get("target_refs") or ()).intersection(ambiguous_refs)
        ]
        absorbed_proposal_ids.update(str(item["decision_id"]) for item in absorbed)
        relationship_proposal_refs = tuple(
            str(ref)
            for ref in relation.get("mirror_decision_ids") or (relation["decision_id"],)
        )
        proposal_refs = relationship_proposal_refs + tuple(
            str(item["decision_id"]) for item in absorbed
        )
        relationship_ref = "->".join(endpoints)
        planned.append(
            Service1OwnerDialogueDecisionV1(
                decision_id=f"dialogue:relationship:{relation['decision_id']}",
                decision_kind=DECISION_KIND_RELATIONSHIP,
                proposal_refs=proposal_refs,
                column_refs=endpoints,
                relationship_refs=(relationship_ref,),
                presentation_text=_relationship_text(endpoints),
                materiality_reason="La relación entre estas columnas es material para vincular evidencia entre hojas.",
                accept_action=ACTION_ACCEPT,
                reject_action=ACTION_REJECT,
                correction_action=ACTION_CORRECT,
                fallback_strategy=FALLBACK_DECOMPOSE_TO_ATOMIC,
                atomic_children=tuple(_atomic_child(item) for item in absorbed),
            )
        )

    confident_concepts = [
        item
        for item in concept_items
        if item.get("status") == DECISION_MATERIAL_CONFIDENT
        and str(item.get("decision_id")) not in absorbed_proposal_ids
        and not set(str(ref) for ref in item.get("target_refs") or ()).intersection(ambiguous_refs)
    ]
    if confident_concepts:
        if atomic_confirmation:
            for item in confident_concepts:
                refs = tuple(str(ref) for ref in item.get("target_refs") or ())
                planned.append(
                    Service1OwnerDialogueDecisionV1(
                        decision_id=f"dialogue:atomic:{item['decision_id']}",
                        decision_kind=DECISION_KIND_UNIT_MEANING,
                        proposal_refs=(str(item["decision_id"]),),
                        column_refs=refs,
                        relationship_refs=(),
                        presentation_text=_atomic_semantic_text(item, refs),
                        materiality_reason=str(
                            item.get("reason")
                            or item.get("rationale")
                            or "PymIA propone este significado a partir del nombre, tipo y contexto de la columna."
                        ),
                        accept_action=ACTION_ACCEPT,
                        reject_action=ACTION_REJECT,
                        correction_action=ACTION_CORRECT,
                        fallback_strategy=FALLBACK_REQUIRE_TARGETED_CORRECTION,
                        atomic_children=(),
                    )
                )
        else:
            proposal_refs = tuple(str(item["decision_id"]) for item in confident_concepts)
            column_refs = _ordered_unique(
                str(ref)
                for item in confident_concepts
                for ref in item.get("target_refs") or []
            )
            planned.append(
                Service1OwnerDialogueDecisionV1(
                    decision_id="dialogue:semantic-group:" + "+".join(proposal_refs),
                    decision_kind=DECISION_KIND_SEMANTIC_GROUP,
                    proposal_refs=proposal_refs,
                    column_refs=column_refs,
                    relationship_refs=(),
                    presentation_text=_semantic_group_text(column_refs),
                    materiality_reason="Estas interpretaciones son materiales para el control solicitado y pueden confirmarse juntas.",
                    accept_action=ACTION_ACCEPT,
                    reject_action=ACTION_REJECT,
                    correction_action=ACTION_CORRECT,
                    fallback_strategy=FALLBACK_DECOMPOSE_TO_ATOMIC,
                    atomic_children=tuple(_atomic_child(item) for item in confident_concepts),
                )
            )

    seen_ambiguity_ids: set[str] = set()
    for item in ambiguity_items:
        item_id = str(item["decision_id"])
        if item_id in seen_ambiguity_ids:
            continue
        seen_ambiguity_ids.add(item_id)
        refs = tuple(str(ref) for ref in item.get("target_refs") or ())
        kind = (
            DECISION_KIND_CONFLICT
            if item.get("status") == DECISION_CONFLICTING_EVIDENCE
            or item.get("source_kind") == "MATERIAL_AMBIGUITY"
            else DECISION_KIND_UNIT_MEANING
        )
        planned.append(
            Service1OwnerDialogueDecisionV1(
                decision_id=f"dialogue:atomic:{item_id}",
                decision_kind=kind,
                proposal_refs=(item_id,),
                column_refs=tuple(ref for ref in refs if "->" not in ref),
                relationship_refs=tuple(ref for ref in refs if "->" in ref),
                presentation_text=_ambiguity_text(refs, conflict=(kind == DECISION_KIND_CONFLICT)),
                materiality_reason=str(item.get("reason") or "La interpretación necesita confirmación empresarial explícita."),
                accept_action=ACTION_ACCEPT,
                reject_action=ACTION_REJECT,
                correction_action=ACTION_CORRECT,
                fallback_strategy=FALLBACK_REQUIRE_TARGETED_CORRECTION,
                atomic_children=(),
            )
        )

    _assert_no_duplicate_owner_questions(planned)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": validated_packet.get("case_id"),
        "requested_capability": validated_packet.get("requested_capability"),
        "decisions": [item.to_dict() for item in planned],
        "question_count": len(planned),
        "suppressed_irrelevant_refs": list(suppressed_refs),
        "zero_duplicate_questions": True,
        "zero_irrelevant_questions": True,
        "all_material_ambiguities_surfaced": _all_material_ambiguities_surfaced(active, planned),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def apply_service_1_owner_dialogue_response_v1(
    *,
    dialogue_plan: Any,
    decision_id: str,
    action: str,
    correction_text: str | None = None,
    targeted_refs: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """Resolve SEM-4 dialogue state only; SEM-5 creates canonical owner events."""
    if not isinstance(dialogue_plan, dict) or dialogue_plan.get("schema_version") != SCHEMA_VERSION or dialogue_plan.get("status") != STATUS_READY:
        return _response_blocked(BLOCK_VALIDATED_PACKET_INVALID)
    target_id = str(decision_id or "").strip()
    decision = next(
        (item for item in dialogue_plan.get("decisions") or [] if item.get("decision_id") == target_id),
        None,
    )
    if not isinstance(decision, dict):
        return _response_blocked(BLOCK_DIALOGUE_DECISION_NOT_FOUND)
    normalized_action = str(action or "").strip().upper()
    if normalized_action not in {ACTION_ACCEPT, ACTION_REJECT, ACTION_CORRECT}:
        return _response_blocked(BLOCK_DIALOGUE_ACTION_INVALID)

    if normalized_action == ACTION_ACCEPT:
        if decision.get("decision_kind") == DECISION_KIND_SEMANTIC_GROUP:
            response_status = RESPONSE_GROUP_CONFIRMED
        elif decision.get("decision_kind") == DECISION_KIND_RELATIONSHIP:
            response_status = RESPONSE_RELATIONSHIP_CONFIRMED
        else:
            response_status = RESPONSE_DECISION_CONFIRMED
        return _response_ready(
            status=response_status,
            decision=decision,
            action=normalized_action,
            atomic_decisions=[],
        )

    if normalized_action == ACTION_REJECT:
        atomic = _decomposed_atomic_decisions(decision)
        return _response_ready(
            status=(
                RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION
                if decision.get("decision_kind") in {DECISION_KIND_SEMANTIC_GROUP, DECISION_KIND_RELATIONSHIP}
                else RESPONSE_NEEDS_GRANULAR_CONFIRMATION
            ),
            decision=decision,
            action=normalized_action,
            atomic_decisions=atomic,
        )

    correction = str(correction_text or "").strip()
    declared_targets = tuple(str(ref).strip() for ref in (targeted_refs or ()) if str(ref).strip())
    allowed_targets = set(decision.get("column_refs") or ()) | set(decision.get("relationship_refs") or ())
    if correction and declared_targets and set(declared_targets).issubset(allowed_targets):
        return _response_ready(
            status=RESPONSE_TARGETED_CORRECTION_PROPOSED,
            decision=decision,
            action=normalized_action,
            atomic_decisions=[],
            correction_text=correction,
            targeted_refs=declared_targets,
        )

    atomic = _decomposed_atomic_decisions(decision)
    return _response_ready(
        status=RESPONSE_NEEDS_GRANULAR_CONFIRMATION,
        decision=decision,
        action=normalized_action,
        atomic_decisions=atomic,
        correction_text=correction or None,
        targeted_refs=declared_targets,
    )


def _valid_validated_packet(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema_version") == VALIDATOR_SCHEMA_VERSION
        and value.get("status") == VALIDATED_READY
        and isinstance(value.get("decisions"), list)
    )


def _deduplicate_mirror_relationships(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], dict[str, Any]] = {}
    order: list[tuple[str, ...]] = []
    for item in items:
        endpoints = tuple(str(ref) for ref in item.get("target_refs") or ())
        key = tuple(sorted(endpoints))
        if key not in grouped:
            grouped[key] = dict(item)
            grouped[key]["mirror_decision_ids"] = [str(item.get("decision_id") or "")]
            order.append(key)
            continue
        grouped[key]["mirror_decision_ids"].append(str(item.get("decision_id") or ""))
    return [grouped[key] for key in order]


def _ordered_unique(values: Any) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def _display_ref(ref: str) -> str:
    return ref.split(".", 1)[1] if "." in ref else ref


def _semantic_group_text(column_refs: tuple[str, ...]) -> str:
    labels = ", ".join(f"`{_display_ref(ref)}`" for ref in column_refs)
    return f"Interpreto {labels} como un conjunto coherente de datos para el control solicitado. ¿Es correcto?"


def _atomic_semantic_text(item: dict[str, Any], refs: tuple[str, ...]) -> str:
    label = _display_ref(refs[0]) if refs else "este dato"
    role = str(item.get("semantic_role") or item.get("proposed_meaning") or "").strip()
    variable = str(item.get("variable_name") or "").strip()
    meaning = role.replace("_", " ") if role else "un significado empresarial específico"
    if variable and variable != role:
        return f"PymIA interpreta `{label}` como {meaning} ({variable}). ¿Es correcto?"
    return f"PymIA interpreta `{label}` como {meaning}. ¿Es correcto?"


def _relationship_text(endpoints: tuple[str, ...]) -> str:
    if len(endpoints) >= 2:
        return f"`{endpoints[0]}` y `{endpoints[1]}` parecen identificar el mismo dato y permiten relacionar ambas hojas. ¿Es correcto?"
    return "Detecté una relación estructural material entre datos del workbook. ¿Es correcta?"


def _ambiguity_text(refs: tuple[str, ...], *, conflict: bool) -> str:
    labels = ", ".join(f"`{ref}`" for ref in refs)
    if conflict:
        return f"Hay evidencia incompatible sobre {labels}. Necesito que confirmes cómo debe interpretarse."
    return f"Necesito confirmar el significado empresarial de {labels} antes de usarlo. ¿Cómo debe interpretarse?"


def _atomic_child(item: dict[str, Any]) -> dict[str, Any]:
    refs = tuple(str(ref) for ref in item.get("target_refs") or ())
    return {
        "proposal_ref": str(item.get("decision_id") or ""),
        "column_refs": list(refs),
        "presentation_text": _ambiguity_text(refs, conflict=False),
        "fallback_strategy": FALLBACK_REQUIRE_TARGETED_CORRECTION,
    }


def _decomposed_atomic_decisions(decision: dict[str, Any]) -> list[dict[str, Any]]:
    children = decision.get("atomic_children") or []
    if children:
        return [dict(item) for item in children if isinstance(item, dict)]
    refs = list(decision.get("column_refs") or ()) + list(decision.get("relationship_refs") or ())
    return [
        {
            "proposal_ref": proposal_ref,
            "column_refs": list(refs),
            "presentation_text": _ambiguity_text(tuple(refs), conflict=False),
            "fallback_strategy": FALLBACK_REQUIRE_TARGETED_CORRECTION,
        }
        for proposal_ref in decision.get("proposal_refs") or ()
    ]


def _assert_no_duplicate_owner_questions(planned: list[Service1OwnerDialogueDecisionV1]) -> None:
    ids = [item.decision_id for item in planned]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate dialogue decision id")
    relationship_refs = [ref for item in planned for ref in item.relationship_refs]
    if len(relationship_refs) != len(set(relationship_refs)):
        raise AssertionError("duplicate relationship owner question")
    proposal_refs = [ref for item in planned for ref in item.proposal_refs]
    if len(proposal_refs) != len(set(proposal_refs)):
        raise AssertionError("same semantic proposal surfaced in more than one owner question")


def _all_material_ambiguities_surfaced(
    active: list[dict[str, Any]],
    planned: list[Service1OwnerDialogueDecisionV1],
) -> bool:
    required = {
        str(item.get("decision_id"))
        for item in active
        if item.get("status") in {DECISION_MATERIAL_AMBIGUOUS, DECISION_CONFLICTING_EVIDENCE}
        or item.get("source_kind") == "MATERIAL_AMBIGUITY"
    }
    surfaced = {ref for item in planned for ref in item.proposal_refs}
    return required.issubset(surfaced)


def _blocked(reason: str, *, case_id: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "requested_capability": None,
        "decisions": [],
        "question_count": 0,
        "suppressed_irrelevant_refs": [],
        "zero_duplicate_questions": False,
        "zero_irrelevant_questions": False,
        "all_material_ambiguities_surfaced": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _response_ready(
    *,
    status: str,
    decision: dict[str, Any],
    action: str,
    atomic_decisions: list[dict[str, Any]],
    correction_text: str | None = None,
    targeted_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocked_reason": None,
        "decision_id": decision.get("decision_id"),
        "decision_kind": decision.get("decision_kind"),
        "action": action,
        "proposal_refs": list(decision.get("proposal_refs") or ()),
        "column_refs": list(decision.get("column_refs") or ()),
        "relationship_refs": list(decision.get("relationship_refs") or ()),
        "atomic_decisions": atomic_decisions,
        "correction_text": correction_text,
        "targeted_refs": list(targeted_refs),
        "confirmed_by_owner": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


def _response_blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": RESPONSE_BLOCKED,
        "blocked_reason": reason,
        "decision_id": None,
        "decision_kind": None,
        "action": None,
        "proposal_refs": [],
        "column_refs": [],
        "relationship_refs": [],
        "atomic_decisions": [],
        "correction_text": None,
        "targeted_refs": [],
        "confirmed_by_owner": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "DECISION_KIND_SEMANTIC_GROUP",
    "DECISION_KIND_RELATIONSHIP",
    "DECISION_KIND_UNIT_MEANING",
    "DECISION_KIND_CONFLICT",
    "DECISION_KIND_NOT_APPLICABLE",
    "FALLBACK_DECOMPOSE_TO_ATOMIC",
    "FALLBACK_REQUIRE_TARGETED_CORRECTION",
    "FALLBACK_BLOCK_IF_UNRESOLVABLE",
    "ACTION_ACCEPT",
    "ACTION_REJECT",
    "ACTION_CORRECT",
    "RESPONSE_GROUP_CONFIRMED",
    "RESPONSE_RELATIONSHIP_CONFIRMED",
    "RESPONSE_DECISION_CONFIRMED",
    "RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION",
    "RESPONSE_NEEDS_GRANULAR_CONFIRMATION",
    "RESPONSE_TARGETED_CORRECTION_PROPOSED",
    "BLOCK_VALIDATED_PACKET_INVALID",
    "BLOCK_VALIDATED_PACKET_AUTHORITY_FORBIDDEN",
    "BLOCK_DUPLICATE_VALIDATED_DECISION",
    "BLOCK_DIALOGUE_DECISION_NOT_FOUND",
    "BLOCK_DIALOGUE_ACTION_INVALID",
    "Service1OwnerDialogueDecisionV1",
    "build_service_1_owner_dialogue_plan_v1",
    "apply_service_1_owner_dialogue_response_v1",
]
