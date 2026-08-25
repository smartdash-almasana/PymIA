"""Servicio 1 — governed deterministic derived evidence V1.

Builds canonical formula inputs from already-confirmed semantic evidence and
canonical normalized tables. It does not parse XLSX, infer semantics, call an
LLM, execute business formulas, or grant runtime/product/delivery authority.

V1 intentionally implements only the derivations required to close REN_001:
- period sales total from confirmed quantity + unit sale price;
- period costs total from confirmed quantity + owner-confirmed product relation
  + confirmed unit cost.

Taxes are never defaulted to zero. Non-zero discounts are never interpreted as
rate vs amount without additional governed unit evidence.
"""
from __future__ import annotations

from math import isfinite
from typing import Any, Final, Mapping

from pymia.contracts.formula_contract import (
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_owner_unit_confirmation_event_v1 import (
    ALLOWED_UNIT_KINDS,
    SCHEMA_VERSION as OWNER_UNIT_EVENT_SCHEMA_VERSION,
    UNIT_DISCOUNT_FRACTION,
    UNIT_DISCOUNT_LINE_AMOUNT,
    UNIT_DISCOUNT_PERCENT,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_DERIVED_EVIDENCE_V1"
STATUS_READY: Final[str] = "DERIVED_EVIDENCE_READY"
STATUS_NEEDS_EVIDENCE: Final[str] = "DERIVED_EVIDENCE_NEEDS_EVIDENCE"
STATUS_BLOCKED: Final[str] = "BLOCKED"

CAPABILITY_NET_MARGIN: Final[str] = "net_margin_real"
DERIVATION_PERIOD_SALES: Final[str] = "REN_001_PERIOD_SALES_FROM_LINES_V1"
DERIVATION_PERIOD_COSTS: Final[str] = "REN_001_PERIOD_COSTS_FROM_PRODUCT_JOIN_V1"

BLOCK_INPUT_INVALID: Final[str] = "BLOCK_DERIVED_EVIDENCE_INPUT_INVALID"
BLOCK_SEMANTIC_RUN_INVALID: Final[str] = "BLOCK_DERIVED_EVIDENCE_SEMANTIC_RUN_INVALID"
BLOCK_AUTHORITY_FORBIDDEN: Final[str] = "BLOCK_DERIVED_EVIDENCE_AUTHORITY_FORBIDDEN"
BLOCK_CASE_MISMATCH: Final[str] = "BLOCK_DERIVED_EVIDENCE_CASE_MISMATCH"
BLOCK_AMBIGUOUS_COMPONENT_SOURCE: Final[str] = "BLOCK_DERIVED_EVIDENCE_AMBIGUOUS_COMPONENT_SOURCE"
BLOCK_COLUMN_REF_NOT_FOUND: Final[str] = "BLOCK_DERIVED_EVIDENCE_COLUMN_REF_NOT_FOUND"
BLOCK_TABLE_NOT_FOUND: Final[str] = "BLOCK_DERIVED_EVIDENCE_TABLE_NOT_FOUND"
BLOCK_RELATIONSHIP_NOT_CONFIRMED: Final[str] = "BLOCK_DERIVED_EVIDENCE_RELATIONSHIP_NOT_CONFIRMED"
BLOCK_LOOKUP_KEY_DUPLICATE: Final[str] = "BLOCK_DERIVED_EVIDENCE_LOOKUP_KEY_DUPLICATE"
BLOCK_INVALID_NUMERIC_EVIDENCE: Final[str] = "BLOCK_DERIVED_EVIDENCE_INVALID_NUMERIC_EVIDENCE"

NEED_COMPONENT_SEMANTICS: Final[str] = "COMPONENT_SEMANTICS_REQUIRED"
NEED_DISCOUNT_UNIT: Final[str] = "DISCOUNT_UNIT_CONFIRMATION_REQUIRED"
NEED_JOIN_COVERAGE: Final[str] = "PRODUCT_RELATIONSHIP_COVERAGE_INCOMPLETE"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)
_REQUIRED_COMPONENT_ROLES: Final[tuple[str, ...]] = (
    "quantity",
    "unit_sale_price",
    "unit_cost_candidate",
)
_PRODUCT_ROLES: Final[tuple[str, ...]] = ("product_identifier", "product_name")
SEMANTIC_SUPPORT_ROLES_NET_MARGIN: Final[tuple[str, ...]] = (
    "quantity",
    "unit_sale_price",
    "unit_cost_candidate",
    "product_identifier",
    "product_name",
    "discount_candidate",
    "period_sales_total",
    "period_costs_total",
    "period_taxes_total",
    "tax_amount",
)


def service_1_derived_evidence_semantic_support_roles_v1(requested_capability: str) -> tuple[str, ...]:
    """Roles whose confirmed meaning can contribute to a governed derivation."""
    return SEMANTIC_SUPPORT_ROLES_NET_MARGIN if str(requested_capability or "").strip() == CAPABILITY_NET_MARGIN else ()


def service_1_derived_evidence_relevant_column_refs_v1(
    *,
    requested_capability: str,
    deterministic_hypotheses: Any,
) -> tuple[str, ...]:
    """Select only primary semantic refs materially usable by the V1 derivation."""
    if str(requested_capability or "").strip() != CAPABILITY_NET_MARGIN:
        return ()
    rows = [item for item in (deterministic_hypotheses or ()) if isinstance(item, Mapping)]
    by_sheet: dict[str, dict[str, list[str]]] = {}
    for item in rows:
        sheet = str(item.get("sheet_name") or "").strip()
        column = str(item.get("column_name") or "").strip()
        primary = item.get("primary_hypothesis")
        primary = primary if isinstance(primary, Mapping) else None
        confidence = float(item.get("confidence") or 0.0)
        if not sheet or not column or primary is None or confidence < 0.60:
            continue
        role = str(primary.get("semantic_role") or "").strip()
        if not role:
            continue
        by_sheet.setdefault(sheet, {}).setdefault(role, []).append(f"{sheet}.{column}")

    sales_sheets = [
        sheet for sheet, roles in by_sheet.items()
        if roles.get("quantity")
        and roles.get("unit_sale_price")
        and (roles.get("product_identifier") or roles.get("product_name"))
    ]
    cost_sheets = [
        sheet for sheet, roles in by_sheet.items()
        if roles.get("unit_cost_candidate")
        and (roles.get("product_identifier") or roles.get("product_name"))
    ]

    selected: list[str] = []
    if len(sales_sheets) == 1 and len(cost_sheets) == 1:
        sales_sheet = sales_sheets[0]
        cost_sheet = cost_sheets[0]
        sales_roles = by_sheet[sales_sheet]
        cost_roles = by_sheet[cost_sheet]
        shared_product_role = next(
            (
                role for role in _PRODUCT_ROLES
                if sales_roles.get(role) and cost_roles.get(role)
            ),
            None,
        )
        for role in ("quantity", "unit_sale_price", "discount_candidate"):
            selected.extend(sales_roles.get(role) or [])
        selected.extend(cost_roles.get("unit_cost_candidate") or [])
        if shared_product_role:
            selected.extend(sales_roles.get(shared_product_role) or [])
            selected.extend(cost_roles.get(shared_product_role) or [])

    for roles in by_sheet.values():
        for role in ("period_sales_total", "period_costs_total", "period_taxes_total", "tax_amount"):
            selected.extend(roles.get(role) or [])
    return tuple(dict.fromkeys(selected))


def build_service_1_derived_evidence_v1(
    *,
    ingestion_output: Any,
    semantic_run: Any,
    requested_capability: str,
    owner_unit_confirmation_events: Any = (),
) -> dict[str, Any]:
    """Build deterministic derived evidence for one confirmed semantic run."""
    if not isinstance(ingestion_output, dict) or not isinstance(semantic_run, dict):
        return _blocked(BLOCK_INPUT_INVALID)
    capability = str(requested_capability or "").strip()
    workbook_context = ingestion_output.get("workbook_context")
    if not isinstance(workbook_context, dict):
        return _blocked(BLOCK_INPUT_INVALID)
    case_id = str(workbook_context.get("case_id") or "").strip()
    if not capability or not case_id:
        return _blocked(BLOCK_INPUT_INVALID, case_id=case_id or None)
    if any(bool(ingestion_output.get(flag)) for flag in _AUTHORITY_FLAGS) or any(
        bool(semantic_run.get(flag)) for flag in _AUTHORITY_FLAGS
    ):
        return _blocked(BLOCK_AUTHORITY_FORBIDDEN, case_id=case_id)
    if semantic_run.get("status") != "CONFIRMED_BINDINGS":
        return _blocked(BLOCK_SEMANTIC_RUN_INVALID, case_id=case_id)

    bridge = semantic_run.get("bridge_packet") if isinstance(semantic_run.get("bridge_packet"), dict) else {}
    semantic_case = str(bridge.get("case_id") or "").strip()
    if semantic_case and semantic_case != case_id:
        return _blocked(BLOCK_CASE_MISMATCH, case_id=case_id)

    # V1 only derives inputs for REN_001. Other capabilities receive a valid,
    # empty packet; P8 continues to use their direct P6/P7 evidence unchanged.
    if capability != CAPABILITY_NET_MARGIN:
        return _packet(case_id=case_id, capability=capability, derived_variables={})

    p6 = _p6_decisions(semantic_run)
    if not p6:
        return _blocked(BLOCK_SEMANTIC_RUN_INVALID, case_id=case_id)
    approved = [item for item in p6 if str(item.get("status") or "") == "APPROVED"]
    role_map: dict[str, list[dict[str, Any]]] = {}
    for item in approved:
        role = str(item.get("approved_role") or "").strip()
        if role:
            role_map.setdefault(role, []).append(item)

    missing_roles = [role for role in _REQUIRED_COMPONENT_ROLES if not role_map.get(role)]
    product_role = next((role for role in _PRODUCT_ROLES if role_map.get(role)), None)
    if missing_roles or product_role is None:
        return _needs(
            case_id=case_id,
            capability=capability,
            requirements=[NEED_COMPONENT_SEMANTICS],
            detail=missing_roles + ([] if product_role else ["product_identifier|product_name"]),
        )

    quantity = _one(role_map, "quantity")
    price = _one(role_map, "unit_sale_price")
    unit_cost = _one(role_map, "unit_cost_candidate")
    product_decisions = role_map.get(product_role) or []
    if quantity is None or price is None or unit_cost is None:
        return _blocked(BLOCK_AMBIGUOUS_COMPONENT_SOURCE, case_id=case_id)

    sales_sheet = str(quantity.get("sheet_ref") or "").strip()
    if str(price.get("sheet_ref") or "").strip() != sales_sheet:
        return _blocked(BLOCK_AMBIGUOUS_COMPONENT_SOURCE, case_id=case_id, detail=["quantity/price sheet mismatch"])
    sales_product = next(
        (item for item in product_decisions if str(item.get("sheet_ref") or "").strip() == sales_sheet),
        None,
    )
    cost_sheet = str(unit_cost.get("sheet_ref") or "").strip()
    cost_product = next(
        (item for item in product_decisions if str(item.get("sheet_ref") or "").strip() == cost_sheet),
        None,
    )
    if sales_product is None or cost_product is None:
        return _blocked(BLOCK_AMBIGUOUS_COMPONENT_SOURCE, case_id=case_id, detail=["product key source unresolved"])

    refs, ref_error = _column_ref_map(ingestion_output)
    if ref_error:
        return _blocked(BLOCK_COLUMN_REF_NOT_FOUND, case_id=case_id, detail=ref_error)
    tables = _table_map(ingestion_output)
    if sales_sheet not in tables or cost_sheet not in tables:
        return _blocked(BLOCK_TABLE_NOT_FOUND, case_id=case_id)

    quantity_col = _normalized_column(refs, quantity)
    price_col = _normalized_column(refs, price)
    sales_product_col = _normalized_column(refs, sales_product)
    cost_col = _normalized_column(refs, unit_cost)
    cost_product_col = _normalized_column(refs, cost_product)
    if not all((quantity_col, price_col, sales_product_col, cost_col, cost_product_col)):
        return _blocked(BLOCK_COLUMN_REF_NOT_FOUND, case_id=case_id)

    relationship_ref: str | None = None
    if sales_sheet != cost_sheet or sales_product_col != cost_product_col:
        relationship_ref = _confirmed_relationship_ref(
            semantic_run,
            left=(sales_sheet, str(sales_product.get("column_ref") or "").strip()),
            right=(cost_sheet, str(cost_product.get("column_ref") or "").strip()),
        )
        if relationship_ref is None:
            return _blocked(BLOCK_RELATIONSHIP_NOT_CONFIRMED, case_id=case_id)

    discount_decision = _one_on_sheet(role_map, "discount_candidate", sales_sheet)
    discount_col = _normalized_column(refs, discount_decision) if discount_decision is not None else None

    sales_rows = list(tables[sales_sheet].get("rows") or [])
    cost_rows = list(tables[cost_sheet].get("rows") or [])
    if not sales_rows or not cost_rows:
        return _blocked(BLOCK_TABLE_NOT_FOUND, case_id=case_id)

    nonzero_discount_rows: list[int] = []
    if discount_col:
        for row_index, row in enumerate(sales_rows, start=1):
            if not isinstance(row, Mapping):
                return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"sales row {row_index} invalid"])
            parsed_discount = _number(row.get(discount_col), minimum=0.0)
            if parsed_discount is None:
                return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"{sales_sheet}.{discount_col}:{row_index}"])
            if parsed_discount != 0:
                nonzero_discount_rows.append(row_index)

    discount_unit_kind: str | None = None
    discount_unit_question_ref: str | None = None
    if nonzero_discount_rows:
        if discount_decision is None:
            return _blocked(BLOCK_AMBIGUOUS_COMPONENT_SOURCE, case_id=case_id, detail=["discount source unresolved"])
        discount_unit_kind, discount_unit_question_ref, unit_error = _confirmed_discount_unit(
            events=owner_unit_confirmation_events,
            case_id=case_id,
            sheet_ref=sales_sheet,
            column_ref=str(discount_decision.get("column_ref") or "").strip(),
        )
        if unit_error:
            return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[unit_error])
        if discount_unit_kind is None:
            question = _discount_unit_question(
                case_id=case_id,
                sheet_ref=sales_sheet,
                column_ref=str(discount_decision.get("column_ref") or "").strip(),
            )
            return _needs(
                case_id=case_id,
                capability=capability,
                requirements=[NEED_DISCOUNT_UNIT],
                detail=[str(item) for item in nonzero_discount_rows],
                owner_questions=[question],
            )

    cost_lookup: dict[str, float] = {}
    for row_index, row in enumerate(cost_rows, start=1):
        if not isinstance(row, Mapping):
            return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"cost row {row_index} invalid"])
        key = _key(row.get(cost_product_col))
        if not key:
            continue
        if key in cost_lookup:
            return _blocked(BLOCK_LOOKUP_KEY_DUPLICATE, case_id=case_id, detail=[key])
        value = _number(row.get(cost_col), minimum=0.0)
        if value is None:
            return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"{cost_sheet}.{cost_col}:{row_index}"])
        cost_lookup[key] = value
    if not cost_lookup:
        return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=["empty cost lookup"])

    math_engine = FormulaEngineService()
    net_sales_values: list[float] = []
    line_cost_values: list[float] = []
    matched_rows = 0
    unmatched_keys: list[str] = []
    for row_index, row in enumerate(sales_rows, start=1):
        if not isinstance(row, Mapping):
            return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"sales row {row_index} invalid"])
        qty = _number(row.get(quantity_col), minimum=0.0)
        unit_price = _number(row.get(price_col), minimum=0.0)
        if qty is None or unit_price is None:
            return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"{sales_sheet}:{row_index}"])
        key = _key(row.get(sales_product_col))
        unit_cost_value = cost_lookup.get(key)
        if unit_cost_value is None:
            unmatched_keys.append(key or f"row:{row_index}")
            continue

        discount = 0.0
        if discount_col:
            parsed_discount = _number(row.get(discount_col), minimum=0.0)
            if parsed_discount is None:
                return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[f"{sales_sheet}.{discount_col}:{row_index}"])
            discount = parsed_discount
        gross_sale_result = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.MULTIPLY,
                values=[qty, unit_price],
                source_refs=[_qualified(quantity), _qualified(price)],
            )
        )
        if gross_sale_result.status != FormulaStatus.OK or gross_sale_result.value is None:
            return _blocked(
                BLOCK_INVALID_NUMERIC_EVIDENCE,
                case_id=case_id,
                detail=[f"{sales_sheet}:{row_index}:{gross_sale_result.blocking_reason or 'gross sale math blocked'}"],
            )
        net_sale, discount_error = _apply_discount(
            math_engine=math_engine,
            gross_sale=float(gross_sale_result.value),
            discount=discount,
            unit_kind=discount_unit_kind,
            source_refs=[_qualified(quantity), _qualified(price), *([_qualified(discount_decision)] if discount_decision else [])],
        )
        if discount_error:
            return _blocked(
                BLOCK_INVALID_NUMERIC_EVIDENCE,
                case_id=case_id,
                detail=[f"{sales_sheet}.{discount_col or 'discount'}:{row_index}:{discount_error}"],
            )
        cost_result = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.MULTIPLY,
                values=[qty, unit_cost_value],
                source_refs=[_qualified(quantity), _qualified(unit_cost)],
            )
        )
        if cost_result.status != FormulaStatus.OK or cost_result.value is None:
            return _blocked(
                BLOCK_INVALID_NUMERIC_EVIDENCE,
                case_id=case_id,
                detail=[f"{cost_sheet}:{row_index}:{cost_result.blocking_reason or 'cost math blocked'}"],
            )
        net_sales_values.append(net_sale)
        line_cost_values.append(float(cost_result.value))
        matched_rows += 1

    if unmatched_keys:
        return _needs(
            case_id=case_id,
            capability=capability,
            requirements=[NEED_JOIN_COVERAGE],
            detail=sorted(set(unmatched_keys)),
        )
    if matched_rows != len(sales_rows) or matched_rows == 0:
        return _needs(case_id=case_id, capability=capability, requirements=[NEED_JOIN_COVERAGE])

    sales_total_result = math_engine.calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.SUM,
            values=net_sales_values,
            source_refs=[_qualified(quantity), _qualified(price), *([_qualified(discount_decision)] if discount_decision else [])],
        )
    )
    costs_total_result = math_engine.calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.SUM,
            values=line_cost_values,
            source_refs=[_qualified(quantity), _qualified(unit_cost)],
        )
    )
    if sales_total_result.status != FormulaStatus.OK or sales_total_result.value is None:
        return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[sales_total_result.blocking_reason or "sales sum blocked"])
    if costs_total_result.status != FormulaStatus.OK or costs_total_result.value is None:
        return _blocked(BLOCK_INVALID_NUMERIC_EVIDENCE, case_id=case_id, detail=[costs_total_result.blocking_reason or "cost sum blocked"])
    sales_total = float(sales_total_result.value)
    costs_total = float(costs_total_result.value)

    sales_source_refs = [
        _qualified(quantity),
        _qualified(price),
    ]
    costs_source_refs = [
        _qualified(quantity),
        _qualified(sales_product),
        _qualified(cost_product),
        _qualified(unit_cost),
    ]
    if discount_decision is not None:
        sales_source_refs.append(_qualified(discount_decision))

    common_coverage = {
        "source_rows": len(sales_rows),
        "matched_rows": matched_rows,
        "coverage_ratio": 1.0,
    }
    derived_variables = {
        "sale_price": {
            "semantic_role": "period_sales_total",
            "value": sales_total,
            "unit": "currency",
            "derivation_id": DERIVATION_PERIOD_SALES,
            "source_column_refs": sales_source_refs,
            "relationship_refs": [],
            "owner_question_refs": _owner_question_refs((quantity, price, discount_decision)),
            "owner_unit_question_refs": [discount_unit_question_ref] if discount_unit_question_ref else [],
            "governed_parameters": {"discount_unit_kind": discount_unit_kind} if discount_unit_kind else {},
            "row_coverage": dict(common_coverage),
        },
        "costs": {
            "semantic_role": "period_costs_total",
            "value": costs_total,
            "unit": "currency",
            "derivation_id": DERIVATION_PERIOD_COSTS,
            "source_column_refs": costs_source_refs,
            "relationship_refs": [relationship_ref] if relationship_ref else [],
            "owner_question_refs": _owner_question_refs((quantity, sales_product, cost_product, unit_cost)),
            "row_coverage": dict(common_coverage),
        },
    }
    return _packet(case_id=case_id, capability=capability, derived_variables=derived_variables)


def _p6_decisions(semantic_run: Mapping[str, Any]) -> list[dict[str, Any]]:
    reentry = semantic_run.get("reentry_packet") if isinstance(semantic_run.get("reentry_packet"), Mapping) else {}
    values = reentry.get("p6_decisions") or semantic_run.get("p6_decisions") or []
    return [dict(item) for item in values if isinstance(item, Mapping)]


def _one(role_map: Mapping[str, list[dict[str, Any]]], role: str) -> dict[str, Any] | None:
    values = role_map.get(role) or []
    return values[0] if len(values) == 1 else None


def _one_on_sheet(role_map: Mapping[str, list[dict[str, Any]]], role: str, sheet: str) -> dict[str, Any] | None:
    values = [item for item in role_map.get(role) or [] if str(item.get("sheet_ref") or "").strip() == sheet]
    return values[0] if len(values) == 1 else None


def _column_ref_map(ingestion_output: Mapping[str, Any]) -> tuple[dict[tuple[str, str], dict[str, Any]], list[str]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    errors: list[str] = []
    for raw in ingestion_output.get("column_refs") or []:
        if not isinstance(raw, Mapping):
            errors.append("column_ref_not_mapping")
            continue
        identity = (
            str(raw.get("sheet_name") or "").strip(),
            str(raw.get("column_name") or "").strip(),
        )
        if not all(identity) or identity in result:
            errors.append("column_ref_identity_invalid")
            continue
        result[identity] = dict(raw)
    return result, errors


def _normalized_column(refs: Mapping[tuple[str, str], Mapping[str, Any]], decision: Mapping[str, Any] | None) -> str | None:
    if not isinstance(decision, Mapping):
        return None
    identity = (
        str(decision.get("sheet_ref") or "").strip(),
        str(decision.get("column_ref") or "").strip(),
    )
    ref = refs.get(identity)
    if not ref:
        return None
    return str(ref.get("normalized_column_name") or ref.get("column_name") or "").strip() or None


def _table_map(ingestion_output: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw in ingestion_output.get("normalized_tables") or []:
        if isinstance(raw, Mapping):
            sheet = str(raw.get("sheet_name") or "").strip()
            if sheet and sheet not in result:
                result[sheet] = dict(raw)
    return result


def _confirmed_relationship_ref(
    semantic_run: Mapping[str, Any], *, left: tuple[str, str], right: tuple[str, str]
) -> str | None:
    for raw in semantic_run.get("confirmed_relationships") or []:
        if not isinstance(raw, Mapping) or raw.get("confirmed_by_owner") is not True:
            continue
        current_left = (
            str(raw.get("left_sheet_ref") or "").strip(),
            str(raw.get("left_column_ref") or "").strip(),
        )
        current_right = (
            str(raw.get("right_sheet_ref") or "").strip(),
            str(raw.get("right_column_ref") or "").strip(),
        )
        if (current_left == left and current_right == right) or (current_left == right and current_right == left):
            kind = str(raw.get("relationship_kind") or "").strip()
            if not kind:
                continue
            return f"{current_left[0]}.{current_left[1]}->{current_right[0]}.{current_right[1]}:{kind}"
    return None


def _number(value: Any, *, minimum: float | None = None) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    if not isfinite(parsed):
        return None
    if minimum is not None and parsed < minimum:
        return None
    return parsed


def _key(value: Any) -> str:
    return str(value or "").strip()


def _qualified(decision: Mapping[str, Any]) -> str:
    return f"{str(decision.get('sheet_ref') or '').strip()}.{str(decision.get('column_ref') or '').strip()}"


def _owner_question_refs(decisions: tuple[Mapping[str, Any] | None, ...]) -> list[str]:
    refs: list[str] = []
    for decision in decisions:
        if not isinstance(decision, Mapping):
            continue
        ref = str(decision.get("owner_confirmation_question_ref") or "").strip()
        if ref and ref not in refs:
            refs.append(ref)
    return refs


def _confirmed_discount_unit(
    *,
    events: Any,
    case_id: str,
    sheet_ref: str,
    column_ref: str,
) -> tuple[str | None, str | None, str | None]:
    if events is None:
        return None, None, None
    if not isinstance(events, (list, tuple)):
        return None, None, "owner unit confirmation events must be a list"
    matches: list[Mapping[str, Any]] = []
    for raw in events:
        if not isinstance(raw, Mapping):
            return None, None, "owner unit confirmation event must be an object"
        if raw.get("schema_version") != OWNER_UNIT_EVENT_SCHEMA_VERSION:
            return None, None, "owner unit confirmation schema is invalid"
        if any(bool(raw.get(flag)) for flag in _AUTHORITY_FLAGS):
            return None, None, "owner unit confirmation carries forbidden authority"
        if str(raw.get("case_id") or "").strip() != case_id:
            continue
        if str(raw.get("sheet_ref") or "").strip() != sheet_ref:
            continue
        if str(raw.get("column_ref") or "").strip() != column_ref:
            continue
        if str(raw.get("semantic_role") or "").strip() != "discount_candidate":
            continue
        matches.append(raw)
    if len(matches) > 1:
        return None, None, "duplicate owner unit confirmations for discount column"
    if not matches:
        return None, None, None
    event = matches[0]
    if event.get("confirmed_by_owner") is not True:
        return None, None, "owner unit confirmation is not confirmed"
    unit_kind = str(event.get("unit_kind") or "").strip()
    question_ref = str(event.get("question_ref") or "").strip()
    if unit_kind not in ALLOWED_UNIT_KINDS or not question_ref:
        return None, None, "owner unit confirmation is invalid"
    return unit_kind, question_ref, None


def _discount_unit_question(*, case_id: str, sheet_ref: str, column_ref: str) -> dict[str, Any]:
    qualified = f"{sheet_ref}.{column_ref}"
    return {
        "question_id": f"derived-unit:{qualified}",
        "question_kind": "UNIT_MEANING",
        "case_id": case_id,
        "sheet_ref": sheet_ref,
        "column_ref": column_ref,
        "semantic_role": "discount_candidate",
        "presentation_text": f"¿Cómo está expresado el descuento de {qualified}?",
        "materiality_reason": "La unidad cambia el importe neto de venta y debe ser confirmada antes de derivar el margen.",
        "options": [
            {"unit_kind": UNIT_DISCOUNT_FRACTION, "label": "Tasa entre 0 y 1", "example": "0,10 = 10%"},
            {"unit_kind": UNIT_DISCOUNT_PERCENT, "label": "Porcentaje entre 0 y 100", "example": "10 = 10%"},
            {"unit_kind": UNIT_DISCOUNT_LINE_AMOUNT, "label": "Importe monetario por línea", "example": "10 = $10 descontados de la línea"},
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _apply_discount(
    *,
    math_engine: FormulaEngineService,
    gross_sale: float,
    discount: float,
    unit_kind: str | None,
    source_refs: list[str],
) -> tuple[float, str | None]:
    """Select the governed discount convention and delegate all arithmetic to the Math Brain."""
    if discount == 0:
        return gross_sale, None
    if unit_kind == UNIT_DISCOUNT_FRACTION:
        if discount > 1:
            return 0.0, "fraction discount must be between 0 and 1"
        remaining = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.SUBTRACT,
                values=[1.0, discount],
                source_refs=source_refs,
            )
        )
        if remaining.status != FormulaStatus.OK or remaining.value is None:
            return 0.0, remaining.blocking_reason or "discount fraction math blocked"
        net = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.MULTIPLY,
                values=[gross_sale, float(remaining.value)],
                source_refs=source_refs,
            )
        )
    elif unit_kind == UNIT_DISCOUNT_PERCENT:
        if discount > 100:
            return 0.0, "percent discount must be between 0 and 100"
        discount_amount = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.PERCENT_OF,
                values=[gross_sale, discount],
                source_refs=source_refs,
            )
        )
        if discount_amount.status != FormulaStatus.OK or discount_amount.value is None:
            return 0.0, discount_amount.blocking_reason or "discount percent math blocked"
        net = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.SUBTRACT,
                values=[gross_sale, float(discount_amount.value)],
                source_refs=source_refs,
            )
        )
    elif unit_kind == UNIT_DISCOUNT_LINE_AMOUNT:
        if discount > gross_sale:
            return 0.0, "line discount amount cannot exceed gross sale"
        net = math_engine.calculate_math_primitive(
            MathPrimitiveInput(
                operation=MathPrimitiveOperation.SUBTRACT,
                values=[gross_sale, discount],
                source_refs=source_refs,
            )
        )
    else:
        return 0.0, "discount unit confirmation is required"
    if net.status != FormulaStatus.OK or net.value is None:
        return 0.0, net.blocking_reason or "discount math blocked"
    return float(net.value), None


def _packet(*, case_id: str, capability: str, derived_variables: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "requested_capability": capability,
        "derived_variables": {str(key): dict(value) for key, value in derived_variables.items()},
        "derived_variable_count": len(derived_variables),
        "evidence_requirements": [],
        "owner_questions": [],
        "detail": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _needs(
    *,
    case_id: str,
    capability: str,
    requirements: list[str],
    detail: list[str] | None = None,
    owner_questions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = _packet(case_id=case_id, capability=capability, derived_variables={})
    payload["status"] = STATUS_NEEDS_EVIDENCE
    payload["evidence_requirements"] = list(requirements)
    payload["owner_questions"] = [dict(item) for item in (owner_questions or [])]
    payload["detail"] = list(detail or [])
    return payload


def _blocked(reason: str, *, case_id: str | None = None, detail: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "requested_capability": None,
        "derived_variables": {},
        "derived_variable_count": 0,
        "evidence_requirements": [],
        "owner_questions": [],
        "detail": list(detail or []),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_BLOCKED",
    "CAPABILITY_NET_MARGIN",
    "DERIVATION_PERIOD_SALES",
    "DERIVATION_PERIOD_COSTS",
    "NEED_COMPONENT_SEMANTICS",
    "NEED_DISCOUNT_UNIT",
    "NEED_JOIN_COVERAGE",
    "build_service_1_derived_evidence_v1",
]
