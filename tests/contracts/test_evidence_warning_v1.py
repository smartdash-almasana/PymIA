from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.contracts.evidence_warning_v1 import (
    blocks_calculation,
    default_severity_for_reason,
    get_warning_severity,
    is_owner_message_allowed,
    list_warning_fields,
    list_warning_severities,
    load_evidence_warning_contract,
    requires_owner_disclosure,
)


def test_evidence_warning_contract_loads_valid_json():
    contract = load_evidence_warning_contract()

    assert isinstance(contract, dict)
    assert contract["schema_version"] == "1.0"
    assert contract["contract_id"] == "EVIDENCE_WARNING_V1"
    assert contract["status"] == "CONTRACT_ONLY"
    assert contract["runtime_impact"] == "NONE"
    assert contract["implementation_authorized"] is False
    assert contract["compatible_contracts"] == ["EVIDENCE_AVAILABILITY_V1"]


def test_evidence_warning_contract_file_is_parseable_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "evidence_warning_v1.json"

    assert contract_path.exists()
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    assert payload["contract_id"] == "EVIDENCE_WARNING_V1"


def test_evidence_warning_declares_expected_severities_and_counts():
    contract = load_evidence_warning_contract()
    severities = list_warning_severities()

    assert severities == ["INFO", "CAUTION", "BLOCKING"]
    assert len(severities) == contract["expected_counts"]["severities"] == 3
    assert len(contract["reason_code_severity_defaults"]) == contract["expected_counts"]["reason_code_severity_defaults"] == 10


def test_evidence_warning_declares_required_warning_fields():
    contract = load_evidence_warning_contract()
    fields = list_warning_fields()

    assert fields == [
        "warning_id",
        "severity",
        "source_field",
        "reason_code",
        "owner_message",
        "operator_detail",
        "blocks_calculation",
        "suggested_next_evidence",
    ]
    assert len(fields) == contract["expected_counts"]["warning_fields"] == 8


def test_info_does_not_block_and_does_not_require_owner_disclosure():
    assert blocks_calculation("INFO") is False
    assert requires_owner_disclosure("INFO") is False
    assert get_warning_severity("INFO")["default_owner_prefix"] == "Nota"


def test_caution_requires_owner_disclosure_but_does_not_block_calculation():
    assert blocks_calculation("CAUTION") is False
    assert requires_owner_disclosure("CAUTION") is True
    assert get_warning_severity("CAUTION")["default_owner_prefix"] == "Atención"


def test_blocking_always_blocks_calculation_and_requires_owner_disclosure():
    assert blocks_calculation("BLOCKING") is True
    assert requires_owner_disclosure("BLOCKING") is True
    assert get_warning_severity("BLOCKING")["default_owner_prefix"] == "No determinable"


def test_calculation_policy_matches_severity_specs():
    contract = load_evidence_warning_contract()
    blocking = set(contract["calculation_policy"]["blocking_severities"])
    non_blocking = set(contract["calculation_policy"]["non_blocking_severities"])
    disclosure = set(contract["calculation_policy"]["disclosure_severities"])

    assert len(blocking) == contract["expected_counts"]["blocking_severities"] == 1
    assert len(non_blocking) == contract["expected_counts"]["non_blocking_severities"] == 2
    assert len(disclosure) == contract["expected_counts"]["disclosure_severities"] == 2
    assert blocking == {"BLOCKING"}
    assert non_blocking == {"INFO", "CAUTION"}
    assert disclosure == {"CAUTION", "BLOCKING"}

    for severity in list_warning_severities():
        assert blocks_calculation(severity) is (severity in blocking)
        assert requires_owner_disclosure(severity) is (severity in disclosure)


def test_reason_codes_map_to_default_warning_severities():
    expected = {
        "OBSERVED_VALUE": "INFO",
        "OBSERVED_ZERO": "INFO",
        "MISSING_FIELD": "BLOCKING",
        "MISSING_SOURCE": "BLOCKING",
        "PARTIAL_SOURCE": "CAUTION",
        "COVERAGE_CAPPED": "CAUTION",
        "AMBIGUOUS_FORMAT": "BLOCKING",
        "AMBIGUOUS_MEANING": "BLOCKING",
        "EXCLUDED_BY_RULE": "BLOCKING",
        "EXCLUDED_LOW_CONFIDENCE": "BLOCKING",
    }

    for reason_code, severity in expected.items():
        assert default_severity_for_reason(reason_code) == severity


def test_blocking_reason_codes_have_blocking_severity():
    blocking_reason_codes = [
        "MISSING_FIELD",
        "MISSING_SOURCE",
        "AMBIGUOUS_FORMAT",
        "AMBIGUOUS_MEANING",
        "EXCLUDED_BY_RULE",
        "EXCLUDED_LOW_CONFIDENCE",
    ]

    for reason_code in blocking_reason_codes:
        severity = default_severity_for_reason(reason_code)
        assert severity == "BLOCKING"
        assert blocks_calculation(severity) is True


def test_owner_message_policy_rejects_technical_terms():
    assert is_owner_message_allowed("No se pudo determinar este dato con la evidencia actual.") is True
    assert is_owner_message_allowed("Este dato surge de evidencia parcial.") is True

    forbidden_messages = [
        "Error en contract_id interno.",
        "Fallo en schema_version.",
        "El pipeline no pudo procesar.",
        "Runtime path inválido.",
        "OCF incompleto.",
        "diagnostic_core no disponible.",
        "formula_id faltante.",
        "stacktrace adjunto.",
        "module_path no existe.",
    ]
    for message in forbidden_messages:
        assert is_owner_message_allowed(message) is False


def test_operator_detail_policy_allows_internal_context_without_stacktrace():
    contract = load_evidence_warning_contract()
    policy = contract["operator_detail_policy"]

    assert policy["may_include_reason_code"] is True
    assert policy["may_include_source_field"] is True
    assert policy["may_include_internal_context"] is True
    assert policy["must_not_include_stacktrace"] is True


def test_unknown_severity_or_reason_is_safe_false_or_none():
    assert get_warning_severity("UNKNOWN") is None
    assert default_severity_for_reason("UNKNOWN") is None
    assert blocks_calculation("UNKNOWN") is False
    assert requires_owner_disclosure("UNKNOWN") is False


def test_blank_inputs_are_rejected():
    with pytest.raises(ValueError):
        get_warning_severity(" ")
    with pytest.raises(ValueError):
        default_severity_for_reason(" ")
    with pytest.raises(ValueError):
        is_owner_message_allowed(" ")


def test_evidence_warning_contract_does_not_expose_runtime_keys():
    contract = load_evidence_warning_contract()

    forbidden_runtime_keys = {"loader", "plugin", "executor", "entrypoint", "runtime_path", "module_path"}
    assert forbidden_runtime_keys.isdisjoint(contract.keys())
    for severity_spec in contract["severities"].values():
        assert forbidden_runtime_keys.isdisjoint(severity_spec.keys())


def test_warning_contract_is_contract_only_and_does_not_define_templates_as_runtime_execution():
    contract = load_evidence_warning_contract()

    serialized = json.dumps(contract, ensure_ascii=False).lower()
    assert "execute" not in serialized
    assert "diagnose" not in serialized
    assert "persist" not in serialized
    assert "run_pipeline" not in serialized
