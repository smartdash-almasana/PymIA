from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pymia.smartpyme.service_1_capability_registry_v1 import (
    get_capability_definition_v1,
    list_capability_refs_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    VARIABLE_FAMILY_DEFINITIONS,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_REMAINING_CAPABILITY_GOVERNANCE_CONVERGENCE_AUDIT_V1"
VERDICT_CONVERGED: Final[str] = "CONVERGED"
VERDICT_GAPS: Final[str] = "GOVERNANCE_GAPS_REMAIN"

CERTIFIED_PHYSICAL: Final[frozenset[str]] = frozenset({
    "sold_vs_collected_gap",
    "projected_closing_cash_balance",
    "dso",
})


def evaluate_service_1_remaining_capability_governance_convergence_audit_v1(
    root: Path | None = None,
) -> dict:
    repo = root or Path(__file__).resolve().parents[1]
    formula_catalog = json.loads((repo / "docs/formula_catalog.v1.json").read_text(encoding="utf-8"))
    pathology_catalog = json.loads((repo / "docs/pathology_catalog.enriched.v2.json").read_text(encoding="utf-8"))
    matrix = json.loads((repo / "docs/service_1_formula_pathology_evidence_matrix.v2.json").read_text(encoding="utf-8"))

    formulas_by_pair = {
        (str(row.get("pathology_code") or ""), str(row.get("formula_id") or "")): row
        for row in formula_catalog.get("formulas", [])
        if isinstance(row, dict)
    }
    formulas_by_pathology = {}
    for row in formula_catalog.get("formulas", []):
        if isinstance(row, dict):
            formulas_by_pathology.setdefault(str(row.get("pathology_code") or ""), []).append(row)

    pathology_codes = {
        str(row.get("pathology_code") or "")
        for row in pathology_catalog.get("pathologies", [])
        if isinstance(row, dict)
    }
    p7_by_capability = {
        capability: definition.family_id
        for definition in VARIABLE_FAMILY_DEFINITIONS
        for capability in definition.target_capabilities
    }
    matrix_by_capability = {
        capability: row
        for row in matrix.get("entries", [])
        if isinstance(row, dict)
        for capability in row.get("capability_refs", [])
    }

    rows: list[dict] = []
    for capability in list_capability_refs_v1():
        definition = get_capability_definition_v1(capability)
        if definition is None:
            continue
        exact_formula = formulas_by_pair.get((definition.pathology_code, definition.formula_ref))
        same_pathology = formulas_by_pathology.get(definition.pathology_code, [])
        catalog_formula_ids = [str(row.get("formula_id") or "") for row in same_pathology]
        calculation_states = sorted({str(row.get("calculation_state") or "") for row in same_pathology if row.get("calculation_state")})
        p7_family = p7_by_capability.get(capability)
        matrix_entry = matrix_by_capability.get(capability)
        pathology_present = definition.pathology_code in pathology_codes
        fully_governed = bool(exact_formula and p7_family and matrix_entry and pathology_present)
        if definition.kind == "COMPOSITE":
            # Composite execution is registry/result governed, but still depends on
            # its prerequisite capabilities being independently governed.
            fully_governed = bool(exact_formula and pathology_present)
        rows.append({
            "capability": capability,
            "kind": definition.kind,
            "pathology_code": definition.pathology_code,
            "registry_formula_ref": definition.formula_ref,
            "registry_variables": [variable.name for variable in definition.variables],
            "exact_formula_in_catalog": exact_formula is not None,
            "catalog_formula_ids_for_pathology": catalog_formula_ids,
            "catalog_calculation_states": calculation_states,
            "pathology_in_enriched_catalog": pathology_present,
            "p7_family": p7_family,
            "p7_governed": p7_family is not None,
            "p8_matrix_governed": matrix_entry is not None,
            "physical_positive_certified": capability in CERTIFIED_PHYSICAL,
            "fully_governed_for_physical_p8": fully_governed,
        })

    gaps = [row for row in rows if not row["physical_positive_certified"] and not row["fully_governed_for_physical_p8"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_CONVERGED if not gaps else VERDICT_GAPS,
        "registry_capabilities": len(rows),
        "physical_positive_certified": sum(bool(row["physical_positive_certified"]) for row in rows),
        "remaining_governance_gaps": len(gaps),
        "rows": rows,
        "gap_capabilities": [row["capability"] for row in gaps],
        "scope_fixed": bool((pathology_catalog.get("scope_policy") or {}).get("scope_fixed")),
        "scope_not_reopened": bool((pathology_catalog.get("scope_policy") or {}).get("scope_not_reopened")),
        "runtime_authorized": False,
        "delivery_authorized": False,
        "product_ready": False,
    }


def main() -> int:
    result = evaluate_service_1_remaining_capability_governance_convergence_audit_v1()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
