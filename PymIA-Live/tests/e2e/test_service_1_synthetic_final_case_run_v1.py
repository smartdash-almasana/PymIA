from __future__ import annotations

import json
from pathlib import Path

import pytest


OWNER_FORBIDDEN_TERMS = [
    "traceback",
    "runtime_authorized",
    "schema_version",
    "taskspec_patch",
    "file_intake",
    "qa_delivery_gate",
    "first_aid_eligibility_gate",
    "operator_packet",
    "llm",
    "fsm",
    "openai",
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
    "recomendamos ejecutar",
    "debe hacer",
]


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


def _load_single_case_dir(tmp_path: Path) -> Path:
    case_root = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [path for path in case_root.iterdir() if path.is_dir()]
    assert len(case_folders) == 1
    return case_folders[0]


def _assert_no_terms(text: str, terms: list[str]) -> None:
    lowered = text.lower()
    for term in terms:
        assert term not in lowered, f"Unexpected term found in owner-facing text: {term}"


def test_service_1_synthetic_final_case_run_v1_owner_package_quality(
    tmp_path, monkeypatch, capsys
) -> None:
    """Synthetic final case run: validate readable artifacts and conservative claims."""
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

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "First Aid mínimo" in stdout
    assert "DRAFT_REVIEW_REQUIRED" in stdout
    assert "Runtime autorizado: false" in stdout
    assert "Traceback" not in stdout

    case_dir = _load_single_case_dir(tmp_path)

    owner_message = (case_dir / "owner_message.md").read_text(encoding="utf-8")
    owner_summary = (case_dir / "first_aid_owner_summary.md").read_text(encoding="utf-8")
    readme = (case_dir / "README.txt").read_text(encoding="utf-8")

    assert len(owner_message.strip()) >= 80
    assert len(owner_summary.strip()) >= 120
    assert "First Aid" in owner_summary
    assert "revision humana" in owner_summary.lower() or "revisión humana" in owner_summary.lower()

    _assert_no_terms(owner_message, OWNER_FORBIDDEN_TERMS)
    _assert_no_terms(owner_summary, OWNER_FORBIDDEN_TERMS)
    _assert_no_terms(owner_message, STRONG_CLAIM_TERMS)
    _assert_no_terms(owner_summary, STRONG_CLAIM_TERMS)

    readme_lower = readme.lower()
    assert "no contiene diagnostico" in readme_lower
    assert "revision humana" in readme_lower
    assert "first aid minimo" in readme_lower

    packet = json.loads((case_dir / "operator_packet.json").read_text(encoding="utf-8"))
    first_aid_result = json.loads(
        (case_dir / "first_aid_result.json").read_text(encoding="utf-8")
    )
    eligibility_gate = json.loads(
        (case_dir / "first_aid_eligibility_gate.json").read_text(encoding="utf-8")
    )

    assert packet["runtime_authorized"] is False
    assert packet["qa_delivery_gate"]["status"] == "PASS"
    assert eligibility_gate["status"] == "ELIGIBLE"
    assert eligibility_gate["human_review_required"] is True
    assert first_aid_result["status"] == "DRAFT_REVIEW_REQUIRED"
    assert first_aid_result["human_review_required"] is True
    assert first_aid_result["summary"]["sheets_profiled"] >= 1
    assert first_aid_result["summary"]["total_findings"] >= 1

    serialized_result = json.dumps(first_aid_result, ensure_ascii=False).lower()
    for forbidden in ["diagnosis", "accounting_result", "tax_result", "certification"]:
        assert forbidden not in serialized_result
