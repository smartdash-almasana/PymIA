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


def _write_five_tool_requests(tmp_path: Path) -> Path:
    tool_requests = [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {"precio_venta": 2500, "costo_unitario": 1625},
        },
        {
            "tool_ref": "caja_diaria_triage",
            "inputs": {"saldo_inicial": 180000, "ingresos": 324500, "egresos": 286750},
        },
        {
            "tool_ref": "stock_alertas_basicas",
            "inputs": {
                "producto": "Pack yerba 1kg",
                "stock_actual": 8,
                "stock_minimo": 15,
                "ventas_diarias_promedio": 3,
            },
        },
        {
            "tool_ref": "gastos_triage",
            "inputs": {
                "concepto": ["alquiler", "luz", "insumos"],
                "importe": [1000, 200, 300],
                "categoria": ["fijo", "fijo", "variable"],
            },
        },
        {
            "tool_ref": "proveedores_precio_variacion_triage",
            "inputs": {
                "proveedor": ["Proveedor A", "Proveedor B"],
                "producto_o_insumo": ["Harina", "Harina"],
                "precio_o_costo": [1000, 1250],
            },
        },
    ]
    tools_path = tmp_path / "five_tool_requests.json"
    tools_path.write_text(json.dumps(tool_requests), encoding="utf-8")
    return tools_path


def _write_confirmed_columns(tmp_path: Path) -> Path:
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
# 1. CLI acepta --run-tools con 5 tools explícitas
# ---------------------------------------------------------------------------


def test_cli_with_run_tools_five_tools_explicit_json(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = _write_five_tool_requests(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pipeline de herramientas First Aid" in captured.out
    assert "precio_margen_basico" in captured.out
    assert "caja_diaria_triage" in captured.out
    assert "gastos_triage" in captured.out
    assert "proveedores_precio_variacion_triage" in captured.out
    assert "stock_alertas_basicas" in captured.out
    assert "Revisi\u00f3n humana requerida: true" in captured.out
    assert "Runtime autorizado: false" in captured.out


# ---------------------------------------------------------------------------
# 2. CLI delega a run_service_1_pipeline_v1
# ---------------------------------------------------------------------------


def test_cli_run_tools_delegates_to_pipeline(
    tmp_path, monkeypatch
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = _write_five_tool_requests(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    assert exit_code == 0

    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1

    operator_packet_path = case_folders[0] / "operator_packet.json"
    packet = json.loads(operator_packet_path.read_text(encoding="utf-8"))
    assert "pipeline_result" in packet
    assert packet["pipeline_result"]["requested_tool_count"] == 5
    assert len(packet["pipeline_result"]["tool_results"]) == 5

    pipeline_result_path = case_folders[0] / "pipeline_result.json"
    assert pipeline_result_path.exists()

    pipeline_data = json.loads(pipeline_result_path.read_text(encoding="utf-8"))
    assert pipeline_data["runtime_authorized"] is False
    assert len(pipeline_data["delivery_flow"]["deliveries"]) == 5


# ---------------------------------------------------------------------------
# 3. Flujo legacy con --run-first-aid sigue funcionando
# ---------------------------------------------------------------------------


def test_legacy_run_first_aid_still_works(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    cc_path = _write_confirmed_columns(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "First Aid m\u00ednimo" in captured.out
    assert "DRAFT_REVIEW_REQUIRED" in captured.out
    assert "QA delivery gate" in captured.out


# ---------------------------------------------------------------------------
# 4. CLI rechaza JSON inválido sin inferir correcciones
# ---------------------------------------------------------------------------


def test_run_tools_rejects_invalid_json(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = tmp_path / "bad.json"
    tools_path.write_text("esto no es json", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "invalid" in captured.out.lower()


# ---------------------------------------------------------------------------
# 5. CLI rechaza requests vacías o mal formadas
# ---------------------------------------------------------------------------


def test_run_tools_rejects_empty_list(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = tmp_path / "empty.json"
    tools_path.write_text("[]", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "non-empty" in captured.out.lower()


def test_run_tools_rejects_missing_tool_ref(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = tmp_path / "no_tool_ref.json"
    tools_path.write_text(
        json.dumps([{"inputs": {"x": 1}}]), encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "tool_ref" in captured.out.lower()


def test_run_tools_rejects_missing_inputs(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = tmp_path / "no_inputs.json"
    tools_path.write_text(
        json.dumps([{"tool_ref": "precio_margen_basico"}]), encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "inputs" in captured.out.lower()


# ---------------------------------------------------------------------------
# 6. Output visible conserva framing operativo (sin diagnóstico)
# ---------------------------------------------------------------------------


def test_run_tools_output_preserves_operational_framing(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = _write_five_tool_requests(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "diagn\u00f3stico" not in captured.out.lower()
    assert "diagnosis" not in captured.out.lower()
    assert "Runtime autorizado: false" in captured.out
    assert "Revisi\u00f3n humana requerida: true" in captured.out


# ---------------------------------------------------------------------------
# 7. --run-tools and --run-first-aid can coexist
# ---------------------------------------------------------------------------


def test_run_tools_and_first_aid_can_coexist(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    tools_path = _write_five_tool_requests(tmp_path)
    cc_path = _write_confirmed_columns(tmp_path)
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tools_path),
        "--confirmed-columns", str(cc_path),
        "--run-first-aid",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pipeline de herramientas First Aid" in captured.out
    assert "First Aid m\u00ednimo" in captured.out
    assert "QA delivery gate" in captured.out

    # Both artifacts in case folder
    case_dir = tmp_path / ".tmp" / "service_1_cases"
    case_folders = [d for d in case_dir.iterdir() if d.is_dir()]
    assert len(case_folders) == 1
    assert (case_folders[0] / "pipeline_result.json").exists()
    assert (case_folders[0] / "first_aid_result.json").exists()


# ---------------------------------------------------------------------------
# 8. CLI rechaza archivo tools no existente
# ---------------------------------------------------------------------------


def test_run_tools_rejects_nonexistent_file(
    tmp_path, monkeypatch, capsys
) -> None:
    xlsx_path = _find_xlsx_fixture()
    monkeypatch.chdir(tmp_path)

    from pymia.cli.service_1_operator import main

    exit_code = main([
        "--file", str(xlsx_path),
        "--run-tools", str(tmp_path / "no_existe.json"),
    ])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "not found" in captured.out.lower()
