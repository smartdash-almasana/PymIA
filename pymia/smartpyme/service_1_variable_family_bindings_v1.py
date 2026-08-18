"""Deterministic variable-family binding for Servicio 1.

This module groups semantic column candidates into business-capability families.
It does not infer new column meanings, execute tools, select diagnoses, or
authorize runtime. It only reports which coherent variable families are ready,
incomplete, ambiguous or absent.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
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
FAMILY_PERIOD_NET_MARGIN: Final[str] = "PERIOD_NET_MARGIN"
FAMILY_CASH_COLLECTIONS: Final[str] = "CASH_COLLECTIONS"
FAMILY_PURCHASES_SUPPLIERS: Final[str] = "PURCHASES_SUPPLIERS"
FAMILY_INVENTORY_CONTROL: Final[str] = "INVENTORY_CONTROL"
FAMILY_CASH_PROJECTION: Final[str] = "CASH_PROJECTION"
FAMILY_RECEIVABLES_DSO: Final[str] = "RECEIVABLES_DSO"
FAMILY_REORDER_POINT: Final[str] = "REORDER_POINT"
FAMILY_INVENTORY_TURNOVER: Final[str] = "INVENTORY_TURNOVER"
FAMILY_CURRENT_RATIO: Final[str] = "CURRENT_RATIO"
FAMILY_SALES_CONCENTRATION: Final[str] = "SALES_CONCENTRATION"
FAMILY_INTEREST_BURDEN: Final[str] = "INTEREST_BURDEN"
FAMILY_INDEX_UPDATE: Final[str] = "INDEX_UPDATE"

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
class Service1GrainV1:
    structural_scope: str
    business_entity_grain: str
    temporal_grain: str
    aggregation_grain: str

    def __post_init__(self) -> None:
        allowed_structural = {"ROW", "REGION", "SHEET"}
        allowed_entity = {
            "TRANSACTION", "LINE_ITEM", "INVOICE", "CUSTOMER", "SUPPLIER",
            "PRODUCT", "CATEGORY", "BRANCH", "EMPLOYEE", "CHANNEL",
            "PAYMENT_METHOD", "ACCOUNT", "NONE",
        }
        allowed_temporal = {
            "EVENT", "DAY", "WEEK", "MONTH", "QUARTER", "YEAR", "HOUR", "PERIOD", "NONE",
        }
        allowed_aggregation = {"ATOMIC", "GROUPED", "AGGREGATED"}
        if self.structural_scope not in allowed_structural:
            raise ValueError("invalid structural_scope")
        entity_parts = tuple(part.strip() for part in self.business_entity_grain.split("+") if part.strip())
        if not entity_parts or len(entity_parts) != len(self.business_entity_grain.split("+")):
            raise ValueError("invalid business_entity_grain")
        if len(set(entity_parts)) != len(entity_parts):
            raise ValueError("business_entity_grain must not contain duplicate components")
        if any(part not in allowed_entity or part == "NONE" and len(entity_parts) > 1 for part in entity_parts):
            raise ValueError("invalid business_entity_grain")
        if self.temporal_grain not in allowed_temporal:
            raise ValueError("invalid temporal_grain")
        if self.aggregation_grain not in allowed_aggregation:
            raise ValueError("invalid aggregation_grain")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_DEFAULT_REQUIREMENT_MATCH_GRAIN: Final[Service1GrainV1] = Service1GrainV1(
    structural_scope="REGION",
    business_entity_grain="NONE",
    temporal_grain="NONE",
    aggregation_grain="ATOMIC",
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
    grain: Service1GrainV1 = _DEFAULT_REQUIREMENT_MATCH_GRAIN

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


ANALYSIS_REQUIREMENT_MATCH_SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_REQUIREMENT_MATCH_V1"


@dataclass(frozen=True)
class Service1AnalysisRequirementMatchV1:
    analysis_id: str
    status: str
    reason: str | None
    required_role_groups: tuple[tuple[str, ...], ...]
    satisfied_role_groups: tuple[tuple[str, ...], ...]
    missing_role_groups: tuple[tuple[str, ...], ...]
    approved_roles: tuple[str, ...]
    source_columns: tuple[str, ...]
    requested_grain: Service1RequestedAnalysisGrainV1
    resolved_grain: Service1GrainV1 | None
    required_relationship_refs: tuple[str, ...]
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    schema_version: str = ANALYSIS_REQUIREMENT_MATCH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.analysis_id.strip():
            raise ValueError("analysis_id is required")
        if self.status not in P7_ALLOWED_STATUSES:
            raise ValueError(f"unsupported P7 status: {self.status}")
        if not isinstance(self.requested_grain, Service1RequestedAnalysisGrainV1):
            raise TypeError("requested_grain must be Service1RequestedAnalysisGrainV1")
        if self.status == P7_STATUS_MATCHED and self.resolved_grain is None:
            raise ValueError("REQUIREMENT_MATCHED requires resolved_grain")
        if self.status != P7_STATUS_MATCHED and self.resolved_grain is not None:
            raise ValueError("non-matched analysis requirement cannot carry resolved_grain")
        if self.status == P7_STATUS_MATCHED and self.reason is not None:
            raise ValueError("REQUIREMENT_MATCHED cannot carry a blocking reason")
        if self.status != P7_STATUS_MATCHED and not str(self.reason or "").strip():
            raise ValueError("non-matched analysis requirement requires reason")
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
        payload["requested_grain"] = self.requested_grain.to_dict()
        payload["resolved_grain"] = self.resolved_grain.to_dict() if self.resolved_grain else None
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
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_REORDER_POINT,
        owner_label="Punto de reposición",
        priority=8,
        required_role_groups=(("average_sales",), ("lead_time",), ("safety_stock",)),
        optional_roles=("product_identifier", "product_name"),
        target_variable_names=("average_sales", "lead_time", "safety_stock"),
        target_capabilities=("reorder_point",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_INVENTORY_TURNOVER,
        owner_label="Rotación de inventario",
        priority=9,
        required_role_groups=(("cost_of_goods_sold",), ("average_stock",)),
        optional_roles=("operation_date",),
        target_variable_names=("cost_of_goods_sold", "average_stock"),
        target_capabilities=("inventory_turnover",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_CURRENT_RATIO,
        owner_label="Liquidez corriente",
        priority=10,
        required_role_groups=(("current_assets",), ("current_liabilities",)),
        optional_roles=(),
        target_variable_names=("current_assets", "current_liabilities"),
        target_capabilities=("current_ratio",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_SALES_CONCENTRATION,
        owner_label="Concentración de ventas",
        priority=11,
        required_role_groups=(("main_sku_sales",), ("total_sales",)),
        optional_roles=("product_identifier", "product_name"),
        target_variable_names=("main_sku_sales", "total_sales"),
        target_capabilities=("sales_concentration",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_INTEREST_BURDEN,
        owner_label="Carga de intereses",
        priority=12,
        required_role_groups=(("interest_expense",), ("ebitda",)),
        optional_roles=(),
        target_variable_names=("interest_expense", "ebitda"),
        target_capabilities=("interest_burden_ratio",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_INDEX_UPDATE,
        owner_label="Actualización por índice",
        priority=13,
        required_role_groups=(("closing_index",), ("origin_index",)),
        optional_roles=(),
        target_variable_names=("closing_index", "origin_index"),
        target_capabilities=("index_update_ratio",),
    ),
    Service1VariableFamilyDefinitionV1(
        family_id=FAMILY_PERIOD_NET_MARGIN,
        owner_label="Margen neto del período",
        priority=14,
        required_role_groups=(
            ("period_sales_total",),
            ("period_costs_total",),
            ("period_taxes_total",),
        ),
        optional_roles=(),
        target_variable_names=("sale_price", "costs", "taxes"),
        target_capabilities=("net_margin_real",),
        grain=Service1GrainV1(
            structural_scope="SHEET",
            business_entity_grain="NONE",
            temporal_grain="PERIOD",
            aggregation_grain="AGGREGATED",
        ),
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

    return tuple(
        _build_requirement_match(
            definition=definition,
            role_columns=role_columns,
            grain=definition.grain,
        )
        for definition in VARIABLE_FAMILY_DEFINITIONS
    )


def build_service_1_analysis_requirement_match_v1(
    analysis_plan: Service1AnalysisPlanV1,
    p6_decisions: tuple[Service1P6ApprovalDecisionV1, ...] | list[Service1P6ApprovalDecisionV1],
) -> Service1AnalysisRequirementMatchV1:
    """Resolve analysis requirements and resolved grain from P6-approved evidence only."""
    if not isinstance(analysis_plan, Service1AnalysisPlanV1):
        raise TypeError("analysis_plan must be Service1AnalysisPlanV1")
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

    required_role_groups, requirement_error = _analysis_required_role_groups(analysis_plan)
    expected_business_grain, grain_error = _analysis_expected_business_grain(analysis_plan)
    requested = analysis_plan.requested_grain
    try:
        Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain=requested.business_entity_grain,
            temporal_grain=requested.temporal_grain,
            aggregation_grain=requested.aggregation_grain,
        )
    except ValueError as exc:
        return _analysis_requirement_decision(
            analysis_plan=analysis_plan,
            status=P7_STATUS_BLOCKED,
            reason=f"INVALID_REQUESTED_GRAIN:{exc}",
            required_role_groups=required_role_groups,
            role_columns=role_columns,
        )
    if requirement_error or grain_error:
        return _analysis_requirement_decision(
            analysis_plan=analysis_plan,
            status=P7_STATUS_BLOCKED,
            reason=requirement_error or grain_error,
            required_role_groups=required_role_groups,
            role_columns=role_columns,
        )
    if requested.business_entity_grain != expected_business_grain:
        return _analysis_requirement_decision(
            analysis_plan=analysis_plan,
            status=P7_STATUS_BLOCKED,
            reason="REQUESTED_BUSINESS_GRAIN_DIMENSION_MISMATCH",
            required_role_groups=required_role_groups,
            role_columns=role_columns,
        )

    satisfied: list[tuple[str, ...]] = []
    missing: list[tuple[str, ...]] = []
    for group in required_role_groups:
        if any(role in role_columns for role in group):
            satisfied.append(group)
        else:
            missing.append(group)
    required_roles = {role for group in required_role_groups for role in group}
    observed = any(role in role_columns for role in required_roles)
    if not missing:
        status = P7_STATUS_MATCHED
        reason = None
    elif observed:
        status = P7_STATUS_MISSING_REQUIREMENTS
        reason = "ANALYSIS_REQUIREMENTS_MISSING"
    else:
        status = P7_STATUS_NOT_OBSERVED
        reason = "ANALYSIS_REQUIREMENTS_NOT_OBSERVED"

    approved_roles = tuple(role for role in sorted(required_roles) if role in role_columns)
    source_columns: list[str] = []
    for role in approved_roles:
        for column in role_columns.get(role, []):
            if column not in source_columns:
                source_columns.append(column)
    resolved_grain = None
    if status == P7_STATUS_MATCHED:
        resolved_grain = Service1GrainV1(
            structural_scope="REGION",
            business_entity_grain=requested.business_entity_grain,
            temporal_grain=requested.temporal_grain,
            aggregation_grain=requested.aggregation_grain,
        )
    return Service1AnalysisRequirementMatchV1(
        analysis_id=analysis_plan.analysis_id,
        status=status,
        reason=reason,
        required_role_groups=required_role_groups,
        satisfied_role_groups=tuple(satisfied),
        missing_role_groups=tuple(missing),
        approved_roles=approved_roles,
        source_columns=tuple(source_columns),
        requested_grain=requested,
        resolved_grain=resolved_grain,
        required_relationship_refs=analysis_plan.relationship_refs,
        provenance={
            "source": "ANALYSIS_PLAN_PLUS_P6_APPROVAL_DECISIONS",
            "p7_analysis_requirement_match_only": True,
            "relationship_resolution_authorized": False,
            "computability_authorized": False,
        },
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
    )


def _analysis_required_role_groups(
    analysis_plan: Service1AnalysisPlanV1,
) -> tuple[tuple[tuple[str, ...], ...], str | None]:
    groups: list[tuple[str, ...]] = []
    for measure in analysis_plan.measures:
        if measure == "sales":
            groups.append(("sales_amount",))
        else:
            return tuple(groups), f"UNSUPPORTED_ANALYSIS_MEASURE:{measure}"
    for dimension in analysis_plan.dimensions:
        if dimension == "product":
            groups.append(("product_identifier", "product_name"))
        elif dimension == "branch":
            groups.append(("branch_identifier", "branch_name"))
        elif dimension == "time":
            temporal = analysis_plan.requested_grain.temporal_grain
            if temporal in {"DAY", "WEEK", "MONTH"}:
                groups.append(("operation_date",))
            elif temporal == "HOUR":
                groups.append(("operation_time",))
            else:
                return tuple(groups), f"UNSUPPORTED_ANALYSIS_TEMPORAL_GRAIN:{temporal}"
        else:
            return tuple(groups), f"UNSUPPORTED_ANALYSIS_DIMENSION:{dimension}"
    unique_groups: list[tuple[str, ...]] = []
    for group in groups:
        if group not in unique_groups:
            unique_groups.append(group)
    return tuple(unique_groups), None


def _analysis_expected_business_grain(
    analysis_plan: Service1AnalysisPlanV1,
) -> tuple[str, str | None]:
    mapping = {"product": "PRODUCT", "branch": "BRANCH"}
    parts: list[str] = []
    for dimension in analysis_plan.dimensions:
        if dimension == "time":
            continue
        mapped = mapping.get(dimension)
        if mapped is None:
            return "", f"UNSUPPORTED_ANALYSIS_DIMENSION:{dimension}"
        parts.append(mapped)
    return "+".join(parts) if parts else "NONE", None


def _analysis_requirement_decision(
    *,
    analysis_plan: Service1AnalysisPlanV1,
    status: str,
    reason: str,
    required_role_groups: tuple[tuple[str, ...], ...],
    role_columns: dict[str, list[str]],
) -> Service1AnalysisRequirementMatchV1:
    required_roles = {role for group in required_role_groups for role in group}
    approved_roles = tuple(role for role in sorted(required_roles) if role in role_columns)
    source_columns = tuple(dict.fromkeys(
        column
        for role in approved_roles
        for column in role_columns.get(role, [])
    ))
    return Service1AnalysisRequirementMatchV1(
        analysis_id=analysis_plan.analysis_id,
        status=status,
        reason=reason,
        required_role_groups=required_role_groups,
        satisfied_role_groups=(),
        missing_role_groups=required_role_groups,
        approved_roles=approved_roles,
        source_columns=source_columns,
        requested_grain=analysis_plan.requested_grain,
        resolved_grain=None,
        required_relationship_refs=analysis_plan.relationship_refs,
        provenance={
            "source": "ANALYSIS_PLAN_PLUS_P6_APPROVAL_DECISIONS",
            "p7_analysis_requirement_match_only": True,
            "relationship_resolution_authorized": False,
            "computability_authorized": False,
        },
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
    "FAMILY_PERIOD_NET_MARGIN",
    "FAMILY_CASH_COLLECTIONS",
    "FAMILY_PURCHASES_SUPPLIERS",
    "FAMILY_INVENTORY_CONTROL",
    "FAMILY_CASH_PROJECTION",
    "FAMILY_RECEIVABLES_DSO",
    "FAMILY_REORDER_POINT",
    "FAMILY_INVENTORY_TURNOVER",
    "FAMILY_CURRENT_RATIO",
    "FAMILY_SALES_CONCENTRATION",
    "FAMILY_INTEREST_BURDEN",
    "FAMILY_INDEX_UPDATE",
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_MISSING_REQUIRED_ROLES",
    "STATUS_NOT_OBSERVED",
    "ALLOWED_STATUSES",
    "Service1VariableFamilyDefinitionV1",
    "Service1GrainV1",
    "Service1RequirementMatchV1",
    "Service1AnalysisRequirementMatchV1",
    "Service1VariableFamilyBindingV1",
    "VARIABLE_FAMILY_DEFINITIONS",
    "P7_STATUS_MATCHED",
    "P7_STATUS_MISSING_REQUIREMENTS",
    "P7_STATUS_NOT_OBSERVED",
    "P7_STATUS_BLOCKED",
    "ANALYSIS_REQUIREMENT_MATCH_SCHEMA_VERSION",
    "build_service_1_requirement_matches_v1",
    "build_service_1_analysis_requirement_match_v1",
    "project_service_1_requirement_matches_to_variable_family_bindings_v1",
    "ready_service_1_requirement_family_ids_v1",
    "build_service_1_variable_family_bindings_v1",
    "ready_service_1_variable_family_ids_v1",
]
