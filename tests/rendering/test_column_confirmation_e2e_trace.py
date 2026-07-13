from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
)
from pymia.rendering.column_confirmation_owner_view import render_column_confirmation_owner_view


def test_total_pending_owner_view_owner_confirms_and_ventas_total_unlocks() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question='La columna "Total" representa el importe final de cada venta?',
            ),
        ],
    )

    assert matrix.can_compute_variable("ventas_total") is False

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Archivo: cafeteria_abc.xlsx" in rendered
    assert "Columna: Total" in rendered
    assert "Relevancia: computacional" in rendered
    assert 'La columna "Total" representa el importe final de cada venta?' in rendered

    matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="Si, Total es el importe final cobrado por cada venta.",
            proposed_role="venta_total",
            confirmed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL,
            unblocks_variable_names=["ventas_total"],
        )
    )

    assert matrix.can_compute_variable("ventas_total") is True
    assert matrix.entries[0].confirmation_status == ConfirmationStatus.CONFIRMED
    assert matrix.entries[0].owner_confirmed_role == "venta_total"


def test_total_pending_owner_unknown_keeps_ventas_total_blocked() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question='La columna "Total" representa el importe final de cada venta?',
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Columna: Total" in rendered
    assert matrix.can_compute_variable("ventas_total") is False

    matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="No se que significa esa columna.",
            proposed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN,
        )
    )

    assert matrix.can_compute_variable("ventas_total") is False
    assert matrix.entries[0].confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION


def test_metodo_pago_owner_view_owner_confirms_informational_and_never_unlocks_amount() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="MetodoPago",
                sheet_name="Ventas",
                suggested_semantic_role="payment_method",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question='La columna "MetodoPago" indica la forma de pago?',
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Columna: MetodoPago" in rendered
    assert "Rol sugerido: metodo o forma de pago" in rendered
    assert "monto" not in rendered.lower()
    assert "importe" not in rendered.lower()

    matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="MetodoPago",
            owner_answer_text="Si, es solo la forma de pago.",
            proposed_role="payment_method",
            confirmed_role="payment_method",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL,
        )
    )

    entry = matrix.entries[0]
    assert entry.confirmation_status == ConfirmationStatus.CONFIRMED
    assert entry.owner_confirmed_role == "payment_method"
    assert entry.calculation_relevance == CalculationRelevance.INFORMATIONAL
    assert entry.feeds_calculation() is False


def test_owner_rejects_total_mapping_and_column_becomes_blocked_ambiguous() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question='La columna "Total" representa el importe final de cada venta?',
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Columna: Total" in rendered
    assert matrix.status() == "pending_confirmation"

    matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="No, Total no es el importe de la venta.",
            proposed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
        )
    )

    assert matrix.status() == "blocked"
    assert matrix.can_compute_variable("ventas_total") is False
    assert matrix.entries[0].confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
