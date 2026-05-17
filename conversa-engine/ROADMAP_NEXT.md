# conversa-engine next roadmap

## Next operational milestone

Build the first useful loop:

```text
symptom -> anamnesis -> document intake -> evidence map -> simple report
```

## Cycle 0: symptom-pathology catalog

Create a deterministic static catalog owned by `conversa-engine`:

```text
owner pain -> operational symptom -> candidate pathologies -> investigable hypothesis -> required variables -> required evidence
```

Implemented first entry:

```text
sospecha_perdida_margen
```

## Cycle 1: structured anamnesis

Create a lightweight state machine owned by `conversa-engine`:

```text
NEW_SYMPTOM
ASK_MINIMUM_CONTEXT
WAITING_FOR_DOCUMENTS
EVIDENCE_RECEIVED
REPORT_READY
```

Do not store this state inside `pymia/`.

## Cycle 2: document intake

Accept uploaded files from the external channel and save them under a tenant/session folder.

Target folder shape:

```text
conversa-engine/data/<tenant_id>/<session_id>/incoming/
```

Ignored by git.

## Cycle 3: evidence map

Extract minimal structured facts from documents:

```text
sales
costs
cash movements
price list
stock
debts
```

## Cycle 4: report builder

Generate a concise report using PymIA output plus extracted evidence.

## Non-goals

- Do not build accounting software.
- Do not build full OCR pipeline in cycle 1.
- Do not contaminate `pymia/` with Telegram, Hermes Agent, providers or file ingestion runtime.
