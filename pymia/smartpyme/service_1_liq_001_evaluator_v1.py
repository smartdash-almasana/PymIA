"""Deterministic evaluator for LIQ_001 sold-versus-collected mismatch.

This module evaluates only explicit numeric evidence. It does not infer business
meaning, select data sources, authorize runtime, or generate an autonomous final
diagnosis. The owner-confirmed semantic layer remains responsible for bindings.
"""
from __future__ import annotations

import math
from typing import Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_LIQ_001_EVALUATION_V1"
PATHOLOGY_CODE: Final[str] = "LIQ_001"
FORMULA_REF: Final[str] = "LIQ_001_vendido_cobrado"
CAPABILITY_REF: Final[str] = "sold_vs_collected_gap"

STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"

CLASS_NO_ACTIVITY: Final[str] = "NO_ACTIVITY"
CLASS_NO_GAP: Final[str] = "NO_GAP"
CLASS_SALES_PENDING_COLLECTION: Final[str] = "SALES_PENDING_COLLECTION"
CLASS_COLLECTIONS_EXCEED_PERIOD_SALES: Final[str] = "COLLECTIONS_EXCEED_PERIOD_SALES"
CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES: Final[str] = "COLLECTIONS_WITHOUT_PERIOD_SALES"


def evaluate_liq_001_v1(*, sold_amount: object, collected_amount: object) -> dict[str, object]:
    """Evaluate LIQ_001 from explicit period totals.

    Mathematical domain:
    - both inputs must be finite real numbers;
    - both inputs must be greater than or equal to zero;
    - ``gap = sold_amount - collected_amount``;
    - ratios are undefined when ``sold_amount == 0``.
    """
    normalized, errors = _normalize_inputs(
        sold_amount=sold_amount,
        collected_amount=collected_amount,
    )
    if errors:
        return _packet(
            status=STATUS_INVALID_INPUT,
            classification=None,
            inputs=normalized,
            errors=errors,
        )

    sold = normalized["sold_amount"]
    collected = normalized["collected_amount"]
    gap = sold - collected

    if sold == 0:
        if collected == 0:
            classification = CLASS_NO_ACTIVITY
        else:
            classification = CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES
        collection_ratio = None
        gap_ratio = None
    else:
        collection_ratio = collected / sold
        gap_ratio = gap / sold
        if gap > 0:
            classification = CLASS_SALES_PENDING_COLLECTION
        elif gap == 0:
            classification = CLASS_NO_GAP
        else:
            classification = CLASS_COLLECTIONS_EXCEED_PERIOD_SALES

    return _packet(
        status=STATUS_EVALUATED,
        classification=classification,
        inputs=normalized,
        computed={
            "gap_amount": gap,
            "collection_ratio": collection_ratio,
            "gap_ratio": gap_ratio,
        },
        mathematical_limits={
            "sold_amount_min_inclusive": 0.0,
            "collected_amount_min_inclusive": 0.0,
            "gap_positive_meaning": CLASS_SALES_PENDING_COLLECTION,
            "gap_zero_meaning": CLASS_NO_GAP,
            "gap_negative_meaning": CLASS_COLLECTIONS_EXCEED_PERIOD_SALES,
            "ratios_defined_when": "sold_amount > 0",
        },
    )


def _normalize_inputs(
    *, sold_amount: object, collected_amount: object
) -> tuple[dict[str, float], list[str]]:
    normalized: dict[str, float] = {}
    errors: list[str] = []
    for field_name, value in (
        ("sold_amount", sold_amount),
        ("collected_amount", collected_amount),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{field_name} must be numeric.")
            continue
        number = float(value)
        if not math.isfinite(number):
            errors.append(f"{field_name} must be finite.")
            continue
        normalized[field_name] = number
        if number < 0:
            errors.append(f"{field_name} must be greater than or equal to 0.")
    return normalized, errors


def _packet(
    *,
    status: str,
    classification: str | None,
    inputs: dict[str, float],
    computed: dict[str, object] | None = None,
    mathematical_limits: dict[str, object] | None = None,
    errors: list[str] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pathology_code": PATHOLOGY_CODE,
        "formula_ref": FORMULA_REF,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "classification": classification,
        "inputs": dict(inputs),
        "computed": dict(computed or {}),
        "mathematical_limits": dict(mathematical_limits or {}),
        "errors": list(errors or []),
        "runtime_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "CAPABILITY_REF",
    "CLASS_COLLECTIONS_EXCEED_PERIOD_SALES",
    "CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES",
    "CLASS_NO_ACTIVITY",
    "CLASS_NO_GAP",
    "CLASS_SALES_PENDING_COLLECTION",
    "FORMULA_REF",
    "PATHOLOGY_CODE",
    "SCHEMA_VERSION",
    "STATUS_EVALUATED",
    "STATUS_INVALID_INPUT",
    "evaluate_liq_001_v1",
]
