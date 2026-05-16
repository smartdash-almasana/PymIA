# conversa-engine contract

## Role

`conversa-engine` is the conversational boundary for PymIA.

## Rule

```text
conversa-engine conversa.
PymIA computa.
```

## Integration path

```text
external channel
-> conversa-engine
-> pymia.hermes.adapter.HermesAdapter
-> result.reply_text
-> user
```

## Constraints

- `conversa-engine` may own channel/provider/runtime dependencies.
- `pymia/` must remain free of Telegram, provider SDKs, LangGraph, SmartPyme, factory and external Hermes Agent runtime dependencies.
- PymIA remains the operational computation system.

## Local smoke

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
.\.venv\Scripts\python smoke_test.py
```
