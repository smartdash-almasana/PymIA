from __future__ import annotations

import importlib
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
