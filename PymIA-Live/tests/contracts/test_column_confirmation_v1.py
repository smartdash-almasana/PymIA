from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    infer_calculation_relevance,
)


def test_infer_calculation_relevance_for_venta_total() -> None:
    assert infer_calculation_relevance("venta_total") == CalculationRelevance.VENTAS


def test_infer_calculation_relevance_for_costo_unitario() -> None:
    assert infer_calculation_relevance("costo_unitario") == CalculationRelevance.COSTOS


def test_infer_calculation_relevance_for_margen() -> None:
    assert infer_calculation_relevance("margen") == CalculationRelevance.MARGEN


def test_infer_calculation_relevance_for_cantidad() -> None:
    assert infer_calculation_relevance("cantidad") == CalculationRelevance.CANTIDADES


def test_infer_calculation_relevance_for_stock() -> None:
    assert infer_calculation_relevance("stock") == CalculationRelevance.STOCK


def test_infer_calculation_relevance_for_pago() -> None:
    assert infer_calculation_relevance("pago") == CalculationRelevance.PAGOS


def test_infer_calculation_relevance_for_canal() -> None:
    assert infer_calculation_relevance("canal") == CalculationRelevance.SEGMENTATION


def test_infer_calculation_relevance_for_producto() -> None:
    assert infer_calculation_relevance("producto") == CalculationRelevance.INFORMATIONAL


def test_infer_calculation_relevance_for_unknown() -> None:
    assert infer_calculation_relevance("unknown") == CalculationRelevance.INFORMATIONAL


def test_column_confirmation_entry_feeds_calculation_for_ventas() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="VentaTotal",
        sheet_name="Ventas",
        suggested_semantic_role="venta_total",
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )
    assert entry.feeds_calculation() is True


def test_column_confirmation_entry_does_not_feed_calculation_for_informational() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="Producto",
        sheet_name="Ventas",
        suggested_semantic_role="producto",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confirmation_status=ConfirmationStatus.IGNORED_NOT_RELEVANT,
    )
    assert entry.feeds_calculation() is False


def test_column_confirmation_entry_is_actionable_when_pending() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="PrecioUnitario",
        sheet_name="Ventas",
        suggested_semantic_role="precio_venta",
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )
    assert entry.is_actionable() is True


def test_column_confirmation_entry_is_actionable_when_blocked() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="Importe",
        sheet_name="Ventas",
        suggested_semantic_role="unknown",
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.BLOCKED_AMBIGUOUS,
    )
    assert entry.is_actionable() is True


def test_column_confirmation_entry_is_not_actionable_when_confirmed() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="VentaTotal",
        sheet_name="Ventas",
        suggested_semantic_role="venta_total",
        calculation_relevance=CalculationRelevance.VENTAS,
        confirmation_status=ConfirmationStatus.CONFIRMED,
        owner_confirmed_role="venta_total",
    )
    assert entry.is_actionable() is False


def test_column_confirmation_entry_is_not_actionable_when_ignored() -> None:
    entry = ColumnConfirmationEntry(
        original_column_name="Producto",
        sheet_name="Ventas",
        suggested_semantic_role="producto",
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confirmation_status=ConfirmationStatus.IGNORED_NOT_RELEVANT,
    )
    assert entry.is_actionable() is False


def test_matrix_status_pending_confirmation() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="PrecioUnitario",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )
    assert matrix.status() == "pending_confirmation"


def test_matrix_status_all_confirmed() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="VentaTotal",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                owner_confirmed_role="venta_total",
            ),
        ],
    )
    assert matrix.status() == "all_confirmed"


def test_matrix_status_blocked() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Importe",
                sheet_name="Ventas",
                suggested_semantic_role="unknown",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.BLOCKED_AMBIGUOUS,
            ),
        ],
    )
    assert matrix.status() == "blocked"


def test_matrix_status_no_columns() -> None:
    matrix = ColumnConfirmationMatrix(file_name="test.xlsx", entries=[])
    assert matrix.status() == "no_columns"


def test_matrix_confirmed_entries() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="VentaTotal",
                sheet_name="Ventas",
                suggested_semantic_role="venta_total",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            ColumnConfirmationEntry(
                original_column_name="PrecioUnitario",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )
    assert len(matrix.confirmed_entries()) == 1
    assert matrix.confirmed_entries()[0].original_column_name == "VentaTotal"


def test_matrix_pending_entries() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="PrecioUnitario",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )
    assert len(matrix.pending_entries()) == 1


def test_matrix_blocked_entries() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Importe",
                sheet_name="Ventas",
                suggested_semantic_role="unknown",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.BLOCKED_AMBIGUOUS,
            ),
        ],
    )
    assert len(matrix.blocked_entries()) == 1


def test_matrix_ignored_entries() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Producto",
                sheet_name="Ventas",
                suggested_semantic_role="producto",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.IGNORED_NOT_RELEVANT,
            ),
        ],
    )
    assert len(matrix.ignored_entries()) == 1


def test_matrix_actionable_for_calculation() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="PrecioUnitario",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
            ColumnConfirmationEntry(
                original_column_name="Producto",
                sheet_name="Ventas",
                suggested_semantic_role="producto",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )
    actionable = matrix.actionable_for_calculation()
    assert len(actionable) == 1
    assert actionable[0].original_column_name == "PrecioUnitario"


def test_matrix_can_compute_variable_when_all_confirmed() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Cantidad",
                sheet_name="Ventas",
                suggested_semantic_role="cantidad",
                calculation_relevance=CalculationRelevance.CANTIDADES,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            ColumnConfirmationEntry(
                original_column_name="PrecioVenta",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
        ],
    )
    assert matrix.can_compute_variable("ventas_total") is True


def test_matrix_cannot_compute_variable_when_pending() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Cantidad",
                sheet_name="Ventas",
                suggested_semantic_role="cantidad",
                calculation_relevance=CalculationRelevance.CANTIDADES,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
            ColumnConfirmationEntry(
                original_column_name="PrecioVenta",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
        ],
    )
    assert matrix.can_compute_variable("ventas_total") is False


def test_matrix_owner_questions() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="PrecioUnitario",
                sheet_name="Ventas",
                suggested_semantic_role="precio_venta",
                calculation_relevance=CalculationRelevance.VENTAS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                owner_question="¿Es el precio cobrado al cliente?",
            ),
        ],
    )
    questions = matrix.owner_questions()
    assert len(questions) == 1
    assert questions[0]["column"] == "PrecioUnitario"
    assert questions[0]["question"] == "¿Es el precio cobrado al cliente?"
    assert questions[0]["suggested_role"] == "precio_venta"
    assert questions[0]["relevance"] == "VENTAS"
    assert questions[0]["status"] == "PENDING_OWNER_CONFIRMATION"


def test_matrix_owner_questions_excludes_ignored() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Producto",
                sheet_name="Ventas",
                suggested_semantic_role="producto",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.IGNORED_NOT_RELEVANT,
                owner_question=None,
            ),
        ],
    )
    assert matrix.owner_questions() == []
