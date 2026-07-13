from pathlib import Path


def test_owner_output_does_not_import_cli_or_argparse():
    source = Path("pymia/smartpyme/owner_output.py").read_text(encoding="utf-8")

    assert "pymia.cli.vertical_slice" not in source
    assert "from pymia.cli" not in source
    assert "import argparse" not in source
