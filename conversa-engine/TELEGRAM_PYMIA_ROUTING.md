# Telegram -> PymIA routing validation

## Current target

Telegram is a user-facing channel for PymIA / SmartPyme first-contact operational conversation.

The user-visible answer must not expose internal routing, execution commands, adapters or architecture names.

## Contract

When a PyME owner sends an operational symptom, the final Telegram reply must:

- preserve PymIA's visible answer;
- avoid adding technical framing;
- avoid exposing internal terms;
- keep the answer short enough for Telegram;
- separate preliminary reading from confirmed diagnosis;
- ask for concrete missing evidence only.

## Forbidden user-visible terms

These terms are allowed in technical documentation but forbidden in the final Telegram response:

- kernel
- keywords
- pipeline
- Hermes
- runtime
- workflow
- job
- adapter
- gateway
- MCP

## Required replacements

If a generated response contains report-style headings, the final visible layer must normalize them:

```text
DIAGNÓSTICO OPERACIONAL -> LECTURA OPERATIVA PRELIMINAR
VEREDICTO -> SEÑAL PRINCIPAL
```

## Telegram mode

The default user-visible message should contain:

1. one synthesis;
2. up to four priorities;
3. one missing-evidence block if needed;
4. optional offer to expand detail.

Long report-style output belongs to an exportable report, not to the first Telegram response.
