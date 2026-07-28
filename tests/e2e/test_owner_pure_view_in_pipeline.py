from pathlib import Path

from openpyxl import Workbook

from pymia.application import vertical_pipeline
from pymia.cli import vertical_slice


def _write_excel(path: Path, rows: list[list[object]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


def test_build_pipeline_exposes_owner_pure_view_without_rendering_it(tmp_path: Path) -> None:
    excel = tmp_path / "caso_owner_pure.xlsx"
    storage_dir = tmp_path / "storage"
    _write_excel(
        excel,
        [
            ["fecha", "producto", "ventas", "costo"],
            ["2026-06-01", "A", 100, 60],
        ],
    )

    profile = vertical_slice.inspect_excel(excel)
    report = vertical_slice.build_report(
        excel,
        "vendo mas pero no me queda plata",
        profile,
        storage_dir=storage_dir,
    )
    pipeline = vertical_pipeline.build_pipeline(
        excel,
        "vendo mas pero no me queda plata",
        storage_dir=storage_dir,
    )

    owner_pure_view = pipeline["owner_pure_view"]

    assert owner_pure_view["schema_version"] == "OWNER_PURE_VIEW_V1"
    assert owner_pure_view["status"] == "DELIVERED_CANDIDATE"
    assert owner_pure_view["owner_summary"] == report["summary"]
    if report["next_questions"]:
        assert owner_pure_view["next_question"] == report["next_questions"][0]
    else:
        assert owner_pure_view["next_question"]
    assert "owner_simple" in pipeline["report"]
    assert all("Slice local" not in limit for limit in owner_pure_view["limits"])
    assert "owner_pure_view" not in pipeline["markdown"]
    assert "OWNER_PURE_VIEW_V1" not in pipeline["markdown"]
