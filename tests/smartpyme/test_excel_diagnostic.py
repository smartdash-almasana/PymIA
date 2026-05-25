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
