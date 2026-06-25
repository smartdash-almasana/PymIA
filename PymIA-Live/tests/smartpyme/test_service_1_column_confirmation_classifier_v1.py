from __future__ import annotations

import pytest

from pymia.contracts.column_confirmation_v1 import (
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
)
from pymia.smartpyme.service_1_column_confirmation_classifier_v1 import (
    OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
    SCHEMA_VERSION,
    classify_owner_column_confirmation_answer,
    parse_column_target_ref,
)

TARGET_REF = "file:ventas_marzo.xlsx:sheet:Ventas:column:Total"


def test_parse_column_target_ref_valid() -> None:
    parsed = parse_column_target_ref(TARGET_REF)

    assert parsed.file_name == "ventas_marzo.xlsx"
    assert parsed.sheet_name == "Ventas"
    assert parsed.column_name == "Total"
    assert parsed.to_dict() == {
        "file_name": "ventas_marzo.xlsx",
        "sheet_name": "Ventas",
        "column_name": "Total",
    }


@pytest.mark.parametrize(
    "target_ref",
    [
        "",
        "sheet:Ventas:column:Total",
        "file:ventas.xlsx:column:Total",
        "file:ventas.xlsx:sheet:Ventas",
        "file::sheet:Ventas:column:Total",
        "file:ventas.xlsx:sheet::column:Total",
        "file:ventas.xlsx:sheet:Ventas:column:",
    ],
)
def test_parse_column_target_ref_rejects_invalid(target_ref: str) -> None:
    with pytest.raises(ValueError):
        parse_column_target_ref(target_ref)


def test_classifies_explicit_confirmation_as_computational() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Sí, correcto. Es el total cobrado por la venta.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    answer = result.owner_column_confirmation_answer
    assert isinstance(answer, OwnerColumnConfirmationAnswer)
    assert answer.sheet_name == "Ventas"
    assert answer.column_name == "Total"
    assert answer.owner_answer_text == "Sí, correcto. Es el total cobrado por la venta."
    assert answer.proposed_role == "venta_total"
    assert answer.confirmed_role == "venta_total"
    assert answer.outcome == OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL
    assert answer.unlocks_computation() is True


def test_classifies_explicit_confirmation_as_informational_when_role_is_informational() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Confirmo, corresponde a producto.",
        question_target_ref="file:ventas.xlsx:sheet:Ventas:column:Producto",
        suggested_semantic_role="producto",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.proposed_role == "producto"
    assert answer.confirmed_role == "producto"
    assert answer.outcome == OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL
    assert answer.marks_informational() is True


def test_classifies_explicit_negation_as_not_relevant() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="No, esa columna no corresponde para este análisis.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.outcome == OwnerColumnConfirmationOutcome.CONFIRMED_NOT_RELEVANT
    assert answer.confirmed_role is None
    assert answer.marks_not_relevant() is True
    assert answer.unlocks_computation() is False


def test_classifies_explicit_ignore_as_not_relevant() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Ignorar esa columna, no sirve.",
        question_target_ref="file:ventas.xlsx:sheet:Ventas:column:Observaciones",
        proposed_role="unknown",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.outcome == OwnerColumnConfirmationOutcome.CONFIRMED_NOT_RELEVANT
    assert answer.column_name == "Observaciones"


def test_classifies_ambiguous_answer_as_insufficient() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Creo que sí, más o menos.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
    assert answer.confirmed_role is None
    assert answer.unlocks_computation() is False
    assert "ambiguous" in (answer.reason or "")


def test_classifies_short_answer_as_insufficient() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="ok",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
    assert answer.confirmed_role is None


def test_confirmation_with_unknown_role_does_not_unlock_computation() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Sí, correcto.",
        question_target_ref=TARGET_REF,
        proposed_role="unknown",
    )

    answer = result.owner_column_confirmation_answer
    assert answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
    assert answer.confirmed_role is None
    assert answer.unlocks_computation() is False


def test_preserves_security_flags_and_declared_not_validated_status() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Sí, correcto.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == "SERVICE_1"
    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.owner_answer_validation_status == OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED


def test_to_dict_serializes_answer_and_target() -> None:
    result = classify_owner_column_confirmation_answer(
        raw_owner_answer="Sí, correcto.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
        metadata={"question_ref": "q1"},
    )

    data = result.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["parsed_target_ref"] == {
        "file_name": "ventas_marzo.xlsx",
        "sheet_name": "Ventas",
        "column_name": "Total",
    }
    assert data["owner_column_confirmation_answer"]["owner_answer_text"] == "Sí, correcto."
    assert data["owner_column_confirmation_answer"]["outcome"] == "CONFIRMED_COMPUTATIONAL"
    assert data["metadata"] == {"question_ref": "q1"}


def test_classifier_is_pure_and_does_not_require_storage(tmp_path) -> None:
    before = set(tmp_path.iterdir())

    classify_owner_column_confirmation_answer(
        raw_owner_answer="Sí, correcto.",
        question_target_ref=TARGET_REF,
        proposed_role="venta_total",
    )

    after = set(tmp_path.iterdir())
    assert after == before
