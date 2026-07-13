from __future__ import annotations

import pytest

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    SCHEMA_VERSION,
    build_service_1_column_confirmation_owner_prompt_batch_v1,
)


def _entry(
    role: str,
    column_name: str,
    *,
    status: ConfirmationStatus = ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    relevance: CalculationRelevance = CalculationRelevance.VENTAS,
) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name="Ventas",
        sample_values=[100, 200, 300],
        inferred_type="number",
        suggested_semantic_role=role,
        calculation_relevance=relevance,
        confirmation_status=status,
        owner_question=f"Confirmame si {column_name} esta bien interpretada.",
    )


def _matrix(entries: list[ColumnConfirmationEntry]) -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(file_name="ventas.xlsx", entries=entries)


def test_matrix_with_pending_venta_total_generates_one_prompt() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("venta_total", "Total")]),
    )

    assert batch.schema_version == SCHEMA_VERSION
    assert batch.file_name == "ventas.xlsx"
    assert batch.matrix_status == "pending_confirmation"
    assert batch.total_entries == 1
    assert batch.actionable_entries_count == 1
    assert batch.has_prompts is True
    assert len(batch.prompts) == 1
    assert batch.prompts[0].suggested_semantic_role == "venta_total"
    assert batch.prompts[0].owner_label == "Ventas del periodo"
    assert "vendido" in batch.prompts[0].owner_facing_role_explanation
    assert "venta_total" not in batch.prompts[0].owner_prompt.prompt_text


def test_matrix_with_multiple_pending_columns_generates_multiple_prompts() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([
            _entry("venta_total", "Total"),
            _entry("cantidad", "Cantidad", relevance=CalculationRelevance.CANTIDADES),
            _entry("producto", "Producto", relevance=CalculationRelevance.INFORMATIONAL),
        ]),
    )

    assert batch.total_entries == 3
    assert batch.actionable_entries_count == 3
    assert len(batch.prompts) == 3
    assert [prompt.column_name for prompt in batch.prompts] == ["Total", "Cantidad", "Producto"]
    assert batch.prompts[1].owner_label == "Cantidad"
    assert batch.prompts[2].owner_label == "Producto"


def test_matrix_without_actionable_entries_returns_empty_batch() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([
            _entry("venta_total", "Total", status=ConfirmationStatus.CONFIRMED),
            _entry("producto", "Producto", status=ConfirmationStatus.IGNORED_NOT_RELEVANT, relevance=CalculationRelevance.INFORMATIONAL),
        ]),
    )

    assert batch.matrix_status == "all_confirmed"
    assert batch.total_entries == 2
    assert batch.actionable_entries_count == 0
    assert batch.prompts == ()
    assert batch.has_prompts is False


def test_empty_matrix_returns_empty_batch() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=ColumnConfirmationMatrix(file_name="empty.xlsx", entries=[]),
    )

    assert batch.file_name == "empty.xlsx"
    assert batch.matrix_status == "no_columns"
    assert batch.total_entries == 0
    assert batch.actionable_entries_count == 0
    assert batch.has_prompts is False
    assert batch.prompts == ()


def test_matrix_with_unknown_role_uses_safe_fallback_prompt() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("campo_raro", "Campo raro", relevance=CalculationRelevance.INFORMATIONAL)]),
    )

    prompt = batch.prompts[0]
    assert prompt.suggested_semantic_role == "campo_raro"
    assert prompt.owner_label == "Rol no reconocido"
    assert prompt.known_role is False
    assert "revision manual" in prompt.owner_facing_role_explanation
    assert prompt.calculation_relevance == CalculationRelevance.INFORMATIONAL.value


def test_metadata_is_propagated_to_batch_bridge_and_prompt() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("venta_total", "Total")]),
        metadata={"case_id": "case-1", "tenant_id": "tenant-1"},
    )

    assert batch.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}
    assert batch.prompts[0].metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}
    assert batch.prompts[0].owner_prompt.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}


def test_security_flags_are_preserved() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("venta_total", "Total")]),
    )

    assert batch.runtime_authorized is False
    assert batch.human_review_required is True
    assert batch.reexecution_authorized is False
    assert batch.recalculation_authorized is False
    assert batch.persistence_authorized is False
    assert batch.prompts[0].runtime_authorized is False
    assert batch.prompts[0].human_review_required is True
    assert batch.prompts[0].reexecution_authorized is False
    assert batch.prompts[0].recalculation_authorized is False
    assert batch.prompts[0].persistence_authorized is False


def test_non_actionable_entries_are_excluded() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([
            _entry("venta_total", "Total", status=ConfirmationStatus.CONFIRMED),
            _entry("cantidad", "Cantidad", status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION, relevance=CalculationRelevance.CANTIDADES),
            _entry("producto", "Producto", status=ConfirmationStatus.IGNORED_NOT_RELEVANT, relevance=CalculationRelevance.INFORMATIONAL),
            _entry("costo_total", "Costo", status=ConfirmationStatus.BLOCKED_AMBIGUOUS, relevance=CalculationRelevance.COSTOS),
        ]),
    )

    assert batch.total_entries == 4
    assert batch.actionable_entries_count == 2
    assert [prompt.column_name for prompt in batch.prompts] == ["Cantidad", "Costo"]


def test_to_dict_serializes_batch_and_nested_prompts() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("venta_total", "Total")]),
        metadata={"run_id": "run-1"},
    )

    data = batch.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["file_name"] == "ventas.xlsx"
    assert data["total_entries"] == 1
    assert data["actionable_entries_count"] == 1
    assert data["metadata"] == {"run_id": "run-1"}
    assert isinstance(data["prompts"], list)
    assert data["prompts"][0]["column_name"] == "Total"
    assert data["prompts"][0]["owner_prompt"]["prompt_text"] == batch.prompts[0].owner_prompt.prompt_text


def test_batch_is_pure_no_storage_side_effects(tmp_path) -> None:
    before = set(tmp_path.iterdir())

    build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([_entry("venta_total", "Total")]),
    )

    after = set(tmp_path.iterdir())
    assert after == before


def test_prompt_texts_exclude_internal_semantic_roles() -> None:
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=_matrix([
            _entry("venta_total", "Total"),
            _entry("costo_unitario", "Costo"),
        ]),
    )

    full_text = "\n".join(prompt.owner_prompt.prompt_text for prompt in batch.prompts)
    assert "venta_total" not in full_text
    assert "costo_unitario" not in full_text
    assert "suggested_semantic_role" not in full_text


def test_rejects_invalid_matrix_type() -> None:
    with pytest.raises(ValueError, match="matrix"):
        build_service_1_column_confirmation_owner_prompt_batch_v1(
            matrix="not-matrix",  # type: ignore[arg-type]
        )


def test_rejects_invalid_metadata_type() -> None:
    with pytest.raises(ValueError, match="metadata"):
        build_service_1_column_confirmation_owner_prompt_batch_v1(
            matrix=_matrix([_entry("venta_total", "Total")]),
            metadata="bad",  # type: ignore[arg-type]
        )
