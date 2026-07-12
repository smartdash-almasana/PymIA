from __future__ import annotations

import importlib

from pymia.smartpyme.service_1_column_understanding_corpus_report_v1 import (
    PRIORITY_CRITICAL,
    SCHEMA_VERSION,
    STATUS_READY,
    build_service_1_column_understanding_corpus_report_v1,
)


def test_report_materializes_current_corpus_metrics() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.schema_version == SCHEMA_VERSION
    assert report.status == STATUS_READY
    assert report.evaluation_verdict == "NOT_READY"
    assert report.cases_count == 6
    assert report.columns_count == 38
    assert report.exact_matches == 18
    assert report.safe_questions == 18
    assert report.safe_unknowns == 0
    assert report.false_confident == 0
    assert report.missed_questions == 2
    assert report.dangerous_errors == 2
    assert report.exact_match_rate == 0.4737
    assert report.safe_resolution_rate == 0.9474


def test_report_identifies_current_critical_columns() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.critical_columns == (
        "S1-CUE-002:precio_lista",
        "S1-CUE-005:subtotal",
    )
    critical = [finding for finding in report.findings if finding.priority == PRIORITY_CRITICAL]
    assert [finding.column_name for finding in critical] == ["precio_lista", "subtotal"]
    assert all(finding.outcome == "MISSED_QUESTION" for finding in critical)


def test_report_recommends_rule_expansion_and_blocks_frontend() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.frontend_wiring_allowed is False
    assert report.frontend_wiring_authorized is False
    assert report.recommended_next_slice == "SERVICE_1_COLUMN_UNDERSTANDING_RULE_EXPANSION_V1"


def test_report_is_observational_and_fail_closed() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.runtime_authorized is False
    assert report.frontend_wiring_authorized is False
    assert report.delivery_authorized is False
    assert report.metadata["observational_only"] is True
    assert report.metadata["report_policy"] == "derive_only_from_corpus_evaluation"


def test_report_is_deterministic() -> None:
    assert (
        build_service_1_column_understanding_corpus_report_v1().to_dict()
        == build_service_1_column_understanding_corpus_report_v1().to_dict()
    )


def test_report_preserves_all_non_exact_rows_as_findings() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert len(report.findings) == report.columns_count - report.exact_matches
    assert {finding.outcome for finding in report.findings} == {
        "SAFE_QUESTION",
        "MISSED_QUESTION",
    }


def test_module_has_no_io_frontend_or_orchestrator_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_corpus_report_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_corpus_report_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "requests.",
        "urllib",
        "subprocess",
        "os.system",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION
