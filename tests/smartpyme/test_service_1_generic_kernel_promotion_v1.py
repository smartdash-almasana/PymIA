from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import list_capability_refs_v1
from pymia.smartpyme.service_1_generic_capability_engine_v1 import execute_generic_capability_v1
from pymia.smartpyme.service_1_liq_002_evaluator_v1 import evaluate_liq_002_v1
from pymia.smartpyme.service_1_liq_002_normalized_evidence_v1 import evaluate_liq_002_from_normalized_tables_v1
from pymia.smartpyme.service_1_liq_002_outcome_v1 import STATUS_READY as LIQ_002_OUTCOME_READY, build_liq_002_outcome_v1
from pymia.smartpyme.service_1_pyme_011_evaluator_v1 import evaluate_pyme_011_v1
from pymia.smartpyme.service_1_pyme_011_normalized_evidence_v1 import evaluate_pyme_011_from_normalized_tables_v1
from pymia.smartpyme.service_1_pyme_011_outcome_v1 import STATUS_READY as PYME_011_OUTCOME_READY, build_pyme_011_outcome_v1


def _plan(capability: str) -> dict[str, object]:
    base = {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    if capability == "projected_closing_cash_balance":
        base["requested_capability"] = "projected_closing_cash_balance"
        base["pathology_code"] = "LIQ_002"
        base["formula_id"] = "LIQ_002_saldo_final_proyectado"
        base["required_variables"] = ["initial_balance", "expected_collections", "expected_payments"]
        base["source_bindings"] = {
            "initial_balance": "saldo",
            "expected_collections": "cobros",
            "expected_payments": "pagos",
        }
    else:
        base["requested_capability"] = "dso"
        base["pathology_code"] = "PYME_011"
        base["formula_id"] = "PYME_011_dso"
        base["required_variables"] = ["accounts_receivable", "sales", "days"]
        base["source_bindings"] = {
            "accounts_receivable": "ctas_cobrar",
            "sales": "ventas",
            "days": "dias",
        }
    return base


def _liq_tables() -> tuple[list[dict], list[dict]]:
    tables = [{"sheet_name": "sheet1", "rows": [{"saldo": 100, "cobros": 50, "pagos": 30}]}]
    refs = [
        {"sheet_name": "sheet1", "column_name": "saldo", "normalized_column_name": "saldo"},
        {"sheet_name": "sheet1", "column_name": "cobros", "normalized_column_name": "cobros"},
        {"sheet_name": "sheet1", "column_name": "pagos", "normalized_column_name": "pagos"},
    ]
    return tables, refs


def _pyme_tables() -> tuple[list[dict], list[dict]]:
    tables = [{"sheet_name": "sheet1", "rows": [{"ctas_cobrar": 600, "ventas": 400, "dias": 30}]}]
    refs = [
        {"sheet_name": "sheet1", "column_name": "ctas_cobrar", "normalized_column_name": "ctas_cobrar"},
        {"sheet_name": "sheet1", "column_name": "ventas", "normalized_column_name": "ventas"},
        {"sheet_name": "sheet1", "column_name": "dias", "normalized_column_name": "dias"},
    ]
    return tables, refs


def _confirmed() -> dict:
    return {"status": product.STATUS_CONFIRMED_BINDINGS, "schema_version": "TEST", "service_name": "SERVICE_1"}


def test_root_executes_generic_kernel_for_liq_002(monkeypatch, tmp_path) -> None:
    tables, refs = _liq_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("projected_closing_cash_balance"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["computation_result"]["capability_ref"] == "projected_closing_cash_balance"


def test_root_executes_generic_kernel_for_pyme_011(monkeypatch, tmp_path) -> None:
    tables, refs = _pyme_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("dso"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
    )
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["computation_result"]["capability_ref"] == "dso"


def test_legacy_adapters_are_not_root_imports() -> None:
    import pymia.smartpyme.service_1_product_pipeline_v1 as mod
    source = mod.__file__ or ""
    content = open(source, encoding="utf-8").read()
    assert "evaluate_liq_002_from_normalized_tables_v1" not in content
    assert "evaluate_pyme_011_from_normalized_tables_v1" not in content
    assert "build_liq_002_outcome_v1" not in content
    assert "build_pyme_011_outcome_v1" not in content


def test_single_execution_per_request(monkeypatch, tmp_path) -> None:
    calls = []
    original = execute_generic_capability_v1
    def tracking(*, capability_ref, computation_plan, normalized_tables, column_refs):
        calls.append(capability_ref)
        return original(capability_ref=capability_ref, computation_plan=computation_plan, normalized_tables=normalized_tables, column_refs=column_refs)
    monkeypatch.setattr(product, "execute_generic_capability_v1", tracking)
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("projected_closing_cash_balance"))
    product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": _liq_tables()[0], "column_refs": _liq_tables()[1]},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )
    assert len(calls) == 1
    assert calls[0] == "projected_closing_cash_balance"


def test_liq_002_preserves_invariants_through_root(monkeypatch, tmp_path) -> None:
    tables, refs = _liq_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("projected_closing_cash_balance"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["diagnosis_generated"] is False
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False


def test_liq_002_delivery_blocked(monkeypatch, tmp_path) -> None:
    tables, refs = _liq_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("projected_closing_cash_balance"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        deliver_result=True,
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "LIQ_002_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False


def test_pyme_011_preserves_invariants_through_root(monkeypatch, tmp_path) -> None:
    tables, refs = _pyme_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("dso"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
    )
    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["diagnosis_generated"] is False


def test_pyme_011_delivery_blocked(monkeypatch, tmp_path) -> None:
    tables, refs = _pyme_tables()
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan("dso"))
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
        deliver_result=True,
    )
    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "PYME_011_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False


def test_legacy_modules_remain_importable() -> None:
    assert evaluate_liq_002_v1(initial_balance=100, expected_collections=50, expected_payments=30)["status"] == "EVALUATED"
    tables = [{"sheet_name": "s", "rows": [{"saldo": 100, "cobros": 50, "pagos": 30}]}]
    refs = [{"sheet_name": "s", "column_name": "saldo", "normalized_column_name": "saldo"},
            {"sheet_name": "s", "column_name": "cobros", "normalized_column_name": "cobros"},
            {"sheet_name": "s", "column_name": "pagos", "normalized_column_name": "pagos"}]
    ev = evaluate_liq_002_from_normalized_tables_v1(computation_plan=_plan("projected_closing_cash_balance"), normalized_tables=tables, column_refs=refs)
    outcome = build_liq_002_outcome_v1(computation_result=ev)
    assert outcome["status"] == LIQ_002_OUTCOME_READY
    assert evaluate_pyme_011_v1(accounts_receivable=100, sales=50, days=30)["status"] == "EVALUATED"
    pt = [{"sheet_name": "s", "rows": [{"ctas_cobrar": 600, "ventas": 400, "dias": 30}]}]
    pref = [{"sheet_name": "s", "column_name": "ctas_cobrar", "normalized_column_name": "ctas_cobrar"},
            {"sheet_name": "s", "column_name": "ventas", "normalized_column_name": "ventas"},
            {"sheet_name": "s", "column_name": "dias", "normalized_column_name": "dias"}]
    pv = evaluate_pyme_011_from_normalized_tables_v1(computation_plan=_plan("dso"), normalized_tables=pt, column_refs=pref)
    poutcome = build_pyme_011_outcome_v1(computation_result=pv)
    assert poutcome["status"] == PYME_011_OUTCOME_READY


def test_absent_plan_flags_block_liq_002(monkeypatch, tmp_path) -> None:
    tables, refs = _liq_tables()
    plan = _plan("projected_closing_cash_balance")
    del plan["delivery_authorized"]
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: plan)
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )
    assert result["status"] == product.STATUS_BLOCKED


def test_absent_plan_flags_block_pyme_011(monkeypatch, tmp_path) -> None:
    tables, refs = _pyme_tables()
    plan = _plan("dso")
    del plan["delivery_authorized"]
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: plan)
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
    )
    assert result["status"] == product.STATUS_BLOCKED


def test_true_plan_flags_block_liq_002(monkeypatch, tmp_path) -> None:
    tables, refs = _liq_tables()
    plan = _plan("projected_closing_cash_balance")
    plan["delivery_authorized"] = True
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: plan)
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )
    assert result["status"] == product.STATUS_BLOCKED


def test_true_plan_flags_block_pyme_011(monkeypatch, tmp_path) -> None:
    tables, refs = _pyme_tables()
    plan = _plan("dso")
    plan["delivery_authorized"] = True
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: _confirmed())
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: plan)
    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
    )
    assert result["status"] == product.STATUS_BLOCKED


def test_root_unchanged_for_liq_001_and_ren_001(monkeypatch, tmp_path) -> None:
    import pymia.smartpyme.service_1_product_pipeline_v1 as mod
    source = mod.__file__ or ""
    content = open(source, encoding="utf-8").read()
    assert "evaluate_liq_001_from_normalized_tables_v1" in content
    assert "LIQ_001_OUTCOME_READY" in content
    assert "evaluate_ren_001_from_normalized_tables_v1" in content
    assert "REN_001_OUTCOME_READY" in content


def test_registry_contains_dpo_dso_and_projected_closing() -> None:
    refs = list_capability_refs_v1()
    assert refs == ("dpo", "dso", "payment_collection_gap", "projected_closing_cash_balance")


def test_no_pyme_013_in_registry() -> None:
    refs = list_capability_refs_v1()
    assert "pyme_013" not in refs
    assert "PYME_013" not in str(refs)
