from __future__ import annotations

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
    from pymia.hermes.adapter import HermesAdapter, HermesInput

    session_id = _session_id(tenant_id, user_id)
    adapter = HermesAdapter()
    result = adapter.handle(
        HermesInput(
            tenant_id=tenant_id,
            channel="telegram",
            message_text=text,
            metadata={"telegram_user_id": user_id},
            previous_progressive_context=_PROGRESSIVE_CONTEXT_BY_SESSION.get(session_id),
        )
    )
    if result.payload.progressive_context is not None:
        _PROGRESSIVE_CONTEXT_BY_SESSION[session_id] = result.payload.progressive_context
    return result.reply_text or ""


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


if __name__ == "__main__":
    exit_code, message, error = _cli_message_from_args(sys.argv[1:])
    if error is not None:
        print(error, file=sys.stderr)
        raise SystemExit(exit_code)
    print(run_message(message))
