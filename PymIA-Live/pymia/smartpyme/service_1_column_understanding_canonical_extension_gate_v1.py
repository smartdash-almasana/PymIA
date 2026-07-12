"""Service 1 — Canonical Extension Gate V1.

Pure gate for proposed column-understanding semantic extensions.
It does not mutate catalogs and does not authorize runtime/frontend wiring.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_CANONICAL_EXTENSION_GATE_V1"
STATUS_READY: Final[str] = "CANONICAL_EXTENSION_GATE_READY"
SUPPORTED: Final[str] = "SUPPORTED"
PARTIAL: Final[str] = "PARTIAL"
BLOCKED: Final[str] = "BLOCKED"

_GAP_TERMS: Final[dict[str, tuple[str, ...]]] = {
    "stock_inicial": ("stock", "inventory", "initial"),
    "entradas": ("stock", "inventory", "incoming", "purchases"),
    "salidas": ("stock", "inventory", "outgoing", "sales"),
    "stock_final": ("stock", "inventory", "closing"),
    "cliente": ("client", "customer"),
    "medio_pago": ("payment", "cash", "collection"),
    "proveedor": ("supplier", "vendor", "payable"),
    "bonif": ("discount", "rebate", "bonus"),
}


@dataclass(frozen=True)
class Service1CanonicalExtensionCandidateV1:
    column_name: str
    status: str
    matching_variables: tuple[str, ...]
    supporting_formula_ids: tuple[str, ...]
    blocking_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1CanonicalExtensionGateV1:
    schema_version: str
    status: str
    candidates: tuple[Service1CanonicalExtensionCandidateV1, ...]
    supported_count: int
    partial_count: int
    blocked_count: int
    catalog_mutation_authorized: bool = False
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_column_understanding_canonical_extension_gate_v1(
    *, repo_root: Path | None = None,
) -> Service1CanonicalExtensionGateV1:
    root = repo_root or Path(__file__).resolve().parents[3]
    variable_path = root / "PymIA-Live/docs/service_1_semantic_variable_catalog.v1.json"
    formula_path = root / "PymIA-Live/docs/formula_catalog.v1.json"

    variable_catalog = json.loads(variable_path.read_text(encoding="utf-8"))
    formula_catalog = json.loads(formula_path.read_text(encoding="utf-8"))

    variable_names = tuple(
        sorted(variable["variable_name"] for variable in variable_catalog["variables"])
    )
    formulas = tuple(formula_catalog["formulas"])

    candidates: list[Service1CanonicalExtensionCandidateV1] = []
    for column_name, terms in _GAP_TERMS.items():
        matching_variables = tuple(
            variable_name
            for variable_name in variable_names
            if any(term in variable_name.casefold() for term in terms)
        )
        supporting_formula_ids = tuple(
            sorted(
                formula["formula_id"]
                for formula in formulas
                if set(formula.get("required_variables", ())) & set(matching_variables)
            )
        )

        if matching_variables and supporting_formula_ids:
            status = PARTIAL
            blocking_reason = (
                "Canonical variables and formulas exist, but they do not prove that the "
                "specific spreadsheet column is equivalent to any one variable."
            )
        elif matching_variables:
            status = PARTIAL
            blocking_reason = (
                "Lexically related canonical variables exist, but no supporting formula "
                "establishes a usable semantic binding for this column."
            )
        else:
            status = BLOCKED
            blocking_reason = (
                "No canonical variable derived from formula required_variables supports "
                "this concept. Add formula/catalog evidence before proposing a mapping."
            )

        candidates.append(
            Service1CanonicalExtensionCandidateV1(
                column_name=column_name,
                status=status,
                matching_variables=matching_variables,
                supporting_formula_ids=supporting_formula_ids,
                blocking_reason=blocking_reason,
            )
        )

    return Service1CanonicalExtensionGateV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_READY,
        candidates=tuple(candidates),
        supported_count=sum(item.status == SUPPORTED for item in candidates),
        partial_count=sum(item.status == PARTIAL for item in candidates),
        blocked_count=sum(item.status == BLOCKED for item in candidates),
        catalog_mutation_authorized=False,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        metadata={
            "derivation_rule": variable_catalog.get("derivation_rule"),
            "variable_catalog_status": variable_catalog.get("status"),
            "observational_only": True,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "SUPPORTED",
    "PARTIAL",
    "BLOCKED",
    "Service1CanonicalExtensionCandidateV1",
    "Service1CanonicalExtensionGateV1",
    "build_service_1_column_understanding_canonical_extension_gate_v1",
]
