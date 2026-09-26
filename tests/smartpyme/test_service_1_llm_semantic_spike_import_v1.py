from __future__ import annotations

import importlib
from pathlib import Path
import sys


def test_llm_semantic_spike_import_does_not_build_vertex_agent(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    module_name = "tools.service_1_llm_semantic_spike_v1"
    sys.modules.pop(module_name, None)

    module = importlib.import_module(module_name)

    assert module._AGENT is None
    assert callable(module.classify_llm_row)
    assert callable(module.aggregate)
    assert callable(module.decide)


def test_llm_semantic_spike_report_path_is_module_relative(monkeypatch, tmp_path: Path) -> None:
    module = importlib.import_module("tools.service_1_llm_semantic_spike_v1")
    monkeypatch.chdir(tmp_path)

    report_path = module._report_path("case-1")

    assert report_path.parent == Path(module.__file__).resolve().parent
    assert report_path.name == "service_1_llm_semantic_spike_report_v1_case-1.json"
