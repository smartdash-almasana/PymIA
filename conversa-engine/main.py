from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

RESERVED_COMMANDS = {
    "--register-evidence",
    "--create-case",
    "--execute",
    "--status",
}

_PROGRESSIVE_CONTEXT_BY_SESSION = {}
_SUPERMEMORY_RECALL_CLIENT = None
_SUPERMEMORY_RECALL_INITIALIZED = False


def _cli_message_from_args(args: list[str]) -> tuple[int, str, str | None]:
    """
    Translate CLI args into a message or a fail-closed command response.

    Returns:
        (exit_code, stdout, stderr)
    """
    if not args:
        return 0, "vendo mucho pero no se si gano plata", None

    first_arg = args[0]
    if first_arg.startswith("-"):
        if first_arg in RESERVED_COMMANDS:
            return 1, "", f"COMANDO_NO_IMPLEMENTADO: {first_arg}"
        return 1, "", f"COMANDO_NO_PERMITIDO: {first_arg}"

    return 0, " ".join(args).strip(), None


def _ensure_repo_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    conversa_dir = repo_root / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))


def _pymia_reply(text: str, tenant_id: str, user_id: str) -> str:
    _ensure_repo_on_path()
    from pymia.smartpyme.anamnesis_fsm_integration import (
        AnamnesisTurnInput,
        run_anamnesis_turn,
    )
    from pymia.smartpyme.supermemory_recall_integration import (
        RecallBeforeReplyInput,
        run_recall_before_reply,
    )

    session_id = _session_id(tenant_id, user_id)
    previous_context = _PROGRESSIVE_CONTEXT_BY_SESSION.get(session_id)
    turn_index = _turn_index_from_context(previous_context)
    message_for_anamnesis = text
    try:
        recall_output = run_recall_before_reply(
            RecallBeforeReplyInput(
                tenant_id=tenant_id,
                session_key=session_id,
                user_message=text,
                turn_index=turn_index,
                phase=_phase_from_context(previous_context),
            ),
            client=_get_supermemory_recall_client(),
        )
        message_for_anamnesis = recall_output.augmented_message
    except Exception:
        # Fail-open: semantic memory must never block the conversation.
        message_for_anamnesis = text

    result = run_anamnesis_turn(
        AnamnesisTurnInput(
            tenant_id=tenant_id,
            message_text=message_for_anamnesis,
            session_id=session_id,
            previous_progressive_context=previous_context,
        )
    )
    if result.updated_progressive_context is not None:
        _PROGRESSIVE_CONTEXT_BY_SESSION[session_id] = result.updated_progressive_context
    return result.reply_text or ""


def _get_supermemory_recall_client():
    """Return optional Supermemory recall client.

    Fail-open by returning None when SUPERMEMORY_API_KEY is absent or client
    initialization fails. This keeps the conversational runtime usable without
    making external memory mandatory.
    """
    global _SUPERMEMORY_RECALL_CLIENT, _SUPERMEMORY_RECALL_INITIALIZED
    if _SUPERMEMORY_RECALL_INITIALIZED:
        return _SUPERMEMORY_RECALL_CLIENT
    _SUPERMEMORY_RECALL_INITIALIZED = True
    if not os.environ.get("SUPERMEMORY_API_KEY"):
        return None
    try:
        from pymia.smartpyme.supermemory_tenant_recall import (
            SupermemoryClientConfig,
            SupermemoryTenantRecallClient,
        )

        _SUPERMEMORY_RECALL_CLIENT = SupermemoryTenantRecallClient(
            SupermemoryClientConfig.from_env()
        )
    except Exception:
        _SUPERMEMORY_RECALL_CLIENT = None
    return _SUPERMEMORY_RECALL_CLIENT


def _turn_index_from_context(context: dict | None) -> int:
    if not isinstance(context, dict):
        return 0
    current = context.get("turn_index")
    if isinstance(current, int) and current >= 0:
        return current + 1
    fsm_state = context.get("fsm_state")
    if isinstance(fsm_state, dict):
        raw = fsm_state.get("turn_index")
        if isinstance(raw, int) and raw >= 0:
            return raw + 1
    return 0


def _phase_from_context(context: dict | None) -> str | None:
    if not isinstance(context, dict):
        return None
    phase = context.get("phase")
    if isinstance(phase, str) and phase:
        return phase
    fsm_state = context.get("fsm_state")
    if isinstance(fsm_state, dict):
        raw = fsm_state.get("phase")
        if isinstance(raw, str) and raw:
            return raw
    return None


def _session_id(tenant_id: str, user_id: str) -> str:
    return f"{tenant_id}/{user_id}"


def _new_text_event(text: str, tenant_id: str, user_id: str):
    from inbound_event import RawInboundEvent

    return RawInboundEvent.text(
        event_id=f"evt-{uuid4()}",
        tenant_id=tenant_id,
        user_id=user_id,
        text=text,
    )


def _register_text_intake(text: str, tenant_id: str, user_id: str) -> None:
    _ensure_repo_on_path()
    from intake_repository import DocumentIntakeRepository
    from primary_context_intake import (
        build_primary_context_record,
        persist_primary_context_record,
    )

    session_id = _session_id(tenant_id, user_id)
    preferred_path = Path(__file__).resolve().parent / ".intake_state"
    fallback_path = Path.home() / ".cache" / "pymia" / "conversa-intake-state"

    for base_path in (preferred_path, fallback_path):
        try:
            repo = DocumentIntakeRepository(base_path=base_path, stale_lock_seconds=60.0)
            state = repo.load(session_id=session_id)
            state.register(_new_text_event(text, tenant_id, user_id))
            repo.save(session_id=session_id, state=state)
            record = build_primary_context_record(tenant_id=tenant_id, message_text=text)
            persist_primary_context_record(
                record=record,
                tenant_id=tenant_id,
                user_id=user_id,
                base_path=base_path,
            )
            return
        except PermissionError:
            continue


def run_message(text: str, tenant_id: str = "telegram:42", user_id: str = "42") -> str:
    _register_text_intake(text, tenant_id, user_id)
    return _pymia_reply(text, tenant_id, user_id)


def route_from_operational_audit(text: str, operational_audit_result_payload: dict) -> str:
    """
    Routing conversacional disciplinado sobre OperationalAuditResult.

    Esta función vive en conversa-engine (runtime externo).
    No pasa metadata ni payload al kernel clínico.
    """
    from pymia.audit_result.models import OperationalAuditResult
    from operational_audit_router import route_operational_audit_message

    audit = OperationalAuditResult.model_validate(operational_audit_result_payload)
    decision = route_operational_audit_message(text, audit)
    return decision.reply_text


def _configure_cli_encoding() -> None:
    """Use UTF-8 for CLI output when the host stream supports reconfiguration."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    _configure_cli_encoding()
    exit_code, message, error = _cli_message_from_args(sys.argv[1:])
    if error is not None:
        print(error, file=sys.stderr)
        raise SystemExit(exit_code)
    print(run_message(message))
