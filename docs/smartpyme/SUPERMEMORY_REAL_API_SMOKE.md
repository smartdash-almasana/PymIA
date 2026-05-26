# SUPERMEMORY_REAL_API_SMOKE

## Objetivo

Validar en entorno local que Supermemory real funciona con alcance tenant-scoped para SmartPyme/Hermes sin usar VM ni Telegram productivo.

## Script

```text
scripts/smoke_supermemory_recall_local.py
```

## Precondición

`SUPERMEMORY_API_KEY` disponible en entorno o en `.env.local` en la raiz del repo.

## Ejecucion

```powershell
cd E:\BuenosPasos\smartbridge\PymIA
python scripts/smoke_supermemory_recall_local.py
```

## Flujo del smoke

1. Carga `SUPERMEMORY_API_KEY` desde entorno y, si existe, desde `.env.local`.
2. Instancia `SupermemoryTenantRecallClient`.
3. Guarda un `TenantTurnSummary` tenant-scoped para:
   - `tenant_id = "smoke_tenant_memory"`
   - `containerTag = tenant:smoke_tenant_memory`
   - `customId = turn:smoke_tenant_memory:smoke_local:0`
4. Ejecuta `recall_tenant_context` con query:
   - `"no se si gano plata"`
5. Imprime solo:
   - `STATUS: OK|FAIL`
   - `MEMORIES: <cantidad>`

## Seguridad

- No imprime API key.
- No imprime payload completo ni contenido sensible.
- No promueve Supermemory a verdad operacional.

## Criterio PASS

```text
- STATUS: OK
- MEMORIES: N (N >= 0)
```

`OK` confirma que save + recall responden para el `containerTag` tenant-scoped.

## Nota

Este smoke es manual y no forma parte del `pytest` default.
