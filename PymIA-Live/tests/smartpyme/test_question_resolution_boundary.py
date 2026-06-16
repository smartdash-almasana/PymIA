from pathlib import Path


def test_question_resolution_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    question_resolution_source = (repo_root / "pymia" / "smartpyme" / "question_resolution.py").read_text(encoding="utf-8")
    vertical_slice_source = (repo_root / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")

    assert "from pymia.cli.vertical_slice" not in question_resolution_source
    assert "import argparse" not in question_resolution_source
    assert "def _build_owner_question(" not in vertical_slice_source
    assert "def _requested_evidence_from_report(" not in vertical_slice_source
    assert "def _resolve_owner_question_and_reference(" not in vertical_slice_source
