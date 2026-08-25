"""Canonical P8 computability authority for Servicio 1 Stage 2 Package 5.

Consumes only P6-approved semantic decisions plus canonical P7 RequirementMatch
objects and governed catalogs. It never re-runs semantic inference/binding and
never executes computation. On READY it emits a GovernedComputationInput value
object suitable for deterministic execution.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from pymia.contracts.formula_rules_v1 import load_formula_rules
from pymia.smartpyme.service_1_analysis_plan_v1 import Service1AnalysisPlanV1
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED as P6_STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_BLOCKED,
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    P7_STATUS_NOT_OBSERVED,
    Service1AnalysisRequirementMatchV1,
    Service1GrainV1,
)
from pymia.smartpyme.service_1_derived_evidence_v1 import (
    SCHEMA_VERSION as DERIVED_EVIDENCE_SCHEMA_VERSION,
    STATUS_BLOCKED as DERIVED_EVIDENCE_BLOCKED,
    STATUS_NEEDS_EVIDENCE as DERIVED_EVIDENCE_NEEDS,
    STATUS_READY as DERIVED_EVIDENCE_READY,
)
from pymia.smartpyme.service_1_semantic_catalog_loader_v1 import (
    STATUS_CATALOGS_LOADED,
    STATUS_CATALOGS_PARTIALLY_LOADED,
    build_service_1_semantic_catalog_load_result_v1,
)
from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)

SCHEMA_VERSION = "SERVICE_1_COMPUTABILITY_V1"
CONFIRMED_BINDINGS_SCHEMA_VERSION = "SERVICE_1_CONFIRMED_SEMANTIC_BINDINGS_V1"
CONFIRMED_BINDINGS_STATUS = "CONFIRMED_BINDINGS"
STATUS_COMPUTABLE = "COMPUTABLE"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
STATUS_UNSUPPORTED_ANALYSIS = "UNSUPPORTED"
STATUS_BLOCKED = "BLOCKED"
ALLOWED_STATUSES = frozenset({STATUS_COMPUTABLE, STATUS_NEEDS_EVIDENCE, STATUS_UNSUPPORTED_CAPABILITY, STATUS_BLOCKED})
ANALYSIS_ALLOWED_STATUSES = frozenset({STATUS_COMPUTABLE, STATUS_NEEDS_EVIDENCE, STATUS_UNSUPPORTED_ANALYSIS, STATUS_BLOCKED})
_ALLOWED_CATALOG_LOAD_STATUSES = {STATUS_CATALOGS_LOADED, STATUS_CATALOGS_PARTIALLY_LOADED}
FANOUT_SAFE_LOOKUP = "SAFE_LOOKUP"
RELATIONSHIP_STATE_RESOLVED = "RESOLVED"
_RELATIONSHIP_AUTHORITY_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "join_execution_authorized",
    "computability_authorized",
)


@dataclass(frozen=True)
class Service1GovernedComputationInputV1:
    case_id: str
    requested_capability: str
    family_id: str
    pathology_code: str
    formula_id: str
    formula_expression: str
    required_variables: tuple[str, ...]
    required_evidence: tuple[str, ...]
    source_bindings: Mapping[str, Any]
    grain: Mapping[str, str]
    catalog_versions: Mapping[str, str | None]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"

    def __post_init__(self) -> None:
        for name in ("case_id", "requested_capability", "family_id", "pathology_code", "formula_id", "formula_expression"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if not self.required_variables:
            raise ValueError("required_variables must not be empty")
        if set(self.required_variables) != set(self.source_bindings):
            raise ValueError("source_bindings must cover exactly required_variables")
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "computability_authorized",
            "join_execution_authorized",
            "automatic_reuse_authorized",
            "semantic_rebind_authorized",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("provenance cannot carry authorization fields")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_bindings"] = dict(self.source_bindings)
        payload["grain"] = dict(self.grain)
        payload["catalog_versions"] = dict(self.catalog_versions)
        payload["provenance"] = dict(self.provenance)
        payload.update({
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        })
        return payload


@dataclass(frozen=True)
class Service1ComputabilityDecisionV1:
    case_id: str
    requested_capability: str
    status: str
    reason: str | None
    family_id: str | None = None
    missing_role_groups: tuple[tuple[str, ...], ...] = ()
    governed_computation_input: Service1GovernedComputationInputV1 | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.requested_capability.strip():
            raise ValueError("case_id and requested_capability are required")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError("invalid computability status")
        if self.status == STATUS_COMPUTABLE and self.governed_computation_input is None:
            raise ValueError("COMPUTABLE requires governed_computation_input")
        if self.status != STATUS_COMPUTABLE and self.governed_computation_input is not None:
            raise ValueError("non-computable decision cannot carry governed input")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "requested_capability": self.requested_capability,
            "status": self.status,
            "reason": self.reason,
            "family_id": self.family_id,
            "missing_role_groups": [list(group) for group in self.missing_role_groups],
            "governed_computation_input": self.governed_computation_input.to_dict() if self.governed_computation_input else None,
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }


@dataclass(frozen=True)
class Service1GovernedAnalysisInputV1:
    case_id: str
    analysis_plan: Service1AnalysisPlanV1
    source_bindings: Mapping[str, str]
    relationship_bindings: Mapping[str, Mapping[str, Any]]
    grain: Service1GrainV1
    formula_refs: tuple[str, ...] = ()
    safety_flags: tuple[str, ...] = (
        "P8_COMPUTABILITY_ONLY",
        "ANALYSIS_EXECUTION_NOT_AUTHORIZED",
        "AGGREGATION_RUNTIME_DEFERRED_TO_F8",
    )
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "SERVICE_1_GOVERNED_ANALYSIS_INPUT_V1"

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip():
            raise ValueError("case_id is required")
        if not isinstance(self.analysis_plan, Service1AnalysisPlanV1):
            raise TypeError("analysis_plan must be Service1AnalysisPlanV1")
        if not isinstance(self.grain, Service1GrainV1):
            raise TypeError("grain must be Service1GrainV1")
        if not isinstance(self.source_bindings, Mapping) or not self.source_bindings:
            raise ValueError("source_bindings must be a non-empty mapping")
        normalized_sources: dict[str, str] = {}
        for raw_role, raw_column in self.source_bindings.items():
            role = str(raw_role or "").strip()
            column = str(raw_column or "").strip()
            if not role or not column:
                raise ValueError("source_bindings require non-empty role and column refs")
            if role in normalized_sources:
                raise ValueError("source_bindings contain duplicate roles")
            normalized_sources[role] = column
        if len(set(normalized_sources.values())) != len(normalized_sources):
            raise ValueError("one source column cannot satisfy multiple analysis roles")
        object.__setattr__(self, "source_bindings", dict(normalized_sources))

        if not isinstance(self.relationship_bindings, Mapping):
            raise ValueError("relationship_bindings must be a mapping")
        normalized_relationships: dict[str, Mapping[str, Any]] = {}
        for raw_ref, raw_binding in self.relationship_bindings.items():
            ref = str(raw_ref or "").strip()
            if not ref or not isinstance(raw_binding, Mapping):
                raise ValueError("relationship_bindings require relationship refs and mapping values")
            normalized_relationships[ref] = dict(raw_binding)
        object.__setattr__(self, "relationship_bindings", normalized_relationships)

        formula_refs = tuple(str(value or "").strip() for value in self.formula_refs)
        if any(not value for value in formula_refs) or len(set(formula_refs)) != len(formula_refs):
            raise ValueError("formula_refs must contain unique non-empty refs")
        object.__setattr__(self, "formula_refs", formula_refs)
        safety_flags = tuple(str(value or "").strip() for value in self.safety_flags)
        if any(not value for value in safety_flags) or len(set(safety_flags)) != len(safety_flags):
            raise ValueError("safety_flags must contain unique non-empty flags")
        object.__setattr__(self, "safety_flags", safety_flags)
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "analysis_execution_authorized",
            "join_execution_authorized",
            "computability_authorized",
            "automatic_reuse_authorized",
            "semantic_rebind_authorized",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("analysis provenance cannot carry execution authority")
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_plan": self.analysis_plan.to_dict(),
            "source_bindings": dict(self.source_bindings),
            "relationship_bindings": {key: dict(value) for key, value in self.relationship_bindings.items()},
            "grain": self.grain.to_dict(),
            "formula_refs": list(self.formula_refs),
            "safety_flags": list(self.safety_flags),
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1GovernedRelationshipBindingV1:
    """P8-governed reference to one D4 relationship, never a copied graph."""

    source_artifact_ref: str
    workbook_ref: str
    schema_fingerprint: str
    d4_graph_ref: str
    relationship_ref: str
    left_logical_table_ref: str
    right_logical_table_ref: str
    left_sheet_ref: str
    left_column_ref: str
    right_sheet_ref: str
    right_column_ref: str
    relationship_kind: str
    cardinality: str
    fanout_evidence: Mapping[str, Any]
    owner_confirmation_event_ref: str
    confirmed_by_owner: bool
    integrity_digest: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "source_artifact_ref",
            "workbook_ref",
            "schema_fingerprint",
            "d4_graph_ref",
            "relationship_ref",
            "left_logical_table_ref",
            "right_logical_table_ref",
            "left_sheet_ref",
            "left_column_ref",
            "right_sheet_ref",
            "right_column_ref",
            "relationship_kind",
            "cardinality",
            "owner_confirmation_event_ref",
        )
        for name in required:
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if self.left_logical_table_ref == self.right_logical_table_ref:
            raise ValueError("relationship endpoints must be different logical tables")
        if self.relationship_kind != self.cardinality:
            raise ValueError("relationship_kind and cardinality must match")
        if self.confirmed_by_owner is not True:
            raise ValueError("relationship must be confirmed_by_owner")
        if not isinstance(self.fanout_evidence, Mapping):
            raise ValueError("fanout_evidence must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if str(self.owner_confirmation_event_ref).strip() in {
            str(self.relationship_ref).strip(),
            str(self.provenance.get("question_ref") or "").strip(),
        }:
            raise ValueError("owner_confirmation_event_ref must be distinct")
        if any(bool(self.provenance.get(flag)) for flag in _RELATIONSHIP_AUTHORITY_FLAGS):
            raise ValueError("relationship provenance cannot carry authority")
        payload = self._integrity_payload()
        expected = build_service_1_structural_digest_v1(payload=payload, prefix="grb_")
        if self.integrity_digest not in (None, expected):
            raise ValueError("relationship binding integrity digest mismatch")
        object.__setattr__(self, "integrity_digest", expected)
        object.__setattr__(self, "fanout_evidence", dict(self.fanout_evidence))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def _integrity_payload(self) -> dict[str, Any]:
        return {
            "source_artifact_ref": self.source_artifact_ref,
            "workbook_ref": self.workbook_ref,
            "schema_fingerprint": self.schema_fingerprint,
            "d4_graph_ref": self.d4_graph_ref,
            "relationship_ref": self.relationship_ref,
            "left_logical_table_ref": self.left_logical_table_ref,
            "right_logical_table_ref": self.right_logical_table_ref,
            "left_sheet_ref": self.left_sheet_ref,
            "left_column_ref": self.left_column_ref,
            "right_sheet_ref": self.right_sheet_ref,
            "right_column_ref": self.right_column_ref,
            "relationship_kind": self.relationship_kind,
            "cardinality": self.cardinality,
            "fanout_evidence": dict(self.fanout_evidence),
            "owner_confirmation_event_ref": self.owner_confirmation_event_ref,
            "confirmed_by_owner": True,
            "provenance": dict(self.provenance),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._integrity_payload(),
            "integrity_digest": self.integrity_digest,
            "p8_governed": True,
            "join_execution_authorized": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "computability_authorized": False,
        }


@dataclass(frozen=True)
class Service1AnalysisComputabilityDecisionV1:
    case_id: str
    analysis_id: str
    status: str
    reason: str | None
    missing_role_groups: tuple[tuple[str, ...], ...] = ()
    missing_relationship_refs: tuple[str, ...] = ()
    governed_analysis_input: Service1GovernedAnalysisInputV1 | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "SERVICE_1_ANALYSIS_COMPUTABILITY_DECISION_V1"

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if self.status not in ANALYSIS_ALLOWED_STATUSES:
            raise ValueError("invalid analysis computability status")
        if self.status == STATUS_COMPUTABLE and self.governed_analysis_input is None:
            raise ValueError("COMPUTABLE requires governed_analysis_input")
        if self.status != STATUS_COMPUTABLE and self.governed_analysis_input is not None:
            raise ValueError("non-computable analysis cannot carry governed input")
        if self.status == STATUS_COMPUTABLE and self.reason is not None:
            raise ValueError("COMPUTABLE cannot carry reason")
        if self.status != STATUS_COMPUTABLE and not str(self.reason or "").strip():
            raise ValueError("non-computable analysis requires reason")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        forbidden = {
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
            "analysis_execution_authorized",
        }
        if forbidden.intersection(self.provenance):
            raise ValueError("analysis decision provenance cannot carry execution authority")
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "reason": self.reason,
            "missing_role_groups": [list(group) for group in self.missing_role_groups],
            "missing_relationship_refs": list(self.missing_relationship_refs),
            "governed_analysis_input": self.governed_analysis_input.to_dict() if self.governed_analysis_input else None,
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


def build_service_1_governed_relationship_binding_v1(
    *,
    d4_graph: Mapping[str, Any] | None = None,
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
    owner_confirmation_event: Any,
    relationship_ref: str | None = None,
    source_artifact_ref: str | None = None,
    workbook_ref: str | None = None,
    schema_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Validate D4/D3/owner evidence and emit one immutable P8 binding."""
    model = d7_workbook_logical_model if isinstance(d7_workbook_logical_model, Mapping) else None
    graph = d4_graph if isinstance(d4_graph, Mapping) else None
    if graph is None and model is not None:
        graph = model.get("relationship_graph") if isinstance(model.get("relationship_graph"), Mapping) else None
    if not isinstance(graph, Mapping):
        raise ValueError("D4_RELATIONSHIP_PROVENANCE_REQUIRED")

    graph_ref = str(graph.get("graph_ref") or graph.get("graph_fingerprint") or "").strip()
    graph_provenance = graph.get("provenance") if isinstance(graph.get("provenance"), Mapping) else {}
    graph_schema = str(
        graph.get("schema_fingerprint")
        or graph_provenance.get("schema_fingerprint")
        or ""
    ).strip()
    if not graph_ref or not graph_schema:
        raise ValueError("D4_RELATIONSHIP_PROVENANCE_REQUIRED")
    expected_schema = str(
        schema_fingerprint
        or ((model or {}).get("schema_identity") or {}).get("schema_fingerprint")
        or ""
    ).strip()
    if expected_schema and expected_schema != graph_schema:
        raise ValueError("D4_SCHEMA_FINGERPRINT_MISMATCH")
    expected_workbook = str(
        workbook_ref
        or (model or {}).get("workbook_ref")
        or graph.get("workbook_ref")
        or graph_provenance.get("workbook_ref")
        or ""
    ).strip()
    expected_artifact = str(
        source_artifact_ref
        or (model or {}).get("source_artifact_ref")
        or graph.get("source_artifact_ref")
        or graph_provenance.get("source_artifact_ref")
        or ""
    ).strip()
    if not expected_workbook or not expected_artifact:
        raise ValueError("D4_RELATIONSHIP_PROVENANCE_REQUIRED")

    event = _event_mapping(owner_confirmation_event)
    event_ref = str(event.get("owner_confirmation_event_ref") or "").strip()
    ref = str(relationship_ref or event.get("relationship_ref") or "").strip()
    if not ref or not event_ref:
        raise ValueError("OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED")
    if event_ref in {ref, str(event.get("question_ref") or "").strip()}:
        raise ValueError("OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED")
    if event.get("confirmed_by_owner") is not True:
        raise ValueError("OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED")

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
        raise ValueError("D4_RELATIONSHIP_REF_NOT_FOUND")
    if str(relation.get("state") or "").strip() != RELATIONSHIP_STATE_RESOLVED:
        raise ValueError("D4_RELATIONSHIP_UNRESOLVED")
    relation_graph_ref = str(relation.get("d4_graph_ref") or relation.get("graph_ref") or graph_ref).strip()
    if relation_graph_ref != graph_ref:
        raise ValueError("D4_GRAPH_REF_MISMATCH")
    relation_schema = str(relation.get("schema_fingerprint") or graph_schema).strip()
    if relation_schema != graph_schema:
        raise ValueError("D4_SCHEMA_FINGERPRINT_MISMATCH")
    fanout = str(
        relation.get("fanout_risk")
        or ((relation.get("fanout_evidence") or {}).get("fanout_risk") if isinstance(relation.get("fanout_evidence"), Mapping) else "")
        or ""
    ).strip()
    if fanout != FANOUT_SAFE_LOOKUP:
        raise ValueError("D4_FANOUT_NOT_SAFE")

    left_sheet, left_column = _split_endpoint(
        relation.get("provenance", {}).get("physical_left_endpoint")
        if isinstance(relation.get("provenance"), Mapping)
        else None
    )
    right_sheet, right_column = _split_endpoint(
        relation.get("provenance", {}).get("physical_right_endpoint")
        if isinstance(relation.get("provenance"), Mapping)
        else None
    )
    expected_endpoints = (
        str(event.get("left_sheet_ref") or "").strip(),
        str(event.get("left_column_ref") or "").strip(),
        str(event.get("right_sheet_ref") or "").strip(),
        str(event.get("right_column_ref") or "").strip(),
    )
    if not all(expected_endpoints) or (left_sheet, left_column, right_sheet, right_column) != expected_endpoints:
        raise ValueError("D4_RELATIONSHIP_ENDPOINT_MISMATCH")
    cardinality = str(relation.get("cardinality") or relation.get("relationship_kind") or "").strip()
    event_kind = str(event.get("relationship_kind") or "").strip()
    if not cardinality or event_kind != cardinality:
        raise ValueError("D4_RELATIONSHIP_CARDINALITY_MISMATCH")
    relation_event_ref = str(relation.get("owner_confirmation_event_ref") or "").strip()
    if relation_event_ref and relation_event_ref != event_ref:
        raise ValueError("OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED")

    logical_left = str(relation.get("left_logical_table_ref") or "").strip()
    logical_right = str(relation.get("right_logical_table_ref") or "").strip()
    binding = Service1GovernedRelationshipBindingV1(
        source_artifact_ref=expected_artifact,
        workbook_ref=expected_workbook,
        schema_fingerprint=graph_schema,
        d4_graph_ref=graph_ref,
        relationship_ref=ref,
        left_logical_table_ref=logical_left,
        right_logical_table_ref=logical_right,
        left_sheet_ref=left_sheet,
        left_column_ref=left_column,
        right_sheet_ref=right_sheet,
        right_column_ref=right_column,
        relationship_kind=cardinality,
        cardinality=cardinality,
        fanout_evidence={
            "fanout_risk": fanout,
            "d4_state": str(relation.get("state") or "").strip(),
            "certificate_ref": str((graph.get("fanout_certificate") or {}).get("certificate_ref") or "").strip() or None,
        },
        owner_confirmation_event_ref=event_ref,
        confirmed_by_owner=True,
        provenance={
            "source": "D4_RELATIONSHIP_GRAPH_VIA_D7_PLUS_OWNER_EVENT",
            "question_ref": str(event.get("question_ref") or "").strip(),
            "case_id": str(event.get("case_id") or "").strip(),
            "p8_governed": True,
            "relationship_resolution_performed": False,
            "join_execution_authorized": False,
        },
    )
    return binding.to_dict()


def _event_mapping(event: Any) -> dict[str, Any]:
    if hasattr(event, "to_dict") and callable(event.to_dict):
        payload = event.to_dict()
        return dict(payload) if isinstance(payload, Mapping) else {}
    if isinstance(event, Mapping):
        payload = dict(event)
        provenance = payload.get("provenance")
        if isinstance(provenance, Mapping):
            for key in (
                "owner_confirmation_event_ref",
                "d4_graph_ref",
                "schema_fingerprint",
                "source_artifact_ref",
                "workbook_ref",
            ):
                if not str(payload.get(key) or "").strip() and str(provenance.get(key) or "").strip():
                    payload[key] = provenance[key]
        return payload
    raise ValueError("OWNER_RELATIONSHIP_CONFIRMATION_REQUIRED")


def _split_endpoint(value: Any) -> tuple[str, str]:
    text = str(value or "").strip()
    if "." not in text:
        return "", ""
    sheet, column = text.rsplit(".", 1)
    return sheet.strip(), column.strip()


def build_service_1_analysis_computability_decision_v1(
    *,
    case_id: str,
    analysis_plan: Service1AnalysisPlanV1,
    p6_decisions: tuple[Service1P6ApprovalDecisionV1, ...] | list[Service1P6ApprovalDecisionV1],
    analysis_requirement_match: Service1AnalysisRequirementMatchV1,
    relationship_bindings: Mapping[str, Mapping[str, Any]] | None = None,
    d4_graph: Mapping[str, Any] | None = None,
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
    source_artifact_ref: str | None = None,
    workbook_ref: str | None = None,
    schema_fingerprint: str | None = None,
) -> Service1AnalysisComputabilityDecisionV1:
    """P8 computability decision for declarative AnalysisPlan; never executes analysis."""
    case = str(case_id or "").strip()
    if not case:
        raise ValueError("case_id is required")
    if not isinstance(analysis_plan, Service1AnalysisPlanV1):
        raise TypeError("analysis_plan must be Service1AnalysisPlanV1")
    if not isinstance(analysis_requirement_match, Service1AnalysisRequirementMatchV1):
        raise TypeError("analysis_requirement_match must be Service1AnalysisRequirementMatchV1")
    match = analysis_requirement_match
    if match.analysis_id != analysis_plan.analysis_id:
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_ANALYSIS_ID_MISMATCH")
    if match.requested_grain.to_dict() != analysis_plan.requested_grain.to_dict():
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_REQUESTED_GRAIN_DRIFT")
    if tuple(match.required_relationship_refs) != tuple(analysis_plan.relationship_refs):
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_RELATIONSHIP_REQUIREMENT_DRIFT")

    decisions = tuple(p6_decisions or ())
    if not decisions:
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P6_APPROVAL_REQUIRED")
    for decision in decisions:
        if not isinstance(decision, Service1P6ApprovalDecisionV1):
            raise TypeError("p6_decisions must contain Service1P6ApprovalDecisionV1")
        if decision.status != P6_STATUS_APPROVED:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P6_APPROVAL_REQUIRED")
        if decision.case_id != case:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P6_CASE_MISMATCH")

    if match.status == P7_STATUS_BLOCKED:
        reason = str(match.reason or "P7_ANALYSIS_MATCH_BLOCKED")
        if reason.startswith("UNSUPPORTED_ANALYSIS_"):
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_UNSUPPORTED_ANALYSIS, reason)
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, reason)
    if match.status in {P7_STATUS_MISSING_REQUIREMENTS, P7_STATUS_NOT_OBSERVED}:
        return _analysis_decision(
            case,
            analysis_plan.analysis_id,
            STATUS_NEEDS_EVIDENCE,
            str(match.reason or "ANALYSIS_REQUIREMENTS_NOT_MATCHED"),
            missing_roles=match.missing_role_groups,
        )
    if match.status != P7_STATUS_MATCHED or match.resolved_grain is None:
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_ANALYSIS_MATCH_INVALID")
    if match.missing_role_groups or set(match.satisfied_role_groups) != set(match.required_role_groups):
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_REQUIREMENT_STATUS_DRIFT")

    requested = analysis_plan.requested_grain
    resolved = match.resolved_grain
    if (
        resolved.structural_scope != "REGION"
        or resolved.business_entity_grain != requested.business_entity_grain
        or resolved.temporal_grain != requested.temporal_grain
        or resolved.aggregation_grain != requested.aggregation_grain
    ):
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_RESOLVED_GRAIN_DRIFT")

    role_columns: dict[str, list[str]] = {}
    for decision in decisions:
        role = str(decision.approved_role or "").strip()
        column = str(decision.column_ref or "").strip()
        if role and column:
            role_columns.setdefault(role, [])
            if column not in role_columns[role]:
                role_columns[role].append(column)

    expected_p7_columns: list[str] = []
    for role in match.approved_roles:
        for column in role_columns.get(role, []):
            if column not in expected_p7_columns:
                expected_p7_columns.append(column)
    if set(expected_p7_columns) != set(match.source_columns) or len(expected_p7_columns) != len(match.source_columns):
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "P7_SOURCE_BINDING_DRIFT")

    source_bindings: dict[str, str] = {}
    used_columns: set[str] = set()
    for group in match.required_role_groups:
        matched_roles = [role for role in group if role_columns.get(role)]
        if not matched_roles:
            return _analysis_decision(
                case,
                analysis_plan.analysis_id,
                STATUS_NEEDS_EVIDENCE,
                "ANALYSIS_SOURCE_EVIDENCE_MISSING",
                missing_roles=(tuple(group),),
            )
        if len(matched_roles) != 1:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "AMBIGUOUS_ANALYSIS_ROLE_GROUP")
        role = matched_roles[0]
        columns = role_columns[role]
        if len(columns) != 1:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "AMBIGUOUS_ANALYSIS_SOURCE_COLUMN")
        column = columns[0]
        if column in used_columns:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "DUPLICATE_ANALYSIS_SOURCE_COLUMN")
        source_bindings[role] = column
        used_columns.add(column)

    provided_relationships = dict(relationship_bindings or {})
    required_relationships = tuple(match.required_relationship_refs)
    undeclared = tuple(ref for ref in provided_relationships if ref not in required_relationships)
    if undeclared:
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "UNDECLARED_RELATIONSHIP_BINDING")
    missing_relationships = tuple(ref for ref in required_relationships if ref not in provided_relationships)
    if missing_relationships:
        return _analysis_decision(
            case,
            analysis_plan.analysis_id,
            STATUS_NEEDS_EVIDENCE,
            "REQUIRED_RELATIONSHIP_EVIDENCE_MISSING",
            missing_relationships=missing_relationships,
        )
    normalized_relationships: dict[str, Mapping[str, Any]] = {}
    provenance_graph = d4_graph if isinstance(d4_graph, Mapping) else d7_workbook_logical_model
    for ref in required_relationships:
        binding = provided_relationships[ref]
        if not isinstance(binding, Mapping):
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "RELATIONSHIP_BINDING_INVALID")
        if str(binding.get("relationship_ref") or ref).strip() != ref:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "RELATIONSHIP_BINDING_REF_MISMATCH")
        if any(
            bool(binding.get(flag))
            for flag in (
                "runtime_authorized",
                "tool_execution_authorized",
                "product_ready",
                "delivery_authorized",
                "diagnosis_generated",
                "analysis_execution_authorized",
            )
        ):
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, "RELATIONSHIP_BINDING_AUTHORITY_FORBIDDEN")
        if binding.get("confirmed_by_owner") is not True:
            return _analysis_decision(
                case,
                analysis_plan.analysis_id,
                STATUS_NEEDS_EVIDENCE,
                "RELATIONSHIP_OWNER_CONFIRMATION_REQUIRED",
                missing_relationships=(ref,),
            )
        if provenance_graph is not None:
            try:
                normalized_relationships[ref] = build_service_1_governed_relationship_binding_v1(
                    d4_graph=d4_graph,
                    d7_workbook_logical_model=d7_workbook_logical_model,
                    owner_confirmation_event=binding,
                    relationship_ref=ref,
                    source_artifact_ref=source_artifact_ref,
                    workbook_ref=workbook_ref,
                    schema_fingerprint=schema_fingerprint,
                )
            except ValueError as exc:
                return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, str(exc))
        else:
            normalized_relationships[ref] = dict(binding)

    formula_refs, formula_ref_error = _analysis_formula_refs(analysis_plan)
    if formula_ref_error is not None:
        return _analysis_decision(case, analysis_plan.analysis_id, STATUS_UNSUPPORTED_ANALYSIS, formula_ref_error)
    for formula_ref in formula_refs:
        if _formula_rule(formula_ref) is None:
            return _analysis_decision(case, analysis_plan.analysis_id, STATUS_BLOCKED, f"FORMULA_RULE_NOT_FOUND:{formula_ref}")
    governed = Service1GovernedAnalysisInputV1(
        case_id=case,
        analysis_plan=analysis_plan,
        source_bindings=source_bindings,
        relationship_bindings=normalized_relationships,
        grain=resolved,
        formula_refs=formula_refs,
        provenance={
            "source": "ANALYSIS_PLAN_PLUS_P6_PLUS_P7",
            "p7_source": "Service1AnalysisRequirementMatchV1",
            "p8_computability_only": True,
            "relationship_resolution_performed": False,
            "analysis_execution_performed": False,
            "p8_relationship_governance": bool(provenance_graph is not None),
            "d4_graph_ref": (
                str((provenance_graph or {}).get("graph_ref") or "").strip() or None
                if isinstance(provenance_graph, Mapping)
                else None
            ),
            "schema_fingerprint": (
                str(schema_fingerprint or ((provenance_graph or {}).get("schema_fingerprint") or ((provenance_graph or {}).get("provenance") or {}).get("schema_fingerprint") or "")).strip() or None
                if isinstance(provenance_graph, Mapping)
                else None
            ),
        },
    )
    return Service1AnalysisComputabilityDecisionV1(
        case_id=case,
        analysis_id=analysis_plan.analysis_id,
        status=STATUS_COMPUTABLE,
        reason=None,
        governed_analysis_input=governed,
        provenance={"source": "P8_ANALYSIS_COMPUTABILITY"},
    )


def build_service_1_computability_decision_v1(
    *,
    case_id: str,
    requested_capability: str,
    p6_decisions: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    requirement_matches: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    derived_evidence_packet: Mapping[str, Any] | None = None,
    formula_catalog_path: str | Path | None = None,
    pathology_catalog_path: str | Path | None = None,
    evidence_matrix_path: str | Path | None = None,
) -> Service1ComputabilityDecisionV1:
    case = str(case_id or "").strip()
    capability = str(requested_capability or "").strip()
    if not case or not capability:
        raise ValueError("case_id and requested_capability are required")

    decisions = tuple(p6_decisions or ())
    if not decisions or any(str(item.get("status") or "") != "APPROVED" for item in decisions):
        return _decision(case, capability, STATUS_BLOCKED, "P6_APPROVAL_REQUIRED")

    matches = tuple(requirement_matches or ())
    match = next((item for item in matches if capability in tuple(item.get("target_capabilities") or ())), None)
    if match is None:
        return _decision(case, capability, STATUS_UNSUPPORTED_CAPABILITY, "CAPABILITY_NOT_GOVERNED")
    family_id = str(match.get("family_id") or "").strip() or None
    match_status = str(match.get("status") or "")
    missing_role_groups = tuple(tuple(group) for group in (match.get("missing_role_groups") or ()))

    family_roles = {
        str(role).strip()
        for group in (match.get("required_role_groups") or ())
        for role in group
        if str(role).strip()
    }
    source_by_variable: dict[str, Any] = {
        str(item.get("approved_variable") or "").strip(): str(item.get("column_ref") or "").strip()
        for item in decisions
        if (not family_roles or str(item.get("approved_role") or "").strip() in family_roles)
        and str(item.get("approved_variable") or "").strip()
        and str(item.get("column_ref") or "").strip()
    }
    # Canonical formula-variable aliases may share the same approved semantic
    # evidence without changing the P6 role. Example: sales_amount is named
    # sold_amount by LIQ_001 and sales by DSO. This is variable normalization,
    # not semantic rebinding.
    for item in decisions:
        role = str(item.get("approved_role") or "").strip()
        column = str(item.get("column_ref") or "").strip()
        if role == "sales_amount" and role in family_roles and column:
            source_by_variable.setdefault("sales", column)

    derived_sources, derived_error = _validated_derived_source_bindings(
        packet=derived_evidence_packet,
        case_id=case,
        requested_capability=capability,
    )
    if derived_error is not None:
        return _decision(case, capability, STATUS_BLOCKED, derived_error, family_id=family_id)
    for variable_name, source in derived_sources.items():
        if variable_name in source_by_variable:
            return _decision(
                case,
                capability,
                STATUS_BLOCKED,
                f"DUPLICATE_FORMULA_INPUT_SOURCE:{variable_name}",
                family_id=family_id,
            )
        source_by_variable[variable_name] = source

    paths = _catalog_paths(formula_catalog_path, pathology_catalog_path, evidence_matrix_path)
    try:
        matrix = _load_json(paths["evidence_matrix"])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _decision(case, capability, STATUS_BLOCKED, f"EVIDENCE_MATRIX_INVALID:{exc}", family_id=family_id)
    if matrix.get("computation_candidate_planning_allowed") is not True:
        return _decision(case, capability, STATUS_BLOCKED, "MATRIX_COMPUTATION_PLANNING_NOT_ALLOWED", family_id=family_id)
    matrix_rule_error = _validate_matrix_against_formula_rules(matrix)
    if matrix_rule_error:
        return _decision(case, capability, STATUS_BLOCKED, matrix_rule_error, family_id=family_id)
    entries = [e for e in matrix.get("entries", []) if isinstance(e, dict) and capability in tuple(e.get("capability_refs") or ())]
    if len(entries) != 1:
        reason = "CAPABILITY_HAS_NO_GOVERNED_FORMULA_MAPPING" if not entries else "AMBIGUOUS_CAPABILITY_FORMULA_MAPPING"
        status = STATUS_UNSUPPORTED_CAPABILITY if not entries else STATUS_BLOCKED
        return _decision(case, capability, status, reason, family_id=family_id)
    entry = entries[0]
    if entry.get("computation_candidate_allowed") is not True:
        return _decision(case, capability, STATUS_BLOCKED, "COMPUTATION_CANDIDATE_NOT_ALLOWED", family_id=family_id)
    formula_refs = tuple(str(v).strip() for v in entry.get("formula_refs", []) if str(v).strip())
    pathology_code = str(entry.get("pathology_code") or "").strip()
    if len(formula_refs) != 1 or not pathology_code:
        return _decision(case, capability, STATUS_BLOCKED, "MATRIX_MAPPING_MUST_RESOLVE_ONE_FORMULA", family_id=family_id)
    canonical_rule = _formula_rule(formula_refs[0])
    if canonical_rule is None:
        return _decision(case, capability, STATUS_BLOCKED, "FORMULA_RULE_NOT_FOUND", family_id=family_id)
    if canonical_rule.get("pathology_code") not in (None, pathology_code):
        return _decision(case, capability, STATUS_BLOCKED, "FORMULA_RULE_PATHOLOGY_DRIFT", family_id=family_id)

    catalog = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=paths["formula_catalog"],
        pathology_catalog_path=paths["pathology_catalog"],
        metadata={"requested_capability": capability},
    )
    if catalog.status not in _ALLOWED_CATALOG_LOAD_STATUSES:
        return _decision(case, capability, STATUS_BLOCKED, f"CATALOG_LOAD_BLOCKED:{catalog.status}", family_id=family_id)
    formulas = tuple(f for f in catalog.formula_entries if f.formula_id == formula_refs[0] and f.pathology_code == pathology_code)
    if len(formulas) != 1:
        return _decision(case, capability, STATUS_BLOCKED, "GOVERNED_FORMULA_OR_PATHOLOGY_MISSING", family_id=family_id)
    formula = formulas[0]
    catalog_drift = _catalog_formula_drift(canonical_rule, formula)
    if catalog_drift:
        return _decision(case, capability, STATUS_BLOCKED, catalog_drift, family_id=family_id)
    required = tuple(str(value) for value in canonical_rule.get("required_inputs") or ())
    if formula.calculation_state != "CALCULABLE":
        return _decision(case, capability, STATUS_NEEDS_EVIDENCE, "FORMULA_REQUIRES_ADDITIONAL_ASSUMPTIONS", family_id=family_id)
    missing_variables = tuple(v for v in required if v not in source_by_variable)
    if missing_variables:
        reason = "REQUIREMENTS_NOT_MATCHED" if match_status != "REQUIREMENT_MATCHED" else "FORMULA_INPUTS_NOT_READY"
        return _decision(
            case,
            capability,
            STATUS_NEEDS_EVIDENCE,
            reason,
            family_id=family_id,
            missing=missing_role_groups,
        )
    if match_status != "REQUIREMENT_MATCHED" and not derived_sources:
        return _decision(
            case,
            capability,
            STATUS_NEEDS_EVIDENCE,
            "REQUIREMENTS_NOT_MATCHED",
            family_id=family_id,
            missing=missing_role_groups,
        )

    versions = _catalog_versions(paths, matrix)
    governed = Service1GovernedComputationInputV1(
        case_id=case,
        requested_capability=capability,
        family_id=family_id or "",
        pathology_code=pathology_code,
        formula_id=str(canonical_rule["formula_id"]),
        formula_expression=str(canonical_rule["expression"]),
        required_variables=required,
        required_evidence=tuple(formula.required_evidence),
        source_bindings={v: source_by_variable[v] for v in required},
        grain=dict(match.get("grain") or {}),
        catalog_versions=versions,
        provenance={"p6_source": "Service1P6ApprovalDecisionV1", "p7_source": "Service1RequirementMatchV1"},
    )
    return Service1ComputabilityDecisionV1(
        case_id=case,
        requested_capability=capability,
        status=STATUS_COMPUTABLE,
        reason=None,
        family_id=family_id,
        governed_computation_input=governed,
        provenance={
            "source": (
                "P6_PLUS_P7_PLUS_DERIVED_EVIDENCE_PLUS_GOVERNED_CATALOGS"
                if derived_sources
                else "P6_PLUS_P7_PLUS_GOVERNED_CATALOGS"
            )
        },
    )


def _validated_derived_source_bindings(
    *,
    packet: Mapping[str, Any] | None,
    case_id: str,
    requested_capability: str,
) -> tuple[dict[str, Any], str | None]:
    if packet is None:
        return {}, None
    if not isinstance(packet, Mapping):
        return {}, "DERIVED_EVIDENCE_PACKET_INVALID"
    if packet.get("schema_version") != DERIVED_EVIDENCE_SCHEMA_VERSION:
        return {}, "DERIVED_EVIDENCE_SCHEMA_INVALID"
    if str(packet.get("case_id") or "").strip() != case_id:
        return {}, "DERIVED_EVIDENCE_CASE_MISMATCH"
    if str(packet.get("requested_capability") or "").strip() != requested_capability:
        return {}, "DERIVED_EVIDENCE_CAPABILITY_MISMATCH"
    if any(
        bool(packet.get(flag))
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    ):
        return {}, "DERIVED_EVIDENCE_AUTHORITY_FORBIDDEN"
    status = str(packet.get("status") or "")
    if status == DERIVED_EVIDENCE_BLOCKED:
        return {}, str(packet.get("blocked_reason") or "DERIVED_EVIDENCE_BLOCKED")
    if status not in {DERIVED_EVIDENCE_READY, DERIVED_EVIDENCE_NEEDS}:
        return {}, "DERIVED_EVIDENCE_STATUS_INVALID"
    raw_variables = packet.get("derived_variables") or {}
    if not isinstance(raw_variables, Mapping):
        return {}, "DERIVED_EVIDENCE_VARIABLES_INVALID"

    sources: dict[str, Any] = {}
    for raw_name, raw_item in raw_variables.items():
        name = str(raw_name or "").strip()
        if not name or not isinstance(raw_item, Mapping):
            return {}, "DERIVED_EVIDENCE_VARIABLE_INVALID"
        derivation_id = str(raw_item.get("derivation_id") or "").strip()
        semantic_role = str(raw_item.get("semantic_role") or "").strip()
        if not derivation_id or not semantic_role or "value" not in raw_item:
            return {}, f"DERIVED_EVIDENCE_VARIABLE_INVALID:{name}"
        if any(
            bool(raw_item.get(flag))
            for flag in (
                "runtime_authorized",
                "tool_execution_authorized",
                "product_ready",
                "delivery_authorized",
                "diagnosis_generated",
            )
        ):
            return {}, f"DERIVED_EVIDENCE_AUTHORITY_FORBIDDEN:{name}"
        sources[name] = {
            "source_kind": "DERIVED_EVIDENCE",
            "schema_version": DERIVED_EVIDENCE_SCHEMA_VERSION,
            "derivation_id": derivation_id,
            "semantic_role": semantic_role,
            "source_column_refs": list(raw_item.get("source_column_refs") or []),
            "relationship_refs": list(raw_item.get("relationship_refs") or []),
        }
    return sources, None


def build_service_1_composite_governed_computation_input_v1(*, case_id: str, capability_ref: str) -> Service1GovernedComputationInputV1:
    """Build governed execution input for a COMPOSITE capability from registry contracts only."""
    from pymia.smartpyme.service_1_capability_registry_v1 import get_capability_definition_v1

    case = str(case_id or "").strip()
    capability = str(capability_ref or "").strip()
    if not case or not capability:
        raise ValueError("case_id and capability_ref are required")
    definition = get_capability_definition_v1(capability)
    if definition is None or definition.kind != "COMPOSITE":
        raise ValueError("composite capability definition required")

    paths = _catalog_paths(None, None, None)
    catalog = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=paths["formula_catalog"],
        pathology_catalog_path=paths["pathology_catalog"],
        metadata={"requested_capability": capability, "composite": True},
    )
    if catalog.status not in _ALLOWED_CATALOG_LOAD_STATUSES:
        raise ValueError(f"CATALOG_LOAD_BLOCKED:{catalog.status}")
    formulas = tuple(f for f in catalog.formula_entries if f.formula_id == definition.formula_ref and f.pathology_code == definition.pathology_code)
    if len(formulas) != 1:
        raise ValueError("GOVERNED_COMPOSITE_FORMULA_MISSING")
    formula = formulas[0]
    canonical_rule = _formula_rule(definition.formula_ref)
    if canonical_rule is None:
        raise ValueError("FORMULA_RULE_NOT_FOUND")
    if canonical_rule.get("pathology_code") not in (None, definition.pathology_code):
        raise ValueError("FORMULA_RULE_PATHOLOGY_DRIFT")
    catalog_drift = _catalog_formula_drift(canonical_rule, formula)
    if catalog_drift:
        raise ValueError(catalog_drift)
    bindings: dict[str, Any] = {}
    for variable in definition.variables:
        if not variable.source_capability_ref or not variable.source_result_key:
            raise ValueError(f"composite source contract missing for {variable.name}")
        bindings[variable.name] = {
            "capability_ref": variable.source_capability_ref,
            "result_key": variable.source_result_key,
        }
    return Service1GovernedComputationInputV1(
        case_id=case,
        requested_capability=capability,
        family_id="COMPOSITE_GOVERNED_RESULTS",
        pathology_code=definition.pathology_code,
        formula_id=definition.formula_ref,
        formula_expression=str(canonical_rule["expression"]),
        required_variables=tuple(str(value) for value in canonical_rule.get("required_inputs") or ()),
        required_evidence=tuple(formula.required_evidence),
        source_bindings=bindings,
        grain={"structural_scope": "RESULT_SET", "business_entity_grain": "NONE", "temporal_grain": "PERIOD", "aggregation_grain": "AGGREGATED"},
        catalog_versions=_catalog_versions(paths, {}),
        provenance={"source": "CAPABILITY_REGISTRY_PLUS_GOVERNED_RESULTS", "composite": True},
    )


def build_computability_decision_from_confirmed_bindings_v1(
    *,
    confirmed_bindings: Any,
    requested_capability: str,
    derived_evidence_packet: Mapping[str, Any] | None = None,
    formula_catalog_path: str | Path | None = None,
    pathology_catalog_path: str | Path | None = None,
    evidence_matrix_path: str | Path | None = None,
) -> Any:
    """Build the canonical P8 decision from SEM-8 confirmed bindings.

    This adapter belongs to P8.  It does not compose semantic stages or
    provide a second semantic state machine.
    """
    if not isinstance(confirmed_bindings, Mapping):
        raise ValueError("confirmed_bindings must be a mapping")
    if (
        str(confirmed_bindings.get("schema_version") or "").strip()
        != CONFIRMED_BINDINGS_SCHEMA_VERSION
        or confirmed_bindings.get("status") != CONFIRMED_BINDINGS_STATUS
    ):
        raise ValueError("confirmed bindings are required")
    capability = str(requested_capability or "").strip()
    if not capability:
        raise ValueError("requested_capability is required")
    evidence = _confirmed_evidence_packet(confirmed_bindings)
    if evidence is None:
        raise ValueError("confirmed evidence packet is missing")
    bridge = confirmed_bindings.get("bridge_packet")
    case_id = str(
        evidence.get("case_id")
        or (bridge.get("case_id") if isinstance(bridge, Mapping) else "")
        or ""
    ).strip()
    if not case_id:
        raise ValueError("case_id is required")
    return build_service_1_computability_decision_v1(
        case_id=case_id,
        requested_capability=capability,
        p6_decisions=list(evidence.get("p6_decisions") or []),
        requirement_matches=list(evidence.get("requirement_matches") or []),
        derived_evidence_packet=derived_evidence_packet,
        formula_catalog_path=formula_catalog_path,
        pathology_catalog_path=pathology_catalog_path,
        evidence_matrix_path=evidence_matrix_path,
    )


def _confirmed_evidence_packet(
    confirmed_bindings: Mapping[str, Any],
) -> dict[str, Any] | None:
    reentry = confirmed_bindings.get("reentry_packet")
    if isinstance(reentry, Mapping) and reentry.get("column_candidates"):
        return dict(reentry)
    bridge = confirmed_bindings.get("bridge_packet")
    gate = confirmed_bindings.get("gate_packet")
    if isinstance(bridge, Mapping) and isinstance(gate, Mapping):
        merged = dict(bridge)
        merged["variable_family_bindings"] = gate.get("variable_family_bindings", ())
        merged["ready_variable_family_ids"] = gate.get("ready_variable_family_ids", [])
        merged["p6_decisions"] = gate.get("p6_decisions", [])
        merged["requirement_matches"] = gate.get("requirement_matches", [])
        return merged
    return None


def _analysis_formula_refs(analysis_plan: Service1AnalysisPlanV1) -> tuple[tuple[str, ...], str | None]:
    formula_by_measure = {
        "sales": None,
        "gross_margin": "margen_bruto",
        "sales_concentration": "PYME_033_concentracion_sku",
        "units": None,
        "row_count": None,
        "catalog_price_variance_pct": "precio_catalogo_variacion_pct",
        "dso": "PYME_011_dso",
        "projected_cash_balance": "LIQ_002_saldo_final_proyectado",
    }
    refs: list[str] = []
    for measure in analysis_plan.measures:
        if measure not in formula_by_measure:
            return (), f"UNSUPPORTED_ANALYSIS_MEASURE:{measure}"
        formula_ref = formula_by_measure[measure]
        if formula_ref and formula_ref not in refs:
            refs.append(formula_ref)
    return tuple(refs), None


def _analysis_decision(
    case_id: str,
    analysis_id: str,
    status: str,
    reason: str,
    *,
    missing_roles: tuple[tuple[str, ...], ...] = (),
    missing_relationships: tuple[str, ...] = (),
) -> Service1AnalysisComputabilityDecisionV1:
    return Service1AnalysisComputabilityDecisionV1(
        case_id=case_id,
        analysis_id=analysis_id,
        status=status,
        reason=reason,
        missing_role_groups=missing_roles,
        missing_relationship_refs=missing_relationships,
        provenance={"source": "P8_ANALYSIS_COMPUTABILITY"},
    )


def _decision(case: str, capability: str, status: str, reason: str, *, family_id: str | None = None, missing: tuple[tuple[str, ...], ...] = ()) -> Service1ComputabilityDecisionV1:
    return Service1ComputabilityDecisionV1(case_id=case, requested_capability=capability, status=status, reason=reason, family_id=family_id, missing_role_groups=missing, provenance={"source": "P8_COMPUTABILITY"})


def _catalog_paths(formula_catalog_path: str | Path | None, pathology_catalog_path: str | Path | None, evidence_matrix_path: str | Path | None) -> dict[str, Path]:
    docs = Path(__file__).resolve().parents[2] / "docs"
    return {
        "formula_catalog": Path(formula_catalog_path) if formula_catalog_path else docs / "formula_catalog.v1.json",
        "pathology_catalog": Path(pathology_catalog_path) if pathology_catalog_path else docs / "pathology_catalog.enriched.v2.json",
        "evidence_matrix": Path(evidence_matrix_path) if evidence_matrix_path else docs / "service_1_formula_pathology_evidence_matrix.v2.json",
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise OSError(f"file_not_found:{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_root_not_object:{path}")
    return payload


def _formula_rules_by_id() -> dict[str, dict[str, Any]]:
    payload = load_formula_rules()
    rules = payload.get("rules_by_formula")
    if not isinstance(rules, dict):
        raise ValueError("FORMULA_RULES_INVALID")
    return {str(key): value for key, value in rules.items() if isinstance(value, dict)}


def _formula_rule(formula_id: str) -> dict[str, Any] | None:
    return _formula_rules_by_id().get(str(formula_id).strip())


def _validate_matrix_against_formula_rules(matrix: Mapping[str, Any]) -> str | None:
    try:
        rules = _formula_rules_by_id()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return f"FORMULA_RULES_INVALID:{exc}"
    for entry in matrix.get("entries", ()):
        if not isinstance(entry, Mapping):
            continue
        required = tuple(str(value).strip() for value in entry.get("required_variables", ()) if str(value).strip())
        for formula_ref in tuple(str(value).strip() for value in entry.get("formula_refs", ()) if str(value).strip()):
            rule = rules.get(formula_ref)
            if rule is None:
                return f"FORMULA_RULES_MATRIX_DRIFT:{formula_ref}:missing_rule"
            rule_required = tuple(str(value) for value in rule.get("required_inputs") or ())
            if required != rule_required:
                return f"FORMULA_RULES_MATRIX_DRIFT:{formula_ref}:required_variables"
            pathology = str(entry.get("pathology_code") or "").strip()
            rule_pathology = rule.get("pathology_code")
            if rule_pathology is not None and str(rule_pathology).strip() != pathology:
                return f"FORMULA_RULES_MATRIX_DRIFT:{formula_ref}:pathology_code"
    return None


def _catalog_formula_drift(rule: Mapping[str, Any], formula: Any) -> str | None:
    comparisons = {
        "formula_id": (str(rule.get("formula_id") or ""), str(formula.formula_id or "")),
        "pathology_code": (str(rule.get("pathology_code") or ""), str(formula.pathology_code or "")),
        "expression": (str(rule.get("expression") or ""), str(formula.expression or "")),
        "required_variables": (
            tuple(str(value) for value in rule.get("required_inputs") or ()),
            tuple(str(value) for value in formula.required_variables),
        ),
        "output_unit": (rule.get("output_unit"), formula.metadata.get("output_unit")),
    }
    for field_name, (expected, actual) in comparisons.items():
        if expected != actual:
            return f"FORMULA_RULES_CATALOG_DRIFT:{formula.formula_id}:{field_name}"
    return None


def _catalog_versions(paths: dict[str, Path], matrix: dict[str, Any]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {"formula_catalog": None, "pathology_catalog": None, "evidence_matrix": str(matrix.get("catalog_version") or "") or None}
    for key in ("formula_catalog", "pathology_catalog"):
        try:
            versions[key] = str(_load_json(paths[key]).get("catalog_version") or "") or None
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    return versions


__all__ = [
    "SCHEMA_VERSION", "CONFIRMED_BINDINGS_SCHEMA_VERSION", "CONFIRMED_BINDINGS_STATUS", "STATUS_COMPUTABLE", "STATUS_NEEDS_EVIDENCE", "STATUS_UNSUPPORTED_CAPABILITY", "STATUS_UNSUPPORTED_ANALYSIS", "STATUS_BLOCKED",
    "Service1ComputabilityDecisionV1", "Service1GovernedComputationInputV1", "Service1GovernedRelationshipBindingV1", "build_service_1_computability_decision_v1", "build_service_1_governed_relationship_binding_v1",
    "Service1AnalysisComputabilityDecisionV1", "Service1GovernedAnalysisInputV1", "build_service_1_analysis_computability_decision_v1",
    "build_service_1_composite_governed_computation_input_v1", "build_computability_decision_from_confirmed_bindings_v1",
]
