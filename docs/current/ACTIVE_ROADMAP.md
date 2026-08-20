# Active Roadmap — Servicio 1

**Fecha de corte:** 2026-08-19
**Autoridad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Estado

```text
F0_F13: CLOSED_COMMITTED
RC1: CLOSED_COMMITTED_FROZEN
RC2: CLOSED_COMMITTED_FROZEN
RC3: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
RC4: CLOSED_BY_DOCUMENTATION_SYNC
SERVICE_1_RELEASE_CANDIDATE_ACCEPTED: NO
```

No existe un frente productivo paralelo autorizado.

## Objetivo actual

Cerrar Servicio 1 como release candidate real sin crear nueva arquitectura ni nuevas capacidades por inercia.

La tarea ya no es inventar cómo analizar Excel. La tarea es congelar el runtime actual, sincronizar autoridad documental, desplegar el SHA exacto y demostrar el journey completo online.

## Secuencia obligatoria vigente

```text
RC1  raíz productiva única                  CLOSED
RC2  limpiar estado stale                   CLOSED
RC3  reentrada durable de ResultSets        CLOSED
SEC   hardening tenant/session              CLOSED
RC4  sincronización documental              CLOSED
RC5  deploy exacto + LLM externo real       PENDING
RC6  acceptance online cafeteria            PENDING
RC7  reentry online después de restart      PENDING
FINAL full suite + production smoke         PENDING
```

No avanzar declarativamente un gate que no tenga evidencia observada.

## RC3 — condición de cierre

RC3 sólo queda cerrado cuando el commit temático contenga exclusivamente su código/test autorizado y se repita el freeze post-commit.

Evidencia de implementación observada:

```text
TENANT_RESULTSET_LISTING: PASS
MEMORY_RECORD_SELECTION: PASS
EXACT_RECORD_LOAD: PASS
RESULTSET_INTEGRITY_REVALIDATION: PASS
TENANT_ISOLATION: PASS
RESTART_REENTRY_SIMULATION: PASS
DIGEST_EQUIVALENCE: PASS
NO_RECALCULATION: PASS
NO_LLM_ON_REENTRY: PASS
```

## RC4 — alcance

Actualizar sólo verdad documental/test contractual obsoleta:

```text
README.md
SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
SERVICE_1_STATUS.md
ACTIVE_ROADMAP.md
SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md
SERVICE_1_OPERABILITY_PACKET.md cuando corresponda
PYMIA_FIVE_BRAINS_AND_COHERENCE_SOVEREIGNTY_V1.md cuando corresponda
tests que congelen literales históricos ya no vigentes
```

RC4 no cambia matemática, semántica, computabilidad, persistencia ni runtime.

## RC5 — deploy y LLM real

Precondiciones:

```text
RC3_COMMITTED_FROZEN
RC4_COMMITTED_FROZEN
FULL_SUITE_CURRENT_RC = PASS
```

Gate:

```text
DEPLOYED_SHA == COMMITTED_SHA
EXTERNAL_LLM_PROVIDER_ACTIVE = PASS
LLM_COLUMN_INTERPRETATION = PASS
OWNER_CORROBORATION = PASS
LLM_MATH = 0
LLM_RUNTIME_AUTHORITY = 0
```

## RC6 — cafetería online

Desde navegador y con `prueba_excels/cafeteria_abc.xlsx`:

```text
login
→ upload
→ lectura de todas las hojas
→ interpretación de columnas
→ confirmación del dueño
→ discovery dinámico
→ análisis seleccionados
→ product root canónico
→ ResultSet
→ F13 persist
→ resultado web
```

Debe ejecutar los análisis computables y bloquear `catalog_price_variance_by_product` mientras no exista `list_price` gobernado.

## RC7 — memoria online

Después de análisis online:

```text
cerrar sesión / reiniciar servicio cuando corresponda
→ volver a autenticar
→ Mis análisis
→ abrir memory_record_id
→ mismo ResultSet/digest
```

Gate:

```text
F13_PERSISTED = PASS
REENTRY_AFTER_REAL_RESTART = PASS
SAME_RESULTSET_DIGEST = PASS
TENANT_ISOLATION = PASS
NO_RECALCULATION = PASS
```

## Gate final

```text
ONE_CANONICAL_PRODUCT_ROOT = PASS
NO_SECOND_XLSX_PARSER = PASS
NO_PARALLEL_PRODUCTIVE_PIPELINE = PASS
NO_SECOND_MATH_AUTHORITY = PASS
P6/P7/P8 = PASS
F7/F8/F9/F10/F12/F13 = PASS
LLM_MATH = 0
LLM_RUNTIME_AUTHORITY = 0
CAFETERIA_ONLINE = PASS
F13_REENTRY_ONLINE = PASS
FULL_SUITE_CURRENT_RC = PASS
PRODUCTION_SMOKE_CURRENT_RC = PASS
```

Sólo entonces:

```text
SERVICE_1_RELEASE_CANDIDATE_ACCEPTED
```

## Congelamiento

Hasta ese cierre:

```text
NO_F14
NO_SECOND_ENGINE
NO_SECOND_PARSER
NO_PARALLEL_PRODUCT_ROOT
NO_NEW_RUBRO_HARDCODE
NO_CAFETERIA_HARDCODE
NO_LLM_MATH
NO_UNGOVERNED_PRODUCT_EXPANSION
```

## Regla de trabajo

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
```
