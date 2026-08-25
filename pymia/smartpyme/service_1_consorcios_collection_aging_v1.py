"""Deterministic collection-aging estimate by consorcio unit.

The capability uses owner-confirmed normalized evidence only. It estimates
period-equivalent debt from prior balance divided by the current monthly charge.
It does not claim certified days past due or legal delinquency age.
"""
from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any, Final

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
    calculate_formula,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_capability_contracts_v1 import (
    ClassificationPredicate,
    ClassificationRule,
    classify_classification_rules,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_CONSORCIOS_COLLECTION_AGING_V1"
CAPABILITY_REF: Final[str] = "collection_aging"
STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_EVIDENCE_BLOCKED: Final[str] = "EVIDENCE_BLOCKED"
FORMULA_AGING_PERIODS: Final[str] = "CONSORCIOS_collection_aging_periods"
CLASS_CURRENT: Final[str] = "CURRENT"
CLASS_ONE_PERIOD: Final[str] = "ONE_PERIOD_EQUIVALENT"
CLASS_TWO_PERIODS: Final[str] = "TWO_PERIODS_EQUIVALENT"
CLASS_THREE_PLUS: Final[str] = "THREE_PLUS_PERIODS_EQUIVALENT"
AGING_ONE_PERIOD_MAX_EXCLUSIVE: Final[Decimal] = Decimal("1.4")
AGING_TWO_PERIOD_MAX_EXCLUSIVE: Final[Decimal] = Decimal("2.4")
_AGING_CLASSIFICATION_RULES: Final[tuple[ClassificationRule, ...]] = (
    ClassificationRule(
        CLASS_CURRENT,
        predicates=(ClassificationPredicate("result", "LE", literal=Decimal("0")),),
    ),
    ClassificationRule(
        CLASS_ONE_PERIOD,
        match="ALL",
        predicates=(
            ClassificationPredicate("result", "GT", literal=Decimal("0")),
            ClassificationPredicate("result", "LT", literal=AGING_ONE_PERIOD_MAX_EXCLUSIVE),
        ),
    ),
    ClassificationRule(
        CLASS_TWO_PERIODS,
        match="ALL",
        predicates=(
            ClassificationPredicate("result", "GE", literal=AGING_ONE_PERIOD_MAX_EXCLUSIVE),
            ClassificationPredicate("result", "LT", literal=AGING_TWO_PERIOD_MAX_EXCLUSIVE),
        ),
    ),
    ClassificationRule(
        CLASS_THREE_PLUS,
        predicates=(ClassificationPredicate("result", "GE", literal=AGING_TWO_PERIOD_MAX_EXCLUSIVE),),
    ),
)

REQUIRED_COLUMNS: Final[tuple[str, str, str]] = (
    "unidad_funcional",
    "saldo_anterior",
    "expensa_mes",
)


def evaluate_collection_aging_from_normalized_tables_v1(*, normalized_tables: object) -> dict[str, Any]:
    if not isinstance(normalized_tables, list) or not normalized_tables:
        return _blocked("normalized_tables must be a non-empty list")

    candidates: list[dict[str, Any]] = []
    for table in normalized_tables:
        if not isinstance(table, dict):
            continue
        rows = table.get("rows")
        if not isinstance(rows, list) or not rows:
            continue
        headers = set()
        for row in rows:
            if isinstance(row, dict):
                headers.update(str(key) for key in row.keys())
        if all(column in headers for column in REQUIRED_COLUMNS):
            candidates.append(table)

    if len(candidates) != 1:
        return _blocked(
            "exactly one normalized table must contain unidad_funcional, saldo_anterior and expensa_mes"
        )

    table = candidates[0]
    rows = table["rows"]
    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"row {index} must be an object")
            continue
        unit = str(row.get("unidad_funcional") or "").strip()
        if not unit:
            errors.append(f"row {index}: unidad_funcional is required")
            continue
        prior, prior_error = _number(row.get("saldo_anterior"))
        charge, charge_error = _number(row.get("expensa_mes"))
        if prior_error:
            errors.append(f"row {index} {unit}: saldo_anterior {prior_error}")
            continue
        if charge_error:
            errors.append(f"row {index} {unit}: expensa_mes {charge_error}")
            continue
        if prior < 0:
            errors.append(f"row {index} {unit}: saldo_anterior must be >= 0")
            continue
        if charge <= 0:
            errors.append(f"row {index} {unit}: expensa_mes must be > 0")
            continue

        formula_result = calculate_formula(
            FORMULA_AGING_PERIODS,
            [
                FormulaInput(
                    name="prior_balance",
                    value=float(prior),
                    source_refs=[f"aging:{unit}:prior_balance"],
                ),
                FormulaInput(
                    name="monthly_charge",
                    value=float(charge),
                    source_refs=[f"aging:{unit}:monthly_charge"],
                ),
            ],
        )
        if formula_result.status != FormulaStatus.OK or formula_result.value is None:
            errors.append(
                f"row {index} {unit}: {formula_result.blocking_reason or 'aging formula blocked'}"
            )
            continue
        equivalent_periods = formula_result.value
        bucket = classify_classification_rules(
            _AGING_CLASSIFICATION_RULES,
            result=equivalent_periods,
        )
        if bucket is None:
            errors.append(f"row {index} {unit}: aging classification policy did not match")
            continue
        results.append(
            {
                "unidad_funcional": unit,
                "saldo_anterior": float(prior),
                "expensa_mes": float(charge),
                "periodos_equivalentes": equivalent_periods,
                "aging_bucket": bucket,
                "requires_human_review": bucket != CLASS_CURRENT,
            }
        )

    if errors:
        return _blocked("; ".join(errors[:20]))

    summary = {
        "total_units": len(results),
        "current": _count_bucket(results, CLASS_CURRENT),
        "one_period": _count_bucket(results, CLASS_ONE_PERIOD),
        "two_periods": _count_bucket(results, CLASS_TWO_PERIODS),
        "three_plus_periods": _count_bucket(results, CLASS_THREE_PLUS),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "status": STATUS_EVALUATED,
        "sheet_name": str(table.get("sheet_name") or ""),
        "rows": results,
        "summary": summary,
        "method": "prior_balance_divided_by_current_month_charge",
        "bucket_thresholds": {
            "one_period_max_exclusive": float(AGING_ONE_PERIOD_MAX_EXCLUSIVE),
            "two_periods_max_exclusive": float(AGING_TWO_PERIOD_MAX_EXCLUSIVE),
        },
        "limitations": [
            "Los períodos equivalentes son una estimación matemática, no antigüedad contable certificada.",
            "Para afirmar días o meses exactos de mora se requiere fecha de vencimiento histórica o detalle de deuda por período.",
            "La capacidad no determina incobrabilidad, responsabilidad ni acciones legales.",
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def build_collection_aging_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict) or computation_result.get("status") != STATUS_EVALUATED:
        return {"status": "BLOCKED", "capability_ref": CAPABILITY_REF}
    summary = dict(computation_result.get("summary") or {})
    rows = [
        row
        for row in computation_result.get("rows", [])
        if isinstance(row, dict)
    ]
    flagged = _count_flagged_rows(rows)
    return {
        "status": "OUTCOME_READY",
        "capability_ref": CAPABILITY_REF,
        "finding": f"Se identificaron {flagged} unidades con saldo anterior y estimación de períodos equivalentes de deuda.",
        "computed_results": summary,
        "rows": list(computation_result.get("rows") or []),
        "limitations": list(computation_result.get("limitations") or []),
        "forbidden_claims": [
            "Afirmar días exactos de mora sin evidencia histórica de vencimientos.",
            "Afirmar incobrabilidad o iniciar acciones automáticas.",
        ],
        "runtime_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _count_bucket(results: list[dict[str, Any]], bucket: str) -> int:
    count = FormulaEngineService().calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.COUNT,
            values=[1 for item in results if item.get("aging_bucket") == bucket],
            source_refs=[f"aging:bucket:{bucket}"],
        )
    )
    if count.status != FormulaStatus.OK or count.value is None:
        raise ValueError(count.blocking_reason or "aging bucket count blocked")
    return int(count.value)


def _count_flagged_rows(results: list[dict[str, Any]]) -> int:
    count = FormulaEngineService().calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.COUNT,
            values=[1 for item in results if item.get("aging_bucket") != CLASS_CURRENT],
            source_refs=["aging:non_current"],
        )
    )
    if count.status != FormulaStatus.OK or count.value is None:
        raise ValueError(count.blocking_reason or "aging flagged count blocked")
    return int(count.value)


def _number(value: object) -> tuple[Decimal, str | None]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0"), "is required"
    if isinstance(value, bool):
        return Decimal("0"), "must be numeric"
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0"), "must be numeric"
    if not number.is_finite():
        return Decimal("0"), "must be finite"
    return number, None


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "status": STATUS_EVIDENCE_BLOCKED,
        "reason": reason,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def build_collection_aging_product_request_v1(*, request: object) -> dict[str, Any]:
    """Validate one owner-confirmed aging request and evaluate it deterministically."""
    if not isinstance(request, Mapping) or not request:
        return _request_blocked("AGING_REQUEST_REQUIRED")
    if request.get("owner_requested") is not True:
        return _request_blocked("EXPLICIT_OWNER_REQUEST_REQUIRED")
    case_id = str(request.get("case_id") or "").strip()
    if not case_id:
        return _request_blocked("CASE_ID_REQUIRED")
    governance = request.get("governance")
    if not isinstance(governance, dict):
        return _request_blocked("GOVERNANCE_PACKET_REQUIRED")
    if governance.get("p5_status") != "CONFIRMED":
        return _request_blocked("P5_CONFIRMATION_REQUIRED")
    decisions = governance.get("p6_decisions")
    if not isinstance(decisions, list) or not decisions:
        return _request_blocked("P6_DECISIONS_REQUIRED")
    approved = {
        str(item.get("column_ref") or "").strip()
        for item in decisions
        if isinstance(item, dict) and item.get("status") == "APPROVED"
    }
    bindings = request.get("field_bindings")
    if not isinstance(bindings, dict):
        return _request_blocked("FIELD_BINDINGS_REQUIRED")
    source_columns = [str(bindings.get(name) or "").strip() for name in REQUIRED_COLUMNS]
    if any(not value for value in source_columns):
        return _request_blocked("REQUIRED_FIELD_BINDING_MISSING")
    if not set(source_columns).issubset(approved):
        return _request_blocked("BOUND_COLUMNS_NOT_P6_APPROVED")
    if governance.get("p7_status") != "REQUIREMENT_MATCHED":
        return _request_blocked("P7_REQUIREMENT_MATCH_REQUIRED")
    if governance.get("p8_status") != "COMPUTABLE":
        return _request_blocked("P8_COMPUTABILITY_REQUIRED")
    if any(governance.get(flag) is True for flag in (
        "runtime_authorized", "tool_execution_authorized", "product_ready",
        "delivery_authorized", "diagnosis_generated",
    )):
        return _request_blocked("GOVERNANCE_FLAGS_FORBIDDEN")
    rows = request.get("rows")
    if not isinstance(rows, list) or not rows:
        return _request_blocked("SOURCE_ROWS_REQUIRED")
    projected: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            return _request_blocked(f"SOURCE_ROW_INVALID:{index}")
        projected.append({
            canonical: row.get(source)
            for canonical, source in zip(REQUIRED_COLUMNS, source_columns)
        })
    computation = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[{"sheet_name": str(request.get("sheet_name") or "Expensas"), "rows": projected}]
    )
    if computation.get("status") != STATUS_EVALUATED:
        return _request_blocked(str(computation.get("reason") or computation.get("status")))
    outcome = build_collection_aging_outcome_v1(computation_result=computation)
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "case_id": case_id,
        "status": "AGING_REVIEW_READY",
        "computation_result": computation,
        "bounded_outcome": outcome,
        "requires_human_review": True,
        "next_allowed_action": "human_collection_aging_review",
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _request_blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "status": "BLOCKED",
        "reason": reason,
        "requires_human_review": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "CAPABILITY_REF",
    "STATUS_EVALUATED",
    "STATUS_EVIDENCE_BLOCKED",
    "evaluate_collection_aging_from_normalized_tables_v1",
    "build_collection_aging_outcome_v1",
    "build_collection_aging_product_request_v1",
]
