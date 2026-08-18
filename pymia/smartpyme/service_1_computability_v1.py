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

SCHEMA_VERSION = "SERVICE_1_COMPUTABILITY_V1"
STATUS_COMPUTABLE = "COMPUTABLE"
STATUS_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
STATUS_UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
STATUS_BLOCKED = "BLOCKED"
ALLOWED_STATUSES = frozenset({STATUS_COMPUTABLE, STATUS_NEEDS_EVIDENCE, STATUS_UNSUPPORTED_CAPABILITY, STATUS_BLOCKED})
_ALLOWED_CATALOG_LOAD_STATUSES = {STATUS_CATALOGS_LOADED, STATUS_CATALOGS_PARTIALLY_LOADED}


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
        forbidden = {"runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated"}
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
    "SCHEMA_VERSION", "STATUS_COMPUTABLE", "STATUS_NEEDS_EVIDENCE", "STATUS_UNSUPPORTED_CAPABILITY", "STATUS_BLOCKED",
    "Service1ComputabilityDecisionV1", "Service1GovernedComputationInputV1", "build_service_1_computability_decision_v1",
    "build_service_1_composite_governed_computation_input_v1",
]
