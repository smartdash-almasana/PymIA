from __future__ import annotations

import inspect

from tools import service_1_excel_reality_lab_a3_rubro_matrix_v1 as a3


def test_a3_rubro_matrix_covers_all_required_rubros_safely() -> None:
    result = a3.evaluate_a3_rubro_matrix_v1()

    assert result["verdict"] == a3.VERDICT_PASS, result
    assert result["rubro_count"] == 8
    assert set(result["rubros_represented"]) == set(a3.REQUIRED_RUBROS)
    assert result["missing_rubros"] == []
    assert result["failures"] == []
    assert sum(result["terminal_counts"].values()) == 8
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False
    assert result["new_capabilities_authorized"] is False
    assert result["sector_runtime_authority_authorized"] is False

    for row in result["rows"]:
        assert row["vocabulary"]
        assert row["sheet_names"]
        assert row["contexts"]
        assert row["row_count"] >= 0
        assert row["granularity"] in {"SMALL", "MEDIUM", "LARGE"}
        assert row["terminal_class"] in {
            "PASS_DETERMINISTIC_UNDERSTANDING",
            "PASS_NEEDS_OWNER",
            "PASS_BLOCKED_FAIL_CLOSED",
        }
        assert row["new_capability_authorized"] is False
        assert row["sector_runtime_authority"] is False


def test_a3_is_corpus_evidence_not_a_sector_parser_or_authority() -> None:
    source = inspect.getsource(a3)

    assert "curate_xlsx_document" in source
    assert "openpyxl" not in source
    assert "load_workbook" not in source
    assert "read_excel" not in source
    assert "run_service_1_product_pipeline_v1" not in source
    assert "build_service_1_computability_decision" not in source
    assert "execute_generic_capability" not in source
    assert "sector_runtime_authority_authorized\": False" in source


def test_a3_representative_mapping_is_complete_and_not_runtime_routing() -> None:
    assert set(a3.REPRESENTATIVE_CASE_IDS) == set(a3.REQUIRED_RUBROS)
    assert len(set(a3.REPRESENTATIVE_CASE_IDS.values())) == 8
