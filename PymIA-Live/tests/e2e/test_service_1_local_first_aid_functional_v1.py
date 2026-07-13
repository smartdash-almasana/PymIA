from __future__ import annotations

import json
from pathlib import Path

import pytest


def _find_xlsx_fixture() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        repo_root / "prueba_excels" / "cafeteria_abc.xlsx",
        repo_root / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip("No XLSX fixture found in prueba_excels/")


def _write_confirmed_columns(tmp_path: Path) -> Path:
    confirmed_columns = {
        "confirmed_columns": {
            "Producto": {"role": "product"},
            "Cantidad": {"role": "quantity"},
            "Precio": {"role": "price"},
            "Total": {"role": "amount"},
        }
    }
    path = tmp_path / "confirmed_columns_sample.json"
    path.write_text(
        json.dumps(confirmed_columns, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _assert_no_runtime_authorized_true(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "runtime_authorized":
                assert nested is not True
            _assert_no_runtime_authorized_true(nested)
    elif isinstance(value, list):
        for item in value:
            _assert_no_runtime_authorized_true(item)


def test_service_1_local_first_aid_functional_v1_pass(
    tmp_path, monkeypatch, capsys
) -> None:
    """End-to-end contract for SERVICE_1_LOCAL_FIRST_AID_FUNCTIONAL_V1."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    confirmed_columns_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main(
        [
            "--file",
            str(xlsx_path),
            "--confirmed-columns",
            str(confirmed_columns_path),
            "--run-first-aid",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "First Aid mínimo" in captured.out
    assert "DRAFT_REVIEW_REQUIRED" in captured.out
    assert "Revisión humana requerida: true" in captured.out
    assert "Runtime autorizado: false" in captured.out
    assert "Carpeta de caso" in captured.out
    assert "Traceback" not in captured.out

    case_root = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [path for path in case_root.iterdir() if path.is_dir()]
    assert len(case_folders) == 1
    case_dir = case_folders[0]

    expected_files = {
        "owner_message.md",
        "operator_packet.json",
        "detected_structure.json",
        "column_confirmation_packet.json",
        "confirmed_columns.json",
        "first_aid_eligibility_gate.json",
        "first_aid_result.json",
        "first_aid_owner_summary.md",
        "README.txt",
    }
    actual_files = {path.name for path in case_dir.iterdir() if path.is_file()}
    assert expected_files.issubset(actual_files)

    packet = json.loads(
        (case_dir / "operator_packet.json").read_text(encoding="utf-8")
    )
    assert packet["service_name"] == "SERVICE_1"
    assert packet["runtime_authorized"] is False
    assert packet["qa_delivery_gate"]["status"] == "PASS"
    assert packet["first_aid_eligibility_gate"]["status"] == "ELIGIBLE"
    assert packet["first_aid_result"]["status"] == "DRAFT_REVIEW_REQUIRED"
    assert packet["first_aid_result"]["human_review_required"] is True
    _assert_no_runtime_authorized_true(packet)

    manifest_files = set(packet["case_delivery_manifest"]["files_written"])
    assert expected_files.issubset(manifest_files)

    readme = (case_dir / "README.txt").read_text(encoding="utf-8").lower()
    assert "no contiene diagnostico" in readme
    assert "confirmacion del dueno" in readme
