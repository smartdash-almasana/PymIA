from __future__ import annotations

import os
import sys
from pathlib import Path
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pymia.smartpyme.supermemory_tenant_recall import (
    SupermemoryClientConfig,
    SupermemoryTenantRecallClient,
    TenantTurnSummary,
)


def _load_env_local(repo_root: Path) -> None:
    env_path = repo_root / ".env.local"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    _load_env_local(REPO_ROOT)

    api_key = os.environ.get("SUPERMEMORY_API_KEY", "").strip()
    if not api_key:
        print("STATUS: FAIL")
        print("MEMORIES: 0")
        return 1

    tenant_id = "smoke_tenant_memory"
    session_key = "smoke_local"
    turn_index = 0

    try:
        client = SupermemoryTenantRecallClient(
            config=SupermemoryClientConfig(api_key=api_key)
        )

        summary = TenantTurnSummary(
            tenant_id=tenant_id,
            session_key=session_key,
            turn_index=turn_index,
            summary=(
                "El dueno declaro que fabrica ropa y vende por Mercado Libre. "
                "Registro no computacional."
            ),
            phase="ANAMNESIS",
            source="smoke_local",
            metadata={
                "scope": "local_smoke",
                "non_operational_truth": True,
            },
        )

        client.save_tenant_turn_summary(summary)
        recalled = client.recall_tenant_context(
            tenant_id=tenant_id,
            query=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
            limit=5,
        )

        print("STATUS: OK")
        print(f"MEMORIES: {len(recalled.memories)}")
        return 0
    except Exception:
        print("STATUS: FAIL")
        print("MEMORIES: 0")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
