from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from pymia.smartpyme.exceland_runtime_v1 import (
    run_exceland_runtime_v1,
)


def test_success_path_generates_xlsx_with_sheets(tmp_path: Path) -> None:
    result = run_exceland_runtime_v1(
        product_ref="precio_margen",
        output_dir=tmp_path,
    )

    assert result["status"] == "OK"
    assert result["product_ref"] == "precio_margen"
    assert result["artifact_exists"] is True
    assert result["runtime_authorized"] is False
    assert result["error_message"] is None

    output_path = Path(result["output_path"])
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    import openpyxl

    wb = openpyxl.load_workbook(output_path)
    assert len(wb.sheetnames) >= 1


def test_success_path_custom_filename(tmp_path: Path) -> None:
    result = run_exceland_runtime_v1(
        product_ref="caja_diaria",
        output_dir=tmp_path,
        output_filename="mi_caja.xlsx",
    )

    assert result["status"] == "OK"
    output_path = Path(result["output_path"])
    assert output_path.name == "mi_caja.xlsx"
    assert output_path.exists()


def test_missing_product_ref(tmp_path: Path) -> None:
    result = run_exceland_runtime_v1(
        product_ref=None,
        output_dir=tmp_path,
    )

    assert result["status"] == "MISSING_PRODUCT_REF"
    assert result["product_ref"] is None
    assert result["output_path"] is None
    assert result["artifact_exists"] is False
    assert result["runtime_authorized"] is False
    assert "required" in result["error_message"].lower()


def test_empty_product_ref(tmp_path: Path) -> None:
    result = run_exceland_runtime_v1(
        product_ref="",
        output_dir=tmp_path,
    )

    assert result["status"] == "MISSING_PRODUCT_REF"


def test_unknown_product_ref(tmp_path: Path) -> None:
    result = run_exceland_runtime_v1(
        product_ref="producto_inexistente",
        output_dir=tmp_path,
    )

    assert result["status"] == "UNKNOWN_PRODUCT"
    assert result["artifact_exists"] is False
    assert "allowlist" in result["error_message"]
    assert result["product_ref"] == "producto_inexistente"


def test_invalid_output_dir(tmp_path: Path) -> None:
    nonexistent = tmp_path / "no_existe"

    result = run_exceland_runtime_v1(
        product_ref="caja_diaria",
        output_dir=nonexistent,
    )

    assert result["status"] == "INVALID_OUTPUT_DIR"
    assert result["artifact_exists"] is False
    assert "does not exist" in result["error_message"]


def test_runtime_authorized_always_false(tmp_path: Path) -> None:
    for product_ref in ("precio_margen", "caja_diaria"):
        result = run_exceland_runtime_v1(
            product_ref=product_ref,
            output_dir=tmp_path,
        )
        assert result["runtime_authorized"] is False, (
            f"runtime_authorized must be False for product_ref={product_ref}"
        )


def test_module_has_no_forbidden_imports() -> None:
    import pymia.smartpyme.exceland_runtime_v1 as module

    source = inspect.getsource(module)

    assert "service_1_pipeline" not in source
    assert "diagnostic_core" not in source
    assert "cli" not in source
    assert "fsm" not in source.lower()
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()


def test_allowed_product_refs_are_callable(tmp_path: Path) -> None:
    from pymia.smartpyme.exceland_runtime_v1 import _EXCELAND_PRODUCT_REFS

    for product_ref in _EXCELAND_PRODUCT_REFS:
        result = run_exceland_runtime_v1(
            product_ref=product_ref,
            output_dir=tmp_path,
        )
        assert result["status"] == "OK", (
            f"Expected OK for product_ref={product_ref}, got {result['status']}: {result.get('error_message')}"
        )
        assert result["artifact_exists"] is True
        assert Path(result["output_path"]).exists()
