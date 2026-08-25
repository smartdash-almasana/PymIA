# Servicio 1 — R10B6A ChatGPT Audit V1

Date: 2026-08-24

Verdict: PASS

Physical checks:
- Evidence file exists and records 56 productive top-level identity/provenance alias reads before migration and 0 after.
- Scoped aliases remain emitted by the canonical ingestion envelope; R10B6A did not delete them.
- Direct productive reads `ingestion_output.get("case_id")` and `ingestion_output.get("source_file_ref")` are absent under `pymia/smartpyme`.
- Canonical locations are `workbook_context` for identity and `provenance` for source/file/sheet provenance.
- Semantic/data aliases were explicitly out of scope.

Observed test evidence from Codex: 218 passed / 0 failed, plus F7 guard 16 passed / 0 failed. No independent rerun performed in this audit because the bounded suite is large and the physical/static evidence is sufficient for authorization of the next slice.

Next allowed action: R10B6B may remove only the now-zero-consumer identity/provenance aliases; semantic/data aliases remain out of scope.
