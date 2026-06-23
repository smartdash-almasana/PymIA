# SERVICE_1_ACCOUNTING_SANDBOX_PATTERN_V1

VEREDICT:

```text
ACCOUNTING_SANDBOX_PATTERN_V1: CAPTURED
```

PURPOSE:

```text
Capturar el patrón descubierto durante la cadena bancaria sandbox.
Evitar repetir mecánicamente microcapas por cada familia contable.
Definir qué piezas son genéricas, cuáles son específicas y cuándo corresponde abrir una nueva capa.
```

SOURCE_CHAIN:

```text
bank_reconciliation_contract_v1
accounting_human_review_gate_v1
bank_reconciliation_sandbox_fixture_model_v1
bank_reconciliation_sandbox_fixture_handoff_v1
bank_reconciliation_sandbox_contract_v1
bank_reconciliation_sandbox_review_packet_v1
service_1_xlsx_delivery_v1
```

PATTERN:

```text
1. Base contract
2. Human gate
3. Fixture model
4. Handoff closure
5. Sandbox permission contract
6. Review packet
7. Generic delivery
```

CANONICAL_FLOW:

```text
base_contract + human_gate + fixture_model
  -> handoff_closure
  -> sandbox_permission_contract
  -> review_packet
  -> generic_delivery
```

CORE_RULE:

```text
No abrir una nueva capa si no agrega una frontera irreversible.
```

IRREVERSIBLE_BOUNDARY_CRITERIA:

```text
A layer is justified only if it does at least one of these:
- validates a new input shape
- blocks a new unsafe path
- converts one contract shape into another explicit handoff
- produces a new owner/operator decision artifact
- creates a stable reusable boundary for another family
```

MICROCYCLE_WARNING:

```text
A layer is probably a microcycle if it only renames, reformats, wraps, or re-expresses the previous output without new validation, blocking, handoff, or decision value.
```

GENERIC_COMPONENTS:

```text
Human gate:
  accounting_human_review_gate_v1 is generic enough for accounting sandbox families.

Generic delivery:
  service_1_xlsx_delivery_v1 is already the preferred output adapter.

Review packet concept:
  The review packet shape may become generic if Mercado Pago or other families need the same owner/operator readiness summary.
```

FAMILY_SPECIFIC_COMPONENTS:

```text
Base contract:
  Usually family-specific because each accounting family has different sources, fields and forbidden claims.

Fixture model:
  Family-specific only when input fixtures have materially different structure.

Handoff closure:
  Should be family-specific only when handoff refs or upstream closure conditions differ.

Sandbox permission contract:
  Should be family-specific only when readiness rules differ from the bank case.
```

REPLICATION_RULES:

```text
Do not copy the full bank chain automatically.
For each new accounting family, first classify:
- reuse existing human gate? usually yes
- reuse generic delivery? yes
- need family base contract? usually yes
- need family fixture model? maybe
- need family handoff? maybe
- need family sandbox contract? maybe
- need family review packet? maybe generic later
```

MERCADO_PAGO_IMPLICATION:

```text
Mercado Pago should not start by copying every bank sandbox module.
First audit whether Mercado Pago needs:
- a distinct fixture model for liquidations, fees, taxes, refunds and settlement dates
- a distinct handoff closure
- a distinct sandbox permission contract
- or only a base contract plus a generic review packet
```

STOP_RULES:

```text
Stop a family chain when it reaches review_packet + generic_delivery compatibility.
Do not add a renderer unless there is a concrete owner-facing artifact that generic delivery cannot express.
Do not add matching, scoring, balance claims, entries, APIs, LLM or FSM inside this pattern.
```

MATURITY_LABELS:

```text
CONTRACT_ONLY:
  scope and required inputs are defined, no sandbox path.

SANDBOX_BOUNDARY:
  fixture or sandbox permission path exists, but no review packet.

SANDBOX_REVIEW_READY:
  review packet exists and can be delivered through generic delivery.

PRODUCTION_RUNTIME:
  not authorized in Service 1 accounting sandbox pattern.
```

BANK_CHAIN_MATURITY:

```text
Bank reconciliation sandbox chain = SANDBOX_REVIEW_READY / NOT_PRODUCTION
```

PROHIBITED_CLAIMS:

```text
No confirmed reconciliation.
No final balance.
No final difference.
No accounting entries.
No fiscal certification.
No live bank execution.
No Mercado Pago execution.
No automated accounting decision.
```

NEXT_SAFE_ACTIONS:

```text
1. Audit Mercado Pago accounting contract against this pattern.
2. Decide reuse vs family-specific fixture model.
3. Avoid renderer unless generic delivery is insufficient.
```

COMMIT_READY:

```text
YES
```
