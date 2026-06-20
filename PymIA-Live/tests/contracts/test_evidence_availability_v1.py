from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.contracts.evidence_availability_v1 import (
    allows_calculation,
    blocks_required_field,
    default_status_for_reason,
    get_availability_status,
    get_reason_code,
    is_excluded_from_calculation,
    list_availability_statuses,
    load_evidence_availability_contract,
    requires_owner_disclosure,
)


def test_evidence_availability_contract_loads_valid_json():
    contract = load_evidence_availability_contract()

    assert isinstance(contract, dict)
    assert contract["schema_version"] == "1.0"
    assert contract["contract_id"] == "EVIDENCE_AVAILABILITY_V1"
    assert contract["status"] == "CONTRACT_ONLY"
    assert contract["runtime_impact"] == "NONE"
    assert contract["implementation_authorized"] is False


def test_evidence_availability_contract_file_is_parseable_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "evidence_availability_v1.json"

    assert contract_path.exists()
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    assert payload["contract_id"] == "EVIDENCE_AVAILABILITY_V1"


def test_evidence_availability_declares_expected_statuses_and_counts():
    contract = load_evidence_availability_contract()
    statuses = list_availability_statuses()

    assert statuses == [
        "MEASURED",
        "ZERO_REAL",
        "NOT_AVAILABLE",
        "PARTIAL",
        "CAPPED",
        "AMBIGUOUS",
        "EXCLUDED",
    ]
    assert len(statuses) == contract["expected_counts"]["availability_statuses"] == 7
    assert len(contract["reason_codes"]) == contract["expected_counts"]["reason_codes"] == 10


def test_zero_real_is_not_not_available():
    zero_real = get_availability_status("ZERO_REAL")
    not_available = get_availability_status("NOT_AVAILABLE")

    assert zero_real is not None
    assert not_available is not None
    assert zero_real != not_available
    assert allows_calculation("ZERO_REAL") is True
    assert allows_calculation("NOT_AVAILABLE") is False
    assert blocks_required_field("ZERO_REAL") is False
    assert blocks_required_field("NOT_AVAILABLE") is True


def test_measured_and_zero_real_allow_calculation_without_disclosure():
    for status in ["MEASURED", "ZERO_REAL"]:
        assert allows_calculation(status) is True
        assert requires_owner_disclosure(status) is False
        assert is_excluded_from_calculation(status) is False
        assert blocks_required_field(status) is False


def test_not_available_blocks_required_field_and_requires_disclosure():
    assert allows_calculation("NOT_AVAILABLE") is False
    assert requires_owner_disclosure("NOT_AVAILABLE") is True
    assert is_excluded_from_calculation("NOT_AVAILABLE") is True
    assert blocks_required_field("NOT_AVAILABLE") is True


def test_partial_and_capped_allow_calculation_but_require_owner_disclosure():
    for status in ["PARTIAL", "CAPPED"]:
        assert allows_calculation(status) is True
        assert requires_owner_disclosure(status) is True
        assert is_excluded_from_calculation(status) is False
        assert blocks_required_field(status) is False


def test_ambiguous_and_excluded_block_calculation_and_required_fields():
    for status in ["AMBIGUOUS", "EXCLUDED"]:
        assert allows_calculation(status) is False
        assert requires_owner_disclosure(status) is True
        assert is_excluded_from_calculation(status) is True
        assert blocks_required_field(status) is True


def test_reason_codes_map_to_default_statuses():
    expected = {
        "OBSERVED_VALUE": "MEASURED",
        "OBSERVED_ZERO": "ZERO_REAL",
        "MISSING_FIELD": "NOT_AVAILABLE",
        "MISSING_SOURCE": "NOT_AVAILABLE",
        "PARTIAL_SOURCE": "PARTIAL",
        "COVERAGE_CAPPED": "CAPPED",
        "AMBIGUOUS_FORMAT": "AMBIGUOUS",
        "AMBIGUOUS_MEANING": "AMBIGUOUS",
        "EXCLUDED_BY_RULE": "EXCLUDED",
        "EXCLUDED_LOW_CONFIDENCE": "EXCLUDED",
    }

    for reason_code, status in expected.items():
        assert default_status_for_reason(reason_code) == status
        assert get_reason_code(reason_code)["default_status"] == status


def test_reason_codes_that_block_required_fields_are_consistent_with_status_policy():
    contract = load_evidence_availability_contract()

    for reason_code, reason in contract["reason_codes"].items():
        default_status = reason["default_status"]
        if reason["blocks_required_field"]:
            assert blocks_required_field(default_status), reason_code
        else:
            assert blocks_required_field(default_status) is False, reason_code


def test_owner_disclosure_statuses_match_status_specs():
    contract = load_evidence_availability_contract()
    disclosure_statuses = set(contract["field_policy"]["owner_disclosure_statuses"])

    assert len(disclosure_statuses) == contract["expected_counts"]["owner_disclosure_statuses"] == 5
    for status in list_availability_statuses():
        assert requires_owner_disclosure(status) is (status in disclosure_statuses)


def test_calculation_allowed_statuses_match_status_specs():
    contract = load_evidence_availability_contract()
    calculation_allowed_statuses = set(contract["field_policy"]["calculation_allowed_statuses"])

    assert len(calculation_allowed_statuses) == contract["expected_counts"]["calculation_allowed_statuses"] == 4
    for status in list_availability_statuses():
        assert allows_calculation(status) is (status in calculation_allowed_statuses)


def test_unknown_status_or_reason_is_safe_false_or_none():
    assert get_availability_status("UNKNOWN") is None
    assert get_reason_code("UNKNOWN") is None
    assert default_status_for_reason("UNKNOWN") is None
    assert allows_calculation("UNKNOWN") is False
    assert requires_owner_disclosure("UNKNOWN") is False
    assert is_excluded_from_calculation("UNKNOWN") is False
    assert blocks_required_field("UNKNOWN") is False


def test_blank_status_and_reason_are_rejected():
    with pytest.raises(ValueError):
        get_availability_status(" ")
    with pytest.raises(ValueError):
        get_reason_code(" ")


def test_evidence_availability_contract_does_not_expose_runtime_keys():
    contract = load_evidence_availability_contract()

    forbidden_runtime_keys = {"loader", "plugin", "executor", "entrypoint", "runtime_path", "module_path"}
    assert forbidden_runtime_keys.isdisjoint(contract.keys())
    for status_spec in contract["availability_statuses"].values():
        assert forbidden_runtime_keys.isdisjoint(status_spec.keys())
    for reason_spec in contract["reason_codes"].values():
        assert forbidden_runtime_keys.isdisjoint(reason_spec.keys())
