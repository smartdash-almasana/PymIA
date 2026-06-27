from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


REAL_ANON_XLSX_ENV = "PYMIA_SERVICE_1_REAL_ANON_XLSX"
REAL_ANON_CONFIRMED_COLUMNS_ENV = "PYMIA_SERVICE_1_REAL_ANON_CONFIRMED_COLUMNS"

EXPECTED_CASE_FILES = {
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

OWNER_FORBIDDEN_TERMS = [
    "traceback",
    "runtime_authorized",
    "schema_version",
    "taskspec_patch",
    "file_intake",
    "qa_delivery_gate",
    "first_aid_eligibility_gate",
    "operator_packet",
    "openai",
    "llm",
    "fsm",
]

STRONG_CLAIM_TERMS = [
    "diagnóstico final",
    "diagnostico final",
    "certifico",
    "certificación",
    "certificacion",
    "auditoría contable",
    "auditoria contable",
    "conciliación definitiva",
    "conciliacion definitiva",
    "liquidación fiscal",
    "liquidacion fiscal",
]


def _real_anonymized_xlsx_path() -> Path:
    raw_path = os.environ.get(REAL_ANON_XLSX_ENV)
    if not raw_path:
        pytest.skip(
            f"Set {REAL_ANON_XLSX_ENV} to run the anonymized real-case Service 1 smoke."
        )
    path = Path(raw_path)
    if not path.exists():
        pytest.skip(f"Configured anonymized XLSX does not exist: {path}")
    if path.suffix.lower() != ".xlsx":
        pytest.skip(f"Configured anonymized file is not .xlsx: {path}")
    return path


def _confirmed_columns_path(tmp_path: Path) -> Path:
    raw_path = os.environ.get(REAL_ANON_CONFIRMED_COLUMNS_ENV)
    if raw_path:
        path = Path(raw_path)
        if not path.exists():
            pytest.skip(f"Configured confirmed-columns JSON does not exist: {path}")
        return path

    confirmed_columns = {
        "confirmed_columns": {
            "Producto": {"role": "product"},
            "Cantidad": {"role": "quantity"},
            "Precio": {"role": "price"},
            "Total": {"role": "amount"},
            "Importe": {"role": "amount"},
            "Fecha": {"role": "date"},
            "Cliente": {"role": "party"},
        }
    }
    path = tmp_path / "confirmed_columns_real_anon_sample.json"
    path.write_text(
        json.dumps(confirmed_columns, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _assert_no_terms(text: str, terms: list[str]) -> None:
    lowered = text.lower()
    for term in terms:
        assert term not in lowered, f"Unexpected term found in owner-facing text: {term}"


def _assert_no_runtime_authorized_true(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "runtime_authorized":
                assert nested is not True
            _assert_no_runtime_authorized_true(nested)
    elif isinstance(value, list):
        for item in value:
            _assert_no_runtime_authorized_true(item)


def test_service_1_anonymized_real_case_run_v1_opt_in(
    tmp_path, monkeypatch, capsys
) -> None:
    """Opt-in smoke for a real anonymized XLSX outside the repository."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _real_anonymized_xlsx_path()
    confirmed_columns_path = _confirmed_columns_path(tmp_path)

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

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "First Aid mínimo" in stdout
    assert "Runtime autorizado: false" in stdout
    assert "Traceback" not in stdout

    case_root = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [path for path in case_root.iterdir() if path.is_dir()]
    assert len(case_folders) == 1
    case_dir = case_folders[0]

    actual_files = {path.name for path in case_dir.iterdir() if path.is_file()}
    assert EXPECTED_CASE_FILES.issubset(actual_files)

    owner_message = (case_dir / "owner_message.md").read_text(encoding="utf-8")
    owner_summary = (case_dir / "first_aid_owner_summary.md").read_text(encoding="utf-8")
    readme = (case_dir / "README.txt").read_text(encoding="utf-8").lower()

    assert len(owner_message.strip()) >= 80
    assert len(owner_summary.strip()) >= 120
    assert "revisión humana" in owner_summary.lower() or "revision humana" in owner_summary.lower()
    assert "no contiene diagnostico" in readme
    assert "revision humana" in readme

    _assert_no_terms(owner_message, OWNER_FORBIDDEN_TERMS)
    _assert_no_terms(owner_summary, OWNER_FORBIDDEN_TERMS)
    _assert_no_terms(owner_message, STRONG_CLAIM_TERMS)
    _assert_no_terms(owner_summary, STRONG_CLAIM_TERMS)

    packet = json.loads((case_dir / "operator_packet.json").read_text(encoding="utf-8"))
    first_aid_result = json.loads(
        (case_dir / "first_aid_result.json").read_text(encoding="utf-8")
    )

    assert packet["runtime_authorized"] is False
    assert packet["qa_delivery_gate"]["status"] == "PASS"
    assert packet["first_aid_eligibility_gate"]["status"] in {"ELIGIBLE", "BLOCKED"}
    assert first_aid_result["status"] == "DRAFT_REVIEW_REQUIRED"
    assert first_aid_result["human_review_required"] is True
    _assert_no_runtime_authorized_true(packet)
