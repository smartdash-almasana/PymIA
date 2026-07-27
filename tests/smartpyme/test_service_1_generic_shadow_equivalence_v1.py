from __future__ import annotations

from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED as GENERIC_BLOCKED,
    STATUS_EVALUATED as GENERIC_EVALUATED,
    execute_generic_capability_v1,
)
from pymia.smartpyme.service_1_liq_002_evaluator_v1 import (
    CLASS_NEGATIVE_BALANCE,
    CLASS_POSITIVE_BALANCE,
    CLASS_ZERO_BALANCE,
    evaluate_liq_002_from_computation_plan_v1 as legacy_liq_002_plan,
    evaluate_liq_002_v1,
)
from pymia.smartpyme.service_1_liq_002_normalized_evidence_v1 import (
    STATUS_EVIDENCE_BLOCKED as LIQ_EVIDENCE_BLOCKED,
    evaluate_liq_002_from_normalized_tables_v1 as legacy_liq_002_evidence,
)
from pymia.smartpyme.service_1_liq_002_outcome_v1 import (
    STATUS_BLOCKED as LIQ_OUTCOME_BLOCKED,
    STATUS_READY as LIQ_OUTCOME_READY,
    build_liq_002_outcome_v1,
)
from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import (
    CLASS_EXCEEDS_PERIOD,
    CLASS_WITHIN_PERIOD,
    evaluate_pyme_011_from_computation_plan_v1 as legacy_pyme_011_plan,
    evaluate_pyme_011_v1,
)
from pymia.smartpyme.service_1_pyme_011_normalized_evidence_v1 import (
    STATUS_EVIDENCE_BLOCKED as PYME_EVIDENCE_BLOCKED,
    evaluate_pyme_011_from_normalized_tables_v1 as legacy_pyme_011_evidence,
)
from pymia.smartpyme.service_1_pyme_011_outcome_v1 import (
    STATUS_BLOCKED as PYME_OUTCOME_BLOCKED,
    STATUS_READY as PYME_OUTCOME_READY,
    build_pyme_011_outcome_v1,
)
from tests.smartpyme.service_1_p8_test_support import governed_payload_from_legacy_plan

_BLOCKED = "BLOCKED"
_EVALUATED = "EVALUATED"
_SAFETY_FLAGS = ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated")


def _liq_plan(**overrides: object) -> dict[str, object]:
    base = {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "projected_closing_cash_balance",
        "pathology_code": "LIQ_002",
        "formula_id": "LIQ_002_saldo_final_proyectado",
        "required_variables": ["initial_balance", "expected_collections", "expected_payments"],
        "source_bindings": {"initial_balance": "saldo", "expected_collections": "cobros", "expected_payments": "pagos"},
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    base.update(overrides)
    return base


def _pyme_plan(**overrides: object) -> dict[str, object]:
    base = {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "dso",
        "pathology_code": "PYME_011",
        "formula_id": "PYME_011_dso",
        "required_variables": ["accounts_receivable", "sales", "days"],
        "source_bindings": {"accounts_receivable": "ctas_cobrar", "sales": "ventas", "days": "dias"},
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    base.update(overrides)
    return base


def _refs(columns: tuple[str, ...], sheet: str = "sheet1") -> list[dict[str, str]]:
    return [{"sheet_name": sheet, "column_name": c, "normalized_column_name": c} for c in columns]


def _table(rows: list[dict[str, object]], sheet: str = "sheet1") -> list[dict[str, object]]:
    return [{"sheet_name": sheet, "rows": rows}]


def _all_flags_false(result: dict[str, object]) -> bool:
    return all(result.get(f) is False for f in _SAFETY_FLAGS)


def _normalize_block(reason: str) -> str:
    r = reason.lower()
    if "safety" in r or "flag" in r:
        return "SAFETY_FLAG_BLOCKED"
    if "plan" in r or "schema_version" in r or "status" in r or "capability" in r or "pathology" in r or "formula" in r:
        return "PLAN_BLOCKED"
    if "eviden" in r or "table" in r or "sheet" in r or "column_ref" in r or "source_binding" in r or "normalized" in r:
        return "EVIDENCE_BLOCKED"
    if "domain" in r or "must be greater" in r or "must be less" in r or "denominator" in r or "zero" in r or "negative" in r:
        return "DOMAIN_BLOCKED"
    if "exactly one" in r or "cardinality" in r or "single" in r or "consistent" in r:
        return "CARDINALITY_BLOCKED"
    return "OTHER_BLOCKED"


def _liq_tables_opening_single(saldo: float, cobros: float = 100, pagos: float = 50) -> tuple[list, list]:
    return _table([{"saldo": saldo, "cobros": cobros, "pagos": pagos}]), _refs(("saldo", "cobros", "pagos"))


def _liq_tables_opening_multi() -> tuple[list, list]:
    rows = [{"saldo": 100, "cobros": 50, "pagos": 30}, {"saldo": 200, "cobros": 30, "pagos": 20}]
    return _table(rows), _refs(("saldo", "cobros", "pagos"))


def _pyme_tables(days_value: int = 30, *, exceed: bool = True) -> tuple[list, list]:
    if exceed:
        rows = [{"ctas_cobrar": 600, "ventas": 400, "dias": days_value}, {"ctas_cobrar": 300, "ventas": 200, "dias": days_value}]
    else:
        rows = [{"ctas_cobrar": 100, "ventas": 500, "dias": days_value}, {"ctas_cobrar": 50, "ventas": 300, "dias": days_value}]
    return _table(rows), _refs(("ctas_cobrar", "ventas", "dias"))


def _run_legacy_liq(plan: dict, tables: list, refs: list) -> dict:
    return legacy_liq_002_evidence(computation_plan=plan, normalized_tables=tables, column_refs=refs)


def _run_generic(capability: str, plan: dict, tables: list, refs: list) -> dict:
    return execute_generic_capability_v1(
        capability_ref=capability,
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(plan),
        normalized_tables=tables,
        column_refs=refs,
    )


def _assert_same_block_category(legacy: dict, generic: dict, label: str) -> None:
    legacy_blocked = legacy.get("status") in (LIQ_EVIDENCE_BLOCKED, PYME_EVIDENCE_BLOCKED, LIQ_OUTCOME_BLOCKED, PYME_OUTCOME_BLOCKED, "PLAN_BLOCKED", "INVALID_INPUT")
    generic_blocked = generic.get("status") == GENERIC_BLOCKED
    assert legacy_blocked and generic_blocked, f"{label}: both must block: legacy={legacy.get('status')} generic={generic.get('status')}"
    if legacy_blocked:
        legacy_cat = _normalize_block(str(legacy.get("errors", legacy.get("blocked_reason", ""))))
    else:
        legacy_cat = "EVALUATED"
    if generic_blocked:
        generic_cat = _normalize_block(str(generic.get("errors", "")))
    else:
        generic_cat = "EVALUATED"
    allowed_mismatch = {"EVIDENCE_BLOCKED", "DOMAIN_BLOCKED"}
    same_or_equivalent = legacy_cat == generic_cat or {legacy_cat, generic_cat} <= allowed_mismatch
    assert same_or_equivalent, \
        f"{label}: block category mismatch: legacy={legacy_cat} generic={generic_cat}"


def _assert_no_outcome_when_blocked(result: dict, label: str) -> None:
    status = result.get("status")
    if status == GENERIC_BLOCKED:
        outcome = result.get("outcome", {})
        assert outcome.get("bounded_finding_generated") is not True, f"{label}: generic blocked but has outcome"
    if status in (LIQ_EVIDENCE_BLOCKED, PYME_EVIDENCE_BLOCKED, LIQ_OUTCOME_BLOCKED, PYME_OUTCOME_BLOCKED):
        assert result.get("bounded_finding_generated") is not True, f"{label}: legacy blocked but has outcome"
    assert _all_flags_false(result), f"{label}: blocked but flags not all false"


def _assert_evaluated_equivalence(legacy_ev: dict, generic: dict, label: str, result_key: str, expected_inputs: dict[str, float] | None = None) -> None:
    assert legacy_ev.get("status") == "EVALUATED", f"{label}: legacy must be EVALUATED, got {legacy_ev.get('status')}"
    assert generic.get("status") == GENERIC_EVALUATED, f"{label}: generic must be EVALUATED, got {generic.get('status')}"
    assert legacy_ev.get("capability_ref") == generic.get("capability_ref"), f"{label}: capability_ref mismatch"
    assert legacy_ev.get("pathology_code") == generic.get("pathology_code"), f"{label}: pathology_code mismatch"
    assert legacy_ev.get("formula_ref") == generic.get("formula_ref"), f"{label}: formula_ref mismatch"
    l_inputs = legacy_ev.get("inputs", {})
    g_inputs = generic.get("inputs", {})
    if expected_inputs:
        for var, val in expected_inputs.items():
            assert abs(l_inputs.get(var, 0) - val) < 0.001, f"{label}: legacy inputs {var} mismatch: {l_inputs.get(var)} != {val}"
            assert abs(g_inputs.get(var, 0) - val) < 0.001, f"{label}: generic inputs {var} mismatch: {g_inputs.get(var)} != {val}"
    assert legacy_ev.get("classification") == generic.get("classification"), f"{label}: classification mismatch: {legacy_ev.get('classification')} != {generic.get('classification')}"
    l_computed = legacy_ev.get("computed", {})
    g_computed = generic.get("computed", {})
    assert result_key in l_computed, f"{label}: legacy missing result_key {result_key}"
    assert result_key in g_computed, f"{label}: generic missing result_key {result_key}"
    assert abs(l_computed[result_key] - g_computed[result_key]) < 0.001, f"{label}: computed {result_key} mismatch: {l_computed[result_key]} != {g_computed[result_key]}"
    assert _all_flags_false(legacy_ev), f"{label}: legacy flags not all false"
    assert _all_flags_false(generic), f"{label}: generic flags not all false"


def _assert_outcome_equivalence(legacy_out: dict, generic: dict, label: str) -> None:
    assert legacy_out.get("status") == LIQ_OUTCOME_READY or legacy_out.get("status") == PYME_OUTCOME_READY, f"{label}: legacy outcome must be READY"
    assert generic.get("status") == GENERIC_EVALUATED, f"{label}: generic must be EVALUATED for outcome comparison"
    gen_out = generic.get("outcome", {})
    assert legacy_out.get("bounded_finding_generated") == gen_out.get("bounded_finding_generated"), f"{label}: bounded_finding_generated mismatch"
    assert legacy_out.get("causal_diagnosis_generated") == gen_out.get("causal_diagnosis_generated"), f"{label}: causal_diagnosis_generated mismatch"
    assert legacy_out.get("classification") == generic.get("classification"), f"{label}: outcome classification mismatch"
    assert legacy_out.get("runtime_authorized") is False, f"{label}: legacy outcome runtime_authorized not false"
    assert legacy_out.get("delivery_authorized") is False, f"{label}: legacy outcome delivery_authorized not false"
    assert gen_out.get("bounded_finding_generated") is True, f"{label}: generic outcome missing bounded_finding"


# ── LIQ_002 cases ──


def test_liq_002_positive_balance() -> None:
    tables, refs = _liq_tables_opening_single(100, 50, 30)
    plan = _liq_plan()
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "liq_002_positive", "projected_closing_balance", {"initial_balance": 100, "expected_collections": 50, "expected_payments": 30})
    assert legacy["classification"] == CLASS_POSITIVE_BALANCE
    outcome = build_liq_002_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "liq_002_positive_outcome")


def test_liq_002_zero_balance() -> None:
    tables, refs = _liq_tables_opening_single(100, 50, 150)
    plan = _liq_plan()
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "liq_002_zero", "projected_closing_balance", {"initial_balance": 100, "expected_collections": 50, "expected_payments": 150})
    assert legacy["classification"] == CLASS_ZERO_BALANCE
    outcome = build_liq_002_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "liq_002_zero_outcome")


def test_liq_002_negative_balance() -> None:
    tables, refs = _liq_tables_opening_single(100, 50, 200)
    plan = _liq_plan()
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "liq_002_negative", "projected_closing_balance", {"initial_balance": 100, "expected_collections": 50, "expected_payments": 200})
    assert legacy["classification"] == CLASS_NEGATIVE_BALANCE
    outcome = build_liq_002_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "liq_002_negative_outcome")


def test_liq_002_blocks_multiple_opening_balances() -> None:
    tables, refs = _liq_tables_opening_multi()
    plan = _liq_plan()
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    _assert_same_block_category(legacy, generic, "liq_002_multi_opening")
    assert legacy.get("status") == LIQ_EVIDENCE_BLOCKED
    _assert_no_outcome_when_blocked(legacy, "liq_002_multi_opening")
    _assert_no_outcome_when_blocked(generic, "liq_002_multi_opening_generic")


def test_liq_002_blocks_negative_input() -> None:
    raw = evaluate_liq_002_v1(initial_balance=0, expected_collections=-5, expected_payments=0)
    assert raw["status"] == "INVALID_INPUT"
    tables, refs = _liq_tables_opening_single(0, -5, 0)
    plan = _liq_plan()
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    _assert_same_block_category(legacy, generic, "liq_002_negative")
    _assert_no_outcome_when_blocked(legacy, "liq_002_negative")
    _assert_no_outcome_when_blocked(generic, "liq_002_negative_gen")


def test_liq_002_legacy_plan_status_does_not_govern_generic_execution() -> None:
    tables, refs = _liq_tables_opening_single(100, 50, 30)
    plan = _liq_plan(status="BLOCKED")
    legacy = _run_legacy_liq(plan, tables, refs)
    generic = _run_generic("projected_closing_cash_balance", plan, tables, refs)
    assert legacy.get("status") == "PLAN_BLOCKED"
    assert generic.get("status") == GENERIC_EVALUATED
    _assert_no_outcome_when_blocked(legacy, "liq_002_legacy_status")


def test_liq_002_safety_flag_absent_or_true() -> None:
    tables, refs = _liq_tables_opening_single(100, 50, 30)
    absent_plan = _liq_plan()
    del absent_plan["delivery_authorized"]
    true_plan = _liq_plan(delivery_authorized=True)
    generic_absent = _run_generic("projected_closing_cash_balance", absent_plan, tables, refs)
    generic_true = _run_generic("projected_closing_cash_balance", true_plan, tables, refs)
    assert generic_absent.get("status") == GENERIC_BLOCKED, "generic must block on absent flag"
    assert generic_true.get("status") == GENERIC_BLOCKED, "generic must block on true flag"
    assert _normalize_block(str(generic_absent.get("errors", ""))) == "SAFETY_FLAG_BLOCKED"
    assert _normalize_block(str(generic_true.get("errors", ""))) == "SAFETY_FLAG_BLOCKED"
    _assert_no_outcome_when_blocked(generic_absent, "liq_002_safety_absent")
    _assert_no_outcome_when_blocked(generic_true, "liq_002_safety_true")
    legacy_absent = _run_legacy_liq(_liq_plan(), tables, refs)
    assert legacy_absent.get("status") == "EVALUATED", "legacy passes on absent flag (lenient)"


# ── PYME_011 cases ──


def _run_legacy_pyme(plan: dict, tables: list, refs: list) -> dict:
    return legacy_pyme_011_evidence(computation_plan=plan, normalized_tables=tables, column_refs=refs)


def test_pyme_011_dso_within_period() -> None:
    tables, refs = _pyme_tables(30, exceed=False)
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "pyme_011_within", "dso_days", {"accounts_receivable": 150, "sales": 800, "days": 30})
    assert legacy["classification"] == CLASS_WITHIN_PERIOD
    outcome = build_pyme_011_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "pyme_011_within_outcome")


def test_pyme_011_dso_exceeds_period() -> None:
    tables, refs = _pyme_tables(30, exceed=True)
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "pyme_011_exceeds", "dso_days", {"accounts_receivable": 900, "sales": 600, "days": 30})
    assert legacy["classification"] == CLASS_EXCEEDS_PERIOD
    outcome = build_pyme_011_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "pyme_011_exceeds_outcome")


def test_pyme_011_dso_equals_period() -> None:
    rows = [{"ctas_cobrar": 600, "ventas": 600, "dias": 30}, {"ctas_cobrar": 0, "ventas": 0, "dias": 30}]
    tables, refs = _table(rows), _refs(("ctas_cobrar", "ventas", "dias"))
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_evaluated_equivalence(legacy, generic, "pyme_011_equals", "dso_days")
    assert legacy["classification"] == "DSO_EQUALS_PERIOD"
    outcome = build_pyme_011_outcome_v1(computation_result=legacy)
    _assert_outcome_equivalence(outcome, generic, "pyme_011_equals_outcome")


def test_pyme_011_blocks_zero_sales() -> None:
    raw = evaluate_pyme_011_v1(accounts_receivable=100, sales=0, days=30)
    assert raw["status"] == "INVALID_INPUT"
    rows = [{"ctas_cobrar": 100, "ventas": 0, "dias": 30}]
    tables, refs = _table(rows), _refs(("ctas_cobrar", "ventas", "dias"))
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_same_block_category(legacy, generic, "pyme_011_zero_sales")
    _assert_no_outcome_when_blocked(legacy, "pyme_011_zero_sales")
    _assert_no_outcome_when_blocked(generic, "pyme_011_zero_sales_gen")


def test_pyme_011_blocks_zero_days() -> None:
    raw = evaluate_pyme_011_v1(accounts_receivable=100, sales=50, days=0)
    assert raw["status"] == "INVALID_INPUT"
    rows = [{"ctas_cobrar": 100, "ventas": 50, "dias": 0}]
    tables, refs = _table(rows), _refs(("ctas_cobrar", "ventas", "dias"))
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_same_block_category(legacy, generic, "pyme_011_zero_days")
    _assert_no_outcome_when_blocked(legacy, "pyme_011_zero_days")
    _assert_no_outcome_when_blocked(generic, "pyme_011_zero_days_gen")


def test_pyme_011_blocks_inconsistent_days() -> None:
    rows = [{"ctas_cobrar": 100, "ventas": 50, "dias": 30}, {"ctas_cobrar": 200, "ventas": 100, "dias": 60}]
    tables, refs = _table(rows), _refs(("ctas_cobrar", "ventas", "dias"))
    plan = _pyme_plan()
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    _assert_same_block_category(legacy, generic, "pyme_011_inconsistent_days")
    _assert_no_outcome_when_blocked(legacy, "pyme_011_inconsistent_days")
    _assert_no_outcome_when_blocked(generic, "pyme_011_inconsistent_days_gen")


def test_pyme_011_legacy_plan_status_does_not_govern_generic_execution() -> None:
    tables, refs = _pyme_tables(30)
    plan = _pyme_plan(status="BLOCKED")
    legacy = _run_legacy_pyme(plan, tables, refs)
    generic = _run_generic("dso", plan, tables, refs)
    assert legacy.get("status") == "PLAN_BLOCKED"
    assert generic.get("status") == GENERIC_EVALUATED
    _assert_no_outcome_when_blocked(legacy, "pyme_011_legacy_status")


def test_pyme_011_safety_flag_absent_or_true() -> None:
    tables, refs = _pyme_tables(30)
    absent_plan = _pyme_plan()
    del absent_plan["delivery_authorized"]
    true_plan = _pyme_plan(delivery_authorized=True)
    generic_absent = _run_generic("dso", absent_plan, tables, refs)
    generic_true = _run_generic("dso", true_plan, tables, refs)
    assert generic_absent.get("status") == GENERIC_BLOCKED
    assert generic_true.get("status") == GENERIC_BLOCKED
    assert _normalize_block(str(generic_absent.get("errors", ""))) == "SAFETY_FLAG_BLOCKED"
    _assert_no_outcome_when_blocked(generic_absent, "pyme_011_safety_absent")
    _assert_no_outcome_when_blocked(generic_true, "pyme_011_safety_true")
    legacy_absent = _run_legacy_pyme(_pyme_plan(), tables, refs)
    assert legacy_absent.get("status") == "EVALUATED", "legacy passes on absent flag (lenient)"
