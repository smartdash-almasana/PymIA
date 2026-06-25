from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ConfirmationStatus,
)
from pymia.smartpyme.service_1_column_interpretation_to_owner_prompt_bridge_v1 import (
    SCHEMA_VERSION,
    build_service_1_column_interpretation_to_owner_prompt_bridge_v1,
)


def _entry(role: str, column_name: str = "Total") -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name="Ventas",
        sample_values=[1000, 2000, 3000],
        inferred_type="number",
        suggested_semantic_role=role,
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
        owner_question="Confirmame si esta columna significa ventas.",
    )


def test_bridges_venta_total_to_owner_prompt() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.file_name == "ventas.xlsx"
    assert result.sheet_name == "Ventas"
    assert result.column_name == "Total"
    assert result.suggested_semantic_role == "venta_total"
    assert result.owner_label == "Ventas del periodo"
    assert "vendido" in result.owner_facing_role_explanation
    assert result.known_role is True
    assert result.calculation_relevance == CalculationRelevance.VENTAS.value
    assert result.owner_prompt.prompt_text.startswith("Dueño, revisé tu Excel")
    assert result.owner_facing_role_explanation in result.owner_prompt.prompt_text
    assert "venta_total" not in result.owner_prompt.prompt_text


def test_bridges_informational_role() -> None:
    entry = _entry("producto", column_name="Producto")
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=entry,
    )

    assert result.owner_label == "Producto"
    assert result.calculation_relevance == CalculationRelevance.INFORMATIONAL.value
    assert result.known_role is True
    assert "producto" in result.owner_facing_role_explanation
    assert 'Columna: "Producto"' in result.owner_prompt.prompt_text


def test_bridges_unknown_role() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("campo_raro"),
    )

    assert result.suggested_semantic_role == "campo_raro"
    assert result.owner_label == "Rol no reconocido"
    assert result.known_role is False
    assert "revision manual" in result.owner_facing_role_explanation
    assert result.calculation_relevance == CalculationRelevance.INFORMATIONAL.value


def test_bridges_with_case_id_and_tenant_id_metadata() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
        metadata={"case_id": "case-1", "tenant_id": "tenant-1"},
    )

    assert result.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}
    assert result.owner_prompt.metadata == {"case_id": "case-1", "tenant_id": "tenant-1"}


def test_preserves_security_flags() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
    )

    assert result.runtime_authorized is False
    assert result.human_review_required is True
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.persistence_authorized is False
    assert result.owner_prompt.runtime_authorized is False
    assert result.owner_prompt.human_review_required is True


def test_prompt_text_contains_file_sheet_column() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
    )

    assert 'Archivo: "ventas.xlsx"' in result.owner_prompt.prompt_text
    assert 'Hoja: "Ventas"' in result.owner_prompt.prompt_text
    assert 'Columna: "Total"' in result.owner_prompt.prompt_text


def test_prompt_text_excludes_internal_semantic_role() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("costo_unitario", column_name="Costo"),
    )

    assert "costo_unitario" not in result.owner_prompt.prompt_text
    assert "suggested_semantic_role" not in result.owner_prompt.prompt_text
    assert 'Columna: "Costo"' in result.owner_prompt.prompt_text


def test_to_dict_serializes_all_fields() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
        metadata={"question_ref": "q1"},
    )

    data = result.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["file_name"] == "ventas.xlsx"
    assert data["sheet_name"] == "Ventas"
    assert data["column_name"] == "Total"
    assert data["suggested_semantic_role"] == "venta_total"
    assert data["owner_label"] == "Ventas del periodo"
    assert data["known_role"] is True
    assert data["metadata"] == {"question_ref": "q1"}
    assert data["owner_prompt"]["prompt_text"] == result.owner_prompt.prompt_text


def test_is_pure_no_storage_side_effects(tmp_path) -> None:
    before = set(tmp_path.iterdir())

    build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
    )

    after = set(tmp_path.iterdir())
    assert after == before


def test_entry_with_owner_question_is_not_used_as_prompt_copy() -> None:
    result = build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
        file_name="ventas.xlsx",
        entry=_entry("venta_total"),
    )

    assert "Confirmame si esta columna significa ventas." not in result.owner_prompt.prompt_text
    assert "SÍ = correcto" in result.owner_prompt.prompt_text
    assert "NO = no es eso" in result.owner_prompt.prompt_text
    assert "TU_RESPUESTA = corregime qué significa" in result.owner_prompt.prompt_text


def test_rejects_invalid_file_name() -> None:
    import pytest

    with pytest.raises(ValueError, match="file_name"):
        build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
            file_name="",
            entry=_entry("venta_total"),
        )


def test_rejects_invalid_entry_type() -> None:
    import pytest

    with pytest.raises(ValueError, match="entry"):
        build_service_1_column_interpretation_to_owner_prompt_bridge_v1(
            file_name="ventas.xlsx",
            entry="not-entry",  # type: ignore[arg-type]
        )
