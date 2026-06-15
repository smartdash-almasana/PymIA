import pytest

from pymia.contracts.question_alignment_v1 import (
    QuestionAlignmentContractError,
    load_question_alignment_contract,
    validate_question_alignment_contract,
)


def test_question_alignment_contract_loads_active_contract():
    contract = load_question_alignment_contract()

    assert contract["schema_version"] == "1.0"
    assert contract["status"] == "ACTIVE"
    assert "caja_liquidez" in contract["owner_keywords"]
    assert contract["formula_prefix_axis"]["LIQ"] == "caja_liquidez"
    assert contract["pathology_axis"]["INV_001"] == "stock_reposicion"
    assert contract["copy_templates"]["misaligned_reconduction"]
    assert contract["copy_templates"]["misaligned_technical_reference"]


def test_question_alignment_contract_requires_active_status():
    contract = load_question_alignment_contract().copy()
    contract["status"] = "DRAFT"

    with pytest.raises(QuestionAlignmentContractError):
        validate_question_alignment_contract(contract)


def test_question_alignment_contract_requires_owner_keywords():
    contract = load_question_alignment_contract().copy()
    contract.pop("owner_keywords")

    with pytest.raises(QuestionAlignmentContractError):
        validate_question_alignment_contract(contract)


def test_question_alignment_contract_requires_copy_templates():
    contract = load_question_alignment_contract().copy()
    contract["copy_templates"] = {}

    with pytest.raises(QuestionAlignmentContractError):
        validate_question_alignment_contract(contract)
