from pathlib import Path


def test_vertical_pipeline_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    vertical_pipeline_source = (repo_root / "pymia" / "application" / "vertical_pipeline.py").read_text(encoding="utf-8")
    vertical_slice_source = (repo_root / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")

    # vertical_pipeline.py decoupling assertions
    assert "pymia.cli.vertical_slice" not in vertical_pipeline_source
    assert "import argparse" not in vertical_pipeline_source

    # vertical_slice.py adapter assertions
    assert "import argparse" in vertical_slice_source
    assert "from pymia.application.vertical_pipeline import" in vertical_slice_source

    # Ensure vertical_slice.py no longer defines the moved functions
    assert "def inspect_excel(" not in vertical_slice_source
    assert "def has_operational_columns(" not in vertical_slice_source
    assert "def build_structured_summary(" not in vertical_slice_source
    assert "def build_report(" not in vertical_slice_source
    assert "def build_markdown(" not in vertical_slice_source
    assert "def build_pipeline(" not in vertical_slice_source

    # Ensure vertical_slice.py still has main
    assert "def main(" in vertical_slice_source
