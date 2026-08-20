# Servicio 1 — Operability Packet V1

**Fecha de corte:** 2026-08-14
**Estado:** `ACTIVE`

## 1. Autoridad operativa

```text
CLI:  python -m pymia.cli.service_1_product
WEB:  python -m pymia.smartpyme.service_1_semantic_reception_server_v1
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

No crear otra entrada con autoridad productiva equivalente.

## 2. Último corte histórico certificado en producción

```text
TARGET: Google Cloud Run
SERVICE: pymia-service1
APP_SHA: d2c9c24
REVISION: pymia-service1-00008-mtf
TRAFFIC: 100%
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
```

Este corte certificado es histórico; no demuestra que el release candidate actual esté desplegado. Identidad/persistencia productiva: Supabase.

## 3. Variables de producción

Runtime:

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

La CLI oficial mantiene compatibilidad gobernada existente:

```text
python -m pymia.cli.service_1_product
  --xlsx <archivo.xlsx>
  --owner-column-answers <owner_column_answers.json>
  --tool-requests <tool_requests.json>
  --output-dir <output_dir>
  --result-json <result.json>
```

Para capability gobernada se usa `--requested-capability`. Las superficies legacy de CLI son compatibilidad, no patrón arquitectónico para nuevos journeys.

## 5. Web local

```text
python -m pymia.smartpyme.service_1_semantic_reception_server_v1 --host 127.0.0.1 --port 8766
```

Health local:

```text
GET /healthz
→ 200
→ {"status":"ok"}
```

Cloud Run se certifica mediante el smoke productivo oficial.

## 6. Journey LIQ_001

```text
upload XLSX
→ SEM-8 semantic proposal
→ owner material confirmation (opciones canónicas en allowed_option_ids)
→ P6/P7/P8
→ deterministic execution
→ bounded outcome
→ controlled XLSX delivery
```

Estado:

```text
PRODUCTION_CERTIFIED: YES
AUTH_FAIL_CLOSED: PASS
DELIVERY: PASS
```

Las respuestas del dueño deben ser option_ids canónicos (allowed_option_ids); texto libre no canónico se bloquea (INVALID_OWNER_OPTION_ID).

## 7. Journey REN_001

```text
upload XLSX
→ WorkbookProfiler / SEM-8
→ owner semantic confirmation
→ owner-confirmed product relationship
→ discount unit confirmation cuando aplica
→ Derived Evidence
→ P8
→ FormulaEngineService/kernel
→ REN_001 bounded outcome
→ controlled XLSX delivery
```

Fail-closed productivo certificado ante ausencia de impuestos requeridos. No usar `taxes=0` implícito.

Estado:

```text
PRODUCTION_CERTIFIED: YES
RELATIONSHIP_DEDUPLICATION: PASS
DISCOUNT_UNIT_CONFIRMATION: PASS
DERIVED_EVIDENCE: PASS
DELIVERY: PASS
```

## 8. Persistencia y reentry

```text
PERSISTED_OWNER_EVIDENCE_REENTRY: PASS
F13_DURABLE_RESULT_MEMORY: PASS
RC3_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
```

RC3 reabre el ResultSet persistido sin volver a cargar el workbook ni recalcular. Todavía no declarar reentrada durable de producto como certificada en producción hasta completar el acceptance online después de restart real.

## 9. Tenant identity y memoria

Producción exige identidad verificada antes de persistir owner evidence.

```text
historical tenant contract
→ structural compatibility
→ COMPATIBLE_HINT only
→ semantic context
```

No hay auto-confirmación ni semantic rebind por memoria.

## 10. Provider semántico

```text
EXTERNAL_PROVIDER_IMPLEMENTATION: AVAILABLE
EXTERNAL_PROVIDER_CURRENT_RC_RUNTIME: NOT_PROVEN
SAFE_DETERMINISTIC_BASELINE_PROVIDER: PRESERVED
NO_LLM_RUNTIME_AUTHORITY
```

La dependencia se inyecta por `semantic_provider`. La activación real sólo se declara después de desplegar el RC exacto y observar el smoke correspondiente.

## 11. Working Capital

```text
TECHNICAL_E2E_READY: YES
PRODUCTION_CERTIFIED: YES
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
COMPOSITE_DELIVERY: NO
```

No incorporar DPO/payment_collection_gap ni nuevas fórmulas durante el frente de sanidad.

## 12. QA de cambio

```text
small isolated change      → focal tests
integration change         → focal + relevant regression
semantic/runtime cut       → relevant regression + architecture gates
release candidate          → full suite / exhaustive shards si el wrapper monolítico falla por transporte
production deployment      → production smoke on exact deployed SHA
```

## 13. Deuda operativa/arquitectónica abierta

```text
RC3_COMMIT_FREEZE: CLOSED
TENANT_REENTRY_HARDENING: CLOSED
RC4_DOCUMENTATION_SYNC: CLOSED
FULL_SUITE_CURRENT_RC: PENDING
DEPLOY_EXACT_RC_SHA: PENDING
EXTERNAL_LLM_CURRENT_RC_PROOF: PENDING
ONLINE_CAFETERIA_ACCEPTANCE: PENDING
ONLINE_F13_REENTRY_AFTER_RESTART: PENDING
```

Compatibilidades legacy de P6/reentry permanecen congeladas y no son autoridad productiva ni frente activo.

## 14. Release gate actual

```text
RC1: CLOSED
RC2: CLOSED
RC3: CLOSED
TENANT_REENTRY_HARDENING: CLOSED
RC4: CLOSED
RC5: DEPLOY + REAL LLM
RC6: ONLINE CAFETERIA
RC7: ONLINE RESULTSET REENTRY
```

El release candidate sólo se acepta con full suite del corte actual y production smoke sobre el SHA exacto desplegado.

## 15. Prohibiciones operativas

```text
NO_SECOND_XLSX_PARSER
NO_SECOND_PRODUCT_ROOT
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
NO_PARALLEL_MARGIN_CALCULATION
NO_IMPLICIT_MATERIAL_DEFAULTS
NO_DELIVERY_WITHOUT_GOVERNED_PATH
NO_SECRET_PRINTING
NO_FEATURE_EXPANSION_DURING_RC_CLOSE
```
