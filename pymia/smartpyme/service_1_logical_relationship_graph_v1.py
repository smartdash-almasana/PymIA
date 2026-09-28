"""D4 evidence-only logical relationship graph and fanout certificate.

The graph is a preflight representation over D2 logical-table candidates and
existing profiler/owner evidence.  It never executes joins, grants join
authority, or decides P8 computability.  F7 remains the only join
materialization authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import re
from typing import Any, Final, Mapping, Sequence

from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_confirmed_relationship_bindings_v1,
)
from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)
from pymia.smartpyme.service_1_workbook_schema_identity_v1 import (
    WorkbookSchemaIdentityV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_LOGICAL_RELATIONSHIP_GRAPH_V1"
STATUS_READY: Final[str] = "LOGICAL_RELATIONSHIP_GRAPH_READY"
STATUS_UNRESOLVED: Final[str] = "UNRESOLVED"
STATUS_BLOCKED: Final[str] = "BLOCKED"

STATE_RESOLVED: Final[str] = "RESOLVED"
STATE_UNRESOLVED: Final[str] = "UNRESOLVED"

CARDINALITY_ONE_TO_ONE: Final[str] = "ONE_TO_ONE"
CARDINALITY_MANY_TO_ONE: Final[str] = "MANY_TO_ONE"
CARDINALITY_ONE_TO_MANY: Final[str] = "ONE_TO_MANY"
CARDINALITY_MANY_TO_MANY: Final[str] = "MANY_TO_MANY"
CARDINALITY_UNRESOLVED: Final[str] = "UNRESOLVED"

FANOUT_SAFE_LOOKUP: Final[str] = "SAFE_LOOKUP"
FANOUT_RISK: Final[str] = "FANOUT_RISK"
FANOUT_UNRESOLVED: Final[str] = "UNRESOLVED"
PATH_CONNECTED: Final[str] = "PATH_CONNECTED"
PATH_NO_PATH: Final[str] = "NO_PATH"

TABLE_MATCH_REF_RE: Final[re.Pattern[str]] = re.compile(r"^lt_.+_r[0-9]+$")
_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "join_execution_authorized",
    "computability_authorized",
)
_SAFE_CARDINALITIES: Final[frozenset[str]] = frozenset(
    {CARDINALITY_ONE_TO_ONE, CARDINALITY_MANY_TO_ONE}
)
_KNOWN_CARDINALITIES: Final[frozenset[str]] = frozenset(
    {
        CARDINALITY_ONE_TO_ONE,
        CARDINALITY_MANY_TO_ONE,
        CARDINALITY_ONE_TO_MANY,
        CARDINALITY_MANY_TO_MANY,
    }
)


@dataclass(frozen=True)
class Service1LogicalRelationshipV1:
    relationship_ref: str
    left_logical_table_ref: str
    right_logical_table_ref: str
    left_key_refs: tuple[str, ...]
    right_key_refs: tuple[str, ...]
    cardinality: str
    evidence_refs: tuple[str, ...] = ()
    owner_confirmation_ref: str | None = None
    state: str = STATE_UNRESOLVED
    fanout_risk: str = FANOUT_UNRESOLVED
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    join_execution_authorized: bool = False
    computability_authorized: bool = False

    def __post_init__(self) -> None:
        for name in (
            "relationship_ref",
            "left_logical_table_ref",
            "right_logical_table_ref",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} must be non-empty")
        if self.left_logical_table_ref == self.right_logical_table_ref:
            raise ValueError("relationship endpoints must be different logical tables")
        if self.cardinality not in _KNOWN_CARDINALITIES | {CARDINALITY_UNRESOLVED}:
            raise ValueError("unsupported relationship cardinality")
        if self.state not in {STATE_RESOLVED, STATE_UNRESOLVED}:
            raise ValueError("unsupported relationship state")
        if self.fanout_risk not in {FANOUT_SAFE_LOOKUP, FANOUT_RISK, FANOUT_UNRESOLVED}:
            raise ValueError("unsupported fanout risk state")
        object.__setattr__(self, "left_key_refs", tuple(str(item) for item in self.left_key_refs))
        object.__setattr__(self, "right_key_refs", tuple(str(item) for item in self.right_key_refs))
        object.__setattr__(self, "evidence_refs", tuple(dict.fromkeys(str(item) for item in self.evidence_refs)))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in _AUTHORITY_FLAGS:
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class Service1FanoutCertificateV1:
    certificate_ref: str
    state: str
    fanout_risk: str
    path_state: str
    safe_paths: tuple[dict[str, Any], ...] = ()
    risk_paths: tuple[dict[str, Any], ...] = ()
    disconnected_components: tuple[tuple[str, ...], ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    join_execution_authorized: bool = False
    computability_authorized: bool = False

    def __post_init__(self) -> None:
        if not str(self.certificate_ref or "").strip():
            raise ValueError("certificate_ref must be non-empty")
        if self.state not in {STATE_RESOLVED, STATE_UNRESOLVED}:
            raise ValueError("unsupported certificate state")
        if self.fanout_risk not in {FANOUT_SAFE_LOOKUP, FANOUT_RISK, FANOUT_UNRESOLVED}:
            raise ValueError("unsupported certificate fanout risk")
        if self.path_state not in {PATH_CONNECTED, PATH_NO_PATH}:
            raise ValueError("unsupported certificate path state")
        object.__setattr__(self, "safe_paths", tuple(dict(item) for item in self.safe_paths))
        object.__setattr__(self, "risk_paths", tuple(dict(item) for item in self.risk_paths))
        object.__setattr__(self, "disconnected_components", tuple(tuple(str(value) for value in component) for component in self.disconnected_components))
        object.__setattr__(self, "evidence_refs", tuple(dict.fromkeys(str(item) for item in self.evidence_refs)))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in _AUTHORITY_FLAGS:
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class Service1LogicalRelationshipGraphV1:
    graph_ref: str
    graph_fingerprint: str
    logical_table_refs: tuple[str, ...]
    relationships: tuple[dict[str, Any], ...]
    fanout_certificate: dict[str, Any]
    state: str
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    product_ready: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    join_execution_authorized: bool = False
    computability_authorized: bool = False

    def __post_init__(self) -> None:
        if not str(self.graph_ref or "").strip() or not str(self.graph_fingerprint or "").strip():
            raise ValueError("graph identity must be non-empty")
        if self.state not in {STATE_RESOLVED, STATE_UNRESOLVED}:
            raise ValueError("unsupported graph state")
        object.__setattr__(self, "logical_table_refs", tuple(dict.fromkeys(str(item) for item in self.logical_table_refs)))
        object.__setattr__(self, "relationships", tuple(dict(item) for item in self.relationships))
        object.__setattr__(self, "fanout_certificate", dict(self.fanout_certificate or {}))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in _AUTHORITY_FLAGS:
            if getattr(self, name) is not False:
                raise ValueError(f"{name} must remain False")

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def build_service_1_logical_relationship_graph_v1(
    *,
    logical_table_candidates: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
    relationship_evidence: Sequence[Mapping[str, Any]] | Mapping[str, Any] = (),
    relationships: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
    owner_confirmation_events: Sequence[Any] = (),
    owner_confirmations: Sequence[Any] | None = None,
    workbook_profile: Mapping[str, Any] | None = None,
    schema_identity: Mapping[str, Any] | WorkbookSchemaIdentityV1 | None = None,
) -> dict[str, Any]:
    """Build D4 graph evidence without materializing any join."""
    candidates = _candidate_records(logical_table_candidates)
    if not candidates:
        return _unresolved("LOGICAL_TABLE_CANDIDATES_REQUIRED")
    if any(_has_authority_flag(item) for item in candidates):
        return _blocked("LOGICAL_TABLE_AUTHORITY_FORBIDDEN")
    nodes = [_normalize_node(item) for item in candidates]
    if any(node["node_ref"] == "" for node in nodes):
        return _unresolved("LOGICAL_TABLE_NODE_ID_UNRESOLVED")
    duplicate_nodes = _duplicates(node["node_ref"] for node in nodes)
    if duplicate_nodes:
        return _unresolved("LOGICAL_TABLE_NODE_ID_AMBIGUOUS")

    evidence = _relationship_records(relationship_evidence or relationships or (), workbook_profile)
    try:
        owner_bindings = build_service_1_confirmed_relationship_bindings_v1(
            owner_confirmation_events if owner_confirmations is None else owner_confirmations
        )
    except (TypeError, ValueError) as exc:
        return _unresolved(f"OWNER_CONFIRMATION_INVALID:{exc}")

    relationships: list[dict[str, Any]] = []
    for raw in evidence:
        relationships.append(_build_relationship(raw=raw, nodes=nodes, owner_bindings=owner_bindings))
    relationships = _apply_fanout_edge_states(relationships)
    fanout = _build_fanout_certificate(nodes=nodes, relationships=relationships)
    graph_state = STATE_RESOLVED
    if any(item["state"] != STATE_RESOLVED for item in relationships):
        graph_state = STATE_UNRESOLVED
    if len(nodes) > 1 and fanout["path_state"] == PATH_NO_PATH:
        graph_state = STATE_UNRESOLVED

    graph_payload = {
        "nodes": sorted(
            (_node_identity_payload(node) for node in nodes),
            key=_payload_sort_key,
        ),
        "relationships": sorted(
            (_relationship_identity_payload(item) for item in relationships),
            key=_payload_sort_key,
        ),
    }
    graph_fingerprint = build_service_1_structural_digest_v1(
        payload=graph_payload,
        prefix="lrg_",
    )
    schema_fingerprint = _schema_fingerprint(schema_identity)
    workbook_ref = (
        _schema_provenance_value(schema_identity, "workbook_ref")
        or _first_candidate_value(candidates, "workbook_ref")
    )
    source_artifact_ref = _schema_provenance_value(schema_identity, "source_artifact_ref")
    for relation in relationships:
        event_ref = str(relation.get("owner_confirmation_event_ref") or "").strip() or None
        relation["d4_graph_ref"] = graph_fingerprint
        relation["graph_fingerprint"] = graph_fingerprint
        relation["schema_fingerprint"] = schema_fingerprint
        relation["source_artifact_ref"] = source_artifact_ref
        relation["workbook_ref"] = workbook_ref
        relation["relationship_kind"] = relation.get("cardinality")
        relation["fanout_evidence"] = {
            "fanout_risk": relation.get("fanout_risk"),
            "state": relation.get("state"),
            "certificate_ref": str(fanout.get("certificate_ref") or "").strip() or None,
        }
        relation["owner_confirmation_event_ref"] = event_ref
        relation["provenance"].update(
            {
                "d4_graph_ref": graph_fingerprint,
                "graph_fingerprint": graph_fingerprint,
                "schema_fingerprint": schema_fingerprint,
                "source_artifact_ref": source_artifact_ref,
                "workbook_ref": workbook_ref,
                "owner_confirmation_event_ref": event_ref,
            }
        )
    graph = Service1LogicalRelationshipGraphV1(
        graph_ref=graph_fingerprint,
        graph_fingerprint=graph_fingerprint,
        logical_table_refs=tuple(sorted(node["node_ref"] for node in nodes)),
        relationships=tuple(relationships),
        fanout_certificate=fanout,
        state=graph_state,
        provenance={
            "contract": SCHEMA_VERSION,
            "schema_fingerprint": _schema_fingerprint(schema_identity),
            "source_artifact_ref": source_artifact_ref,
            "workbook_ref": workbook_ref,
            "graph_ref": graph_fingerprint,
            "evidence_only": True,
            "join_execution_authorized": False,
            "computability_authorized": False,
            "identity_exclusions": [
                "filename", "local_path", "region_index", "processing_order", "rubro", "business_values",
            ],
        },
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY if graph_state == STATE_RESOLVED else STATUS_UNRESOLVED,
        "blocked_reason": None,
        "graph_ref": graph.graph_ref,
        "graph_fingerprint": graph.graph_fingerprint,
        "source_artifact_ref": source_artifact_ref,
        "workbook_ref": workbook_ref,
        "schema_fingerprint": schema_fingerprint,
        "nodes": list(graph.logical_table_refs),
        "logical_table_refs": list(graph.logical_table_refs),
        "relationships": list(graph.relationships),
        "fanout_certificate": graph.fanout_certificate,
        "state": graph.state,
        "provenance": graph.provenance,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
        "graph": graph.to_dict(),
    }


def _candidate_records(value: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        if value.get("status") in {STATUS_UNRESOLVED, STATUS_BLOCKED}:
            return []
        value = value.get("candidates")
    if value is None or isinstance(value, (str, bytes)):
        return []
    try:
        return [item for item in value if isinstance(item, Mapping)]
    except TypeError:
        return []


def _normalize_node(candidate: Mapping[str, Any]) -> dict[str, Any]:
    instance_ref = str(candidate.get("logical_table_id") or candidate.get("candidate_id") or candidate.get("table_key") or "").strip()
    structural_signature = str(candidate.get("structural_signature") or "").strip()
    explicit = str(candidate.get("matching_identity") or candidate.get("stable_table_ref") or candidate.get("table_match_key") or "").strip()
    if explicit:
        node_ref = explicit
    elif instance_ref and not TABLE_MATCH_REF_RE.fullmatch(instance_ref):
        node_ref = instance_ref
    elif structural_signature:
        node_ref = f"logical:{structural_signature}"
    else:
        node_ref = ""
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), Mapping) else {}
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
    structural = provenance.get("structural_payload") if isinstance(provenance.get("structural_payload"), Mapping) else {}
    raw_columns = structural.get("columns") if isinstance(structural.get("columns"), Sequence) and not isinstance(structural.get("columns"), (str, bytes)) else candidate.get("columns") or ()
    columns = tuple(
        _normalize_header(item.get("normalized_header") or item.get("header") or item.get("column_name"))
        for item in raw_columns
        if isinstance(item, Mapping) and _normalize_header(item.get("normalized_header") or item.get("header") or item.get("column_name"))
    )
    return {
        "node_ref": node_ref,
        "instance_ref": instance_ref,
        "structural_signature": structural_signature,
        "sheet_refs": sheets,
        "region_refs": regions,
        "columns": tuple(dict.fromkeys(columns)),
        "candidate": candidate,
    }


def _relationship_records(
    value: Sequence[Mapping[str, Any]] | Mapping[str, Any],
    workbook_profile: Mapping[str, Any] | None,
) -> list[Mapping[str, Any]]:
    if not value and isinstance(workbook_profile, Mapping):
        value = workbook_profile.get("relationships") or workbook_profile.get("relationship_evidence") or ()
    if isinstance(value, Mapping):
        value = value.get("relationships") or value.get("relationship_evidence") or ()
    if isinstance(value, (str, bytes)):
        return []
    try:
        return [item for item in value if isinstance(item, Mapping)]
    except TypeError:
        return []


def _build_relationship(
    *,
    raw: Mapping[str, Any],
    nodes: Sequence[Mapping[str, Any]],
    owner_bindings: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    left_endpoint = str(raw.get("left_column_ref") or raw.get("left_key_ref") or "").strip()
    right_endpoint = str(raw.get("right_column_ref") or raw.get("right_key_ref") or "").strip()
    relationship_ref = str(raw.get("relationship_ref") or f"{left_endpoint}->{right_endpoint}").strip()
    left_matches = _resolve_endpoint(left_endpoint, nodes)
    right_matches = _resolve_endpoint(right_endpoint, nodes)
    evidence_refs = tuple(str(item) for item in (raw.get("evidence_refs") or (f"ev:relationship:{relationship_ref}",)))
    owner = _find_owner_binding(raw, owner_bindings)
    cardinality = _normalize_cardinality(raw.get("cardinality") or raw.get("relationship_kind"))
    left_node = left_matches[0] if len(left_matches) == 1 else None
    right_node = right_matches[0] if len(right_matches) == 1 else None
    endpoint_error: str | None = None
    if len(left_matches) != 1:
        endpoint_error = "LEFT_ENDPOINT_AMBIGUOUS" if left_matches else "LEFT_ENDPOINT_UNRESOLVED"
    elif len(right_matches) != 1:
        endpoint_error = "RIGHT_ENDPOINT_AMBIGUOUS" if right_matches else "RIGHT_ENDPOINT_UNRESOLVED"
    elif left_node["node_ref"] == right_node["node_ref"]:
        endpoint_error = "RELATIONSHIP_ENDPOINTS_SAME_TABLE"
    if cardinality == CARDINALITY_UNRESOLVED:
        endpoint_error = endpoint_error or "CARDINALITY_UNRESOLVED"
    if not _cardinality_evidence_sufficient(raw, cardinality):
        endpoint_error = endpoint_error or "CARDINALITY_EVIDENCE_INSUFFICIENT"
    if owner is not None and _normalize_cardinality(owner.get("relationship_kind")) != cardinality:
        endpoint_error = "OWNER_CONTRADICTS_PHYSICAL_EVIDENCE"
    state = STATE_RESOLVED if endpoint_error is None else STATE_UNRESOLVED
    left_ref = left_node["node_ref"] if left_node else "unresolved:left"
    right_ref = right_node["node_ref"] if right_node else "unresolved:right"
    left_column = _endpoint_column(left_endpoint)
    right_column = _endpoint_column(right_endpoint)
    left_sheet, _ = _endpoint_sheet_column(left_endpoint)
    right_sheet, _ = _endpoint_sheet_column(right_endpoint)
    return {
        "relationship_ref": relationship_ref,
        "left_logical_table_ref": left_ref,
        "right_logical_table_ref": right_ref,
        "left_key_refs": [f"{left_ref}.{left_column}"] if left_column else [],
        "right_key_refs": [f"{right_ref}.{right_column}"] if right_column else [],
        "left_sheet_ref": left_sheet,
        "left_column_ref": left_column,
        "right_sheet_ref": right_sheet,
        "right_column_ref": right_column,
        "cardinality": cardinality,
        "relationship_kind": cardinality,
        "evidence_refs": list(dict.fromkeys(evidence_refs)),
        "owner_confirmation_ref": str(owner.get("relationship_ref")) if owner is not None else None,
        "owner_confirmation_event_ref": (
            str(owner.get("owner_confirmation_event_ref") or "").strip() or None
            if owner is not None
            else None
        ),
        "state": state,
        "fanout_risk": FANOUT_UNRESOLVED if state != STATE_RESOLVED else (
            FANOUT_RISK if cardinality == CARDINALITY_MANY_TO_MANY else FANOUT_SAFE_LOOKUP
        ),
        "provenance": {
            "source": "WORKBOOK_PROFILER_AND_OWNER_RELATIONSHIP_EVIDENCE",
            "physical_left_endpoint": left_endpoint,
            "physical_right_endpoint": right_endpoint,
            "blocked_reason": endpoint_error,
            "owner_confirmation_is_evidence_only": owner is not None,
            "owner_confirmation_event_ref": (
                str(owner.get("owner_confirmation_event_ref") or "").strip() or None
                if owner is not None
                else None
            ),
            "join_execution_authorized": False,
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
    }


def _resolve_endpoint(endpoint: str, nodes: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    sheet, column = _endpoint_sheet_column(endpoint)
    if not sheet or not column:
        return []
    return [
        node
        for node in nodes
        if sheet in node["sheet_refs"] and column in node["columns"]
    ]


def _endpoint_sheet_column(endpoint: str) -> tuple[str, str]:
    text = str(endpoint or "").strip()
    if "." not in text:
        return "", _normalize_header(text)
    sheet, column = text.rsplit(".", 1)
    return sheet.strip(), _normalize_header(column)


def _endpoint_column(endpoint: str) -> str:
    return _endpoint_sheet_column(endpoint)[1]


def _normalize_cardinality(value: Any) -> str:
    normalized = str(value or "").strip().upper()
    return normalized if normalized in _KNOWN_CARDINALITIES else CARDINALITY_UNRESOLVED


def _cardinality_evidence_sufficient(raw: Mapping[str, Any], cardinality: str) -> bool:
    if cardinality == CARDINALITY_UNRESOLVED:
        return False
    has_evidence = bool(raw.get("evidence_refs")) or raw.get("intersection_cardinality") is not None
    has_evidence = has_evidence or raw.get("left_value_coverage") is not None or raw.get("right_value_coverage") is not None
    has_evidence = has_evidence or raw.get("candidate_foreign_key") is not None or raw.get("candidate_primary_key_ref") is not None
    if not has_evidence:
        return False
    if cardinality == CARDINALITY_MANY_TO_ONE and raw.get("candidate_foreign_key") is False:
        return False
    return True


def _find_owner_binding(raw: Mapping[str, Any], bindings: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any] | None:
    if not bindings:
        return None
    relationship_ref = str(raw.get("relationship_ref") or "").strip()
    if relationship_ref in bindings:
        return bindings[relationship_ref]
    left = str(raw.get("left_column_ref") or "").strip()
    right = str(raw.get("right_column_ref") or "").strip()
    for binding in bindings.values():
        candidate_left = f"{binding.get('left_sheet_ref')}.{binding.get('left_column_ref')}"
        candidate_right = f"{binding.get('right_sheet_ref')}.{binding.get('right_column_ref')}"
        if (candidate_left, candidate_right) in {(left, right), (right, left)}:
            return binding
    return None


def _apply_fanout_edge_states(relationships: list[dict[str, Any]]) -> list[dict[str, Any]]:
    incoming_many: dict[str, list[int]] = {}
    outgoing_many: dict[str, list[int]] = {}
    for index, relation in enumerate(relationships):
        if relation["state"] != STATE_RESOLVED:
            continue
        kind = relation["cardinality"]
        if kind == CARDINALITY_MANY_TO_ONE:
            incoming_many.setdefault(relation["right_logical_table_ref"], []).append(index)
        elif kind == CARDINALITY_ONE_TO_MANY:
            outgoing_many.setdefault(relation["left_logical_table_ref"], []).append(index)
        elif kind == CARDINALITY_MANY_TO_MANY:
            relation["fanout_risk"] = FANOUT_RISK
    risky_indices = {
        index
        for values in list(incoming_many.values()) + list(outgoing_many.values())
        if len(values) > 1
        for index in values
    }
    for index in risky_indices:
        relationships[index]["fanout_risk"] = FANOUT_RISK
    return relationships


def _build_fanout_certificate(*, nodes: Sequence[Mapping[str, Any]], relationships: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    resolved = [item for item in relationships if item.get("state") == STATE_RESOLVED]
    unresolved = [item for item in relationships if item.get("state") != STATE_RESOLVED]
    adjacency: dict[str, set[str]] = {node["node_ref"]: set() for node in nodes}
    for relation in resolved:
        left = relation["left_logical_table_ref"]
        right = relation["right_logical_table_ref"]
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    components = _components(adjacency)
    disconnected = tuple(component for component in components if len(components) > 1)
    risk_paths: list[dict[str, Any]] = []
    safe_paths: list[dict[str, Any]] = []
    for relation in relationships:
        path = f"{relation['left_logical_table_ref']}->{relation['right_logical_table_ref']}"
        record = {"path": path, "relationship_ref": relation["relationship_ref"]}
        if relation.get("state") != STATE_RESOLVED or relation.get("fanout_risk") == FANOUT_UNRESOLVED:
            risk_paths.append({**record, "reason": "RELATIONSHIP_UNRESOLVED"})
        elif relation.get("fanout_risk") == FANOUT_RISK:
            risk_paths.append({**record, "reason": "EDGE_OR_STAR_FANOUT"})
        else:
            safe_paths.append(record)
    if unresolved:
        state, risk, path_state = STATE_UNRESOLVED, FANOUT_UNRESOLVED, PATH_NO_PATH
    elif disconnected:
        state, risk, path_state = STATE_UNRESOLVED, FANOUT_UNRESOLVED, PATH_NO_PATH
    elif risk_paths:
        state, risk, path_state = STATE_RESOLVED, FANOUT_RISK, PATH_CONNECTED
    elif safe_paths:
        state, risk, path_state = STATE_RESOLVED, FANOUT_SAFE_LOOKUP, PATH_CONNECTED
    else:
        state, risk, path_state = STATE_UNRESOLVED, FANOUT_UNRESOLVED, PATH_NO_PATH
    certificate_payload = {
        "nodes": sorted(node["node_ref"] for node in nodes),
        "safe_paths": safe_paths,
        "risk_paths": risk_paths,
        "components": [list(component) for component in components],
        "state": state,
        "fanout_risk": risk,
    }
    certificate_ref = build_service_1_structural_digest_v1(payload=certificate_payload, prefix="fct_")
    certificate = Service1FanoutCertificateV1(
        certificate_ref=certificate_ref,
        state=state,
        fanout_risk=risk,
        path_state=path_state,
        safe_paths=tuple(safe_paths),
        risk_paths=tuple(risk_paths),
        disconnected_components=disconnected,
        evidence_refs=tuple(item["relationship_ref"] for item in relationships),
        provenance={"source": SCHEMA_VERSION, "join_execution_authorized": False},
    )
    return certificate.to_dict()


def _components(adjacency: Mapping[str, set[str]]) -> tuple[tuple[str, ...], ...]:
    remaining = set(adjacency)
    components: list[tuple[str, ...]] = []
    while remaining:
        start = min(remaining)
        pending = [start]
        component: set[str] = set()
        while pending:
            node = pending.pop()
            if node in component:
                continue
            component.add(node)
            pending.extend(sorted(adjacency.get(node, set()) - component))
        remaining -= component
        components.append(tuple(sorted(component)))
    return tuple(sorted(components))


def _node_identity_payload(node: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "node_ref": node["node_ref"],
        "structural_signature": node.get("structural_signature") or None,
        "columns": sorted(node.get("columns") or ()),
    }


def _relationship_identity_payload(relation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "left": relation.get("left_logical_table_ref"),
        "right": relation.get("right_logical_table_ref"),
        "left_keys": sorted(relation.get("left_key_refs") or ()),
        "right_keys": sorted(relation.get("right_key_refs") or ()),
        "cardinality": relation.get("cardinality"),
        "state": relation.get("state"),
    }


def _schema_fingerprint(value: Mapping[str, Any] | WorkbookSchemaIdentityV1 | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, WorkbookSchemaIdentityV1):
        return value.schema_fingerprint
    return str(value.get("schema_fingerprint") or "") or None


def _schema_provenance_value(
    value: Mapping[str, Any] | WorkbookSchemaIdentityV1 | None,
    key: str,
) -> str | None:
    if value is None:
        return None
    provenance = value.provenance if isinstance(value, WorkbookSchemaIdentityV1) else value.get("provenance")
    if not isinstance(provenance, Mapping):
        return None
    return str(provenance.get(key) or "").strip() or None


def _first_candidate_value(candidates: Sequence[Mapping[str, Any]], key: str) -> str | None:
    values = {
        str(item.get(key) or "").strip()
        for item in candidates
        if str(item.get(key) or "").strip()
    }
    return next(iter(values)) if len(values) == 1 else None


def _normalize_header(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _duplicates(values: Sequence[str] | Any) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _has_authority_flag(value: Mapping[str, Any]) -> bool:
    return any(bool(value.get(flag)) for flag in _AUTHORITY_FLAGS)


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _payload_sort_key(value: Mapping[str, Any]) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _unresolved(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_UNRESOLVED,
        "blocked_reason": reason,
        "graph_ref": None,
        "graph_fingerprint": None,
        "nodes": [],
        "logical_table_refs": [],
        "relationships": [],
        "fanout_certificate": {
            "state": STATE_UNRESOLVED,
            "fanout_risk": FANOUT_UNRESOLVED,
            "path_state": PATH_NO_PATH,
        },
        "state": STATE_UNRESOLVED,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "join_execution_authorized": False,
        "computability_authorized": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    result = _unresolved(reason)
    result["status"] = STATUS_BLOCKED
    return result


LogicalRelationshipV1 = Service1LogicalRelationshipV1
LogicalRelationshipGraphV1 = Service1LogicalRelationshipGraphV1
FanoutCertificateV1 = Service1FanoutCertificateV1


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_UNRESOLVED",
    "STATUS_BLOCKED",
    "STATE_RESOLVED",
    "STATE_UNRESOLVED",
    "CARDINALITY_ONE_TO_ONE",
    "CARDINALITY_MANY_TO_ONE",
    "CARDINALITY_ONE_TO_MANY",
    "CARDINALITY_MANY_TO_MANY",
    "CARDINALITY_UNRESOLVED",
    "FANOUT_SAFE_LOOKUP",
    "FANOUT_RISK",
    "FANOUT_UNRESOLVED",
    "PATH_CONNECTED",
    "PATH_NO_PATH",
    "Service1LogicalRelationshipV1",
    "Service1LogicalRelationshipGraphV1",
    "Service1FanoutCertificateV1",
    "LogicalRelationshipV1",
    "LogicalRelationshipGraphV1",
    "FanoutCertificateV1",
    "build_service_1_logical_relationship_graph_v1",
]
