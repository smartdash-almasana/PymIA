from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_confirmation_applier_v1 import (
    apply_service_1_column_confirmation_v1,
)
from pymia.smartpyme.service_1_column_confirmation_case_patch_v1 import (
    SCHEMA_VERSION,
    Service1ColumnConfirmationCasePatchKindV1,
    build_service_1_column_confirmation_case_patch_v1,
    derive_service_1_column_confirmation_case_patch_kind_v1,
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


def _matrix_with_product() -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(
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


def _applier_result(raw: str, role: str = "venta_total", matrix: ColumnConfirmationMatrix | None = None):
    matrix = matrix or _matrix_with_total(role)
    classification = classify_owner_column_confirmation_answer(
        raw_owner_answer=raw,
        question_target_ref=TARGET_REF,
        proposed_role=role,
    )
    return apply_service_1_column_confirmation_v1(
        classification=classification,
        matrix=matrix,
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
    )


def test_patch_confirm_computational_with_unlock() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("SÍ, correcto."),
    )

    assert patch.schema_version == SCHEMA_VERSION
    assert patch.patch_kind == Service1ColumnConfirmationCasePatchKindV1.CONFIRM_COMPUTATIONAL
    assert patch.computation_unlocked is True
    assert "ventas_total" in patch.variables_affected
    assert patch.applied_entry_snapshot.confirmation_status == ConfirmationStatus.CONFIRMED


def test_patch_confirm_informational_without_unlock() -> None:
    matrix = _matrix_with_product()
    classification = classify_owner_column_confirmation_answer(
        raw_owner_answer="Confirmo, corresponde al producto.",
        question_target_ref="file:ventas.xlsx:sheet:Ventas:column:Producto",
        proposed_role="producto",
    )
    applier_result = apply_service_1_column_confirmation_v1(
        classification=classification,
        matrix=matrix,
    )

    patch = build_service_1_column_confirmation_case_patch_v1(applier_result=applier_result)

    assert patch.patch_kind == Service1ColumnConfirmationCasePatchKindV1.CONFIRM_INFORMATIONAL
    assert patch.computation_unlocked is False
    assert patch.variables_affected == []


def test_patch_ignore_not_relevant() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("Ignorar esa columna, no sirve."),
    )

    assert patch.patch_kind == Service1ColumnConfirmationCasePatchKindV1.IGNORE_NOT_RELEVANT
    assert patch.applied_entry_snapshot.confirmation_status == ConfirmationStatus.IGNORED_NOT_RELEVANT


def test_patch_block_rejected() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("NO, no es eso."),
    )

    assert patch.patch_kind == Service1ColumnConfirmationCasePatchKindV1.BLOCK_REJECTED
    assert patch.applied_entry_snapshot.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS


def test_patch_keep_pending() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("Creo que sí, más o menos."),
    )

    assert patch.patch_kind == Service1ColumnConfirmationCasePatchKindV1.KEEP_PENDING
    assert patch.applied_entry_snapshot.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION


def test_passthrough_case_ids_and_target_ref() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("SÍ, correcto."),
    )

    assert patch.case_id == "case-1"
    assert patch.tenant_id == "tenant-1"
    assert patch.intake_id == "intake-1"
    assert patch.target_ref == TARGET_REF
    assert patch.parsed_target_ref == {
        "file_name": "ventas.xlsx",
        "sheet_name": "Ventas",
        "column_name": "Total",
    }


def test_preserves_security_flags_and_declared_not_validated() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("SÍ, correcto."),
    )

    assert patch.runtime_authorized is False
    assert patch.human_review_required is True
    assert patch.reexecution_authorized is False
    assert patch.recalculation_authorized is False
    assert patch.persistence_authorized is False
    assert patch.owner_answer_validation_status == "DECLARED_NOT_VALIDATED"


def test_is_pure_no_filesystem_side_effects_and_does_not_mutate_applier_result(tmp_path) -> None:
    applier_result = _applier_result("SÍ, correcto.")
    before_files = set(tmp_path.iterdir())
    before_snapshot = applier_result.to_dict()

    build_service_1_column_confirmation_case_patch_v1(
        applier_result=applier_result,
        metadata={"source": "test"},
    )

    assert set(tmp_path.iterdir()) == before_files
    assert applier_result.to_dict() == before_snapshot


def test_to_dict_serializes_snapshot_patch_kind_and_metadata() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("SÍ, correcto."),
        metadata={"question_ref": "q1"},
    )

    data = patch.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["patch_kind"] == "CONFIRM_COMPUTATIONAL"
    assert data["metadata"] == {"question_ref": "q1"}
    assert data["applied_entry_snapshot"]["original_column_name"] == "Total"
    assert data["applied_entry_snapshot"]["confirmation_status"] == "CONFIRMED"


def test_patch_kind_table_is_one_to_one_without_new_heuristics() -> None:
    confirmed = ColumnConfirmationEntry(
        original_column_name="Total",
        sheet_name="Ventas",
        suggested_semantic_role="venta_total",
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )
    ignored = confirmed.model_copy(update={"confirmation_status": ConfirmationStatus.IGNORED_NOT_RELEVANT})
    blocked = confirmed.model_copy(update={"confirmation_status": ConfirmationStatus.BLOCKED_AMBIGUOUS})
    pending = confirmed.model_copy(update={"confirmation_status": ConfirmationStatus.PENDING_OWNER_CONFIRMATION})

    assert derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=confirmed,
        computation_unlocked=True,
    ) == Service1ColumnConfirmationCasePatchKindV1.CONFIRM_COMPUTATIONAL
    assert derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=confirmed,
        computation_unlocked=False,
    ) == Service1ColumnConfirmationCasePatchKindV1.CONFIRM_INFORMATIONAL
    assert derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=ignored,
        computation_unlocked=False,
    ) == Service1ColumnConfirmationCasePatchKindV1.IGNORE_NOT_RELEVANT
    assert derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=blocked,
        computation_unlocked=False,
    ) == Service1ColumnConfirmationCasePatchKindV1.BLOCK_REJECTED
    assert derive_service_1_column_confirmation_case_patch_kind_v1(
        applied_entry_snapshot=pending,
        computation_unlocked=False,
    ) == Service1ColumnConfirmationCasePatchKindV1.KEEP_PENDING


def test_case_patch_is_frozen() -> None:
    patch = build_service_1_column_confirmation_case_patch_v1(
        applier_result=_applier_result("SÍ, correcto."),
    )

    with pytest.raises(FrozenInstanceError):
        patch.case_id = "changed"  # type: ignore[misc]
