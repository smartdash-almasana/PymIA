from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_column_confirmation_owner_prompt_v1 import (
    ALLOWED_OWNER_RESPONSES,
    OWNER_RESPONSE_NO,
    OWNER_RESPONSE_SI,
    OWNER_RESPONSE_TU_RESPUESTA,
    SCHEMA_VERSION,
    build_service_1_column_confirmation_owner_prompt_v1,
)


def test_renders_sales_column_prompt_in_natural_language() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas_marzo.xlsx",
        sheet_name="Ventas",
        column_name="Ventas",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa las ventas de este período.",
    )

    assert "Dueño, revisé tu Excel y entendí esta columna así:" in prompt.prompt_text
    assert 'Columna: "Ventas"' in prompt.prompt_text
    assert "Esta columna representa las ventas de este período." in prompt.prompt_text
    assert "Confirmame:" in prompt.prompt_text


def test_renders_cost_column_prompt_in_natural_language() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="costos.xlsx",
        sheet_name="Productos",
        column_name="Costo",
        suggested_semantic_role="costo_unitario",
        owner_facing_role_explanation="Esta columna representa el valor en pesos que cuesta cada producto.",
    )

    assert 'Columna: "Costo"' in prompt.prompt_text
    assert "valor en pesos que cuesta cada producto" in prompt.prompt_text
    assert "costo_unitario" not in prompt.prompt_text


def test_renders_quantity_column_prompt_in_natural_language() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="stock.xlsx",
        sheet_name="Movimientos",
        column_name="Cantidad",
        suggested_semantic_role="cantidad",
        owner_facing_role_explanation="Esta columna representa las unidades vendidas, compradas o movidas en el período.",
    )

    assert 'Columna: "Cantidad"' in prompt.prompt_text
    assert "unidades vendidas, compradas o movidas" in prompt.prompt_text


def test_includes_exact_allowed_owner_responses() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas.xlsx",
        sheet_name="Ventas",
        column_name="Importe",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa el importe vendido en el período.",
    )

    assert prompt.allowed_owner_responses == ALLOWED_OWNER_RESPONSES
    assert prompt.allowed_owner_responses == (
        OWNER_RESPONSE_SI,
        OWNER_RESPONSE_NO,
        OWNER_RESPONSE_TU_RESPUESTA,
    )
    assert "SÍ = correcto" in prompt.prompt_text
    assert "NO = no es eso" in prompt.prompt_text
    assert "TU_RESPUESTA = corregime qué significa" in prompt.prompt_text


def test_does_not_expose_internal_semantic_role_to_owner() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas.xlsx",
        sheet_name="Ventas",
        column_name="Total",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa el total vendido o facturado en el período.",
    )

    assert "venta_total" not in prompt.prompt_text
    assert "computed_variables" not in prompt.prompt_text
    assert prompt.suggested_semantic_role == "venta_total"


def test_rejects_owner_prompt_copy_that_leaks_internal_terms() -> None:
    with pytest.raises(ValueError):
        build_service_1_column_confirmation_owner_prompt_v1(
            file_name="ventas.xlsx",
            sheet_name="Ventas",
            column_name="Total",
            suggested_semantic_role="venta_total",
            owner_facing_role_explanation="Esta columna representa venta_total.",
        )


def test_preserves_security_flags() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas.xlsx",
        sheet_name="Ventas",
        column_name="Total",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa el total vendido o facturado en el período.",
    )

    assert prompt.schema_version == SCHEMA_VERSION
    assert prompt.service_name == "SERVICE_1"
    assert prompt.runtime_authorized is False
    assert prompt.human_review_required is True
    assert prompt.reexecution_authorized is False
    assert prompt.recalculation_authorized is False


def test_to_dict_serializes_allowed_owner_responses_as_list() -> None:
    prompt = build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas.xlsx",
        sheet_name="Ventas",
        column_name="Total",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa el total vendido o facturado en el período.",
        metadata={"question_ref": "q1"},
    )

    data = prompt.to_dict()
    assert data["allowed_owner_responses"] == ["SÍ", "NO", "TU_RESPUESTA"]
    assert data["metadata"] == {"question_ref": "q1"}
    assert data["prompt_text"] == prompt.prompt_text


def test_prompt_builder_is_pure_and_does_not_require_storage(tmp_path) -> None:
    before = set(tmp_path.iterdir())

    build_service_1_column_confirmation_owner_prompt_v1(
        file_name="ventas.xlsx",
        sheet_name="Ventas",
        column_name="Total",
        suggested_semantic_role="venta_total",
        owner_facing_role_explanation="Esta columna representa el total vendido o facturado en el período.",
    )

    after = set(tmp_path.iterdir())
    assert after == before


@pytest.mark.parametrize(
    "field_name, kwargs",
    [
        ("file_name", {"file_name": ""}),
        ("sheet_name", {"sheet_name": ""}),
        ("column_name", {"column_name": ""}),
        ("suggested_semantic_role", {"suggested_semantic_role": ""}),
        ("owner_facing_role_explanation", {"owner_facing_role_explanation": ""}),
    ],
)
def test_requires_minimum_text_fields(field_name: str, kwargs: dict[str, str]) -> None:
    base = {
        "file_name": "ventas.xlsx",
        "sheet_name": "Ventas",
        "column_name": "Total",
        "suggested_semantic_role": "venta_total",
        "owner_facing_role_explanation": "Esta columna representa el total vendido o facturado en el período.",
    }
    base.update(kwargs)

    with pytest.raises(ValueError, match=field_name):
        build_service_1_column_confirmation_owner_prompt_v1(**base)
