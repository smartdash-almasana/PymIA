from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def run_message(text: str, tenant_id: str = "telegram:42", user_id: str = "42") -> str:
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


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]).strip() or "vendo mucho pero no se si gano plata"
    print(run_message(message))
