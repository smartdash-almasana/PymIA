from tools.service_1_physical_xlsx_product_readiness_corpus_v1 import (
    SCHEMA_VERSION,
    evaluate_physical_xlsx_product_readiness_corpus_v1,
)


def test_physical_xlsx_product_readiness_corpus_is_reproducible_and_fail_closed() -> None:
    first = evaluate_physical_xlsx_product_readiness_corpus_v1()
    second = evaluate_physical_xlsx_product_readiness_corpus_v1()
    assert first == second
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["cases_count"] == 7
    assert first["columns_count"] > 50
    assert first["runtime_authorized"] is False
    assert first["delivery_authorized"] is False
    assert first["product_ready"] is False


def test_physical_corpus_reports_all_outcomes_without_hiding_failures() -> None:
    result = evaluate_physical_xlsx_product_readiness_corpus_v1()
    rows = result["rows"]
    assert result["exact_matches"] == sum(row["outcome"] == "EXACT_MATCH" for row in rows)
    assert result["safe_questions"] == sum(row["outcome"] == "SAFE_QUESTION" for row in rows)
    assert result["safe_unknowns"] == sum(row["outcome"] == "SAFE_UNKNOWN" for row in rows)
    assert result["false_confident"] == sum(row["outcome"] == "FALSE_CONFIDENT" for row in rows)
    assert result["dangerous_errors"] == sum(
        row["outcome"] == "FALSE_CONFIDENT" and row["dangerous_if_wrong"] for row in rows
    )
