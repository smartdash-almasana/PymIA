# INVOICE_COLLECTION_MATCHING_SANDBOX_COMPLETION_SLICE_V1

## Status

```text
IMPLEMENTED_SANDBOX_COMPLETION_SLICE
```

## Purpose

Close the first functional sandbox slice for Servicio 1 invoice/collection matching.

This slice converts the existing `invoice_collection_matching_basic` contract into a synthetic, reviewable output packet with:

```text
- deterministic sandbox fixture
- conservative matching rows
- XLSX review packet
- owner summary
- operator notes
- output hashes
- explicit human-review limits
```

It does not process real client files and does not authorize runtime accounting use.

## Files created

```text
PymIA-Live/pymia/smartpyme/invoice_collection_matching_sandbox_completion_slice_v1.py
PymIA-Live/tests/smartpyme/test_invoice_collection_matching_sandbox_completion_slice_v1.py
docs/producto/INVOICE_COLLECTION_MATCHING_SANDBOX_COMPLETION_SLICE_V1.md
```

## Upstream contract

```text
Contract module:
PymIA-Live/pymia/smartpyme/invoice_collection_matching_contract_v1.py

Contract test:
PymIA-Live/tests/smartpyme/test_invoice_collection_matching_contract_v1.py
```

Required sources:

```text
registro_facturas
registro_cobros
```

Required fields:

```text
fecha
cliente
numero_factura
importe
```

## Runtime posture

```text
synthetic_data: true
real_client_data: false
runtime_authorized: false
production_allowed: false
human_review_required: true
```

## Matching statuses

The slice uses only deterministic fixture-level matching:

```text
MATCHED_BY_INVOICE_NUMBER
PENDING_COLLECTION
UNMATCHED_COLLECTION
AMOUNT_DIFFERENCE_REVIEW
```

Rules:

```text
If numero_factura exists in invoice register and collection register, and importe is equal:
  MATCHED_BY_INVOICE_NUMBER

If invoice exists but no collection exists for the invoice number:
  PENDING_COLLECTION

If collection exists but no invoice exists for the invoice number:
  UNMATCHED_COLLECTION

If invoice and collection share invoice number but importe differs:
  AMOUNT_DIFFERENCE_REVIEW
```

## Synthetic fixture result

Current embedded fixture produces:

```text
MATCHED_BY_INVOICE_NUMBER: 1
PENDING_COLLECTION: 2
UNMATCHED_COLLECTION: 1
AMOUNT_DIFFERENCE_REVIEW: 1
matching_rows_count: 5
```

## Generated artifacts

The completion slice generates three reviewable files:

```text
invoice_collection_matching_sandbox_review_packet.xlsx
owner_summary_invoice_collection_matching_sandbox.txt
operator_notes_invoice_collection_matching_sandbox.txt
```

Each generated file is included in `output_files` and receives a SHA-256 hash in `output_hashes`.

## XLSX delivery

The XLSX packet is generated through the generic Servicio 1 XLSX delivery builder:

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
```

Capability reference inside the workbook:

```text
service_1_invoice_collection_matching_sandbox_review_packet_v1
```

Workbook sheets include:

```text
Resumen
Datos usados
Resultados
Faltantes
Limitaciones
Claims prohibidos
Notas técnicas
```

## Owner-facing limits

The owner summary must remain conservative:

```text
No confirma deuda final.
No confirma cobranza aplicada definitiva.
No certifica saldo de cliente.
No genera asientos contables.
No usa API ni archivos reales.
Requiere revisión humana contable antes de cualquier interpretación con cliente.
```

## Operator-facing limits

Operator notes explicitly state:

```text
Use as sandbox review packet only.
Do not treat as final invoice/collection matching.
No API was called.
No source files were read or parsed in this completion slice.
No Mercado Pago logic is included.
Human accounting review remains mandatory.
```

## Forbidden claims

This slice must not claim:

```text
Final debt confirmation.
Definitive collection application.
Certified customer balance.
Automatic journal entries.
Replacement of human accounting review.
Real-file processing.
API execution.
```

## Tests

Focal test:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pytest tests/smartpyme/test_invoice_collection_matching_sandbox_completion_slice_v1.py -q
```

Expected result:

```text
PASS — 9 passed
```

Recommended mini-suite:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pytest `
  tests/smartpyme/test_invoice_collection_matching_contract_v1.py `
  tests/smartpyme/test_invoice_collection_matching_sandbox_completion_slice_v1.py `
  tests/smartpyme/test_service_1_xlsx_delivery_v1.py `
  tests/smartpyme/test_accounting_human_review_gate_v1.py -q
```

## Non-goals

```text
No real client data.
No source-file parser.
No live invoice register ingestion.
No live collection register ingestion.
No Mercado Pago integration.
No API.
No automatic accounting imputation.
No definitive debt calculation.
No final collection application.
No tax/fiscal conclusion.
No Servicio 2 diagnosis.
```

## Maturity impact

Before this slice:

```text
Invoice / Collection Matching: CONTRACT_ONLY / ~48% maturity
```

After this slice:

```text
Invoice / Collection Matching: SANDBOX_REVIEW_PACKET_READY / ~68-72% maturity
```

Remaining blockers to real-client readiness:

```text
Need real anonymized fixture.
Need operator rehearsal.
Need field normalization policy.
Need partial-payment policy.
Need duplicate invoice-number policy.
Need multi-currency policy if applicable.
Need accountant review of matching semantics.
```

## Closeout verdict

```text
INVOICE_COLLECTION_MATCHING_SANDBOX_COMPLETION_SLICE_V1:
READY_FOR_TEST_EVIDENCE_AND_COMMIT
```
