from __future__ import annotations

import importlib
import json
from pathlib import Path

from pymia.smartpyme.service_1_column_understanding_canonical_gap_audit_v1 import (
    SCHEMA_VERSION,
    STATUS_READY,
    VERDICT_GAPS_REMAIN,
    audit_service_1_column_understanding_canonical_gaps_v1,
)


def _canonical_names() -> tuple[str, ...]:
    path = Path(__file__).resolve().parents[2] / "docs" / "service_1_semantic_variable_catalog.v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(item["variable_name"] for item in payload["variables"])


def test_audit_reports_remaining_canonical_gaps_without_authorizing_mappings() -> None:
    audit = audit_service_1_column_understanding_canonical_gaps_v1(_canonical_names())

    assert audit.schema_version == SCHEMA_VERSION
    assert audit.status == STATUS_READY
    assert audit.verdict == VERDICT_GAPS_REMAIN
    assert audit.unresolved_columns_count == 6
    assert audit.unresolved_columns_count == len(audit.findings)
    assert audit.columns_without_lexical_candidates > 0
    assert all(finding.canonical_mapping_authorized is False for finding in audit.findings)


def test_resolved_stock_headers_are_not_reported_as_remaining_gaps() -> None:
    audit = audit_service_1_column_understanding_canonical_gaps_v1(_canonical_names())
    unresolved_columns = {finding.column_name for finding in audit.findings}

    assert "stock_inicial" not in unresolved_columns
    assert "stock_final" not in unresolved_columns


def test_columns_without_canonical_language_remain_explicit_gaps() -> None:
    audit = audit_service_1_column_understanding_canonical_gaps_v1(_canonical_names())
    without_candidates = [finding for finding in audit.findings if not finding.lexical_candidates]

    assert without_candidates
    for finding in without_candidates:
        assert finding.canonical_mapping_authorized is False
        assert "No canonical variable" in finding.reason


def test_audit_is_deterministic_and_fail_closed() -> None:
    names = _canonical_names()
    first = audit_service_1_column_understanding_canonical_gaps_v1(names)
    second = audit_service_1_column_understanding_canonical_gaps_v1(names)

    assert first.to_dict() == second.to_dict()
    assert first.runtime_authorized is False
    assert first.frontend_wiring_authorized is False
    assert first.delivery_authorized is False
    assert first.metadata["mapping_policy"] == "lexical_candidates_never_authorize_mapping"


def test_module_has_no_frontend_or_orchestrator_dependency() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_canonical_gap_audit_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_canonical_gap_audit_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
    ]:
        assert token not in text
    assert module.SCHEMA_VERSION == SCHEMA_VERSION
