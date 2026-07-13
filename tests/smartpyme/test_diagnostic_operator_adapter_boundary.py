from pathlib import Path


def test_diagnostic_operator_adapter_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    diagnostic_operator_adapter_source = (repo_root / "pymia" / "smartpyme" / "diagnostic_operator_adapter.py").read_text(encoding="utf-8")
    vertical_slice_source = (repo_root / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")

    assert "from pymia.cli.vertical_slice" not in diagnostic_operator_adapter_source
    assert "import argparse" not in diagnostic_operator_adapter_source
    assert "def _serializable_diagnostic_pipeline_result(" not in vertical_slice_source
    assert "def _diagnostic_pipeline_result_for_report(" not in vertical_slice_source
    assert "def _diagnostic_operator_summary_from_report(" not in vertical_slice_source
