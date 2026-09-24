"""Declarative commercial analytics for Service 1.

This module is intentionally downstream of canonical XLSX ingestion. It never
opens a workbook, never infers from filenames/rubros, and never grants runtime
or delivery authority. Capability discovery is projected from declarative
requirements plus semantic evidence. Execution is deterministic over canonical
normalized tables after P8-style computability has been established.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time
from math import isfinite
from statistics import mean
from typing import Any, Final, Iterable, Mapping, Sequence

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as SEMANTIC_BRIDGE_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_owner_unit_confirmation_event_v1 import (
    UNIT_DISCOUNT_FRACTION,
    UNIT_DISCOUNT_LINE_AMOUNT,
    UNIT_DISCOUNT_PERCENT,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_COMMERCIAL_ANALYTICS_V1"
DISCOVERY_AVAILABLE: Final[str] = "AVAILABLE"
DISCOVERY_NEEDS_OWNER: Final[str] = "NEEDS_OWNER_CONFIRMATION"
DISCOVERY_NOT_AVAILABLE: Final[str] = "NOT_AVAILABLE"
P8_COMPUTABLE: Final[str] = "COMPUTABLE"
P8_NEEDS_OWNER: Final[str] = "NEEDS_OWNER_CONFIRMATION"
P8_NOT_COMPUTABLE: Final[str] = "NOT_COMPUTABLE"
EXECUTED: Final[str] = "EVALUATED"

SALES_BASIS = (frozenset({"sales_amount"}), frozenset({"quantity", "unit_sale_price"}))
PRODUCT_KEY = (frozenset({"product_identifier"}), frozenset({"product_name"}))
BRANCH_KEY = (frozenset({"branch_identifier"}), frozenset({"branch_name"}))
EMPLOYEE_KEY = (frozenset({"employee_identifier"}), frozenset({"employee_name"}))


@dataclass(frozen=True, slots=True)
class CommercialAnalysisSpecV1:
    capability_ref: str
    owner_label: str
    owner_description: str
    requirement_groups: tuple[tuple[frozenset[str], ...], ...]
    needs_discount_unit: bool = False


def _g(*alternatives: frozenset[str]) -> tuple[frozenset[str], ...]:
    return alternatives


COMMERCIAL_ANALYSES: Final[tuple[CommercialAnalysisSpecV1, ...]] = (
    CommercialAnalysisSpecV1("sales_summary", "Resumen de ventas", "Ventas, unidades, operaciones y ticket según la evidencia disponible.", (_g(*SALES_BASIS),), True),
    CommercialAnalysisSpecV1("gross_margin_by_product", "Margen bruto por producto", "Ventas menos costo de catálogo por producto; no es margen neto.", (_g(*SALES_BASIS), _g(*PRODUCT_KEY), _g(frozenset({"unit_cost_candidate"}))), True),
    CommercialAnalysisSpecV1("product_profitability_ranking", "Productos más y menos rentables", "Ranking determinístico por margen bruto calculable.", (_g(*SALES_BASIS), _g(*PRODUCT_KEY), _g(frozenset({"unit_cost_candidate"}))), True),
    CommercialAnalysisSpecV1("sales_margin_by_branch", "Ventas y margen por sucursal", "Ventas y margen bruto agrupados por sucursal.", (_g(*SALES_BASIS), _g(*BRANCH_KEY), _g(*PRODUCT_KEY), _g(frozenset({"unit_cost_candidate"}))), True),
    CommercialAnalysisSpecV1("branch_comparison", "Comparación entre sucursales", "Comparación homogénea de ventas, unidades y margen bruto entre sucursales.", (_g(*SALES_BASIS), _g(*BRANCH_KEY), _g(*PRODUCT_KEY), _g(frozenset({"unit_cost_candidate"}))), True),
    CommercialAnalysisSpecV1("category_performance", "Rendimiento por categoría", "Ventas, unidades y margen bruto por categoría de producto.", (_g(*SALES_BASIS), _g(*PRODUCT_KEY), _g(frozenset({"commercial_category"}))), True),
    CommercialAnalysisSpecV1("discount_impact", "Impacto de descuentos", "Cuantifica descuento aplicado y diferencia frente al importe bruto.", (_g(frozenset({"quantity", "unit_sale_price", "discount_candidate"})),), True),
    CommercialAnalysisSpecV1("sales_by_employee", "Ventas por empleado", "Ventas, operaciones y ticket agrupados por empleado o vendedor.", (_g(*SALES_BASIS), _g(*EMPLOYEE_KEY)), True),
    CommercialAnalysisSpecV1("sales_channels", "Canales de venta", "Distribución de ventas por canal comercial.", (_g(*SALES_BASIS), _g(frozenset({"sales_channel"}))), True),
    CommercialAnalysisSpecV1("payment_methods", "Medios de pago", "Distribución de ventas por medio de pago.", (_g(*SALES_BASIS), _g(frozenset({"payment_method"}))), True),
    CommercialAnalysisSpecV1("peak_sales_times", "Horas y días de mayor venta", "Identifica concentración temporal por día y hora.", (_g(*SALES_BASIS), _g(frozenset({"operation_date"})), _g(frozenset({"operation_time"}))), True),
    CommercialAnalysisSpecV1("sales_evolution", "Evolución de ventas", "Serie temporal diaria y mensual de ventas.", (_g(*SALES_BASIS), _g(frozenset({"operation_date"}))), True),
    CommercialAnalysisSpecV1("product_concentration", "Concentración de productos", "Participación de cada producto en ventas y unidades.", (_g(*SALES_BASIS), _g(*PRODUCT_KEY)), True),
    CommercialAnalysisSpecV1("catalog_price_control", "Control de precios contra catálogo", "Contrasta precio observado en ventas contra precio del maestro de productos.", (_g(frozenset({"unit_sale_price", "product_identifier"})),)),
    CommercialAnalysisSpecV1("workbook_quality", "Anomalías y calidad del Excel", "Resume señales estructurales y de calidad producidas por la ingesta canónica.", tuple()),
    CommercialAnalysisSpecV1("demand_by_product_branch", "Demanda por producto y sucursal", "Unidades vendidas por producto y sucursal.", (_g(frozenset({"quantity"})), _g(*PRODUCT_KEY), _g(*BRANCH_KEY))),
    CommercialAnalysisSpecV1("commercial_full_report", "Informe comercial completo", "Consolida los análisis comerciales computables sin inventar datos faltantes.", (_g(*SALES_BASIS), _g(*PRODUCT_KEY), _g(*BRANCH_KEY), _g(frozenset({"commercial_category"})), _g(*EMPLOYEE_KEY), _g(frozenset({"sales_channel"})), _g(frozenset({"payment_method"})), _g(frozenset({"operation_date"})), _g(frozenset({"operation_time"})), _g(frozenset({"unit_cost_candidate"}))), True),
)

_SPEC_BY_REF: Final[dict[str, CommercialAnalysisSpecV1]] = {spec.capability_ref: spec for spec in COMMERCIAL_ANALYSES}


@dataclass(frozen=True, slots=True)
class RoleRefV1:
    role: str
    sheet_name: str
    column_name: str
    normalized_column_name: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "sheet_name": self.sheet_name,
            "column_name": self.column_name,
            "normalized_column_name": self.normalized_column_name,
            "confidence": self.confidence,
        }


def list_commercial_analysis_specs_v1() -> tuple[CommercialAnalysisSpecV1, ...]:
    return COMMERCIAL_ANALYSES


def get_commercial_analysis_spec_v1(capability_ref: str) -> CommercialAnalysisSpecV1 | None:
    return _SPEC_BY_REF.get(str(capability_ref or "").strip())


def build_role_inventory_v1(ingestion_output: Mapping[str, Any]) -> dict[str, list[RoleRefV1]]:
    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=dict(ingestion_output),
    )
    if bridge.get("status") != SEMANTIC_BRIDGE_READY:
        return {}
    refs = list(bridge.get("column_refs") or [])
    understandings = list(bridge.get("column_understandings") or [])
    inventory: dict[str, list[RoleRefV1]] = defaultdict(list)
    for ref, raw in zip(refs, understandings):
        item = raw.to_dict() if hasattr(raw, "to_dict") else dict(raw) if isinstance(raw, Mapping) else {}
        primary = item.get("primary_hypothesis") if isinstance(item, Mapping) else None
        if not isinstance(primary, Mapping):
            continue
        role = str(primary.get("semantic_role") or "").strip()
        confidence = float(item.get("confidence") or 0.0)
        if not role or role == "unknown" or confidence < 0.60:
            continue
        inventory[role].append(
            RoleRefV1(
                role=role,
                sheet_name=str(ref.get("sheet_name") or "").strip(),
                column_name=str(ref.get("column_name") or "").strip(),
                normalized_column_name=str(ref.get("normalized_column_name") or ref.get("column_name") or "").strip(),
                confidence=confidence,
            )
        )
    return dict(inventory)


def discover_commercial_analyses_v1(
    *,
    ingestion_output: Mapping[str, Any],
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    inventory = build_role_inventory_v1(ingestion_output)
    roles = frozenset(inventory)
    discount_unit = _discount_unit(owner_unit_confirmation_events)
    analyses: list[dict[str, Any]] = []
    for spec in COMMERCIAL_ANALYSES:
        requirements_ok, missing = _requirements_satisfied(spec, roles)
        if not requirements_ok:
            status = DISCOVERY_NOT_AVAILABLE
        elif spec.needs_discount_unit and "sales_amount" not in roles and "discount_candidate" in roles and _has_nonzero_discount(ingestion_output, inventory) and discount_unit is None:
            status = DISCOVERY_NEEDS_OWNER
        else:
            status = DISCOVERY_AVAILABLE
        analyses.append({
            "capability_ref": spec.capability_ref,
            "label": spec.owner_label,
            "description": spec.owner_description,
            "status": status,
            "missing_evidence_roles": sorted(missing),
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "DISCOVERY_READY",
        "analyses": analyses,
        "available_count": sum(item["status"] == DISCOVERY_AVAILABLE for item in analyses),
        "needs_owner_confirmation_count": sum(item["status"] == DISCOVERY_NEEDS_OWNER for item in analyses),
        "not_available_count": sum(item["status"] == DISCOVERY_NOT_AVAILABLE for item in analyses),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


def build_tabular_p8_decision_v1(
    *,
    ingestion_output: Mapping[str, Any],
    capability_ref: str,
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """P8 authority for declarative tabular analyses.

    This decision only establishes computability from confirmed workbook evidence.
    It does not execute an analysis.
    """
    spec = get_commercial_analysis_spec_v1(capability_ref)
    if spec is None:
        return _p8(P8_NOT_COMPUTABLE, capability_ref, "UNKNOWN_COMMERCIAL_CAPABILITY")
    inventory = build_role_inventory_v1(ingestion_output)
    roles = frozenset(inventory)
    requirements_ok, missing = _requirements_satisfied(spec, roles)
    if not requirements_ok:
        return _p8(P8_NOT_COMPUTABLE, capability_ref, "MISSING_REQUIRED_EVIDENCE", missing=missing)
    if spec.needs_discount_unit and "sales_amount" not in roles and "discount_candidate" in roles and _has_nonzero_discount(ingestion_output, inventory):
        if _discount_unit(owner_unit_confirmation_events) is None:
            return _p8(P8_NEEDS_OWNER, capability_ref, "DISCOUNT_UNIT_CONFIRMATION_REQUIRED", owner_questions=[_discount_question(ingestion_output, inventory)])
    return _p8(P8_COMPUTABLE, capability_ref, None)


def execute_commercial_analysis_v1(
    *,
    ingestion_output: Mapping[str, Any],
    capability_ref: str,
    owner_unit_confirmation_events: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    p8 = build_tabular_p8_decision_v1(
        ingestion_output=ingestion_output,
        capability_ref=capability_ref,
        owner_unit_confirmation_events=owner_unit_confirmation_events,
    )
    if p8["status"] != P8_COMPUTABLE:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": p8["status"],
            "capability_ref": capability_ref,
            "p8_decision": p8,
            "owner_questions": p8.get("owner_questions", []),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "delivery_authorized": False,
        }
    inventory = build_role_inventory_v1(ingestion_output)
    ctx = _Context(ingestion_output, inventory, _discount_unit(owner_unit_confirmation_events))
    dispatcher = {
        "sales_summary": _sales_summary,
        "gross_margin_by_product": _gross_margin_by_product,
        "product_profitability_ranking": _product_profitability_ranking,
        "sales_margin_by_branch": _sales_margin_by_branch,
        "branch_comparison": _branch_comparison,
        "category_performance": _category_performance,
        "discount_impact": _discount_impact,
        "sales_by_employee": _sales_by_employee,
        "sales_channels": _sales_channels,
        "payment_methods": _payment_methods,
        "peak_sales_times": _peak_sales_times,
        "sales_evolution": _sales_evolution,
        "product_concentration": _product_concentration,
        "catalog_price_control": _catalog_price_control,
        "workbook_quality": _workbook_quality,
        "demand_by_product_branch": _demand_by_product_branch,
        "commercial_full_report": _commercial_full_report,
    }
    result = dispatcher[capability_ref](ctx)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": EXECUTED,
        "capability_ref": capability_ref,
        "p8_decision": p8,
        "result": result,
        "limitations": _limitations(capability_ref),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


def _requirements_satisfied(spec: CommercialAnalysisSpecV1, roles: frozenset[str]) -> tuple[bool, set[str]]:
    missing: set[str] = set()
    for group in spec.requirement_groups:
        if any(alt.issubset(roles) for alt in group):
            continue
        best = min(group, key=lambda alt: len(alt - roles)) if group else frozenset()
        missing.update(best - roles)
    return (not missing, missing)


def _p8(status: str, capability_ref: str, reason: str | None, *, missing: Iterable[str] = (), owner_questions: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    return {
        "schema_version": "SERVICE_1_TABULAR_P8_DECISION_V1",
        "status": status,
        "capability_ref": capability_ref,
        "reason": reason,
        "missing_evidence_roles": sorted(set(missing)),
        "owner_questions": [dict(item) for item in owner_questions],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
    }


def _discount_question(ingestion: Mapping[str, Any], inventory: Mapping[str, list[RoleRefV1]]) -> dict[str, Any]:
    ref = (inventory.get("discount_candidate") or [RoleRefV1("discount_candidate", "", "", "", 0.0)])[0]
    case_id = str(ingestion.get("case_id") or "").strip()
    question_ref = f"discount-unit:{case_id}:{ref.sheet_name}:{ref.column_name}"
    return {
        "question_ref": question_ref,
        "question_id": question_ref,
        "question_type": "UNIT_CONFIRMATION",
        "question_kind": "UNIT_MEANING",
        "case_id": case_id,
        "sheet_ref": ref.sheet_name,
        "column_ref": ref.column_name,
        "semantic_role": "discount_candidate",
        "question_text": "¿Cómo está expresado el descuento de esta columna?",
        "options": [
            {"unit_kind": UNIT_DISCOUNT_FRACTION, "label": "Tasa entre 0 y 1", "example": "0,10 = 10%"},
            {"unit_kind": UNIT_DISCOUNT_PERCENT, "label": "Porcentaje entre 0 y 100", "example": "10 = 10%"},
            {"unit_kind": UNIT_DISCOUNT_LINE_AMOUNT, "label": "Importe monetario por línea", "example": "10 = $10 descontados de la línea"},
        ],
    }


def _discount_unit(events: Sequence[Mapping[str, Any]]) -> str | None:
    units = {
        str(item.get("unit_kind") or "").strip()
        for item in events
        if isinstance(item, Mapping)
        and str(item.get("semantic_role") or "").strip() == "discount_candidate"
        and item.get("confirmed_by_owner", True) is True
    }
    units.discard("")
    return next(iter(units)) if len(units) == 1 else None


def _tables(ingestion: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(table.get("sheet_name") or "").strip(): dict(table)
        for table in (ingestion.get("normalized_tables") or [])
        if isinstance(table, Mapping)
    }


def _rows(table: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (table.get("rows") or []) if isinstance(row, Mapping)]


def _has_nonzero_discount(ingestion: Mapping[str, Any], inventory: Mapping[str, list[RoleRefV1]]) -> bool:
    for ref in inventory.get("discount_candidate") or []:
        table = _tables(ingestion).get(ref.sheet_name, {})
        for row in _rows(table):
            value = _num(row.get(ref.normalized_column_name, row.get(ref.column_name)))
            if value is not None and value != 0:
                return True
    return False


class _Context:
    def __init__(self, ingestion: Mapping[str, Any], inventory: Mapping[str, list[RoleRefV1]], discount_unit: str | None) -> None:
        self.ingestion = ingestion
        self.inventory = inventory
        self.tables = _tables(ingestion)
        self.discount_unit = discount_unit
        self.sales_sheet = self._select_sales_sheet()
        self.sales_rows = _rows(self.tables.get(self.sales_sheet, {}))
        self.product_sheet = self._select_product_sheet()
        self.product_rows = _rows(self.tables.get(self.product_sheet, {})) if self.product_sheet else []
        self.branch_sheet = self._select_branch_sheet()
        self.branch_rows = _rows(self.tables.get(self.branch_sheet, {})) if self.branch_sheet else []

    def _select_sales_sheet(self) -> str:
        scores: Counter[str] = Counter()
        for role in ("quantity", "sales_amount", "unit_sale_price", "operation_date", "product_identifier", "sales_channel", "payment_method", "employee_name", "branch_identifier"):
            for ref in self.inventory.get(role) or []:
                scores[ref.sheet_name] += 1
        return scores.most_common(1)[0][0] if scores else next(iter(self.tables), "")

    def _select_product_sheet(self) -> str | None:
        scores: Counter[str] = Counter()
        for role in ("product_identifier", "product_name", "commercial_category", "unit_cost_candidate", "unit_sale_price"):
            for ref in self.inventory.get(role) or []:
                if ref.sheet_name != self.sales_sheet:
                    scores[ref.sheet_name] += 1
        return scores.most_common(1)[0][0] if scores else None

    def _select_branch_sheet(self) -> str | None:
        scores: Counter[str] = Counter()
        for role in ("branch_identifier", "branch_name"):
            for ref in self.inventory.get(role) or []:
                if ref.sheet_name != self.sales_sheet:
                    scores[ref.sheet_name] += 1
        return scores.most_common(1)[0][0] if scores else None

    def ref(self, role: str, sheet: str | None = None) -> RoleRefV1 | None:
        refs = self.inventory.get(role) or []
        if sheet is not None:
            refs = [ref for ref in refs if ref.sheet_name == sheet]
        return max(refs, key=lambda item: item.confidence) if refs else None

    def value(self, row: Mapping[str, Any], role: str, sheet: str | None = None) -> Any:
        ref = self.ref(role, sheet)
        if ref is None:
            return None
        return row.get(ref.normalized_column_name, row.get(ref.column_name))

    def product_lookup(self) -> dict[str, dict[str, Any]]:
        if not self.product_sheet:
            return {}
        key_ref = self.ref("product_identifier", self.product_sheet) or self.ref("product_name", self.product_sheet)
        if key_ref is None:
            return {}
        result: dict[str, dict[str, Any]] = {}
        for row in self.product_rows:
            key = _key(row.get(key_ref.normalized_column_name, row.get(key_ref.column_name)))
            if key:
                result[key] = row
        return result

    def branch_lookup(self) -> dict[str, dict[str, Any]]:
        if not self.branch_sheet:
            return {}
        key_ref = self.ref("branch_identifier", self.branch_sheet) or self.ref("branch_name", self.branch_sheet)
        if key_ref is None:
            return {}
        return {
            key: row
            for row in self.branch_rows
            if (key := _key(row.get(key_ref.normalized_column_name, row.get(key_ref.column_name))))
        }

    def sale_components(self, row: Mapping[str, Any]) -> tuple[float, float, float, float]:
        direct = _num(self.value(row, "sales_amount", self.sales_sheet))
        qty = _num(self.value(row, "quantity", self.sales_sheet))
        price = _num(self.value(row, "unit_sale_price", self.sales_sheet))
        discount = _num(self.value(row, "discount_candidate", self.sales_sheet)) or 0.0
        if direct is not None:
            net = direct
            gross = direct
        elif qty is not None and price is not None:
            gross = qty * price
            net = _apply_discount(gross, discount, self.discount_unit)
        else:
            raise ValueError("sales evidence is not computable")
        return (qty or 0.0, price or 0.0, gross, net)

    def product_key(self, row: Mapping[str, Any]) -> str:
        return _key(self.value(row, "product_identifier", self.sales_sheet) or self.value(row, "product_name", self.sales_sheet))

    def product_record(self, row: Mapping[str, Any]) -> dict[str, Any] | None:
        return self.product_lookup().get(self.product_key(row))

    def cost_for_sale(self, row: Mapping[str, Any]) -> float | None:
        direct = _num(self.value(row, "unit_cost_candidate", self.sales_sheet))
        if direct is not None:
            return direct
        product = self.product_record(row)
        if product is None or not self.product_sheet:
            return None
        return _num(self.value(product, "unit_cost_candidate", self.product_sheet))

    def product_label(self, row: Mapping[str, Any]) -> str:
        product = self.product_record(row)
        if product is not None and self.product_sheet:
            value = self.value(product, "product_name", self.product_sheet) or self.value(product, "product_identifier", self.product_sheet)
            if value is not None:
                return str(value)
        value = self.value(row, "product_name", self.sales_sheet) or self.value(row, "product_identifier", self.sales_sheet)
        return str(value or "Sin identificar")

    def branch_label(self, row: Mapping[str, Any]) -> str:
        raw_key = self.value(row, "branch_identifier", self.sales_sheet) or self.value(row, "branch_name", self.sales_sheet)
        record = self.branch_lookup().get(_key(raw_key))
        if record is not None and self.branch_sheet:
            value = self.value(record, "branch_name", self.branch_sheet) or raw_key
            return str(value)
        return str(raw_key or "Sin identificar")


def _sales_summary(ctx: _Context) -> dict[str, Any]:
    sales = [ctx.sale_components(row) for row in ctx.sales_rows]
    total = sum(item[3] for item in sales)
    units = sum(item[0] for item in sales)
    return {
        "sales_total": _r(total),
        "units_total": _r(units),
        "operations": len(sales),
        "average_ticket": _r(total / len(sales)) if sales else 0.0,
    }


def _gross_margin_rows(ctx: _Context) -> list[dict[str, Any]]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "cost": 0.0, "units": 0.0})
    labels: dict[str, str] = {}
    for row in ctx.sales_rows:
        qty, _price, _gross, net = ctx.sale_components(row)
        cost = ctx.cost_for_sale(row)
        if cost is None:
            continue
        key = ctx.product_key(row)
        labels[key] = ctx.product_label(row)
        acc[key]["sales"] += net
        acc[key]["cost"] += qty * cost
        acc[key]["units"] += qty
    result = []
    for key, values in acc.items():
        margin = values["sales"] - values["cost"]
        result.append({
            "product": labels.get(key, key),
            "units": _r(values["units"]),
            "sales": _r(values["sales"]),
            "catalog_cost": _r(values["cost"]),
            "gross_margin": _r(margin),
            "gross_margin_pct": _r((margin / values["sales"] * 100.0) if values["sales"] else 0.0),
        })
    return sorted(result, key=lambda item: (-item["gross_margin"], item["product"]))


def _gross_margin_by_product(ctx: _Context) -> dict[str, Any]:
    rows = _gross_margin_rows(ctx)
    return {"rows": rows, "total_gross_margin": _r(sum(item["gross_margin"] for item in rows))}


def _product_profitability_ranking(ctx: _Context) -> dict[str, Any]:
    rows = _gross_margin_rows(ctx)
    ascending = sorted(rows, key=lambda item: (item["gross_margin"], item["product"]))
    return {"most_profitable": rows[:10], "least_profitable": ascending[:10]}


def _branch_margin_rows(ctx: _Context) -> list[dict[str, Any]]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "cost": 0.0, "units": 0.0, "operations": 0.0})
    for row in ctx.sales_rows:
        qty, _price, _gross, net = ctx.sale_components(row)
        cost = ctx.cost_for_sale(row)
        label = ctx.branch_label(row)
        acc[label]["sales"] += net
        acc[label]["units"] += qty
        acc[label]["operations"] += 1
        if cost is not None:
            acc[label]["cost"] += qty * cost
    rows = []
    for branch, values in acc.items():
        margin = values["sales"] - values["cost"]
        rows.append({"branch": branch, "sales": _r(values["sales"]), "units": _r(values["units"]), "operations": int(values["operations"]), "catalog_cost": _r(values["cost"]), "gross_margin": _r(margin), "gross_margin_pct": _r(margin / values["sales"] * 100.0) if values["sales"] else 0.0})
    return sorted(rows, key=lambda item: (-item["sales"], item["branch"]))


def _sales_margin_by_branch(ctx: _Context) -> dict[str, Any]:
    return {"rows": _branch_margin_rows(ctx)}


def _branch_comparison(ctx: _Context) -> dict[str, Any]:
    rows = _branch_margin_rows(ctx)
    return {"rows": rows, "leader_by_sales": rows[0]["branch"] if rows else None, "leader_by_gross_margin": max(rows, key=lambda item: item["gross_margin"])["branch"] if rows else None}


def _category_performance(ctx: _Context) -> dict[str, Any]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "cost": 0.0, "units": 0.0})
    for row in ctx.sales_rows:
        qty, _price, _gross, net = ctx.sale_components(row)
        product = ctx.product_record(row)
        category = ctx.value(row, "commercial_category", ctx.sales_sheet)
        if category is None and product is not None and ctx.product_sheet:
            category = ctx.value(product, "commercial_category", ctx.product_sheet)
        label = str(category or "Sin categoría")
        acc[label]["sales"] += net
        acc[label]["units"] += qty
        cost = ctx.cost_for_sale(row)
        if cost is not None:
            acc[label]["cost"] += qty * cost
    rows = []
    for category, values in acc.items():
        margin = values["sales"] - values["cost"]
        rows.append({"category": category, "sales": _r(values["sales"]), "units": _r(values["units"]), "gross_margin": _r(margin), "gross_margin_pct": _r(margin / values["sales"] * 100.0) if values["sales"] else 0.0})
    return {"rows": sorted(rows, key=lambda item: (-item["sales"], item["category"]))}


def _discount_impact(ctx: _Context) -> dict[str, Any]:
    gross = net = discounted_sales = 0.0
    discounted_operations = 0
    for row in ctx.sales_rows:
        _qty, _price, line_gross, line_net = ctx.sale_components(row)
        gross += line_gross
        net += line_net
        if line_net != line_gross:
            discounted_operations += 1
            discounted_sales += line_net
    return {"gross_sales_before_discount": _r(gross), "net_sales_after_discount": _r(net), "discount_value": _r(gross - net), "discounted_operations": discounted_operations, "discounted_sales": _r(discounted_sales), "discount_rate_over_gross_pct": _r((gross - net) / gross * 100.0) if gross else 0.0}


def _group_sales(ctx: _Context, role: str, label_key: str) -> dict[str, Any]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "operations": 0.0, "units": 0.0})
    for row in ctx.sales_rows:
        qty, _price, _gross, net = ctx.sale_components(row)
        label = str(ctx.value(row, role, ctx.sales_sheet) or "Sin identificar")
        acc[label]["sales"] += net
        acc[label]["operations"] += 1
        acc[label]["units"] += qty
    rows = [{label_key: label, "sales": _r(v["sales"]), "operations": int(v["operations"]), "units": _r(v["units"]), "average_ticket": _r(v["sales"] / v["operations"]) if v["operations"] else 0.0} for label, v in acc.items()]
    return {"rows": sorted(rows, key=lambda item: (-item["sales"], str(item[label_key])))}


def _sales_by_employee(ctx: _Context) -> dict[str, Any]:
    role = "employee_identifier" if ctx.ref("employee_identifier", ctx.sales_sheet) else "employee_name"
    return _group_sales(ctx, role, "employee")


def _sales_channels(ctx: _Context) -> dict[str, Any]:
    return _group_sales(ctx, "sales_channel", "channel")


def _payment_methods(ctx: _Context) -> dict[str, Any]:
    return _group_sales(ctx, "payment_method", "payment_method")


def _peak_sales_times(ctx: _Context) -> dict[str, Any]:
    by_day: dict[str, float] = defaultdict(float)
    by_weekday: dict[str, float] = defaultdict(float)
    by_hour: dict[str, float] = defaultdict(float)
    weekday_names = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
    for row in ctx.sales_rows:
        _qty, _price, _gross, net = ctx.sale_components(row)
        d = _date(ctx.value(row, "operation_date", ctx.sales_sheet))
        t = _time(ctx.value(row, "operation_time", ctx.sales_sheet))
        if d is not None:
            by_day[d.isoformat()] += net
            by_weekday[weekday_names[d.weekday()]] += net
        if t is not None:
            by_hour[f"{t.hour:02d}:00"] += net
    return {"top_days": _rank_map(by_day), "top_weekdays": _rank_map(by_weekday), "top_hours": _rank_map(by_hour)}


def _sales_evolution(ctx: _Context) -> dict[str, Any]:
    daily: dict[str, float] = defaultdict(float)
    monthly: dict[str, float] = defaultdict(float)
    for row in ctx.sales_rows:
        _qty, _price, _gross, net = ctx.sale_components(row)
        d = _date(ctx.value(row, "operation_date", ctx.sales_sheet))
        if d is None:
            continue
        daily[d.isoformat()] += net
        monthly[f"{d.year:04d}-{d.month:02d}"] += net
    return {"daily": [{"period": key, "sales": _r(value)} for key, value in sorted(daily.items())], "monthly": [{"period": key, "sales": _r(value)} for key, value in sorted(monthly.items())]}


def _product_concentration(ctx: _Context) -> dict[str, Any]:
    acc: dict[str, dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "units": 0.0})
    labels: dict[str, str] = {}
    for row in ctx.sales_rows:
        qty, _price, _gross, net = ctx.sale_components(row)
        key = ctx.product_key(row)
        labels[key] = ctx.product_label(row)
        acc[key]["sales"] += net
        acc[key]["units"] += qty
    total = sum(v["sales"] for v in acc.values())
    rows = [{"product": labels.get(key, key), "sales": _r(v["sales"]), "units": _r(v["units"]), "sales_share_pct": _r(v["sales"] / total * 100.0) if total else 0.0} for key, v in acc.items()]
    rows.sort(key=lambda item: (-item["sales"], item["product"]))
    return {"rows": rows, "top_product_share_pct": rows[0]["sales_share_pct"] if rows else 0.0}


def _catalog_price_control(ctx: _Context) -> dict[str, Any]:
    if not ctx.product_sheet:
        return {"rows": [], "mismatch_count": 0}
    rows = []
    product_price_ref = ctx.ref("unit_sale_price", ctx.product_sheet)
    for row in ctx.sales_rows:
        sale_price = _num(ctx.value(row, "unit_sale_price", ctx.sales_sheet))
        product = ctx.product_record(row)
        catalog_price = None
        if product is not None and product_price_ref is not None:
            catalog_price = _num(product.get(product_price_ref.normalized_column_name, product.get(product_price_ref.column_name)))
        if sale_price is None or catalog_price is None:
            continue
        delta = sale_price - catalog_price
        if abs(delta) > 1e-9:
            rows.append({"product": ctx.product_label(row), "observed_unit_price": _r(sale_price), "catalog_unit_price": _r(catalog_price), "difference": _r(delta), "difference_pct": _r(delta / catalog_price * 100.0) if catalog_price else None})
    return {"rows": rows, "mismatch_count": len(rows)}


def _workbook_quality(ctx: _Context) -> dict[str, Any]:
    report = ctx.ingestion.get("report") if isinstance(ctx.ingestion.get("report"), Mapping) else {}
    source = ctx.ingestion.get("source_profile") if isinstance(ctx.ingestion.get("source_profile"), Mapping) else {}
    sheet_reports = dict(report.get("sheet_reports") or {}) if isinstance(report, Mapping) else {}
    issues = list(report.get("validation_issues") or []) if isinstance(report, Mapping) else []
    unknown = list(report.get("unknown_fields") or []) if isinstance(report, Mapping) else []
    ambiguous = list(report.get("ambiguous_fields") or []) if isinstance(report, Mapping) else []
    return {"sheet_reports": sheet_reports, "validation_issue_count": len(issues), "unknown_field_count": len(unknown), "ambiguous_field_count": len(ambiguous), "unknown_fields": unknown, "ambiguous_fields": ambiguous, "source_profile": source}


def _demand_by_product_branch(ctx: _Context) -> dict[str, Any]:
    acc: dict[tuple[str, str], float] = defaultdict(float)
    for row in ctx.sales_rows:
        qty = _num(ctx.value(row, "quantity", ctx.sales_sheet)) or 0.0
        acc[(ctx.branch_label(row), ctx.product_label(row))] += qty
    rows = [{"branch": branch, "product": product, "units": _r(units)} for (branch, product), units in acc.items()]
    rows.sort(key=lambda item: (-item["units"], item["branch"], item["product"]))
    return {"rows": rows}


def _commercial_full_report(ctx: _Context) -> dict[str, Any]:
    return {
        "sales_summary": _sales_summary(ctx),
        "gross_margin_by_product": _gross_margin_by_product(ctx),
        "product_profitability_ranking": _product_profitability_ranking(ctx),
        "sales_margin_by_branch": _sales_margin_by_branch(ctx),
        "branch_comparison": _branch_comparison(ctx),
        "category_performance": _category_performance(ctx),
        "discount_impact": _discount_impact(ctx),
        "sales_by_employee": _sales_by_employee(ctx),
        "sales_channels": _sales_channels(ctx),
        "payment_methods": _payment_methods(ctx),
        "peak_sales_times": _peak_sales_times(ctx),
        "sales_evolution": _sales_evolution(ctx),
        "product_concentration": _product_concentration(ctx),
        "catalog_price_control": _catalog_price_control(ctx),
        "workbook_quality": _workbook_quality(ctx),
        "demand_by_product_branch": _demand_by_product_branch(ctx),
    }


def _limitations(capability_ref: str) -> list[str]:
    limitations = ["Los cálculos usan exclusivamente evidencia del workbook ingerido por la ruta canónica."]
    if capability_ref in {"gross_margin_by_product", "product_profitability_ranking", "sales_margin_by_branch", "branch_comparison", "category_performance", "commercial_full_report"}:
        limitations.append("El costo usado es el costo de catálogo/maestro disponible en el archivo; el resultado es margen bruto según esa evidencia, no margen neto contable.")
        limitations.append("No incluye impuestos, retenciones, comisiones u otros gastos no presentes y gobernados en el archivo.")
    return limitations


def _apply_discount(gross: float, discount: float, unit: str | None) -> float:
    if discount == 0:
        return gross
    if unit == UNIT_DISCOUNT_FRACTION:
        if not 0 <= discount <= 1:
            raise ValueError("discount fraction out of range")
        return gross * (1.0 - discount)
    if unit == UNIT_DISCOUNT_PERCENT:
        if not 0 <= discount <= 100:
            raise ValueError("discount percentage out of range")
        return gross * (1.0 - discount / 100.0)
    if unit == UNIT_DISCOUNT_LINE_AMOUNT:
        if discount > gross:
            raise ValueError("discount line amount exceeds gross sale")
        return gross - discount
    raise ValueError("discount unit confirmation required")


def _num(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        return result if isfinite(result) else None
    if isinstance(value, str):
        text = value.strip().replace("$", "").replace(" ", "")
        if not text:
            return None
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        try:
            result = float(text)
        except ValueError:
            return None
        return result if isfinite(result) else None
    return None


def _date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(text[:10], fmt).date()
            except ValueError:
                continue
    return None


def _time(value: Any) -> time | None:
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(text, fmt).time()
            except ValueError:
                continue
    return None


def _key(value: Any) -> str:
    return str(value or "").strip().casefold()


def _rank_map(values: Mapping[str, float], limit: int = 10) -> list[dict[str, Any]]:
    return [{"label": key, "sales": _r(value)} for key, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def _r(value: float) -> float:
    return round(float(value), 6)


__all__ = [
    "SCHEMA_VERSION",
    "DISCOVERY_AVAILABLE",
    "DISCOVERY_NEEDS_OWNER",
    "DISCOVERY_NOT_AVAILABLE",
    "P8_COMPUTABLE",
    "P8_NEEDS_OWNER",
    "P8_NOT_COMPUTABLE",
    "EXECUTED",
    "CommercialAnalysisSpecV1",
    "list_commercial_analysis_specs_v1",
    "get_commercial_analysis_spec_v1",
    "build_role_inventory_v1",
    "discover_commercial_analyses_v1",
    "build_tabular_p8_decision_v1",
    "execute_commercial_analysis_v1",
]
