from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_LOCAL = REPO_ROOT / ".env.local"


def _load_env_local() -> None:
    if not ENV_LOCAL.exists():
        return
    for raw_line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _load_conversa_main():
    module_path = REPO_ROOT / "conversa-engine" / "main.py"
    spec = importlib.util.spec_from_file_location(
        "conversa_engine_main_for_real_recall_smoke",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load conversa-engine/main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_supermemory(tenant_id: str, session_key: str) -> None:
    from pymia.smartpyme.supermemory_tenant_recall import (
        SupermemoryClientConfig,
        SupermemoryTenantRecallClient,
        TenantTurnSummary,
    )

    client = SupermemoryTenantRecallClient(SupermemoryClientConfig.from_env())
    summary = TenantTurnSummary(
        tenant_id=tenant_id,
        session_key=session_key,
        turn_index=0,
        summary=(
            "El dueño declaró que fabrica ropa y vende por Mercado Libre. "
            "Quiere entender si gana plata. Registro no computacional."
        ),
        phase="ANAMNESIS_TAXONOMIA",
        metadata={"smoke": "conversa_real_recall"},
    )
    client.save_tenant_turn_summary(summary)


def _looks_like_amnesia(reply: str) -> bool:
    lowered = reply.lower()
    markers = (
        "vendés productos, fabricás algo o prestás servicios",
        "vendes productos, fabricas algo o prestas servicios",
        "necesito entender tu negocio",
    )
    return any(marker in lowered for marker in markers)


def _sanitize_error_message(message: str) -> str:
    api_key = os.environ.get("SUPERMEMORY_API_KEY", "")
    sanitized = str(message)
    if api_key:
        sanitized = sanitized.replace(api_key, "***")
    sanitized = sanitized.replace("Bearer ", "Bearer ***")
    return sanitized[:500]


def main() -> int:
    _load_env_local()
    if not os.environ.get("SUPERMEMORY_API_KEY"):
        print("STATUS: FAIL")
        print("REASON: missing SUPERMEMORY_API_KEY")
        return 1

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    tenant_id = "smoke_tenant_conversa_real_recall"
    user_id = "user_conversa_real_recall"
    session_key = f"{tenant_id}/{user_id}"

    try:
        _seed_supermemory(tenant_id=tenant_id, session_key=session_key)
        time.sleep(5)

        conversa_main = _load_conversa_main()
        conversa_main._PROGRESSIVE_CONTEXT_BY_SESSION.clear()
        conversa_main._SUPERMEMORY_RECALL_CLIENT = None
        conversa_main._SUPERMEMORY_RECALL_INITIALIZED = False

        reply = conversa_main.run_message(
            RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        amnesia = _looks_like_amnesia(reply)
        print("STATUS: OK")
        print(f"AMNESIA: {'YES' if amnesia else 'NO'}")
        print(f"REPLY_CHARS: {len(reply)}")
        return 0 if not amnesia else 2
    except Exception as exc:  # noqa: BLE001 - smoke must report failure without traceback/secrets
        print("STATUS: FAIL")
        print(f"REASON: {type(exc).__name__}")
        print(f"DETAIL: {_sanitize_error_message(str(exc))}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
