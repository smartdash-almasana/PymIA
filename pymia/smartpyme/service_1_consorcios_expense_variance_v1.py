"""Deterministic expense variance review for Consorcios.

Aggregates actual expenses by rubro and compares them with owner-confirmed
monthly budget and historical average. It does not perform accounting
classification or autonomous approval.
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

SCHEMA_VERSION: Final[str] = "SERVICE_1_CONSORCIOS_EXPENSE_VARIANCE_V1"
CAPABILITY_REF: Final[str] = "consorcios_expense_variance"
STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_BLOCKED: Final[str] = "BLOCKED"
FORMULA_BUDGET_VARIANCE: Final[str] = "CONSORCIOS_expense_variance_budget_pct"
FORMULA_HISTORICAL_VARIANCE: Final[str] = "CONSORCIOS_expense_variance_historical_pct"
CLASSIFICATION_HIGH: Final[str] = "ALTO"
CLASSIFICATION_MODERATE: Final[str] = "MODERADO"
CLASSIFICATION_NORMAL: Final[str] = "NORMAL"
_CLASSIFICATION_RULES: Final[tuple[ClassificationRule, ...]] = (
    ClassificationRule(
        CLASSIFICATION_HIGH,
        predicates=(ClassificationPredicate("result", "GE", literal=Decimal("50")),),
    ),
    ClassificationRule(
        CLASSIFICATION_MODERATE,
        predicates=(ClassificationPredicate("result", "GE", literal=Decimal("25")),),
    ),
    ClassificationRule(
        CLASSIFICATION_NORMAL,
        predicates=(ClassificationPredicate("result", "GE", literal=Decimal("0")),),
    ),
)


def build_expense_variance_product_request_v1(*, request: object) -> dict[str, Any]:
    if not isinstance(request, Mapping) or not request:
        return _blocked("EXPENSE_VARIANCE_REQUEST_REQUIRED")
    if request.get("owner_requested") is not True:
        return _blocked("EXPLICIT_OWNER_REQUEST_REQUIRED")
    case_id = str(request.get("case_id") or "").strip()
    if not case_id:
        return _blocked("CASE_ID_REQUIRED")
    governance = request.get("governance")
    if not isinstance(governance, dict):
        return _blocked("GOVERNANCE_PACKET_REQUIRED")
    if governance.get("p5_status") != "CONFIRMED":
        return _blocked("P5_CONFIRMATION_REQUIRED")
    decisions = governance.get("p6_decisions")
    if not isinstance(decisions, list) or not decisions:
        return _blocked("P6_DECISIONS_REQUIRED")
    approved = {
        str(item.get("column_ref") or "").strip()
        for item in decisions
        if isinstance(item, dict) and item.get("status") == "APPROVED"
    }
    if governance.get("p7_status") != "REQUIREMENT_MATCHED":
        return _blocked("P7_REQUIREMENT_MATCH_REQUIRED")
    if governance.get("p8_status") != "COMPUTABLE":
        return _blocked("P8_COMPUTABILITY_REQUIRED")
    if any(governance.get(flag) is True for flag in (
        "runtime_authorized", "tool_execution_authorized", "product_ready",
        "delivery_authorized", "diagnosis_generated",
    )):
        return _blocked("GOVERNANCE_FLAGS_FORBIDDEN")

    expense_rows = request.get("expense_rows")
    budget_rows = request.get("budget_rows")
    if not isinstance(expense_rows, list) or not expense_rows:
        return _blocked("EXPENSE_ROWS_REQUIRED")
    if not isinstance(budget_rows, list) or not budget_rows:
        return _blocked("BUDGET_ROWS_REQUIRED")

    expense_bindings = request.get("expense_bindings")
    budget_bindings = request.get("budget_bindings")
    if not isinstance(expense_bindings, dict) or not isinstance(budget_bindings, dict):
        return _blocked("FIELD_BINDINGS_REQUIRED")

    required_expense = ("rubro", "importe")
    required_budget = (
        "rubro", "presupuesto_mensual", "promedio_historico"
    )
    expense_sources = [str(expense_bindings.get(key) or "").strip() for key in required_expense]
    budget_sources = [str(budget_bindings.get(key) or "").strip() for key in required_budget]
    if any(not value for value in [*expense_sources, *budget_sources]):
        return _blocked("REQUIRED_FIELD_BINDING_MISSING")
    if not set([*expense_sources, *budget_sources]).issubset(approved):
        return _blocked("BOUND_COLUMNS_NOT_P6_APPROVED")

    computation = evaluate_expense_variance_v1(
        expense_rows=expense_rows,
        budget_rows=budget_rows,
        expense_bindings=dict(zip(required_expense, expense_sources)),
        budget_bindings=dict(zip(required_budget, budget_sources)),
    )
    if computation.get("status") != STATUS_EVALUATED:
        return _blocked(str(computation.get("reason") or computation.get("status")))
    outcome = build_expense_variance_outcome_v1(computation_result=computation)
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "case_id": case_id,
        "status": "EXPENSE_VARIANCE_REVIEW_READY",
        "computation_result": computation,
        "bounded_outcome": outcome,
        "requires_human_review": True,
        "next_allowed_action": "human_expense_variance_review",
        **_safety_flags(),
    }


def evaluate_expense_variance_v1(
    *,
    expense_rows: list[dict[str, Any]],
    budget_rows: list[dict[str, Any]],
    expense_bindings: dict[str, str],
    budget_bindings: dict[str, str],
) -> dict[str, Any]:
    actual_values_by_rubro: dict[str, list[Decimal]] = {}
    engine = FormulaEngineService()
    try:
        for index, row in enumerate(expense_rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"expense row {index} invalid")
            rubro = str(row.get(expense_bindings["rubro"]) or "").strip()
            if not rubro:
                raise ValueError(f"expense row {index}: rubro required")
            amount = _number(row.get(expense_bindings["importe"]))
            if amount < 0:
                raise ValueError(f"expense row {index}: importe must be >= 0")
            actual_values_by_rubro.setdefault(rubro, []).append(amount)

        results: list[dict[str, Any]] = []
        budget_seen: set[str] = set()
        for index, row in enumerate(budget_rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"budget row {index} invalid")
            rubro = str(row.get(budget_bindings["rubro"]) or "").strip()
            if not rubro:
                raise ValueError(f"budget row {index}: rubro required")
            if rubro in budget_seen:
                raise ValueError(f"duplicate budget rubro: {rubro}")
            budget_seen.add(rubro)
            budget = _number(row.get(budget_bindings["presupuesto_mensual"]))
            historical = _number(row.get(budget_bindings["promedio_historico"]))
            if budget <= 0 or historical <= 0:
                raise ValueError(f"budget row {index}: invalid baseline")
            actual_result = engine.calculate_math_primitive(
                MathPrimitiveInput(
                    operation=MathPrimitiveOperation.SUM,
                    values=actual_values_by_rubro.get(rubro, [Decimal("0")]),
                    source_refs=[f"expense:{rubro}:importe"],
                )
            )
            if actual_result.status != FormulaStatus.OK or actual_result.value is None:
                raise ValueError(actual_result.blocking_reason or "expense aggregation blocked")
            actual = actual_result.value
            budget_result = calculate_formula(
                FORMULA_BUDGET_VARIANCE,
                [
                    FormulaInput(name="actual", value=actual, source_refs=[f"expense:{rubro}:actual"]),
                    FormulaInput(name="baseline", value=float(budget), source_refs=[f"budget:{rubro}:monthly"]),
                ],
            )
            historical_result = calculate_formula(
                FORMULA_HISTORICAL_VARIANCE,
                [
                    FormulaInput(name="actual", value=actual, source_refs=[f"expense:{rubro}:actual"]),
                    FormulaInput(name="baseline", value=float(historical), source_refs=[f"budget:{rubro}:historical"]),
                ],
            )
            if (
                budget_result.status != FormulaStatus.OK
                or budget_result.value is None
                or historical_result.status != FormulaStatus.OK
                or historical_result.value is None
            ):
                raise ValueError(
                    budget_result.blocking_reason
                    or historical_result.blocking_reason
                    or "expense variance formula blocked"
                )
            max_result = engine.calculate_math_primitive(
                MathPrimitiveInput(
                    operation=MathPrimitiveOperation.MAX,
                    values=[0.0, budget_result.value, historical_result.value],
                    source_refs=[
                        f"expense:{rubro}:budget_variance",
                        f"expense:{rubro}:historical_variance",
                    ],
                )
            )
            if max_result.status != FormulaStatus.OK or max_result.value is None:
                raise ValueError(max_result.blocking_reason or "expense deviation maximum blocked")
            classification = classify_classification_rules(
                _CLASSIFICATION_RULES,
                result=max_result.value,
            )
            if classification is None:
                raise ValueError("expense variance classification policy did not match")
            results.append({
                "rubro": rubro,
                "gasto_real": float(actual),
                "presupuesto_mensual": float(budget),
                "promedio_historico": float(historical),
                "desvio_presupuesto_pct": float(budget_result.value),
                "desvio_promedio_pct": float(historical_result.value),
                "umbral_moderado_pct": 25.0,
                "umbral_alto_pct": 50.0,
                "classification": classification,
                "requires_human_review": classification != "NORMAL",
            })
    except (ValueError, InvalidOperation) as exc:
        return {"schema_version": SCHEMA_VERSION, "capability_ref": CAPABILITY_REF, "status": STATUS_BLOCKED, "reason": str(exc), **_safety_flags()}

    summary_counts = {
        classification: _count_results(results, classification)
        for classification in (
            CLASSIFICATION_HIGH,
            CLASSIFICATION_MODERATE,
            CLASSIFICATION_NORMAL,
        )
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "status": STATUS_EVALUATED,
        "rows": results,
        "summary": {
            "total_rubros": len(results),
            "alto": summary_counts[CLASSIFICATION_HIGH],
            "moderado": summary_counts[CLASSIFICATION_MODERATE],
            "normal": summary_counts[CLASSIFICATION_NORMAL],
        },
        "method": "actual_by_rubro_vs_budget_and_confirmed_historical_average",
        "limitations": [
            "El desvío es matemático y no determina por sí solo si el gasto es correcto, necesario o extraordinario.",
            "La comparación depende de la calidad del presupuesto y del promedio histórico confirmados.",
            "No clasifica gastos contable ni fiscalmente y requiere revisión humana.",
        ],
        **_safety_flags(),
    }


def build_expense_variance_outcome_v1(*, computation_result: object) -> dict[str, Any]:
    if not isinstance(computation_result, dict) or computation_result.get("status") != STATUS_EVALUATED:
        return {"status": STATUS_BLOCKED, "capability_ref": CAPABILITY_REF}
    flagged = [row for row in computation_result.get("rows", []) if isinstance(row, dict) and row.get("classification") != "NORMAL"]
    return {
        "status": "OUTCOME_READY",
        "capability_ref": CAPABILITY_REF,
        "finding": f"Se identificaron {len(flagged)} rubros con desvío sobre el umbral confirmado.",
        "rows": flagged,
        "computed_results": dict(computation_result.get("summary") or {}),
        "limitations": list(computation_result.get("limitations") or []),
        "forbidden_claims": [
            "Afirmar gasto indebido, fraude o responsabilidad causal sin evidencia adicional.",
            "Aprobar o rechazar pagos automáticamente.",
        ],
        **_safety_flags(),
    }


def _number(value: object) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError("numeric value required")
    number = Decimal(str(value).strip())
    if not number.is_finite():
        raise ValueError("numeric value must be finite")
    return number


def _count_results(results: list[dict[str, Any]], classification: str) -> int:
    count = FormulaEngineService().calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.COUNT,
            values=[1 for row in results if row.get("classification") == classification],
            source_refs=[f"expense:classification:{classification}"],
        )
    )
    if count.status != FormulaStatus.OK or count.value is None:
        raise ValueError(count.blocking_reason or "expense classification count blocked")
    return int(count.value)


def _safety_flags() -> dict[str, bool]:
    return {
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "capability_ref": CAPABILITY_REF,
        "status": STATUS_BLOCKED,
        "reason": reason,
        "requires_human_review": True,
        **_safety_flags(),
    }


__all__ = [
    "SCHEMA_VERSION",
    "CAPABILITY_REF",
    "STATUS_EVALUATED",
    "build_expense_variance_product_request_v1",
    "evaluate_expense_variance_v1",
    "build_expense_variance_outcome_v1",
]
