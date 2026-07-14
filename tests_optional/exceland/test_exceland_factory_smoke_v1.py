from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

factory_module = pytest.importorskip(
    "exceland_factory.factory",
    reason="Install a governed exceland-factory build to run this optional integration smoke.",
)
build_product = factory_module.build_product


def test_external_exceland_factory_generates_xlsx(tmp_path: Path) -> None:
    output_path = tmp_path / "smoke_precio_margen.xlsx"
    build_product("precio_margen", output_path=output_path)
    assert output_path.exists() and output_path.stat().st_size > 0
    assert openpyxl.load_workbook(output_path).sheetnames
