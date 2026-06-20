"""Tests for Corte 2: blocking computed variables when columns are not confirmed."""
from __future__ import annotations

from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
)
from tools.document_ingestion import StructuredEvidenceExporter


def _make_matrix_with_confirmed_roles(roles: set[str], existing_roles: set[str] | None = None) -> ColumnConfirmationMatrix:
    """Helper to create a matrix with specific roles confirmed."""
    from pymia.contracts.column_confirmation_v1 import infer_calculation_relevance
    entries = []
    for role in roles:
        entries.append(
            ColumnConfirmationEntry(
                original_column_name=f"col_{role}",
                sheet_name="Sheet1",
                suggested_semantic_role=role,
                calculation_relevance=infer_calculation_relevance(role),
                confirmation_status=ConfirmationStatus.CONFIRMED,
                owner_confirmed_role=role,
            )
        )
    # Add pending entries for common calc fields not in the confirmed set
    target_pending = existing_roles if existing_roles is not None else {"cantidad", "precio_venta", "venta_total", "costo_unitario"}
    for role in target_pending:
        if role not in roles:
            entries.append(
                ColumnConfirmationEntry(
                    original_column_name=f"col_{role}",
                    sheet_name="Sheet1",
                    suggested_semantic_role=role,
                    calculation_relevance=infer_calculation_relevance(role),
                    confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
                )
            )
    return ColumnConfirmationMatrix(file_name="test.xlsx", entries=entries)


def test_compute_blocks_ventas_total_when_precio_venta_not_confirmed() -> None:
    """ventas_total should not be computed if precio_venta is pending."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0},
        {"cantidad": 5, "precio_venta": 200.0},
    ]
    # Only cantidad is confirmed, precio_venta is pending
    matrix = _make_matrix_with_confirmed_roles({"cantidad"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "ventas_total" not in computed
    blocking_warnings = [w for w in warnings if w["reason_code"] == "COLUMN_CONFIRMATION_PENDING"]
    assert any("ventas_total" in w["source_field"] for w in blocking_warnings)


def test_compute_blocks_ventas_total_when_cantidad_not_confirmed() -> None:
    """ventas_total should not be computed if cantidad is pending."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0},
    ]
    # Only precio_venta is confirmed, cantidad is pending
    matrix = _make_matrix_with_confirmed_roles({"precio_venta"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "ventas_total" not in computed


def test_compute_allows_ventas_total_when_all_required_confirmed() -> None:
    """ventas_total should be computed when cantidad and precio_venta are confirmed."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0},
        {"cantidad": 5, "precio_venta": 200.0},
    ]
    matrix = _make_matrix_with_confirmed_roles({"cantidad", "precio_venta"}, existing_roles={"cantidad", "precio_venta"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "ventas_total" in computed
    assert computed["ventas_total"] == 2000.0  # (10*100) + (5*200)


def test_compute_blocks_costos_total_when_costo_unitario_not_confirmed() -> None:
    """costos_total should not be computed if costo_unitario is pending."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "costo_unitario": 50.0},
    ]
    matrix = _make_matrix_with_confirmed_roles({"cantidad"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "costos_total" not in computed


def test_compute_blocks_margen_bruto_when_dependencies_not_confirmed() -> None:
    """margen_bruto should not be computed if any dependency is pending."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0, "costo_unitario": 50.0},
    ]
    # Only cantidad confirmed
    matrix = _make_matrix_with_confirmed_roles({"cantidad"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "margen_bruto" not in computed


def test_compute_blocks_cantidad_total_when_cantidad_not_confirmed() -> None:
    """cantidad_total should not be computed if cantidad is pending."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10},
        {"cantidad": 20},
    ]
    matrix = _make_matrix_with_confirmed_roles(set())  # Nothing confirmed

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "cantidad_total" not in computed


def test_compute_without_matrix_computes_normally() -> None:
    """Without a matrix (legacy behavior), compute normally."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0},
    ]
    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=None)

    assert "ventas_total" in computed
    assert computed["ventas_total"] == 1000.0


def test_compute_emits_blocking_warning_with_column_names() -> None:
    """Blocking warning should include the names of pending columns."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0},
    ]
    matrix = _make_matrix_with_confirmed_roles(set())  # Nothing confirmed

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    blocking_warnings = [w for w in warnings if w["reason_code"] == "COLUMN_CONFIRMATION_PENDING"]
    assert len(blocking_warnings) >= 1
    # Warning should mention the variable and pending columns
    ventas_warning = next(
        (w for w in blocking_warnings if "ventas_total" in w["source_field"]),
        None,
    )
    assert ventas_warning is not None
    assert ventas_warning["blocks_calculation"] is True
    assert "pending_columns" in ventas_warning["operator_detail"]


def test_compute_allows_margen_bruto_when_all_confirmed() -> None:
    """margen_bruto should be computed when all dependencies are confirmed."""
    exporter = StructuredEvidenceExporter()
    rows = [
        {"cantidad": 10, "precio_venta": 100.0, "costo_unitario": 60.0},
    ]
    matrix = _make_matrix_with_confirmed_roles({"cantidad", "precio_venta", "costo_unitario"}, existing_roles={"cantidad", "precio_venta", "costo_unitario"})

    computed, warnings = exporter._compute_variables(rows, column_confirmation_matrix=matrix)

    assert "margen_bruto" in computed
    # margen = (100 - 60) * 10 = 400
    assert computed["margen_bruto"] == 400.0
