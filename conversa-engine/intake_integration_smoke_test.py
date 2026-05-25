from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pathlib import Path
from tempfile import TemporaryDirectory

from inbound_event import RawInboundEvent
from intake_repository import DocumentIntakeRepository
from intake_state import DocumentIntakeState
from evidence_router import IngestionRoute


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        repo = DocumentIntakeRepository(base_path=Path(tmp_dir), stale_lock_seconds=1.0)
        session_id = "telegram:42/42"
        state = repo.load(session_id=session_id)

        text_event = RawInboundEvent.text(
            event_id="evt-integration-text-001",
            tenant_id="telegram:42",
            user_id="42",
            text="vendo mucho pero no sé si gano plata",
        )
        assert text_event.get_ingestion_route() == IngestionRoute.NARRATIVE
        state.register(text_event)
        state.require_evidence("facturas_proveedor")
        repo.save(session_id=session_id, state=state)

        reloaded = repo.load(session_id=session_id)
        assert reloaded.received_events == ["evt-integration-text-001"]
        assert reloaded.missing_evidence == ["facturas_proveedor"]

    print("INTAKE_INTEGRATION_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
