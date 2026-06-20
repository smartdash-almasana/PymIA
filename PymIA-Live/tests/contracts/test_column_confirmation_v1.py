from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
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


def test_owner_answer_confirms_computational_column_and_unblocks_variable() -> None:
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
    assert matrix.can_compute_variable("ventas_total") is False

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="Sí, es el importe final cobrado por cada venta.",
            proposed_role="unknown",
            confirmed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL,
            unblocks_variable_names=["ventas_total"],
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.CONFIRMED
    assert entry.owner_confirmed_role == "venta_total"
    assert entry.suggested_semantic_role == "venta_total"
    assert entry.calculation_relevance == CalculationRelevance.VENTAS
    assert matrix.can_compute_variable("ventas_total") is True


def test_owner_answer_confirms_informational_column_without_unblocking_money_calculation() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="MetodoPago",
                sheet_name="Ventas",
                suggested_semantic_role="unknown",
                calculation_relevance=CalculationRelevance.PAGOS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="MetodoPago",
            owner_answer_text="Sí, indica si fue efectivo, tarjeta o transferencia.",
            proposed_role="unknown",
            confirmed_role="payment_method",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.CONFIRMED
    assert entry.owner_confirmed_role == "payment_method"
    assert entry.calculation_relevance == CalculationRelevance.INFORMATIONAL
    assert entry.feeds_calculation() is False
    assert matrix.can_compute_variable("ventas_total") is True


def test_owner_unknown_answer_keeps_column_pending_and_does_not_unlock() -> None:
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

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="No sé qué significa esa columna.",
            proposed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.OWNER_UNKNOWN,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert matrix.can_compute_variable("ventas_total") is False


def test_owner_rejected_mapping_blocks_column_as_ambiguous() -> None:
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

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="No, Total no es el importe de la venta.",
            proposed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.BLOCKED_AMBIGUOUS
    assert matrix.status() == "blocked"
    assert matrix.can_compute_variable("ventas_total") is False


def test_owner_explicitly_ignores_column_only_after_answer() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="test.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="Observaciones",
                sheet_name="Ventas",
                suggested_semantic_role="unknown",
                calculation_relevance=CalculationRelevance.INFORMATIONAL,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Observaciones",
            owner_answer_text="Ignorar esa columna, no sirve para este análisis.",
            proposed_role="unknown",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_NOT_RELEVANT,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.IGNORED_NOT_RELEVANT
    assert entry.owner_confirmed_role == "IGNORED_NOT_RELEVANT"
    assert entry.feeds_calculation() is False


def test_metodo_pago_confirmed_as_payment_method_never_becomes_amount() -> None:
    matrix = ColumnConfirmationMatrix(
        file_name="cafeteria_abc.xlsx",
        entries=[
            ColumnConfirmationEntry(
                original_column_name="MetodoPago",
                sheet_name="Ventas",
                suggested_semantic_role="pago",
                calculation_relevance=CalculationRelevance.PAGOS,
                confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
            ),
        ],
    )

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="MetodoPago",
            owner_answer_text="Es sólo la forma de pago.",
            proposed_role="pago",
            confirmed_role="payment_method",
            outcome=OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.CONFIRMED
    assert entry.suggested_semantic_role == "payment_method"
    assert entry.calculation_relevance == CalculationRelevance.INFORMATIONAL
    assert entry.feeds_calculation() is False


def test_insufficient_owner_answer_keeps_column_pending() -> None:
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

    entry = matrix.apply_owner_answer(
        OwnerColumnConfirmationAnswer(
            sheet_name="Ventas",
            column_name="Total",
            owner_answer_text="Creo que sí, más o menos.",
            proposed_role="venta_total",
            outcome=OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
        )
    )

    assert entry.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION
    assert matrix.can_compute_variable("ventas_total") is False
