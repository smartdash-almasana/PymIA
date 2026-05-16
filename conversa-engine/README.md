# conversa-engine

Interlocutor conversacional de PymIA.

Regla arquitectónica:
- conversa-engine conversa.
- PymIA computa.

Flujo:
canal externo -> conversa-engine -> pymia.hermes.adapter.HermesAdapter -> result.reply_text -> usuario.

## Setup Windows (local)

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install hermes-agent
```

## Setup Linux (VM GCP)

```bash
cd /opt/smartpyme-factory/repos/PymIA/conversa-engine
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install hermes-agent
```

## Smoke test (Windows)

```powershell
.\.venv\Scripts\python.exe smoke_test.py
```

## Smoke test (Linux)

```bash
./.venv/bin/python smoke_test.py
```

## Ejecución mínima (Windows)

```powershell
.\.venv\Scripts\python.exe main.py "vendo mucho pero no se si gano plata"
```

## Ejecución mínima (Linux)

```bash
./.venv/bin/python main.py "vendo mucho pero no se si gano plata"
```
