# SERVICE_1_ACCOUNTING_RUNTIME_AUTHORIZATION_MATRIX_V1

VEREDICT:

```text
SERVICE_1_ACCOUNTING_RUNTIME_AUTHORIZATION_MATRIX_V1: IMPLEMENTED_GOVERNANCE_MATRIX
```

PURPOSE:

```text
Definir qué tipos de runtime contable podrían autorizarse en Servicio 1 y bajo qué condiciones.
Este documento no autoriza ejecución real.
Este documento no implementa runtime.
Este documento sólo fija matriz de gobierno para futuros bloques.
```

PREVIOUS_CHAIN:

```text
SERVICE_1_ACCOUNTING_CONTRACTS_V1
SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1
SERVICE_1_MERCADO_PAGO_RECONCILIATION_CONTRACT_V1
SERVICE_1_INVOICE_COLLECTION_MATCHING_CONTRACT_V1
SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1
SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1
SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_CLOSURE_V1
SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_INDEX_V1
```

GLOBAL_DEFAULT:

```text
runtime_authorized=false
```

REASON:

```text
La familia contable actual es contractual.
No lee archivos reales.
No matchea movimientos reales.
No calcula diferencias reales.
No produce asientos.
No certifica exactitud fiscal.
No genera papeles finales.
```

LEVELS:

```text
BLOCKED
CONTRACT_ONLY
SANDBOX_DIAGNOSTIC_ALLOWED
HUMAN_REVIEW_REQUIRED
RUNTIME_ALLOWED_FUTURE
PRODUCTION_FORBIDDEN
```

MATRIX:

| Capability | Current Level | Future Candidate Runtime | Required Before Runtime | Forbidden Claims |
|---|---|---|---|---|
| bank_reconciliation_basic | CONTRACT_ONLY | deterministic_bank_matching_sandbox | field mapping, date normalization, amount normalization, duplicate policy, human review | conciliación cerrada, saldo correcto, auditoría |
| mercado_pago_reconciliation_basic | CONTRACT_ONLY | deterministic_payment_platform_matching_sandbox | report schema, fees/taxes handling policy, gross/net policy, human review | cobros liquidados confirmados, exactitud fiscal, saldo cerrado |
| invoice_collection_matching_basic | CONTRACT_ONLY | deterministic_invoice_collection_matching_sandbox | invoice id policy, customer normalization, partial payment policy, human review | cobranza aplicada definitiva, deuda exacta, imputación contable final |
| supplier_purchase_review_basic | CONTRACT_ONLY | deterministic_supplier_purchase_review_sandbox | supplier identity policy, document number policy, tax field policy, human review | comprobante válido, impuesto correcto, deuda exigible |
| accounting_workpaper_basic | CONTRACT_ONLY | workpaper_draft_builder_sandbox | template contract, evidence manifest, traceability policy, human review | papel certificado, auditoría aprobada, evidencia suficiente final |

CURRENTLY ALLOWED ACTIONS:

```text
build_contract_status
list_required_sources
list_required_fields
list_missing_sources
list_missing_fields
build_next_allowed_action
build_owner_summary
build_delivery_input
export_contractual_xlsx_payload
```

CURRENTLY FORBIDDEN ACTIONS:

```text
read_bank_statement
read_payment_platform_report
read_invoice_register
read_collection_register
read_supplier_register
read_purchase_register
read_supporting_evidence
execute_real_matching
calculate_real_differences
classify_real_movements
post_accounting_entries
generate_final_workpaper
certify_reconciliation
certify_tax_accuracy
call_bank_api
call_payment_platform_api
```

MINIMUM RUNTIME OPENING CONDITIONS:

```text
1. Dedicated runtime contract per capability.
2. Fixture-based tests before any real file processing.
3. Explicit input schema.
4. Explicit output schema.
5. Deterministic transformation only.
6. No external API.
7. No production claims.
8. runtime_authorized remains false until FSM/event explicitly grants authorization.
9. Human review remains mandatory for owner-facing accounting interpretation.
10. XLSX output must identify itself as draft/diagnostic unless separately approved.
```

FSM RELATION:

```text
Accounting contracts currently stop at CONTRACT_ONLY.
They must not jump to PROCESSING_AUTHORIZED.
PROCESSING_AUTHORIZED requires a future authorization event and a dedicated runtime contract.
```

RESERVED EVENTS:

```text
ACCOUNTING_RUNTIME_REQUESTED
ACCOUNTING_RUNTIME_SCOPE_VALIDATED
ACCOUNTING_RUNTIME_FIXTURES_VALIDATED
ACCOUNTING_RUNTIME_HUMAN_APPROVED
ACCOUNTING_RUNTIME_AUTHORIZATION_GRANTED
ACCOUNTING_RUNTIME_AUTHORIZATION_REVOKED
```

BLOCKING STATES:

```text
BLOCKED_ACCOUNTING_RUNTIME_NOT_AUTHORIZED
BLOCKED_ACCOUNTING_SCOPE_TOO_BROAD
BLOCKED_ACCOUNTING_EVIDENCE_INSUFFICIENT
BLOCKED_ACCOUNTING_FORBIDDEN_CLAIM
BLOCKED_ACCOUNTING_HUMAN_REVIEW_REQUIRED
BLOCKED_ACCOUNTING_EXTERNAL_INTEGRATION_FORBIDDEN
BLOCKED_ACCOUNTING_PRODUCTION_USE_FORBIDDEN
```

ANTI_DRIFT RULES:

```text
No runtime by implication.
No runtime because a contract is READY_FOR_REVIEW.
No runtime because XLSX delivery exists.
No runtime because tests pass on contracts.
No runtime because a file name resembles an accounting source.
No runtime without explicit authorization block.
```

NEXT ALLOWED BLOCKS:

```text
SERVICE_1_ACCOUNTING_RUNTIME_AUTHORIZATION_CONTRACT_V1
SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1
SERVICE_1_ACCOUNTING_HUMAN_REVIEW_GATE_V1
```

NOT ALLOWED NEXT:

```text
SERVICE_1_BANK_RECONCILIATION_RUNTIME_V1
SERVICE_1_MERCADO_PAGO_RUNTIME_V1
SERVICE_1_ACCOUNTING_AUTOMATION_V1
SERVICE_1_WORKPAPER_FINAL_GENERATOR_V1
```

VERIFICATION:

```text
Documentation/governance only.
No runtime files modified.
No tests required beyond repo status unless paired with code in future block.
```

COMMIT_READY:

```text
YES
```
