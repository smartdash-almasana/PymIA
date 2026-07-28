from __future__ import annotations

from pathlib import Path

import pandas as pd

from pymia.smartpyme.excel_diagnostic import diagnose_excel


def test_excel_diagnostic_slice_detects_expected_findings_and_writes_markdown(tmp_path: Path) -> None:
    excel_path = tmp_path / "ventas_costos.xlsx"
    markdown_path = tmp_path / "diagnostic.md"

    df = pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 95},   # margen bajo
            {"producto": "A", "ventas": 100, "costo": 95},   # duplicada
            {"producto": "B", "ventas": 120, "costo": None}, # sin costo
            {"producto": "C", "ventas": 0, "costo": 30},     # no calculable
            {"producto": None, "ventas": 80, "costo": 20},   # vacío relevante
        ]
    )
    df.to_excel(excel_path, index=False)

    result = diagnose_excel(
        excel_path=excel_path,
        tenant_id="tenant-smartpyme-slice",
        markdown_output_path=markdown_path,
    )

    assert result.evidence.tenant_id == "tenant-smartpyme-slice"
    assert markdown_path.exists()
    assert "tenant_id: `tenant-smartpyme-slice`" in markdown_path.read_text(encoding="utf-8")

    codes = {f.code for f in result.findings}
    assert "EMPTY_PRODUCT" in codes
    assert "DUPLICATE_ROWS" in codes
    assert "PRODUCT_WITHOUT_COST" in codes
    assert "LOW_MARGIN" in codes
    assert "MARGIN_NOT_CALCULABLE" in codes
    assert result.evidence.sheets_processed == 1


def test_excel_diagnostic_multisheet_no_false_positives(tmp_path: Path) -> None:
    excel_path = tmp_path / "multi.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame(
            [
                {"fecha": "2026-05-01", "producto": "A", "cantidad": 2, "precio_unitario_vendido": 10, "importe_total": 20},
                {"fecha": "2026-05-02", "producto": "B", "cantidad": 1, "precio_unitario_vendido": 11, "importe_total": 11},
            ]
        ).to_excel(writer, sheet_name="ventas", index=False)
        pd.DataFrame(
            [
                {"fecha": "2026-05-01", "producto": "A", "cantidad_comprada": 2, "costo_unitario": 7},
                {"fecha": "2026-05-02", "producto": "B", "cantidad_comprada": 1, "costo_unitario": 8},
            ]
        ).to_excel(writer, sheet_name="compras", index=False)
        pd.DataFrame([{"sku": "A", "producto": "A", "costo_unitario_actual": 7}]).to_excel(
            writer, sheet_name="productos", index=False
        )
        pd.DataFrame([{"mes": "mayo", "ventas_brutas": 31, "costo_variable": 22, "margen_bruto": 9, "costos_fijos": 4}]).to_excel(
            writer, sheet_name="resumen_mensual", index=False
        )

    result = diagnose_excel(excel_path=excel_path, tenant_id="tenant-multi")
    high_missing = {(f.code, f.sheet_name) for f in result.findings if f.severity == "high"}
    assert ("EMPTY_SALES", "compras") not in high_missing
    assert ("EMPTY_COST", "ventas") not in high_missing
    assert result.evidence.sheets_processed == 4


def test_excel_diagnostic_single_sheet_backward_compatible(tmp_path: Path) -> None:
    excel_path = tmp_path / "single.xlsx"
    pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 80},
            {"producto": "B", "ventas": 50, "costo": None},
        ]
    ).to_excel(excel_path, index=False)

    result = diagnose_excel(excel_path=excel_path, tenant_id="tenant-single")
    codes = {f.code for f in result.findings}
    assert "PRODUCT_WITHOUT_COST" in codes
    assert result.evidence.sheets_processed == 1


def test_excel_diagnostic_detects_empty_cells_in_correct_sheet(tmp_path: Path) -> None:
    excel_path = tmp_path / "empty-per-sheet.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame(
            [
                {"fecha": "2026-05-01", "producto": "A", "cantidad": 2, "precio_unitario_vendido": None, "importe_total": 20},
            ]
        ).to_excel(writer, sheet_name="ventas", index=False)
        pd.DataFrame(
            [
                {"fecha": "2026-05-01", "producto": "A", "cantidad_comprada": 2, "costo_unitario": None},
            ]
        ).to_excel(writer, sheet_name="compras", index=False)

    result = diagnose_excel(excel_path=excel_path, tenant_id="tenant-empty")
    sales_empty = [f for f in result.findings if f.code == "EMPTY_SALES"]
    cost_empty = [f for f in result.findings if f.code == "EMPTY_COST"]
    assert any(f.sheet_name == "ventas" and f.severity == "medium" for f in sales_empty)
    assert any(f.sheet_name == "compras" and f.severity == "medium" for f in cost_empty)


def test_excel_diagnostic_recognizes_spanish_aliases(tmp_path: Path) -> None:
    excel_path = tmp_path / "aliases.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame(
            [
                {"producto": "A", "cantidad": 2, "precio_unitario_vendido": 10, "importe_total": 20},
            ]
        ).to_excel(writer, sheet_name="ventas", index=False)
        pd.DataFrame(
            [
                {"producto": "A", "cantidad_comprada": 2, "costo_unitario": 7},
            ]
        ).to_excel(writer, sheet_name="compras", index=False)
        pd.DataFrame([{"mes": "mayo", "ventas_brutas": 20, "costo_variable": 14, "margen_bruto": 6, "costos_fijos": 2}]).to_excel(
            writer, sheet_name="resumen_mensual", index=False
        )

    result = diagnose_excel(excel_path=excel_path, tenant_id="tenant-aliases")
    high = [f.code for f in result.findings if f.severity == "high"]
    assert "EMPTY_SALES" not in high
    assert "EMPTY_COST" not in high
