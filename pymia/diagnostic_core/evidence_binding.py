from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence

from .models import DiagnosticCoreInput


@lru_cache(maxsize=1)
def _load_formula_variable_aliases() -> dict[str, dict[str, list[str]]]:
    catalog_path = Path(__file__).resolve().parents[1] / "contracts" / "formula_aliases_v1.json"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    aliases_by_formula = data.get("aliases_by_formula")
    if not isinstance(aliases_by_formula, dict):
        return {}

    clean: dict[str, dict[str, list[str]]] = {}
    for formula_id, variable_aliases in aliases_by_formula.items():
        if not isinstance(formula_id, str) or not isinstance(variable_aliases, dict):
            continue
        clean_variables: dict[str, list[str]] = {}
        for variable_name, aliases in variable_aliases.items():
            if not isinstance(variable_name, str) or not isinstance(aliases, list):
                continue
            clean_aliases = [str(alias) for alias in aliases if str(alias).strip()]
            if clean_aliases:
                clean_variables[variable_name] = clean_aliases
        if clean_variables:
            clean[formula_id] = clean_variables
    return clean


def build_diagnostic_core_input_from_structured_evidence(
    evidence: StructuredEvidence,
    *,
    case_id: str,
    tenant_id: str,
    formula_ids: list[str],
    hypothesis_codes: list[str] | None = None,
) -> DiagnosticCoreInput:
    computed = evidence.computed_variables or {}
    variables: dict[str, float | int | None] = {}
    evidence_refs: dict[str, list[str]] = {}
    aliases_by_formula = _load_formula_variable_aliases()

    for formula_id in formula_ids:
        for target_name, aliases in aliases_by_formula.get(formula_id, {}).items():
            value, matched_alias = _pick_first_available(computed, aliases)
            if value is None:
                continue
            variables[target_name] = value
            refs = _source_refs_for(evidence, target_name, matched_alias)
            if refs:
                evidence_refs[target_name] = refs

    return DiagnosticCoreInput(
        case_id=case_id,
        tenant_id=tenant_id,
        hypothesis_codes=hypothesis_codes or [],
        formula_ids=formula_ids,
        variables=variables,
        evidence_refs=evidence_refs,
        evidence_status="STRUCTURED_EVIDENCE_BOUND",
        metadata={
            "binding_source": "StructuredEvidence.computed_variables",
            "formula_aliases_source": "pymia/contracts/formula_aliases_v1.json",
            "document_type": evidence.document_type,
            "file_name": evidence.file_name,
        },
    )


def _pick_first_available(
    computed: dict[str, float],
    aliases: list[str],
) -> tuple[float | int | None, str | None]:
    for alias in aliases:
        if alias in computed and computed[alias] is not None:
            return computed[alias], alias
    return None, None


def _source_refs_for(
    evidence: StructuredEvidence,
    canonical_name: str,
    matched_alias: str | None,
) -> list[str]:
    if not matched_alias:
        return []

    metadata = evidence.metadata or {}
    variable_refs = metadata.get("variable_source_refs")
    if isinstance(variable_refs, dict):
        for key in (canonical_name, matched_alias):
            refs = variable_refs.get(key)
            if isinstance(refs, list):
                clean_refs = [str(ref) for ref in refs if str(ref).strip()]
                if clean_refs:
                    return clean_refs

    file_name = evidence.file_name or "structured_evidence"
    return [f"{file_name}:{matched_alias}"]
