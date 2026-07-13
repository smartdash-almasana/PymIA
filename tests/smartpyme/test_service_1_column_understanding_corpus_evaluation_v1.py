from __future__ import annotations

import importlib

from pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1 import (
    OUTCOME_EXACT_MATCH,
    OUTCOME_FALSE_CONFIDENT,
    OUTCOME_MISSED_QUESTION,
    OUTCOME_SAFE_QUESTION,
    OUTCOME_SAFE_UNKNOWN,
    SCHEMA_VERSION,
    STATUS_READY,
    VERDICT_NOT_READY,
    VERDICT_READY_FOR_FRONTEND,
    VERDICT_READY_WITH_FIXES,
    build_default_service_1_column_understanding_corpus_v1,
    evaluate_service_1_column_understanding_corpus_v1,
)


def test_default_corpus_has_varied_excel_like_cases() -> None:
    corpus = build_default_service_1_column_understanding_corpus_v1()

    assert len(corpus) == 6
    assert {case.case_id for case in corpus} == {
        "S1-CUE-001",
        "S1-CUE-002",
        "S1-CUE-003",
        "S1-CUE-004",
        "S1-CUE-005",
        "S1-CUE-006",
    }
    assert sum(len(case.columns) for case in corpus) >= 36
    scenarios = " ".join(case.business_scenario.lower() for case in corpus)
    for expected in ["venta", "stock", "caja", "compras", "raras"]:
        assert expected in scenarios


def test_evaluation_runs_and_reports_precision_metrics() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()

    assert result.schema_version == SCHEMA_VERSION
    assert result.status == STATUS_READY
    assert result.cases_count == 6
    assert result.columns_count >= 36
    assert result.exact_matches > 0
    assert result.safe_resolution_rate >= result.exact_match_rate
    assert result.verdict in {
        VERDICT_READY_FOR_FRONTEND,
        VERDICT_READY_WITH_FIXES,
        VERDICT_NOT_READY,
    }
    assert len(result.rows) == result.columns_count


def test_case_001_like_sales_columns_are_understood_exactly() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()
    rows = {
        (row.case_id, row.column_name): row
        for row in result.rows
    }

    expected = {
        "fecha": "operation_date",
        "producto": "product_name",
        "cantidad": "quantity",
        "precio_unitario": "unit_sale_price",
        "costo_unitario": "unit_cost_candidate",
        "venta_total": "sales_amount",
    }
    for column, role in expected.items():
        row = rows[("S1-CUE-001", column)]
        assert row.predicted_semantic_role == role
        assert row.outcome == OUTCOME_EXACT_MATCH
        assert row.confidence >= 0.6
        assert row.evidence


def test_unknown_or_out_of_scope_columns_are_measured_not_hidden() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()
    risky_rows = [
        row
        for row in result.rows
        if row.expected_semantic_role == "unknown"
    ]

    assert risky_rows
    assert any(row.outcome in {OUTCOME_SAFE_QUESTION, OUTCOME_SAFE_UNKNOWN} for row in risky_rows)
    unsafe = [
        row
        for row in risky_rows
        if row.outcome in {OUTCOME_FALSE_CONFIDENT, OUTCOME_MISSED_QUESTION}
    ]
    if unsafe:
        assert result.verdict == VERDICT_NOT_READY
        assert result.metadata["frontend_wiring_allowed"] is False


def test_verdict_is_not_ready_for_frontend_when_dangerous_errors_exist() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()

    if result.dangerous_errors or result.false_confident or result.missed_questions:
        assert result.verdict == VERDICT_NOT_READY
    elif result.exact_match_rate < 0.8:
        assert result.verdict == VERDICT_READY_WITH_FIXES


def test_current_corpus_surfaces_frontend_readiness_decision() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()

    assert "frontend_wiring_allowed" in result.metadata
    assert result.metadata["frontend_wiring_allowed"] is (
        result.verdict == VERDICT_READY_FOR_FRONTEND
    )
    assert result.metadata["corpus_policy"] == "in_memory_excel_like_column_layouts"


def test_report_rows_include_human_question_when_owner_input_needed() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()
    question_rows = [row for row in result.rows if row.owner_question_needed]

    assert question_rows
    for row in question_rows:
        assert row.owner_question_text
        lower = row.owner_question_text.lower()
        assert "rol semantico" not in lower
        assert "confirmas" not in lower


def test_output_flags_are_fail_closed() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()

    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False
    serialized = repr(result.to_dict())
    for forbidden in [
        "runtime_authorized=True",
        "tool_execution_authorized=True",
        "delivery_authorized=True",
        "diagnosis_generated=True",
    ]:
        assert forbidden not in serialized


def test_evaluation_is_deterministic() -> None:
    a = evaluate_service_1_column_understanding_corpus_v1().to_dict()
    b = evaluate_service_1_column_understanding_corpus_v1().to_dict()

    assert a == b


def test_module_is_pure_no_io_no_web_endpoint_no_orchestrator_imports() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    forbidden_tokens = [
        "requests.",
        "urllib",
        "http.client",
        "subprocess",
        "os.system",
        "popen",
        "exec(",
        "eval(",
        "import openai",
        "import anthropic",
        "service_1_assisted_flow_orchestrator",
        "service_1_web_experiment",
    ]
    for token in forbidden_tokens:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION


def test_outcome_counts_match_rows() -> None:
    result = evaluate_service_1_column_understanding_corpus_v1()
    rows = list(result.rows)

    assert result.exact_matches == sum(1 for row in rows if row.outcome == OUTCOME_EXACT_MATCH)
    assert result.safe_questions == sum(1 for row in rows if row.outcome == OUTCOME_SAFE_QUESTION)
    assert result.safe_unknowns == sum(1 for row in rows if row.outcome == OUTCOME_SAFE_UNKNOWN)
    assert result.false_confident == sum(1 for row in rows if row.outcome == OUTCOME_FALSE_CONFIDENT)
    assert result.missed_questions == sum(1 for row in rows if row.outcome == OUTCOME_MISSED_QUESTION)
