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
APP_SHA: 225f2c4
REVISION: pymia-service1-00006-h45
TRAFFIC: 100%
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
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
→ owner material confirmation
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
EXTERNAL_PROVIDER: NOT_CONNECTED
SAFE_DETERMINISTIC_BASELINE_PROVIDER: ACTIVE
```

La dependencia se inyecta por `semantic_provider`. No importar SDK externo dentro de `pymia/` mientras rija la policy actual.

## 11. Working Capital

```text
TECHNICAL_E2E_READY: YES
PRODUCTION_CERTIFIED: NO
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

No hay un release pendiente del corte SEM-1→SEM-9 para LIQ_001/REN_001: ya está certificado.

Frente vigente:

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

Orden:

```text
document authority sync
→ physical journey map
→ legacy dependency inventory
→ convergence cuts
→ full regression
→ production recertification
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
