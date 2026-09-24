"""F9 governed ResultSet, bounded outcomes and findings for Service 1.

F9 consumes F8 mathematical results plus the F7 evidence surface used to
produce them. It projects typed immutable analytical results and bounded
findings. It does not execute math, infer causes, assign severity/risk, create
recommendations, render UI, persist data, or authorize delivery.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Final, Mapping

from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    Service1PreparedAnalysisEvidenceV1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    Service1AnalysisMathResultV1,
    Service1ExecutedGroupV1,
    Service1ExecutedMeasureV1,
)
from pymia.smartpyme.service_1_analysis_plan_v1 import AnalysisKind
from pymia.smartpyme.service_1_variable_family_bindings_v1 import Service1GrainV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_RESULT_PROJECTION_V1"
RESULT_SET_SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_RESULT_SET_V1"
FINDING_SCHEMA_VERSION: Final[str] = "SERVICE_1_FINDING_V1"
OUTCOME_SCHEMA_VERSION: Final[str] = "SERVICE_1_BOUNDED_ANALYSIS_OUTCOME_V1"
INTEGRITY_SCOPE_FINDING: Final[str] = "SERVICE_1_FINDING_CANONICAL_PAYLOAD_V1"
INTEGRITY_SCOPE_RESULT_SET: Final[str] = "SERVICE_1_RESULT_SET_CANONICAL_PAYLOAD_V1"

STATUS_READY: Final[str] = "RESULT_PROJECTION_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "analysis_execution_authorized",
)

_GENERIC_LIMITATIONS: Final[tuple[str, ...]] = (
    "The result describes governed mathematical evidence and does not establish causality.",
    "No severity, risk level, recommendation, or financial impact is inferred without a separate governed policy and sufficient evidence.",
)
_GENERIC_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "Do not claim causality, fraud, misconduct, insolvency, operational failure, or responsibility from this analytical result alone.",
    "Do not present an inferred recommendation, risk severity, or financial impact as evidence unless a governed downstream policy explicitly supports it.",
)


@dataclass(frozen=True)
class Service1IntegrityDigestV1:
    algorithm: str
    digest: str
    scope: str
    authenticity_asserted: bool = False
    non_repudiation_asserted: bool = False

    def __post_init__(self) -> None:
        if self.algorithm != "SHA-256":
            raise ValueError("algorithm must equal SHA-256")
        if len(self.digest) != 64 or any(character not in "0123456789abcdef" for character in self.digest):
            raise ValueError("digest must be a lowercase SHA-256 hex digest")
        if not str(self.scope or "").strip():
            raise ValueError("scope is required")
        if self.authenticity_asserted or self.non_repudiation_asserted:
            raise ValueError("F9 content digests do not assert authenticity or non-repudiation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "digest": self.digest,
            "scope": self.scope,
            "authenticity_asserted": False,
            "non_repudiation_asserted": False,
        }


@dataclass(frozen=True)
class Service1FinancialImpactV1:
    """Optional factual financial impact supplied by a future governed policy.

    F9 currently does not infer or populate this contract automatically.
    """

    amount: float
    currency_code: str
    impact_kind: str
    basis_ref: str

    def __post_init__(self) -> None:
        if isinstance(self.amount, bool) or not isinstance(self.amount, (int, float)) or not math.isfinite(float(self.amount)):
            raise ValueError("amount must be a finite number")
        currency = str(self.currency_code or "").strip().upper()
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("currency_code must be a three-letter alphabetic code")
        for name in ("impact_kind", "basis_ref"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "currency_code", currency)

    def to_dict(self) -> dict[str, Any]:
        return {
            "amount": float(self.amount),
            "currency_code": self.currency_code,
            "impact_kind": self.impact_kind,
            "basis_ref": self.basis_ref,
        }


@dataclass(frozen=True)
class Service1EvidenceChainV1:
    source_refs: tuple[str, ...]
    member_row_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    formula_ref: str | None
    math_trace: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        if not self.source_refs or any(not str(ref).strip() for ref in self.source_refs):
            raise ValueError("source_refs must be non-empty")
        if not self.member_row_refs or any(not str(ref).strip() for ref in self.member_row_refs):
            raise ValueError("member_row_refs must be non-empty")
        if any(not str(ref).strip() for ref in self.relationship_refs):
            raise ValueError("relationship_refs must contain non-empty refs")
        object.__setattr__(self, "source_refs", tuple(dict.fromkeys(self.source_refs)))
        object.__setattr__(self, "member_row_refs", tuple(dict.fromkeys(self.member_row_refs)))
        object.__setattr__(self, "relationship_refs", tuple(dict.fromkeys(self.relationship_refs)))
        object.__setattr__(self, "math_trace", tuple(_freeze_json(dict(item)) for item in self.math_trace))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_refs": list(self.source_refs),
            "member_row_refs": list(self.member_row_refs),
            "relationship_refs": list(self.relationship_refs),
            "formula_ref": self.formula_ref,
            "math_trace": [_thaw_json(item) for item in self.math_trace],
        }


@dataclass(frozen=True)
class Service1ResultMeasureV1:
    measure_ref: str
    value: float
    unit: str
    currency_code: str | None
    formula_ref: str | None
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not str(self.measure_ref or "").strip() or not str(self.unit or "").strip():
            raise ValueError("measure_ref and unit are required")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)) or not math.isfinite(float(self.value)):
            raise ValueError("value must be a finite number")
        if self.currency_code is not None:
            currency = str(self.currency_code).strip().upper()
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError("currency_code must be a three-letter alphabetic code")
            object.__setattr__(self, "currency_code", currency)
        if self.unit != "currency" and self.currency_code is not None:
            raise ValueError("currency_code can only be attached to currency measures")
        if not self.source_refs or any(not str(ref).strip() for ref in self.source_refs):
            raise ValueError("source_refs must be non-empty")
        object.__setattr__(self, "source_refs", tuple(dict.fromkeys(self.source_refs)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "measure_ref": self.measure_ref,
            "value": float(self.value),
            "unit": self.unit,
            "currency_code": self.currency_code,
            "formula_ref": self.formula_ref,
            "source_refs": list(self.source_refs),
        }


@dataclass(frozen=True)
class Service1ResultGroupV1:
    group_ref: str
    key: Mapping[str, str]
    measures: Mapping[str, Service1ResultMeasureV1]
    member_row_refs: tuple[str, ...]
    rank: int | None = None

    def __post_init__(self) -> None:
        if not str(self.group_ref or "").strip():
            raise ValueError("group_ref is required")
        if not isinstance(self.key, Mapping):
            raise ValueError("key must be a mapping")
        if not isinstance(self.measures, Mapping) or not self.measures:
            raise ValueError("measures must be a non-empty mapping")
        if any(not isinstance(value, Service1ResultMeasureV1) for value in self.measures.values()):
            raise TypeError("measures must contain Service1ResultMeasureV1")
        if not self.member_row_refs:
            raise ValueError("member_row_refs must be non-empty")
        if self.rank is not None and self.rank <= 0:
            raise ValueError("rank must be positive")
        object.__setattr__(self, "key", MappingProxyType(dict(self.key)))
        object.__setattr__(self, "measures", MappingProxyType(dict(self.measures)))
        object.__setattr__(self, "member_row_refs", tuple(self.member_row_refs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_ref": self.group_ref,
            "key": dict(self.key),
            "measures": {key: value.to_dict() for key, value in self.measures.items()},
            "member_row_refs": list(self.member_row_refs),
            "rank": self.rank,
        }


@dataclass(frozen=True)
class Service1AnalysisResultSetV1:
    case_id: str
    analysis_id: str
    analysis_kind: AnalysisKind
    grain: Service1GrainV1
    groups: tuple[Service1ResultGroupV1, ...]
    source_sheet_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    applied_filters: tuple[Mapping[str, Any], ...]
    provenance: Mapping[str, Any]
    integrity: Service1IntegrityDigestV1
    schema_version: str = RESULT_SET_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        try:
            kind = self.analysis_kind if isinstance(self.analysis_kind, AnalysisKind) else AnalysisKind(self.analysis_kind)
        except (TypeError, ValueError) as exc:
            raise ValueError("analysis_kind must be a supported AnalysisKind") from exc
        object.__setattr__(self, "analysis_kind", kind)
        if not isinstance(self.grain, Service1GrainV1):
            raise TypeError("grain must be Service1GrainV1")
        if not self.groups:
            raise ValueError("groups must be non-empty")
        if not self.source_sheet_refs:
            raise ValueError("source_sheet_refs must be non-empty")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("result-set provenance cannot carry downstream authority")
        if not isinstance(self.integrity, Service1IntegrityDigestV1):
            raise TypeError("integrity must be Service1IntegrityDigestV1")
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "source_sheet_refs", tuple(dict.fromkeys(self.source_sheet_refs)))
        object.__setattr__(self, "relationship_refs", tuple(dict.fromkeys(self.relationship_refs)))
        object.__setattr__(self, "applied_filters", tuple(_freeze_json(dict(item)) for item in self.applied_filters))
        object.__setattr__(self, "provenance", _freeze_json(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            **_result_set_payload(self),
            "integrity": self.integrity.to_dict(),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1FindingV1:
    case_id: str
    finding_id: str
    category: str
    analysis_id: str
    group_ref: str
    entity_ref: str
    metric_ref: str
    observed_value: float
    unit: str
    currency_code: str | None
    rank: int | None
    classification: str | None
    severity: str | None
    financial_impact: Service1FinancialImpactV1 | None
    evidence_chain: Service1EvidenceChainV1
    limitations: tuple[str, ...]
    provenance: Mapping[str, Any]
    integrity: Service1IntegrityDigestV1
    schema_version: str = FINDING_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("case_id", "finding_id", "category", "analysis_id", "group_ref", "entity_ref", "metric_ref", "unit"):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        if isinstance(self.observed_value, bool) or not isinstance(self.observed_value, (int, float)) or not math.isfinite(float(self.observed_value)):
            raise ValueError("observed_value must be a finite number")
        if self.currency_code is not None:
            currency = str(self.currency_code).strip().upper()
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError("currency_code must be a three-letter alphabetic code")
            object.__setattr__(self, "currency_code", currency)
        if self.rank is not None and self.rank <= 0:
            raise ValueError("rank must be positive")
        if self.financial_impact is not None and not isinstance(self.financial_impact, Service1FinancialImpactV1):
            raise TypeError("financial_impact must be Service1FinancialImpactV1 or None")
        if not isinstance(self.evidence_chain, Service1EvidenceChainV1):
            raise TypeError("evidence_chain must be Service1EvidenceChainV1")
        if not self.limitations or any(not str(value).strip() for value in self.limitations):
            raise ValueError("limitations must be non-empty")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("finding provenance cannot carry downstream authority")
        if not isinstance(self.integrity, Service1IntegrityDigestV1):
            raise TypeError("integrity must be Service1IntegrityDigestV1")
        object.__setattr__(self, "limitations", tuple(self.limitations))
        object.__setattr__(self, "provenance", _freeze_json(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            **_finding_payload(self),
            "integrity": self.integrity.to_dict(),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
            "recommendation_generated": False,
            "severity_assigned": False,
            "financial_impact_inferred": False,
        }


@dataclass(frozen=True)
class Service1BoundedAnalysisOutcomeV1:
    outcome_id: str
    analysis_id: str
    finding_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    provenance: Mapping[str, Any]
    schema_version: str = OUTCOME_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.outcome_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("outcome_id and analysis_id are required")
        if not self.finding_refs or any(not str(ref).strip() for ref in self.finding_refs):
            raise ValueError("finding_refs must be non-empty")
        if not self.limitations or not self.forbidden_claims:
            raise ValueError("limitations and forbidden_claims must be non-empty")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("outcome provenance cannot carry downstream authority")
        object.__setattr__(self, "finding_refs", tuple(self.finding_refs))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        object.__setattr__(self, "forbidden_claims", tuple(self.forbidden_claims))
        object.__setattr__(self, "provenance", _freeze_json(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "outcome_id": self.outcome_id,
            "analysis_id": self.analysis_id,
            "finding_refs": list(self.finding_refs),
            "limitations": list(self.limitations),
            "forbidden_claims": list(self.forbidden_claims),
            "causal_diagnosis_generated": False,
            "recommendations_generated": False,
            "severity_assigned": False,
            "financial_impact_inferred": False,
            "provenance": _thaw_json(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1AnalysisResultProjectionV1:
    result_set: Service1AnalysisResultSetV1
    findings: tuple[Service1FindingV1, ...]
    outcome: Service1BoundedAnalysisOutcomeV1

    def __post_init__(self) -> None:
        if not isinstance(self.result_set, Service1AnalysisResultSetV1):
            raise TypeError("result_set must be Service1AnalysisResultSetV1")
        if not self.findings or any(not isinstance(value, Service1FindingV1) for value in self.findings):
            raise TypeError("findings must contain Service1FindingV1")
        if not isinstance(self.outcome, Service1BoundedAnalysisOutcomeV1):
            raise TypeError("outcome must be Service1BoundedAnalysisOutcomeV1")
        if tuple(item.finding_id for item in self.findings) != self.outcome.finding_refs:
            raise ValueError("outcome finding_refs must match findings exactly")
        object.__setattr__(self, "findings", tuple(self.findings))

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_set": self.result_set.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "outcome": self.outcome.to_dict(),
        }


@dataclass(frozen=True)
class Service1AnalysisResultProjectionDecisionV1:
    case_id: str
    analysis_id: str
    status: str
    reason: str | None
    projection: Service1AnalysisResultProjectionV1 | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if self.status not in {STATUS_READY, STATUS_BLOCKED}:
            raise ValueError("invalid result projection status")
        if self.status == STATUS_READY and self.projection is None:
            raise ValueError("RESULT_PROJECTION_READY requires projection")
        if self.status != STATUS_READY and self.projection is not None:
            raise ValueError("blocked decision cannot carry projection")
        if self.status == STATUS_READY and self.reason is not None:
            raise ValueError("ready decision cannot carry reason")
        if self.status == STATUS_BLOCKED and not str(self.reason or "").strip():
            raise ValueError("blocked decision requires reason")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        object.__setattr__(self, "provenance", _freeze_json(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "reason": self.reason,
            "projection": self.projection.to_dict() if self.projection else None,
            "provenance": _thaw_json(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


def build_service_1_analysis_result_projection_v1(
    *,
    math_result: Service1AnalysisMathResultV1,
    prepared_evidence: Service1PreparedAnalysisEvidenceV1,
    currency_code: str | None = None,
) -> Service1AnalysisResultProjectionDecisionV1:
    """Project F8 result into typed F9 ResultSet/findings without new business inference."""
    if not isinstance(math_result, Service1AnalysisMathResultV1):
        raise TypeError("math_result must be Service1AnalysisMathResultV1")
    if not isinstance(prepared_evidence, Service1PreparedAnalysisEvidenceV1):
        raise TypeError("prepared_evidence must be Service1PreparedAnalysisEvidenceV1")
    case_id = math_result.case_id
    analysis_id = math_result.analysis_id
    if prepared_evidence.case_id != case_id:
        return _blocked(case_id, analysis_id, "CASE_ID_DRIFT")
    if prepared_evidence.analysis_id != analysis_id:
        return _blocked(case_id, analysis_id, "ANALYSIS_ID_DRIFT")
    currency, currency_error = _currency_code(currency_code)
    if currency_error is not None:
        return _blocked(case_id, analysis_id, currency_error)

    plan = prepared_evidence.analysis_plan
    prepared_groups = {group.group_ref: group for group in prepared_evidence.groups}
    prepared_rows = {row.row_ref: row for row in prepared_evidence.prepared_rows}
    if len(prepared_groups) != len(prepared_evidence.groups):
        return _blocked(case_id, analysis_id, "DUPLICATE_PREPARED_GROUP_REF")
    if len(prepared_rows) != len(prepared_evidence.prepared_rows):
        return _blocked(case_id, analysis_id, "DUPLICATE_PREPARED_ROW_REF")

    result_groups: list[Service1ResultGroupV1] = []
    findings: list[Service1FindingV1] = []
    seen_result_group_refs: set[str] = set()
    for executed_group in math_result.groups:
        drift = _validate_executed_group(
            executed_group=executed_group,
            prepared_groups=prepared_groups,
            expected_measures=plan.measures,
        )
        if drift is not None:
            return _blocked(case_id, analysis_id, drift)
        if executed_group.group_ref in seen_result_group_refs:
            return _blocked(case_id, analysis_id, "DUPLICATE_RESULT_GROUP_REF")
        seen_result_group_refs.add(executed_group.group_ref)

        projected_measures: dict[str, Service1ResultMeasureV1] = {}
        for measure_ref, executed_measure in executed_group.measures.items():
            measure_currency = currency if executed_measure.unit == "currency" else None
            projected_measures[measure_ref] = Service1ResultMeasureV1(
                measure_ref=measure_ref,
                value=executed_measure.value,
                unit=executed_measure.unit,
                currency_code=measure_currency,
                formula_ref=executed_measure.formula_ref,
                source_refs=executed_measure.source_refs,
            )
            finding = _build_finding(
                case_id=case_id,
                analysis_id=analysis_id,
                analysis_kind=plan.kind,
                executed_group=executed_group,
                executed_measure=executed_measure,
                prepared_rows=prepared_rows,
                currency_code=measure_currency,
            )
            findings.append(finding)
        result_groups.append(
            Service1ResultGroupV1(
                group_ref=executed_group.group_ref,
                key=executed_group.key,
                measures=projected_measures,
                member_row_refs=executed_group.member_row_refs,
                rank=executed_group.rank,
            )
        )

    result_payload = {
        "schema_version": RESULT_SET_SCHEMA_VERSION,
        "case_id": case_id,
        "analysis_id": analysis_id,
        "analysis_kind": plan.kind.value,
        "grain": prepared_evidence.grain.to_dict(),
        "groups": [group.to_dict() for group in result_groups],
        "source_sheet_refs": list(prepared_evidence.source_sheet_refs),
        "relationship_refs": [item.relationship_ref for item in prepared_evidence.materialized_relationships],
        "applied_filters": [dict(item) for item in prepared_evidence.applied_filters],
        "provenance": {
            "source": "F8_MATH_RESULT_PLUS_F7_PREPARED_EVIDENCE",
            "result_projection_runtime": "F9",
            "finding_generation_kind": "BOUNDED_FACTUAL_OBSERVATION",
            "financial_impact_policy_applied": False,
            "severity_policy_applied": False,
        },
    }
    result_integrity = _integrity(result_payload, INTEGRITY_SCOPE_RESULT_SET)
    result_set = Service1AnalysisResultSetV1(
        case_id=case_id,
        analysis_id=analysis_id,
        analysis_kind=plan.kind,
        grain=prepared_evidence.grain,
        groups=tuple(result_groups),
        source_sheet_refs=prepared_evidence.source_sheet_refs,
        relationship_refs=tuple(item.relationship_ref for item in prepared_evidence.materialized_relationships),
        applied_filters=prepared_evidence.applied_filters,
        provenance=result_payload["provenance"],
        integrity=result_integrity,
    )

    finding_refs = tuple(item.finding_id for item in findings)
    outcome_id = "outcome:" + _digest(
        {
            "case_id": case_id,
            "analysis_id": analysis_id,
            "finding_refs": list(finding_refs),
            "limitations": list(_GENERIC_LIMITATIONS),
            "forbidden_claims": list(_GENERIC_FORBIDDEN_CLAIMS),
        }
    )[:24]
    outcome = Service1BoundedAnalysisOutcomeV1(
        outcome_id=outcome_id,
        analysis_id=analysis_id,
        finding_refs=finding_refs,
        limitations=_GENERIC_LIMITATIONS,
        forbidden_claims=_GENERIC_FORBIDDEN_CLAIMS,
        provenance={
            "source": "F9_BOUNDED_RESULT_PROJECTION",
            "causal_policy_applied": False,
            "recommendation_policy_applied": False,
            "financial_impact_policy_applied": False,
            "severity_policy_applied": False,
        },
    )
    projection = Service1AnalysisResultProjectionV1(
        result_set=result_set,
        findings=tuple(findings),
        outcome=outcome,
    )
    return Service1AnalysisResultProjectionDecisionV1(
        case_id=case_id,
        analysis_id=analysis_id,
        status=STATUS_READY,
        reason=None,
        projection=projection,
        provenance={"source": "F9_ANALYSIS_RESULT_PROJECTION"},
    )


def verify_service_1_finding_integrity_v1(finding: Service1FindingV1) -> bool:
    if not isinstance(finding, Service1FindingV1):
        raise TypeError("finding must be Service1FindingV1")
    return finding.integrity.digest == _digest(_finding_payload(finding))


def verify_service_1_result_set_integrity_v1(result_set: Service1AnalysisResultSetV1) -> bool:
    if not isinstance(result_set, Service1AnalysisResultSetV1):
        raise TypeError("result_set must be Service1AnalysisResultSetV1")
    return result_set.integrity.digest == _digest(_result_set_payload(result_set))


def _validate_executed_group(
    *,
    executed_group: Service1ExecutedGroupV1,
    prepared_groups: Mapping[str, Any],
    expected_measures: tuple[str, ...],
) -> str | None:
    if not isinstance(executed_group, Service1ExecutedGroupV1):
        return "INVALID_F8_GROUP"
    prepared_group = prepared_groups.get(executed_group.group_ref)
    if prepared_group is None:
        return f"RESULT_GROUP_NOT_IN_F7:{executed_group.group_ref}"
    if dict(executed_group.key) != dict(prepared_group.key):
        return f"RESULT_GROUP_KEY_DRIFT:{executed_group.group_ref}"
    if tuple(executed_group.member_row_refs) != tuple(prepared_group.member_row_refs):
        return f"RESULT_GROUP_MEMBERSHIP_DRIFT:{executed_group.group_ref}"
    if tuple(executed_group.measures) != tuple(expected_measures):
        return f"RESULT_MEASURE_SET_DRIFT:{executed_group.group_ref}"
    for measure_ref, measure in executed_group.measures.items():
        if not isinstance(measure, Service1ExecutedMeasureV1) or measure.measure_ref != measure_ref:
            return f"RESULT_MEASURE_IDENTITY_DRIFT:{executed_group.group_ref}:{measure_ref}"
    return None


def _build_finding(
    *,
    case_id: str,
    analysis_id: str,
    analysis_kind: AnalysisKind,
    executed_group: Service1ExecutedGroupV1,
    executed_measure: Service1ExecutedMeasureV1,
    prepared_rows: Mapping[str, Any],
    currency_code: str | None,
) -> Service1FindingV1:
    relationship_refs: list[str] = []
    for row_ref in executed_group.member_row_refs:
        row = prepared_rows.get(row_ref)
        if row is None:
            raise ValueError(f"prepared row missing for finding evidence chain: {row_ref}")
        relationship_refs.extend(row.relationship_refs)
    evidence_chain = Service1EvidenceChainV1(
        source_refs=executed_measure.source_refs,
        member_row_refs=executed_group.member_row_refs,
        relationship_refs=tuple(dict.fromkeys(relationship_refs)),
        formula_ref=executed_measure.formula_ref,
        math_trace=executed_measure.math_trace,
    )
    category = "RANKED_ANALYTICAL_RESULT" if executed_group.rank is not None else "ANALYTICAL_RESULT"
    entity_ref = _entity_ref(executed_group.key)
    identity_payload = {
        "case_id": case_id,
        "analysis_id": analysis_id,
        "group_ref": executed_group.group_ref,
        "metric_ref": executed_measure.measure_ref,
        "observed_value": float(executed_measure.value),
        "unit": executed_measure.unit,
        "formula_ref": executed_measure.formula_ref,
        "rank": executed_group.rank,
    }
    finding_id = "finding:" + _digest(identity_payload)[:24]
    limitations = list(_GENERIC_LIMITATIONS)
    if executed_measure.unit == "currency" and currency_code is None:
        limitations.append("The measure is monetary, but no currency code was supplied to F9; no currency code or financial impact is inferred.")
    base_payload = {
        "schema_version": FINDING_SCHEMA_VERSION,
        "case_id": case_id,
        "finding_id": finding_id,
        "category": category,
        "analysis_id": analysis_id,
        "group_ref": executed_group.group_ref,
        "entity_ref": entity_ref,
        "metric_ref": executed_measure.measure_ref,
        "observed_value": float(executed_measure.value),
        "unit": executed_measure.unit,
        "currency_code": currency_code,
        "rank": executed_group.rank,
        "classification": None,
        "severity": None,
        "financial_impact": None,
        "evidence_chain": evidence_chain.to_dict(),
        "limitations": limitations,
        "provenance": {
            "source": "F8_EXECUTED_MEASURE_PLUS_F7_EVIDENCE_CHAIN",
            "analysis_kind": analysis_kind.value,
            "classification_policy_applied": False,
            "severity_policy_applied": False,
            "financial_impact_policy_applied": False,
        },
    }
    integrity = _integrity(base_payload, INTEGRITY_SCOPE_FINDING)
    return Service1FindingV1(
        case_id=case_id,
        finding_id=finding_id,
        category=category,
        analysis_id=analysis_id,
        group_ref=executed_group.group_ref,
        entity_ref=entity_ref,
        metric_ref=executed_measure.measure_ref,
        observed_value=executed_measure.value,
        unit=executed_measure.unit,
        currency_code=currency_code,
        rank=executed_group.rank,
        classification=None,
        severity=None,
        financial_impact=None,
        evidence_chain=evidence_chain,
        limitations=tuple(limitations),
        provenance=base_payload["provenance"],
        integrity=integrity,
    )


def _finding_payload(finding: Service1FindingV1) -> dict[str, Any]:
    return {
        "schema_version": finding.schema_version,
        "case_id": finding.case_id,
        "finding_id": finding.finding_id,
        "category": finding.category,
        "analysis_id": finding.analysis_id,
        "group_ref": finding.group_ref,
        "entity_ref": finding.entity_ref,
        "metric_ref": finding.metric_ref,
        "observed_value": float(finding.observed_value),
        "unit": finding.unit,
        "currency_code": finding.currency_code,
        "rank": finding.rank,
        "classification": finding.classification,
        "severity": finding.severity,
        "financial_impact": finding.financial_impact.to_dict() if finding.financial_impact else None,
        "evidence_chain": finding.evidence_chain.to_dict(),
        "limitations": list(finding.limitations),
        "provenance": _thaw_json(finding.provenance),
    }


def _result_set_payload(result_set: Service1AnalysisResultSetV1) -> dict[str, Any]:
    return {
        "schema_version": result_set.schema_version,
        "case_id": result_set.case_id,
        "analysis_id": result_set.analysis_id,
        "analysis_kind": result_set.analysis_kind.value,
        "grain": result_set.grain.to_dict(),
        "groups": [group.to_dict() for group in result_set.groups],
        "source_sheet_refs": list(result_set.source_sheet_refs),
        "relationship_refs": list(result_set.relationship_refs),
        "applied_filters": [_thaw_json(item) for item in result_set.applied_filters],
        "provenance": _thaw_json(result_set.provenance),
    }


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _integrity(payload: Mapping[str, Any], scope: str) -> Service1IntegrityDigestV1:
    return Service1IntegrityDigestV1(
        algorithm="SHA-256",
        digest=_digest(payload),
        scope=scope,
        authenticity_asserted=False,
        non_repudiation_asserted=False,
    )


def _digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _currency_code(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    currency = str(value).strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        return None, "CURRENCY_CODE_INVALID"
    return currency, None


def _entity_ref(key: Mapping[str, str]) -> str:
    if not key:
        return "ALL"
    return "|".join(f"{name}={value}" for name, value in key.items())


def _blocked(case_id: str, analysis_id: str, reason: str) -> Service1AnalysisResultProjectionDecisionV1:
    return Service1AnalysisResultProjectionDecisionV1(
        case_id=case_id,
        analysis_id=analysis_id,
        status=STATUS_BLOCKED,
        reason=reason,
        provenance={"source": "F9_ANALYSIS_RESULT_PROJECTION"},
    )


__all__ = [
    "SCHEMA_VERSION",
    "RESULT_SET_SCHEMA_VERSION",
    "FINDING_SCHEMA_VERSION",
    "OUTCOME_SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "Service1IntegrityDigestV1",
    "Service1FinancialImpactV1",
    "Service1EvidenceChainV1",
    "Service1ResultMeasureV1",
    "Service1ResultGroupV1",
    "Service1AnalysisResultSetV1",
    "Service1FindingV1",
    "Service1BoundedAnalysisOutcomeV1",
    "Service1AnalysisResultProjectionV1",
    "Service1AnalysisResultProjectionDecisionV1",
    "build_service_1_analysis_result_projection_v1",
    "verify_service_1_finding_integrity_v1",
    "verify_service_1_result_set_integrity_v1",
]
