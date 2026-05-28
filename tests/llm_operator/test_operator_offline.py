"""Tests offline del LLM Operator C16.

Principios:
- Usa registry real (os_tool_registry) para verificar integración.
- No importa graph, state_storage, smartpyme ni telegram directamente.
- Todo el E2E pasa por LLMOperator + os_tool_registry.
- MockProvider es determinístico: mismos inputs → mismos outputs.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType

import pandas as pd
import pytest

import pymia.orchestration.os_tool_registry as registry_module
from pymia.llm_operator.operator import LLMOperator, OperatorResult
from pymia.llm_operator.providers import AbstractProvider, MockProvider, ToolDecision


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_operator(extra_input: dict | None = None) -> LLMOperator:
    return LLMOperator(
        provider=MockProvider(extra_input=extra_input),
        registry=registry_module,
    )


def _minimal_xlsx(path: Path) -> Path:
    pd.DataFrame(
        [
            {"producto": "A", "ventas": 200, "costo": 150},
            {"producto": "B", "ventas": 80, "costo": 60},
        ]
    ).to_excel(path, index=False)
    return path


# ---------------------------------------------------------------------------
# Guardrails: contratos de imports y source
# ---------------------------------------------------------------------------


def test_llm_operator_source_has_no_forbidden_imports() -> None:
    """El operador no debe importar directamente módulos prohibidos."""
    import pymia.llm_operator.operator as op_module
    import pymia.llm_operator.providers as prov_module

    # These are checked as full import statements to avoid docstring false positives
    forbidden_import_patterns = [
        "from pymia.orchestration.graph",
        "import pymia.orchestration.graph",
        "from pymia.orchestration.state_storage",
        "import pymia.orchestration.state_storage",
        "from pymia.smartpyme",
        "import pymia.smartpyme",
        "import telegram",
        "from telegram",
        "import hermes",
        "from hermes",
        "import langgraph",
        "from langgraph",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "import pydantic_ai",
        "from pydantic_ai",
    ]

    for mod in (op_module, prov_module):
        source = Path(mod.__file__).read_text(encoding="utf-8")
        for pattern in forbidden_import_patterns:
            assert pattern not in source, (
                f"Forbidden import pattern '{pattern}' found in {mod.__file__}"
            )


def test_os_tool_registry_not_modified() -> None:
    """os_tool_registry.py no debe haber sido modificado por C16."""
    source = Path("pymia/orchestration/os_tool_registry.py").read_text(encoding="utf-8")
    # Los 4 tools originales deben estar presentes
    for tool_name in ["submit_text_message", "submit_document", "request_diagnostic", "get_conversation_state"]:
        assert tool_name in source, f"Tool '{tool_name}' missing from os_tool_registry"
    # No debe haber referencias al módulo llm_operator
    assert "llm_operator" not in source


def test_operator_init_rejects_non_provider() -> None:
    with pytest.raises(TypeError, match="AbstractProvider"):
        LLMOperator(provider="not_a_provider", registry=registry_module)  # type: ignore[arg-type]


def test_operator_init_rejects_non_module() -> None:
    with pytest.raises(TypeError, match="module"):
        LLMOperator(provider=MockProvider(), registry="not_a_module")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ToolDecision y MockProvider
# ---------------------------------------------------------------------------


def test_mock_provider_chooses_submit_text_for_generic_message() -> None:
    provider = MockProvider()
    schema = registry_module.OS_TOOLS
    decision = provider.choose_tool("hola, necesito ayuda", state={}, tools_schema=schema)
    assert decision.tool_name == "submit_text_message"
    assert isinstance(decision.reasoning, str)
    assert decision.reasoning


def test_mock_provider_chooses_request_diagnostic_for_margen() -> None:
    provider = MockProvider()
    schema = registry_module.OS_TOOLS
    decision = provider.choose_tool("no sé si gano plata con esto", state={}, tools_schema=schema)
    assert decision.tool_name == "request_diagnostic"


def test_mock_provider_chooses_request_diagnostic_for_diagnosticar() -> None:
    provider = MockProvider()
    schema = registry_module.OS_TOOLS
    decision = provider.choose_tool("quiero diagnosticar mi negocio", state={}, tools_schema=schema)
    assert decision.tool_name == "request_diagnostic"


def test_mock_provider_chooses_submit_document_when_path_available(tmp_path: Path) -> None:
    doc = _minimal_xlsx(tmp_path / "ventas.xlsx")
    provider = MockProvider(extra_input={"document_path": doc, "document_name": "ventas.xlsx"})
    schema = registry_module.OS_TOOLS
    decision = provider.choose_tool("te mando el excel con las ventas", state={}, tools_schema=schema)
    assert decision.tool_name == "submit_document"
    assert "document_path" in decision.extra_args


def test_mock_provider_falls_back_to_text_when_no_document_path() -> None:
    """Menciona excel pero no hay document_path → submit_text_message."""
    provider = MockProvider()  # sin extra_input
    schema = registry_module.OS_TOOLS
    decision = provider.choose_tool("quiero subir un excel", state={}, tools_schema=schema)
    assert decision.tool_name == "submit_text_message"


def test_mock_provider_render_reply_uses_reply_text() -> None:
    provider = MockProvider()
    result = {"reply_text": "[PymIA:TELEGRAM_RUNTIME] Hola, bienvenido.", "phase": "NEW", "error": None}
    reply = provider.render_reply("hola", result)
    assert "Hola, bienvenido" in reply


def test_mock_provider_render_reply_uses_delivery_summary_when_no_reply_text() -> None:
    provider = MockProvider()
    result = {"reply_text": None, "delivery_summary": "Análisis completado: 3 hallazgos.", "phase": "DELIVERED", "error": None}
    reply = provider.render_reply("analizar", result)
    assert "Análisis completado" in reply


def test_mock_provider_render_reply_handles_error() -> None:
    provider = MockProvider()
    result = {"error": "document_path not found", "phase": None}
    reply = provider.render_reply("archivo", result)
    assert "Error" in reply or "error" in reply.lower()


# ---------------------------------------------------------------------------
# OperatorResult
# ---------------------------------------------------------------------------


def test_operator_result_is_json_serializable() -> None:
    result = OperatorResult(
        reply_text="OK",
        selected_tool="submit_text_message",
        tool_args={"tenant_id": "t", "chat_id": "c", "conversation_id": "cv", "text": "hola"},
        tool_result={"phase": "NEW", "reply_text": "OK", "progressive_context_updated": True, "decision_trail_entry": "x", "error": None},
        operator_trace=["step1", "step2"],
        error=None,
    )
    assert result.is_json_serializable()
    d = result.to_dict()
    assert d["selected_tool"] == "submit_text_message"
    assert d["error"] is None


# ---------------------------------------------------------------------------
# handle_turn — flujos E2E via registry
# ---------------------------------------------------------------------------


def test_handle_turn_text_message_returns_operator_result(tmp_path: Path) -> None:
    operator = _make_operator()
    result = operator.handle_turn(
        tenant_id="tenant_c16",
        chat_id="chat_c16",
        conversation_id="conv_c16",
        message="hola, necesito revisar mis números",
        base_dir=tmp_path,
    )
    assert isinstance(result, OperatorResult)
    assert result.selected_tool == "submit_text_message"
    assert result.error is None
    assert result.reply_text
    assert result.is_json_serializable()


def test_handle_turn_uses_registry_not_graph_directly(tmp_path: Path) -> None:
    """Verificar que handle_turn no usa graph ni state_storage directamente."""
    import pymia.llm_operator.operator as op_src

    source = Path(op_src.__file__).read_text(encoding="utf-8")
    assert "run_pymia_graph" not in source
    assert "save_state" not in source
    assert "load_state" not in source


def test_handle_turn_request_diagnostic_after_document(tmp_path: Path) -> None:
    """Flujo completo via operator: texto → documento → diagnóstico."""
    # Turno 1: texto
    op_text = _make_operator()
    result1 = op_text.handle_turn(
        tenant_id="tenant_diag",
        chat_id="chat_diag",
        conversation_id="conv_diag",
        message="hola, tengo un negocio de ropa",
        base_dir=tmp_path,
    )
    assert result1.selected_tool == "submit_text_message"
    assert result1.error is None

    # Turno 2: documento
    doc = _minimal_xlsx(tmp_path / "ventas_ropa.xlsx")
    op_doc = _make_operator(extra_input={"document_path": doc, "document_name": "ventas_ropa.xlsx"})
    result2 = op_doc.handle_turn(
        tenant_id="tenant_diag",
        chat_id="chat_diag",
        conversation_id="conv_diag",
        message="te mando el excel con ventas",
        base_dir=tmp_path,
    )
    assert result2.selected_tool == "submit_document"
    assert result2.error is None
    # El OS debe haber registrado intake/evidence
    assert result2.tool_result.get("error") is None

    # Turno 3: diagnóstico
    op_diag = _make_operator()
    result3 = op_diag.handle_turn(
        tenant_id="tenant_diag",
        chat_id="chat_diag",
        conversation_id="conv_diag",
        message="quiero diagnosticar todo",
        base_dir=tmp_path,
    )
    assert result3.selected_tool == "request_diagnostic"
    assert result3.error is None
    assert result3.is_json_serializable()


def test_handle_turn_with_invalid_tenant_returns_error_result(tmp_path: Path) -> None:
    """Si el registry rechaza el tool por params inválidos, OperatorResult.error es None
    pero tool_result.error estará presente (fail-closed del registry)."""
    # MockProvider elegirá submit_text_message; el registry lo rechazará por tenant vacío
    op = _make_operator()
    result = op.handle_turn(
        tenant_id="",
        chat_id="chat",
        conversation_id="conv",
        message="hola",
        base_dir=tmp_path,
    )
    # El operador mismo no lanza excepción
    assert isinstance(result, OperatorResult)
    assert result.is_json_serializable()
    # El error queda en tool_result (registry fail-closed) o en operator error
    has_error = bool(result.error) or bool(result.tool_result.get("error"))
    assert has_error


def test_handle_turn_operator_trace_is_populated(tmp_path: Path) -> None:
    op = _make_operator()
    result = op.handle_turn(
        tenant_id="tenant_trace",
        chat_id="chat_trace",
        conversation_id="conv_trace",
        message="quiero saber si tengo margen",
        base_dir=tmp_path,
    )
    assert isinstance(result.operator_trace, list)
    assert len(result.operator_trace) >= 2  # al menos choose_tool + invoke


def test_handle_turn_result_to_dict_matches_json_roundtrip(tmp_path: Path) -> None:
    op = _make_operator()
    result = op.handle_turn(
        tenant_id="tenant_json",
        chat_id="chat_json",
        conversation_id="conv_json",
        message="hola",
        base_dir=tmp_path,
    )
    d = result.to_dict()
    roundtrip = json.loads(json.dumps(d))
    assert roundtrip["selected_tool"] == result.selected_tool
    assert roundtrip["reply_text"] == result.reply_text
