from __future__ import annotations

import importlib

from pymia.smartpyme.service_1_column_understanding_owner_question_corpus_audit_v1 import (
    SCHEMA_VERSION,
    STATUS_READY,
    VERDICT_PASS,
    audit_service_1_column_understanding_owner_questions_v1,
)


def test_audit_covers_all_current_owner_questions() -> None:
    audit = audit_service_1_column_understanding_owner_questions_v1()

    assert audit.schema_version == SCHEMA_VERSION
    assert audit.status == STATUS_READY
    assert audit.cases_count == 6
    assert audit.question_views_count == 20
    assert audit.covered_question_views == 20


def test_audit_current_corpus_has_no_structural_question_defects() -> None:
    audit = audit_service_1_column_understanding_owner_questions_v1()

    assert audit.verdict == VERDICT_PASS
    assert audit.findings == ()
    assert audit.missing_other_option == 0
    assert audit.missing_risk_note == 0
    assert audit.empty_question == 0
    assert audit.duplicate_option_labels == 0
    assert audit.jargon_hits == 0


def test_audit_is_deterministic_and_fail_closed() -> None:
    first = audit_service_1_column_understanding_owner_questions_v1()
    second = audit_service_1_column_understanding_owner_questions_v1()

    assert first.to_dict() == second.to_dict()
    assert first.runtime_authorized is False
    assert first.frontend_wiring_authorized is False
    assert first.delivery_authorized is False
    assert first.metadata["observational_only"] is True


def test_module_has_no_frontend_io_or_orchestrator_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_owner_question_corpus_audit_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_owner_question_corpus_audit_v1"
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
