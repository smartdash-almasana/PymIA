"""Deterministic variable-family binding for Servicio 1.

This module groups semantic column candidates into business-capability families.
It does not infer new column meanings, execute tools, select diagnoses, or
authorize runtime. It only reports which coherent variable families are ready,
incomplete, ambiguous or absent.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_VARIABLE_FAMILY_BINDINGS_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

FAMILY_OPERATION_CORE: Final[str] = "OPERATION_CORE"
FAMILY_SALES_MARGIN: Final[str] = "SALES_MARGIN"
FAMILY_CASH_COLLECTIONS: Final[str] = "CASH_COLLECTIONS"
FAMILY_PURCHASES_SUPPLIERS: Final[str] = "PURCHASES_SUPPLIERS"
FAMILY_INVENTORY_CONTROL: Final[str] = "INVENTORY_CONTROL"
FAMILY_CASH_PROJECTION: Final[str] = "CASH_PROJECTION"
FAMILY_RECEIVABLES_DSO: Final[str] = "RECEIVABLES_DSO"

STATUS_READY: Final[str] = "VARIABLE_FAMILY_READY"
STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "VARIABLE_FAMILY_NEEDS_OWNER_CONFIRMATION"
STATUS_MISSING_REQUIRED_ROLES: Final[str] = "VARIABLE_FAMILY_MISSING_REQUIRED_ROLES"
STATUS_NOT_OBSERVED: Final[str] = "VARIABLE_FAMILY_NOT_OBSERVED"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_READY,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_MISSING_REQUIRED_ROLES,
    STATUS_NOT_OBSERVED,
)


@dataclass(frozen=True)
class Service1VariableFamilyDefinitionV1:
    family_id: str
    owner_label: str
    priority: int
    required_role_groups: tuple[tuple[str, ...], ...]
    optional_roles: tuple[str, ...]
    target_variable_names: tuple[str, ...]
    target_capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.family_id.strip():
            raise ValueError("family_id is required")
        if not self.owner_label.strip():
            raise ValueError("owner_label is required")
        if self.priority < 1:
            raise ValueError("priority must be >= 1")
        if not self.required_role_groups:
            raise ValueError("required_role_groups must not be empty")
        for group in self.required_role_groups:
            if not group or any(not str(role).strip() for role in group):
                raise ValueError("every required role group must contain roles")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1VariableFamilyBindingV1:
    schema_version: str
    service_name: str
    family_id: str
    owner_label: str
    priority: int
    status: str
    coverage_ratio: float
    required_role_groups: tuple[tuple[str, ...], ...]
    satisfied_role_groups: tuple[tuple[str, ...], ...]
    missing_role_groups: tuple[tuple[str, ...], ...]
    ambiguous_role_groups: tuple[tuple[str, ...], ...]
    bound_roles: tuple[str, ...]
    ambiguous_roles: tuple[str, ...]
    optional_roles_present: tuple[str, ...]
    source_columns: tuple[str, ...]
    target_variable_names: tuple[str, ...]
    target_capabilities: tuple[str, ...]
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported family binding status: {self.status}")
        if self.coverage_ratio < 0 or self.coverage_ratio > 1:
            raise ValueError("coverage_ratio must be between 0 and 1")
        for field_name in (
            "runtime_authorized",
            "tool_execution_authorized",
            "delivery_authorized",
            "diagnosis_generated",
        ):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain False")
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


VARIABLE_FAMILY_DEFINITIONS: Final[tuple[Service1VariableFamilyDefinitionV1, ...]] = (
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_OPERATION_CORE,
        owner_label="Operación comercial básica",
        priority=1,
        required_role_groups=(("operation_date",), ("product_identifier", "product_name"), ("quantity",), ("sales_amount",)),
        optional_roles=("document_reference", "sales_channel", "commercial_category"),
        target_variable_names=("operation_date", "document_ref", "product_id_or_name", "quantity", "sold_amount", "customer", "sales_channel"),
        target_capabilities=("reconstruct_transactions", "group_sales_by_product_and_period", "detect_duplicate_or_untraceable_operations"),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_SALES_MARGIN,
        owner_label="Venta, precio y margen",
        priority=2,
        required_role_groups=(("product_identifier", "product_name"), ("quantity",), ("unit_sale_price",), ("unit_cost_candidate",)),
        optional_roles=("sales_amount", "discount_amount", "tax_amount", "sales_channel", "commercial_category"),
        target_variable_names=("product_id_or_name", "quantity", "sale_price", "cost", "sold_amount", "discount", "taxes_and_commissions"),
        target_capabilities=("gross_margin", "markup", "price_cost_variation", "margin_by_product_or_segment"),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_CASH_COLLECTIONS,
        owner_label="Caja y cobranzas",
        priority=3,
        required_role_groups=(("operation_date",), ("sales_amount",), ("collected_amount",)),
        optional_roles=("accounts_receivable_amount", "document_reference", "initial_balance", "payment_method", "due_date"),
        target_variable_names=("operation_date", "sold_amount", "collected_amount", "accounts_receivable", "initial_balance", "payment_method", "due_date"),
        target_capabilities=("sold_vs_collected_gap", "receivables_visibility", "cash_flow_ordering", "collection_aging"),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_PURCHASES_SUPPLIERS,
        owner_label="Compras y proveedores",
        priority=4,
        required_role_groups=(("operation_date",), ("supplier_name",), ("product_identifier", "product_name"), ("purchase_amount",)),
        optional_roles=("paid_amount", "due_date", "payment_method", "document_reference", "unit_cost_candidate"),
        target_variable_names=("operation_date", "supplier", "product_id_or_name", "purchase_amount", "paid_amount", "due_date", "payment_method"),
        target_capabilities=("supplier_price_variation", "purchases_vs_payments", "supplier_dependency", "payment_due_visibility"),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_INVENTORY_CONTROL,
        owner_label="Stock e inventario",
        priority=5,
        required_role_groups=(("product_identifier", "product_name"), ("stock_current",), ("stock_minimum",)),
        optional_roles=("quantity", "average_daily_sales", "unit_cost_candidate", "operation_date"),
        target_variable_names=("product_id_or_name", "stock_current", "stock_minimum", "average_daily_sales", "cost"),
        target_capabilities=("low_stock_alert", "days_of_stock_remaining", "inventory_value_visibility", "reorder_evidence"),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_CASH_PROJECTION,
        owner_label="Proyección de caja",
        priority=6,
        required_role_groups=(("initial_balance",), ("expected_collections",), ("expected_payments",)),
        optional_roles=("operation_date", "due_date", "document_reference"),
        target_variable_names=("initial_balance", "expected_collections", "expected_payments"),
        target_capabilities=("projected_closing_cash_balance",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_RECEIVABLES_DSO,
        owner_label="Plazo de cuentas por cobrar",
        priority=7,
        required_role_groups=(("accounts_receivable_amount",), ("sales_amount",), ("period_days", "days")),
        optional_roles=("operation_date", "due_date", "document_reference", "customer_name"),
        target_variable_names=("accounts_receivable", "sales", "days"),
        target_capabilities=("dso",),
    ),
)


def build_service_1_variable_family_bindings_v1(
    column_candidates: tuple[Service1ColumnSemanticCandidateV1, ...] | list[Service1ColumnSemanticCandidateV1],
) -> tuple[Service1VariableFamilyBindingV1, ...]:
    """Resolve the canonical variable families from semantic candidates."""
    candidates = tuple(column_candidates or ())
    for candidate in candidates:
        if not isinstance(candidate, Service1ColumnSemanticCandidateV1):
            raise TypeError("column_candidates must contain Service1ColumnSemanticCandidateV1")

    resolved_role_columns: dict[str, list[str]] = {}
    ambiguous_role_columns: dict[str, list[str]] = {}
    for candidate in candidates:
        metadata = dict(candidate.metadata or {})
        if metadata.get("owner_ignored_not_relevant"):
            continue
        roles = tuple(role for role in candidate.candidate_semantic_roles if role and role != "unknown")
        if not roles:
            continue
        source_column = candidate.source_column_name
        if candidate.owner_confirmation_required:
            for role in roles:
                _append_unique(ambiguous_role_columns, role, source_column)
            continue
        primary_role = str(metadata.get("primary_semantic_role") or "").strip()
        if primary_role and primary_role != "unknown" and primary_role in roles:
            resolved_roles = (primary_role,)
        elif len(roles) == 1:
            resolved_roles = roles
        else:
            for role in roles:
                _append_unique(ambiguous_role_columns, role, source_column)
            continue
        for role in resolved_roles:
            _append_unique(resolved_role_columns, role, source_column)

    return tuple(
        _build_family_binding(
            definition=definition,
            resolved_role_columns=resolved_role_columns,
            ambiguous_role_columns=ambiguous_role_columns,
        )
        for definition in VARIABLE_FAMILY_DEFINITIONS
    )


def ready_service_1_variable_family_ids_v1(
    bindings: tuple[Service1VariableFamilyBindingV1, ...] | list[Service1VariableFamilyBindingV1],
) -> tuple[str, ...]:
    return tuple(binding.family_id for binding in bindings if binding.status == STATUS_READY)


def _build_family_binding(*, definition: Service1VariableFamilyDefinitionV1, resolved_role_columns: dict[str, list[str]], ambiguous_role_columns: dict[str, list[str]]) -> Service1VariableFamilyBindingV1:
    satisfied: list[tuple[str, ...]] = []
    missing: list[tuple[str, ...]] = []
    ambiguous_groups: list[tuple[str, ...]] = []
    for group in definition.required_role_groups:
        if any(role in resolved_role_columns for role in group):
            satisfied.append(group)
        elif any(role in ambiguous_role_columns for role in group):
            ambiguous_groups.append(group)
        else:
            missing.append(group)

    required_roles = {role for group in definition.required_role_groups for role in group}
    family_roles = required_roles | set(definition.optional_roles)
    bound_roles = tuple(role for role in sorted(family_roles) if role in resolved_role_columns)
    ambiguous_roles = tuple(role for role in sorted(family_roles) if role in ambiguous_role_columns)
    optional_roles_present = tuple(role for role in definition.optional_roles if role in resolved_role_columns)
    observed = any(role in resolved_role_columns or role in ambiguous_role_columns for role in required_roles)
    if len(satisfied) == len(definition.required_role_groups):
        status = STATUS_READY
    elif ambiguous_groups:
        status = STATUS_NEEDS_OWNER_CONFIRMATION
    elif observed:
        status = STATUS_MISSING_REQUIRED_ROLES
    else:
        status = STATUS_NOT_OBSERVED

    source_columns: list[str] = []
    for role in sorted(family_roles):
        for column in resolved_role_columns.get(role, []):
            if column not in source_columns:
                source_columns.append(column)
        for column in ambiguous_role_columns.get(role, []):
            if column not in source_columns:
                source_columns.append(column)

    return Service1VariableFamilyBindingV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        family_id=definition.family_id,
        owner_label=definition.owner_label,
        priority=definition.priority,
        status=status,
        coverage_ratio=round(len(satisfied) / len(definition.required_role_groups), 6),
        required_role_groups=definition.required_role_groups,
        satisfied_role_groups=tuple(satisfied),
        missing_role_groups=tuple(missing),
        ambiguous_role_groups=tuple(ambiguous_groups),
        bound_roles=bound_roles,
        ambiguous_roles=ambiguous_roles,
        optional_roles_present=optional_roles_present,
        source_columns=tuple(source_columns),
        target_variable_names=definition.target_variable_names,
        target_capabilities=definition.target_capabilities,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata={"family_binding_only": True, "tool_selection_authorized": False},
    )


def _append_unique(mapping: dict[str, list[str]], role: str, column: str) -> None:
    values = mapping.setdefault(role, [])
    if column not in values:
        values.append(column)


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "FAMILY_OPERATION_CORE",
    "FAMILY_SALES_MARGIN",
    "FAMILY_CASH_COLLECTIONS",
    "FAMILY_PURCHASES_SUPPLIERS",
    "FAMILY_INVENTORY_CONTROL",
    "FAMILY_CASH_PROJECTION",
    "FAMILY_RECEIVABLES_DSO",
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_MISSING_REQUIRED_ROLES",
    "STATUS_NOT_OBSERVED",
    "ALLOWED_STATUSES",
    "Service1VariableFamilyDefinitionV1",
    "Service1VariableFamilyBindingV1",
    "VARIABLE_FAMILY_DEFINITIONS",
    "build_service_1_variable_family_bindings_v1",
    "ready_service_1_variable_family_ids_v1",
]
