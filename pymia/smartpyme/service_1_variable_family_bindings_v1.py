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
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_APPROVED as P6_STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
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

P7_STATUS_MATCHED: Final[str] = "REQUIREMENT_MATCHED"
P7_STATUS_MISSING_REQUIREMENTS: Final[str] = "MISSING_REQUIREMENTS"
P7_STATUS_NOT_OBSERVED: Final[str] = "REQUIREMENTS_NOT_OBSERVED"
P7_STATUS_BLOCKED: Final[str] = "BLOCKED"
P7_ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    P7_STATUS_NOT_OBSERVED,
    P7_STATUS_BLOCKED,
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
class Service1GrainV1:
    structural_scope: str
    business_entity_grain: str
    temporal_grain: str
    aggregation_grain: str

    def __post_init__(self) -> None:
        allowed_structural = {"ROW", "REGION", "SHEET"}
        allowed_entity = {
            "TRANSACTION", "LINE_ITEM", "INVOICE", "CUSTOMER", "SUPPLIER",
            "PRODUCT", "ACCOUNT", "NONE",
        }
        allowed_temporal = {
            "EVENT", "DAY", "WEEK", "MONTH", "QUARTER", "YEAR", "PERIOD", "NONE",
        }
        allowed_aggregation = {"ATOMIC", "GROUPED", "AGGREGATED"}
        if self.structural_scope not in allowed_structural:
            raise ValueError("invalid structural_scope")
        if self.business_entity_grain not in allowed_entity:
            raise ValueError("invalid business_entity_grain")
        if self.temporal_grain not in allowed_temporal:
            raise ValueError("invalid temporal_grain")
        if self.aggregation_grain not in allowed_aggregation:
            raise ValueError("invalid aggregation_grain")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1RequirementMatchV1:
    schema_version: str
    service_name: str
    family_id: str
    status: str
    required_role_groups: tuple[tuple[str, ...], ...]
    satisfied_role_groups: tuple[tuple[str, ...], ...]
    missing_role_groups: tuple[tuple[str, ...], ...]
    approved_roles: tuple[str, ...]
    source_columns: tuple[str, ...]
    target_variable_names: tuple[str, ...]
    target_capabilities: tuple[str, ...]
    grain: Service1GrainV1
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        if self.status not in P7_ALLOWED_STATUSES:
            raise ValueError(f"unsupported P7 status: {self.status}")
        if not self.family_id.strip():
            raise ValueError("family_id is required")
        for field_name in (
            "runtime_authorized",
            "tool_execution_authorized",
            "delivery_authorized",
            "diagnosis_generated",
        ):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain False")
        object.__setattr__(self, "provenance", dict(self.provenance or {}))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["grain"] = self.grain.to_dict()
        return payload


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


def build_service_1_requirement_matches_v1(
    p6_decisions: tuple[Service1P6ApprovalDecisionV1, ...] | list[Service1P6ApprovalDecisionV1],
) -> tuple[Service1RequirementMatchV1, ...]:
    """Canonical P7 requirement matching from approved P6 decisions only."""
    decisions = tuple(p6_decisions or ())
    for decision in decisions:
        if not isinstance(decision, Service1P6ApprovalDecisionV1):
            raise TypeError("p6_decisions must contain Service1P6ApprovalDecisionV1")
        if decision.status != P6_STATUS_APPROVED:
            raise ValueError("P7 requires only APPROVED P6 decisions")

    role_columns: dict[str, list[str]] = {}
    for decision in decisions:
        role = str(decision.approved_role or "").strip()
        column = str(decision.column_ref or "").strip()
        if role and column:
            _append_unique(role_columns, role, column)

    grain = Service1GrainV1(
        structural_scope="REGION",
        business_entity_grain="NONE",
        temporal_grain="NONE",
        aggregation_grain="ATOMIC",
    )
    return tuple(
        _build_requirement_match(
            definition=definition,
            role_columns=role_columns,
            grain=grain,
        )
        for definition in VARIABLE_FAMILY_DEFINITIONS
    )


def _build_requirement_match(
    *,
    definition: Service1VariableFamilyDefinitionV1,
    role_columns: dict[str, list[str]],
    grain: Service1GrainV1,
) -> Service1RequirementMatchV1:
    satisfied: list[tuple[str, ...]] = []
    missing: list[tuple[str, ...]] = []
    for group in definition.required_role_groups:
        if any(role in role_columns for role in group):
            satisfied.append(group)
        else:
            missing.append(group)

    required_roles = {role for group in definition.required_role_groups for role in group}
    family_roles = required_roles | set(definition.optional_roles)
    observed = any(role in role_columns for role in required_roles)
    if len(satisfied) == len(definition.required_role_groups):
        status = P7_STATUS_MATCHED
    elif observed:
        status = P7_STATUS_MISSING_REQUIREMENTS
    else:
        status = P7_STATUS_NOT_OBSERVED

    approved_roles = tuple(role for role in sorted(family_roles) if role in role_columns)
    source_columns: list[str] = []
    for role in approved_roles:
        for column in role_columns.get(role, []):
            if column not in source_columns:
                source_columns.append(column)

    return Service1RequirementMatchV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        family_id=definition.family_id,
        status=status,
        required_role_groups=definition.required_role_groups,
        satisfied_role_groups=tuple(satisfied),
        missing_role_groups=tuple(missing),
        approved_roles=approved_roles,
        source_columns=tuple(source_columns),
        target_variable_names=definition.target_variable_names,
        target_capabilities=definition.target_capabilities,
        grain=grain,
        provenance={
            "source": "P6_APPROVAL_DECISIONS",
            "p7_requirement_match_only": True,
        },
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
    )


def project_service_1_requirement_matches_to_variable_family_bindings_v1(
    matches: tuple[Service1RequirementMatchV1, ...] | list[Service1RequirementMatchV1],
) -> tuple[Service1VariableFamilyBindingV1, ...]:
    """Legacy projection only; canonical P7 authority is Service1RequirementMatchV1."""
    projected: list[Service1VariableFamilyBindingV1] = []
    definitions = {definition.family_id: definition for definition in VARIABLE_FAMILY_DEFINITIONS}
    for match in tuple(matches or ()):
        if not isinstance(match, Service1RequirementMatchV1):
            raise TypeError("matches must contain Service1RequirementMatchV1")
        definition = definitions.get(match.family_id)
        if definition is None:
            raise ValueError("unknown family_id in requirement match")
        if match.status == P7_STATUS_MATCHED:
            legacy_status = STATUS_READY
        elif match.status == P7_STATUS_MISSING_REQUIREMENTS:
            legacy_status = STATUS_MISSING_REQUIRED_ROLES
        elif match.status == P7_STATUS_NOT_OBSERVED:
            legacy_status = STATUS_NOT_OBSERVED
        else:
            legacy_status = STATUS_MISSING_REQUIRED_ROLES
        projected.append(
            Service1VariableFamilyBindingV1(
                schema_version=SCHEMA_VERSION,
                service_name=SERVICE_NAME,
                family_id=definition.family_id,
                owner_label=definition.owner_label,
                priority=definition.priority,
                status=legacy_status,
                coverage_ratio=round(
                    len(match.satisfied_role_groups) / len(match.required_role_groups), 6
                ),
                required_role_groups=match.required_role_groups,
                satisfied_role_groups=match.satisfied_role_groups,
                missing_role_groups=match.missing_role_groups,
                ambiguous_role_groups=(),
                bound_roles=match.approved_roles,
                ambiguous_roles=(),
                optional_roles_present=tuple(
                    role for role in definition.optional_roles if role in match.approved_roles
                ),
                source_columns=match.source_columns,
                target_variable_names=match.target_variable_names,
                target_capabilities=match.target_capabilities,
                runtime_authorized=False,
                tool_execution_authorized=False,
                delivery_authorized=False,
                diagnosis_generated=False,
                metadata={
                    "compatibility_projection": True,
                    "canonical_source": "Service1RequirementMatchV1",
                    "tool_selection_authorized": False,
                },
            )
        )
    return tuple(projected)


def ready_service_1_requirement_family_ids_v1(
    matches: tuple[Service1RequirementMatchV1, ...] | list[Service1RequirementMatchV1],
) -> tuple[str, ...]:
    return tuple(match.family_id for match in matches if match.status == P7_STATUS_MATCHED)


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
    "Service1GrainV1",
    "Service1RequirementMatchV1",
    "Service1VariableFamilyBindingV1",
    "VARIABLE_FAMILY_DEFINITIONS",
    "P7_STATUS_MATCHED",
    "P7_STATUS_MISSING_REQUIREMENTS",
    "P7_STATUS_NOT_OBSERVED",
    "P7_STATUS_BLOCKED",
    "build_service_1_requirement_matches_v1",
    "project_service_1_requirement_matches_to_variable_family_bindings_v1",
    "ready_service_1_requirement_family_ids_v1",
    "build_service_1_variable_family_bindings_v1",
    "ready_service_1_variable_family_ids_v1",
]
