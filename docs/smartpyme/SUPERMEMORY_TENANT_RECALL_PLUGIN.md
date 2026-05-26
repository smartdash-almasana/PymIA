# SUPERMEMORY_TENANT_RECALL_PLUGIN

## Estado

Candidato implementativo aislado.

## Frente

SMARTPYME_SUPERMEMORY_TENANT_RECALL_PLUGIN

## Propósito

Implementar una frontera mínima, testeable y tenant-scoped para usar Supermemory como memoria semántica conversacional diferida de Hermes.

Este frente resuelve continuidad conversacional entre interacciones del mismo tenant sin convertir memoria en verdad operacional.

## No autoriza

- Telegram productivo.
- Ejecución automática de kernel.
- Cambios en PymIA kernel.
- Nuevas MCP tools productivas.
- Uso de Supermemory como CMF/Supabase.
- Uso de Supermemory como fuente de hallazgos confirmados.

## Módulo

```text
pymia/smartpyme/supermemory_tenant_recall.py
```

## Tests

```text
tests/smartpyme/test_supermemory_tenant_recall.py
```

## Contratos principales

### `TenantTurnSummary`

Resumen conversacional seguro a persistir.

Campos:

```text
tenant_id
session_key
turn_index
summary
phase
source
metadata
```

Invariantes:

```text
- tenant_id obligatorio.
- session_key obligatorio.
- turn_index >= 0.
- summary no puede contener marcadores de verdad operacional confirmada.
- metadata debe ser plana: str, int, float o bool.
```

### `SupermemoryTenantRecallClient`

Cliente mínimo con transporte inyectable.

Funciones:

```text
save_tenant_turn_summary(summary)
recall_tenant_context(tenant_id, query, limit)
```

## Scope tenant

Toda escritura y búsqueda usa:

```text
containerTag = tenant:{tenant_id}
```

Toda escritura usa:

```text
customId = turn:{tenant_id}:{session_key}:{turn_index}
```

## Seguridad mnémica

Bloquea summaries que contengan marcadores como:

```text
gate_verdict=PASS
readiness PASS
hallazgo confirmado
diagnóstico confirmado
margen real
output_ref
delivery_package_id
excel crudo
```

## Regla de autoridad

```text
Supermemory recuerda contexto conversacional.
Supabase CMF gobierna estado operacional.
PymIA confirma verdad computacional.
```

## Validación

```bash
python -m pytest tests/smartpyme/test_supermemory_tenant_recall.py -q
```

Resultado local reportado:

```text
tests/smartpyme/test_supermemory_tenant_recall.py .......... [100%]
10 passed in 0.39s
```

## Criterio PASS

```text
- No permite operaciones sin tenant_id.
- Siempre usa containerTag tenant-scoped.
- customId es determinístico por tenant/session/turn.
- No guarda diagnósticos ni hallazgos no gateados.
- No hace llamadas reales de red en tests.
- La API key se lee desde entorno y no se imprime ni se loguea.
```
