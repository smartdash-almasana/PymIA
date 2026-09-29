from pathlib import Path

import pytest

from pymia.smartpyme.service_1_c2_golden_business_corpus_v1 import (
    STATUS_READY,
    evaluate_service_1_c2_golden_business_corpus_v1,
)


pytestmark = pytest.mark.golden


def test_f11_multi_business_golden_corpus_uses_real_xlsx_and_canonical_context() -> None:
    root = Path(__file__).resolve().parents[2]
    result = evaluate_service_1_c2_golden_business_corpus_v1(repo_root=root)

    assert result["status"] == STATUS_READY, result
    assert result["case_count"] == 7
    assert result["golden_coordinate_column_count"] >= 25
    assert result["safe_unknown_column_count"] >= 4
    assert all(item["canonical_context_ready"] for item in result["cases"])
    assert all(result[flag] is False for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "automatic_reuse_authorized",
    ))


def test_f11_corpus_spans_distinct_business_contexts_and_keeps_safe_unknowns() -> None:
    root = Path(__file__).resolve().parents[2]
    result = evaluate_service_1_c2_golden_business_corpus_v1(repo_root=root)
    ids = {item["case_id"] for item in result["cases"]}

    assert {
        "F11-SALES",
        "F11-TEXTILE-SALES",
        "F11-TEXTILE-PURCHASES",
        "F11-TEXTILE-STOCK",
        "F11-COLLECTIONS",
        "F11-WORKSHOP",
        "F11-CASH-BANK-SAFE-UNKNOWN",
    } == ids
    cash = next(item for item in result["cases"] if item["case_id"] == "F11-CASH-BANK-SAFE-UNKNOWN")
    assert len(cash["safe_unknown_columns"]) == 4


def test_f11_new_c2_runtime_files_do_not_contain_business_case_switches() -> None:
    root = Path(__file__).resolve().parents[2]
    runtime_files = [
        "pymia/smartpyme/service_1_workbook_semantic_context_v1.py",
        "pymia/smartpyme/service_1_semantic_knowledge_context_v1.py",
        "pymia/smartpyme/service_1_workbook_business_understanding_v1.py",
        "pymia/smartpyme/service_1_semantic_compression_v1.py",
    ]
    forbidden = (
        "F11-SALES",
        "F11-WORKSHOP",
        "taller_mecanico_lubricar_srl.xlsx",
        "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        "if vertical ==",
        "if sector ==",
    )
    for rel in runtime_files:
        source = (root / rel).read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), (rel, source)
