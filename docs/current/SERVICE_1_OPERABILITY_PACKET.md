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

## 2. Producción vigente

```text
TARGET: Google Cloud Run
SERVICE: pymia-service1
LAST_CERTIFIED_APP_SHA: 4db43ae
LAST_CERTIFIED_REVISION: pymia-service1-00009-czm
TRAFFIC: 100%
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS_FOR_PREVIOUS_CERTIFIED_BASELINE
SEMANTIC_RECEPTION_SEQUENTIAL_MAIN_SHA: 26ef6c8c57bb201da1a36a1073147c641d1309f4
SEMANTIC_RECEPTION_SEQUENTIAL_DEPLOYMENT: PENDING
SEMANTIC_RECEPTION_SEQUENTIAL_PRODUCTION_SMOKE: PENDING
```

Identidad/persistencia productiva: Supabase.

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
python -m pymia.smartpyme.service_1_assisted_web_v1 --host 127.0.0.1 --port 8766
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
PERSISTED_CASE_LISTING: PASS
PERSISTED_CASE_REENTRY: PASS
DURABLE_REENTRY_SCOPE: OWNER_EVIDENCE_ONLY
```

No afirmar restauración durable del workbook ni del result snapshot completo después de restart.

La sanidad arquitectónica debe converger las múltiples superficies/mecanismos de reentry detectados sin ampliar claims.

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
LLM_COLUMN_INTERPRETER_V1: MERGED_IN_MAIN
SEQUENTIAL_OWNER_CORROBORATION_V1: MERGED_IN_MAIN
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_YET_PROVEN
SAFE_DETERMINISTIC_BASELINE_PROVIDER: PRESERVED
```

La dependencia se inyecta por `semantic_provider`. El provider externo no adquiere autoridad de cálculo, runtime ni delivery. Su estado productivo sólo puede cambiar después de deploy + production smoke del corte semántico secuencial.

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
WORKING_CAPITAL_LEGACY_SEMANTIC_FORK: CLOSED_PRODUCTION_PASS
MULTIPLE_REENTRY_MECHANISMS: OPEN
LEGACY_P8/P6_PROJECTIONS: OPEN
UNUSED_SANDBOX_SLICES: NEEDS_CLASSIFICATION
```

## 14. Release gate actual

La baseline previa de LIQ_001/REN_001/Working Capital ya está certificada. Existe un release pendiente únicamente para el nuevo corte semántico secuencial integrado en `main`.

Frente vigente:

```text
SEMANTIC_RECEPTION_SEQUENTIAL_CUT: MERGED_IN_MAIN
PRODUCTION_CERTIFICATION_OF_NEW_CUT: PENDING
```

Orden:

```text
DEPLOY_SEMANTIC_RECEPTION_SEQUENTIAL_CUT
→ PRODUCTION_SMOKE
→ CONFIRM_RUNTIME_PROVIDER_STATE
→ UPDATE_CURRENT_AUTHORITY_DOCS
→ CLOSE_CUT
```

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
NO_FEATURE_EXPANSION_DURING_SANITATION
```
