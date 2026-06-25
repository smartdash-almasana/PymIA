from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_confirmation_applier_v1 import (
    SCHEMA_VERSION,
    apply_service_1_column_confirmation_v1,
)
from pymia.smartpyme.service_1_column_confirmation_classifier_v1 import (
    classify_owner_column_confirmation_answer,
)

TARGET_REF = "file:ventas.xlsx:sheet:Ventas:column:Total"


def _matrix_with_total(role: str = "venta_total") -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
        file_name="ventas.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role=role,
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            )
        ],
    )


def _classify(raw: str, role: str = "venta_total"):
    return classify_owner_column_confirmation_answer(
        raw_owner_answer=raw,
        question_target_ref=TARGET_REF,
        proposed_role=role,
    )


def test_applies_confirmed_computational_and_unlocks() -> None:
    matrix = _matrix_with_total()
    assert matrix.can_compute_variable("ventas_total") is False

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.case_id == "case-1"
    assert result.tenant_id == "tenant-1"
    assert result.intake_id == "intake-1"
    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.CONFIRMED
    assert result.applied_entry_snapshot.owner_confirmed_role == "venta_total"
    assert matrix.entries[0].confirmation_status == ConfirmationStatus.CONFIRMED
    assert matrix.can_compute_variable("ventas_total") is True
    assert result.computation_unlocked is True
    assert "ventas_total" in result.variables_affected


def test_applies_confirmed_informational_without_computation_unlock() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="ventas.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Producto",
                sheet_name="Ventas",
                suggested_semantic_role="producto",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            )
        ],
    )
    classification = classify_owner_column_confirmation_answer(
        raw_owner_answer="Confirmo, corresponde al producto.",
        question_target_ref="file:ventas.xlsx:sheet:Ventas:column:Producto",
        proposed_role="producto",
    )

    result = apply_service_1_column_confirmation_v1(classification=classification, matrix=matrix)

    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.CONFIRMED
    assert result.applied_entry_snapshot.calculation_relevance == CalculationRelevance.INFORMATIONAL
    assert result.computation_unlocked is False
    assert result.variables_affected == []


def test_applies_not_relevant_marks_ignored() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("Ignorar esa columna, no sirve para este análisis."),
        matrix=matrix,
    )

    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.IGNORED_NOT_RELEVANT
    assert result.applied_entry_snapshot.owner_confirmed_role == "IGNORED_NOT_RELEVANT"
    assert matrix.ignored_entries()[0].original_column_name == "Total"
    assert result.computation_unlocked is False


def test_rejected_mapping_blocks_column() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("NO, no es el total de ventas."),
        matrix=matrix,
    )

    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert matrix.blocked_entries()[0].original_column_name == "Total"
    assert result.matrix_status_after == "blocked"
    assert result.computation_unlocked is False


def test_tu_respuesta_correction_blocks_without_guessing() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("Tu respuesta: esa columna es saldo pendiente, no venta total."),
        matrix=matrix,
    )

    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert result.applied_entry_snapshot.owner_confirmed_role is None
    assert result.applied_entry_snapshot.suggested_semantic_role == "venta_total"
    assert result.computation_unlocked is False


def test_insufficient_answer_does_not_unlock_and_stays_pending() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("Creo que sí, más o menos."),
        matrix=matrix,
    )

    assert result.applied_entry_snapshot.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert result.applied_entry_snapshot.owner_confirmed_role is None
    assert matrix.entries[0].confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert result.computation_unlocked is False
    assert result.variables_affected == []


def test_tracks_matrix_status_before_and_after() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
    )

    assert result.matrix_status_before == "pending_confirmation"
    assert result.matrix_status_after == "all_confirmed"


def test_tracks_computation_unlock_flags_for_custom_variable_list() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
        variables_to_track=["ventas_total", "cantidad_total"],
    )

    assert result.computation_unlocked is True
    assert result.variables_affected == ["ventas_total"]


def test_preserves_security_flags_and_declared_not_validated_status() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
    )

    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.owner_answer_validation_status == "DECLARED_NOT_VALIDATED"


def test_is_pure_no_storage_side_effects(tmp_path) -> None:
    matrix = _matrix_with_total()
    before = set(tmp_path.iterdir())

    apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
    )

    after = set(tmp_path.iterdir())
    assert after == before


def test_to_dict_serializes_snapshot_and_metadata() -> None:
    matrix = _matrix_with_total()

    result = apply_service_1_column_confirmation_v1(
        classification=_classify("SÍ, correcto."),
        matrix=matrix,
        metadata={"question_ref": "q1"},
    )

    data = result.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["metadata"] == {"question_ref": "q1"}
    assert data["applied_entry_snapshot"]["original_column_name"] == "Total"
    assert data["applied_entry_snapshot"]["confirmation_status"] == "CONFIRMED"
    assert data["parsed_target_ref"] == {
        "file_name": "ventas.xlsx",
        "sheet_name": "Ventas",
        "column_name": "Total",
    }
