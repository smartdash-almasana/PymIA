"""Bounded PydanticAI provider for Servicio 1 column semantics.

This module has one authority only: propose semantic meaning for already-profiled
Excel columns. It never opens XLSX files, never calculates business results,
never calls the product pipeline, never persists owner evidence, and never grants
runtime/delivery authority.

The provider consumes the existing SEM-2 provider payload and returns the closed
SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1 shape. Deterministic structural relationship
proposals are preserved from the existing baseline provider; the LLM is limited
to column concept interpretation and material ambiguity detection.
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
from collections.abc import Mapping
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import PROPOSAL_SCHEMA_VERSION


class ColumnSemanticDecisionV1(BaseModel):
    """One model-produced interpretation. No calculation/output authority exists."""

    model_config = ConfigDict(extra="forbid")

    column_ref: str
    semantic_role: str | None = None
    variable_name: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    needs_owner_confirmation: bool
    rationale: str


class ColumnSemanticBatchV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisions: list[ColumnSemanticDecisionV1]


class ColumnSemanticAssistanceReplyV1(BaseModel):
    """Conversational help only; never owner evidence or semantic authority."""

    model_config = ConfigDict(extra="forbid")

    response_text: str
    suggested_semantic_role: str | None = None
    suggested_variable_name: str | None = None
    suggestion_reason: str | None = None


_SYSTEM_PROMPT = """You are the column-meaning interpreter for PymIA Servicio 1.

Your only job is to interpret the semantic meaning of Excel columns from the
provided workbook profile, including sheet name, raw header, normalized header,
inferred type, bounded sample values, neighboring columns, deterministic
hypotheses and allowed semantic roles.

Hard limits:
- Do not calculate totals, margins, ratios, balances or any business result.
- Do not infer or return runtime, tool, product or delivery authorization.
- Do not modify evidence.
- Do not invent column references.
- Use only semantic_role values listed in allowed_semantic_roles.
- Prefer no mapping over a wrong mapping.
- If the meaning is materially ambiguous, set needs_owner_confirmation=true.
- If no allowed role fits, return semantic_role=null and variable_name=null and
  needs_owner_confirmation=true.
- confidence expresses semantic interpretation confidence only; it is never an
  authorization signal.

Return one decision for every column_ref supplied in columns_to_interpret.
"""

_ASSISTANT_SYSTEM_PROMPT = """You are the bounded semantic help drawer for PymIA Servicio 1.

You are helping a business owner understand one currently visible Excel column.
The request supplies interaction_mode, which is either "QUESTION" or "CORRECTION".

For interaction_mode="QUESTION":
- The owner is asking to understand the current proposal.
- Explain the existing proposal, point to the supplied sample values and business
  context, and help the owner phrase a correction in plain language.
- suggestion may be null; you are not required to propose a pair.

For interaction_mode="CORRECTION":
- The owner is explaining that the current proposal is wrong and stating what the
  column actually means.
- Interpret their text against allowed_role_variable_pairs supplied in the request.
- If their explanation clearly matches exactly one allowed pair, return that exact
  suggested_semantic_role and suggested_variable_name.
- If no allowed pair clearly matches, return both suggested fields as null.
- Never invent pairs. Never return a pair that is not in allowed_role_variable_pairs.

Hard limits (both modes):
- Never confirm a meaning on behalf of the owner.
- Never persist evidence or claim that anything was saved.
- Never calculate totals, margins, balances, ratios or business results.
- Never authorize tools, runtime, product execution or delivery.
- Never invent workbook values or column references.
- A suggestion is only a proposal for the owner to review; it is not confirmation.
- Keep the answer concise and in the owner's language.

The owner remains the only source of confirmation.
"""


def _compact_column_context(payload: Mapping[str, Any]) -> dict[str, Any]:
    profile = payload.get("workbook_profile")
    profile = profile if isinstance(profile, Mapping) else {}
    hypotheses = [
        dict(item)
        for item in (payload.get("deterministic_hypotheses") or [])
        if isinstance(item, Mapping)
    ]
    hypothesis_by_ref: dict[str, dict[str, Any]] = {}
    for hypothesis in hypotheses:
        sheet = str(hypothesis.get("sheet_name") or "").strip()
        column = str(hypothesis.get("column_name") or "").strip()
        if sheet and column:
            hypothesis_by_ref[f"{sheet}.{column}"] = hypothesis

    columns: list[dict[str, Any]] = []
    all_profile_columns = [
        dict(item)
        for item in (profile.get("columns") or [])
        if isinstance(item, Mapping)
    ]
    neighbor_headers_by_sheet: dict[str, list[str]] = {}
    for item in all_profile_columns:
        sheet = str(item.get("sheet_name") or "").strip()
        header = str(item.get("column_name") or "").strip()
        if sheet and header:
            neighbor_headers_by_sheet.setdefault(sheet, []).append(header)

    for item in all_profile_columns:
        column_ref = str(item.get("column_ref") or "").strip()
        if not column_ref:
            continue
        sheet = str(item.get("sheet_name") or "").strip()
        columns.append(
            {
                "column_ref": column_ref,
                "sheet_name": sheet,
                "column_name": str(item.get("column_name") or "").strip(),
                "normalized_header": str(item.get("normalized_header") or "").strip(),
                "inferred_type": str(item.get("inferred_type") or "").strip(),
                "sample_values": list(item.get("sample_values") or [])[:5],
                "null_ratio": item.get("null_ratio"),
                "cardinality": item.get("cardinality"),
                "neighbor_headers": neighbor_headers_by_sheet.get(sheet, []),
                "deterministic_hypothesis": hypothesis_by_ref.get(column_ref),
            }
        )

    return {
        "case_id": str(payload.get("case_id") or "").strip(),
        "requested_capability": str(payload.get("requested_capability") or "").strip(),
        "allowed_semantic_roles": [
            str(role).strip()
            for role in (payload.get("allowed_semantic_roles") or [])
            if str(role).strip()
        ],
        "capability_relevant_roles": [
            str(role).strip()
            for role in (payload.get("capability_relevant_roles") or [])
            if str(role).strip()
        ],
        "compatible_tenant_memory_hints": [
            dict(item)
            for item in (payload.get("compatible_tenant_memory_hints") or [])
            if isinstance(item, Mapping)
        ],
        "columns_to_interpret": columns,
    }


def _decision_payload(
    *,
    payload: Mapping[str, Any],
    batch: ColumnSemanticBatchV1,
) -> dict[str, Any]:
    baseline = build_service_1_deterministic_semantic_proposal_v1(payload)
    profile = payload.get("workbook_profile")
    profile = profile if isinstance(profile, Mapping) else {}
    evidence_registry = payload.get("evidence_registry")
    evidence_registry = evidence_registry if isinstance(evidence_registry, Mapping) else {}
    allowed_roles = {
        str(role).strip()
        for role in (payload.get("allowed_semantic_roles") or [])
        if str(role).strip()
    }
    relevant_roles = {
        str(role).strip()
        for role in (payload.get("capability_relevant_roles") or [])
        if str(role).strip()
    }
    known_refs = {
        str(item.get("column_ref") or "").strip()
        for item in (profile.get("columns") or [])
        if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
    }

    concepts: list[dict[str, Any]] = []
    ambiguities: list[dict[str, Any]] = []
    mapped_refs: set[str] = set()
    seen_refs: set[str] = set()

    for index, decision in enumerate(batch.decisions, start=1):
        column_ref = decision.column_ref.strip()
        if not column_ref or column_ref not in known_refs or column_ref in seen_refs:
            continue
        seen_refs.add(column_ref)
        role = (decision.semantic_role or "").strip()
        variable = (decision.variable_name or "").strip()
        evidence_refs = [f"ev:column:{column_ref}:type"]
        range_ref = f"ev:column:{column_ref}:range"
        if range_ref in evidence_registry:
            evidence_refs.append(range_ref)

        role_is_allowed = bool(role and role in allowed_roles)
        role_is_relevant = not relevant_roles or role in relevant_roles
        if (
            role_is_allowed
            and role_is_relevant
            and variable
            and not decision.needs_owner_confirmation
        ):
            concepts.append(
                {
                    "proposal_id": f"pydantic-ai:concept:{index}:{column_ref}",
                    "target_column_refs": [column_ref],
                    "semantic_role": role,
                    "variable_name": variable,
                    "confidence": decision.confidence,
                    "rationale": decision.rationale,
                    "evidence_refs": evidence_refs,
                }
            )
            mapped_refs.add(column_ref)
            continue

        if decision.needs_owner_confirmation or role:
            ambiguities.append(
                {
                    "ambiguity_id": f"pydantic-ai:ambiguity:{index}:{column_ref}",
                    "target_refs": [column_ref],
                    "reason": decision.rationale,
                    "confidence": decision.confidence,
                    "evidence_refs": evidence_refs,
                }
            )

    return {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "concept_proposals": concepts,
        "relationship_proposals": list(baseline.get("relationship_proposals") or []),
        "duplicate_semantics": [],
        "irrelevant_refs": sorted(known_refs - mapped_refs),
        "material_ambiguities": ambiguities,
    }


class Service1PydanticAIColumnSemanticProviderV1:
    """Callable semantic provider with no tools and no calculation authority.

    Runs pydantic-ai agents on a single persistent event loop so concurrent
    threaded web requests never rebind the shared httpx/anyio resources to a
    second loop (which raises "Event bound to a different event loop").
    """

    def __init__(self, *, agent: Any, assistant_agent: Any | None = None) -> None:
        self._agent = agent
        self._assistant_agent = assistant_agent
        self._loop = asyncio.new_event_loop()
        self._lock = threading.Lock()

    def _run_sync(self, callable_agent: Any, prompt: str) -> Any:
        run = getattr(callable_agent, "run", None)
        if callable(run):
            with self._lock:
                return self._loop.run_until_complete(run(prompt))
        run_sync = getattr(callable_agent, "run_sync", None)
        if callable(run_sync):
            return run_sync(prompt)
        raise RuntimeError("semantic agent exposes no run/run_sync callable")

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("semantic provider payload must be a mapping")
        context = _compact_column_context(payload)
        result = self._run_sync(self._agent, json.dumps(context, ensure_ascii=False, default=str))
        output = getattr(result, "output", None)
        batch = output if isinstance(output, ColumnSemanticBatchV1) else ColumnSemanticBatchV1.model_validate(output)
        return _decision_payload(payload=payload, batch=batch)

    def assist(self, payload: Mapping[str, Any]) -> dict[str, str]:
        """Explain one semantic transaction without mutating or confirming it."""
        if self._assistant_agent is None:
            raise RuntimeError("semantic assistance agent is not configured")
        if not isinstance(payload, Mapping):
            raise ValueError("semantic assistance payload must be a mapping")
        result = self._run_sync(
            self._assistant_agent,
            json.dumps(dict(payload), ensure_ascii=False, default=str),
        )
        output = getattr(result, "output", None)
        reply = (
            output
            if isinstance(output, ColumnSemanticAssistanceReplyV1)
            else ColumnSemanticAssistanceReplyV1.model_validate(output)
        )
        return {
            "response_text": reply.response_text.strip(),
            "suggested_semantic_role": reply.suggested_semantic_role,
            "suggested_variable_name": reply.suggested_variable_name,
            "suggestion_reason": reply.suggestion_reason,
        }


def build_service_1_pydantic_ai_column_semantic_provider_v1(
    *,
    model: str,
    agent_factory: Callable[..., Any] | None = None,
) -> Service1PydanticAIColumnSemanticProviderV1:
    model_name = str(model or "").strip()
    if not model_name:
        raise ValueError("semantic LLM model is required")
    resolved_model: Any = model_name
    if agent_factory is None:
        try:
            from pydantic_ai import Agent
        except ImportError as exc:  # pragma: no cover - environment contract
            raise RuntimeError("pydantic-ai is required for semantic LLM mode") from exc
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "").strip()
        if project and location and model_name.startswith("gemini"):
            try:
                from pydantic_ai.models.google import GoogleModel
                from pydantic_ai.providers.google_cloud import GoogleCloudProvider
            except ImportError as exc:  # pragma: no cover - environment contract
                raise RuntimeError("pydantic-ai google extra is required for Vertex semantic mode") from exc
            resolved_model = GoogleModel(
                model_name,
                provider=GoogleCloudProvider(project=project, location=location),
            )
        agent_factory = Agent
    agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticBatchV1,
        instructions=_SYSTEM_PROMPT,
    )
    assistant_agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticAssistanceReplyV1,
        instructions=_ASSISTANT_SYSTEM_PROMPT,
    )
    return Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        assistant_agent=assistant_agent,
    )


def semantic_provider_from_environment_v1() -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Select LLM semantics only when explicitly configured; otherwise keep baseline."""

    model = os.getenv("PYMIA_SEMANTIC_LLM_MODEL", "").strip()
    if not model:
        return build_service_1_deterministic_semantic_proposal_v1
    return build_service_1_pydantic_ai_column_semantic_provider_v1(model=model)


__all__ = [
    "ColumnSemanticAssistanceReplyV1",
    "ColumnSemanticBatchV1",
    "ColumnSemanticDecisionV1",
    "Service1PydanticAIColumnSemanticProviderV1",
    "build_service_1_pydantic_ai_column_semantic_provider_v1",
    "semantic_provider_from_environment_v1",
]
