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
from contextlib import contextmanager
import contextvars
from dataclasses import dataclass
import json
import os
import threading
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

from pymia.smartpyme.service_1_semantic_coordinate_model_v2 import (
    AXES as SEMANTIC_COORDINATE_AXES,
    Service1SemanticCoordinateV2,
    load_service_1_semantic_coordinate_taxonomy_v2,
)
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import PROPOSAL_SCHEMA_VERSION
from pymia.smartpyme.service_1_workbook_business_understanding_v1 import (
    AUTHORITY as BUSINESS_UNDERSTANDING_AUTHORITY,
    SCHEMA_VERSION as BUSINESS_UNDERSTANDING_SCHEMA_VERSION,
)


class CompositionalSemanticProposalV1(BaseModel):
    """Bounded C2 coordinate proposal; evidence/provenance stay system-owned."""

    model_config = ConfigDict(extra="forbid")

    entity: str | None = None
    object: str | None = None
    process: str | None = None
    measure: str | None = None
    state: str | None = None
    grain: str | None = None
    scope: str | None = None
    time: str | None = None
    identity: str | None = None
    relation: str | None = None
    unit: str | None = None
    aggregation: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: str | None = None


class ColumnSemanticDecisionV1(BaseModel):
    """One model-produced interpretation. No calculation/output authority exists."""

    model_config = ConfigDict(extra="forbid")

    column_ref: str
    semantic_role: str | None = None
    variable_name: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    needs_owner_confirmation: bool
    rationale: str
    compositional_semantic: CompositionalSemanticProposalV1 | None = None


class ColumnSemanticBatchV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisions: list[ColumnSemanticDecisionV1]


class WorkbookTableUnderstandingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sheet_name: str
    table_meaning: str
    grain: str | None = None
    business_objects: list[str] = Field(default_factory=list)
    processes: list[str] = Field(default_factory=list)
    semantic_groups: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class WorkbookBusinessUnderstandingV1(BaseModel):
    """Context-only whole-workbook hypothesis produced before column mapping."""

    model_config = ConfigDict(extra="forbid")

    workbook_summary: str
    tables: list[WorkbookTableUnderstandingV1]
    material_ambiguities: list[str] = Field(default_factory=list)


class ColumnSemanticAssistanceReplyV1(BaseModel):
    """Conversational help only; never owner evidence or semantic authority."""

    model_config = ConfigDict(extra="forbid")

    response_text: str
    suggested_compositional_semantic: CompositionalSemanticProposalV1 | None = None
    suggestion_reason: str | None = None


NVIDIA_NIM_PROVIDER = "NVIDIA_NIM"
NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_NIM_MODEL = "nvidia/nemotron-3-super-120b-a12b"
NVIDIA_NIM_MODEL_ENV = "NVIDIA_NIM_MODEL"
OPENCODE_ZEN_PROVIDER = "OPENCODE_ZEN"
OPENCODE_ZEN_BASE_URL = "https://opencode.ai/zen/v1"
OPENCODE_ZEN_MODEL = "muse-spark-1.3-contributor-free"
OPENCODE_ZEN_MODEL_ENV = "OPENCODE_ZEN_MODEL"
GEMINI_PROVIDER = "GEMINI"
GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_MODEL_ENV = "GEMINI_MODEL"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
SEMANTIC_PROVIDER_ENV = "PYMIA_SEMANTIC_PROVIDER"
SEMANTIC_MODEL_ENV = "PYMIA_SEMANTIC_LLM_MODEL"
SEMANTIC_BASE_URL_ENV = "PYMIA_SEMANTIC_LLM_BASE_URL"
NVIDIA_API_KEY_ENV = "NVIDIA_API_KEY"
OPENCODE_API_KEY_ENV = "OPENCODE_API_KEY"
SEMANTIC_TIMEOUT_SECONDS = 180.0
SEMANTIC_MAX_TOKENS = 512
SEMANTIC_COLUMN_MAX_TOKENS = 3072
SEMANTIC_WORKBOOK_MAX_TOKENS = 768
SEMANTIC_MAX_RETRIES = 1
SEMANTIC_RETRY_BACKOFF_SECONDS = 2.0
SERVICE_1_SEMANTIC_TOTAL_TIMEOUT_SECONDS = 300.0
GEMINI_TIMEOUT_SECONDS = 120.0
OPENCODE_ZEN_WORKBOOK_MAX_TOKENS = 8192
OPENCODE_ZEN_COLUMN_MAX_TOKENS = 8192
NVIDIA_NIM_TIMEOUT_SECONDS = SEMANTIC_TIMEOUT_SECONDS
NVIDIA_NIM_MAX_TOKENS = SEMANTIC_MAX_TOKENS
NVIDIA_NIM_COLUMN_MAX_TOKENS = SEMANTIC_COLUMN_MAX_TOKENS
NVIDIA_NIM_WORKBOOK_MAX_TOKENS = SEMANTIC_WORKBOOK_MAX_TOKENS
NVIDIA_NIM_MAX_RETRIES = 0
NVIDIA_NIM_RETRY_BACKOFF_SECONDS = SEMANTIC_RETRY_BACKOFF_SECONDS

_NVIDIA_NIM_MODEL_SETTINGS = {
    "timeout": NVIDIA_NIM_TIMEOUT_SECONDS,
    "max_tokens": NVIDIA_NIM_MAX_TOKENS,
    "thinking": False,
    "extra_body": {"chat_template_kwargs": {"thinking": False}},
}
_NVIDIA_NIM_WORKBOOK_MODEL_SETTINGS = {
    **_NVIDIA_NIM_MODEL_SETTINGS,
    "max_tokens": NVIDIA_NIM_WORKBOOK_MAX_TOKENS,
}
_NVIDIA_NIM_COLUMN_MODEL_SETTINGS = {
    **_NVIDIA_NIM_MODEL_SETTINGS,
    "max_tokens": NVIDIA_NIM_COLUMN_MAX_TOKENS,
}

_OPENCODE_ZEN_MODEL_SETTINGS = {
    "timeout": SEMANTIC_TIMEOUT_SECONDS,
    "max_tokens": SEMANTIC_MAX_TOKENS,
    "thinking": False,
}
_OPENCODE_ZEN_WORKBOOK_MODEL_SETTINGS = {
    **_OPENCODE_ZEN_MODEL_SETTINGS,
    "max_tokens": OPENCODE_ZEN_WORKBOOK_MAX_TOKENS,
}
_OPENCODE_ZEN_COLUMN_MODEL_SETTINGS = {
    **_OPENCODE_ZEN_MODEL_SETTINGS,
    "max_tokens": OPENCODE_ZEN_COLUMN_MAX_TOKENS,
}
_GEMINI_MODEL_SETTINGS = {
    "timeout": GEMINI_TIMEOUT_SECONDS,
}


class Service1SemanticTimeoutError(TimeoutError):
    """Raised when the governed Product Root semantic deadline expires."""


class Service1SemanticProviderTimeoutError(TimeoutError):
    """Raised when one provider call exceeds its own bounded timeout."""


class Service1TransientProviderFailureV1(RuntimeError):
    """Structured terminal failure: every attempted provider failed transiently
    (or a non-transient fallback failure followed transient primary failures).

    Carries the governed attempt log so callers can report the outage without
    mistaking it for a semantic verdict. Never carries semantic content and
    must never be converted into owner ambiguity.
    """

    def __init__(
        self,
        message: str,
        *,
        provider_attempts: Sequence[Any] | None = None,
        attempted_providers: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.provider_attempts: list[dict[str, Any]] = [
            dict(item) for item in (provider_attempts or ()) if isinstance(item, Mapping)
        ]
        self.attempted_providers: list[str] = [
            str(item) for item in (attempted_providers or ())
        ]


@dataclass(frozen=True, slots=True)
class Service1SemanticExecutionContextV1:
    deadline_monotonic: float
    cancellation_event: threading.Event

    def remaining_seconds(self) -> float:
        if self.cancellation_event.is_set():
            raise Service1SemanticTimeoutError("SERVICE_1_SEMANTIC_OPERATION_CANCELLED")
        remaining = self.deadline_monotonic - time.monotonic()
        if remaining <= 0:
            self.cancellation_event.set()
            raise Service1SemanticTimeoutError("SERVICE_1_SEMANTIC_OPERATION_TIMEOUT")
        return remaining


_SERVICE_1_SEMANTIC_EXECUTION_CONTEXT: contextvars.ContextVar[
    Service1SemanticExecutionContextV1 | None
] = contextvars.ContextVar(
    "service_1_semantic_execution_context",
    default=None,
)


@contextmanager
def service_1_semantic_execution_scope_v1(
    *,
    total_timeout_seconds: float | None = None,
):
    """Install one deadline/cancellation scope for a Product Root operation."""
    timeout = float(
        SERVICE_1_SEMANTIC_TOTAL_TIMEOUT_SECONDS
        if total_timeout_seconds is None
        else total_timeout_seconds
    )
    if timeout <= 0:
        raise ValueError("semantic total timeout must be greater than zero")
    context = Service1SemanticExecutionContextV1(
        deadline_monotonic=time.monotonic() + timeout,
        cancellation_event=threading.Event(),
    )
    token = _SERVICE_1_SEMANTIC_EXECUTION_CONTEXT.set(context)
    try:
        yield context
    finally:
        context.cancellation_event.set()
        _SERVICE_1_SEMANTIC_EXECUTION_CONTEXT.reset(token)


def _current_semantic_execution_context() -> Service1SemanticExecutionContextV1 | None:
    return _SERVICE_1_SEMANTIC_EXECUTION_CONTEXT.get()


_BUSINESS_UNDERSTANDING_SYSTEM_PROMPT = """You are the whole-workbook business-understanding pass for PymIA Servicio 1.

Before any column is interpreted individually, reconstruct what the workbook appears to represent as a business system.
Use only the supplied workbook_semantic_context and semantic_knowledge_context.

For every supplied sheet/table, identify:
- table_meaning in plain business language;
- the apparent grain (what one row represents), when support is sufficient;
- business_objects present;
- business processes represented;
- coherent semantic groups visible across neighboring columns.

Hard limits:
- Do not calculate business results.
- Do not invent sheets or columns.
- Do not confirm semantic truth on behalf of the owner.
- Do not grant runtime, tool, product or delivery authority.
- Retrieved knowledge is CONTEXT_ONLY and may guide interpretation but never overrides workbook evidence.
- Prefer an explicit material ambiguity over invented certainty.
- Each request is scoped to one whole workbook. Return exactly one table entry
  for every supplied sheet/table in workbook_semantic_context.tables; do not
  create, drop, reorder or infer sheets.
- This output is a context-only hypothesis for the subsequent column pass.
- Keep the JSON compact: workbook_summary <= 80 words; each table_meaning and grain <= 20 words;
  use at most 4 short items in each list field. Do not include explanatory prose outside the JSON object.
"""


_SYSTEM_PROMPT = """You are the column-meaning interpreter for PymIA Servicio 1.

Your only job is to interpret the semantic meaning of Excel columns from the
provided workbook profile, including sheet name, raw header, normalized header,
inferred type, bounded sample values, neighboring columns, deterministic
hypotheses, allowed semantic roles and the governed compositional semantic
catalogs.

Hard limits:
- Do not calculate totals, margins, ratios, balances or any business result.
- Do not infer or return runtime, tool, product or delivery permission.
- Do not modify evidence.
- The model proposes semantic meaning only. Evidence/provenance references are
  attached by the deterministic system; do not generate evidence identifiers.
- The compositional_semantic_ontology is governed catalog metadata: each entry
  carries an id/value and may include a label, definition, exclusions, criteria
  or aliases. Treat that metadata as explanatory context, never as authority.
- Do not invent column references.
- Use only semantic_role values listed in allowed_semantic_roles.
- For compositional_semantic, use only values from the supplied coordinate catalogs.
  Never invent an entity, object, process, measure, state, grain, scope, time,
  identity, relation, unit or aggregation value.
- Reconstruct meaning compositionally from the complete header, sample values, neighboring columns and the explicit business_context attached to each column from the prior whole-workbook understanding pass. Do not interpret a token in isolation when the compound header changes its meaning.
- Treat business_context.table_meaning, grain, business_objects, processes and semantic_groups as context-only hypotheses: use them to disambiguate the column when they agree with workbook evidence, never as final truth and never to override contradictory samples/types.
- Distinguish clock/event time from duration and from rates or prices expressed per time unit. A header containing a time word does not by itself mean event time when cost, price, duration, labor, quantity or rate context changes the business meaning.
- Use surrounding columns to infer the business object and process when that inference is uniquely supported by the workbook context; otherwise leave the axis null and require owner confirmation when the ambiguity is material.
- Reconstruct meaning compositionally. The same measure may appear multiple times
  when object/process/grain differ (for example labor margin vs parts margin).
- Return the C2 coordinate descriptor for every business meaning you claim to understand.
- In this LLM path, compositional_semantic is the only accepted semantic representation.
  Always leave top-level semantic_role and variable_name null. If the business meaning
  cannot be represented with the supplied V2 catalogs, leave compositional_semantic null
  and set needs_owner_confirmation=true instead of inventing or falling back to a legacy role.
- Runtime projection is derived only by the deterministic system from the governed descriptor;
  never choose or emit a nearest runtime role.
- Prefer no mapping over a wrong mapping.
- If the business meaning itself is materially ambiguous, set
  needs_owner_confirmation=true.
- Lack of an allowed runtime role is not semantic ambiguity: if the
  compositional meaning is clear, keep the descriptor, leave top-level runtime
  fields null, and set needs_owner_confirmation according to meaning only.
- confidence expresses semantic interpretation confidence only; it is never an
  permission signal.

Return one decision for every column_ref supplied in columns_to_interpret.
The request is one contextual group, not the whole workbook. Return exactly
the supplied column_refs and no others; missing or contradictory coverage is
unsafe and must not be filled by guessing.
"""

_ASSISTANT_SYSTEM_PROMPT = """You are the bounded semantic help drawer for PymIA Servicio 1.

You are helping a business owner understand one currently visible Excel column.
The request supplies interaction_mode: "CONVERSATION" or "CORRECTION".

For interaction_mode="CONVERSATION":
- Converse naturally in the owner's language about the current column.
- Use the header, sample values, sheet context and current proposal.
- If the owner is only asking a question, answer it directly and suggestion may be null.
- If the owner clearly explains what the column actually means, reconstruct that
  meaning only with values from compositional_semantic_catalogs.
- Return suggested_compositional_semantic when the owner's explanation can be
  represented with governed V2 coordinates. Multiple instances of the same measure
  are valid when object/process/grain differ.
- If the explanation cannot be represented by the governed coordinates, say so
  plainly and do not invent a coordinate value.

For interaction_mode="CORRECTION":
- The owner is explicitly correcting the current proposal.
- Reconstruct the correction using only compositional_semantic_catalogs.
- Return suggested_compositional_semantic when the meaning is representable.
- Otherwise return it as null and explain what you understood in plain business language.
- Never invent coordinate values.

Hard limits (both modes):
- Never confirm a meaning on behalf of the owner.
- Never persist evidence or claim that anything was saved.
- Never calculate totals, margins, balances, ratios or business results.
- Never authorize tools, runtime, product execution or delivery.
- Never invent workbook values or column references.
- A suggestion is only a proposal for the owner to review; it is not confirmation.
- Keep the answer concise and in the owner's language.
- When the owner writes in Spanish, answer entirely in plain Spanish. Do not expose internal semantic-role names, variable names, schema terms or English implementation jargon.

The owner remains the only source of confirmation.
"""


def _compact_column_context(
    payload: Mapping[str, Any],
    *,
    selected_refs: set[str] | None = None,
) -> dict[str, Any]:
    profile = payload.get("workbook_profile")
    profile = profile if isinstance(profile, Mapping) else {}
    workbook_understanding = payload.get("workbook_business_understanding")
    workbook_understanding = workbook_understanding if isinstance(workbook_understanding, Mapping) else {}
    table_understanding_by_sheet = {
        str(item.get("sheet_name") or "").strip(): dict(item)
        for item in (workbook_understanding.get("tables") or [])
        if isinstance(item, Mapping) and str(item.get("sheet_name") or "").strip()
    }
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

    selected_refs = set(selected_refs or {
        str(item.get("column_ref") or "").strip()
        for item in all_profile_columns
        if str(item.get("column_ref") or "").strip()
    })
    for item in all_profile_columns:
        column_ref = str(item.get("column_ref") or "").strip()
        if not column_ref or column_ref not in selected_refs:
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
                "business_context": table_understanding_by_sheet.get(sheet),
            }
        )

    catalogs = _compositional_catalog_values(payload)
    ontology = _compositional_catalog_ontology(payload=payload, catalogs=catalogs)
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
        "workbook_semantic_context": _compact_workbook_semantic_context(
            payload=payload,
            selected_refs={item["column_ref"] for item in columns},
        ),
        "semantic_knowledge_context": dict(payload.get("semantic_knowledge_context") or {}),
        "workbook_business_understanding": dict(payload.get("workbook_business_understanding") or {}),
        "compositional_semantic_catalogs": {
            key: list(values) for key, values in catalogs.items()
        },
        "compositional_semantic_ontology": ontology,
        "columns_to_interpret": columns,
}


_GROUP_STOP_TOKENS = frozenset({
    "id", "ids", "codigo", "code", "name", "nombre", "fecha", "date",
    "valor", "value", "numero", "number", "tipo", "type",
})


def _compact_workbook_semantic_context(
    *,
    payload: Mapping[str, Any],
    selected_refs: set[str],
) -> dict[str, Any]:
    """Project only the structural context needed by one semantic group."""
    source = payload.get("workbook_semantic_context")
    if not isinstance(source, Mapping):
        return {}
    tables: list[dict[str, Any]] = []
    selected_sheets: set[str] = set()
    for raw_table in source.get("tables") or ():
        if not isinstance(raw_table, Mapping):
            continue
        selected_columns = [
            dict(column)
            for column in raw_table.get("columns") or ()
            if isinstance(column, Mapping)
            and str(column.get("column_ref") or "").strip() in selected_refs
        ]
        if not selected_columns:
            continue
        sheet = str(raw_table.get("sheet_name") or "").strip()
        selected_sheets.add(sheet)
        tables.append({
            "sheet_name": sheet,
            "row_count": raw_table.get("row_count"),
            "column_count": len(selected_columns),
            "columns": selected_columns,
            "logical_table_refs": list(raw_table.get("logical_table_refs") or ()),
            "grain_refs": list(raw_table.get("grain_refs") or ()),
        })
    relationships = [
        {
            key: raw.get(key)
            for key in (
                "relationship_ref", "left_column_ref", "right_column_ref",
                "relationship_kind", "same_normalized_header",
                "left_value_coverage", "right_value_coverage",
                "candidate_foreign_key", "candidate_primary_key_ref",
                "intersection_cardinality",
            )
        }
        for raw in source.get("relationships") or ()
        if isinstance(raw, Mapping)
        and (
            str(raw.get("left_column_ref") or "").strip() in selected_refs
            or str(raw.get("right_column_ref") or "").strip() in selected_refs
        )
    ]
    return {
        "schema_version": source.get("schema_version"),
        "status": source.get("status"),
        "case_id": source.get("case_id"),
        "source_file_ref": source.get("source_file_ref"),
        "sheet_count": len(selected_sheets),
        "column_count": len(selected_refs),
        "relationship_count": len(relationships),
        "tables": tables,
        "relationships": relationships,
    }


def _header_tokens(value: Any) -> frozenset[str]:
    raw = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or ""))
    tokens = {token.rstrip("s") for token in raw.split("_") if len(token.rstrip("s")) >= 4}
    return frozenset(token for token in tokens if token not in _GROUP_STOP_TOKENS)


def _column_groups(payload: Mapping[str, Any]) -> list[tuple[str, ...]]:
    """Build deterministic context groups from structure, relations and headers."""
    profile = payload.get("workbook_profile")
    profile = profile if isinstance(profile, Mapping) else {}
    raw_columns = [
        dict(item)
        for item in profile.get("columns") or ()
        if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
    ]
    if not raw_columns:
        raise ValueError("workbook_profile has no columns")
    refs = [str(item["column_ref"]).strip() for item in raw_columns]
    index = {ref: position for position, ref in enumerate(refs)}
    parent = list(range(len(refs)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for relation in profile.get("relationships") or ():
        if not isinstance(relation, Mapping):
            continue
        left = str(relation.get("left_column_ref") or "").strip()
        right = str(relation.get("right_column_ref") or "").strip()
        if left in index and right in index:
            union(index[left], index[right])

    for left_position, left in enumerate(raw_columns):
        left_sheet = str(left.get("sheet_name") or "").strip()
        left_tokens = _header_tokens(left.get("normalized_header") or left.get("column_name"))
        for right_position in range(left_position + 1, len(raw_columns)):
            right = raw_columns[right_position]
            if str(right.get("sheet_name") or "").strip() != left_sheet:
                continue
            right_tokens = _header_tokens(right.get("normalized_header") or right.get("column_name"))
            if left_tokens.intersection(right_tokens):
                union(left_position, right_position)

    grouped: dict[int, list[str]] = defaultdict(list)
    for position, ref in enumerate(refs):
        grouped[find(position)].append(ref)
    return [tuple(group) for group in grouped.values()]


def _merge_batches(*, batches: Sequence[ColumnSemanticBatchV1], expected_refs: Sequence[str]) -> ColumnSemanticBatchV1:
    by_ref: dict[str, ColumnSemanticDecisionV1] = {}
    expected = set(expected_refs)
    for batch in batches:
        for decision in batch.decisions:
            ref = decision.column_ref.strip()
            if ref not in expected:
                raise ValueError(f"column decision references unknown column: {ref}")
            previous = by_ref.get(ref)
            if previous is not None and previous.model_dump() != decision.model_dump():
                raise ValueError(f"CONTRADICTORY_COLUMN_DECISIONS:{ref}")
            by_ref[ref] = decision
    missing = [ref for ref in expected_refs if ref not in by_ref]
    if missing:
        raise ValueError("COLUMN_GROUP_COVERAGE_INCOMPLETE:" + ",".join(missing))
    return ColumnSemanticBatchV1(decisions=[by_ref[ref] for ref in expected_refs])


def _compositional_catalog_values(
    payload: Mapping[str, Any],
) -> dict[str, tuple[str, ...]]:
    raw = payload.get("compositional_semantic_catalogs")
    if raw is None:
        taxonomy = load_service_1_semantic_coordinate_taxonomy_v2()
        return {axis: taxonomy.allowed(axis) for axis in SEMANTIC_COORDINATE_AXES}
    if not isinstance(raw, Mapping):
        raise ValueError("compositional_semantic_catalogs must be a mapping")
    result: dict[str, tuple[str, ...]] = {}
    if set(raw) != set(SEMANTIC_COORDINATE_AXES):
        raise ValueError("compositional semantic catalogs must define exactly the V2 coordinate axes")
    for axis in SEMANTIC_COORDINATE_AXES:
        values = raw.get(axis)
        if not isinstance(values, (list, tuple, set, frozenset)):
            raise ValueError(f"compositional catalog {axis} must be a list")
        normalized = tuple(str(value).strip() for value in values)
        if any(not value for value in normalized) or len(normalized) != len(set(normalized)):
            raise ValueError(f"compositional catalog {axis} contains invalid values")
        if not normalized:
            raise ValueError(f"compositional catalog {axis} must not be empty")
        result[axis] = normalized
    return result


def _catalog_entry(
    *,
    value: str,
    label: str | None = None,
    aliases: tuple[str, ...] = (),
    **metadata: Any,
) -> dict[str, Any]:
    entry: dict[str, Any] = {"id": value, "value": value}
    if label:
        entry["label"] = label
    if aliases:
        entry["aliases"] = list(aliases)
    for key, item in metadata.items():
        if item is not None:
            entry[key] = list(item) if isinstance(item, tuple) else item
    return entry


def _compositional_catalog_ontology(
    *,
    payload: Mapping[str, Any],
    catalogs: Mapping[str, tuple[str, ...]],
) -> dict[str, list[dict[str, Any]]]:
    """Project the governed V2 coordinate space for the bounded semantic prompt."""
    del payload
    return {
        axis: [_catalog_entry(value=value) for value in catalogs[axis]]
        for axis in SEMANTIC_COORDINATE_AXES
    }


# ---------------------------------------------------------------------------
# C2 coordinate → runtime role fallback table.
#
# Used only when no deterministic hypothesis exists for a column yet the LLM
# has produced a fully governed compositional semantic. Rules are ordered by
# specificity (most required axes first). The first matching rule wins.
# Fail-closed: coordinates not covered by any rule produce (None, None) and
# approved_role stays empty — P7 will correctly report missing requirements.
#
# Rules intentionally omit:
#   - measure=duration  (no P7 role; existing test asserts None)
#   - measure=balance   (no P7 role without further disambiguation)
#   - measure=margin, rate, tax_amount, fee_amount (no direct P7 role)
# ---------------------------------------------------------------------------
_C2_TO_RUNTIME_ROLE: tuple[
    tuple[dict[str, str | None], str, str], ...
] = (
    # ---- 3-axis rules (most specific) ---------------------------------------
    # unit_sale_price: price measure at unit scope in a sale process
    (
        {"measure": "price", "scope": "unit", "process": "sale"},
        "unit_sale_price",
        "sale_price",
    ),
    # ---- 2-axis rules -------------------------------------------------------
    # quantity: quantity measure expressed in units
    (
        {"measure": "quantity", "unit": "units"},
        "quantity",
        "volume_sold",
    ),
    # sales_amount: revenue measure at event scope
    (
        {"measure": "revenue", "scope": "event"},
        "sales_amount",
        "sold_amount",
    ),
    # operation_time: event_date time axis with a time-of-day unit
    (
        {"time": "event_date", "unit": "hours"},
        "operation_time",
        "operation_time",
    ),
    (
        {"time": "event_date", "unit": "minutes"},
        "operation_time",
        "operation_time",
    ),
    # product_identifier: product entity with an identifier or sequence
    (
        {"entity": "product", "identity": "identifier"},
        "product_identifier",
        "product_id",
    ),
    (
        {"entity": "product", "identity": "sequence"},
        "product_identifier",
        "product_id",
    ),
    # branch_identifier: branch entity with a stable identifier
    (
        {"entity": "branch", "identity": "identifier"},
        "branch_identifier",
        "branch_id",
    ),
    # transaction_identifier: process=sale with a sequence/identifier identity
    (
        {"process": "sale", "identity": "sequence"},
        "transaction_identifier",
        "transaction_id",
    ),
    (
        {"process": "sale", "identity": "identifier"},
        "transaction_identifier",
        "transaction_id",
    ),
    # ---- 1-axis rules (broadest; must come after all 2- and 3-axis rules) --
    # operation_date: event_date time (no conflicting time-of-day unit)
    (
        {"time": "event_date"},
        "operation_date",
        "business_period",
    ),
    # unit_cost_candidate: cost measure
    (
        {"measure": "cost"},
        "unit_cost_candidate",
        "cost",
    ),
    # discount_candidate: discount measure
    (
        {"measure": "discount"},
        "discount_candidate",
        "discount",
    ),
    # product_name: product entity (no identity coordinate -> name, not code)
    (
        {"entity": "product"},
        "product_name",
        "product",
    ),
    # branch_name: branch entity (no identity -> readable name)
    (
        {"entity": "branch"},
        "branch_name",
        "branch_name",
    ),
    # sales_channel: grain=sale with no entity and no measure (categorical)
    (
        {"grain": "sale", "entity": None, "measure": None},
        "sales_channel",
        "segment",
    ),
    # payment_method: grain=payment with no entity and no measure (categorical)
    (
        {"grain": "payment", "entity": None, "measure": None},
        "payment_method",
        "payment_method",
    ),
)


def _c2_coordinate_fallback_projection(
    descriptor: "Service1SemanticCoordinateV2",
) -> tuple[str | None, str | None]:
    """Derive a runtime role from C2 coordinate axes when no deterministic
    hypothesis match exists. Returns (None, None) if no rule matches.

    Invariant: caller must have already exhausted the deterministic-hypothesis
    path. This function is a governed projection only — it does not grant any
    runtime, delivery, or owner-confirmation authority.
    """
    for required_axes, role, variable in _C2_TO_RUNTIME_ROLE:
        matched = True
        for axis, expected_value in required_axes.items():
            actual = getattr(descriptor, axis, None)
            if actual != expected_value:
                matched = False
                break
        if matched:
            return role, variable
    return None, None


def _deterministic_runtime_projection(
    *,
    payload: Mapping[str, Any],
    descriptor: Service1SemanticCoordinateV2,
) -> tuple[str | None, str | None]:
    matches: list[Mapping[str, Any]] = []
    for raw in payload.get("deterministic_hypotheses") or ():
        if not isinstance(raw, Mapping):
            continue
        ref = ".".join(
            part for part in (
                str(raw.get("sheet_name") or "").strip(),
                str(raw.get("column_name") or "").strip(),
            ) if part
        )
        if ref == descriptor.field_ref:
            matches.append(raw)
    if len(matches) != 1:
        # No deterministic hypothesis for this column — fall back to the
        # governed C2 coordinate projection table.
        return _c2_coordinate_fallback_projection(descriptor)
    deterministic = matches[0].get("compositional_semantic")
    primary = matches[0].get("primary_hypothesis")
    if not isinstance(deterministic, Mapping) or not isinstance(primary, Mapping):
        return None, None
    for axis in SEMANTIC_COORDINATE_AXES:
        expected = deterministic.get(axis)
        if expected is not None and getattr(descriptor, axis) != expected:
            return None, None
    role = str(primary.get("semantic_role") or "").strip()
    variable = str(primary.get("variable_name") or "").strip()
    if not role or role == "unknown" or not variable or variable == "unknown":
        return None, None
    return role, variable


def _build_compositional_semantic(
    *,
    payload: Mapping[str, Any],
    decision: ColumnSemanticDecisionV1,
    evidence_refs: list[str],
) -> tuple[dict[str, Any], str | None, str | None]:
    raw = decision.compositional_semantic
    if raw is None:  # pragma: no cover - guarded by caller
        raise ValueError("compositional semantic decision is required")
    catalogs = _compositional_catalog_values(payload)
    coordinate_values = {axis: getattr(raw, axis) for axis in SEMANTIC_COORDINATE_AXES}
    if not any(value is not None for value in coordinate_values.values()):
        raise ValueError("compositional semantic requires at least one V2 coordinate")
    for axis, value in coordinate_values.items():
        if value is not None and value not in set(catalogs[axis]):
            raise ValueError(f"compositional semantic {axis} is outside the governed taxonomy")
    descriptor = Service1SemanticCoordinateV2(
        field_ref=decision.column_ref,
        **coordinate_values,
        confidence=raw.confidence,
        evidence=tuple(evidence_refs),
        source="LLM_C2_PROPOSAL",
    ).validate_against(load_service_1_semantic_coordinate_taxonomy_v2())
    # ``to_dict`` is an internal descriptor serialization and includes safety
    # flags such as ``runtime_authorized=False``. Those flags are intentionally
    # forbidden in the LLM proposal contract, so project only its public
    # semantic coordinates at this boundary rather than leaking the internal
    # descriptor representation back into that contract.
    payload_out = {
        axis: getattr(descriptor, axis)
        for axis in SEMANTIC_COORDINATE_AXES
    }
    projected_role, projected_variable = _deterministic_runtime_projection(
        payload=payload,
        descriptor=descriptor,
    )
    payload_out.update(
        field_ref=descriptor.field_ref,
        confidence=descriptor.confidence,
        evidence=list(descriptor.evidence),
        source=descriptor.source,
        runtime_semantic_role=projected_role,
        runtime_variable_name=projected_variable,
    )
    return payload_out, projected_role, projected_variable


def _decision_payload(
    *,
    payload: Mapping[str, Any],
    batch: ColumnSemanticBatchV1,
) -> dict[str, Any]:
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

        if decision.compositional_semantic is not None:
            if evidence_refs[0] not in evidence_registry:
                raise ValueError("compositional semantic has no registered column evidence")
            compositional, projected_role, projected_variable = _build_compositional_semantic(
                payload=payload,
                decision=decision,
                evidence_refs=evidence_refs,
            )
            if projected_role and (
                projected_role not in allowed_roles
                or (relevant_roles and projected_role not in relevant_roles)
            ):
                # C2 business meaning is authoritative only as semantic understanding.
                # A downstream/runtime role restriction must not erase an otherwise
                # valid compositional descriptor; simply withhold the optional
                # runtime projection and let the semantic meaning continue.
                compositional = dict(compositional)
                compositional["runtime_semantic_role"] = None
                compositional["runtime_variable_name"] = None
                projected_role, projected_variable = None, None
            if decision.needs_owner_confirmation:
                ambiguities.append(
                    {
                        "ambiguity_id": f"pydantic-ai:ambiguity:{index}:{column_ref}",
                        "target_refs": [column_ref],
                        "reason": decision.rationale,
                        "confidence": decision.confidence,
                        "evidence_refs": evidence_refs,
                    }
                )
            else:
                concepts.append(
                    {
                        "proposal_id": f"pydantic-ai:concept:{index}:{column_ref}",
                        "target_column_refs": [column_ref],
                        # C2 remains the semantic representation. The exact
                        # deterministic compatibility projection travels inside
                        # its descriptor for P6 and is not an LLM-emitted role.
                        "semantic_role": None,
                        "variable_name": None,
                        "confidence": decision.confidence,
                        "rationale": decision.rationale,
                        "evidence_refs": evidence_refs,
                        "compositional_semantic": compositional,
                    }
                )
                mapped_refs.add(column_ref)
            continue

        productive_v2_context = bool(
            payload.get("workbook_semantic_context")
            or payload.get("workbook_business_understanding")
        )
        if productive_v2_context:
            # F10: governed V2 is the only productive C2 semantic representation.
            # Legacy semantic_role / variable_name may still exist in historical
            # contracts and downstream adapters, but productive C2 never promotes
            # them to semantic truth. Absence of a V2 projection stays explicit.
            if decision.needs_owner_confirmation or role or variable:
                reason = decision.rationale.strip()
                if decision.compositional_semantic is None:
                    reason = (
                        f"{reason} " if reason else ""
                    ) + "No governed V2 compositional projection was produced."
                ambiguities.append(
                    {
                        "ambiguity_id": f"pydantic-ai:ambiguity:{index}:{column_ref}",
                        "target_refs": [column_ref],
                        "reason": reason,
                        "confidence": decision.confidence,
                        "evidence_refs": evidence_refs,
                    }
                )
            continue

        # Historical direct-provider compatibility only. Productive F1+ wiring
        # always supplies workbook_semantic_context, so this branch has no Product
        # Root authority and can be removed with the legacy test surface later.
        role_is_allowed = bool(role and role in allowed_roles)
        role_is_relevant = not relevant_roles or role in relevant_roles
        if role_is_allowed and not role_is_relevant:
            continue
        if role_is_allowed and role_is_relevant and variable and not decision.needs_owner_confirmation:
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

    relationships = _structural_relationship_proposals_from_v2(
        profile=profile,
        evidence_registry=evidence_registry,
        concepts=concepts,
    )
    return {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "concept_proposals": concepts,
        "relationship_proposals": relationships,
        "duplicate_semantics": [],
        "irrelevant_refs": sorted(known_refs - mapped_refs),
        "material_ambiguities": ambiguities,
    }


def _structural_relationship_proposals_from_v2(
    *,
    profile: Mapping[str, Any],
    evidence_registry: Mapping[str, Any],
    concepts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Project governed structural relationships without invoking a semantic engine."""
    semantic_by_ref: dict[str, Mapping[str, Any]] = {}
    for concept in concepts:
        semantic = concept.get("compositional_semantic")
        refs = concept.get("target_column_refs") or []
        if not isinstance(semantic, Mapping) or len(refs) != 1:
            continue
        ref = str(refs[0] or "").strip()
        if ref:
            semantic_by_ref[ref] = semantic

    relationships: list[dict[str, Any]] = []
    for index, relation in enumerate(profile.get("relationships") or [], start=1):
        if not isinstance(relation, Mapping):
            continue
        left = str(relation.get("left_column_ref") or "").strip()
        right = str(relation.get("right_column_ref") or "").strip()
        kind = str(relation.get("relationship_kind") or "").strip()
        if not left or not right or not kind:
            continue
        left_semantic = semantic_by_ref.get(left)
        right_semantic = semantic_by_ref.get(right)
        if not isinstance(left_semantic, Mapping) or not isinstance(right_semantic, Mapping):
            continue
        left_identity = str(left_semantic.get("identity") or "").strip()
        right_identity = str(right_semantic.get("identity") or "").strip()
        left_entity = str(left_semantic.get("entity") or "").strip()
        right_entity = str(right_semantic.get("entity") or "").strip()
        if (
            not left_identity
            or not right_identity
            or left_identity != right_identity
            or not left_entity
            or left_entity != right_entity
        ):
            continue
        evidence_ref = f"ev:relationship:{left}->{right}:overlap"
        if evidence_ref not in evidence_registry:
            continue
        relationships.append(
            {
                "relationship_id": f"structural-v2:relationship:{index}:{left}->{right}",
                "left_column_ref": left,
                "right_column_ref": right,
                "relationship_type": kind,
                "confidence": 1.0,
                "rationale": "Workbook structural relationship corroborated by matching governed V2 identity semantics.",
                "evidence_refs": [evidence_ref],
            }
        )
    return relationships


class Service1PydanticAIColumnSemanticProviderV1:
    """Callable semantic provider with no tools and no calculation authority.

    Runs pydantic-ai agents on a single persistent event loop so concurrent
    threaded web requests never rebind the shared httpx/anyio resources to a
    second loop (which raises "Event bound to a different event loop").
    """

    def __init__(
        self,
        *,
        agent: Any,
        assistant_agent: Any | None = None,
        business_understanding_agent: Any | None = None,
        retry_transient: bool = False,
        provider_timeout_seconds: float | None = None,
    ) -> None:
        self._agent = agent
        self._assistant_agent = assistant_agent
        self._business_understanding_agent = business_understanding_agent
        self._loop = asyncio.new_event_loop()
        self._lock = threading.Lock()
        self._retry_transient = bool(retry_transient)
        self._provider_timeout_seconds = (
            None if provider_timeout_seconds is None else float(provider_timeout_seconds)
        )
        if self._provider_timeout_seconds is not None and self._provider_timeout_seconds <= 0:
            raise ValueError("semantic provider timeout must be greater than zero")
        self.last_call_metrics: list[dict[str, Any]] = []

    @staticmethod
    def _is_transient_transport_error(exc: BaseException) -> bool:
        """Return True only for provider-side transient failures (overload/gateway/timeout).

        Non-retryable (schema, auth, refusal, invalid output) must propagate immediately.
        """
        if isinstance(exc, Service1SemanticTimeoutError):
            context = _current_semantic_execution_context()
            if context is None:
                return False
            if context.cancellation_event.is_set():
                return False
            return time.monotonic() < context.deadline_monotonic
        if isinstance(exc, Service1SemanticProviderTimeoutError):
            return True
        try:
            from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
        except ImportError:  # pragma: no cover - guarded by provider construction
            ModelAPIError = RuntimeError
            ModelHTTPError = RuntimeError
        if isinstance(exc, ModelHTTPError):
            return exc.status_code in {429, 500, 502, 503, 504, 529}
        if isinstance(exc, ModelAPIError):
            message = str(exc).lower()
            return "timed out" in message or "timeout" in message or "connect" in message
        if isinstance(exc, (TimeoutError, ConnectionError)):
            return True
        return False

    def _run_sync(
        self,
        callable_agent: Any,
        prompt: str,
        *,
        invocation_deadline: float | None = None,
    ) -> Any:
        run = getattr(callable_agent, "run", None)
        run_sync = getattr(callable_agent, "run_sync", None)
        if not callable(run) and not callable(run_sync):
            raise RuntimeError("semantic agent exposes no run/run_sync callable")

        attempts = 2 if self._retry_transient else 1
        last_exc: BaseException | None = None
        for attempt in range(attempts):
            if attempt > 0:
                context = _current_semantic_execution_context()
                if context is not None:
                    context.remaining_seconds()
                if invocation_deadline is not None:
                    remaining_invocation = invocation_deadline - time.monotonic()
                    if remaining_invocation <= 0:
                        raise Service1SemanticProviderTimeoutError(
                            "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                        )
                    time.sleep(min(NVIDIA_NIM_RETRY_BACKOFF_SECONDS, remaining_invocation))
                else:
                    time.sleep(NVIDIA_NIM_RETRY_BACKOFF_SECONDS)
            try:
                context = _current_semantic_execution_context()
                remaining = context.remaining_seconds() if context is not None else None
                if invocation_deadline is not None:
                    remaining_invocation = invocation_deadline - time.monotonic()
                    if remaining_invocation <= 0:
                        raise Service1SemanticProviderTimeoutError(
                            "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                        )
                    remaining = (
                        remaining_invocation
                        if remaining is None
                        else min(remaining, remaining_invocation)
                    )
                if callable(run):
                    acquired = (
                        self._lock.acquire()
                        if remaining is None
                        else self._lock.acquire(timeout=remaining)
                    )
                    if not acquired:
                        if invocation_deadline is not None and time.monotonic() >= invocation_deadline:
                            raise Service1SemanticProviderTimeoutError(
                                "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                            )
                        raise Service1SemanticTimeoutError(
                            "SERVICE_1_SEMANTIC_OPERATION_TIMEOUT"
                        )
                    try:
                        if context is not None:
                            remaining = context.remaining_seconds()
                        coroutine = run(prompt)
                        request_timeout = self._provider_timeout_seconds
                        if remaining is not None:
                            request_timeout = (
                                remaining
                                if request_timeout is None
                                else min(remaining, request_timeout)
                            )
                        if request_timeout is None:
                            return self._loop.run_until_complete(coroutine)
                        try:
                            return self._loop.run_until_complete(
                                asyncio.wait_for(coroutine, timeout=request_timeout)
                            )
                        except asyncio.TimeoutError as exc:
                            if context is not None and time.monotonic() >= context.deadline_monotonic:
                                context.cancellation_event.set()
                                raise Service1SemanticTimeoutError(
                                    "SERVICE_1_SEMANTIC_OPERATION_TIMEOUT"
                                ) from exc
                            if invocation_deadline is not None and time.monotonic() >= invocation_deadline:
                                raise Service1SemanticProviderTimeoutError(
                                    "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                                ) from exc
                            raise Service1SemanticProviderTimeoutError(
                                "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                            ) from exc
                    finally:
                        self._lock.release()
                if invocation_deadline is not None and time.monotonic() >= invocation_deadline:
                    raise Service1SemanticProviderTimeoutError(
                        "SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT"
                    )
                if remaining is not None and remaining <= 0:
                    raise Service1SemanticTimeoutError(
                        "SERVICE_1_SEMANTIC_OPERATION_TIMEOUT"
                    )
                if remaining is not None:
                    raise Service1SemanticTimeoutError(
                        "SERVICE_1_SEMANTIC_SYNC_AGENT_CANNOT_BE_CANCELLED"
                    )
                return run_sync(prompt)
            except BaseException as exc:  # provider boundary; decide retry vs fail-closed
                last_exc = exc
                if attempt == attempts - 1 or not self._is_transient_transport_error(exc):
                    raise
        assert last_exc is not None  # pragma: no cover - attempts >= 1
        raise last_exc

    def understand_workbook(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self._business_understanding_agent is None:
            raise RuntimeError("workbook business-understanding agent is not configured")
        workbook_context = payload.get("workbook_semantic_context")
        if not isinstance(workbook_context, Mapping) or not workbook_context.get("tables"):
            raise ValueError("workbook_semantic_context is required for business understanding")
        tables = [item for item in workbook_context.get("tables") or () if isinstance(item, Mapping)]
        if not tables:
            raise ValueError("workbook_semantic_context contains no tables")
        expected_sheets = [str(table.get("sheet_name") or "").strip() for table in tables]
        prompt_payload = {
            "case_id": str(payload.get("case_id") or "").strip(),
            "workbook_semantic_context": dict(workbook_context),
            "semantic_knowledge_context": dict(payload.get("semantic_knowledge_context") or {}),
        }
        prompt = json.dumps(prompt_payload, ensure_ascii=False, default=str)
        self.last_call_metrics = [item for item in self.last_call_metrics if item.get("stage") != "WORKBOOK_BUSINESS_UNDERSTANDING"]
        self.last_call_metrics.append({
            "stage": "WORKBOOK_BUSINESS_UNDERSTANDING",
            "group": "workbook",
            "input_chars": len(prompt),
            "estimated_input_tokens": (len(prompt) + 3) // 4,
            "column_refs": [
                item.get("column_ref")
                for table in tables
                for item in table.get("columns") or ()
                if isinstance(item, Mapping)
            ],
        })
        result = self._run_sync(self._business_understanding_agent, prompt)
        output = getattr(result, "output", None)
        understanding = (
            output
            if isinstance(output, WorkbookBusinessUnderstandingV1)
            else WorkbookBusinessUnderstandingV1.model_validate(output)
        )
        returned_sheets = [table.sheet_name.strip() for table in understanding.tables]
        if sorted(returned_sheets) != sorted(expected_sheets) or len(returned_sheets) != len(expected_sheets):
            raise ValueError(
                "WORKBOOK_GROUP_COVERAGE_INVALID:"
                + ",".join(sorted(set(expected_sheets) ^ set(returned_sheets)))
            )

        workbook_summary = "Workbook structural summary: " + ", ".join(
            f"{table.sheet_name} ({table.table_meaning.strip()})" for table in understanding.tables
        )
        return {
            "schema_version": BUSINESS_UNDERSTANDING_SCHEMA_VERSION,
            "authority": BUSINESS_UNDERSTANDING_AUTHORITY,
            "workbook_summary": workbook_summary,
            "tables": [item.model_dump() for item in understanding.tables],
            "material_ambiguities": list(dict.fromkeys(understanding.material_ambiguities)),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("semantic provider payload must be a mapping")
        groups = _column_groups(payload)
        expected_refs = [
            str(item.get("column_ref") or "").strip()
            for item in (payload.get("workbook_profile") or {}).get("columns") or ()
            if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
        ]
        batches: list[ColumnSemanticBatchV1] = []
        self.last_call_metrics = [item for item in self.last_call_metrics if item.get("stage") != "COLUMN_SEMANTICS"]
        invocation_deadline = (
            None
            if self._provider_timeout_seconds is None
            else time.monotonic() + self._provider_timeout_seconds
        )
        for index, refs in enumerate(groups, start=1):
            context = _compact_column_context(payload, selected_refs=set(refs))
            prompt = json.dumps(context, ensure_ascii=False, default=str)
            self.last_call_metrics.append({
                "stage": "COLUMN_SEMANTICS",
                "group": index,
                "input_chars": len(prompt),
                "estimated_input_tokens": (len(prompt) + 3) // 4,
                "column_refs": list(refs),
            })
            result = self._run_sync(
                self._agent,
                prompt,
                invocation_deadline=invocation_deadline,
            )
            output = getattr(result, "output", None)
            batches.append(
                output if isinstance(output, ColumnSemanticBatchV1)
                else ColumnSemanticBatchV1.model_validate(output)
            )
        batch = _merge_batches(batches=batches, expected_refs=expected_refs)
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
        suggested = reply.suggested_compositional_semantic
        return {
            "response_text": reply.response_text.strip(),
            "suggested_compositional_semantic": (
                None if suggested is None else suggested.model_dump()
            ),
            "suggestion_reason": reply.suggestion_reason,
        }


@dataclass(frozen=True, slots=True)
class Service1SemanticProviderStepV1:
    """One named provider in the governed productive order."""

    provider: Any
    provider_name: str
    model: str


class Service1SemanticProviderResultV1(dict[str, Any]):
    """Closed semantic proposal plus system-owned provider provenance.

    Provenance intentionally stays outside the mapping keys: the mapping crosses
    into the closed LLM proposal parser, where a model-provided ``provenance``
    key must remain an unknown-field failure. The virtual legacy accessor keeps
    provider-chain observability available to callers without contaminating the
    proposal contract.
    """

    def __init__(self, result: Mapping[str, Any], *, provider_provenance: Mapping[str, Any]) -> None:
        super().__init__(result)
        self.provider_provenance = dict(provider_provenance)

    def __getitem__(self, key: str) -> Any:
        if key == "provenance" and key not in self:
            return self.provider_provenance
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "provenance" and key not in self:
            return self.provider_provenance
        return super().get(key, default)


class Service1SemanticProviderChainV1:
    """Governed ordered provider chain for transient provider failures only.

    Providers are invoked in the owner-declared productive order: Gemini primary,
    NVIDIA NIM second, OpenCode Zen third. A provider is only skipped to the next
    one when it fails with a transient provider error (429/500/502/503/504/529 or
    transport timeout/connection). Non-transient failures (invalid JSON/schema,
    Pydantic or semantic validation, refusal, structurally invalid output) fail
    closed without any fallback. When every provider in the chain fails
    transiently, the last transient error propagates as an explicit productive
    block. Provenance records which provider produced the result.
    """

    def __init__(self, *, steps: Sequence[Service1SemanticProviderStepV1]) -> None:
        resolved = tuple(steps)
        if not resolved:
            raise ValueError("semantic provider chain requires at least one step")
        self._steps = resolved

    def _provenance(self, *, served_index: int, primary_failure_reason: str | None) -> dict[str, Any]:
        primary = self._steps[0]
        served = self._steps[served_index]
        return {
            "primary_provider": primary.provider_name,
            "primary_model": primary.model,
            "primary_failure_reason": primary_failure_reason,
            "fallback_used": served_index != 0,
            "final_provider": served.provider_name,
            "final_model": served.model,
            "attempted_providers": [
                step.provider_name for step in self._steps[: served_index + 1]
            ],
        }

    def _with_provenance(self, result: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
        return Service1SemanticProviderResultV1(
            result,
            provider_provenance=provenance,
        )

    @staticmethod
    def _global_budget_remaining_seconds() -> float | None:
        context = _current_semantic_execution_context()
        if context is None:
            return None
        return round(max(0.0, context.deadline_monotonic - time.monotonic()), 3)

    @staticmethod
    def _safe_attempt_timeout_seconds(step: Service1SemanticProviderStepV1) -> float:
        """Return the bounded timeout that must fit inside the global budget."""
        configured = getattr(step.provider, "_provider_timeout_seconds", None)
        if configured is not None:
            return max(0.001, float(configured))
        if step.provider_name == GEMINI_PROVIDER:
            return GEMINI_TIMEOUT_SECONDS
        return SEMANTIC_TIMEOUT_SECONDS

    @classmethod
    def _retry_budget_available(
        cls,
        *,
        step: Service1SemanticProviderStepV1,
        fallback_step: Service1SemanticProviderStepV1 | None,
        remaining: float | None,
    ) -> bool:
        if remaining is None:
            return True
        # Retrying the current provider is optional; preserving one bounded
        # opportunity for the next owner-authorized provider is mandatory.
        # Otherwise Gemini can use two 120 s attempts inside a 300 s operation
        # and leave NVIDIA no viable 180 s fallback window.
        required = cls._safe_attempt_timeout_seconds(step) + SEMANTIC_RETRY_BACKOFF_SECONDS
        if fallback_step is not None:
            required += cls._safe_attempt_timeout_seconds(fallback_step)
        return remaining >= required

    @staticmethod
    def _failure_reason(exc: BaseException) -> str:
        status = getattr(exc, "status_code", "")
        suffix = f":{status}" if status not in (None, "") else ""
        return type(exc).__name__ + suffix

    def _invoke(self, method: str, payload: Any) -> dict[str, Any]:
        last_exc: BaseException | None = None
        attempts: list[dict[str, Any]] = []
        saw_transient_failure = False
        for index, step in enumerate(self._steps):
            fallback_step = self._steps[index + 1] if index + 1 < len(self._steps) else None
            target = getattr(step.provider, method, None)
            if not callable(target):
                error = RuntimeError(
                    f"{step.provider_name} does not expose the required method"
                )
                setattr(error, "service1_provider_attempts", attempts)
                raise error
            for retry_number in range(SEMANTIC_MAX_RETRIES + 1):
                attempt_number = retry_number + 1
                global_budget_before = self._global_budget_remaining_seconds()
                if retry_number > 0:
                    if not self._retry_budget_available(
                        step=step,
                        fallback_step=fallback_step,
                        remaining=global_budget_before,
                    ):
                        attempts.append(
                            {
                                "provider": step.provider_name,
                                "model": step.model,
                                "method": method,
                                "provider_attempt_number": attempt_number,
                                "retry_number": retry_number,
                                "elapsed_seconds": 0.0,
                                "global_budget_before_seconds": global_budget_before,
                                "global_budget_after_seconds": self._global_budget_remaining_seconds(),
                                "exception_type": type(last_exc).__name__ if last_exc else None,
                                "http_status": getattr(last_exc, "status_code", None) if last_exc else None,
                                "classification": "transient_fallback_eligible",
                                "retry_decision": "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET",
                                "fallback_decision": "advance_to_next_provider",
                                "terminal_condition": "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET",
                            }
                        )
                        break
                    time.sleep(SEMANTIC_RETRY_BACKOFF_SECONDS)
                    global_budget_before = self._global_budget_remaining_seconds()

                started_at = time.monotonic()
                try:
                    result = target(payload)
                except BaseException as exc:
                    fallback_eligible = Service1PydanticAIColumnSemanticProviderV1._is_transient_transport_error(exc)
                    if fallback_eligible:
                        saw_transient_failure = True
                    if not fallback_eligible:
                        retry_decision = "not_retryable"
                        fallback_decision = "blocked"
                        terminal_condition = "NON_TRANSIENT_FAILURE"
                    elif retry_number < SEMANTIC_MAX_RETRIES:
                        retry_decision = (
                            "retry_same_provider"
                            if self._retry_budget_available(
                                step=step,
                                fallback_step=fallback_step,
                                remaining=self._global_budget_remaining_seconds(),
                            )
                            else "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET"
                        )
                        fallback_decision = (
                            "deferred_retry"
                            if retry_decision == "retry_same_provider"
                            else "advance_to_next_provider"
                        )
                        terminal_condition = (
                            None
                            if retry_decision == "retry_same_provider"
                            else "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET"
                        )
                    else:
                        retry_decision = "retry_exhausted"
                        fallback_decision = "advance_to_next_provider"
                        terminal_condition = "PROVIDER_RETRY_EXHAUSTED"
                    attempts.append(
                        {
                            "provider": step.provider_name,
                            "model": step.model,
                            "method": method,
                            "provider_attempt_number": attempt_number,
                            "retry_number": retry_number,
                            "elapsed_seconds": round(max(0.0, time.monotonic() - started_at), 3),
                            "global_budget_before_seconds": global_budget_before,
                            "global_budget_after_seconds": self._global_budget_remaining_seconds(),
                            "exception_type": type(exc).__name__,
                            "http_status": getattr(exc, "status_code", None),
                            "classification": (
                                "transient_fallback_eligible"
                                if fallback_eligible
                                else "terminal_non_fallback"
                            ),
                            "retry_decision": retry_decision,
                            "fallback_decision": fallback_decision,
                            "terminal_condition": terminal_condition,
                        }
                    )
                    if retry_decision == "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET":
                        attempts.append(
                            {
                                "provider": step.provider_name,
                                "model": step.model,
                                "method": method,
                                "provider_attempt_number": attempt_number + 1,
                                "retry_number": retry_number + 1,
                                "elapsed_seconds": 0.0,
                                "global_budget_before_seconds": self._global_budget_remaining_seconds(),
                                "global_budget_after_seconds": self._global_budget_remaining_seconds(),
                                "exception_type": type(exc).__name__,
                                "http_status": getattr(exc, "status_code", None),
                                "classification": "transient_fallback_eligible",
                                "retry_decision": "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET",
                                "fallback_decision": "advance_to_next_provider",
                                "terminal_condition": "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET",
                            }
                        )
                    if not fallback_eligible:
                        if saw_transient_failure:
                            failure = Service1TransientProviderFailureV1(
                                "TRANSIENT_PROVIDER_FAILURE: provider unavailable after bounded retries",
                                provider_attempts=attempts,
                                attempted_providers=[step.provider_name for step in self._steps],
                            )
                            setattr(failure, "service1_provider_attempts", attempts)
                            raise failure from exc
                        setattr(exc, "service1_provider_attempts", attempts)
                        raise
                    last_exc = exc
                    if retry_decision != "retry_same_provider":
                        break
                    continue

                attempts.append(
                    {
                        "provider": step.provider_name,
                        "model": step.model,
                        "method": method,
                        "provider_attempt_number": attempt_number,
                        "retry_number": retry_number,
                        "elapsed_seconds": round(max(0.0, time.monotonic() - started_at), 3),
                        "global_budget_before_seconds": global_budget_before,
                        "global_budget_after_seconds": self._global_budget_remaining_seconds(),
                        "exception_type": None,
                        "http_status": None,
                        "classification": "success",
                        "retry_decision": "none" if retry_number == 0 else "retry_succeeded",
                        "fallback_decision": "serve_provider",
                        "terminal_condition": None,
                    }
                )
                if not isinstance(result, dict):
                    error = RuntimeError(
                        f"{step.provider_name} returned a non-mapping result"
                    )
                    setattr(error, "service1_provider_attempts", attempts)
                    raise error
                reason = self._failure_reason(last_exc) if last_exc is not None else None
                provenance = self._provenance(
                    served_index=index,
                    primary_failure_reason=reason,
                )
                provenance["provider_attempts"] = attempts
                return self._with_provenance(
                    result,
                    provenance,
                )
        if last_exc is not None:
            failure = Service1TransientProviderFailureV1(
                "TRANSIENT_PROVIDER_FAILURE: provider unavailable after bounded retries",
                provider_attempts=attempts,
                attempted_providers=[step.provider_name for step in self._steps],
            )
            setattr(failure, "service1_provider_attempts", attempts)
            raise failure from last_exc
        raise RuntimeError("semantic provider chain exhausted without a result")

    def understand_workbook(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._invoke("understand_workbook", payload)

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._invoke("__call__", payload)

    def assist(self, payload: Mapping[str, Any]) -> dict[str, str]:
        last_exc: BaseException | None = None
        for step in self._steps:
            target = getattr(step.provider, "assist", None)
            if not callable(target):
                raise RuntimeError(
                    f"{step.provider_name} does not expose the required assist method"
                )
            try:
                return target(payload)
            except BaseException as exc:
                if not Service1PydanticAIColumnSemanticProviderV1._is_transient_transport_error(exc):
                    raise
                last_exc = exc
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("semantic provider chain exhausted without an assist result")


def build_service_1_semantic_provider_chain_v1(
    *,
    steps: Sequence[Service1SemanticProviderStepV1],
) -> Service1SemanticProviderChainV1:
    """Build the governed ordered provider chain.

    Steps are ordered primary-first following the owner decision:
    Gemini -> NVIDIA NIM -> OpenCode Zen. Each step carries its own provider
    and model so environment wiring cannot reuse one provider's model for
    another provider.
    """
    return Service1SemanticProviderChainV1(steps=steps)


def build_service_1_semantic_fallback_provider_v1(
    *,
    primary_provider: Any,
    fallback_provider: Any,
    primary_provider_name: str,
    primary_model: str,
    fallback_provider_name: str,
    fallback_model: str,
) -> Service1SemanticProviderChainV1:
    """Build a two-step semantic provider chain (primary plus one fallback).

    Preserved as the generic two-provider convenience over the chain; the
    productive environment wiring uses the full ordered chain instead.
    """
    return Service1SemanticProviderChainV1(
        steps=[
            Service1SemanticProviderStepV1(
                provider=primary_provider,
                provider_name=primary_provider_name,
                model=primary_model,
            ),
            Service1SemanticProviderStepV1(
                provider=fallback_provider,
                provider_name=fallback_provider_name,
                model=fallback_model,
            ),
        ],
    )


def _vertex_openai_base_url_v1(*, project: str, location: str) -> str:
    host = (
        "https://aiplatform.googleapis.com"
        if location == "global"
        else f"https://{location}-aiplatform.googleapis.com"
    )
    return f"{host}/v1/projects/{project}/locations/{location}/endpoints/openapi"


def _vertex_open_model_name_v1(model_name: str) -> str:
    if "/" in model_name:
        return model_name
    if model_name.startswith("gemma-"):
        return f"google/{model_name}"
    return model_name


def _build_vertex_open_model_v1(*, model_name: str, project: str, location: str) -> Any:
    try:
        import google.auth
        from google.auth.transport.requests import Request
        from pydantic_ai.models.openai import OpenAIChatModel, OpenAIModelProfile
        from pydantic_ai.providers import openai as openai_provider_module
        from pydantic_ai.providers.openai import OpenAIProvider
    except ImportError as exc:  # pragma: no cover - environment contract
        raise RuntimeError("Vertex open-model dependencies are required for semantic LLM mode") from exc

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    refresh_request = Request()
    refresh_lock = threading.Lock()

    async def access_token() -> str:
        def current_token() -> str:
            with refresh_lock:
                if not credentials.valid or not credentials.token:
                    credentials.refresh(refresh_request)
                token = str(credentials.token or "").strip()
                if not token:
                    raise RuntimeError("Google Cloud ADC returned no access token")
                return token

        return await asyncio.to_thread(current_token)

    client = openai_provider_module.AsyncOpenAI(
        base_url=_vertex_openai_base_url_v1(project=project, location=location),
        api_key=access_token,
    )
    provider = OpenAIProvider(openai_client=client)
    profile = OpenAIModelProfile(
        supports_json_object_output=True,
        default_structured_output_mode="prompted",
        openai_supports_strict_tool_definition=False,
    )
    return OpenAIChatModel(
        _vertex_open_model_name_v1(model_name),
        provider=provider,
        profile=profile,
    )


def _build_nvidia_nim_open_model_v1(
    *,
    model_name: str,
    base_url: str,
    api_key: str,
) -> Any:
    """Build the same bounded OpenAI-compatible model seam for NVIDIA NIM."""
    try:
        from pydantic_ai.models.openai import OpenAIChatModel, OpenAIModelProfile
        from pydantic_ai.providers.openai import OpenAIProvider
        from openai import AsyncOpenAI
    except ImportError as exc:  # pragma: no cover - environment contract
        raise RuntimeError("pydantic-ai OpenAI dependencies are required for NVIDIA NIM semantic mode") from exc

    resolved_base_url = str(base_url or "").strip()
    resolved_api_key = str(api_key or "").strip()
    if not resolved_base_url:
        raise RuntimeError(f"{SEMANTIC_BASE_URL_ENV} is required for NVIDIA NIM semantic mode")
    if not resolved_api_key:
        raise RuntimeError(f"{NVIDIA_API_KEY_ENV} is required for NVIDIA NIM semantic mode")

    client = AsyncOpenAI(
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        timeout=SEMANTIC_TIMEOUT_SECONDS,
        max_retries=NVIDIA_NIM_MAX_RETRIES,
    )
    provider = OpenAIProvider(openai_client=client)
    profile = OpenAIModelProfile(
        supports_json_object_output=True,
        default_structured_output_mode="prompted",
        openai_supports_strict_tool_definition=False,
        openai_chat_supports_max_completion_tokens=False,
    )
    return OpenAIChatModel(
        str(model_name).strip(),
        provider=provider,
        profile=profile,
    )


def _build_opencode_zen_responses_model_v1(
    *,
    model_name: str,
    base_url: str,
    api_key: str,
) -> Any:
    """Build the bounded OpenCode Zen model through the Responses API."""
    try:
        from pydantic_ai.models.openai import OpenAIModelProfile, OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from openai import AsyncOpenAI
    except ImportError as exc:  # pragma: no cover - environment contract
        raise RuntimeError("pydantic-ai OpenAI Responses dependencies are required for OpenCode Zen semantic mode") from exc

    resolved_base_url = str(base_url or "").strip()
    resolved_api_key = str(api_key or "").strip()
    if not resolved_base_url:
        raise RuntimeError(f"{SEMANTIC_BASE_URL_ENV} is required for OpenCode Zen semantic mode")
    if not resolved_api_key:
        raise RuntimeError(f"{OPENCODE_API_KEY_ENV} is required for OpenCode Zen semantic mode")

    client = AsyncOpenAI(
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        timeout=NVIDIA_NIM_TIMEOUT_SECONDS,
        max_retries=NVIDIA_NIM_MAX_RETRIES,
    )
    provider = OpenAIProvider(openai_client=client)
    profile = OpenAIModelProfile(
        supports_json_object_output=True,
        default_structured_output_mode="prompted",
        openai_supports_strict_tool_definition=False,
    )
    return OpenAIResponsesModel(
        str(model_name).strip(),
        provider=provider,
        profile=profile,
    )


def build_service_1_pydantic_ai_column_semantic_provider_v1(
    *,
    model: str,
    agent_factory: Callable[..., Any] | None = None,
    provider_timeout_seconds: float | None = None,
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
        elif (
            model_name.startswith("gemma-")
            or model_name.startswith("google/gemma-")
        ) and model_name.endswith("-maas"):
            if not project or not location:
                raise RuntimeError("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION are required for Vertex semantic mode")
            resolved_model = _build_vertex_open_model_v1(
                model_name=model_name,
                project=project,
                location=location,
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
    business_understanding_agent = agent_factory(
        resolved_model,
        output_type=WorkbookBusinessUnderstandingV1,
        instructions=_BUSINESS_UNDERSTANDING_SYSTEM_PROMPT,
    )
    return Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        assistant_agent=assistant_agent,
        business_understanding_agent=business_understanding_agent,
        provider_timeout_seconds=provider_timeout_seconds,
    )


def build_service_1_gemini_column_semantic_provider_v1(
    *,
    model: str = GEMINI_MODEL,
    api_key: str | None = None,
) -> Service1PydanticAIColumnSemanticProviderV1:
    """Create the existing semantic provider seam backed by Gemini API key auth."""
    model_name = str(model or "").strip()
    if not model_name:
        raise ValueError(f"{SEMANTIC_MODEL_ENV} is required for Gemini semantic mode")
    resolved_api_key = str(
        api_key if api_key is not None else os.getenv(GEMINI_API_KEY_ENV, "") or ""
    ).strip()
    if not resolved_api_key:
        raise RuntimeError(f"{GEMINI_API_KEY_ENV} is required for Gemini semantic mode")
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider
    except ImportError as exc:  # pragma: no cover - environment contract
        raise RuntimeError("pydantic-ai google dependencies are required for Gemini semantic mode") from exc

    resolved_model = GoogleModel(
        model_name,
        provider=GoogleProvider(api_key=resolved_api_key),
    )

    def _agent_factory(_: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("model_settings", dict(_GEMINI_MODEL_SETTINGS))
        kwargs.setdefault("retries", 0)
        return Agent(resolved_model, **kwargs)

    return build_service_1_pydantic_ai_column_semantic_provider_v1(
        model=model_name,
        agent_factory=_agent_factory,
        provider_timeout_seconds=GEMINI_TIMEOUT_SECONDS,
    )


def build_service_1_nvidia_nim_column_semantic_provider_v1(
    *,
    model: str = NVIDIA_NIM_MODEL,
    base_url: str = NVIDIA_NIM_BASE_URL,
    api_key: str | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> Service1PydanticAIColumnSemanticProviderV1:
    """Create the existing SEM-8 provider seam backed by NVIDIA NIM."""
    model_name = str(model or "").strip()
    if not model_name:
        raise ValueError(f"{SEMANTIC_MODEL_ENV} is required for NVIDIA NIM semantic mode")
    resolved_api_key = str(api_key if api_key is not None else os.getenv(NVIDIA_API_KEY_ENV, "") or "").strip()
    if agent_factory is None:
        try:
            from pydantic_ai import Agent
        except ImportError as exc:  # pragma: no cover - environment contract
            raise RuntimeError("pydantic-ai is required for semantic LLM mode") from exc
        agent_factory = Agent
        resolved_model = _build_nvidia_nim_open_model_v1(
            model_name=model_name,
            base_url=base_url,
            api_key=resolved_api_key,
        )
    else:
        resolved_model = model_name
    agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticBatchV1,
        instructions=_SYSTEM_PROMPT,
        model_settings=dict(_NVIDIA_NIM_COLUMN_MODEL_SETTINGS),
        retries=NVIDIA_NIM_MAX_RETRIES,
    )
    assistant_agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticAssistanceReplyV1,
        instructions=_ASSISTANT_SYSTEM_PROMPT,
        model_settings=dict(_NVIDIA_NIM_MODEL_SETTINGS),
        retries=NVIDIA_NIM_MAX_RETRIES,
    )
    business_understanding_agent = agent_factory(
        resolved_model,
        output_type=WorkbookBusinessUnderstandingV1,
        instructions=_BUSINESS_UNDERSTANDING_SYSTEM_PROMPT,
        model_settings=dict(_NVIDIA_NIM_WORKBOOK_MODEL_SETTINGS),
        retries=NVIDIA_NIM_MAX_RETRIES,
    )
    return Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        assistant_agent=assistant_agent,
        business_understanding_agent=business_understanding_agent,
        retry_transient=False,
        provider_timeout_seconds=NVIDIA_NIM_TIMEOUT_SECONDS,
    )


def build_service_1_opencode_zen_column_semantic_provider_v1(
    *,
    model: str = OPENCODE_ZEN_MODEL,
    base_url: str = OPENCODE_ZEN_BASE_URL,
    api_key: str | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> Service1PydanticAIColumnSemanticProviderV1:
    """Create the existing SEM-8 provider seam backed by OpenCode Zen Responses."""
    model_name = str(model or "").strip()
    if not model_name:
        raise ValueError(f"{SEMANTIC_MODEL_ENV} is required for OpenCode Zen semantic mode")
    resolved_api_key = str(api_key if api_key is not None else os.getenv(OPENCODE_API_KEY_ENV, "") or "").strip()
    try:
        from pydantic_ai import NativeOutput
    except ImportError as exc:  # pragma: no cover - environment contract
        raise RuntimeError("pydantic-ai is required for semantic LLM mode") from exc
    if agent_factory is None:
        try:
            from pydantic_ai import Agent
        except ImportError as exc:  # pragma: no cover - environment contract
            raise RuntimeError("pydantic-ai is required for semantic LLM mode") from exc
        agent_factory = Agent
        resolved_model = _build_opencode_zen_responses_model_v1(
            model_name=model_name,
            base_url=base_url,
            api_key=resolved_api_key,
        )
    else:
        resolved_model = model_name
    agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticBatchV1,
        instructions=_SYSTEM_PROMPT,
        model_settings=dict(_OPENCODE_ZEN_COLUMN_MODEL_SETTINGS),
        retries=0,
    )
    assistant_agent = agent_factory(
        resolved_model,
        output_type=ColumnSemanticAssistanceReplyV1,
        instructions=_ASSISTANT_SYSTEM_PROMPT,
        model_settings=dict(_OPENCODE_ZEN_MODEL_SETTINGS),
        retries=0,
    )
    business_understanding_agent = agent_factory(
        resolved_model,
        output_type=NativeOutput(WorkbookBusinessUnderstandingV1),
        instructions=_BUSINESS_UNDERSTANDING_SYSTEM_PROMPT,
        model_settings=dict(_OPENCODE_ZEN_WORKBOOK_MODEL_SETTINGS),
        retries=0,
    )
    return Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        assistant_agent=assistant_agent,
        business_understanding_agent=business_understanding_agent,
    )


def semantic_provider_from_environment_v1() -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Resolve the productive C2 provider chain, fail-closed when unconfigured.

    Provider order follows the owner decision: Gemini primary, NVIDIA NIM
    second. Each provider participates only when its credentials are present;
    a provider missing its API key is omitted from the chain (a config gap,
    not a runtime fallback). OpenCode Zen is intentionally NOT appended
    automatically: its free-tier credential only serves inside the OpenCode
    client (FreeTierError HTTP 403 server-side), so automatic invocation
    would convert every NVIDIA outage into a secondary auth failure. The
    explicit Zen builder remains available for manual/governed chains. The
    chain fails closed when the primary is unconfigured and every configured
    provider exhausts its transient budget. F10 retires the automatic
    deterministic semantic fallback: deterministic hypotheses remain
    evidence/context but productive semantic interpretation requires the
    configured V2-capable LLM provider chain.
    """

    steps: list[Service1SemanticProviderStepV1] = []

    gemini_api_key = os.getenv(GEMINI_API_KEY_ENV, "").strip()
    if gemini_api_key:
        gemini_model = os.getenv(GEMINI_MODEL_ENV, GEMINI_MODEL).strip() or GEMINI_MODEL
        steps.append(
            Service1SemanticProviderStepV1(
                provider=build_service_1_gemini_column_semantic_provider_v1(
                    model=gemini_model,
                    api_key=gemini_api_key,
                ),
                provider_name=GEMINI_PROVIDER,
                model=gemini_model,
            )
        )

    nvidia_api_key = os.getenv(NVIDIA_API_KEY_ENV, "").strip()
    if nvidia_api_key:
        # Priority: canonical Service-1 name → VTV-compatible alias → hard-coded default (EOL guard).
        nvidia_model = (
            os.getenv(NVIDIA_NIM_MODEL_ENV, "").strip()
            or os.getenv("NVIDIA_MODEL", "").strip()
            or NVIDIA_NIM_MODEL
        )
        nvidia_base_url = (
            os.getenv(SEMANTIC_BASE_URL_ENV, "").strip()
            or os.getenv("NVIDIA_BASE_URL", "").strip()
            or NVIDIA_NIM_BASE_URL
        )
        steps.append(
            Service1SemanticProviderStepV1(
                provider=build_service_1_nvidia_nim_column_semantic_provider_v1(
                    model=nvidia_model,
                    base_url=nvidia_base_url,
                    api_key=nvidia_api_key,
                ),
                provider_name=NVIDIA_NIM_PROVIDER,
                model=nvidia_model,
            )
        )

    # NOTE: OpenCode Zen is deliberately not appended automatically. Its
    # free-tier credential only serves inside the OpenCode client (HTTP 403
    # FreeTierError server-side), so automatic inclusion turned NVIDIA
    # outages into secondary auth failures. Use the explicit Zen builder
    # for manual/governed chains only.

    if not steps:
        def _missing_productive_c2_provider(_: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("PYMIA_SEMANTIC_LLM_MODEL is required for productive C2 semantics")
        return _missing_productive_c2_provider

    return Service1SemanticProviderChainV1(steps=steps)


__all__ = [
    "ColumnSemanticAssistanceReplyV1",
    "ColumnSemanticBatchV1",
    "ColumnSemanticDecisionV1",
    "CompositionalSemanticProposalV1",
    "Service1PydanticAIColumnSemanticProviderV1",
    "NVIDIA_NIM_BASE_URL",
    "NVIDIA_NIM_MODEL",
    "NVIDIA_NIM_PROVIDER",
    "OPENCODE_ZEN_BASE_URL",
    "OPENCODE_ZEN_MODEL",
    "OPENCODE_ZEN_MODEL_ENV",
    "OPENCODE_ZEN_PROVIDER",
    "GEMINI_API_KEY_ENV",
    "GEMINI_MODEL",
    "GEMINI_MODEL_ENV",
    "GEMINI_PROVIDER",
    "GEMINI_TIMEOUT_SECONDS",
    "Service1SemanticTimeoutError",
    "Service1SemanticProviderTimeoutError",
    "build_service_1_pydantic_ai_column_semantic_provider_v1",
    "build_service_1_gemini_column_semantic_provider_v1",
    "build_service_1_nvidia_nim_column_semantic_provider_v1",
    "build_service_1_opencode_zen_column_semantic_provider_v1",
    "build_service_1_semantic_fallback_provider_v1",
    "build_service_1_semantic_provider_chain_v1",
    "Service1SemanticProviderStepV1",
    "Service1SemanticProviderChainV1",
    "semantic_provider_from_environment_v1",
]
