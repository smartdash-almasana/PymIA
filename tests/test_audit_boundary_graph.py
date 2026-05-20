from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Ensure conversa-engine is in path
CONVERSA_DIR = Path(__file__).resolve().parents[1] / "conversa-engine"
if str(CONVERSA_DIR) not in sys.path:
    sys.path.insert(0, str(CONVERSA_DIR))

# Ensure repo root is in path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from audit_boundary_graph import run_audit_boundary_graph_v1, build_audit_boundary_graph

TEXTIL_XLSX = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def test_audit_boundary_graph_internal_fact_file_flow(tmp_path: Path) -> None:
    initial_state: Dict[str, Any] = {
        "tenant_id": "graph_test",
        "user_id": "user_1",
        "session_id": "graph_test/user_1",
        "graph_thread_id": "thread-12345",
        "file_path": str(TEXTIL_XLSX),
        "file_name": "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        "mime_type": None,
        "expected_schema": "unknown",
        "entropy_level": 0.1,  # Force INTERNAL_FACT
        "message_text": "quiero ver PYME_033",
        "base_path": str(tmp_path),
        "fallback_path": str(tmp_path),
    }

    final_state = run_audit_boundary_graph_v1(initial_state)

    assert final_state["error"] is None, f"Workflow failed with error: {final_state['error']}"
    assert final_state["route_label"] == "INTERNAL_FACT"
    assert final_state["audit_found"] is True
    assert final_state["audit_output_path"] is not None
    assert Path(final_state["audit_output_path"]).exists()

    # Routing assertions
    routing_decision = final_state["routing_decision"]
    assert routing_decision is not None
    assert routing_decision["pathology_code"] == "PYME_033"
    assert "ventas_por_sku" in routing_decision["missing_evidence"]
    assert "ventas_por_sku" in final_state["reply_text"]


def test_audit_boundary_graph_message_without_audit_fails_closed(tmp_path: Path) -> None:
    initial_state: Dict[str, Any] = {
        "tenant_id": "graph_test_empty",
        "user_id": "user_2",
        "session_id": "graph_test_empty/user_2",
        "graph_thread_id": "thread-empty-999",
        "file_path": None,
        "message_text": "quiero mejorar margen",
        "base_path": str(tmp_path),
        "fallback_path": str(tmp_path),
    }

    final_state = run_audit_boundary_graph_v1(initial_state)

    assert final_state["error"] is None
    assert final_state["audit_found"] is False
    assert final_state["audit_output_path"] is None
    assert "Todavía no tengo una auditoría operacional activa" in final_state["reply_text"]
    assert final_state["routing_decision"] is None


def test_audit_boundary_graph_does_not_store_audit_payload(tmp_path: Path) -> None:
    initial_state: Dict[str, Any] = {
        "tenant_id": "graph_test_payload",
        "user_id": "user_3",
        "session_id": "graph_test_payload/user_3",
        "graph_thread_id": "thread-payload-abc",
        "file_path": str(TEXTIL_XLSX),
        "file_name": "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        "mime_type": None,
        "expected_schema": "unknown",
        "entropy_level": 0.1,
        "message_text": "quiero ver PYME_033",
        "base_path": str(tmp_path),
        "fallback_path": str(tmp_path),
    }

    final_state = run_audit_boundary_graph_v1(initial_state)

    assert final_state["error"] is None
    
    # Assert that actual audit object or large tables/raw_tables are never stored in StateGraph dict
    for forbidden_key in ["OperationalAuditResult", "audit_result", "tables", "raw_tables", "normalized_tables"]:
        assert forbidden_key not in final_state


def test_no_langgraph_imports_under_pymia() -> None:
    pymia_dir = REPO_ROOT / "pymia"
    py_files = list(pymia_dir.rglob("*.py"))
    assert len(py_files) > 0, "No Python files found under pymia/"

    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        assert "langgraph" not in content, f"Forbidden import/mention of langgraph in {py_file}"


def test_build_audit_boundary_graph_uses_langgraph_when_available(tmp_path: Path) -> None:
    compiled = build_audit_boundary_graph()
    try:
        import langgraph
        assert compiled is not None
        assert hasattr(compiled, "invoke")
    except ImportError:
        assert compiled is None
        return

    # Let's run a test invocation of the real compiled LangGraph StateGraph!
    initial_state: Dict[str, Any] = {
        "tenant_id": "graph_real_langgraph",
        "user_id": "user_real",
        "session_id": "graph_real_langgraph/user_real",
        "graph_thread_id": "thread-real-langgraph",
        "file_path": str(TEXTIL_XLSX),
        "file_name": "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        "mime_type": None,
        "expected_schema": "unknown",
        "entropy_level": 0.1,
        "message_text": "quiero ver PYME_033",
        "base_path": str(tmp_path),
        "fallback_path": str(tmp_path),
        "route_label": None,
        "intake_message": None,
        "audit_output_path": None,
        "audit_found": False,
        "routing_decision": None,
        "reply_text": None,
        "error": None,
    }

    # Execute using the real CompiledStateGraph .invoke
    config = {"configurable": {"thread_id": "thread-real-langgraph"}}
    final_state = compiled.invoke(initial_state, config)

    assert final_state.get("error") is None, f"Workflow failed: {final_state.get('error')}"
    assert final_state.get("route_label") == "INTERNAL_FACT"
    assert final_state.get("audit_found") is True
    assert final_state.get("audit_output_path") is not None
    assert Path(final_state["audit_output_path"]).exists()

    routing_decision = final_state.get("routing_decision")
    assert routing_decision is not None
    assert routing_decision["pathology_code"] == "PYME_033"
    assert "ventas_por_sku" in routing_decision["missing_evidence"]
    assert "ventas_por_sku" in final_state.get("reply_text", "")


