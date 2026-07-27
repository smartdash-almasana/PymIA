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
    assert report.evaluation_verdict == "READY_FOR_FRONTEND"
    assert report.cases_count == 6
    assert report.columns_count == 38
    assert report.exact_matches == 32
    assert report.safe_questions == 6
    assert report.safe_unknowns == 0
    assert report.false_confident == 0
    assert report.missed_questions == 0
    assert report.dangerous_errors == 0
    assert report.exact_match_rate == 0.8421
    assert report.safe_resolution_rate == 1.0
    assert report.metadata["supported_scope_columns_count"] == 32
    assert report.metadata["supported_scope_exact_matches"] == 32
    assert report.metadata["supported_scope_exact_match_rate"] == 1.0
    assert report.metadata["direct_resolution_coverage"] == 0.8421
    assert report.metadata["intentional_unknown_columns_count"] == 6


def test_report_has_no_critical_columns_after_ambiguity_fix() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.critical_columns == ()
    critical = [finding for finding in report.findings if finding.priority == PRIORITY_CRITICAL]
    assert critical == []
    assert report.findings
    assert {finding.column_name for finding in report.findings} == {
        "x1", "monto", "valor", "ref", "concepto", "obs"
    }
    assert all(finding.outcome == "SAFE_QUESTION" for finding in report.findings)


def test_report_allows_semantic_frontend_wiring_but_does_not_authorize_it() -> None:
    report = build_service_1_column_understanding_corpus_report_v1()

    assert report.frontend_wiring_allowed is True
    assert report.frontend_wiring_authorized is False
    assert report.recommended_next_slice == "SERVICE_1_COLUMN_UNDERSTANDING_OWNER_QUESTION_ADAPTER_V1"


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
    assert {finding.outcome for finding in report.findings} == {"SAFE_QUESTION"}


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
