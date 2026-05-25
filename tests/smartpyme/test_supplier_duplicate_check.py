from __future__ import annotations

from pathlib import Path

import pandas as pd

from pymia.smartpyme.classifications.supplier_duplicate_check import diagnose_supplier_duplicates


def test_supplier_duplicate_check_pass(tmp_path: Path) -> None:
    excel_path = tmp_path / "proveedores.xlsx"
    df = pd.DataFrame(
        [
            {"proveedor": "Uno", "cuit": "30-12345678-9", "razon_social": "SERVICIOS SRL"},
            {"proveedor": "Dos", "cuit": "30-99999999-9", "razon_social": "OTRA SA"},
        ]
    )
    df.to_excel(excel_path, index=False)

    result, status = diagnose_supplier_duplicates(excel_path=excel_path, tenant_id="tenant-1")

    assert status == "PASS"
    assert result.evidence.tenant_id == "tenant-1"


def test_supplier_duplicate_check_blocked_without_proveedor(tmp_path: Path) -> None:
    excel_path = tmp_path / "proveedores.xlsx"
    df = pd.DataFrame([{"cuit": "30-12345678-9", "razon_social": "SERVICIOS SRL"}])
    df.to_excel(excel_path, index=False)

    result, status = diagnose_supplier_duplicates(excel_path=excel_path, tenant_id="tenant-1")

    assert status == "BLOCKED"
    assert any(f.code == "MISSING_PROVEEDOR_COLUMN" for f in result.findings)


def test_supplier_duplicate_check_detects_required_findings(tmp_path: Path) -> None:
    excel_path = tmp_path / "proveedores.xlsx"
    df = pd.DataFrame(
        [
            {"proveedor": "Uno", "cuit": "30-12345678-9", "razon_social": "SERVICIOS  SRL"},
            {"proveedor": "Dos", "cuit": "30-12345678-9", "razon_social": "SERVICIOS S.R.L."},
            {"proveedor": "Tres", "cuit": None, "razon_social": None},
        ]
    )
    df.to_excel(excel_path, index=False)

    result, status = diagnose_supplier_duplicates(excel_path=excel_path, tenant_id="tenant-1")

    assert status == "PASS"
    codes = {f.code for f in result.findings}
    assert "DUPLICATE_CUIT" in codes
    assert "MISSING_CUIT" in codes
    assert "MISSING_RAZON_SOCIAL" in codes
    assert "NORMALIZATION_NEEDED" in codes
    assert "LEGAL_SUFFIX_VARIATION" in codes


def test_supplier_duplicate_check_partial_if_only_proveedor(tmp_path: Path) -> None:
    excel_path = tmp_path / "proveedores.xlsx"
    df = pd.DataFrame([{"proveedor": "Solo proveedor"}])
    df.to_excel(excel_path, index=False)

    _result, status = diagnose_supplier_duplicates(excel_path=excel_path, tenant_id="tenant-1")

    assert status == "PARTIAL"
