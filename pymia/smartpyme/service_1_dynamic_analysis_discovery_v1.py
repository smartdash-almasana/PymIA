"""F10 dynamic analysis discovery for Service 1.

F10 converts confirmed P6 semantic evidence into candidate AnalysisPlans,
passes every candidate through canonical P7 and P8, and reports technical
availability separately from commercial exposure. It never executes joins,
math, findings, UI rendering or delivery.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from itertools import product
from typing import Any, Final, Iterable, Mapping

from pymia.smartpyme.service_1_analysis_plan_v1 import (
    AnalysisKind,
    Service1AnalysisFilterV1,
    Service1AnalysisOrderByV1,
    Service1AnalysisPlanV1,
    Service1RequestedAnalysisGrainV1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    STATUS_BLOCKED as P8_STATUS_BLOCKED,
    STATUS_COMPUTABLE as P8_STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE as P8_STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_ANALYSIS as P8_STATUS_UNSUPPORTED,
    Service1GovernedAnalysisInputV1,
    build_service_1_analysis_computability_decision_v1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    SCHEMA_VERSION as P6_SCHEMA_VERSION,
    STATUS_APPROVED as P6_STATUS_APPROVED,
    Service1P6ApprovalDecisionV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    P7_STATUS_BLOCKED,
    P7_STATUS_MATCHED,
    P7_STATUS_MISSING_REQUIREMENTS,
    P7_STATUS_NOT_OBSERVED,
    Service1AnalysisRequirementMatchV1,
    build_service_1_analysis_requirement_match_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_DYNAMIC_ANALYSIS_DISCOVERY_V1"
CATALOG_SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_DISCOVERY_CATALOG_V1"

STATUS_READY: Final[str] = "DISCOVERY_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

TECHNICALLY_AVAILABLE: Final[str] = "TECHNICALLY_AVAILABLE"
TECHNICALLY_NEEDS_EVIDENCE: Final[str] = "TECHNICALLY_NEEDS_EVIDENCE"
TECHNICALLY_UNSUPPORTED: Final[str] = "TECHNICALLY_UNSUPPORTED"
TECHNICALLY_BLOCKED: Final[str] = "TECHNICALLY_BLOCKED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "analysis_execution_authorized",
)


@dataclass(frozen=True)
class Service1AnalysisDiscoveryTemplateV1:
    analysis_id: str
    title: str
    question: str
    kind: AnalysisKind
    measures: tuple[str, ...]
    dimensions: tuple[str, ...]
    business_entity_grain: str
    temporal_grain: str
    aggregation_grain: str
    filters: tuple[Service1AnalysisFilterV1, ...] = ()
    order_by: tuple[Service1AnalysisOrderByV1, ...] = ()
    limit: int | None = None
    preferred_roles: tuple[str, ...] = ()
    commercially_exposed_by_default: bool = False
    schema_version: str = CATALOG_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "analysis_id",
            "title",
            "question",
            "business_entity_grain",
            "temporal_grain",
            "aggregation_grain",
        ):
            if not str(getattr(self, name) or "").strip():
                raise ValueError(f"{name} is required")
        kind = self.kind if isinstance(self.kind, AnalysisKind) else AnalysisKind(self.kind)
        object.__setattr__(self, "kind", kind)
        if not self.measures or any(not str(value).strip() for value in self.measures):
            raise ValueError("measures must be non-empty")
        if any(not str(value).strip() for value in self.dimensions):
            raise ValueError("dimensions must contain non-empty refs")
        if len(set(self.measures)) != len(self.measures) or len(set(self.dimensions)) != len(self.dimensions):
            raise ValueError("measures and dimensions cannot contain duplicates")
        if any(not str(value).strip() for value in self.preferred_roles):
            raise ValueError("preferred_roles must contain non-empty refs")
        if len(set(self.preferred_roles)) != len(self.preferred_roles):
            raise ValueError("preferred_roles cannot contain duplicates")
        filters = tuple(self.filters)
        if any(not isinstance(item, Service1AnalysisFilterV1) for item in filters):
            raise ValueError("filters must contain Service1AnalysisFilterV1 values")
        object.__setattr__(self, "measures", tuple(self.measures))
        object.__setattr__(self, "dimensions", tuple(self.dimensions))
        object.__setattr__(self, "filters", filters)
        object.__setattr__(self, "order_by", tuple(self.order_by))
        object.__setattr__(self, "preferred_roles", tuple(self.preferred_roles))

    def build_plan(self, *, relationship_refs: tuple[str, ...] = ()) -> Service1AnalysisPlanV1:
        return Service1AnalysisPlanV1(
            analysis_id=self.analysis_id,
            kind=self.kind,
            measures=self.measures,
            dimensions=self.dimensions,
            relationship_refs=tuple(relationship_refs),
            requested_grain=Service1RequestedAnalysisGrainV1(
                business_entity_grain=self.business_entity_grain,
                temporal_grain=self.temporal_grain,
                aggregation_grain=self.aggregation_grain,
            ),
            filters=self.filters,
            order_by=self.order_by,
            limit=self.limit,
            provenance={"source": "F10_ANALYSIS_DISCOVERY_CATALOG"},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "analysis_id": self.analysis_id,
            "title": self.title,
            "question": self.question,
            "kind": self.kind.value,
            "measures": list(self.measures),
            "dimensions": list(self.dimensions),
            "business_entity_grain": self.business_entity_grain,
            "temporal_grain": self.temporal_grain,
            "aggregation_grain": self.aggregation_grain,
            "filters": [item.to_dict() for item in self.filters],
            "order_by": [item.to_dict() for item in self.order_by],
            "limit": self.limit,
            "preferred_roles": list(self.preferred_roles),
            "commercially_exposed_by_default": self.commercially_exposed_by_default,
        }


ANALYSIS_DISCOVERY_CATALOG_V1: Final[tuple[Service1AnalysisDiscoveryTemplateV1, ...]] = (
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_total",
        title="Resumen de ventas",
        question="¿Cuánto vendiste en total con la evidencia confirmada?",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("sales",),
        dimensions=(),
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_product",
        title="Ventas por producto",
        question="¿Cuánto vendió cada producto?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="gross_margin_by_product",
        title="Margen bruto por producto",
        question="¿Qué margen bruto muestra cada producto según ventas y costos confirmados?",
        kind=AnalysisKind.GROUPED,
        measures=("gross_margin",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_branch",
        title="Ventas por sucursal",
        question="¿Cuánto vendió cada sucursal?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("branch",),
        business_entity_grain="BRANCH",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("branch_name",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_category",
        title="Ventas por categoría",
        question="¿Cuánto vendió cada categoría?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("category",),
        business_entity_grain="CATEGORY",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_employee",
        title="Ventas por empleado",
        question="¿Cuánto vendió cada empleado según las operaciones registradas?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("employee",),
        business_entity_grain="EMPLOYEE",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_channel",
        title="Ventas por canal",
        question="¿Cuánto vendió cada canal de venta?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("channel",),
        business_entity_grain="CHANNEL",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_payment_method",
        title="Ventas por medio de pago",
        question="¿Cuánto se vendió por cada medio de pago registrado?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("payment_method",),
        business_entity_grain="PAYMENT_METHOD",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="units_by_product",
        title="Unidades vendidas por producto",
        question="¿Cuántas unidades se vendieron de cada producto?",
        kind=AnalysisKind.GROUPED,
        measures=("units",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="rows_by_product",
        title="Registros observados por producto",
        question="¿Cuántas filas registradas corresponden a cada producto?",
        kind=AnalysisKind.GROUPED,
        measures=("row_count",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="top_products_by_sales",
        title="Productos con más ventas",
        question="¿Qué productos concentran mayor importe bruto de ventas?",
        kind=AnalysisKind.RANKED,
        measures=("sales",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales", direction="DESC"),),
        limit=10,
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="top_products_by_units",
        title="Productos con más unidades vendidas",
        question="¿Qué productos muestran mayor demanda observada en unidades?",
        kind=AnalysisKind.RANKED,
        measures=("units",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="units", direction="DESC"),),
        limit=10,
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="product_sales_concentration",
        title="Concentración de ventas por producto",
        question="¿Qué participación tiene cada producto sobre las ventas totales?",
        kind=AnalysisKind.RANKED,
        measures=("sales_concentration",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="sales_concentration", direction="DESC"),),
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="discounted_rows",
        title="Registros con descuento informado",
        question="¿Cuántas filas tienen un valor de descuento distinto de cero?",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("row_count",),
        dimensions=(),
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
        filters=(Service1AnalysisFilterV1(field_ref="discount_candidate", operator="GT", value=0),),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="discounted_rows_by_product",
        title="Registros con descuento por producto",
        question="¿Qué productos aparecen con mayor cantidad de filas marcadas con descuento?",
        kind=AnalysisKind.RANKED,
        measures=("row_count",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        filters=(Service1AnalysisFilterV1(field_ref="discount_candidate", operator="GT", value=0),),
        order_by=(Service1AnalysisOrderByV1(field_ref="row_count", direction="DESC"),),
        limit=10,
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="catalog_price_variance_by_product",
        title="Precio observado contra precio de catálogo",
        question="¿Qué diferencia porcentual hay entre el precio observado y el precio de catálogo confirmado?",
        kind=AnalysisKind.GROUPED,
        measures=("catalog_price_variance_pct",),
        dimensions=("product",),
        business_entity_grain="PRODUCT",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="transaction_id_multiplicity",
        title="Multiplicidad por identificador de operación",
        question="¿Cuántas filas aparecen asociadas a cada identificador de operación?",
        kind=AnalysisKind.RANKED,
        measures=("row_count",),
        dimensions=("transaction",),
        business_entity_grain="TRANSACTION",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="row_count", direction="DESC"),),
        limit=20,
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_product_branch",
        title="Ventas por producto y sucursal",
        question="¿Cómo se distribuyen las ventas de cada producto entre sucursales?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("product", "branch"),
        business_entity_grain="PRODUCT+BRANCH",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("product_identifier", "branch_name"),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_by_category_branch",
        title="Ventas por categoría y sucursal",
        question="¿Cómo se distribuyen las ventas de cada categoría entre sucursales?",
        kind=AnalysisKind.GROUPED,
        measures=("sales",),
        dimensions=("category", "branch"),
        business_entity_grain="CATEGORY+BRANCH",
        temporal_grain="PERIOD",
        aggregation_grain="GROUPED",
        preferred_roles=("branch_name",),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_series_day",
        title="Evolución diaria de ventas",
        question="¿Cómo evolucionaron las ventas día por día?",
        kind=AnalysisKind.SERIES,
        measures=("sales",),
        dimensions=("time",),
        business_entity_grain="NONE",
        temporal_grain="DAY",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_series_hour",
        title="Ventas por hora",
        question="¿Cómo se distribuyen las ventas según la hora de la operación?",
        kind=AnalysisKind.SERIES,
        measures=("sales",),
        dimensions=("time",),
        business_entity_grain="NONE",
        temporal_grain="HOUR",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="sales_series_month",
        title="Evolución mensual de ventas",
        question="¿Cómo evolucionaron las ventas mes a mes?",
        kind=AnalysisKind.SERIES,
        measures=("sales",),
        dimensions=("time",),
        business_entity_grain="NONE",
        temporal_grain="MONTH",
        aggregation_grain="GROUPED",
        order_by=(Service1AnalysisOrderByV1(field_ref="time", direction="ASC"),),
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="dso",
        title="Tiempo de cobro",
        question="¿Qué plazo de cobro muestran las cuentas por cobrar y las ventas confirmadas?",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("dso",),
        dimensions=(),
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    ),
    Service1AnalysisDiscoveryTemplateV1(
        analysis_id="projected_cash_balance",
        title="Saldo de caja proyectado",
        question="¿Qué saldo de cierre resulta de los cobros y pagos previstos confirmados?",
        kind=AnalysisKind.SINGLE_VALUE,
        measures=("projected_cash_balance",),
        dimensions=(),
        business_entity_grain="NONE",
        temporal_grain="PERIOD",
        aggregation_grain="AGGREGATED",
    ),
)


F12_COMMERCIAL_ANALYSIS_IDS: Final[tuple[str, ...]] = (
    "sales_total",
    "sales_by_product",
    "gross_margin_by_product",
    "sales_by_branch",
    "sales_by_category",
    "sales_by_employee",
    "sales_by_channel",
    "sales_by_payment_method",
    "units_by_product",
    "rows_by_product",
    "top_products_by_sales",
    "top_products_by_units",
    "product_sales_concentration",
    "discounted_rows",
    "discounted_rows_by_product",
    "catalog_price_variance_by_product",
    "transaction_id_multiplicity",
    "sales_by_product_branch",
    "sales_by_category_branch",
    "sales_series_day",
    "sales_series_hour",
    "sales_series_month",
)


@dataclass(frozen=True)
class Service1DiscoveredAnalysisV1:
    analysis_id: str
    title: str
    question: str
    plan: Service1AnalysisPlanV1
    technical_status: str
    technically_available: bool
    commercially_requested: bool
    commercially_exposed: bool
    p7_status: str
    p7_reason: str | None
    p8_status: str
    p8_reason: str | None
    governed_analysis_input: Service1GovernedAnalysisInputV1 | None = None
    missing_role_groups: tuple[tuple[str, ...], ...] = ()
    required_relationship_refs: tuple[str, ...] = ()
    missing_relationship_evidence: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.technical_status not in {
            TECHNICALLY_AVAILABLE,
            TECHNICALLY_NEEDS_EVIDENCE,
            TECHNICALLY_UNSUPPORTED,
            TECHNICALLY_BLOCKED,
        }:
            raise ValueError("invalid technical_status")
        if self.technically_available != (self.technical_status == TECHNICALLY_AVAILABLE):
            raise ValueError("technically_available must match technical_status")
        if self.commercially_exposed and not self.commercially_requested:
            raise ValueError("commercial exposure requires commercial request")
        if self.commercially_exposed and not self.technically_available:
            raise ValueError("commercial exposure requires technical availability")
        if self.technically_available and not isinstance(self.governed_analysis_input, Service1GovernedAnalysisInputV1):
            raise ValueError("technical availability requires canonical P8 governed analysis input")
        if not self.technically_available and self.governed_analysis_input is not None:
            raise ValueError("non-available discovery cannot carry governed analysis input")
        if not isinstance(self.plan, Service1AnalysisPlanV1) or self.plan.analysis_id != self.analysis_id:
            raise ValueError("plan identity mismatch")
        object.__setattr__(self, "missing_role_groups", tuple(tuple(group) for group in self.missing_role_groups))
        object.__setattr__(self, "required_relationship_refs", tuple(self.required_relationship_refs))
        object.__setattr__(self, "missing_relationship_evidence", tuple(self.missing_relationship_evidence))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "title": self.title,
            "question": self.question,
            "plan": self.plan.to_dict(),
            "technical_status": self.technical_status,
            "technically_available": self.technically_available,
            "commercially_requested": self.commercially_requested,
            "commercially_exposed": self.commercially_exposed,
            "p7_status": self.p7_status,
            "p7_reason": self.p7_reason,
            "p8_status": self.p8_status,
            "p8_reason": self.p8_reason,
            "governed_analysis_input": (
                self.governed_analysis_input.to_dict()
                if self.governed_analysis_input is not None
                else None
            ),
            "missing_role_groups": [list(group) for group in self.missing_role_groups],
            "required_relationship_refs": list(self.required_relationship_refs),
            "missing_relationship_evidence": list(self.missing_relationship_evidence),
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1DynamicAnalysisDiscoveryV1:
    case_id: str
    analyses: tuple[Service1DiscoveredAnalysisV1, ...]
    status: str = STATUS_READY
    blocked_reason: str | None = None
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip():
            raise ValueError("case_id is required")
        if self.status not in {STATUS_READY, STATUS_BLOCKED}:
            raise ValueError("invalid discovery status")
        if self.status == STATUS_READY and self.blocked_reason is not None:
            raise ValueError("ready discovery cannot carry blocked_reason")
        if self.status == STATUS_BLOCKED and not str(self.blocked_reason or "").strip():
            raise ValueError("blocked discovery requires blocked_reason")
        object.__setattr__(self, "analyses", tuple(self.analyses))

    @property
    def technically_available(self) -> tuple[Service1DiscoveredAnalysisV1, ...]:
        return tuple(item for item in self.analyses if item.technically_available)

    @property
    def commercially_exposed(self) -> tuple[Service1DiscoveredAnalysisV1, ...]:
        return tuple(item for item in self.analyses if item.commercially_exposed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "status": self.status,
            "blocked_reason": self.blocked_reason,
            "analyses": [item.to_dict() for item in self.analyses],
            "technically_available": [item.analysis_id for item in self.technically_available],
            "commercially_exposed": [item.analysis_id for item in self.commercially_exposed],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


def build_service_1_dynamic_analysis_discovery_v1(
    *,
    confirmed_bindings: Mapping[str, Any],
    commercially_exposed_analysis_ids: Iterable[str] | None = None,
    templates: Iterable[Service1AnalysisDiscoveryTemplateV1] | None = None,
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
) -> Service1DynamicAnalysisDiscoveryV1:
    """Discover candidate AnalysisPlans from confirmed semantics through P7/P8."""
    if not isinstance(confirmed_bindings, Mapping) or confirmed_bindings.get("status") != "CONFIRMED_BINDINGS":
        return Service1DynamicAnalysisDiscoveryV1(
            case_id="UNRESOLVED",
            analyses=(),
            status=STATUS_BLOCKED,
            blocked_reason="CONFIRMED_BINDINGS_REQUIRED",
        )
    if any(bool(confirmed_bindings.get(flag)) for flag in _AUTHORITY_FLAGS):
        return Service1DynamicAnalysisDiscoveryV1(
            case_id=_case_id(confirmed_bindings) or "UNRESOLVED",
            analyses=(),
            status=STATUS_BLOCKED,
            blocked_reason="CONFIRMED_BINDINGS_AUTHORITY_FORBIDDEN",
        )
    case_id = _case_id(confirmed_bindings)
    if not case_id:
        return Service1DynamicAnalysisDiscoveryV1(
            case_id="UNRESOLVED",
            analyses=(),
            status=STATUS_BLOCKED,
            blocked_reason="CASE_ID_REQUIRED",
        )
    try:
        p6_decisions = _p6_decisions(confirmed_bindings, case_id=case_id)
        relationship_bindings = _relationship_bindings(confirmed_bindings)
    except (TypeError, ValueError) as exc:
        return Service1DynamicAnalysisDiscoveryV1(
            case_id=case_id,
            analyses=(),
            status=STATUS_BLOCKED,
            blocked_reason=f"DISCOVERY_EVIDENCE_INVALID:{exc}",
        )
    if not p6_decisions:
        return Service1DynamicAnalysisDiscoveryV1(
            case_id=case_id,
            analyses=(),
            status=STATUS_BLOCKED,
            blocked_reason="APPROVED_P6_EVIDENCE_REQUIRED",
        )

    candidate_templates = tuple(templates or ANALYSIS_DISCOVERY_CATALOG_V1)
    if not candidate_templates or len({item.analysis_id for item in candidate_templates}) != len(candidate_templates):
        raise ValueError("discovery templates must be non-empty with unique analysis_id")
    if any(not isinstance(item, Service1AnalysisDiscoveryTemplateV1) for item in candidate_templates):
        raise TypeError("templates must contain Service1AnalysisDiscoveryTemplateV1")

    if commercially_exposed_analysis_ids is None:
        exposure = {item.analysis_id for item in candidate_templates if item.commercially_exposed_by_default}
    else:
        exposure = {str(value).strip() for value in commercially_exposed_analysis_ids if str(value).strip()}
        unknown = exposure - {item.analysis_id for item in candidate_templates}
        if unknown:
            raise ValueError(f"unknown commercial exposure analysis ids:{','.join(sorted(unknown))}")

    analyses = tuple(
        _discover_one(
            case_id=case_id,
            template=template,
            p6_decisions=p6_decisions,
            relationship_bindings=relationship_bindings,
            commercially_requested=template.analysis_id in exposure,
            d7_workbook_logical_model=d7_workbook_logical_model,
        )
        for template in candidate_templates
    )
    return Service1DynamicAnalysisDiscoveryV1(case_id=case_id, analyses=analyses)


def _discover_one(
    *,
    case_id: str,
    template: Service1AnalysisDiscoveryTemplateV1,
    p6_decisions: tuple[Service1P6ApprovalDecisionV1, ...],
    relationship_bindings: Mapping[str, Mapping[str, Any]],
    commercially_requested: bool,
    d7_workbook_logical_model: Mapping[str, Any] | None = None,
) -> Service1DiscoveredAnalysisV1:
    provisional_plan = template.build_plan()
    preliminary_match = build_service_1_analysis_requirement_match_v1(provisional_plan, p6_decisions)

    required_relationship_refs: tuple[str, ...] = ()
    missing_relationship_evidence: tuple[str, ...] = ()
    relationship_error: str | None = None
    effective_p6 = p6_decisions
    if preliminary_match.status == P7_STATUS_MATCHED:
        source_decisions, source_error = _selected_source_decisions(
            preliminary_match,
            p6_decisions,
            relationship_bindings=relationship_bindings,
            preferred_roles=template.preferred_roles,
        )
        if source_error is None:
            effective_p6 = source_decisions
            (
                required_relationship_refs,
                missing_relationship_evidence,
                relationship_error,
            ) = _required_relationship_path(
                source_decisions=source_decisions,
                relationship_bindings=relationship_bindings,
            )
        else:
            relationship_error = source_error

    plan = template.build_plan(relationship_refs=required_relationship_refs)
    p7 = build_service_1_analysis_requirement_match_v1(plan, effective_p6)
    selected_bindings = {
        ref: dict(relationship_bindings[ref])
        for ref in required_relationship_refs
        if ref in relationship_bindings
    }
    d4_graph = (
        d7_workbook_logical_model.get("relationship_graph")
        if isinstance(d7_workbook_logical_model, Mapping)
        and isinstance(d7_workbook_logical_model.get("relationship_graph"), Mapping)
        else None
    )
    schema_identity = (
        d7_workbook_logical_model.get("schema_identity")
        if isinstance(d7_workbook_logical_model, Mapping)
        and isinstance(d7_workbook_logical_model.get("schema_identity"), Mapping)
        else {}
    )
    p8 = build_service_1_analysis_computability_decision_v1(
        case_id=case_id,
        analysis_plan=plan,
        p6_decisions=list(effective_p6),
        analysis_requirement_match=p7,
        relationship_bindings=selected_bindings,
        d4_graph=d4_graph,
        d7_workbook_logical_model=d7_workbook_logical_model,
        source_artifact_ref=(
            str(d7_workbook_logical_model.get("source_artifact_ref") or "").strip()
            if isinstance(d7_workbook_logical_model, Mapping)
            else None
        ),
        workbook_ref=(
            str(d7_workbook_logical_model.get("workbook_ref") or "").strip()
            if isinstance(d7_workbook_logical_model, Mapping)
            else None
        ),
        schema_fingerprint=(
            str(schema_identity.get("schema_fingerprint") or "").strip() or None
        ),
    )

    if relationship_error is not None:
        technical_status = TECHNICALLY_BLOCKED
        p8_status = p8.status
        p8_reason = relationship_error
    elif missing_relationship_evidence:
        technical_status = TECHNICALLY_NEEDS_EVIDENCE
        p8_status = p8.status
        p8_reason = "CROSS_SHEET_RELATIONSHIP_EVIDENCE_REQUIRED"
    elif p8.status == P8_STATUS_COMPUTABLE:
        technical_status = TECHNICALLY_AVAILABLE
        p8_status = p8.status
        p8_reason = None
    elif p8.status == P8_STATUS_NEEDS_EVIDENCE:
        technical_status = TECHNICALLY_NEEDS_EVIDENCE
        p8_status = p8.status
        p8_reason = p8.reason
    elif p8.status == P8_STATUS_UNSUPPORTED:
        technical_status = TECHNICALLY_UNSUPPORTED
        p8_status = p8.status
        p8_reason = p8.reason
    else:
        technical_status = TECHNICALLY_BLOCKED
        p8_status = p8.status
        p8_reason = p8.reason

    available = technical_status == TECHNICALLY_AVAILABLE
    return Service1DiscoveredAnalysisV1(
        analysis_id=template.analysis_id,
        title=template.title,
        question=template.question,
        plan=plan,
        technical_status=technical_status,
        technically_available=available,
        commercially_requested=commercially_requested,
        commercially_exposed=available and commercially_requested,
        p7_status=p7.status,
        p7_reason=p7.reason,
        p8_status=p8_status,
        p8_reason=p8_reason,
        governed_analysis_input=(p8.governed_analysis_input if available else None),
        missing_role_groups=p7.missing_role_groups,
        required_relationship_refs=required_relationship_refs,
        missing_relationship_evidence=missing_relationship_evidence,
        provenance={
            "source": "CONFIRMED_P6_PLUS_P7_PLUS_P8",
            "catalog_ref": CATALOG_SCHEMA_VERSION,
            "relationship_path_resolution": "OWNER_CONFIRMED_BINDINGS_ONLY",
            "commercial_exposure_is_separate_policy": True,
        },
    )


def _case_id(confirmed_bindings: Mapping[str, Any]) -> str:
    reentry = confirmed_bindings.get("reentry_packet")
    if isinstance(reentry, Mapping) and str(reentry.get("case_id") or "").strip():
        return str(reentry.get("case_id")).strip()
    bridge = confirmed_bindings.get("bridge_packet")
    if isinstance(bridge, Mapping):
        return str(bridge.get("case_id") or "").strip()
    return ""


def _p6_decisions(
    confirmed_bindings: Mapping[str, Any], *, case_id: str
) -> tuple[Service1P6ApprovalDecisionV1, ...]:
    reentry = confirmed_bindings.get("reentry_packet")
    raw_values: Any = reentry.get("p6_decisions") if isinstance(reentry, Mapping) else None
    if raw_values is None:
        gate = confirmed_bindings.get("gate_packet")
        raw_values = gate.get("p6_decisions") if isinstance(gate, Mapping) else ()
    decisions: list[Service1P6ApprovalDecisionV1] = []
    for raw in raw_values or ():
        if isinstance(raw, Service1P6ApprovalDecisionV1):
            decision = raw
        elif isinstance(raw, Mapping):
            if str(raw.get("status") or "") != P6_STATUS_APPROVED:
                continue
            decision = Service1P6ApprovalDecisionV1(
                case_id=str(raw.get("case_id") or "").strip(),
                sheet_ref=str(raw.get("sheet_ref") or "").strip(),
                column_ref=str(raw.get("column_ref") or "").strip(),
                status=P6_STATUS_APPROVED,
                approved_role=str(raw.get("approved_role") or "").strip() or None,
                approved_variable=str(raw.get("approved_variable") or "").strip() or None,
                reason=str(raw.get("reason") or "DISCOVERY_REHYDRATED_APPROVAL").strip(),
                owner_confirmation_question_ref=(
                    str(raw.get("owner_confirmation_question_ref") or "").strip() or None
                ),
                confidence=float(raw["confidence"]) if raw.get("confidence") is not None else None,
                provenance=dict(raw.get("provenance") or {}),
                schema_version=str(raw.get("schema_version") or P6_SCHEMA_VERSION),
            )
        else:
            raise TypeError("p6_decisions must contain mappings or canonical P6 decisions")
        if decision.case_id != case_id:
            raise ValueError("P6 case_id mismatch")
        if decision.status == P6_STATUS_APPROVED:
            decisions.append(decision)
    return tuple(decisions)


def _relationship_bindings(confirmed_bindings: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw in confirmed_bindings.get("confirmed_relationships") or ():
        if not isinstance(raw, Mapping):
            raise TypeError("confirmed_relationships must contain mappings")
        if raw.get("confirmed_by_owner") is not True:
            continue
        left_sheet = str(raw.get("left_sheet_ref") or "").strip()
        left_column = str(raw.get("left_column_ref") or "").strip()
        right_sheet = str(raw.get("right_sheet_ref") or "").strip()
        right_column = str(raw.get("right_column_ref") or "").strip()
        kind = str(raw.get("relationship_kind") or "").strip()
        if not all((left_sheet, left_column, right_sheet, right_column, kind)):
            raise ValueError("confirmed relationship endpoint evidence missing")
        ref = str(raw.get("relationship_ref") or "").strip() or f"{left_sheet}.{left_column}->{right_sheet}.{right_column}"
        if ref in result:
            raise ValueError(f"duplicate confirmed relationship:{ref}")
        result[ref] = {
            "relationship_ref": ref,
            "left_sheet_ref": left_sheet,
            "left_column_ref": left_column,
            "right_sheet_ref": right_sheet,
            "right_column_ref": right_column,
            "relationship_kind": kind,
            "confirmed_by_owner": True,
            "owner_confirmation_event_ref": str(
                raw.get("owner_confirmation_event_ref") or ""
            ).strip(),
            "question_ref": str(raw.get("question_ref") or "").strip(),
            "provenance": dict(raw.get("provenance") or {}),
            "relationship_resolution_authorized": False,
            "join_execution_authorized": False,
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        }
    return result


def _selected_source_decisions(
    match: Service1AnalysisRequirementMatchV1,
    decisions: tuple[Service1P6ApprovalDecisionV1, ...],
    *,
    relationship_bindings: Mapping[str, Mapping[str, Any]],
    preferred_roles: tuple[str, ...] = (),
) -> tuple[tuple[Service1P6ApprovalDecisionV1, ...], str | None]:
    """Choose one coherent P6 evidence set for the requested AnalysisPlan.

    P7 role-groups express admissible evidence, not source preference. F10 may
    therefore project the approved evidence down to one unambiguous source set
    before invoking P8. Selection is structural: explicit template role
    preferences first, then fact-side relationship sources, then minimal sheet
    span. It never changes semantic meaning or invents a relationship.
    """
    candidate_groups: list[tuple[Service1P6ApprovalDecisionV1, ...]] = []
    for group in match.required_role_groups:
        candidates = tuple(
            decision
            for decision in decisions
            if str(decision.approved_role or "").strip() in group
        )
        if not candidates:
            return (), "DISCOVERY_REQUIRED_SOURCE_MISSING"
        candidate_groups.append(candidates)

    fact_sheets = {
        str(binding.get("left_sheet_ref") or "").strip()
        for binding in relationship_bindings.values()
        if binding.get("confirmed_by_owner") is True
        and str(binding.get("relationship_kind") or "").strip() in {"MANY_TO_ONE", "ONE_TO_ONE"}
        and str(binding.get("left_sheet_ref") or "").strip()
    }
    preferred = set(preferred_roles)
    ranked: list[tuple[tuple[int, int, int, int], tuple[Service1P6ApprovalDecisionV1, ...]]] = []
    for raw_combo in product(*candidate_groups):
        unique: list[Service1P6ApprovalDecisionV1] = []
        seen_identity: set[tuple[str, str, str]] = set()
        for decision in raw_combo:
            identity = (
                decision.sheet_ref,
                decision.column_ref,
                str(decision.approved_role or "").strip(),
            )
            if identity not in seen_identity:
                seen_identity.add(identity)
                unique.append(decision)

        valid = True
        by_role: dict[str, set[tuple[str, str]]] = {}
        selected_roles = {str(item.approved_role or "").strip() for item in unique}
        for group in match.required_role_groups:
            matched_roles = {role for role in group if role in selected_roles}
            if len(matched_roles) != 1:
                valid = False
                break
        if not valid:
            continue
        for decision in unique:
            role = str(decision.approved_role or "").strip()
            by_role.setdefault(role, set()).add((decision.sheet_ref, decision.column_ref))
        if any(len(columns) != 1 for columns in by_role.values()):
            continue

        sheets = {item.sheet_ref for item in unique}
        score = (
            sum(1 for item in unique if str(item.approved_role or "").strip() in preferred),
            sum(1 for item in unique if item.sheet_ref in fact_sheets),
            -len(sheets),
            -len(unique),
        )
        ranked.append((score, tuple(unique)))

    if not ranked:
        return (), "DISCOVERY_AMBIGUOUS_REQUIRED_ROLE_GROUP"
    best_score = max(score for score, _items in ranked)
    best = [items for score, items in ranked if score == best_score]
    identities = {
        tuple(sorted((item.sheet_ref, item.column_ref, str(item.approved_role or "")) for item in items))
        for items in best
    }
    if len(identities) != 1:
        return (), "DISCOVERY_AMBIGUOUS_SOURCE_COLUMN"
    return best[0], None


def _required_relationship_path(
    *,
    source_decisions: tuple[Service1P6ApprovalDecisionV1, ...],
    relationship_bindings: Mapping[str, Mapping[str, Any]],
) -> tuple[tuple[str, ...], tuple[str, ...], str | None]:
    sheet_counts = Counter(decision.sheet_ref for decision in source_decisions)
    required_sheets = tuple(sorted(sheet_counts))
    if len(required_sheets) <= 1:
        return (), (), None

    adjacency: dict[str, list[tuple[str, str]]] = {}
    for ref, binding in relationship_bindings.items():
        if binding.get("confirmed_by_owner") is not True:
            continue
        if str(binding.get("relationship_kind") or "") not in {"MANY_TO_ONE", "ONE_TO_ONE"}:
            continue
        left = str(binding.get("left_sheet_ref") or "").strip()
        right = str(binding.get("right_sheet_ref") or "").strip()
        if left and right:
            adjacency.setdefault(left, []).append((right, ref))

    root_candidates = sorted(required_sheets, key=lambda sheet: (-sheet_counts[sheet], sheet))
    for root in root_candidates:
        refs: list[str] = []
        complete = True
        for target in required_sheets:
            if target == root:
                continue
            path, ambiguous = _unique_shortest_relationship_path(root, target, adjacency)
            if ambiguous:
                return (), (), "DISCOVERY_AMBIGUOUS_RELATIONSHIP_PATH"
            if path is None:
                complete = False
                break
            for ref in path:
                if ref not in refs:
                    refs.append(ref)
        if complete:
            return tuple(refs), (), None
    missing = tuple(f"RELATIONSHIP_PATH_REQUIRED:{left}->{right}" for left in required_sheets for right in required_sheets if left < right)
    return (), missing, None


def _unique_shortest_relationship_path(
    start: str,
    target: str,
    adjacency: Mapping[str, list[tuple[str, str]]],
) -> tuple[tuple[str, ...] | None, bool]:
    queue: deque[tuple[str, tuple[str, ...], tuple[str, ...]]] = deque(
        [(start, (), (start,))]
    )
    found: list[tuple[str, ...]] = []
    shortest_length: int | None = None
    while queue:
        sheet, path, visited_sheets = queue.popleft()
        if shortest_length is not None and len(path) >= shortest_length:
            continue
        for next_sheet, ref in sorted(adjacency.get(sheet, ()), key=lambda item: (item[0], item[1])):
            if next_sheet in visited_sheets:
                continue
            next_path = (*path, ref)
            if next_sheet == target:
                if shortest_length is None:
                    shortest_length = len(next_path)
                if len(next_path) == shortest_length and next_path not in found:
                    found.append(next_path)
                continue
            queue.append((next_sheet, next_path, (*visited_sheets, next_sheet)))
    if not found:
        return None, False
    if len(found) > 1:
        return None, True
    return found[0], False


def project_service_1_dynamic_discovery_menu_v1(
    discovery: Service1DynamicAnalysisDiscoveryV1,
) -> dict[str, Any]:
    """Project commercially requested F10 analyses into the existing generic menu shape."""
    if not isinstance(discovery, Service1DynamicAnalysisDiscoveryV1):
        raise TypeError("discovery must be Service1DynamicAnalysisDiscoveryV1")
    if discovery.status != STATUS_READY:
        return {
            "status": "BLOCKED",
            "available": [],
            "blocked": [],
            "blocked_reason": discovery.blocked_reason or "DISCOVERY_NOT_READY",
        }
    available: list[tuple[str, str, str]] = []
    blocked: list[dict[str, Any]] = []
    for item in discovery.analyses:
        if not item.commercially_requested:
            continue
        if item.commercially_exposed:
            available.append((item.analysis_id, item.title, item.question))
            continue
        missing = [" o ".join(group) for group in item.missing_role_groups]
        missing.extend(item.missing_relationship_evidence)
        blocked.append(
            {
                "analysis_id": item.analysis_id,
                "name": item.title,
                "question": item.question,
                "missing_evidence": [value for value in missing if value],
                "why_needed": f"Hace falta para responder de forma trazable: {item.question}",
                "technical_status": item.technical_status,
                "p7_status": item.p7_status,
                "p8_status": item.p8_status,
                "p8_reason": item.p8_reason,
            }
        )
    return {
        "status": "READY",
        "available": available,
        "blocked": blocked,
        "blocked_reason": None,
    }


__all__ = [
    "SCHEMA_VERSION",
    "CATALOG_SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "TECHNICALLY_AVAILABLE",
    "TECHNICALLY_NEEDS_EVIDENCE",
    "TECHNICALLY_UNSUPPORTED",
    "TECHNICALLY_BLOCKED",
    "Service1AnalysisDiscoveryTemplateV1",
    "Service1DiscoveredAnalysisV1",
    "Service1DynamicAnalysisDiscoveryV1",
    "ANALYSIS_DISCOVERY_CATALOG_V1",
    "F12_COMMERCIAL_ANALYSIS_IDS",
    "build_service_1_dynamic_analysis_discovery_v1",
    "project_service_1_dynamic_discovery_menu_v1",
]
