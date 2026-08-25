"""Governed evidence preparation for Service 1 AnalysisPlan F7.

F7 materializes only the evidence surface that a later analytical runtime may
consume: selected rows, row lineage, confirmed relationship joins, temporal
bucket labels and group membership. It never aggregates business values,
executes formulas, ranks results or grants runtime/product authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from typing import Any, Final, Mapping

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisFilterV1,
    Service1AnalysisPlanV1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    Service1GovernedAnalysisInputV1,
    Service1GovernedRelationshipBindingV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_EVIDENCE_PREPARATION_V1"
PREPARED_SCHEMA_VERSION: Final[str] = "SERVICE_1_PREPARED_ANALYSIS_EVIDENCE_V1"

STATUS_PREPARED: Final[str] = "PREPARED"
STATUS_NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
STATUS_UNSUPPORTED: Final[str] = "UNSUPPORTED"
STATUS_BLOCKED: Final[str] = "BLOCKED"
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {STATUS_PREPARED, STATUS_NEEDS_EVIDENCE, STATUS_UNSUPPORTED, STATUS_BLOCKED}
)

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "analysis_execution_authorized",
    "join_execution_authorized",
)

_SUPPORTED_FILTER_OPERATORS: Final[frozenset[str]] = frozenset(
    {"EQ", "NE", "IN", "NOT_IN", "GT", "GTE", "LT", "LTE", "BETWEEN"}
)

_DIMENSION_ROLE_CANDIDATES: Final[dict[str, tuple[str, ...]]] = {
    "product": ("product_identifier", "product_name"),
    "branch": ("branch_identifier", "branch_name"),
    "category": ("commercial_category",),
    "employee": ("employee_identifier", "employee_name"),
    "channel": ("sales_channel",),
    "payment_method": ("payment_method",),
    "transaction": ("transaction_identifier",),
    "city": ("city",),
    "time": ("operation_date", "operation_time"),
}

_FIELD_ROLE_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    **_DIMENSION_ROLE_CANDIDATES,
    "sales": ("sales_amount",),
    "dso": ("accounts_receivable_amount",),
    "projected_cash_balance": ("initial_balance",),
}


@dataclass(frozen=True)
class Service1PreparedRowV1:
    row_ref: str
    base_sheet_ref: str
    role_values: Mapping[str, Any]
    role_source_refs: Mapping[str, str]
    source_row_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.row_ref or "").strip() or not str(self.base_sheet_ref or "").strip():
            raise ValueError("row_ref and base_sheet_ref are required")
        if not isinstance(self.role_values, Mapping) or not self.role_values:
            raise ValueError("role_values must be a non-empty mapping")
        if not isinstance(self.role_source_refs, Mapping):
            raise ValueError("role_source_refs must be a mapping")
        if set(self.role_values) != set(self.role_source_refs):
            raise ValueError("role_source_refs must cover exactly role_values")
        if not self.source_row_refs or any(not str(ref).strip() for ref in self.source_row_refs):
            raise ValueError("source_row_refs must be non-empty")
        object.__setattr__(self, "role_values", dict(self.role_values))
        object.__setattr__(self, "role_source_refs", dict(self.role_source_refs))
        object.__setattr__(self, "source_row_refs", tuple(self.source_row_refs))
        object.__setattr__(self, "relationship_refs", tuple(self.relationship_refs))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_ref": self.row_ref,
            "base_sheet_ref": self.base_sheet_ref,
            "role_values": dict(self.role_values),
            "role_source_refs": dict(self.role_source_refs),
            "source_row_refs": list(self.source_row_refs),
            "relationship_refs": list(self.relationship_refs),
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True)
class Service1PreparedGroupV1:
    group_ref: str
    key: Mapping[str, str]
    member_row_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not str(self.group_ref or "").strip():
            raise ValueError("group_ref is required")
        if not isinstance(self.key, Mapping):
            raise ValueError("key must be a mapping")
        if not self.member_row_refs or any(not str(ref).strip() for ref in self.member_row_refs):
            raise ValueError("member_row_refs must be non-empty")
        object.__setattr__(self, "key", dict(self.key))
        object.__setattr__(self, "member_row_refs", tuple(self.member_row_refs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_ref": self.group_ref,
            "key": dict(self.key),
            "member_row_refs": list(self.member_row_refs),
        }


@dataclass(frozen=True)
class Service1PreparedRelationshipV1:
    relationship_ref: str
    relationship_kind: str
    left_sheet_ref: str
    right_sheet_ref: str
    materialized_pairs: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        for name in (
            "relationship_ref",
            "relationship_kind",
            "left_sheet_ref",
            "right_sheet_ref",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if not self.materialized_pairs:
            raise ValueError("materialized_pairs must be non-empty")
        object.__setattr__(self, "materialized_pairs", tuple(self.materialized_pairs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_ref": self.relationship_ref,
            "relationship_kind": self.relationship_kind,
            "left_sheet_ref": self.left_sheet_ref,
            "right_sheet_ref": self.right_sheet_ref,
            "materialized_pairs": [list(pair) for pair in self.materialized_pairs],
            "evidence_join_materialized": True,
            "join_runtime_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1PreparedAnalysisEvidenceV1:
    case_id: str
    analysis_id: str
    analysis_plan: Service1AnalysisPlanV1
    grain: Service1GrainV1
    source_sheet_refs: tuple[str, ...]
    prepared_rows: tuple[Service1PreparedRowV1, ...]
    groups: tuple[Service1PreparedGroupV1, ...]
    materialized_relationships: tuple[Service1PreparedRelationshipV1, ...] = ()
    applied_filters: tuple[Mapping[str, Any], ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = PREPARED_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if not isinstance(self.analysis_plan, Service1AnalysisPlanV1):
            raise TypeError("analysis_plan must be Service1AnalysisPlanV1")
        if self.analysis_plan.analysis_id != self.analysis_id:
            raise ValueError("analysis_id must match analysis_plan")
        if not isinstance(self.grain, Service1GrainV1):
            raise TypeError("grain must be Service1GrainV1")
        if not self.source_sheet_refs or any(not str(ref).strip() for ref in self.source_sheet_refs):
            raise ValueError("source_sheet_refs must be non-empty")
        if not self.prepared_rows:
            raise ValueError("prepared_rows must be non-empty")
        if not self.groups:
            raise ValueError("groups must be non-empty")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("provenance cannot carry authority fields")
        object.__setattr__(self, "source_sheet_refs", tuple(self.source_sheet_refs))
        object.__setattr__(self, "prepared_rows", tuple(self.prepared_rows))
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "materialized_relationships", tuple(self.materialized_relationships))
        object.__setattr__(self, "applied_filters", tuple(dict(item) for item in self.applied_filters))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "analysis_plan": self.analysis_plan.to_dict(),
            "grain": self.grain.to_dict(),
            "source_sheet_refs": list(self.source_sheet_refs),
            "prepared_rows": [row.to_dict() for row in self.prepared_rows],
            "groups": [group.to_dict() for group in self.groups],
            "materialized_relationships": [item.to_dict() for item in self.materialized_relationships],
            "applied_filters": [dict(item) for item in self.applied_filters],
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
            "aggregation_execution_authorized": False,
            "formula_execution_authorized": False,
            "ranking_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1EvidencePreparationDecisionV1:
    case_id: str
    analysis_id: str
    status: str
    reason: str | None
    missing_evidence_refs: tuple[str, ...] = ()
    prepared_evidence: Service1PreparedAnalysisEvidenceV1 | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError("invalid evidence preparation status")
        if self.status == STATUS_PREPARED and self.prepared_evidence is None:
            raise ValueError("PREPARED requires prepared_evidence")
        if self.status != STATUS_PREPARED and self.prepared_evidence is not None:
            raise ValueError("non-prepared decision cannot carry prepared evidence")
        if self.status == STATUS_PREPARED and self.reason is not None:
            raise ValueError("PREPARED cannot carry reason")
        if self.status != STATUS_PREPARED and not str(self.reason or "").strip():
            raise ValueError("non-prepared decision requires reason")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("decision provenance cannot carry authority fields")
        object.__setattr__(self, "missing_evidence_refs", tuple(self.missing_evidence_refs))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "reason": self.reason,
            "missing_evidence_refs": list(self.missing_evidence_refs),
            "prepared_evidence": self.prepared_evidence.to_dict() if self.prepared_evidence else None,
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
            "aggregation_execution_authorized": False,
            "formula_execution_authorized": False,
            "ranking_execution_authorized": False,
        }


@dataclass
class _RowState:
    base_sheet_ref: str
    source_rows: dict[str, Mapping[str, Any]]
    source_row_refs: dict[str, str]
    relationship_refs: list[str]


@dataclass(frozen=True)
class _TableView:
    sheet_ref: str
    rows: tuple[Mapping[str, Any], ...]
    original_to_normalized: Mapping[str, str]
    normalized_headers: tuple[str, ...]
    row_refs: tuple[str, ...]

    def normalized_column(self, column_ref: str) -> str | None:
        raw = str(column_ref or "").strip()
        if raw in self.original_to_normalized:
            return str(self.original_to_normalized[raw])
        if raw in self.normalized_headers:
            return raw
        return None


def build_service_1_analysis_evidence_preparation_v1(
    *,
    case_id: str,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    ingestion_output: Mapping[str, Any],
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
) -> Service1EvidencePreparationDecisionV1:
    """Prepare row-level evidence for later F8 execution without calculating results."""
    case = str(case_id or "").strip()
    if not case:
        raise ValueError("case_id is required")
    if not isinstance(governed_analysis_input, Service1GovernedAnalysisInputV1):
        raise TypeError("governed_analysis_input must be Service1GovernedAnalysisInputV1")
    if governed_analysis_input.case_id != case:
        return _decision(case, governed_analysis_input.analysis_plan.analysis_id, STATUS_BLOCKED, "P8_CASE_MISMATCH")
    plan = governed_analysis_input.analysis_plan
    if not isinstance(ingestion_output, Mapping):
        raise TypeError("ingestion_output must be a mapping")
    if any(bool(ingestion_output.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "INGESTION_AUTHORITY_FORBIDDEN")
    workbook_context = ingestion_output.get("workbook_context")
    if (
        ingestion_output.get("schema_version") == "SERVICE_1_CANONICAL_INGESTION_OUTPUT_V2"
        and not isinstance(workbook_context, Mapping)
    ):
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "WORKBOOK_CONTEXT_REQUIRED")
    ingestion_case = (
        str(workbook_context.get("case_id") or "").strip()
        if isinstance(workbook_context, Mapping)
        else ""
    )
    if ingestion_case and ingestion_case != case:
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "INGESTION_CASE_MISMATCH")

    tables, table_error = _table_views(ingestion_output)
    if table_error is not None:
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, table_error)

    relationships = dict(governed_analysis_input.relationship_bindings)
    relation_error = _validate_relationship_bindings(
        relationships,
        governed_analysis_input=governed_analysis_input,
        ingestion_output=ingestion_output,
        d7_workbook_logical_model=d7_workbook_logical_model,
    )
    if relation_error is not None:
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, relation_error)

    base_sheet, base_error = _select_base_sheet(
        source_bindings=governed_analysis_input.source_bindings,
        relationships=relationships,
        tables=tables,
    )
    if base_error is not None:
        status = STATUS_NEEDS_EVIDENCE if base_error.startswith("SOURCE_COLUMN_NOT_FOUND") else STATUS_BLOCKED
        return _decision(case, plan.analysis_id, status, base_error)
    assert base_sheet is not None

    row_states = [
        _RowState(
            base_sheet_ref=base_sheet,
            source_rows={base_sheet: row},
            source_row_refs={base_sheet: tables[base_sheet].row_refs[index]},
            relationship_refs=[],
        )
        for index, row in enumerate(tables[base_sheet].rows)
    ]
    if not row_states:
        return _decision(case, plan.analysis_id, STATUS_NEEDS_EVIDENCE, "BASE_SHEET_HAS_NO_ROWS")

    prepared_relationships: list[Service1PreparedRelationshipV1] = []
    if relationships:
        materialized, relation_decision = _materialize_relationships(
            row_states=row_states,
            relationships=relationships,
            tables=tables,
        )
        if relation_decision is not None:
            return _decision(
                case,
                plan.analysis_id,
                relation_decision[0],
                relation_decision[1],
                missing=relation_decision[2],
            )
        prepared_relationships.extend(materialized)

    prepared_rows_raw: list[tuple[_RowState, dict[str, Any], dict[str, str]]] = []
    for state in row_states:
        role_values, role_refs, source_error = _project_role_values(
            state=state,
            source_bindings=governed_analysis_input.source_bindings,
            tables=tables,
        )
        if source_error is not None:
            status = STATUS_NEEDS_EVIDENCE if source_error.startswith("SOURCE_VALUE_MISSING") else STATUS_BLOCKED
            return _decision(case, plan.analysis_id, status, source_error)
        prepared_rows_raw.append((state, role_values, role_refs))

    filtered_rows, filter_decision = _apply_filters(
        rows=prepared_rows_raw,
        filters=plan.filters,
        source_roles=set(governed_analysis_input.source_bindings),
    )
    if filter_decision is not None:
        return _decision(case, plan.analysis_id, filter_decision[0], filter_decision[1])
    if not filtered_rows:
        return _decision(case, plan.analysis_id, STATUS_NEEDS_EVIDENCE, "FILTERS_SELECT_NO_ROWS")

    prepared_rows: list[Service1PreparedRowV1] = []
    for state, role_values, role_refs in filtered_rows:
        row_ref = state.source_row_refs[state.base_sheet_ref]
        prepared_rows.append(
            Service1PreparedRowV1(
                row_ref=row_ref,
                base_sheet_ref=state.base_sheet_ref,
                role_values=role_values,
                role_source_refs=role_refs,
                source_row_refs=tuple(state.source_row_refs.values()),
                relationship_refs=tuple(state.relationship_refs),
                provenance={
                    "source": "CANONICAL_NORMALIZED_TABLE_ROWS",
                    "row_membership_only": True,
                },
            )
        )

    groups, group_decision = _build_groups(plan=plan, rows=prepared_rows)
    if group_decision is not None:
        return _decision(case, plan.analysis_id, group_decision[0], group_decision[1])

    source_sheets: list[str] = []
    for row in prepared_rows:
        for qualified_ref in row.role_source_refs.values():
            sheet = qualified_ref.split(".", 1)[0]
            if sheet and sheet not in source_sheets:
                source_sheets.append(sheet)
    for relation in prepared_relationships:
        for sheet in (relation.left_sheet_ref, relation.right_sheet_ref):
            if sheet not in source_sheets:
                source_sheets.append(sheet)

    prepared = Service1PreparedAnalysisEvidenceV1(
        case_id=case,
        analysis_id=plan.analysis_id,
        analysis_plan=plan,
        grain=governed_analysis_input.grain,
        source_sheet_refs=tuple(source_sheets or [base_sheet]),
        prepared_rows=tuple(prepared_rows),
        groups=tuple(groups),
        materialized_relationships=tuple(prepared_relationships),
        applied_filters=tuple(item.to_dict() for item in plan.filters),
        provenance={
            "source": "P8_GOVERNED_ANALYSIS_INPUT_PLUS_CANONICAL_INGESTION",
            "base_sheet_ref": base_sheet,
            "group_membership_prepared": True,
            "relationship_materialization_prepared": bool(prepared_relationships),
            "aggregation_performed": False,
            "formula_execution_performed": False,
            "ranking_performed": False,
            "order_by_deferred": bool(plan.order_by),
            "limit_deferred": plan.limit is not None,
            "d4_graph_ref": governed_analysis_input.provenance.get("d4_graph_ref"),
            "schema_fingerprint": governed_analysis_input.provenance.get("schema_fingerprint"),
            "d4_provenance_validated": bool(relation_error is None and relationships and _d4_context_required(
                governed_analysis_input=governed_analysis_input,
                ingestion_output=ingestion_output,
                d7_workbook_logical_model=d7_workbook_logical_model,
            )),
        },
    )
    return Service1EvidencePreparationDecisionV1(
        case_id=case,
        analysis_id=plan.analysis_id,
        status=STATUS_PREPARED,
        reason=None,
        prepared_evidence=prepared,
        provenance={"source": "F7_GOVERNED_EVIDENCE_PREPARATION"},
    )


def _table_views(ingestion_output: Mapping[str, Any]) -> tuple[dict[str, _TableView], str | None]:
    raw_tables = ingestion_output.get("normalized_tables")
    if not isinstance(raw_tables, list) or not raw_tables:
        return {}, "NORMALIZED_TABLES_MISSING"
    tables: dict[str, _TableView] = {}
    for raw in raw_tables:
        if not isinstance(raw, Mapping) or str(raw.get("status") or "") != "OK":
            return {}, "NORMALIZED_TABLE_INVALID"
        sheet = str(raw.get("sheet_name") or "").strip()
        headers = raw.get("headers")
        normalized = raw.get("normalized_headers")
        rows = raw.get("rows")
        if not sheet or not isinstance(headers, list) or not isinstance(normalized, list) or not isinstance(rows, list):
            return {}, "NORMALIZED_TABLE_INVALID"
        if len(headers) != len(normalized) or not headers or any(not isinstance(row, Mapping) for row in rows):
            return {}, "NORMALIZED_TABLE_INVALID"
        if sheet in tables:
            return {}, "DUPLICATE_NORMALIZED_SHEET"
        mapping = {str(original).strip(): str(norm).strip() for original, norm in zip(headers, normalized)}
        if any(not key or not value for key, value in mapping.items()):
            return {}, "NORMALIZED_HEADER_INVALID"
        source_row_numbers = raw.get("source_row_numbers")
        if source_row_numbers is not None and (
            not isinstance(source_row_numbers, list) or len(source_row_numbers) != len(rows)
        ):
            return {}, "SOURCE_ROW_NUMBERS_INVALID"
        row_refs: list[str] = []
        for index in range(len(rows)):
            if isinstance(source_row_numbers, list):
                marker = str(source_row_numbers[index])
                row_refs.append(f"{sheet}!row:{marker}")
            else:
                row_refs.append(f"{sheet}!index:{index}")
        tables[sheet] = _TableView(
            sheet_ref=sheet,
            rows=tuple(dict(row) for row in rows),
            original_to_normalized=mapping,
            normalized_headers=tuple(str(value).strip() for value in normalized),
            row_refs=tuple(row_refs),
        )
    return tables, None


def _validate_relationship_bindings(
    relationships: Mapping[str, Mapping[str, Any]],
    *,
    governed_analysis_input: Service1GovernedAnalysisInputV1 | None = None,
    ingestion_output: Mapping[str, Any] | None = None,
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
) -> str | None:
    strict = _d4_context_required(
        governed_analysis_input=governed_analysis_input,
        ingestion_output=ingestion_output,
        d7_workbook_logical_model=d7_workbook_logical_model,
    )
    graph = (
        d7_workbook_logical_model.get("relationship_graph")
        if isinstance(d7_workbook_logical_model, Mapping)
        and isinstance(d7_workbook_logical_model.get("relationship_graph"), Mapping)
        else None
    )
    if strict and not isinstance(graph, Mapping):
        return "D4_RELATIONSHIP_PROVENANCE_REQUIRED"
    current_context = (
        ingestion_output.get("workbook_context")
        if isinstance(ingestion_output, Mapping)
        and isinstance(ingestion_output.get("workbook_context"), Mapping)
        else {}
    )
    for ref, binding in relationships.items():
        if not str(ref or "").strip() or not isinstance(binding, Mapping):
            return "RELATIONSHIP_BINDING_INVALID"
        if str(binding.get("relationship_ref") or ref).strip() != str(ref).strip():
            return "RELATIONSHIP_BINDING_REF_MISMATCH"
        if binding.get("confirmed_by_owner") is not True:
            return "RELATIONSHIP_OWNER_CONFIRMATION_REQUIRED"
        if any(bool(binding.get(flag)) for flag in _AUTHORITY_FLAGS):
            return "RELATIONSHIP_AUTHORITY_FORBIDDEN"
        for key in (
            "left_sheet_ref",
            "left_column_ref",
            "right_sheet_ref",
            "right_column_ref",
            "relationship_kind",
        ):
            if not str(binding.get(key) or "").strip():
                return f"RELATIONSHIP_ENDPOINT_EVIDENCE_MISSING:{ref}:{key}"
        if strict:
            provenance_error = _validate_d4_binding(
                ref=str(ref),
                binding=binding,
                graph=graph,
                governed_analysis_input=governed_analysis_input,
                current_context=current_context,
            )
            if provenance_error is not None:
                return provenance_error
    return None


def _d4_context_required(
    *,
    governed_analysis_input: Service1GovernedAnalysisInputV1 | None,
    ingestion_output: Mapping[str, Any] | None,
    d7_workbook_logical_model: Mapping[str, Any] | None,
) -> bool:
    if isinstance(d7_workbook_logical_model, Mapping):
        return True
    provenance = governed_analysis_input.provenance if isinstance(governed_analysis_input, Service1GovernedAnalysisInputV1) else {}
    if isinstance(provenance, Mapping) and provenance.get("p8_relationship_governance") is True:
        return True
    if isinstance(ingestion_output, Mapping) and isinstance(ingestion_output.get("workbook_context"), Mapping):
        return True
    return False


def _validate_d4_binding(
    *,
    ref: str,
    binding: Mapping[str, Any],
    graph: Mapping[str, Any],
    governed_analysis_input: Service1GovernedAnalysisInputV1 | None,
    current_context: Mapping[str, Any],
) -> str | None:
    required = (
        "source_artifact_ref",
        "workbook_ref",
        "schema_fingerprint",
        "d4_graph_ref",
        "owner_confirmation_event_ref",
        "integrity_digest",
    )
    for key in required:
        if not str(binding.get(key) or "").strip():
            return "D4_RELATIONSHIP_PROVENANCE_REQUIRED"
    if binding.get("p8_governed") is not True:
        return "P8_RELATIONSHIP_GOVERNANCE_REQUIRED"
    graph_ref = str(graph.get("graph_ref") or graph.get("graph_fingerprint") or "").strip()
    graph_provenance = graph.get("provenance") if isinstance(graph.get("provenance"), Mapping) else {}
    graph_schema = str(graph.get("schema_fingerprint") or graph_provenance.get("schema_fingerprint") or "").strip()
    if str(binding.get("d4_graph_ref") or "").strip() != graph_ref:
        return "D4_GRAPH_REF_MISMATCH"
    if str(binding.get("schema_fingerprint") or "").strip() != graph_schema:
        return "D4_SCHEMA_FINGERPRINT_MISMATCH"
    expected_schema = str(
        (governed_analysis_input.provenance.get("schema_fingerprint") if isinstance(governed_analysis_input, Service1GovernedAnalysisInputV1) else None)
        or current_context.get("schema_fingerprint")
        or ""
    ).strip()
    if expected_schema and expected_schema != str(binding.get("schema_fingerprint") or "").strip():
        return "D4_SCHEMA_FINGERPRINT_MISMATCH"
    for binding_key, context_key in (("workbook_ref", "workbook_ref"), ("source_artifact_ref", "source_artifact_ref")):
        expected = str(current_context.get(context_key) or "").strip()
        if expected and str(binding.get(binding_key) or "").strip() != expected:
            return "D4_RELATIONSHIP_PROVENANCE_REQUIRED"
    relation = next(
        (
            item
            for item in graph.get("relationships") or ()
            if isinstance(item, Mapping)
            and str(item.get("relationship_ref") or "").strip() == ref
        ),
        None,
    )
    if relation is None:
        return "D4_RELATIONSHIP_REF_NOT_FOUND"
    if str(relation.get("state") or "").strip() != "RESOLVED":
        return "D4_RELATIONSHIP_UNRESOLVED"
    if str(relation.get("d4_graph_ref") or relation.get("graph_ref") or graph_ref).strip() != graph_ref:
        return "D4_GRAPH_REF_MISMATCH"
    if str(relation.get("schema_fingerprint") or graph_schema).strip() != graph_schema:
        return "D4_SCHEMA_FINGERPRINT_MISMATCH"
    fanout = str(relation.get("fanout_risk") or "").strip()
    if fanout != "SAFE_LOOKUP":
        return "D4_FANOUT_NOT_SAFE"
    relation_provenance = relation.get("provenance") if isinstance(relation.get("provenance"), Mapping) else {}
    if (
        str(binding.get("left_sheet_ref") or "").strip(),
        str(binding.get("left_column_ref") or "").strip(),
        str(binding.get("right_sheet_ref") or "").strip(),
        str(binding.get("right_column_ref") or "").strip(),
    ) != _endpoint_pair(relation_provenance):
        return "D4_RELATIONSHIP_ENDPOINT_MISMATCH"
    relation_kind = str(relation.get("cardinality") or relation.get("relationship_kind") or "").strip()
    if str(binding.get("relationship_kind") or "").strip() != relation_kind or str(binding.get("cardinality") or relation_kind).strip() != relation_kind:
        return "D4_RELATIONSHIP_CARDINALITY_MISMATCH"
    relation_event_ref = str(relation.get("owner_confirmation_event_ref") or "").strip()
    if relation_event_ref and relation_event_ref != str(binding.get("owner_confirmation_event_ref") or "").strip():
        return "OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED"
    try:
        Service1GovernedRelationshipBindingV1(**{
            key: binding[key]
            for key in (
                "source_artifact_ref", "workbook_ref", "schema_fingerprint", "d4_graph_ref",
                "relationship_ref", "left_logical_table_ref", "right_logical_table_ref",
                "left_sheet_ref", "left_column_ref", "right_sheet_ref", "right_column_ref",
                "relationship_kind", "cardinality", "fanout_evidence",
                "owner_confirmation_event_ref", "confirmed_by_owner", "integrity_digest", "provenance",
            )
        })
    except (KeyError, TypeError, ValueError):
        return "D4_RELATIONSHIP_PROVENANCE_REQUIRED"
    return None


def _endpoint_pair(provenance: Mapping[str, Any]) -> tuple[str, str, str, str]:
    left = str(provenance.get("physical_left_endpoint") or "").strip()
    right = str(provenance.get("physical_right_endpoint") or "").strip()
    left_sheet, left_column = left.rsplit(".", 1) if "." in left else ("", "")
    right_sheet, right_column = right.rsplit(".", 1) if "." in right else ("", "")
    return left_sheet.strip(), left_column.strip(), right_sheet.strip(), right_column.strip()


def _select_base_sheet(
    *,
    source_bindings: Mapping[str, str],
    relationships: Mapping[str, Mapping[str, Any]],
    tables: Mapping[str, _TableView],
) -> tuple[str | None, str | None]:
    if not source_bindings:
        return None, "SOURCE_BINDINGS_MISSING"
    left_sheets = {
        str(binding.get("left_sheet_ref") or "").strip()
        for binding in relationships.values()
        if str(binding.get("relationship_kind") or "").strip() in {"MANY_TO_ONE", "ONE_TO_ONE"}
    }
    left_sheets.discard("")
    if len(left_sheets) == 1:
        candidate = next(iter(left_sheets))
        if candidate not in tables:
            return None, f"RELATIONSHIP_LEFT_SHEET_NOT_FOUND:{candidate}"
        return candidate, None

    scores: dict[str, int] = {}
    for sheet, table in tables.items():
        score = sum(1 for column in source_bindings.values() if table.normalized_column(str(column)) is not None)
        scores[sheet] = score
    if not scores or max(scores.values()) == 0:
        first = next(iter(source_bindings.values()))
        return None, f"SOURCE_COLUMN_NOT_FOUND:{first}"
    best = max(scores.values())
    candidates = [sheet for sheet, score in scores.items() if score == best]
    if len(candidates) != 1:
        return None, "BASE_SHEET_AMBIGUOUS"
    base = candidates[0]
    missing_on_base = [
        str(column)
        for column in source_bindings.values()
        if tables[base].normalized_column(str(column)) is None
    ]
    if missing_on_base and not relationships:
        return None, "CROSS_SHEET_SOURCE_REQUIRES_RELATIONSHIP"
    return base, None


def _materialize_relationships(
    *,
    row_states: list[_RowState],
    relationships: Mapping[str, Mapping[str, Any]],
    tables: Mapping[str, _TableView],
) -> tuple[list[Service1PreparedRelationshipV1], tuple[str, str, tuple[str, ...]] | None]:
    pending = dict(relationships)
    prepared: list[Service1PreparedRelationshipV1] = []
    while pending:
        progressed = False
        for ref in list(pending):
            binding = pending[ref]
            kind = str(binding.get("relationship_kind") or "").strip()
            if kind not in {"MANY_TO_ONE", "ONE_TO_ONE"}:
                return [], (STATUS_UNSUPPORTED, f"RELATIONSHIP_KIND_NOT_JOIN_SAFE:{kind}", (ref,))
            left_sheet = str(binding.get("left_sheet_ref") or "").strip()
            right_sheet = str(binding.get("right_sheet_ref") or "").strip()
            if left_sheet not in tables or right_sheet not in tables:
                return [], (STATUS_NEEDS_EVIDENCE, f"RELATIONSHIP_SHEET_NOT_FOUND:{ref}", (ref,))
            if not any(left_sheet in state.source_rows for state in row_states):
                continue
            left_column = tables[left_sheet].normalized_column(str(binding.get("left_column_ref") or ""))
            right_column = tables[right_sheet].normalized_column(str(binding.get("right_column_ref") or ""))
            if left_column is None or right_column is None:
                return [], (STATUS_NEEDS_EVIDENCE, f"RELATIONSHIP_COLUMN_NOT_FOUND:{ref}", (ref,))

            index: dict[str, int] = {}
            duplicate_keys: set[str] = set()
            for right_index, row in enumerate(tables[right_sheet].rows):
                key = _join_key(row.get(right_column))
                if key is None:
                    continue
                if key in index:
                    duplicate_keys.add(key)
                else:
                    index[key] = right_index
            if duplicate_keys:
                return [], (STATUS_BLOCKED, f"RELATIONSHIP_CARDINALITY_VIOLATION:{ref}", (ref,))

            if kind == "ONE_TO_ONE":
                seen_left: set[str] = set()
                for state in row_states:
                    if left_sheet not in state.source_rows:
                        continue
                    key = _join_key(state.source_rows[left_sheet].get(left_column))
                    if key is None:
                        continue
                    if key in seen_left:
                        return [], (STATUS_BLOCKED, f"RELATIONSHIP_CARDINALITY_VIOLATION:{ref}", (ref,))
                    seen_left.add(key)

            pairs: list[tuple[str, str]] = []
            for state in row_states:
                if left_sheet not in state.source_rows:
                    continue
                left_key = _join_key(state.source_rows[left_sheet].get(left_column))
                if left_key is None:
                    return [], (STATUS_NEEDS_EVIDENCE, f"RELATIONSHIP_LEFT_KEY_MISSING:{ref}", (ref,))
                right_index = index.get(left_key)
                if right_index is None:
                    return [], (STATUS_NEEDS_EVIDENCE, f"RELATIONSHIP_MATCH_MISSING:{ref}", (ref,))
                right_row = tables[right_sheet].rows[right_index]
                right_row_ref = tables[right_sheet].row_refs[right_index]
                if right_sheet in state.source_rows:
                    existing = state.source_row_refs[right_sheet]
                    if existing != right_row_ref:
                        return [], (STATUS_BLOCKED, f"RELATIONSHIP_JOIN_CONFLICT:{ref}", (ref,))
                else:
                    state.source_rows[right_sheet] = right_row
                    state.source_row_refs[right_sheet] = right_row_ref
                if ref not in state.relationship_refs:
                    state.relationship_refs.append(ref)
                pairs.append((state.source_row_refs[left_sheet], right_row_ref))
            if not pairs:
                return [], (STATUS_NEEDS_EVIDENCE, f"RELATIONSHIP_HAS_NO_MATERIALIZED_ROWS:{ref}", (ref,))
            prepared.append(
                Service1PreparedRelationshipV1(
                    relationship_ref=ref,
                    relationship_kind=kind,
                    left_sheet_ref=left_sheet,
                    right_sheet_ref=right_sheet,
                    materialized_pairs=tuple(pairs),
                )
            )
            del pending[ref]
            progressed = True
        if not progressed:
            return [], (STATUS_BLOCKED, "RELATIONSHIP_TOPOLOGY_NOT_CONNECTABLE", tuple(pending))
    return prepared, None


def _project_role_values(
    *,
    state: _RowState,
    source_bindings: Mapping[str, str],
    tables: Mapping[str, _TableView],
) -> tuple[dict[str, Any], dict[str, str], str | None]:
    values: dict[str, Any] = {}
    refs: dict[str, str] = {}
    for role, raw_column in source_bindings.items():
        column_ref = str(raw_column or "").strip()
        candidates: list[tuple[str, str, Any]] = []
        for sheet, row in state.source_rows.items():
            normalized = tables[sheet].normalized_column(column_ref)
            if normalized is not None:
                candidates.append((sheet, normalized, row.get(normalized)))
        if not candidates:
            return {}, {}, f"SOURCE_VALUE_MISSING:{role}:{column_ref}"
        base_candidates = [item for item in candidates if item[0] == state.base_sheet_ref]
        if base_candidates:
            chosen = base_candidates[0]
        elif len(candidates) == 1:
            chosen = candidates[0]
        else:
            return {}, {}, f"SOURCE_BINDING_AMBIGUOUS:{role}:{column_ref}"
        sheet, normalized, value = chosen
        if value is None or (isinstance(value, str) and not value.strip()):
            return {}, {}, f"SOURCE_VALUE_MISSING:{role}:{sheet}.{column_ref}"
        values[str(role)] = value
        refs[str(role)] = f"{sheet}.{column_ref}"
    return values, refs, None


def _apply_filters(
    *,
    rows: list[tuple[_RowState, dict[str, Any], dict[str, str]]],
    filters: tuple[Service1AnalysisFilterV1, ...],
    source_roles: set[str],
) -> tuple[list[tuple[_RowState, dict[str, Any], dict[str, str]]], tuple[str, str] | None]:
    current = list(rows)
    for item in filters:
        operator = str(item.operator or "").strip().upper()
        if operator not in _SUPPORTED_FILTER_OPERATORS:
            return [], (STATUS_UNSUPPORTED, f"FILTER_OPERATOR_UNSUPPORTED:{item.operator}")
        role = _resolve_field_role(item.field_ref, source_roles)
        if role is None:
            return [], (STATUS_UNSUPPORTED, f"FILTER_FIELD_UNSUPPORTED:{item.field_ref}")
        kept: list[tuple[_RowState, dict[str, Any], dict[str, str]]] = []
        for row in current:
            value = row[1].get(role)
            try:
                matches = _filter_matches(value, operator, item.value)
            except (TypeError, ValueError) as exc:
                return [], (STATUS_BLOCKED, f"FILTER_VALUE_INVALID:{item.field_ref}:{exc}")
            if matches:
                kept.append(row)
        current = kept
    return current, None


def _resolve_field_role(field_ref: str, source_roles: set[str]) -> str | None:
    field = str(field_ref or "").strip()
    if field in source_roles:
        return field
    for candidate in _FIELD_ROLE_ALIASES.get(field, ()):
        if candidate in source_roles:
            return candidate
    return None


def _filter_matches(value: Any, operator: str, expected: Any) -> bool:
    if operator == "EQ":
        return _comparable(value) == _comparable(expected)
    if operator == "NE":
        return _comparable(value) != _comparable(expected)
    if operator in {"IN", "NOT_IN"}:
        if not isinstance(expected, (list, tuple, set, frozenset)):
            raise ValueError("IN requires a collection")
        matches = _comparable(value) in {_comparable(item) for item in expected}
        return matches if operator == "IN" else not matches
    if operator == "BETWEEN":
        if not isinstance(expected, (list, tuple)) or len(expected) != 2:
            raise ValueError("BETWEEN requires exactly two bounds")
        current = _comparable(value)
        lower = _comparable(expected[0])
        upper = _comparable(expected[1])
        return lower <= current <= upper
    current = _comparable(value)
    target = _comparable(expected)
    if operator == "GT":
        return current > target
    if operator == "GTE":
        return current >= target
    if operator == "LT":
        return current < target
    if operator == "LTE":
        return current <= target
    raise ValueError("unsupported operator")


def _comparable(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    text = str(value).strip()
    if not text:
        return ""
    numeric = text.replace(" ", "").replace(",", ".")
    try:
        return Decimal(numeric)
    except InvalidOperation:
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text.casefold()


def _build_groups(
    *,
    plan: Service1AnalysisPlanV1,
    rows: list[Service1PreparedRowV1],
) -> tuple[list[Service1PreparedGroupV1], tuple[str, str] | None]:
    if plan.kind is AnalysisKind.SINGLE_VALUE:
        return [
            Service1PreparedGroupV1(
                group_ref="group:ALL",
                key={},
                member_row_refs=tuple(row.row_ref for row in rows),
            )
        ], None

    source_roles = set(rows[0].role_values)
    dimension_roles: dict[str, str] = {}
    for dimension in plan.dimensions:
        if dimension == "time":
            temporal_role = _time_role(plan, source_roles)
            if temporal_role is None:
                return [], (STATUS_NEEDS_EVIDENCE, "TEMPORAL_SOURCE_ROLE_MISSING")
            dimension_roles[dimension] = temporal_role
            continue
        role = _resolve_field_role(dimension, source_roles)
        if role is None:
            return [], (STATUS_UNSUPPORTED, f"DIMENSION_ROLE_UNSUPPORTED:{dimension}")
        dimension_roles[dimension] = role

    membership: dict[tuple[tuple[str, str], ...], list[str]] = {}
    for row in rows:
        key_items: list[tuple[str, str]] = []
        for dimension in plan.dimensions:
            role = dimension_roles[dimension]
            raw_value = row.role_values.get(role)
            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                return [], (STATUS_NEEDS_EVIDENCE, f"DIMENSION_VALUE_MISSING:{dimension}:{row.row_ref}")
            if dimension == "time":
                bucket, error = _temporal_bucket(raw_value, plan.requested_grain.temporal_grain)
                if error is not None:
                    return [], (STATUS_NEEDS_EVIDENCE, f"TEMPORAL_BUCKET_INVALID:{row.row_ref}:{error}")
                value = bucket
            else:
                value = str(raw_value).strip()
            key_items.append((dimension, value))
        key_tuple = tuple(key_items)
        membership.setdefault(key_tuple, []).append(row.row_ref)

    groups: list[Service1PreparedGroupV1] = []
    for key_tuple, members in membership.items():
        key = dict(key_tuple)
        token = "|".join(f"{name}={value}" for name, value in key_tuple)
        groups.append(
            Service1PreparedGroupV1(
                group_ref=f"group:{token}",
                key=key,
                member_row_refs=tuple(members),
            )
        )
    return groups, None


def _time_role(plan: Service1AnalysisPlanV1, source_roles: set[str]) -> str | None:
    temporal = plan.requested_grain.temporal_grain
    preferred = "operation_time" if temporal == "HOUR" else "operation_date"
    return preferred if preferred in source_roles else None


def _temporal_bucket(value: Any, temporal_grain: str) -> tuple[str, str | None]:
    temporal = str(temporal_grain or "").strip()
    if temporal == "HOUR":
        parsed_time = _parse_time(value)
        if parsed_time is None:
            return "", "operation_time_unparseable"
        return f"{parsed_time.hour:02d}:00", None
    parsed_date = _parse_date(value)
    if parsed_date is None:
        return "", "operation_date_unparseable"
    if temporal == "DAY":
        return parsed_date.isoformat(), None
    if temporal == "WEEK":
        iso_year, iso_week, _ = parsed_date.isocalendar()
        return f"{iso_year}-W{iso_week:02d}", None
    if temporal == "MONTH":
        return f"{parsed_date.year:04d}-{parsed_date.month:02d}", None
    return "", f"temporal_grain_unsupported:{temporal}"


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def _parse_time(value: Any) -> time | None:
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, time):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return time.fromisoformat(text)
    except ValueError:
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).time()
        except ValueError:
            return None


def _join_key(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _decision(
    case_id: str,
    analysis_id: str,
    status: str,
    reason: str,
    *,
    missing: tuple[str, ...] = (),
) -> Service1EvidencePreparationDecisionV1:
    return Service1EvidencePreparationDecisionV1(
        case_id=case_id,
        analysis_id=analysis_id,
        status=status,
        reason=reason,
        missing_evidence_refs=missing,
        provenance={"source": "F7_GOVERNED_EVIDENCE_PREPARATION"},
    )


__all__ = [
    "SCHEMA_VERSION",
    "PREPARED_SCHEMA_VERSION",
    "STATUS_PREPARED",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_UNSUPPORTED",
    "STATUS_BLOCKED",
    "Service1PreparedRowV1",
    "Service1PreparedGroupV1",
    "Service1PreparedRelationshipV1",
    "Service1PreparedAnalysisEvidenceV1",
    "Service1EvidencePreparationDecisionV1",
    "build_service_1_analysis_evidence_preparation_v1",
]
