from __future__ import annotations

import inspect

import pytest

from pymia.smartpyme.evidence_value_normalizer import (
    EvidenceWarning,
    NormalizedEvidenceValue,
    normalize_evidence_value,
)


def test_normalizes_measured_text_value():
    result = normalize_evidence_value(
        raw_value="  Producto A  ",
        field_name="producto",
        expected_type="text",
        required=True,
    )

    assert isinstance(result, NormalizedEvidenceValue)
    assert result.normalized_value == "Producto A"
    assert result.availability_status == "MEASURED"
    assert result.reason_code == "OBSERVED_VALUE"
    assert result.allows_calculation is True
    assert result.excluded_from_calculation is False
    assert result.blocks_required_field is False
    assert result.requires_owner_disclosure is False
    assert result.warnings == []


def test_zero_number_is_zero_real_not_missing():
    result = normalize_evidence_value(
        raw_value=0,
        field_name="ventas",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value == 0
    assert result.availability_status == "ZERO_REAL"
    assert result.reason_code == "OBSERVED_ZERO"
    assert result.availability_status != "NOT_AVAILABLE"
    assert result.allows_calculation is True
    assert result.blocks_required_field is False
    assert result.excluded_from_calculation is False
    assert result.warnings == []


def test_zero_string_number_is_zero_real():
    result = normalize_evidence_value(
        raw_value="0",
        field_name="saldo",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value == 0
    assert result.availability_status == "ZERO_REAL"
    assert result.reason_code == "OBSERVED_ZERO"


def test_missing_required_value_blocks_required_field_and_creates_blocking_warning():
    result = normalize_evidence_value(
        raw_value=None,
        field_name="costo",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value is None
    assert result.availability_status == "NOT_AVAILABLE"
    assert result.reason_code == "MISSING_FIELD"
    assert result.allows_calculation is False
    assert result.excluded_from_calculation is True
    assert result.blocks_required_field is True
    assert result.requires_owner_disclosure is True
    assert len(result.warnings) == 1
    warning = result.warnings[0]
    assert isinstance(warning, EvidenceWarning)
    assert warning.severity == "BLOCKING"
    assert warning.blocks_calculation is True
    assert warning.owner_message == "Falta un dato necesario para calcular con seguridad."
    assert "reason_code=MISSING_FIELD" in warning.operator_detail


def test_missing_optional_value_is_not_available_but_does_not_block_required_field():
    result = normalize_evidence_value(
        raw_value=" ",
        field_name="observacion",
        expected_type="text",
        required=False,
    )

    assert result.availability_status == "NOT_AVAILABLE"
    assert result.blocks_required_field is False
    assert result.allows_calculation is False
    assert result.excluded_from_calculation is True
    assert len(result.warnings) == 1
    assert result.warnings[0].severity == "BLOCKING"
    assert result.warnings[0].owner_message == "No se pudo determinar este dato con la evidencia actual."


def test_ambiguous_number_blocks_calculation_and_is_excluded():
    result = normalize_evidence_value(
        raw_value="1,200.50",
        field_name="importe",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value is None
    assert result.availability_status == "AMBIGUOUS"
    assert result.reason_code == "AMBIGUOUS_FORMAT"
    assert result.allows_calculation is False
    assert result.excluded_from_calculation is True
    assert result.blocks_required_field is True
    assert len(result.warnings) == 1
    assert result.warnings[0].severity == "BLOCKING"
    assert result.warnings[0].owner_message == "Este dato es ambiguo y no se usó para calcular."


def test_number_with_decimal_comma_is_measured():
    result = normalize_evidence_value(
        raw_value="12,5",
        field_name="margen",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value == 12.5
    assert result.availability_status == "MEASURED"
    assert result.reason_code == "OBSERVED_VALUE"
    assert result.warnings == []


def test_integer_rejects_decimal_value_as_ambiguous():
    result = normalize_evidence_value(
        raw_value="12.5",
        field_name="unidades",
        expected_type="integer",
        required=True,
    )

    assert result.normalized_value is None
    assert result.availability_status == "AMBIGUOUS"
    assert result.reason_code == "AMBIGUOUS_FORMAT"
    assert result.excluded_from_calculation is True
    assert result.blocks_required_field is True


def test_integer_accepts_numeric_integer_string():
    result = normalize_evidence_value(
        raw_value="12",
        field_name="unidades",
        expected_type="integer",
        required=True,
    )

    assert result.normalized_value == 12
    assert result.availability_status == "MEASURED"
    assert result.allows_calculation is True


def test_boolean_accepts_yes_no_values():
    true_result = normalize_evidence_value(
        raw_value="sí",
        field_name="tiene_stock",
        expected_type="boolean",
        required=True,
    )
    false_result = normalize_evidence_value(
        raw_value="no",
        field_name="tiene_stock",
        expected_type="boolean",
        required=True,
    )

    assert true_result.normalized_value is True
    assert false_result.normalized_value is False
    assert true_result.availability_status == "MEASURED"
    assert false_result.availability_status == "MEASURED"


def test_boolean_rejects_ambiguous_text():
    result = normalize_evidence_value(
        raw_value="quizás",
        field_name="tiene_stock",
        expected_type="boolean",
        required=True,
    )

    assert result.normalized_value is None
    assert result.availability_status == "AMBIGUOUS"
    assert result.blocks_required_field is True
    assert result.warnings[0].severity == "BLOCKING"


def test_boolean_is_not_accepted_as_number():
    result = normalize_evidence_value(
        raw_value=True,
        field_name="cantidad",
        expected_type="number",
        required=True,
    )

    assert result.normalized_value is None
    assert result.availability_status == "AMBIGUOUS"
    assert result.reason_code == "AMBIGUOUS_FORMAT"


def test_owner_messages_do_not_expose_internal_terms():
    result = normalize_evidence_value(
        raw_value="abc",
        field_name="importe",
        expected_type="number",
        required=True,
    )

    owner_text = " ".join(warning.owner_message for warning in result.warnings).lower()
    forbidden_terms = [
        "contract_id",
        "schema_version",
        "pipeline",
        "runtime",
        "ocf",
        "diagnostic_core",
        "formula_id",
        "stacktrace",
        "module_path",
    ]
    for term in forbidden_terms:
        assert term not in owner_text


def test_invalid_field_name_and_expected_type_are_rejected():
    with pytest.raises(ValueError):
        normalize_evidence_value(
            raw_value="x",
            field_name=" ",
            expected_type="text",
        )
    with pytest.raises(ValueError):
        normalize_evidence_value(
            raw_value="x",
            field_name="campo",
            expected_type="money",  # type: ignore[arg-type]
        )


def test_normalizer_has_no_runtime_pipeline_or_diagnostic_dependencies():
    import pymia.smartpyme.evidence_value_normalizer as module

    source = inspect.getsource(module)
    forbidden_imports = [
        "vertical_pipeline",
        "structured_evidence_builder",
        "diagnostic_core",
        "ocf_snapshot",
        "case_replay",
        "storage",
        "pipeline_registration",
    ]
    for forbidden in forbidden_imports:
        assert forbidden not in source


def test_normalizer_is_pure_value_service_without_file_or_persistence_calls():
    import pymia.smartpyme.evidence_value_normalizer as module

    source = inspect.getsource(module)
    forbidden_terms = [
        "open(",
        "read_text",
        "write_text",
        "json.dump",
        "subprocess",
        "requests",
        "pandas",
        "openpyxl",
    ]
    for forbidden in forbidden_terms:
        assert forbidden not in source
