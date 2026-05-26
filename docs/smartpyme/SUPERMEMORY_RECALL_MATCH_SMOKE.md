# SUPERMEMORY_RECALL_MATCH_SMOKE

## Objetivo

Validar localmente que Supermemory no solo acepta escritura y busqueda, sino que recupera una memoria recien guardada en tenant-scope.

## Script

```text
scripts/smoke_supermemory_recall_match_local.py
```

## Precondicion

`SUPERMEMORY_API_KEY` disponible en entorno o en `.env.local` en la raiz del repo.

## Ejecucion

```powershell
cd E:\BuenosPasos\smartbridge\PymIA
python scripts/smoke_supermemory_recall_match_local.py
```

## Flujo

1. Carga `SUPERMEMORY_API_KEY` desde entorno o `.env.local`.
2. Instancia `SupermemoryTenantRecallClient`.
3. Usa `tenant_id = "smoke_tenant_memory_match"`.
4. Guarda `TenantTurnSummary` no computacional.
5. Captura respuesta de save y extrae `id/status` si existe.
6. Si hay `id`, consulta `GET /v3/documents/{id}` hasta `done` o timeout 30s.
7. Ejecuta busqueda con query literal:
   - `fabrica ropa Mercado Libre gana plata`
   usando `POST https://api.supermemory.ai/v4/search` con:
   - `searchMode = hybrid`
   - `threshold = 0.3`
8. Imprime solo:
   - `STATUS: OK|FAIL`
   - `DOCUMENT_STATUS: <queued|processing|done|unknown|failed|error>`
   - `MEMORIES: <n>`
   - `MATCH: YES|NO`

## Regla de match

- `MATCH: YES` si `MEMORIES >= 1` con resultado que incluya
  `memory`, `chunk`, `content`, `text` o `summary`.
- `MATCH: NO` si `MEMORIES = 0`.

## Seguridad

- No imprime API key.
- No imprime payload completo ni contenido sensible.
- No promueve Supermemory a verdad operacional.

## Interpretacion

Caso ideal:

```text
STATUS: OK
DOCUMENT_STATUS: done
MEMORIES: >=1
MATCH: YES
```

Caso API reachable sin match confirmado:

```text
STATUS: OK
DOCUMENT_STATUS: queued|processing|done|unknown
MEMORIES: 0
MATCH: NO
```

Interpretar como: `API reachable but recall match not confirmed`.

## Nota

Smoke manual. No forma parte del `pytest` default.
