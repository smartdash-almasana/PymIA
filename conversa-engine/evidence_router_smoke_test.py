from __future__ import annotations

from evidence_router import IngestionRoute, route_evidence


def main() -> None:
    assert route_evidence(
        evidence_id="pdf-001",
        file_extension=".pdf",
        mime_type="application/pdf",
        expected_schema="invoice_v1",
        entropy_level=0.1,
    ) == IngestionRoute.BEM_AI

    assert route_evidence(
        evidence_id="xlsx-chaos-001",
        file_extension=".xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        expected_schema="sales_v1",
        entropy_level=0.8,
    ) == IngestionRoute.BEM_AI

    assert route_evidence(
        evidence_id="xlsx-clean-001",
        file_extension=".xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        expected_schema="sales_v1",
        entropy_level=0.1,
    ) == IngestionRoute.INTERNAL_FACT

    assert route_evidence(
        evidence_id="claim-001",
        file_extension="",
        mime_type="text/plain",
        expected_schema="human_claim",
        entropy_level=0.0,
    ) == IngestionRoute.NARRATIVE

    print("EVIDENCE_ROUTER_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
