# conversa-engine

Interlocutor conversacional de PymIA.

Regla arquitectónica:
- conversa-engine conversa.
- PymIA computa.

Flujo:
canal externo -> conversa-engine -> pymia.hermes.adapter.HermesAdapter -> result.reply_text -> usuario.

Frontera auditada:
- Hermes/conversa-engine puede consumir `OperationalAuditResult` para routing conversacional.
- Hermes no recibe Excel ni tablas crudas.
- Hermes no recalcula patologías ni fórmulas.
- PymIA computa y entrega resultado auditado.

## Setup Windows (local)

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install hermes-agent==0.14
```

## Setup Linux (VM GCP)

```bash
cd /opt/smartpyme-factory/repos/PymIA/conversa-engine
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install hermes-agent==0.14
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

## Routing sobre OperationalAuditResult

Uso opcional para seguimiento conversacional:
- `conversa-engine/operational_audit_router.py`
- `conversa-engine/main.py::route_from_operational_audit(...)`

Inputs permitidos para routing:
- `pathology_routing_summary`
- `open_audit_threads`
- `narrative_payload.allowed_messages`
- `narrative_payload.forbidden_inferences`

Reglas:
- no pasar metadata al kernel clínico;
- no inyectar `tables`, `raw_tables`, `normalized_tables`, `kernel_output`;
- Hermes conversa y enruta; PymIA computa.
