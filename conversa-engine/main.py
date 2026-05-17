from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4


def _ensure_repo_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _pymia_reply(text: str, tenant_id: str, user_id: str) -> str:
    _ensure_repo_on_path()
    from pymia.hermes.adapter import HermesAdapter, HermesInput

    adapter = HermesAdapter()
    result = adapter.handle(
        HermesInput(
            tenant_id=tenant_id,
            channel="telegram",
            message_text=text,
            metadata={"telegram_user_id": user_id},
        )
    )
    return result.reply_text


def _catalog_contrast(text: str) -> str:
    from symptom_pathology_catalog import match_symptoms_from_owner_message

    matches = match_symptoms_from_owner_message(text)
    if not matches:
        return ""

    entry = matches[0]
    return "\n".join(
        [
            "",
            "---",
            "CONTRASTE CON CATÁLOGO PYME",
            "",
            f"Síntoma operativo: {entry.name}.",
            "",
            "Patologías candidatas, no confirmadas:",
            *[f"- {item}" for item in entry.candidate_pathologies],
            "",
            "Variables necesarias:",
            *[f"- {item}" for item in entry.required_variables],
            "",
            "Evidencia requerida:",
            *[f"- {item}" for item in entry.required_evidence],
            "",
            "Pregunta mayéutica mínima:",
            f"- {entry.mayeutic_questions[0]}",
            "",
            "Regla: estas patologías son hipótesis candidatas. No son hallazgos confirmados hasta contrastar evidencia.",
        ]
    )


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
    from intake_repository import DocumentIntakeRepository

    session_id = _session_id(tenant_id, user_id)
    preferred_path = Path(__file__).resolve().parent / ".intake_state"
    fallback_path = Path.home() / ".cache" / "pymia" / "conversa-intake-state"

    for base_path in (preferred_path, fallback_path):
        try:
            repo = DocumentIntakeRepository(base_path=base_path, stale_lock_seconds=60.0)
            state = repo.load(session_id=session_id)
            state.register(_new_text_event(text, tenant_id, user_id))
            repo.save(session_id=session_id, state=state)
            return
        except PermissionError:
            continue


def run_message(text: str, tenant_id: str = "telegram:42", user_id: str = "42") -> str:
    _register_text_intake(text, tenant_id, user_id)
    pymia = _pymia_reply(text, tenant_id, user_id)
    contrast = _catalog_contrast(text)
    if contrast:
        return f"{pymia}\n{contrast}"
    return pymia


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]).strip() or "vendo mucho pero no se si gano plata"
    print(run_message(message))
