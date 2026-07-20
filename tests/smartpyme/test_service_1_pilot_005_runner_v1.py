from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "run_service_1_pilot_005_fabrica_industrial.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("pilot_005_runner", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_targets_authorized_fixture_and_sheet() -> None:
    runner = _load_runner()
    assert runner.FIXTURE == ROOT / "prueba_excels" / "fabrica_industrial_compleja.xlsx"
    assert runner.SHEET_NAME == "PRODUCCION"
    assert runner.FIXTURE.exists()


def test_runner_uses_only_explicit_supported_tool_request() -> None:
    runner = _load_runner()
    assert runner.TOOL_REQUESTS == [
        {
            "tool_ref": "precio_margen_basico",
            "inputs": {"precio_venta": 1200, "costo_unitario": 800},
        }
    ]


def test_runner_writes_only_temporary_observation() -> None:
    runner = _load_runner()
    assert runner.OBSERVATION_PATH == (
        ROOT / ".tmp" / "service_1_pilot_005_fabrica_industrial" / "observed_run.json"
    )
    assert "docs" not in runner.OBSERVATION_PATH.parts


def test_runner_requires_canonical_semantic_options() -> None:
    runner = _load_runner()
    first = {
        "product_pipeline": {
            "owner_questions": [
                {
                    "column_name": "maquina",
                    "allowed_option_ids": ["A", "B", "OTHER", "IGNORE"],
                }
            ]
        }
    }
    selected, allowed = runner._canonical_semantic_answers(first)
    assert selected == {"maquina": "A"}
    assert allowed == {"maquina": ["A", "B", "OTHER", "IGNORE"]}


def test_runner_preserves_industrial_scope_limits() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "not a full industrial diagnosis" in source
    assert "Scrap, OEE, machine efficiency" in source
    assert "does not claim automatic tool selection" in source
    assert "No new formula, pathology, semantic capability" in source
