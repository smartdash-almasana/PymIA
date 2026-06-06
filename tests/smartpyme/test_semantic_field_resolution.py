from __future__ import annotations

from pymia.smartpyme.semantic_field_resolution import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    resolve_semantic_fields,
)


def test_exact_field_match_covers_high_confidence() -> None:
    result = resolve_semantic_fields(
        parser_fields=["producto"],
        required_fields=["producto"],
    )

    assert result.covered_fields == ["producto"]
    assert result.missing_fields == []
    assert result.ambiguous_fields == []
    assert result.owner_questions_required is False
    assert result.field_resolution["producto"].confidence == CONFIDENCE_HIGH
    assert result.field_resolution["producto"].owner_confirmation_required is False


def test_fecha_or_mes_covers_periodo_high_confidence() -> None:
    result_fecha = resolve_semantic_fields(
        parser_fields=["fecha"],
        required_fields=["periodo"],
    )
    result_mes = resolve_semantic_fields(
        parser_fields=["mes"],
        required_fields=["periodo"],
    )

    assert result_fecha.covered_fields == ["periodo"]
    assert result_fecha.field_resolution["periodo"].confidence == CONFIDENCE_HIGH
    assert result_fecha.field_resolution["periodo"].owner_confirmation_required is False

    assert result_mes.covered_fields == ["periodo"]
    assert result_mes.field_resolution["periodo"].confidence == CONFIDENCE_HIGH
    assert result_mes.field_resolution["periodo"].owner_confirmation_required is False


def test_venta_total_maps_to_venta_neta_medium_with_owner_question() -> None:
    result = resolve_semantic_fields(
        parser_fields=["venta_total"],
        required_fields=["venta_neta"],
    )

    assert result.covered_fields == []
    assert result.missing_fields == ["venta_neta"]
    assert result.ambiguous_fields == ["venta_neta"]
    assert result.owner_questions_required is True
    assert result.field_resolution["venta_neta"].confidence == CONFIDENCE_MEDIUM
    assert result.field_resolution["venta_neta"].owner_confirmation_required is True
    assert "venta neta" in result.field_resolution["venta_neta"].owner_question.lower()
    assert "iva" in result.field_resolution["venta_neta"].owner_question.lower()


def test_costo_unitario_maps_to_costo_directo_medium_with_owner_question() -> None:
    result = resolve_semantic_fields(
        parser_fields=["costo_unitario"],
        required_fields=["costo_directo"],
    )

    assert result.covered_fields == []
    assert result.missing_fields == ["costo_directo"]
    assert result.ambiguous_fields == ["costo_directo"]
    assert result.owner_questions_required is True
    assert result.field_resolution["costo_directo"].confidence == CONFIDENCE_MEDIUM
    assert result.field_resolution["costo_directo"].owner_confirmation_required is True
    assert "costo directo" in result.field_resolution["costo_directo"].owner_question.lower()


def test_costos_fijos_does_not_cover_costo_directo() -> None:
    result = resolve_semantic_fields(
        parser_fields=["costos_fijos"],
        required_fields=["costo_directo"],
    )

    assert result.covered_fields == []
    assert result.missing_fields == ["costo_directo"]
    assert result.ambiguous_fields == []
    assert "costo_directo" not in result.field_resolution
    assert result.owner_questions_required is False


def test_missing_required_fields_are_reported() -> None:
    result = resolve_semantic_fields(
        parser_fields=["producto"],
        required_fields=["producto", "periodo", "venta_neta"],
    )

    assert result.covered_fields == ["producto"]
    assert "periodo" in result.missing_fields
    assert "venta_neta" in result.missing_fields
    assert result.ambiguous_fields == []


def test_textile_like_fields_resolve_with_ambiguity() -> None:
    result = resolve_semantic_fields(
        parser_fields=[
            "producto",
            "fecha",
            "venta_total",
            "costo_unitario",
            "costos_fijos",
        ],
        required_fields=["producto", "periodo", "venta_neta", "costo_directo"],
    )

    assert set(result.covered_fields) == {"producto", "periodo"}
    assert set(result.missing_fields) == {"venta_neta", "costo_directo"}
    assert set(result.ambiguous_fields) == {"venta_neta", "costo_directo"}
    assert result.owner_questions_required is True
    assert len(result.owner_questions) == 2
    assert result.field_resolution["venta_neta"].confidence == CONFIDENCE_MEDIUM
    assert result.field_resolution["costo_directo"].confidence in {
        CONFIDENCE_MEDIUM,
        CONFIDENCE_LOW,
    }
