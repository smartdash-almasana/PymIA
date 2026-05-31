from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from evidence_router import IngestionRoute
from inbound_event import RawInboundEvent
from intake_state import DocumentIntakeState
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


def main() -> None:
    state = DocumentIntakeState()
    state.require_evidence("facturas_proveedor")

    text_event = RawInboundEvent.text(
        event_id="evt-text-001",
        tenant_id="telegram:42",
        user_id="42",
        text=RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
    )
    assert text_event.get_ingestion_route() == IngestionRoute.NARRATIVE
    state.register(text_event)

    file_event = RawInboundEvent.file(
        event_id="evt-file-001",
        tenant_id="telegram:42",
        user_id="42",
        file_name="facturas.pdf",
        mime_type="application/pdf",
        expected_schema="invoice_v1",
        entropy_level=0.1,
    )
    assert file_event.get_ingestion_route() == IngestionRoute.BEM_AI
    state.register(file_event)

    state.resolve_evidence("facturas_proveedor")
    assert not state.missing_evidence
    assert state.received_events == ["evt-text-001", "evt-file-001"]
    assert state.received_files == ["facturas.pdf"]

    print("INTAKE_SMOKE_OK:", True)


if __name__ == "__main__":
    main()

