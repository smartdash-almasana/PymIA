from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import load_state, save_state
from pymia.telegram_document_handler import DocumentResult
from pymia.telegram_runtime import SENTINEL
from pymia.telegram_bot_runtime import _route_document_with_evidence_gate


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXTILE_FIXTURE = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def _seed_state(base_dir: Path, chat_id: str, progressive_context: dict) -> None:
    state = PymIAState(
        tenant_id="telegram",
        chat_id=chat_id,
        conversation_id=chat_id,
        phase="FICHA_PYME_INICIAL",
    )
    state.progressive_context = progressive_context
    save_state("telegram", chat_id, state, base_dir)


def _post_ficha_context(*, evidence_requests: list[dict]) -> dict:
    return {
        "phase": "FICHA_PYME_INICIAL",
        "fsm_state": {
            "phase": "FICHA_PYME_INICIAL",
            "profile_step": "INITIAL_PROFILE_COMPLETE",
            "profile_data": {
                "profile_status": "COMPLETE",
                "raw_first_message": "No me cierra la caja.",
            },
        },
        "post_ficha_routing": {
            "intake_id": "intake-telegram-001",
            "evidence_requests": evidence_requests,
        },
    }


def _doc_result(file_name: str = "ventas.xlsx", path: Path = TEXTILE_FIXTURE) -> DocumentResult:
    return DocumentResult(
        text=f"{SENTINEL} Documento recibido: {file_name}. Ya lo guarde y podes pedirme el analisis cuando quieras.",
        mode="received",
        file_path=str(path),
    )


def test_document_upload_after_ficha_complete_invokes_evidence_gate(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))
    _seed_state(
        tmp_path,
        "chat-doc-001",
        _post_ficha_context(
            evidence_requests=[
                {
                    "request_id": "req-1",
                    "evidence_type": "sales_records",
                    "description": "Ventas del periodo",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["periodo"],
                }
            ]
        ),
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        reply = _route_document_with_evidence_gate("fake-token", "file-1", "ventas.xlsx", "chat-doc-001")

    assert "Documento recibido" in reply
    assert "Evidencia recibida" in reply
    state = load_state("telegram", "chat-doc-001", tmp_path)
    assert state is not None
    assert "evidence_records" in state.progressive_context
    assert len(state.progressive_context["evidence_records"]) == 1
    assert "post_ficha_readiness" in state.progressive_context
    assert state.progressive_context["post_ficha_readiness"]["readiness_state"] in {"READY_FOR_ANALYSIS", "NEEDS_EVIDENCE"}
    lowered = reply.lower()
    assert "diagnóstico" not in lowered
    assert "diagnostico" not in lowered


def test_document_upload_without_ficha_complete_returns_generic_confirmation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))
    _seed_state(
        tmp_path,
        "chat-doc-002",
        {
            "phase": "FICHA_PYME_INICIAL",
            "fsm_state": {"profile_step": "ASK_CONTACT_NAME", "profile_data": {}},
        },
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        reply = _route_document_with_evidence_gate("fake-token", "file-2", "ventas.xlsx", "chat-doc-002")

    assert "Documento recibido" in reply
    assert "Evidencia recibida" not in reply
    state = load_state("telegram", "chat-doc-002", tmp_path)
    assert state is not None
    assert "evidence_records" not in state.progressive_context


def test_document_upload_without_previous_state_returns_generic_confirmation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        reply = _route_document_with_evidence_gate("fake-token", "file-3", "ventas.xlsx", "chat-doc-003")

    assert "Documento recibido" in reply
    assert "Evidencia recibida" not in reply
    state = load_state("telegram", "chat-doc-003", tmp_path)
    assert state is None


def test_same_file_uploaded_twice_does_not_duplicate_evidence_records(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))
    _seed_state(
        tmp_path,
        "chat-doc-004",
        _post_ficha_context(
            evidence_requests=[
                {
                    "request_id": "req-1",
                    "evidence_type": "sales_records",
                    "description": "Ventas del periodo",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["periodo"],
                }
            ]
        ),
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        _route_document_with_evidence_gate("fake-token", "file-4", "ventas.xlsx", "chat-doc-004")
        _route_document_with_evidence_gate("fake-token", "file-4", "ventas.xlsx", "chat-doc-004")

    state = load_state("telegram", "chat-doc-004", tmp_path)
    assert state is not None
    assert len(state.progressive_context.get("evidence_records", [])) == 1


def test_honest_reply_lists_missing_evidence_types_when_incomplete(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))
    _seed_state(
        tmp_path,
        "chat-doc-005",
        _post_ficha_context(
            evidence_requests=[
                {
                    "request_id": "req-1",
                    "evidence_type": "sales_records",
                    "description": "Ventas del periodo",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["periodo"],
                },
                {
                    "request_id": "req-2",
                    "evidence_type": "price_list",
                    "description": "Lista de precios",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["producto"],
                },
            ]
        ),
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        reply = _route_document_with_evidence_gate("fake-token", "file-5", "ventas.xlsx", "chat-doc-005")

    assert "todavía falta esta evidencia mínima" in reply.lower()
    assert "price_list" in reply


def test_bot_never_diagnoses_without_sufficient_evidence(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))
    _seed_state(
        tmp_path,
        "chat-doc-006",
        _post_ficha_context(
            evidence_requests=[
                {
                    "request_id": "req-1",
                    "evidence_type": "sales_records",
                    "description": "Ventas del periodo",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["periodo"],
                },
                {
                    "request_id": "req-2",
                    "evidence_type": "cost_records",
                    "description": "Costos",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["costo_directo"],
                },
            ]
        ),
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        reply = _route_document_with_evidence_gate("fake-token", "file-6", "ventas.xlsx", "chat-doc-006")

    lowered = reply.lower()
    for forbidden in ("margen", "diagnóstico", "diagnostico", "hipótesis confirmada", "123", "45%"):
        assert forbidden not in lowered


def test_document_bridge_respects_PYMIA_TELEGRAM_STATE_BASE_DIR_env(tmp_path, monkeypatch) -> None:
    state_dir = tmp_path / "telegram-state-env"
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(state_dir))
    _seed_state(
        state_dir,
        "chat-doc-007",
        _post_ficha_context(
            evidence_requests=[
                {
                    "request_id": "req-1",
                    "evidence_type": "sales_records",
                    "description": "Ventas del periodo",
                    "status": "REQUESTED",
                    "blocks_analysis": True,
                    "required_fields": ["periodo"],
                }
            ]
        ),
    )

    with patch("pymia.telegram_bot_runtime.handle_document", return_value=_doc_result()):
        _route_document_with_evidence_gate("fake-token", "file-7", "ventas.xlsx", "chat-doc-007")

    state = load_state("telegram", "chat-doc-007", state_dir)
    assert state is not None
    assert state.progressive_context.get("evidence_records")
