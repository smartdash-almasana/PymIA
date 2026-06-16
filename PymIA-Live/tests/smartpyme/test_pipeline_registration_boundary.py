from pathlib import Path


def test_pipeline_registration_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    pipeline_registration_source = (repo_root / "pymia" / "smartpyme" / "pipeline_registration.py").read_text(encoding="utf-8")
    vertical_slice_source = (repo_root / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")

    assert "from pymia.cli.vertical_slice" not in pipeline_registration_source
    assert "import argparse" not in pipeline_registration_source
    assert "def register_anamnesis_record(" not in vertical_slice_source
    assert "def register_pipeline_run_record(" not in vertical_slice_source
