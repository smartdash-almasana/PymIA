from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from pymia.rendering.column_confirmation_owner_view import render_column_confirmation_owner_view


def test_renders_pending_column_questions() -> None:
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

    assert "Confirmacion de columnas" in rendered
    assert "Archivo: cafeteria_abc.xlsx" in rendered
    assert "Hoja: Ventas" in rendered
    assert "Columna: Total" in rendered
    assert 'La columna "Total" representa el importe final de cada venta?' in rendered


def test_excludes_confirmed_columns() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                owner_confirmed_role="venta_total",
                owner_question="Debe quedar oculto",
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "No hay confirmaciones de columnas pendientes" in rendered
    assert "Debe quedar oculto" not in rendered
    assert "Columna: Total" not in rendered


def test_excludes_ignored_columns() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Observaciones",
                sheet_name="Ventas",
                suggested_semantic_role="unknown",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.IGNORED_NOT_RELEVANT,
                owner_question="Debe quedar oculto",
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "No hay confirmaciones de columnas pendientes" in rendered
    assert "Debe quedar oculto" not in rendered
    assert "Observaciones" not in rendered


def test_distinguishes_computational_column() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Relevancia: computacional" in rendered
    assert "puede bloquear calculos dependientes" in rendered


def test_distinguishes_informational_column() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Producto",
                sheet_name="Ventas",
                suggested_semantic_role="producto",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Relevancia: informativa" in rendered
    assert "no bloquea ventas/margen" in rendered


def test_includes_allowed_response_options() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Total",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Opciones de respuesta permitidas:" in rendered
    assert "1. Si, es correcto." in rendered
    assert "2. No, significa otra cosa: ______" in rendered
    assert "3. No se." in rendered
    assert "4. Ignorar esta columna." in rendered


def test_metodo_pago_is_rendered_as_payment_method_not_amount() -> None:
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


def test_no_pending_confirmations_message() -> None:
    matrix = ColumnConfirmationMatrix(file_name="test.xlsx", entries=[])

    rendered = render_column_confirmation_owner_view(matrix)

    assert "Archivo: test.xlsx" in rendered
    assert "No hay confirmaciones de columnas pendientes para el dueno." in rendered
