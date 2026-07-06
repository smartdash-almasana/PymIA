from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


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


def _write_question_bundle(tmp_path: Path) -> tuple[Path, str]:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_cli_reentry",
        tenant_id="tenant_cli",
        intake_id="intake_cli",
        run_id="run_cli",
        report={
            "next_questions": [
                {"text": "Que periodo queres revisar?", "target_ref": "missing:period"},
                {"text": "Que archivo representa ventas?", "target_ref": "missing:sales_file"},
            ]
        },
    )
    path = tmp_path / "question_bundle.json"
    path.write_text(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path, bundle.questions[0].question_ref


def test_cli_wires_owner_evidence_reentry_into_case_folder(tmp_path, monkeypatch, capsys) -> None:
    xlsx_path = _find_xlsx_fixture()
    bundle_path, question_ref = _write_question_bundle(tmp_path)
    reentry_storage_dir = tmp_path / "owner_reentry_store"
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--question-bundle", str(bundle_path),
        "--question-ref", question_ref,
        "--owner-answer", "Marzo 2026.",
        "--owner-reentry-storage-dir", str(reentry_storage_dir),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Owner evidence reentry" in captured.out
    assert "ACCEPTED_AND_PROJECTED" in captured.out
    assert "Runtime autorizado: false" in captured.out

    case_root = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [path for path in case_root.iterdir() if path.is_dir()]
    assert len(case_folders) == 1
    case_dir = case_folders[0]

    reentry_artifact = case_dir / "owner_reentry_bridge.json"
    assert reentry_artifact.exists()
    reentry_data = json.loads(reentry_artifact.read_text(encoding="utf-8"))
    assert reentry_data["status"] == "ACCEPTED_AND_PROJECTED"
    assert reentry_data["question_ref"] == question_ref
    assert reentry_data["runtime_authorized"] is False
    assert reentry_data["reexecution_authorized"] is False
    assert reentry_data["recalculation_authorized"] is False
    assert reentry_data["delivery_authorized"] is False

    operator_packet = json.loads((case_dir / "operator_packet.json").read_text(encoding="utf-8"))
    assert operator_packet["owner_reentry_bridge"]["status"] == "ACCEPTED_AND_PROJECTED"

    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    filenames = {record["filename"] for record in manifest["files"]}
    assert "owner_reentry_bridge.json" in filenames


def test_cli_reentry_requires_complete_argument_set(tmp_path, monkeypatch, capsys) -> None:
    xlsx_path = _find_xlsx_fixture()
    bundle_path, _question_ref = _write_question_bundle(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--question-bundle", str(bundle_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "reentry requires" in captured.out


def test_cli_reentry_rejects_invalid_question_bundle_json(tmp_path, monkeypatch, capsys) -> None:
    xlsx_path = _find_xlsx_fixture()
    bad_bundle = tmp_path / "bad_question_bundle.json"
    bad_bundle.write_text("no es json", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--question-bundle", str(bad_bundle),
        "--question-ref", "service_1:missing:period",
        "--owner-answer", "Marzo 2026.",
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "invalid question bundle JSON" in captured.out
