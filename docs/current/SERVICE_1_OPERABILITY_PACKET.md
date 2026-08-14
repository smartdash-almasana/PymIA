# Servicio 1 — Operability Packet V1

**Fecha de corte:** 2026-08-14
**Estado:** `ACTIVE`

## 1. Autoridad operativa

```text
CLI:  python -m pymia.cli.service_1_product
WEB:  python -m pymia.smartpyme.service_1_assisted_web_v1
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

No crear otra entrada con autoridad productiva equivalente.

## 2. Producción

Target vigente:

```text
Google Cloud Run
web entrypoint: pymia.smartpyme.service_1_assisted_web_v1
identity/persistence: Supabase
```

El último corte desplegado obtuvo production smoke PASS el 2026-08-13.

El worktree actual SEM-1→SEM-9 no está desplegado. Antes de reemplazar el corte productivo vigente requiere full-suite, commit autorizado, deploy y smoke sobre el nuevo SHA.

## 3. Variables de producción

Requeridas por el runtime productivo:

```text
PYMIA_SUPABASE_URL
PYMIA_SUPABASE_PUBLISHABLE_KEY
PYMIA_SUPABASE_SERVICE_ROLE_KEY
```

Smoke:

```text
PYMIA_PRODUCTION_BASE_URL
PYMIA_SMOKE_EMAIL
PYMIA_SMOKE_PASSWORD
```

Nunca imprimir ni commitear valores secretos.

## 4. CLI compatibility surface

La CLI oficial sigue soportando los modos gobernados existentes:

```text
python -m pymia.cli.service_1_product
  --xlsx <archivo.xlsx>
  --owner-column-answers <owner_column_answers.json>
  --tool-requests <tool_requests.json>
  --output-dir <output_dir>
  --result-json <result.json>
```

Para plan/capability gobernada se usa `--requested-capability` en lugar de `--tool-requests`. La reentrada semántica legacy de CLI usa `--semantic-owner-answers` y cada respuesta debe provenir de `allowed_option_ids`; no se acepta texto libre como binding canónico.

Esta compatibilidad CLI no crea una segunda raíz ni reemplaza el journey SEM-8 de Cobros/Margen en la web.

## 5. Local web

Arranque canónico:

```text
python -m pymia.smartpyme.service_1_assisted_web_v1 --host 127.0.0.1 --port 8766
```

Health local:

```text
GET /healthz
→ 200
→ {"status":"ok"}
```

En Cloud Run el smoke utiliza `GET /` conforme al contrato de deployment vigente.

## 5. Journey Cobros

```text
upload XLSX
→ SEM-8 semantic proposal
→ owner material confirmation
→ P6/P7/P8
→ LIQ_001 deterministic execution
→ bounded outcome
→ controlled XLSX delivery
```

La web no debe volver a mantener listas semánticas propias para este journey.

## 6. Journey Margen Real

```text
upload XLSX
→ WorkbookProfiler
→ semantic proposal
→ owner confirms columns + product relation
→ optional owner unit confirmation for discount
→ Derived Evidence
→ P8
→ FormulaEngineService/kernel
→ REN_001 outcome
→ controlled XLSX delivery
```

### Fail-closed

Debe bloquear o pedir evidencia si:

```text
product relationship is not owner-confirmed
join coverage is incomplete
unit cost/quantity/unit price semantics are missing
non-zero discount unit is not confirmed
required taxes are absent
numeric evidence is invalid
```

No usar `taxes=0` implícito.

## 7. Provider semántico

Estado actual:

```text
external provider: not connected
safe deterministic baseline provider: active
```

La dependencia se inyecta por `semantic_provider`. No importar SDK externo dentro de `pymia/` mientras rija la policy actual.

## 8. Tenant identity y memoria

Producción exige identidad verificada antes de persistir owner evidence.

Memoria:

```text
historical tenant contract
→ structural compatibility
→ COMPATIBLE_HINT only
→ semantic context
```

No hay auto-confirmación ni semantic rebind por memoria.

## 9. Working Capital

`working_capital` conserva en este corte su semantic scoping legacy. Es una excepción explícita de piloto y no debe utilizarse como patrón para nuevos journeys.

## 10. QA de cambio

```text
small isolated change      → focal tests
integration change         → focal + relevant regression
semantic/runtime cut       → relevant regression + architecture gates
release candidate          → full suite
production deployment      → production smoke on deployed SHA
```

Última evidencia del worktree:

```text
297 relevant tests PASS
FULL_SUITE_COVERAGE: PASS_BY_EXHAUSTIVE_SHARDS
3614 passed / 7 skipped / 0 failed
MONOLITHIC_MCP_RUNNER: HTTP_502_TIMEOUT
```

## 11. Release gate actual

```text
1. review worktree classification
2. authorized thematic commits
3. deploy exact SHA
4. production smoke exact SHA
```

## 12. Prohibiciones operativas

```text
NO_SECOND_XLSX_PARSER
NO_SECOND_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_PARALLEL_MARGIN_CALCULATION
NO_IMPLICIT_MATERIAL_DEFAULTS
NO_DELIVERY_WITHOUT_GOVERNED_PATH
NO_SECRET_PRINTING
```
