from __future__ import annotations

import importlib

from pymia.smartpyme.service_1_column_understanding_owner_question_semantic_audit_v1 import (
    ISSUE_NO_SEMANTIC_ALIGNMENT,
    SCHEMA_VERSION,
    STATUS_READY,
    VERDICT_NEEDS_FIXES,
    audit_service_1_column_understanding_owner_question_semantics_v1,
)


def test_semantic_audit_detects_generic_or_misaligned_options() -> None:
    audit = audit_service_1_column_understanding_owner_question_semantics_v1()

    assert audit.schema_version == SCHEMA_VERSION
    assert audit.status == STATUS_READY
    assert audit.verdict == VERDICT_NEEDS_FIXES
    assert audit.question_views_count == 20
    assert audit.auditable_views_count > 0
    assert audit.unaligned_views_count > 0
    assert audit.aligned_views_count + audit.unaligned_views_count == audit.auditable_views_count


def test_semantic_audit_surfaces_known_scope_gap_columns_without_parallel_meanings() -> None:
    audit = audit_service_1_column_understanding_owner_question_semantics_v1()
    by_column = {finding.column_name: finding for finding in audit.findings}

    for column_name in {
        "stock_inicial",
        "entradas",
        "salidas",
        "stock_final",
        "cliente",
        "medio_pago",
        "proveedor",
        "iva",
        "bonif",
    }:
        assert column_name in by_column
        assert by_column[column_name].issue_code == ISSUE_NO_SEMANTIC_ALIGNMENT
        assert by_column[column_name].option_labels


def test_semantic_audit_is_observational_and_fail_closed() -> None:
    audit = audit_service_1_column_understanding_owner_question_semantics_v1()

    assert audit.runtime_authorized is False
    assert audit.frontend_wiring_authorized is False
    assert audit.delivery_authorized is False
    assert audit.metadata["observational_only"] is True
    assert audit.metadata["audit_policy"] == "lexical_semantic_alignment_without_parallel_catalog"


def test_semantic_audit_is_deterministic() -> None:
    assert (
        audit_service_1_column_understanding_owner_question_semantics_v1().to_dict()
        == audit_service_1_column_understanding_owner_question_semantics_v1().to_dict()
    )


def test_module_has_no_frontend_io_or_orchestrator_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_owner_question_semantic_audit_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_owner_question_semantic_audit_v1"
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
