from __future__ import annotations

import importlib

import pytest

from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_column_understanding_v1,
)
from pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1 import (
    SCHEMA_VERSION,
    STATUS_NO_QUESTION_REQUIRED,
    STATUS_QUESTION_READY,
    build_service_1_column_owner_question_view_v1,
    build_service_1_column_owner_question_views_v1,
)


def test_adapter_builds_human_question_for_ambiguous_header() -> None:
    understanding = build_column_understanding_v1(
        column_name="precio_lista",
        sheet_name="Ventas_Detalle",
        sample_values=[130, 260],
        inferred_data_type="number",
        co_column_names=["producto", "importe_total"],
    )

    view = build_service_1_column_owner_question_view_v1(understanding)

    assert view.schema_version == SCHEMA_VERSION
    assert view.status == STATUS_QUESTION_READY
    assert view.question_required is True
    assert "precio_lista" in view.title
    assert "Ventas_Detalle" in view.context
    assert "130" in view.context
    assert view.question
    assert "¿Qué representa esta columna en tu negocio?" in view.question
    assert "rol semantico" not in view.question.lower()
    assert len(view.options) >= 2
    assert view.options[-1].option_id == "OTHER"
    assert view.risk_note


def test_adapter_keeps_engine_options_as_stable_view_options() -> None:
    understanding = build_column_understanding_v1(
        column_name="monto",
        sheet_name="Datos",
        sample_values=[1000, 2000],
        inferred_data_type="number",
    )

    view = build_service_1_column_owner_question_view_v1(understanding)

    assert view.question_required is True
    assert [option.option_id for option in view.options] == [
        option.option_id for option in understanding.allowed_owner_answers
    ]
    assert [option.label for option in view.options] == [
        option.label for option in understanding.allowed_owner_answers
    ]


def test_adapter_returns_no_question_view_for_exact_column() -> None:
    understanding = build_column_understanding_v1(
        column_name="fecha",
        sheet_name="Ventas",
        sample_values=["2026-06-01", "2026-06-02"],
        inferred_data_type="date",
        co_column_names=["producto", "venta_total"],
    )

    view = build_service_1_column_owner_question_view_v1(understanding)

    assert view.status == STATUS_NO_QUESTION_REQUIRED
    assert view.question_required is False
    assert view.question is None
    assert view.options == ()
    assert view.risk_note is None
    assert "PymIA la interpreta" in view.confidence_note


def test_adapter_is_fail_closed_and_projection_only() -> None:
    understanding = build_column_understanding_v1(
        column_name="subtotal",
        sheet_name="Compras",
        sample_values=[2100, 6000],
        inferred_data_type="number",
        co_column_names=["fecha", "producto", "iva"],
    )

    view = build_service_1_column_owner_question_view_v1(understanding)

    assert view.runtime_authorized is False
    assert view.frontend_wiring_authorized is False
    assert view.delivery_authorized is False
    assert view.metadata["projection_only"] is True


def test_adapter_is_deterministic_and_does_not_mutate_input() -> None:
    understanding = build_column_understanding_v1(
        column_name="cliente",
        sheet_name="Cobros",
        sample_values=["Cliente A", "Cliente B"],
        inferred_data_type="text",
        co_column_names=["fecha", "factura"],
    )
    before = understanding.to_dict()

    first = build_service_1_column_owner_question_view_v1(understanding).to_dict()
    second = build_service_1_column_owner_question_view_v1(understanding).to_dict()

    assert first == second
    assert understanding.to_dict() == before


def test_batch_adapter_preserves_order() -> None:
    items = [
        build_column_understanding_v1(
            column_name="fecha",
            sheet_name="Ventas",
            sample_values=["2026-06-01"],
            inferred_data_type="date",
        ),
        build_column_understanding_v1(
            column_name="monto",
            sheet_name="Datos",
            sample_values=[1000],
            inferred_data_type="number",
        ),
    ]

    views = build_service_1_column_owner_question_views_v1(items)

    assert [view.column_name for view in views] == ["fecha", "monto"]


def test_adapter_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        build_service_1_column_owner_question_view_v1({})  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        build_service_1_column_owner_question_views_v1("bad")  # type: ignore[arg-type]


def test_module_has_no_frontend_io_or_orchestrator_dependencies() -> None:
    module = importlib.import_module(
        "pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1"
    )
    spec = importlib.util.find_spec(
        "pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1"
    )
    text = open(spec.origin, encoding="utf-8").read()  # type: ignore[union-attr]

    for token in [
        "requests.",
        "urllib",
        "subprocess",
        "os.system",
        "service_1_web_experiment",
        "service_1_assisted_flow_orchestrator",
        "import openai",
        "import anthropic",
    ]:
        assert token not in text, token
    assert module.SCHEMA_VERSION == SCHEMA_VERSION
