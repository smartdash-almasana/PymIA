from __future__ import annotations

from pathlib import Path
from typing import Any

from pymia.orchestration.graph import run_pymia_graph
from pymia.orchestration.organization_profile_intake import (
    answer_organization_profile_question,
    start_organization_profile_intake,
)
from pymia.orchestration.state import PymIAEvent
from pymia.orchestration.state_storage import load_state, save_state

DEFAULT_BASE_DIR = Path(".runtime/os_storage")


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _tail_decision(state: Any) -> str | None:
    if state is None or not state.decision_trail:
        return None
    return state.decision_trail[-1]


def _coerce_state(tenant_id: str, chat_id: str, conversation_id: str, base_dir: Path) -> Any:
    from pymia.orchestration.state import PymIAState

    state = load_state(tenant_id, chat_id, base_dir)
    if state is None:
        state = PymIAState(
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
        )
    return state


def start_organization_profile(
    *,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id) and _is_non_empty_str(conversation_id)):
        return {
            "phase": None,
            "reply_text": None,
            "completed": False,
            "next_question_id": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": "invalid tenant_id/chat_id/conversation_id",
        }
    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        state = _coerce_state(tenant_id, chat_id, conversation_id, target_base)
        before_context = dict(state.progressive_context) if isinstance(state.progressive_context, dict) else {}
        intake_result = start_organization_profile_intake(before_context)
        state.progressive_context = dict(intake_result.updated_progressive_context)
        state.phase = "NEW"
        state.add_decision(intake_result.decision_trail_entry)
        save_state(tenant_id, chat_id, state, target_base)
        return {
            "phase": state.phase,
            "reply_text": intake_result.reply_text,
            "completed": intake_result.completed,
            "next_question_id": intake_result.next_question_id,
            "progressive_context_updated": state.progressive_context != before_context,
            "decision_trail_entry": intake_result.decision_trail_entry,
            "error": None,
        }
    except Exception as exc:
        return {
            "phase": None,
            "reply_text": None,
            "completed": False,
            "next_question_id": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": str(exc),
        }


def answer_organization_profile(
    *,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    answer: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id) and _is_non_empty_str(conversation_id)):
        return {
            "phase": None,
            "reply_text": None,
            "completed": False,
            "next_question_id": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": "invalid tenant_id/chat_id/conversation_id",
        }
    if not _is_non_empty_str(answer):
        return {
            "phase": None,
            "reply_text": None,
            "completed": False,
            "next_question_id": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": "invalid answer",
        }
    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        state = _coerce_state(tenant_id, chat_id, conversation_id, target_base)
        before_context = dict(state.progressive_context) if isinstance(state.progressive_context, dict) else {}
        intake_result = answer_organization_profile_question(before_context, answer)
        state.progressive_context = dict(intake_result.updated_progressive_context)
        state.phase = "NEW"
        state.add_decision(intake_result.decision_trail_entry)
        save_state(tenant_id, chat_id, state, target_base)
        return {
            "phase": state.phase,
            "reply_text": intake_result.reply_text,
            "completed": intake_result.completed,
            "next_question_id": intake_result.next_question_id,
            "progressive_context_updated": state.progressive_context != before_context,
            "decision_trail_entry": intake_result.decision_trail_entry,
            "error": None,
        }
    except Exception as exc:
        return {
            "phase": None,
            "reply_text": None,
            "completed": False,
            "next_question_id": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": str(exc),
        }


def submit_text_message(
    *,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    text: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id) and _is_non_empty_str(conversation_id)):
        return {
            "phase": None,
            "reply_text": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": "invalid tenant_id/chat_id/conversation_id",
        }
    if not _is_non_empty_str(text):
        return {
            "phase": None,
            "reply_text": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": "invalid text",
        }
    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        current = load_state(tenant_id, chat_id, target_base)
        progressive_context = (
            dict(current.progressive_context)
            if current is not None and isinstance(current.progressive_context, dict)
            else {}
        )
        profile_status = str(progressive_context.get("organization_profile_status") or "").upper()
        profile = progressive_context.get("organization_profile")
        profile_complete = profile_status == "COMPLETED" and isinstance(profile, dict) and bool(profile)
        if not profile_complete:
            return start_organization_profile(
                tenant_id=tenant_id,
                chat_id=chat_id,
                conversation_id=conversation_id,
                base_dir=target_base,
            )

        before = load_state(tenant_id, chat_id, target_base)
        before_context = dict(before.progressive_context) if before else {}
        reply = run_pymia_graph(
            PymIAEvent(
                event_type="text_message",
                tenant_id=tenant_id,
                chat_id=chat_id,
                conversation_id=conversation_id,
                text=text,
            ),
            base_dir=target_base,
        )
        after = load_state(tenant_id, chat_id, target_base)
        after_context = dict(after.progressive_context) if after else {}
        return {
            "phase": after.phase if after else None,
            "reply_text": reply,
            "progressive_context_updated": after_context != before_context,
            "decision_trail_entry": _tail_decision(after),
            "error": None,
        }
    except Exception as exc:
        return {
            "phase": None,
            "reply_text": None,
            "progressive_context_updated": False,
            "decision_trail_entry": None,
            "error": str(exc),
        }


def submit_document(
    *,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    document_path: Path | str,
    document_name: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id) and _is_non_empty_str(conversation_id)):
        return {
            "phase": None,
            "intake_id": None,
            "evidence_ids": [],
            "decision_trail_entry": None,
            "error": "invalid tenant_id/chat_id/conversation_id",
        }
    if not _is_non_empty_str(document_name):
        return {"phase": None, "intake_id": None, "evidence_ids": [], "decision_trail_entry": None, "error": "invalid document_name"}

    doc_path = Path(document_path)
    if not doc_path.exists():
        return {"phase": None, "intake_id": None, "evidence_ids": [], "decision_trail_entry": None, "error": "document_path not found"}

    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        _ = run_pymia_graph(
            PymIAEvent(
                event_type="document_received",
                tenant_id=tenant_id,
                chat_id=chat_id,
                conversation_id=conversation_id,
                document_path=doc_path,
                document_name=document_name,
            ),
            base_dir=target_base,
        )
        state = load_state(tenant_id, chat_id, target_base)
        return {
            "phase": state.phase if state else None,
            "intake_id": state.intake_id if state else None,
            "evidence_ids": list(state.evidence_ids) if state else [],
            "decision_trail_entry": _tail_decision(state),
            "error": None,
        }
    except Exception as exc:
        return {"phase": None, "intake_id": None, "evidence_ids": [], "decision_trail_entry": None, "error": str(exc)}


def request_diagnostic(
    *,
    tenant_id: str,
    chat_id: str,
    conversation_id: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id) and _is_non_empty_str(conversation_id)):
        return {
            "phase": None,
            "delivery_status": None,
            "delivery_summary": None,
            "findings_count": 0,
            "output_refs": [],
            "decision_trail_entry": None,
            "error": "invalid tenant_id/chat_id/conversation_id",
        }
    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        _ = run_pymia_graph(
            PymIAEvent(
                event_type="diagnostic_request",
                tenant_id=tenant_id,
                chat_id=chat_id,
                conversation_id=conversation_id,
                text="diagnosticalo",
            ),
            base_dir=target_base,
        )
        state = load_state(tenant_id, chat_id, target_base)
        return {
            "phase": state.phase if state else None,
            "delivery_status": state.delivery_status if state else None,
            "delivery_summary": state.delivery_summary if state else None,
            "findings_count": int(state.findings_count) if state else 0,
            "output_refs": list(state.output_refs) if state else [],
            "decision_trail_entry": _tail_decision(state),
            "error": None,
        }
    except Exception as exc:
        return {
            "phase": None,
            "delivery_status": None,
            "delivery_summary": None,
            "findings_count": 0,
            "output_refs": [],
            "decision_trail_entry": None,
            "error": str(exc),
        }


def get_conversation_state(
    *,
    tenant_id: str,
    chat_id: str,
    base_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not (_is_non_empty_str(tenant_id) and _is_non_empty_str(chat_id)):
        return {"phase": None, "progressive_context": {}, "decision_trail_tail": [], "errors": [], "error": "invalid tenant_id/chat_id"}
    target_base = Path(base_dir) if base_dir is not None else DEFAULT_BASE_DIR
    try:
        state = load_state(tenant_id, chat_id, target_base)
        if state is None:
            return {"phase": None, "progressive_context": {}, "decision_trail_tail": [], "errors": [], "error": "state not found"}
        return {
            "phase": state.phase,
            "progressive_context": dict(state.progressive_context),
            "decision_trail_tail": list(state.decision_trail[-5:]),
            "errors": list(state.errors),
            "error": None,
        }
    except Exception as exc:
        return {"phase": None, "progressive_context": {}, "decision_trail_tail": [], "errors": [], "error": str(exc)}


OS_TOOLS = [
    {
        "name": "start_organization_profile",
        "description": "Start mandatory organization profile intake flow.",
        "parameters": ["tenant_id", "chat_id", "conversation_id", "base_dir"],
        "returns": ["phase", "reply_text", "completed", "next_question_id", "progressive_context_updated", "decision_trail_entry", "error"],
    },
    {
        "name": "answer_organization_profile",
        "description": "Answer next organization profile intake question.",
        "parameters": ["tenant_id", "chat_id", "conversation_id", "answer", "base_dir"],
        "returns": ["phase", "reply_text", "completed", "next_question_id", "progressive_context_updated", "decision_trail_entry", "error"],
    },
    {
        "name": "submit_text_message",
        "description": "Submit a text message turn to orchestration OS.",
        "parameters": ["tenant_id", "chat_id", "conversation_id", "text", "base_dir"],
        "returns": ["phase", "reply_text", "progressive_context_updated", "decision_trail_entry", "error"],
    },
    {
        "name": "submit_document",
        "description": "Register a document event in orchestration OS.",
        "parameters": ["tenant_id", "chat_id", "conversation_id", "document_path", "document_name", "base_dir"],
        "returns": ["phase", "intake_id", "evidence_ids", "decision_trail_entry", "error"],
    },
    {
        "name": "request_diagnostic",
        "description": "Request diagnostic execution for current conversation state.",
        "parameters": ["tenant_id", "chat_id", "conversation_id", "base_dir"],
        "returns": ["phase", "delivery_status", "delivery_summary", "findings_count", "output_refs", "decision_trail_entry", "error"],
    },
    {
        "name": "get_conversation_state",
        "description": "Get persisted conversation state snapshot.",
        "parameters": ["tenant_id", "chat_id", "base_dir"],
        "returns": ["phase", "progressive_context", "decision_trail_tail", "errors", "error"],
    },
]
