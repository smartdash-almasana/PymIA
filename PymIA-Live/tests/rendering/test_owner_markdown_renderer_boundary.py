from pathlib import Path


def test_owner_markdown_renderer_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    owner_markdown_renderer_source = (repo_root / "pymia" / "rendering" / "owner_markdown_renderer.py").read_text(encoding="utf-8")
    vertical_slice_source = (repo_root / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")

    assert "from pymia.cli.vertical_slice" not in owner_markdown_renderer_source
    assert "import argparse" not in owner_markdown_renderer_source
    assert "def render_markdown_from_report(" not in vertical_slice_source
    assert "def _humanize_field(" not in vertical_slice_source
    assert "def _owner_label_for_variable(" not in vertical_slice_source
    assert "from pymia.rendering.owner_markdown_renderer import render_markdown_from_report" in vertical_slice_source
