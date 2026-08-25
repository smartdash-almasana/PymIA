"""Servicio 1 — SEM-8 assisted semantic wiring into the canonical product root.

This module is composition only. It does not parse XLSX, own semantic rules,
call a provider SDK, persist tenant memory, calculate business results or grant
runtime/delivery authority.

Initial pass:
canonical ingestion -> legacy deterministic bridge -> workbook profile ->
closed LLM context -> provider-neutral interpreter -> deterministic validator ->
minimal owner dialogue plan.

Owner reentry:
exact prior assisted state + explicit owner dialogue responses -> canonical
SEM-5 evidence -> SEM-6 adapter -> existing reinjection/P6 -> canonical
CONFIRMED_BINDINGS packet shape used by the existing product root.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as BRIDGE_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_capability_registry_v1 import get_capability_definition_v1
from pymia.smartpyme.service_1_derived_evidence_v1 import (
    service_1_derived_evidence_semantic_support_roles_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    VARIABLE_FAMILY_DEFINITIONS,
)
from pymia.smartpyme.service_1_computability_v1 import (
    CONFIRMED_BINDINGS_SCHEMA_VERSION,
)
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    Service1LLMConceptProposalV1,
    Service1LLMSemanticContextV1,
    Service1LLMSemanticContractErrorV1,
    Service1LLMSemanticProposalV1,
    build_service_1_llm_semantic_context_v1,
)
from pymia.smartpyme.service_1_llm_semantic_interpreter_v1 import (
    STATUS_READY as INTERPRETER_READY,
    interpret_service_1_semantics_v1,
)
from pymia.smartpyme.service_1_owner_semantic_answer_projection_v1 import (
    SCHEMA_VERSION as SEM5_SCHEMA_VERSION,
    STATUS_READY as SEM5_READY,
    project_service_1_owner_semantic_answer_v1,
)
from pymia.smartpyme.service_1_owner_semantic_dialogue_v1 import (
    ACTION_ACCEPT,
    ACTION_SKIP,
    RESPONSE_DECISION_CONFIRMED,
    RESPONSE_DECISION_SKIPPED,
    RESPONSE_GROUP_CONFIRMED,
    RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION,
    RESPONSE_NEEDS_GRANULAR_CONFIRMATION,
    RESPONSE_RELATIONSHIP_CONFIRMED,
    RESPONSE_TARGETED_CORRECTION_PROPOSED,
    STATUS_READY as DIALOGUE_READY,
    apply_service_1_owner_dialogue_response_v1,
    build_service_1_owner_dialogue_plan_v1,
)
from pymia.smartpyme.service_1_owner_semantic_evidence_reentry_v1 import (
    STATUS_READY as SEM6_READY,
    build_service_1_owner_semantic_evidence_reentry_v1,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    STATUS_READY as VALIDATOR_READY,
    validate_service_1_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_table_scoped_semantic_context_v1 import (
    STATUS_READY as TABLE_SCOPE_READY,
    enrich_service_1_deterministic_hypotheses_with_table_scope_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    STATUS_READY as PROFILE_READY,
    build_service_1_workbook_profile_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_ASSISTED_SEMANTIC_PRODUCT_WIRING_V1"
STATUS_OWNER_DIALOGUE_REQUIRED: Final[str] = "OWNER_DIALOGUE_REQUIRED"
STATUS_OWNER_DIALOGUE_FOLLOWUP: Final[str] = "OWNER_DIALOGUE_FOLLOWUP_REQUIRED"
STATUS_CONFIRMED: Final[str] = "CONFIRMED_BINDINGS"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_INGESTION_INVALID: Final[str] = "BLOCK_SEM8_INGESTION_INVALID"
BLOCK_CAPABILITY_REQUIRED: Final[str] = "BLOCK_SEM8_CAPABILITY_REQUIRED"
BLOCK_BRIDGE_FAILED: Final[str] = "BLOCK_SEM8_BRIDGE_FAILED"
BLOCK_PROFILE_FAILED: Final[str] = "BLOCK_SEM8_PROFILE_FAILED"
BLOCK_NO_ALLOWED_ROLES: Final[str] = "BLOCK_SEM8_NO_ALLOWED_SEMANTIC_ROLES"
BLOCK_CONTEXT_FAILED: Final[str] = "BLOCK_SEM8_CONTEXT_FAILED"
BLOCK_INTERPRETER_FAILED: Final[str] = "BLOCK_SEM8_INTERPRETER_FAILED"
BLOCK_VALIDATOR_FAILED: Final[str] = "BLOCK_SEM8_VALIDATOR_FAILED"
BLOCK_DIALOGUE_FAILED: Final[str] = "BLOCK_SEM8_DIALOGUE_FAILED"
BLOCK_STATE_INVALID: Final[str] = "BLOCK_SEM8_STATE_INVALID"
BLOCK_OWNER_IDENTITY_REQUIRED: Final[str] = "BLOCK_SEM8_OWNER_IDENTITY_REQUIRED"
BLOCK_OWNER_RESPONSES_INVALID: Final[str] = "BLOCK_SEM8_OWNER_RESPONSES_INVALID"
BLOCK_OWNER_RESPONSE_DUPLICATE: Final[str] = "BLOCK_SEM8_OWNER_RESPONSE_DUPLICATE"
BLOCK_OWNER_RESPONSE_UNKNOWN_DECISION: Final[str] = "BLOCK_SEM8_OWNER_RESPONSE_UNKNOWN_DECISION"
BLOCK_OWNER_RESPONSE_MISSING: Final[str] = "BLOCK_SEM8_OWNER_RESPONSE_MISSING"
BLOCK_OWNER_PROJECTION_FAILED: Final[str] = "BLOCK_SEM8_OWNER_PROJECTION_FAILED"
BLOCK_REENTRY_FAILED: Final[str] = "BLOCK_SEM8_REENTRY_FAILED"
BLOCK_OWNER_CORRECTION_INVALID: Final[str] = "BLOCK_SEM8_OWNER_CORRECTION_INVALID"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)
_ACCEPTED_DIALOGUE_STATUSES: Final[frozenset[str]] = frozenset(
    {RESPONSE_GROUP_CONFIRMED, RESPONSE_RELATIONSHIP_CONFIRMED, RESPONSE_DECISION_CONFIRMED}
)
_FOLLOWUP_DIALOGUE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        RESPONSE_GROUP_REJECTED_REQUIRES_DECOMPOSITION,
        RESPONSE_NEEDS_GRANULAR_CONFIRMATION,
        RESPONSE_TARGETED_CORRECTION_PROPOSED,
    }
)


def run_service_1_assisted_semantic_initial_v1(
    *,
    ingestion_output: Any,
    requested_capability: str | None,
    provider: Any,
    compatible_tenant_memory_hints: Sequence[Mapping[str, Any]] = (),
    semantic_scope_capabilities: Sequence[str] = (),
    atomic_confirmation: bool = False,
    table_scoped_semantics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one exact assisted semantic state and its minimal owner dialogue."""
    if not isinstance(ingestion_output, dict) or not ingestion_output:
        return _blocked(BLOCK_INGESTION_INVALID)
    capability = None if requested_capability is None else str(requested_capability).strip()
    if capability == "":
        return _blocked(BLOCK_CAPABILITY_REQUIRED, case_id=(ingestion_output.get("workbook_context") or {}).get("case_id") if isinstance(ingestion_output.get("workbook_context"), Mapping) else None)
    if any(bool(ingestion_output.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(BLOCK_INGESTION_INVALID, case_id=(ingestion_output.get("workbook_context") or {}).get("case_id") if isinstance(ingestion_output.get("workbook_context"), Mapping) else None)

    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=ingestion_output,
    )
    if bridge.get("status") != BRIDGE_READY:
        return _blocked(
            BLOCK_BRIDGE_FAILED,
            case_id=(ingestion_output.get("workbook_context") or {}).get("case_id") if isinstance(ingestion_output.get("workbook_context"), Mapping) else None,
            detail=bridge.get("blocked_reason"),
            bridge_packet=bridge,
        )

    profile = build_service_1_workbook_profile_v1(ingestion_output=ingestion_output)
    if profile.get("status") != PROFILE_READY:
        return _blocked(
            BLOCK_PROFILE_FAILED,
            case_id=bridge.get("case_id"),
            detail=profile.get("blocked_reason"),
            bridge_packet=bridge,
            workbook_profile=profile,
        )

    deterministic_hypotheses = _deterministic_hypotheses(bridge)
    semantic_scope_packet = None
    if table_scoped_semantics is not None:
        if (
            not isinstance(table_scoped_semantics, Mapping)
            or table_scoped_semantics.get("status") != TABLE_SCOPE_READY
        ):
            return _blocked(
                BLOCK_CONTEXT_FAILED,
                case_id=bridge.get("case_id"),
                detail=(
                    table_scoped_semantics.get("blocked_reason")
                    if isinstance(table_scoped_semantics, Mapping)
                    else "TABLE_SCOPED_SEMANTICS_PACKET_REQUIRED"
                ),
                bridge_packet=bridge,
                workbook_profile=profile,
            )
        semantic_scope_packet = dict(table_scoped_semantics)
        deterministic_hypotheses = enrich_service_1_deterministic_hypotheses_with_table_scope_v1(
            deterministic_hypotheses=deterministic_hypotheses,
            column_refs=tuple(
                item for item in (bridge.get("column_refs") or ()) if isinstance(item, Mapping)
            ),
            semantic_scope_packet=semantic_scope_packet,
        )
        profile = dict(profile)
        profile["table_scoped_semantics"] = semantic_scope_packet
        profile["logical_table_scopes"] = list(semantic_scope_packet.get("column_scopes") or ())

    allowed_roles = _allowed_roles(deterministic_hypotheses)
    if not allowed_roles:
        return _blocked(
            BLOCK_NO_ALLOWED_ROLES,
            case_id=bridge.get("case_id"),
            bridge_packet=bridge,
            workbook_profile=profile,
        )
    relevant_roles = (
        tuple(allowed_roles)
        if capability is None
        else _capability_relevant_roles(
            requested_capability=capability,
            deterministic_hypotheses=deterministic_hypotheses,
            allowed_roles=allowed_roles,
            semantic_scope_capabilities=semantic_scope_capabilities,
        )
    )
    try:
        context = build_service_1_llm_semantic_context_v1(
            case_id=str(bridge.get("case_id") or "").strip(),
            requested_capability=capability,
            workbook_profile=profile,
            deterministic_hypotheses=deterministic_hypotheses,
            allowed_semantic_roles=allowed_roles,
            capability_relevant_roles=relevant_roles,
            compatible_tenant_memory_hints=compatible_tenant_memory_hints,
        )
    except (Service1LLMSemanticContractErrorV1, TypeError, ValueError) as exc:
        return _blocked(
            BLOCK_CONTEXT_FAILED,
            case_id=bridge.get("case_id"),
            detail=getattr(exc, "code", type(exc).__name__),
            bridge_packet=bridge,
            workbook_profile=profile,
        )

    interpreted = interpret_service_1_semantics_v1(context=context, provider=provider)
    if interpreted.get("status") != INTERPRETER_READY:
        return _blocked(
            BLOCK_INTERPRETER_FAILED,
            case_id=bridge.get("case_id"),
            detail=interpreted.get("blocked_reason"),
            bridge_packet=bridge,
            workbook_profile=profile,
            context=context,
            interpreter_packet=interpreted,
        )

    validated = validate_service_1_semantic_proposal_v1(
        context=context,
        proposal=interpreted.get("proposal"),
    )
    if validated.get("status") != VALIDATOR_READY:
        return _blocked(
            BLOCK_VALIDATOR_FAILED,
            case_id=bridge.get("case_id"),
            detail=validated.get("blocked_reason"),
            bridge_packet=bridge,
            workbook_profile=profile,
            context=context,
            interpreter_packet=interpreted,
            validated_packet=validated,
        )

    dialogue = build_service_1_owner_dialogue_plan_v1(
        validated_packet=validated,
        # Workbook-first still preserves first-contact owner evidence, but
        # confident concepts are grouped so the owner is not turned into a
        # column-by-column parser. Capability-scoped callers keep their
        # existing confirmation mode.
        atomic_confirmation=(False if capability is None else atomic_confirmation),
    )
    if dialogue.get("status") != DIALOGUE_READY:
        return _blocked(
            BLOCK_DIALOGUE_FAILED,
            case_id=bridge.get("case_id"),
            detail=dialogue.get("blocked_reason"),
            bridge_packet=bridge,
            workbook_profile=profile,
            context=context,
            interpreter_packet=interpreted,
            validated_packet=validated,
            dialogue_plan=dialogue,
        )

    owner_questions = list(dialogue.get("decisions") or [])
    if capability is None and not owner_questions:
        return _blocked(
            BLOCK_DIALOGUE_FAILED,
            case_id=bridge.get("case_id"),
            detail="workbook-first semantic pass produced no owner-confirmable decisions",
            bridge_packet=bridge,
            workbook_profile=profile,
            context=context,
            interpreter_packet=interpreted,
            validated_packet=validated,
            dialogue_plan=dialogue,
        )

    return _packet(
        status=STATUS_OWNER_DIALOGUE_REQUIRED,
        case_id=str(bridge.get("case_id") or "").strip(),
        requested_capability=capability,
        bridge_packet=bridge,
        workbook_profile=profile,
        context=context,
        interpreter_packet=interpreted,
        validated_packet=validated,
        dialogue_plan=dialogue,
        owner_questions=owner_questions,
        table_scoped_semantics=semantic_scope_packet,
        semantic_scope_capabilities=semantic_scope_capabilities,
    )


def revise_service_1_assisted_semantic_decision_v1(
    *,
    previous_state: Any,
    decision_id: str,
    semantic_role: str,
    variable_name: str,
    owner_correction_text: str,
) -> dict[str, Any]:
    """Create a validated replacement proposal for one owner-corrected column.

    This is still proposal state: it creates no owner evidence and grants no
    authority. The revised meaning must pass the existing SEM-3 deterministic
    validator and is returned as a new one-question dialogue for explicit owner
    acceptance.
    """
    if not _valid_previous_state(previous_state):
        return _blocked(BLOCK_STATE_INVALID)
    target_decision_id = str(decision_id or "").strip()
    role = str(semantic_role or "").strip()
    variable = str(variable_name or "").strip()
    correction = str(owner_correction_text or "").strip()
    if not target_decision_id or not role or not variable or not correction:
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="missing correction decision, role, variable or owner text",
        )

    context = previous_state.get("context")
    if not isinstance(context, Service1LLMSemanticContextV1):
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="semantic context is unavailable",
        )
    dialogue_plan = previous_state.get("dialogue_plan") or {}
    decision = next(
        (
            item
            for item in (dialogue_plan.get("decisions") or [])
            if isinstance(item, Mapping)
            and str(item.get("decision_id") or "").strip() == target_decision_id
        ),
        None,
    )
    if not isinstance(decision, Mapping):
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="dialogue decision not found",
        )
    column_refs = [
        str(ref).strip()
        for ref in (decision.get("column_refs") or [])
        if str(ref).strip()
    ]
    relationship_refs = [
        str(ref).strip()
        for ref in (decision.get("relationship_refs") or [])
        if str(ref).strip()
    ]
    proposal_refs = [
        str(ref).strip()
        for ref in (decision.get("proposal_refs") or [])
        if str(ref).strip()
    ]
    if len(column_refs) != 1 or relationship_refs or len(proposal_refs) != 1:
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="only one-column semantic decisions can be revised here",
        )

    target_ref = column_refs[0]
    proposal_ref = proposal_refs[0]
    interpreter_packet = previous_state.get("interpreter_packet") or {}
    old_proposal = interpreter_packet.get("proposal")
    if not isinstance(old_proposal, Service1LLMSemanticProposalV1):
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="typed semantic proposal is unavailable",
        )

    evidence_refs: list[str] = []
    for candidate in (
        f"ev:column:{target_ref}:type",
        f"ev:column:{target_ref}:range",
    ):
        if candidate in context.evidence_registry:
            evidence_refs.append(candidate)

    replacement = Service1LLMConceptProposalV1(
        proposal_id=proposal_ref,
        target_column_refs=(target_ref,),
        semantic_role=role,
        variable_name=variable,
        confidence=0.95,
        rationale=(
            f"Owner described the column as: {correction}. "
            "LLM-assisted correction is still pending explicit owner confirmation."
        ),
        evidence_refs=tuple(evidence_refs),
    )
    proposal = Service1LLMSemanticProposalV1(
        concept_proposals=tuple(
            [
                item
                for item in old_proposal.concept_proposals
                if item.proposal_id != proposal_ref
                and target_ref not in item.target_column_refs
            ]
            + [replacement]
        ),
        relationship_proposals=old_proposal.relationship_proposals,
        duplicate_semantics=tuple(
            item
            for item in old_proposal.duplicate_semantics
            if target_ref not in item.column_refs
        ),
        irrelevant_refs=tuple(
            ref for ref in old_proposal.irrelevant_refs if ref != target_ref
        ),
        material_ambiguities=tuple(
            item
            for item in old_proposal.material_ambiguities
            if item.ambiguity_id != proposal_ref and target_ref not in item.target_refs
        ),
    )
    validated = validate_service_1_semantic_proposal_v1(
        context=context,
        proposal=proposal,
    )
    if validated.get("status") != VALIDATOR_READY:
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail={
                "validator_reason": validated.get("blocked_reason"),
                "validator_detail": validated.get("detail"),
            },
        )
    dialogue = build_service_1_owner_dialogue_plan_v1(
        validated_packet=validated,
        atomic_confirmation=True,
    )
    if dialogue.get("status") != DIALOGUE_READY:
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail=dialogue.get("blocked_reason"),
        )
    revised_question = next(
        (
            item
            for item in (dialogue.get("decisions") or [])
            if isinstance(item, Mapping)
            and str(item.get("decision_id") or "").strip() == target_decision_id
        ),
        None,
    )
    if not isinstance(revised_question, Mapping):
        return _blocked(
            BLOCK_OWNER_CORRECTION_INVALID,
            case_id=previous_state.get("case_id"),
            detail="validated correction is not material to the current dialogue",
        )

    revised_interpreter_packet = dict(interpreter_packet)
    revised_interpreter_packet["proposal"] = proposal
    revised_interpreter_packet["proposal_payload"] = proposal.to_dict()
    return _packet(
        status=STATUS_OWNER_DIALOGUE_REQUIRED,
        case_id=str(previous_state.get("case_id") or "").strip(),
        requested_capability=previous_state.get("requested_capability"),
        bridge_packet=dict(previous_state.get("bridge_packet") or {}),
        workbook_profile=dict(previous_state.get("workbook_profile") or {}),
        context=context,
        interpreter_packet=revised_interpreter_packet,
        validated_packet=validated,
        dialogue_plan=dialogue,
        owner_questions=[dict(revised_question)],
        table_scoped_semantics=previous_state.get("table_scoped_semantics"),
        semantic_scope_capabilities=previous_state.get("semantic_scope_capabilities") or (),
    )


def run_service_1_assisted_semantic_reentry_v1(
    *,
    previous_state: Any,
    owner_responses: Any,
    owner_actor_id: str,
    owner_actor_role: str,
    file_ref: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Apply owner responses to the exact prior SEM-8 state without recalling the LLM."""
    if not _valid_previous_state(previous_state):
        return _blocked(BLOCK_STATE_INVALID)
    actor = str(owner_actor_id or "").strip()
    role = str(owner_actor_role or "").strip()
    if not actor or not role:
        return _blocked(
            BLOCK_OWNER_IDENTITY_REQUIRED,
            case_id=previous_state.get("case_id"),
        )
    if not isinstance(owner_responses, (list, tuple)):
        return _blocked(
            BLOCK_OWNER_RESPONSES_INVALID,
            case_id=previous_state.get("case_id"),
        )

    dialogue = previous_state["dialogue_plan"]
    decisions = {
        str(item.get("decision_id") or "").strip(): dict(item)
        for item in dialogue.get("decisions") or []
        if isinstance(item, dict) and str(item.get("decision_id") or "").strip()
    }
    responses: dict[str, dict[str, Any]] = {}
    for raw in owner_responses:
        if not isinstance(raw, Mapping):
            return _blocked(
                BLOCK_OWNER_RESPONSES_INVALID,
                case_id=previous_state.get("case_id"),
            )
        decision_id = str(raw.get("decision_id") or "").strip()
        if not decision_id:
            return _blocked(
                BLOCK_OWNER_RESPONSES_INVALID,
                case_id=previous_state.get("case_id"),
            )
        if decision_id in responses:
            return _blocked(
                BLOCK_OWNER_RESPONSE_DUPLICATE,
                case_id=previous_state.get("case_id"),
                detail=decision_id,
            )
        if decision_id not in decisions:
            return _blocked(
                BLOCK_OWNER_RESPONSE_UNKNOWN_DECISION,
                case_id=previous_state.get("case_id"),
                detail=decision_id,
            )
        responses[decision_id] = dict(raw)

    missing = sorted(set(decisions) - set(responses))
    if missing:
        return _packet(
            status=STATUS_OWNER_DIALOGUE_FOLLOWUP,
            case_id=previous_state["case_id"],
            requested_capability=previous_state["requested_capability"],
            bridge_packet=previous_state["bridge_packet"],
            workbook_profile=previous_state["workbook_profile"],
            context=previous_state["context"],
            interpreter_packet=previous_state["interpreter_packet"],
            validated_packet=previous_state["validated_packet"],
            dialogue_plan=dialogue,
            owner_questions=[decisions[item] for item in missing],
            blocked_reason=BLOCK_OWNER_RESPONSE_MISSING,
            table_scoped_semantics=previous_state.get("table_scoped_semantics"),
            semantic_scope_capabilities=previous_state.get("semantic_scope_capabilities") or (),
        )

    column_events: list[dict[str, Any]] = []
    relationship_events: list[dict[str, Any]] = []
    owner_skipped_refs: list[str] = []
    followup_questions: list[dict[str, Any]] = []
    dialogue_responses: list[dict[str, Any]] = []

    for decision_id in decisions:
        raw = responses[decision_id]
        resolved = apply_service_1_owner_dialogue_response_v1(
            dialogue_plan=dialogue,
            decision_id=decision_id,
            action=str(raw.get("action") or ""),
            correction_text=(
                str(raw.get("correction_text"))
                if raw.get("correction_text") is not None
                else None
            ),
            targeted_refs=raw.get("targeted_refs"),
        )
        dialogue_responses.append(resolved)
        response_status = str(resolved.get("status") or "")
        if response_status in _FOLLOWUP_DIALOGUE_STATUSES:
            atomic = [dict(item) for item in resolved.get("atomic_decisions") or [] if isinstance(item, dict)]
            followup_questions.extend(atomic or [decisions[decision_id]])
            continue
        if response_status == RESPONSE_DECISION_SKIPPED and resolved.get("action") == ACTION_SKIP:
            owner_skipped_refs.extend(
                str(ref).strip()
                for ref in (resolved.get("targeted_refs") or [])
                if str(ref).strip()
            )
            continue
        if response_status not in _ACCEPTED_DIALOGUE_STATUSES or resolved.get("action") != ACTION_ACCEPT:
            return _blocked(
                BLOCK_OWNER_RESPONSES_INVALID,
                case_id=previous_state.get("case_id"),
                detail=response_status,
            )

        projected = project_service_1_owner_semantic_answer_v1(
            dialogue_response=resolved,
            validated_packet=previous_state["validated_packet"],
            case_id=previous_state["case_id"],
            file_ref=file_ref,
            owner_actor_id=actor,
            owner_actor_role=role,
            owner_answer=ACTION_ACCEPT,
            timestamp=timestamp,
        )
        if projected.get("status") != SEM5_READY:
            return _blocked(
                BLOCK_OWNER_PROJECTION_FAILED,
                case_id=previous_state.get("case_id"),
                detail=projected.get("blocked_reason"),
            )
        column_events.extend(
            dict(item) for item in projected.get("owner_confirmation_events") or [] if isinstance(item, dict)
        )
        relationship_events.extend(
            dict(item)
            for item in projected.get("owner_relationship_confirmation_events") or []
            if isinstance(item, dict)
        )

    if followup_questions:
        return _packet(
            status=STATUS_OWNER_DIALOGUE_FOLLOWUP,
            case_id=previous_state["case_id"],
            requested_capability=previous_state["requested_capability"],
            bridge_packet=previous_state["bridge_packet"],
            workbook_profile=previous_state["workbook_profile"],
            context=previous_state["context"],
            interpreter_packet=previous_state["interpreter_packet"],
            validated_packet=previous_state["validated_packet"],
            dialogue_plan=dialogue,
            owner_questions=followup_questions,
            dialogue_responses=dialogue_responses,
            table_scoped_semantics=previous_state.get("table_scoped_semantics"),
            semantic_scope_capabilities=previous_state.get("semantic_scope_capabilities") or (),
        )

    owner_scope_exclusions = list(dict.fromkeys(owner_skipped_refs))
    evidence_packet = {
        "schema_version": SEM5_SCHEMA_VERSION,
        "status": SEM5_READY,
        "blocked_reason": None,
        "detail": None,
        "case_id": previous_state["case_id"],
        "owner_confirmation_events": column_events,
        "owner_relationship_confirmation_events": relationship_events,
        "owner_confirmation_event_count": len(column_events),
        "owner_relationship_confirmation_event_count": len(relationship_events),
        "owner_scope_exclusions": owner_scope_exclusions,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    sem6 = build_service_1_owner_semantic_evidence_reentry_v1(
        semantic_bridge_packet=previous_state["bridge_packet"],
        owner_semantic_evidence_packet=evidence_packet,
        suppressed_irrelevant_refs=list(
            dict.fromkeys(
                list(previous_state["dialogue_plan"].get("suppressed_irrelevant_refs") or [])
                + owner_scope_exclusions
            )
        ),
    )
    if sem6.get("status") != SEM6_READY:
        return _blocked(
            BLOCK_REENTRY_FAILED,
            case_id=previous_state["case_id"],
            detail=sem6.get("blocked_reason"),
            sem6_packet=sem6,
        )

    semantic_run = {
        "schema_version": CONFIRMED_BINDINGS_SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "status": STATUS_CONFIRMED,
        "blocked_reason": None,
        "bridge_packet": previous_state["bridge_packet"],
        "gate_packet": None,
        "owner_loop_packet": {
            "owner_confirmation_events": column_events,
            "owner_relationship_confirmation_events": relationship_events,
            "owner_scope_exclusions": owner_scope_exclusions,
            "system_scope_exclusions": list(sem6.get("system_scope_exclusions") or []),
        },
        "reentry_packet": sem6.get("reentry_packet"),
        "owner_questions": [],
        "owner_followup": [],
        "confirmed_candidate": sem6.get("confirmed_candidate"),
        "confirmed_relationships": relationship_events,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return _packet(
        status=STATUS_CONFIRMED,
        case_id=previous_state["case_id"],
        requested_capability=previous_state["requested_capability"],
        bridge_packet=previous_state["bridge_packet"],
        workbook_profile=previous_state["workbook_profile"],
        context=previous_state["context"],
        interpreter_packet=previous_state["interpreter_packet"],
        validated_packet=previous_state["validated_packet"],
        dialogue_plan=dialogue,
        owner_questions=[],
        dialogue_responses=dialogue_responses,
        owner_evidence_packet=evidence_packet,
        sem6_packet=sem6,
        semantic_run=semantic_run,
        table_scoped_semantics=previous_state.get("table_scoped_semantics"),
        semantic_scope_capabilities=previous_state.get("semantic_scope_capabilities") or (),
    )


def _deterministic_hypotheses(bridge: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    for raw in bridge.get("column_understandings") or ():
        if hasattr(raw, "to_dict"):
            item = raw.to_dict()
        elif isinstance(raw, Mapping):
            item = dict(raw)
        else:
            continue
        if isinstance(item, dict):
            result.append(item)
    return tuple(result)


def _allowed_roles(hypotheses: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    roles: list[str] = []
    for item in hypotheses:
        candidates = item.get("candidate_meanings")
        if isinstance(candidates, (list, tuple)):
            for candidate in candidates:
                if not isinstance(candidate, Mapping):
                    continue
                role = str(candidate.get("semantic_role") or "").strip()
                if role and role != "unknown" and role not in roles:
                    roles.append(role)
        primary = item.get("primary_hypothesis")
        if isinstance(primary, Mapping):
            role = str(primary.get("semantic_role") or "").strip()
            if role and role != "unknown" and role not in roles:
                roles.append(role)
    return tuple(roles)


def _capability_relevant_roles(
    *,
    requested_capability: str,
    deterministic_hypotheses: Sequence[Mapping[str, Any]],
    allowed_roles: Sequence[str],
    semantic_scope_capabilities: Sequence[str] = (),
) -> tuple[str, ...]:
    primary = str(requested_capability or "").strip()
    scope = tuple(
        dict.fromkeys(
            item
            for item in (
                str(value or "").strip()
                for value in (semantic_scope_capabilities or (primary,))
            )
            if item
        )
    ) or (primary,)
    allowed = set(allowed_roles)
    relevant: list[str] = []

    for capability in scope:
        definition = get_capability_definition_v1(capability)
        if definition is not None and definition.kind == "ATOMIC":
            required_variables = {
                str(item.name or "").strip()
                for item in definition.variables
                if str(item.name or "").strip()
            }
            for hypothesis in deterministic_hypotheses:
                candidates = hypothesis.get("candidate_meanings")
                if not isinstance(candidates, (list, tuple)):
                    continue
                for candidate in candidates:
                    if not isinstance(candidate, Mapping):
                        continue
                    variable = str(candidate.get("variable_name") or "").strip()
                    role = str(candidate.get("semantic_role") or "").strip()
                    if variable in required_variables and role in allowed and role not in relevant:
                        relevant.append(role)

        for family in VARIABLE_FAMILY_DEFINITIONS:
            if capability not in family.target_capabilities:
                continue
            for group in family.required_role_groups:
                for role in group:
                    if role in allowed and role not in relevant:
                        relevant.append(role)
            for role in family.optional_roles:
                if role in allowed and role not in relevant:
                    relevant.append(role)

        for role in service_1_derived_evidence_semantic_support_roles_v1(capability):
            if role in allowed and role not in relevant:
                relevant.append(role)

    return tuple(relevant or allowed_roles)


def _valid_previous_state(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema_version") == SCHEMA_VERSION
        and value.get("status") in {STATUS_OWNER_DIALOGUE_REQUIRED, STATUS_OWNER_DIALOGUE_FOLLOWUP}
        and isinstance(value.get("bridge_packet"), dict)
        and isinstance(value.get("workbook_profile"), dict)
        and value.get("context") is not None
        and isinstance(value.get("interpreter_packet"), dict)
        and isinstance(value.get("validated_packet"), dict)
        and isinstance(value.get("dialogue_plan"), dict)
    )


def _packet(
    *,
    status: str,
    case_id: str,
    requested_capability: str | None,
    bridge_packet: dict[str, Any],
    workbook_profile: dict[str, Any],
    context: Any,
    interpreter_packet: dict[str, Any],
    validated_packet: dict[str, Any],
    dialogue_plan: dict[str, Any],
    owner_questions: list[dict[str, Any]],
    blocked_reason: str | None = None,
    dialogue_responses: list[dict[str, Any]] | None = None,
    owner_evidence_packet: dict[str, Any] | None = None,
    sem6_packet: dict[str, Any] | None = None,
    semantic_run: dict[str, Any] | None = None,
    table_scoped_semantics: Mapping[str, Any] | None = None,
    semantic_scope_capabilities: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocked_reason": blocked_reason,
        "detail": None,
        "case_id": case_id,
        "requested_capability": requested_capability,
        "semantic_scope_capabilities": [
            str(item).strip()
            for item in semantic_scope_capabilities
            if str(item).strip()
        ],
        "bridge_packet": bridge_packet,
        "workbook_profile": workbook_profile,
        "context": context,
        "interpreter_packet": interpreter_packet,
        "validated_packet": validated_packet,
        "dialogue_plan": dialogue_plan,
        "owner_questions": [dict(item) for item in owner_questions],
        "dialogue_responses": [dict(item) for item in (dialogue_responses or [])],
        "owner_evidence_packet": owner_evidence_packet,
        "sem6_packet": sem6_packet,
        "semantic_run": semantic_run,
        "table_scoped_semantics": (
            dict(table_scoped_semantics)
            if isinstance(table_scoped_semantics, Mapping)
            else None
        ),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(
    reason: str,
    *,
    case_id: Any = None,
    detail: Any = None,
    bridge_packet: Any = None,
    workbook_profile: Any = None,
    context: Any = None,
    interpreter_packet: Any = None,
    validated_packet: Any = None,
    dialogue_plan: Any = None,
    sem6_packet: Any = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "case_id": str(case_id or "").strip() or None,
        "requested_capability": None,
        "bridge_packet": bridge_packet,
        "workbook_profile": workbook_profile,
        "context": context,
        "interpreter_packet": interpreter_packet,
        "validated_packet": validated_packet,
        "dialogue_plan": dialogue_plan,
        "owner_questions": [],
        "dialogue_responses": [],
        "owner_evidence_packet": None,
        "sem6_packet": sem6_packet,
        "semantic_run": None,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_OWNER_DIALOGUE_REQUIRED",
    "STATUS_OWNER_DIALOGUE_FOLLOWUP",
    "STATUS_CONFIRMED",
    "STATUS_BLOCKED",
    "BLOCK_INGESTION_INVALID",
    "BLOCK_CAPABILITY_REQUIRED",
    "BLOCK_BRIDGE_FAILED",
    "BLOCK_PROFILE_FAILED",
    "BLOCK_NO_ALLOWED_ROLES",
    "BLOCK_CONTEXT_FAILED",
    "BLOCK_INTERPRETER_FAILED",
    "BLOCK_VALIDATOR_FAILED",
    "BLOCK_DIALOGUE_FAILED",
    "BLOCK_STATE_INVALID",
    "BLOCK_OWNER_IDENTITY_REQUIRED",
    "BLOCK_OWNER_RESPONSES_INVALID",
    "BLOCK_OWNER_RESPONSE_DUPLICATE",
    "BLOCK_OWNER_RESPONSE_UNKNOWN_DECISION",
    "BLOCK_OWNER_RESPONSE_MISSING",
    "BLOCK_OWNER_PROJECTION_FAILED",
    "BLOCK_REENTRY_FAILED",
    "BLOCK_OWNER_CORRECTION_INVALID",
    "run_service_1_assisted_semantic_initial_v1",
    "revise_service_1_assisted_semantic_decision_v1",
    "run_service_1_assisted_semantic_reentry_v1",
]
