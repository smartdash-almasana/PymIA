from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


# Path to the CLI module
CLI_MODULE = "pymia.cli.service_1_operator"


def _find_xlsx_fixture() -> Path:
    """Find a real XLSX fixture in the repo for testing."""
    # Use absolute path from repo root (PymIA-Live is a subdirectory of the repo)
    repo_root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        repo_root / "prueba_excels" / "cafeteria_abc.xlsx",
        repo_root / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip("No XLSX fixture found in prueba_excels/")


# ---------------------------------------------------------------------------
# 1. XLSX fixture existente produce stdout con "Respuesta inicial de Servicio 1"
# ---------------------------------------------------------------------------

def test_xlsx_fixture_produces_owner_message(capsys, tmp_path, monkeypatch) -> None:
    """XLSX fixture exists → stdout contains expected owner message."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path), "--source-channel", "cli"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Respuesta inicial de Servicio 1" in captured.out
    assert "Próximo paso" in captured.out


# ---------------------------------------------------------------------------
# 2. Archivo inexistente devuelve exit code 2
# ---------------------------------------------------------------------------

def test_nonexistent_file_returns_exit_code_2(tmp_path, monkeypatch, capsys) -> None:
    """Non-existent file → exit code 2, error message on stdout."""
    monkeypatch.chdir(tmp_path)
    fake_path = tmp_path / "no_existe.xlsx"

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(fake_path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not found" in captured.out.lower() or "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# 3. stdout no contiene traceback ni claves técnicas prohibidas
# ---------------------------------------------------------------------------

_FORBIDDEN_STDOUT_TERMS = [
    "traceback",
    "exception",
    "runtime_authorized",
    "pipeline_run",
    "evidence_id",
    "document_ingestion",
    "reentry",
    "fsm",
    "llm",
    "taskspec_patch",
    "file_intake_id",
    "schema_version",
]


def test_stdout_is_clean_no_traceback_no_forbidden_keys(capsys, tmp_path, monkeypatch) -> None:
    """stdout must be owner-friendly: no tracebacks, no internal keys."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    stdout_lower = captured.out.lower()

    for term in _FORBIDDEN_STDOUT_TERMS:
        assert term not in stdout_lower, f"stdout must not contain forbidden term: {term}"


# ---------------------------------------------------------------------------
# 4. Packet JSON queda escrito en .tmp/service_1_operator/<asset_id>.json
# ---------------------------------------------------------------------------

def test_packet_json_is_written(tmp_path, monkeypatch) -> None:
    """After a successful run, a JSON packet file must exist."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    # Find the output JSON file
    output_dir = tmp_path / ".tmp" / "service_1_operator"
    assert output_dir.exists(), f"Output directory {output_dir} was not created"

    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1, f"Expected exactly 1 JSON file, found {len(json_files)}"

    # Validate JSON is parseable
    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["service_name"] == "SERVICE_1"
    assert packet["schema_version"] == "1.0"
    assert "owner_message" in packet
    assert len(packet["owner_message"]) > 0


# ---------------------------------------------------------------------------
# 5. Packet mantiene runtime_authorized = false
# ---------------------------------------------------------------------------

def test_packet_runtime_authorized_is_false(tmp_path, monkeypatch) -> None:
    """JSON packet must have runtime_authorized = False."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    # Top-level runtime_authorized
    assert packet["runtime_authorized"] is False

    # Nested invariants
    assert packet["taskspec_patch"]["runtime_authorized"] is False
    assert packet["owner_response"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 6. No importa módulos prohibidos (pipeline, FSM, reentry, LLM, etc.)
# ---------------------------------------------------------------------------

_FORBIDDEN_MODULES = [
    "pymia.smartpyme.vertical_pipeline",
    "pymia.smartpyme.service_1_boundary_chain_v1",
    "pymia.smartpyme.service_1_fsm_decision_patch_v1",
    "pymia.smartpyme.service_1_pipeline_v1",
    "pymia.smartpyme.service_1_owner_answer_reentry_v1",
    "pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1",
    "pymia.smartpyme.service_1_case_reentry_read_model_v1",
    "pymia.application.vertical_pipeline",
    "tools.document_ingestion",
    "openai",
    "chatbot",
]


def test_cli_does_not_import_forbidden_modules(tmp_path, monkeypatch) -> None:
    """After running the CLI, forbidden modules must not be in sys.modules."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    # Clear cached forbidden modules
    for mod in _FORBIDDEN_MODULES:
        sys.modules.pop(mod, None)

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    for mod in _FORBIDDEN_MODULES:
        assert mod not in sys.modules, f"CLI must not import {mod}"


# ---------------------------------------------------------------------------
# 7. XLSX genera packet JSON con key detected_structure
# ---------------------------------------------------------------------------

def test_xlsx_generates_detected_structure_in_packet(tmp_path, monkeypatch) -> None:
    """XLSX file → packet JSON must contain detected_structure key with structure data."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "detected_structure" in packet
    assert packet["detected_structure"] is not None
    assert packet["detected_structure"]["service_name"] == "SERVICE_1"
    assert "workbook" in packet["detected_structure"]


# ---------------------------------------------------------------------------
# 8. detected_structure.runtime_authorized es false
# ---------------------------------------------------------------------------

def test_detected_structure_runtime_authorized_is_false(tmp_path, monkeypatch) -> None:
    """The detected_structure block must have runtime_authorized = False."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["detected_structure"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 9. packet runtime_authorized principal sigue false
# ---------------------------------------------------------------------------

def test_packet_runtime_authorized_remains_false_with_structure(tmp_path, monkeypatch) -> None:
    """Top-level runtime_authorized must remain False even when structure is added."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["runtime_authorized"] is False
    assert packet["detected_structure"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 10. stdout incluye "Estructura detectada" y "Hojas detectadas"
# ---------------------------------------------------------------------------

def test_stdout_includes_structure_block(capsys, tmp_path, monkeypatch) -> None:
    """stdout must contain the structure block with Spanish labels."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    assert "Estructura detectada" in captured.out
    assert "Hojas detectadas" in captured.out


# ---------------------------------------------------------------------------
# 11. Archivo no XLSX no agrega detected_structure y no rompe
# ---------------------------------------------------------------------------

def test_non_xlsx_file_no_detected_structure(tmp_path, monkeypatch) -> None:
    """Non-XLSX file → packet must NOT have detected_structure, and CLI must not crash."""
    monkeypatch.chdir(tmp_path)

    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4", encoding="utf-8")

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(csv_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "detected_structure" not in packet


# ---------------------------------------------------------------------------
# 12. Error del reader no produce traceback y agrega warning
# ---------------------------------------------------------------------------

def test_reader_error_no_traceback_adds_warning(capsys, tmp_path, monkeypatch) -> None:
    """When the reader raises, stdout must show warning without stack trace."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    import pymia.cli.service_1_operator as cli_mod

    def _failing_reader(_path: str):
        raise OSError("simulated read failure")

    monkeypatch.setattr(
        cli_mod,
        "read_service_1_xlsx_structure_v1",
        _failing_reader,
    )

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No se pudo leer" in captured.out
    assert "Traceback" not in captured.out

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "detected_structure" in packet
    assert packet["detected_structure"]["error"] is True
    assert "warning" in packet["detected_structure"]


# ---------------------------------------------------------------------------
# 13. XLSX agrega column_confirmation_packet al JSON
# ---------------------------------------------------------------------------

def test_xlsx_generates_column_confirmation_packet(tmp_path, monkeypatch) -> None:
    """XLSX file → packet JSON must contain column_confirmation_packet."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "column_confirmation_packet" in packet
    assert packet["column_confirmation_packet"] is not None
    assert packet["column_confirmation_packet"]["packet_type"] == "COLUMN_CONFIRMATION"
    assert len(packet["column_confirmation_packet"]["questions"]) > 0


# ---------------------------------------------------------------------------
# 14. stdout incluye "Confirmación necesaria"
# ---------------------------------------------------------------------------

def test_stdout_includes_column_confirmation_block(capsys, tmp_path, monkeypatch) -> None:
    """stdout must contain the column confirmation block."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    assert "Confirmaci\u00f3n necesaria" in captured.out
    assert "Preguntas generadas" in captured.out
    assert "Primera pregunta" in captured.out


# ---------------------------------------------------------------------------
# 15. column_confirmation_packet.runtime_authorized sigue false
# ---------------------------------------------------------------------------

def test_column_confirmation_packet_runtime_authorized_is_false(tmp_path, monkeypatch) -> None:
    """Column confirmation packet must have runtime_authorized = False."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["runtime_authorized"] is False
    assert packet["column_confirmation_packet"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 16. Non-XLSX no agrega column_confirmation_packet
# ---------------------------------------------------------------------------

def test_non_xlsx_file_no_column_confirmation_packet(tmp_path, monkeypatch) -> None:
    """Non-XLSX file → packet must NOT have column_confirmation_packet."""
    monkeypatch.chdir(tmp_path)

    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4", encoding="utf-8")

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(csv_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "column_confirmation_packet" not in packet
    assert "detected_structure" not in packet


# ---------------------------------------------------------------------------
# 17. stdout con XLSX no contiene traceback
# ---------------------------------------------------------------------------

def test_xlsx_stdout_no_traceback(capsys, tmp_path, monkeypatch) -> None:
    """Successful XLSX run must not print traceback to stdout."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Traceback" not in captured.out
    assert "traceback" not in captured.out.lower()


# ---------------------------------------------------------------------------
# 18. CLI con XLSX crea case_delivery_manifest en packet
# ---------------------------------------------------------------------------

def test_xlsx_creates_case_delivery_manifest_in_packet(tmp_path, monkeypatch) -> None:
    """XLSX file → packet JSON must contain case_delivery_manifest."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "case_delivery_manifest" in packet
    assert packet["case_delivery_manifest"]["service_name"] == "SERVICE_1"
    assert "case_id" in packet["case_delivery_manifest"]


# ---------------------------------------------------------------------------
# 19. Crea carpeta .tmp/service_1_cases/<case_id>
# ---------------------------------------------------------------------------

def test_creates_case_folder_under_service_1_cases(tmp_path, monkeypatch) -> None:
    """Case folder must exist under .tmp/service_1_cases/<case_id>."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    assert case_dir.exists()

    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1


# ---------------------------------------------------------------------------
# 20. Stdout incluye "Carpeta de caso"
# ---------------------------------------------------------------------------

def test_stdout_includes_case_folder_block(capsys, tmp_path, monkeypatch) -> None:
    """stdout must contain the case folder summary block."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    assert "Carpeta de caso" in captured.out


# ---------------------------------------------------------------------------
# 21. operator_packet.json existe dentro de carpeta
# ---------------------------------------------------------------------------

def test_operator_packet_json_in_case_folder(tmp_path, monkeypatch) -> None:
    """Case folder must contain operator_packet.json with complete data."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    op_packet = case_folders[0] / "operator_packet.json"
    assert op_packet.exists()

    with open(op_packet, encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["service_name"] == "SERVICE_1"
    assert "case_delivery_manifest" in packet


# ---------------------------------------------------------------------------
# 22. detected_structure.json existe para XLSX
# ---------------------------------------------------------------------------

def test_detected_structure_json_in_case_folder(tmp_path, monkeypatch) -> None:
    """Case folder must contain detected_structure.json for XLSX files."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    ds_file = case_folders[0] / "detected_structure.json"
    assert ds_file.exists()

    data = json.loads(ds_file.read_text(encoding="utf-8"))
    assert data["service_name"] == "SERVICE_1"


# ---------------------------------------------------------------------------
# 23. column_confirmation_packet.json existe para XLSX
# ---------------------------------------------------------------------------

def test_column_confirmation_packet_json_in_case_folder(tmp_path, monkeypatch) -> None:
    """Case folder must contain column_confirmation_packet.json for XLSX files."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    cc_file = case_folders[0] / "column_confirmation_packet.json"
    assert cc_file.exists()

    data = json.loads(cc_file.read_text(encoding="utf-8"))
    assert data["packet_type"] == "COLUMN_CONFIRMATION"


# ---------------------------------------------------------------------------
# 24. Non-XLSX crea carpeta con archivos mínimos
# ---------------------------------------------------------------------------

def test_non_xlsx_creates_minimal_case_folder(tmp_path, monkeypatch) -> None:
    """Non-XLSX file must still create a case folder with minimum files."""
    monkeypatch.chdir(tmp_path)

    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4", encoding="utf-8")

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(csv_path)])
    assert exit_code == 0

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    assert (case_folders[0] / "owner_message.md").exists()
    assert (case_folders[0] / "operator_packet.json").exists()
    assert (case_folders[0] / "README.txt").exists()

    assert not (case_folders[0] / "detected_structure.json").exists()
    assert not (case_folders[0] / "column_confirmation_packet.json").exists()


# ---------------------------------------------------------------------------
# 25. runtime_authorized top-level sigue false con case delivery
# ---------------------------------------------------------------------------

def test_packet_runtime_authorized_false_with_case_delivery(tmp_path, monkeypatch) -> None:
    """Top-level runtime_authorized must be False after adding case delivery manifest."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["runtime_authorized"] is False
    assert packet["case_delivery_manifest"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 26. CLI con XLSX agrega qa_delivery_gate al packet
# ---------------------------------------------------------------------------


def test_xlsx_adds_qa_delivery_gate_to_packet(tmp_path, monkeypatch) -> None:
    """XLSX file → packet JSON must contain qa_delivery_gate."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(xlsx_path)])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "qa_delivery_gate" in packet
    assert packet["qa_delivery_gate"]["service_name"] == "SERVICE_1"
    assert packet["qa_delivery_gate"]["gate_type"] == "QA_DELIVERY_GATE"


# ---------------------------------------------------------------------------
# 27. qa_delivery_gate.status == PASS para caso completo
# ---------------------------------------------------------------------------


def test_qa_delivery_gate_status_is_pass_for_complete_case(tmp_path, monkeypatch) -> None:
    """Complete XLSX case → qa_delivery_gate.status must be PASS."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["qa_delivery_gate"]["status"] == "PASS"


# ---------------------------------------------------------------------------
# 28. qa_delivery_gate.runtime_authorized == false
# ---------------------------------------------------------------------------


def test_qa_delivery_gate_runtime_authorized_is_false(tmp_path, monkeypatch) -> None:
    """qa_delivery_gate must have runtime_authorized = False."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert packet["qa_delivery_gate"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 29. stdout incluye "QA delivery gate"
# ---------------------------------------------------------------------------


def test_stdout_includes_qa_delivery_gate_block(capsys, tmp_path, monkeypatch) -> None:
    """stdout must contain the QA delivery gate summary block."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    captured = capsys.readouterr()
    assert "QA delivery gate" in captured.out
    assert "Estado:" in captured.out
    assert "Checks:" in captured.out
    assert "Runtime autorizado: false" in captured.out


# ---------------------------------------------------------------------------
# 30. operator_packet.json final contiene qa_delivery_gate
# ---------------------------------------------------------------------------


def test_operator_packet_json_contains_qa_delivery_gate(tmp_path, monkeypatch) -> None:
    """operator_packet.json in case folder must contain qa_delivery_gate."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    op_packet = case_folders[0] / "operator_packet.json"
    assert op_packet.exists()

    with open(op_packet, encoding="utf-8") as f:
        packet = json.load(f)

    assert "qa_delivery_gate" in packet
    assert packet["qa_delivery_gate"]["status"] == "PASS"


# ---------------------------------------------------------------------------
# 31. Non-XLSX no rompe; gate puede PASS o BLOCKED sin traceback
# ---------------------------------------------------------------------------


def test_non_xlsx_qa_gate_does_not_crash(tmp_path, monkeypatch, capsys) -> None:
    """Non-XLSX file → qa_delivery_gate must not crash, no traceback."""
    monkeypatch.chdir(tmp_path)

    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4", encoding="utf-8")

    from pymia.cli.service_1_operator import main
    exit_code = main(["--file", str(csv_path)])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Traceback" not in captured.out
    assert "traceback" not in captured.out.lower()

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "qa_delivery_gate" in packet
    # For non-XLSX, gate may PASS (if minimal artifacts present) or BLOCKED
    assert packet["qa_delivery_gate"]["status"] in ("PASS", "BLOCKED")


# ---------------------------------------------------------------------------
# 32. No runtime_authorized true en ningún nivel
# ---------------------------------------------------------------------------


def test_no_runtime_authorized_true_at_any_level(tmp_path, monkeypatch) -> None:
    """Packet must not have runtime_authorized=True at any nesting level."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    def _check_no_true(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "runtime_authorized":
                    assert value is not True, f"Found runtime_authorized=True at key: {key}"
                _check_no_true(value)
        elif isinstance(obj, list):
            for item in obj:
                _check_no_true(item)

    _check_no_true(packet)


# ---------------------------------------------------------------------------
# 33. No imports prohibidos en CLI con QA gate
# ---------------------------------------------------------------------------


def test_cli_with_qa_gate_does_not_import_forbidden_modules(tmp_path, monkeypatch) -> None:
    """After running CLI with QA gate, forbidden modules must not be in sys.modules."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    forbidden = [
        "pymia.smartpyme.vertical_pipeline",
        "pymia.smartpyme.service_1_boundary_chain_v1",
        "pymia.smartpyme.service_1_fsm_decision_patch_v1",
        "pymia.smartpyme.service_1_pipeline_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1",
        "pymia.smartpyme.service_1_case_reentry_read_model_v1",
        "openai",
        "chatbot",
    ]

    for mod in forbidden:
        sys.modules.pop(mod, None)

    from pymia.cli.service_1_operator import main
    main(["--file", str(xlsx_path)])

    for mod in forbidden:
        assert mod not in sys.modules, f"CLI must not import {mod}"


# ---------------------------------------------------------------------------
# First Aid tests (34-43)
# ---------------------------------------------------------------------------

def _write_confirmed_columns(tmp_path: Path) -> Path:
    """Write a minimal confirmed_columns JSON file."""
    cc = {
        "confirmed_columns": {
            "Cantidad": {"role": "quantity"},
            "Precio": {"role": "price"},
            "Total": {"role": "amount"},
        }
    }
    cc_path = tmp_path / "confirmed_columns.json"
    cc_path.write_text(json.dumps(cc), encoding="utf-8")
    return cc_path


# ---------------------------------------------------------------------------
# 34. CLI con --confirmed-columns agrega confirmed_columns al packet
# ---------------------------------------------------------------------------

def test_cli_with_confirmed_columns_adds_to_packet(tmp_path, monkeypatch) -> None:
    """CLI with --confirmed-columns must add confirmed_columns to packet."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    exit_code = main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
    ])
    assert exit_code == 0

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "confirmed_columns" in packet
    assert packet["confirmed_columns"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 35. CLI con --run-first-aid genera first_aid_eligibility_gate
# ---------------------------------------------------------------------------

def test_cli_run_first_aid_generates_eligibility_gate(tmp_path, monkeypatch) -> None:
    """CLI with --run-first-aid must generate first_aid_eligibility_gate."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    assert "first_aid_eligibility_gate" in packet
    assert packet["first_aid_eligibility_gate"]["gate_type"] == "FIRST_AID_MINIMAL_ELIGIBILITY"


# ---------------------------------------------------------------------------
# 36. CLI con --run-first-aid genera first_aid_result si eligible
# ---------------------------------------------------------------------------

def test_cli_run_first_aid_generates_result_if_eligible(tmp_path, monkeypatch) -> None:
    """CLI with --run-first-aid must generate first_aid_result when eligible."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    # If eligible, first_aid_result must exist
    if packet["first_aid_eligibility_gate"]["status"] == "ELIGIBLE":
        assert "first_aid_result" in packet
        assert packet["first_aid_result"]["status"] == "DRAFT_REVIEW_REQUIRED"


# ---------------------------------------------------------------------------
# 37. Carpeta contiene confirmed_columns.json
# ---------------------------------------------------------------------------

def test_case_folder_contains_confirmed_columns_json(tmp_path, monkeypatch) -> None:
    """Case folder must contain confirmed_columns.json when provided."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    cc_file = case_folders[0] / "confirmed_columns.json"
    assert cc_file.exists()


# ---------------------------------------------------------------------------
# 38. Carpeta contiene first_aid_result.json
# ---------------------------------------------------------------------------

def test_case_folder_contains_first_aid_result_json(tmp_path, monkeypatch) -> None:
    """Case folder must contain first_aid_result.json when eligible."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    # Check if first_aid_result.json was written (depends on eligibility)
    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    if packet["first_aid_eligibility_gate"]["status"] == "ELIGIBLE":
        fa_file = case_folders[0] / "first_aid_result.json"
        assert fa_file.exists()


# ---------------------------------------------------------------------------
# 39. Carpeta contiene first_aid_owner_summary.md
# ---------------------------------------------------------------------------

def test_case_folder_contains_first_aid_owner_summary_md(tmp_path, monkeypatch) -> None:
    """Case folder must contain first_aid_owner_summary.md when eligible."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))
    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    if packet["first_aid_eligibility_gate"]["status"] == "ELIGIBLE":
        md_file = case_folders[0] / "first_aid_owner_summary.md"
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert "First Aid" in content


# ---------------------------------------------------------------------------
# 40. stdout incluye "First Aid mínimo"
# ---------------------------------------------------------------------------

def test_stdout_includes_first_aid_block(capsys, tmp_path, monkeypatch) -> None:
    """stdout must contain 'First Aid mínimo' when --run-first-aid is used."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    captured = capsys.readouterr()
    assert "First Aid mínimo" in captured.out
    assert "Runtime autorizado: false" in captured.out


# ---------------------------------------------------------------------------
# 41. Sin --confirmed-columns y con --run-first-aid bloquea sin traceback
# ---------------------------------------------------------------------------

def test_run_first_aid_without_confirmed_columns_blocks_gracefully(
    tmp_path, monkeypatch, capsys
) -> None:
    """--run-first-aid without --confirmed-columns → BLOCKED, no traceback."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()

    from pymia.cli.service_1_operator import main
    exit_code = main([
        "--file", str(xlsx_path),
        "--run-first-aid",
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Traceback" not in captured.out
    assert "First Aid mínimo" in captured.out
    assert "BLOCKED" in captured.out


# ---------------------------------------------------------------------------
# 42. runtime_authorized false en todos los niveles con First Aid
# ---------------------------------------------------------------------------

def test_runtime_authorized_false_at_all_levels_with_first_aid(
    tmp_path, monkeypatch
) -> None:
    """runtime_authorized must be False at all levels when First Aid runs."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    output_dir = tmp_path / ".tmp" / "service_1_operator"
    json_files = list(output_dir.glob("*.json"))

    with open(json_files[0], encoding="utf-8") as f:
        packet = json.load(f)

    def _check_no_true(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "runtime_authorized":
                    assert value is not True, f"runtime_authorized=True at key: {key}"
                _check_no_true(value)
        elif isinstance(obj, list):
            for item in obj:
                _check_no_true(item)

    _check_no_true(packet)


# ---------------------------------------------------------------------------
# 43. No imports prohibidos con First Aid
# ---------------------------------------------------------------------------

def test_cli_with_first_aid_does_not_import_forbidden_modules(
    tmp_path, monkeypatch
) -> None:
    """After running CLI with First Aid, forbidden modules must not be imported."""
    monkeypatch.chdir(tmp_path)
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)

    forbidden = [
        "pymia.smartpyme.vertical_pipeline",
        "pymia.smartpyme.service_1_pipeline_v1",
        "pymia.smartpyme.service_1_fsm_decision_patch_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_v1",
        "openai",
        "chatbot",
    ]

    for mod in forbidden:
        sys.modules.pop(mod, None)

    from pymia.cli.service_1_operator import main
    main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])

    for mod in forbidden:
        assert mod not in sys.modules, f"CLI must not import {mod}"
