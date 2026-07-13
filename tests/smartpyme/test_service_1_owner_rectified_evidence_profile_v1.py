from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    SemanticRectificationStatus,
)
from pymia.smartpyme.service_1_owner_rectified_evidence_profile_v1 import (
    MARGIN_SIGNAL,
    SALES_COLLECTION_SIGNAL,
    STOCK_SIGNAL,
    build_service_1_owner_rectified_evidence_profile_v1,
)


def _entry(
    *,
    header: str,
    rectified_function: str | None,
    suggested: str = "unknown",
    sheet: str = "Ventas",
    status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
) -> ColumnConfirmationEntry:
    return ColumnConfirmationEntry(
        original_column_name=header,
        sheet_name=sheet,
        suggested_semantic_role=suggested,
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        owner_rectified_function=rectified_function,
        owner_confirmed_role=rectified_function,
        semantic_rectification_status=(
            SemanticRectificationStatus.OWNER_CONFIRMED_AS_INFERRED
            if rectified_function == suggested
            else SemanticRectificationStatus.OWNER_RECTIFIED_TO_NEW_FUNCTION
        ),
        confirmation_status=status,
    )


def _profile(entries: list[ColumnConfirmationEntry]):
    matrix = ColumnConfirmationMatrix(file_name="pyme.xlsx", entries=entries)
    return build_service_1_owner_rectified_evidence_profile_v1(
        matrix=matrix,
        case_ref="CASE-001",
    )


def _signal(profile, signal_name: str):
    for signal in profile.evidence_signals:
        if signal.signal_name == signal_name:
            return signal
    raise AssertionError(f"signal not found: {signal_name}")


def test_margin_ready_from_owner_rectified_product_sale_and_cost() -> None:
    profile = _profile([
        _entry(header="Producto", suggested="producto", rectified_function="producto"),
        _entry(header="Precio", suggested="precio_venta", rectified_function="precio_venta"),
        _entry(header="Costo", suggested="costo_unitario", rectified_function="costo_unitario"),
    ])

    signal = _signal(profile, MARGIN_SIGNAL)

    assert signal.evidence_ready is True
    assert signal.missing_requirements == ()
    assert signal.allowed_next_steps == ("MARGIN_EVIDENCE_REVIEW",)
    assert profile.evidence_ready is True
    assert profile.runtime_authorized is False
    assert profile.tool_execution_authorized is False


def test_margin_incomplete_when_cost_is_missing() -> None:
    profile = _profile([
        _entry(header="Producto", suggested="producto", rectified_function="producto"),
        _entry(header="Precio", suggested="precio_venta", rectified_function="precio_venta"),
    ])

    signal = _signal(profile, MARGIN_SIGNAL)

    assert signal.evidence_ready is False
    assert signal.missing_requirements == ("cost_function",)
    assert "margen_basico:cost_function" in profile.missing_requirements
    assert "MARGIN_EVIDENCE_REVIEW" not in profile.allowed_next_steps


def test_stock_ready_from_owner_rectified_product_and_stock() -> None:
    profile = _profile([
        _entry(header="SKU", suggested="sku", rectified_function="sku"),
        _entry(header="StockActual", suggested="stock", rectified_function="stock"),
    ])

    signal = _signal(profile, STOCK_SIGNAL)

    assert signal.evidence_ready is True
    assert signal.missing_requirements == ()
    assert signal.allowed_next_steps == ("STOCK_EVIDENCE_REVIEW",)
    assert "STOCK_EVIDENCE_REVIEW" in profile.allowed_next_steps


def test_sales_collection_possible_from_date_sale_and_collection() -> None:
    profile = _profile([
        _entry(header="Fecha", suggested="fecha", rectified_function="fecha"),
        _entry(header="Venta", suggested="venta_total", rectified_function="venta_total"),
        _entry(header="Cobrado", suggested="cobro", rectified_function="cobro"),
    ])

    signal = _signal(profile, SALES_COLLECTION_SIGNAL)

    assert signal.evidence_ready is True
    assert signal.missing_requirements == ()
    assert signal.allowed_next_steps == ("SALES_COLLECTION_EVIDENCE_REVIEW",)
    assert "SALES_COLLECTION_EVIDENCE_REVIEW" in profile.allowed_next_steps


def test_unrectified_columns_block_profile() -> None:
    profile = _profile([
        ColumnConfirmationEntry(
            original_column_name="Precio",
            sheet_name="Ventas",
            suggested_semantic_role="precio_venta",
            calculation_relevance=CalculationRelevance.VENTAS,
            confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
        )
    ])

    assert profile.evidence_ready is False
    assert profile.source_columns == ()
    assert "NO_OWNER_RECTIFIED_FUNCTIONS" in profile.blockers
    assert "UNRECTIFIED_SEMANTIC_FUNCTION:Ventas.Precio" in profile.blockers


def test_suggested_semantic_role_is_not_enough_for_evidence() -> None:
    profile = _profile([
        ColumnConfirmationEntry(
            original_column_name="Precio",
            sheet_name="Ventas",
            suggested_semantic_role="precio_venta",
            calculation_relevance=CalculationRelevance.VENTAS,
            confirmation_status=ConfirmationStatus.CONFIRMED,
        )
    ])

    assert profile.evidence_ready is False
    assert profile.source_columns == ()
    assert profile.allowed_next_steps == ()
    assert profile.blockers == ("NO_OWNER_RECTIFIED_FUNCTIONS",)


def test_profile_never_authorizes_runtime_or_tool_execution() -> None:
    profile = _profile([
        _entry(header="Producto", suggested="producto", rectified_function="producto"),
        _entry(header="Precio", suggested="precio_venta", rectified_function="precio_venta"),
        _entry(header="Costo", suggested="costo_unitario", rectified_function="costo_unitario"),
    ])

    assert profile.runtime_authorized is False
    assert profile.tool_execution_authorized is False


def test_profile_output_is_deterministic() -> None:
    entries = [
        _entry(header="Costo", suggested="costo_unitario", rectified_function="costo_unitario"),
        _entry(header="Producto", suggested="producto", rectified_function="producto"),
        _entry(header="Precio", suggested="precio_venta", rectified_function="precio_venta"),
    ]

    first = _profile(entries).to_dict()
    second = _profile(list(reversed(entries))).to_dict()

    assert first == second
