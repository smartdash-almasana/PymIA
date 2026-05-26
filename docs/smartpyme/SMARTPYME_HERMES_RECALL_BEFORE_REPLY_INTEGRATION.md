# SMARTPYME_HERMES_RECALL_BEFORE_REPLY_INTEGRATION

## Estado

Candidato implementativo aislado.

## Frente

SMARTPYME_HERMES_RECALL_BEFORE_REPLY_INTEGRATION

## Propósito

Integrar Supermemory tenant recall antes de generar respuesta conversacional, sin convertir memoria en verdad operacional y sin bloquear el flujo si Supermemory no está disponible.

## Archivos

```text
pymia/smartpyme/supermemory_recall_integration.py
pymia/smartpyme/supermemory_tenant_recall.py
tests/smartpyme/test_supermemory_recall_integration.py
tests/smartpyme/test_supermemory_tenant_recall.py
conversa-engine/main.py
```

## Comportamiento

En `conversa-engine/main.py`, antes de llamar a `run_anamnesis_turn`:

1. Se resuelve `session_id = tenant_id/user_id`.
2. Se calcula `turn_index` desde `previous_progressive_context` si existe.
3. Se intenta cargar un cliente Supermemory solo si existe `SUPERMEMORY_API_KEY`.
4. Se llama a `run_recall_before_reply`.
5. Si hay contexto recuperado, se antepone como contexto conversacional explícitamente no soberano.
6. Si Supermemory falla, el flujo continúa con el mensaje original.

## Fail-open

La memoria semántica no debe bloquear conversación.

```text
Supermemory disponible → recall tenant-scoped.
Supermemory ausente/fallido → mensaje original.
```

## No autoridad operacional

El preámbulo de memoria se marca como:

```text
Contexto conversacional recuperado del mismo tenant (no es verdad operacional confirmada)
```

## Validación

```bash
python -m pytest tests/smartpyme/test_supermemory_tenant_recall.py tests/smartpyme/test_supermemory_recall_integration.py -q
```

Resultado local reportado: 16 passed in 0.33s.

## Criterio PASS

```text
- Sin cliente Supermemory, la integración es no-op.
- Con cliente fake, recupera contexto del mismo tenant.
- Guarda resumen seguro no diagnóstico.
- El contexto recuperado queda marcado como no verdad operacional.
- No hace llamadas reales de red en tests.
- Supermemory no bloquea respuesta si falla.
```

## No autorizado

```text
- Telegram productivo.
- Cambios en kernel PymIA.
- Supermemory como CMF.
- Supermemory como fuente de readiness.
- Supermemory como fuente de hallazgos confirmados.
```
