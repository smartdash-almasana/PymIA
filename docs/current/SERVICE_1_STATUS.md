# Servicio 1 — estado actual

**Fecha de corte:** 2026-08-07
**Estado documental:** fundación contractual tenant-scoped implementada y validada; revisión independiente e integración pendientes.
**HEAD base de la definición:** `8aced9c`.

## Estado ejecutivo

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS
RAÍZ PRODUCTIVA CANÓNICA ÚNICA: ACTIVA
CLI PRODUCTIVA CANÓNICA: ACTIVA
P0–P10: ARQUITECTURA VIGENTE
STAGE 2: CLOSED_PASS
12/12 CAPACIDADES PRODUCTIVAS HISTÓRICAMENTE CONECTADAS: CONSERVADAS
KERNEL GENÉRICO PRODUCTIVO: ACTIVO
KERNEL GENÉRICO: ACTIVO
OWNER CONFIRMATION: EVIDENCIA, NO PERMISO
P8 GOVERNED INPUT: AUTORIDAD DE COMPUTABILIDAD
LLM RUNTIME AUTHORITY: NO
SIN LLM RUNTIME
SIN DIAGNÓSTICO CAUSAL
SEGUNDA RAÍZ PRODUCTIVA: NO
DELIVERY AUTÓNOMO: NO AUTORIZADO
API PRODUCTIVA: NO AUTORIZADA
CAPABILITY_PHYSICAL_COVERAGE_GATE_V1: CLOSED_PASS
FIRST_CONTACT_EXPLICIT_OWNER_CONFIRMATION: CLOSED_PASS
CONCILIACIÓN CONTROLADA: PILOTO CERRADO PASS
MATCHING 1:N / N:1: CANDIDATOS TRAZABLES
DUPLICADOS EXACTOS: EXPLÍCITOS
REVISIÓN HUMANA: OBLIGATORIA
TENANT SEMANTIC CONTRACT V1: FOUNDATION_IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW
TENANT-ISOLATED APPEND-ONLY STORE: IMPLEMENTED
TENANT MEMORY: NO IMPLEMENTADA
AUTOMATIC TENANT MAPPING REUSE: NO IMPLEMENTADA
12/12 PRODUCTIVAS CONECTADAS ≠ TODAS CON DELIVERY AUTÓNOMO
```

## 1. Autoridad productiva

Entrada oficial:

```text
pymia/cli/service_1_product.py
```

Raíz productiva:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe una segunda raíz productiva autorizada.

## 2. Clasificación física Service 1

Fuente:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado:

```text
TOTAL_SERVICE_1_MODULES = 60
PRODUCTIVE = 30
SUPPORT_NECESSARY = 30
```

La clasificación `PRODUCTIVE` sigue siendo la frontera para determinar el closure ejecutable de la raíz.

## 3. Cadena vigente

```text
P0 intake
→ P1 canonical XLSX ingestion
→ P2 profiling / physical evidence
→ P3 semantic hypothesis
→ P4 contextual evidence
→ P5 OwnerConfirmationEvent
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ P9 deterministic execution
→ P10 QA / delivery
```

Los límites siguen siendo:

```text
owner confirmation ≠ runtime authorization
semantic hypothesis ≠ approval
approval ≠ computability
computation ≠ diagnosis final
delivery result ≠ delivery authorization general
```

## 4. Capacidades productivas vigentes

El catálogo productivo conserva las 12 capacidades cerradas previamente:

| Patología | Capacidad |
|---|---|
| `LIQ_001` | `sold_vs_collected_gap` |
| `REN_001` | `net_margin_real` |
| `LIQ_002` | `projected_closing_cash_balance` |
| `PYME_011` | `dso` |
| `PYME_013` | `payment_collection_gap` |
| `INV_001` | `reorder_point` |
| `INV_002` | `inventory_turnover` |
| `PYME_024` | `current_ratio` |
| `PYME_033` | `sales_concentration` |
| `REN_002` | `index_update_ratio` |
| `PYME_027` | `interest_burden_ratio` |
| `PYME_026` | `adjusted_operating_cash_flow` |

DPO continúa como prerrequisito técnico de `PYME_013`, no como decimotercera patología productiva.

El gate consolidado `CAPABILITY_PHYSICAL_COVERAGE_GATE_V1` está cerrado y vuelve a pasar bajo el contrato vigente de confirmación explícita. Conserva exactamente doce capacidades productivas; DPO sigue siendo prerrequisito técnico de `PYME_013`, no una decimotercera capacidad. `adjusted_operating_cash_flow` permanece `PHYSICAL_PARTIAL` con bloqueo explícito `CAPABILITY_NOT_GOVERNED`, y `payment_collection_gap` conserva su deferimiento contractual hasta completar sus prerrequisitos físicos. El gate no autoriza delivery autónomo.

La existencia de una capacidad productiva no implica que su delivery esté autorizado automáticamente.

## 5. Arquitectura nueva integrada alrededor de Servicio 1

Después de Stage 2 se integraron varias fundaciones de plataforma.

### Modelo de dominio

```text
pymia/domain/*
```

Objetivo: lenguaje de dominio puro, entidades, primitivas, snapshots y tipos sin dependencia de infraestructura.

Estado frente a Servicio 1:

```text
PLATFORM_FOUNDATION
NOT_SECOND_PRODUCT_ROOT
```

### Admisión

```text
pymia/contracts/admission_v1.py
pymia/pipeline/admission/v1/*
```

Objetivo: transformar narrativa inicial en síntomas, hipótesis y evidencia requerida.

Estado frente a Servicio 1:

```text
PREANALYTIC_SUPPORT
HYPOTHESIS_NOT_AUTHORITY
CONFIDENCE_SCORE_NOT_EXECUTION_AUTHORITY
```

### Faithful Operator

```text
pymia/faithful_operator.py
```

Objetivo: interacción determinística con el dueño, pedido de evidencia, resultado candidato y corrección/confirmación.

Estado frente a Servicio 1:

```text
APPLICATION_SUPPORT
FAIL_CLOSED
NOT_SECOND_PRODUCT_ROOT
```

### Vertical application pipeline

```text
pymia/cli/vertical_slice.py
pymia/application/vertical_pipeline.py
```

Objetivo: flujo local de evidencia, reporte, registro y presentación.

Estado:

```text
APPLICATION_SUPPORT
NOT_CANONICAL_PRODUCT_AUTHORITY
```

### Diagnostic Core

```text
pymia/diagnostic_core/*
pymia/services/formula_engine_service.py
```

Objetivo: cálculo reusable y resultados candidatos/bloqueados basados en evidencia.

Estado:

```text
COMPUTATION_SUPPORT
CALCULATED_NOT_EQUAL_DIAGNOSED
```

### Narrative layer

```text
pymia/narrative/*
```

Objetivo: convertir evidencia y señales en claims legibles y trazables.

Estado:

```text
PRESENTATION_SUPPORT
NARRATIVE_NOT_EQUAL_EVIDENCE
```

### Operational Harness + Pipeline Radiography

```text
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Objetivo: escenarios, observación, clasificación del estado técnico y detección de ambigüedad/partial readiness.

Estado:

```text
ENGINEERING_OBSERVABILITY
NOT_PRODUCT_RUNTIME
```

## 6. Contabilidad y conciliación

Existe una familia de contratos contables y workpapers, incluida:

```text
service_1_accounting_contracts_v1
```

Su disposición vigente es:

```text
SUPPORT_NECESSARY
```

También existen contratos específicos de:

- conciliación bancaria;
- Mercado Pago;
- factura/cobranza;
- compra/proveedor.

El matcher algorítmico actual está en:

```text
service_2_reconciliation_match_candidates_v1
```

Estado actual del frente:

```text
MATCHER_EXISTS
ALGORITHMIC_MATCHING_EXISTS
MATCHING_1N_N1_CLOSED_FOR_CONTROLLED_PILOT
EXACT_DUPLICATES_EXPLICIT
AMBIGUITY_EXPOSED_TO_HUMAN_REVIEW
CONTROLLED_PILOT_MATCHES_EXPECTED_CATEGORIES
WORKPAPER_XLSX_TRACEABLE
PRODUCTIVE_S1_WIRING_ACTIVE
NO_AUTOMATIC_ACCOUNTING_CLOSURE
```

Decisiones cerradas:

- referencia es evidencia, no identidad;
- fecha + importe no prueba identidad;
- float confidence no decide conciliación;
- 1:N / N:1 / N:M debe quedar explícito;
- no resolver colisiones mediante matching codicioso;
- diferencias de importe no pueden hacer desaparecer movimientos no imputados;
- `AMBIGUOUS` escala a revisión humana.

## 7. Evolución Git relevante

```text
039f0cd  feat(domain): integrate domain model foundation
1b62053  feat(narrative): integrate deterministic narrative layer
05cf07b  feat(pipeline): integrate admission pipeline foundation
bc2fabf  feat(tooling): integrate pipeline radiography and operational harness
c240080  refactor(service1): remove live root dependency and legacy evidence bridge
9181abf  feat(service1): integrate faithful operator and document parsing support
48aa4a0  docs(service1): reconcile current authority and retire Hermes legacy
17e36a2  test(repo): retain regression coverage and local tooling
```

## 8. Límites actuales

- Completo no significa ERP total, CRM, SaaS autónomo ni Servicios 2/3 completos.
- No existe LLM soberano en runtime de Servicio 1.
- No existe selección de capacidad por texto libre con autoridad productiva.
- La confirmación del dueño sigue siendo evidencia semántica, no permiso general.
- Las capas de admisión, operador fiel, dominio, narrativa y harness no sustituyen la raíz canónica.
- Los contratos contables no ejecutan por existir.
- El piloto controlado de conciliación está cerrado con comparación contra control, pero sus `76/76` decisiones permanecen `PENDING` para revisión humana.
- No existe aceptación automática, asiento contable ni cierre definitivo de conciliación.
- La confirmación explícita del primer contacto está implementada y conectada al journey web real con identidad Supabase por tenant, persistencia durable append-only, memory recall asistido y supersesión versionada. La segunda carga puede mostrar antecedentes del mismo tenant sin preselección ni auto-reuse, exige reconfirmación explícita y persiste nuevas revisiones encadenadas (`revision=n+1`, `supersedes_contract_id=prior.contract_id`). El E2E físico real de LIQ_001 cerró memoria, supersesión, P6/P7/P8, P10 y descarga XLSX. Drift/contradiction resolution y semantic rebinding automático siguen fuera de alcance.
- API y microservicios distribuidos no son el siguiente paso autorizado de conciliación.

## 9. Documentación de arquitectura

```text
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
```

## 10. Regla de continuidad

Todo nuevo desarrollo de Servicio 1 debe responder primero:

```text
¿es producto, soporte o incubación?
¿en qué punto P0–P10 entra?
¿qué contrato gobierna?
¿qué evidencia lo autoriza?
¿crea una segunda autoridad?
```

Si la última respuesta es sí, el diseño está bloqueado hasta reconciliación arquitectónica.
