from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import assume, given, settings, strategies as st

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.storage import load_intake_record_by_id, save_intake_record


FINITE_FLOATS = st.floats(
    min_value=-1_000_000.0,
    max_value=1_000_000.0,
    allow_nan=False,
    allow_infinity=False,
)
SAFE_IDENTIFIERS = st.from_regex(r"[a-z][a-z0-9_-]{0,8}", fullmatch=True)


@settings(max_examples=50)
@given(FINITE_FLOATS)
def test_fail_closed_for_unknown_formula(value: float) -> None:
    service = FormulaEngineService()

    result = service.calculate(
        "unknown_formula_from_property_test",
        [FormulaInput(name="value", value=value)],
    )

    assert result.status is FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "FORMULA_NOT_SUPPORTED"

    incomplete = service.calculate(
        "ganancia_bruta",
        [FormulaInput(name="ventas", value=value)],
    )

    assert incomplete.status is FormulaStatus.BLOCKED
    assert incomplete.value is None
    assert incomplete.blocking_reason == "MISSING_INPUTS: costos"


@settings(max_examples=50)
@given(FINITE_FLOATS, FINITE_FLOATS)
def test_formula_calculation_is_deterministic(ventas: float, costos: float) -> None:
    service = FormulaEngineService()
    inputs = [
        FormulaInput(name="ventas", value=ventas, source_refs=["property:ventas"]),
        FormulaInput(name="costos", value=costos, source_refs=["property:costos"]),
    ]

    first = service.calculate("ganancia_bruta", inputs)
    second = service.calculate("ganancia_bruta", inputs)

    assert first.model_dump() == second.model_dump()


@settings(max_examples=50)
@given(st.lists(st.integers(min_value=-1_000, max_value=1_000), min_size=1, max_size=20))
def test_sum_is_invariant_under_reordering(values: list[int]) -> None:
    service = FormulaEngineService()
    original = service.calculate_math_primitive(
        MathPrimitiveInput(operation=MathPrimitiveOperation.SUM, values=values)
    )
    reordered = service.calculate_math_primitive(
        MathPrimitiveInput(operation=MathPrimitiveOperation.SUM, values=list(reversed(values)))
    )

    assert original.model_dump() == reordered.model_dump()


def _intake_record(tenant_id: str, intake_id: str) -> dict[str, object]:
    return {
        "intake_id": intake_id,
        "tenant_id": tenant_id,
        "raw_input": "property test intake",
        "structured_selectors": {},
        "interrogation_result": {},
        "tank_selection_result": {},
        "evidence_requests": [],
        "intake_state": "RECEIVED",
        "suggested_next_state": "REQUEST_EVIDENCE",
        "warnings": [],
        "audit_notes": [],
        "created_at": "2026-01-01T00:00:00+00:00",
    }


@settings(max_examples=30)
@given(SAFE_IDENTIFIERS, SAFE_IDENTIFIERS, SAFE_IDENTIFIERS)
def test_tenant_storage_does_not_cross_read(
    tenant_a: str,
    tenant_b: str,
    intake_id: str,
) -> None:
    assume(tenant_a != tenant_b)

    with TemporaryDirectory() as base_dir:
        record = _intake_record(tenant_a, intake_id)
        save_intake_record(tenant_a, record, base_dir=Path(base_dir))

        assert load_intake_record_by_id(tenant_b, intake_id, base_dir=Path(base_dir)) is None
        with pytest.raises(ValueError, match="does not match"):
            save_intake_record(tenant_b, record, base_dir=Path(base_dir))
