"""D5 table-scoped semantic context for Servicio 1.

Evidence-only projection from D2 logical-table candidates and the D4
relationship graph into the existing semantic chain.  This module does not
interpret business meaning, call an LLM, confirm owner evidence, execute joins,
or grant runtime/computability authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_TABLE_SCOPED_SEMANTIC_CONTEXT_V1"
STATUS_READY: Final[str] = "TABLE_SCOPED_SEMANTIC_CONTEXT_READY"
STATUS_PARTIAL: Final[str] = "TABLE_SCOPED_SEMANTIC_CONTEXT_PARTIAL"
STATUS_BLOCKED: Final[str] = "BLOCKED"

SCOPE_RESOLVED: Final[str] = "RESOLVED"
SCOPE_UNRESOLVED: Final[str] = "UNRESOLVED"
GRAIN_RESOLVED: Final[str] = "RESOLVED"
GRAIN_UNRESOLVED: Final[str] = "UNRESOLVED"

_D2_INSTANCE_REF_RE: Final[re.Pattern[str]] = re.compile(r"^lt_.+_r[0-9]+$")
_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "join_execution_authorized",
    "computability_authorized",
    "semantic_rebind_authorized",
)


@dataclass(frozen=True)
class Service1ColumnSemanticScopeV1:
    column_ref: str
    sheet_ref: str
    normalized_header: str
    logical_table_ref: str | None
    region_refs: tuple[str, ...]
    grain_state: str
    grain_ref: str | None
    relationship_context_refs: tuple[str, ...]
    scope_state: str
    unresolved_reason: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    join_execution_authorized: bool = False
    computability_authorized: bool = False
    semantic_rebind_authorized: bool = False

    def __post_init__(self) -> None:
        if not str(self.column_ref or "").strip():
            raise ValueError("column_ref must be non-empty")
        if not str(self.sheet_ref or "").strip():
            raise ValueError("sheet_ref must be non-empty")
        if not str(self.normalized_header or "").strip():
            raise ValueError("normalized_header must be non-empty")
        if self.scope_state not in {SCOPE_RESOLVED, SCOPE_UNRESOLVED}:
            raise ValueError("unsupported scope_state")
        if self.grain_state not in {GRAIN_RESOLVED, GRAIN_UNRESOLVED}:
            raise ValueError("unsupported grain_state")
        if self.scope_state == SCOPE_RESOLVED and not self.logical_table_ref:
            raise ValueError("resolved scope requires logical_table_ref")
        object.__setattr__(self, "region_refs", tuple(dict.fromkeys(str(item) for item in self.region_refs if str(item).strip())))
        object.__setattr__(self, "relationship_context_refs", tuple(dict.fromkeys(str(item) for item in self.relationship_context_refs if str(item).strip())))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in (
            "runtime_authorized",
            "join_execution_authorized",
            "computability_authorized",
            "semantic_rebind_authorized",
        ):
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_table_scoped_semantic_context_v1(
    *,
    column_refs: Sequence[Mapping[str, Any]],
    logical_table_candidates: Sequence[Mapping[str, Any]] | Mapping[str, Any],
    logical_relationship_graph: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve each semantic column to exactly one D2 logical table when possible."""
    candidates = _candidate_records(logical_table_candidates)
    if not candidates:
        return _blocked("LOGICAL_TABLE_CANDIDATES_REQUIRED")
    if any(_has_authority_flag(item) for item in candidates):
        return _blocked("LOGICAL_TABLE_AUTHORITY_FORBIDDEN")
    if not isinstance(column_refs, Sequence) or isinstance(column_refs, (str, bytes)) or not column_refs:
        return _blocked("COLUMN_REFS_REQUIRED")

    nodes = [_candidate_scope_record(item) for item in candidates]
    graph_relationships = _graph_relationships(logical_relationship_graph)
    scopes: list[Service1ColumnSemanticScopeV1] = []
    for raw in column_refs:
        if not isinstance(raw, Mapping):
            return _blocked("COLUMN_REF_INVALID")
        column_ref = str(raw.get("field_id") or raw.get("column_ref") or "").strip()
        sheet = str(raw.get("sheet_name") or raw.get("sheet_ref") or "").strip()
        header = _normalize_header(
            raw.get("normalized_column_name") or raw.get("column_name") or raw.get("normalized_header")
        )
        if not column_ref or not sheet or not header:
            return _blocked("COLUMN_REF_INCOMPLETE")
        matches = [
            node for node in nodes
            if sheet in node["sheet_refs"] and header in node["columns"]
        ]
        if len(matches) != 1:
            scopes.append(
                Service1ColumnSemanticScopeV1(
                    column_ref=column_ref,
                    sheet_ref=sheet,
                    normalized_header=header,
                    logical_table_ref=None,
                    region_refs=(),
                    grain_state=GRAIN_UNRESOLVED,
                    grain_ref=None,
                    relationship_context_refs=(),
                    scope_state=SCOPE_UNRESOLVED,
                    unresolved_reason=(
                        "LOGICAL_TABLE_ENDPOINT_AMBIGUOUS" if len(matches) > 1
                        else "LOGICAL_TABLE_ENDPOINT_NOT_FOUND"
                    ),
                    provenance={"candidate_match_count": len(matches)},
                )
            )
            continue

        node = matches[0]
        candidate = node["candidate"]
        grain_state = str(candidate.get("grain_state") or GRAIN_UNRESOLVED).strip().upper()
        if grain_state not in {GRAIN_RESOLVED, GRAIN_UNRESOLVED}:
            grain_state = GRAIN_UNRESOLVED
        grain_ref = _grain_ref(candidate) if grain_state == GRAIN_RESOLVED else None
        relationship_refs = tuple(
            str(item.get("relationship_ref") or "").strip()
            for item in graph_relationships
            if str(item.get("relationship_ref") or "").strip()
            and node["logical_table_ref"] in {
                str(item.get("left_logical_table_ref") or "").strip(),
                str(item.get("right_logical_table_ref") or "").strip(),
            }
        )
        scopes.append(
            Service1ColumnSemanticScopeV1(
                column_ref=column_ref,
                sheet_ref=sheet,
                normalized_header=header,
                logical_table_ref=node["logical_table_ref"],
                region_refs=node["region_refs"],
                grain_state=grain_state,
                grain_ref=grain_ref,
                relationship_context_refs=relationship_refs,
                scope_state=SCOPE_RESOLVED,
                unresolved_reason=None,
                provenance={
                    "structural_signature": node["structural_signature"],
                    "evidence_only": True,
                },
            )
        )

    status = STATUS_READY if all(item.scope_state == SCOPE_RESOLVED for item in scopes) else STATUS_PARTIAL
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocked_reason": None,
        "column_scopes": [item.to_dict() for item in scopes],
        "resolved_count": sum(item.scope_state == SCOPE_RESOLVED for item in scopes),
        "unresolved_count": sum(item.scope_state == SCOPE_UNRESOLVED for item in scopes),
        "runtime_authorized": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
        "semantic_rebind_authorized": False,
    }


def enrich_service_1_deterministic_hypotheses_with_table_scope_v1(
    *,
    deterministic_hypotheses: Sequence[Mapping[str, Any]],
    column_refs: Sequence[Mapping[str, Any]],
    semantic_scope_packet: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    """Add D5 scope evidence to existing hypotheses without changing their meaning."""
    scopes = {
        str(item.get("column_ref") or "").strip(): dict(item)
        for item in semantic_scope_packet.get("column_scopes") or ()
        if isinstance(item, Mapping) and str(item.get("column_ref") or "").strip()
    }
    refs_by_identity: dict[tuple[str, str], list[str]] = {}
    for raw in column_refs:
        if not isinstance(raw, Mapping):
            continue
        field_id = str(raw.get("field_id") or "").strip()
        sheet = str(raw.get("sheet_name") or "").strip()
        header = _normalize_header(raw.get("normalized_column_name") or raw.get("column_name"))
        if field_id and sheet and header:
            refs_by_identity.setdefault((sheet, header), []).append(field_id)

    enriched: list[dict[str, Any]] = []
    for raw in deterministic_hypotheses:
        item = dict(raw)
        sheet = str(item.get("sheet_name") or "").strip()
        header = _normalize_header(item.get("normalized_header") or item.get("column_name"))
        matches = refs_by_identity.get((sheet, header), [])
        scope = scopes.get(matches[0]) if len(matches) == 1 else None
        if scope is None:
            item.update(
                {
                    "column_ref": matches[0] if len(matches) == 1 else None,
                    "logical_table_ref": None,
                    "region_refs": [],
                    "grain_state": GRAIN_UNRESOLVED,
                    "grain_ref": None,
                    "relationship_context_refs": [],
                    "semantic_scope_state": SCOPE_UNRESOLVED,
                    "semantic_scope_reason": (
                        "COLUMN_IDENTITY_AMBIGUOUS" if len(matches) > 1 else "COLUMN_IDENTITY_NOT_FOUND"
                    ),
                }
            )
        else:
            item.update(
                {
                    "column_ref": scope.get("column_ref"),
                    "logical_table_ref": scope.get("logical_table_ref"),
                    "region_refs": list(scope.get("region_refs") or ()),
                    "grain_state": scope.get("grain_state") or GRAIN_UNRESOLVED,
                    "grain_ref": scope.get("grain_ref"),
                    "relationship_context_refs": list(scope.get("relationship_context_refs") or ()),
                    "semantic_scope_state": scope.get("scope_state") or SCOPE_UNRESOLVED,
                    "semantic_scope_reason": scope.get("unresolved_reason"),
                }
            )
        enriched.append(item)
    return tuple(enriched)


def _candidate_records(value: Sequence[Mapping[str, Any]] | Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        value = value.get("candidates") or ()
    if isinstance(value, (str, bytes)):
        return []
    try:
        return [item for item in value if isinstance(item, Mapping)]
    except TypeError:
        return []


def _candidate_scope_record(candidate: Mapping[str, Any]) -> dict[str, Any]:
    instance_ref = str(candidate.get("logical_table_id") or candidate.get("candidate_id") or candidate.get("table_key") or "").strip()
    signature = str(candidate.get("structural_signature") or "").strip()
    explicit = str(candidate.get("matching_identity") or candidate.get("stable_table_ref") or candidate.get("table_match_key") or "").strip()
    if explicit:
        logical_table_ref = explicit
    elif instance_ref and not _D2_INSTANCE_REF_RE.fullmatch(instance_ref):
        logical_table_ref = instance_ref
    elif signature:
        logical_table_ref = f"logical:{signature}"
    else:
        logical_table_ref = ""
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), Mapping) else {}
    structural = provenance.get("structural_payload") if isinstance(provenance.get("structural_payload"), Mapping) else {}
    columns = tuple(
        _normalize_header(item.get("normalized_header") or item.get("header") or item.get("column_name"))
        for item in (structural.get("columns") or candidate.get("columns") or ())
        if isinstance(item, Mapping)
        and _normalize_header(item.get("normalized_header") or item.get("header") or item.get("column_name"))
    )
    sheets = tuple(dict.fromkeys(
        str(item).strip()
        for item in (candidate.get("source_sheet_refs") or (provenance.get("sheet_ref"),))
        if str(item or "").strip()
    ))
    regions = tuple(dict.fromkeys(
        str(item).strip()
        for item in (candidate.get("source_region_refs") or (provenance.get("region_ref"),))
        if str(item or "").strip()
    ))
    return {
        "logical_table_ref": logical_table_ref,
        "structural_signature": signature,
        "sheet_refs": sheets,
        "region_refs": regions,
        "columns": columns,
        "candidate": candidate,
    }


def _grain_ref(candidate: Mapping[str, Any]) -> str | None:
    grain = candidate.get("grain_candidate")
    if not isinstance(grain, Mapping):
        return None
    payload = {
        "kind": str(grain.get("kind") or grain.get("grain_kind") or "").strip(),
        "key_refs": sorted(str(item).split(".")[-1].strip().casefold() for item in (grain.get("key_refs") or grain.get("candidate_key_refs") or ()) if str(item).strip()),
    }
    if not payload["kind"] and not payload["key_refs"]:
        return None
    return build_service_1_structural_digest_v1(payload=payload, prefix="grain_")


def _graph_relationships(graph: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if not isinstance(graph, Mapping):
        return []
    value = graph.get("relationships") or ()
    return [item for item in value if isinstance(item, Mapping)]


def _has_authority_flag(value: Mapping[str, Any]) -> bool:
    return any(bool(value.get(flag)) for flag in _AUTHORITY_FLAGS)


def service_1_table_scoped_semantic_group_key_v1(
    decision: Mapping[str, Any],
) -> str | None:
    """Return the D5 grouped-confirmation boundary.

    Grouping never crosses logical tables.  A resolved grain remains part of
    the key.  If the source grain is still unresolved, concepts from the same
    logical table may be presented together without resolving or confirming
    that grain; the unresolved state remains explicit downstream.
    """
    tables = _ordered_unique_text(decision.get("logical_table_refs") or ())
    grains = _ordered_unique_text(decision.get("grain_refs") or ())
    grain_states = _ordered_unique_text(decision.get("grain_states") or ())
    if len(tables) != 1 or str(decision.get("scope_conflict_reason") or "").strip():
        return None
    if grain_states == (GRAIN_RESOLVED,) and len(grains) == 1:
        return f"logical-table:{tables[0]}|grain:{grains[0]}"
    if grain_states == (GRAIN_UNRESOLVED,) and not grains:
        return f"logical-table:{tables[0]}|grain:{GRAIN_UNRESOLVED}"
    return None


def service_1_has_table_scoped_semantic_evidence_v1(
    decision: Mapping[str, Any],
) -> bool:
    """Identify decisions already governed by D5 table/grain evidence."""
    return bool(
        decision.get("logical_table_refs")
        or decision.get("region_refs")
        or decision.get("grain_refs")
        or decision.get("grain_states")
        or decision.get("scope_conflict_reason")
    )


def _ordered_unique_text(values: Any) -> tuple[str, ...]:
    result: list[str] = []
    for raw in values or ():
        value = str(raw or "").strip()
        if value and value not in result:
            result.append(value)
    return tuple(result)


def _normalize_header(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "column_scopes": [],
        "resolved_count": 0,
        "unresolved_count": 0,
        "runtime_authorized": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
        "semantic_rebind_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_PARTIAL",
    "STATUS_BLOCKED",
    "SCOPE_RESOLVED",
    "SCOPE_UNRESOLVED",
    "GRAIN_RESOLVED",
    "GRAIN_UNRESOLVED",
    "Service1ColumnSemanticScopeV1",
    "build_service_1_table_scoped_semantic_context_v1",
    "enrich_service_1_deterministic_hypotheses_with_table_scope_v1",
    "service_1_table_scoped_semantic_group_key_v1",
    "service_1_has_table_scoped_semantic_evidence_v1",
]
