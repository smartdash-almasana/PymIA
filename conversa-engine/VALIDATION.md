# conversa-engine validation

## Current validation

- PymIA test suite: `61 passed`.
- Forbidden architecture terms: clean.
- Docs index audit: OK.
- `conversa-engine` imports PymIA through `pymia.hermes.adapter.HermesAdapter`.

## Smoke command

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
.\.venv\Scripts\python smoke_test.py
```

Expected result:

```text
SMOKE_OK: True
```
