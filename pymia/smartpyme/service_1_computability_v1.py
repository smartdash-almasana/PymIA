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
    source_bindings: Mapping[str, str]
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
    if str(match.get("status") or "") != "REQUIREMENT_MATCHED":
        missing = tuple(tuple(group) for group in (match.get("missing_role_groups") or ()))
        return _decision(case, capability, STATUS_NEEDS_EVIDENCE, "REQUIREMENTS_NOT_MATCHED", family_id=family_id, missing=missing)

    source_by_variable = {
        str(item.get("approved_variable") or "").strip(): str(item.get("column_ref") or "").strip()
        for item in decisions
        if str(item.get("approved_variable") or "").strip() and str(item.get("column_ref") or "").strip()
    }

    paths = _catalog_paths(formula_catalog_path, pathology_catalog_path, evidence_matrix_path)
    try:
        matrix = _load_json(paths["evidence_matrix"])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _decision(case, capability, STATUS_BLOCKED, f"EVIDENCE_MATRIX_INVALID:{exc}", family_id=family_id)
    if matrix.get("computation_candidate_planning_allowed") is not True:
        return _decision(case, capability, STATUS_BLOCKED, "MATRIX_COMPUTATION_PLANNING_NOT_ALLOWED", family_id=family_id)
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
    required = tuple(formula.required_variables)
    if tuple(str(v).strip() for v in entry.get("required_variables", []) if str(v).strip()) != required:
        return _decision(case, capability, STATUS_BLOCKED, "MATRIX_FORMULA_VARIABLE_DRIFT", family_id=family_id)
    if formula.calculation_state != "CALCULABLE":
        return _decision(case, capability, STATUS_NEEDS_EVIDENCE, "FORMULA_REQUIRES_ADDITIONAL_ASSUMPTIONS", family_id=family_id)
    missing_variables = tuple(v for v in required if v not in source_by_variable)
    if missing_variables:
        return _decision(case, capability, STATUS_NEEDS_EVIDENCE, "FORMULA_INPUTS_NOT_READY", family_id=family_id)

    versions = _catalog_versions(paths, matrix)
    governed = Service1GovernedComputationInputV1(
        case_id=case,
        requested_capability=capability,
        family_id=family_id or "",
        pathology_code=pathology_code,
        formula_id=formula.formula_id,
        formula_expression=formula.expression,
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
        provenance={"source": "P6_PLUS_P7_PLUS_GOVERNED_CATALOGS"},
    )


def _decision(case: str, capability: str, status: str, reason: str, *, family_id: str | None = None, missing: tuple[tuple[str, ...], ...] = ()) -> Service1ComputabilityDecisionV1:
    return Service1ComputabilityDecisionV1(case_id=case, requested_capability=capability, status=status, reason=reason, family_id=family_id, missing_role_groups=missing, provenance={"source": "P8_COMPUTABILITY"})


def _catalog_paths(formula_catalog_path: str | Path | None, pathology_catalog_path: str | Path | None, evidence_matrix_path: str | Path | None) -> dict[str, Path]:
    docs = Path(__file__).resolve().parents[2] / "docs"
    return {
        "formula_catalog": Path(formula_catalog_path) if formula_catalog_path else docs / "formula_catalog.v1.json",
        "pathology_catalog": Path(pathology_catalog_path) if pathology_catalog_path else docs / "pathology_catalog.enriched.v1.json",
        "evidence_matrix": Path(evidence_matrix_path) if evidence_matrix_path else docs / "service_1_formula_pathology_evidence_matrix.v1.json",
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise OSError(f"file_not_found:{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_root_not_object:{path}")
    return payload


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
]
