## 6. Physical Architecture Reality

### 6.1 Lo que existe físicamente

| Componente | Estado |
|---|---|
| Canonical XLSX ingestion (single parser) | EXISTENTE (ACTIVO) |
| WorkbookProfiler | EXISTENTE (ACTIVO) |
| Deterministic semantic roles engine | EXISTENTE (ACTIVO) |
| Bridge + controlled execution gate | EXISTENTE (ACTIVO) |
| Owner confirmation loop + reentry | EXISTENTE (ACTIVO) |
| P6 (per-column approval) | EXISTENTE (ACTIVO) |
| P7 (family requirement match + grain) | EXISTENTE (ACTIVO), grain soportado pero NO consumido aguas abajo |
| P8 (computability + GovernedComputationInput) | EXISTENTE (ACTIVO) |
| Derived Evidence V1 | EXISTENTE (ACTIVO, 2 derivaciones REN_001) |
| Capability registry + GenericCapabilityEngine | EXISTENTE (ACTIVO, 11 abilities) |
| FormulaEngineService (Kernel) | EXISTENTE (ACTIVO, 18 fórmulas declaradas) |
| Evaluadores especializados | LIQ_001, REN_001 (ACTIVOS) |
| Bounded outcomes + XLSX delivery | EXISTENTE (ACTIVO para LIQ_001/REN_001) |
| Product root | EXISTENTE (ACTIVO) |
| Web assisted reception (F2/F3) | WORKTREE-ONLY (no committeado) |
| CLI `service_1_product.py` | EXISTENTE (ACTIVO) |
| Tenant semantic persistence | EXISTENTE (wiring + Supabase adapter), post-discovery F3 sin usar |
| Memoria longitudinal (series temporales) | NO IMPLEMENTADO |
| PydanticAI provider externo | IMPLEMENTADO (código) pero NO activado (fallback determinístico en este entorno) |

### 6.2 Rutas semánticas paralelas (coexistencia, no cálculo paralelo)

El root contiene DOS caminos semánticos:

1. **Legacy determinístico**: `run_initial_pass` → `run_owner_reentry` → `build_computability_decision_from_confirmed_bindings_v1`.
2. **Asistido F2 (capability-neutral)**: `run_service_1_assisted_semantic_initial_v1(requested_capability=None)` → validator → dialogue → `run_service_1_assisted_semantic_reentry_v1` → `CONFIRMED_BINDINGS`.

Ambos producen el mismo `semantic_run` con `status=CONFIRMED_BINDINGS`, y P8 consume la misma firma. Esto cumple `NO_PARALLEL_PRODUCTIVE_PIPELINE` (no hay segundo parser ni segunda matemática); pero SÍ hay dos rutas semánticas que coexisten y duplican mantenimiento.

### 6.3 No hay invasión de capas grave

- El Kernel NO interpreta Excel ni inventa inputs (verificado: `calculate()` sólo lee `SUPPORTED_FORMULAS` + valores).
- P8 NO ejecuta fórmula (verificado: `to_dict()` no calcula; sólo valida catálogos y bindings).
- Derived Evidence NO ejecuta la fórmula final (sólo multiplica cantidad×precio y suma filas para REN_001; la fórmula del margen la ejecuta el kernel).
- La web NO contiene fórmulas de negocio (verificado por grep en `assisted_web*.py`).
- Excepción: `run_working_capital` (web) reúne 3 evaluaciones; la matemática real sigue en los evaluadores.

---

## 7. Current Service 1 Product

### 7.1 Inventario real desde código (no aceptado sólo por documentación)

**Capabilities gobernadas en registry (`list_capability_refs_v1` = 11):**

```text
LIQ_002        projected_closing_cash_balance   ATOMIC
INV_001        reorder_point                    ATOMIC
INV_002        inventory_turnover               ATOMIC
DPO            dpo                              ATOMIC (registry; NO en evidence matrix)
PYME_011       dso                              ATOMIC
PYME_013       payment_collection_gap           COMPOSITE (registry; NO en matrix)
PYME_024       current_ratio                    ATOMIC
PYME_033       sales_concentration             ATOMIC
PYME_027       interest_burden_ratio            ATOMIC
PYME_026       adjusted_operating_cash_flow     ATOMIC (formula no en matrix)
REN_002        index_update_ratio               ATOMIC
```

**Formulas en `formula_catalog.v1.json` (18) vs implementadas:**

Implementadas en Kernel (`SUPPORTED_FORMULAS`): las 17 declaradas, todas CALCULABLE.
`PYME_026_adjusted_operating_cash_flow` NO está en `SUPPORTED_FORMULAS`; el generic engine la resuelve vía `FormulaNodeV1` desde registry.
`PYME_013_PREREQUISITE_dpo`, `PYME_004_recpam_basico`, `PYME_047_*`, `M05_roi_automatizacion`, `OPE_001_*`: declaradas en catálogo pero no implementadas en kernel ni registry → `DECLARED_NOT_IMPLEMENTED`.

**Evidence matrix (v2.0):** 10 capabilities con `computation_candidate_allowed=true`; 4 entries de patología sin fórmula (`SAL_001`, `STK_001`, `CST_001`, `CSH_001`).

**Menú web (`_REVIEW_OPTIONS`, 12 refs):** incluye 12 análisis, pero pocos tienen evaluador productivo completo (LIQ_001 y REN_001 con evaluador propio + generic para el resto).

### 7.2 Lo certificado en producción vs hoy

Documentación (`README.md:26,34-46`, `SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`):
```text
PRODUCTION_APP_SHA: d2c9c24
PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00008-mtf
PRODUCTION_TRAFFIC: 100%
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED (SEM8 composite)
MAIN_HEAD (documentado): 26ef6c8 (anterior a 4cda16d)
```

Hecho físico del repo: HEAD actual de `main`/branch = `4cda16d`, posterior incluso al `MAIN_HEAD` documentado. Es **imposible sustentar** que HEAD actual esté certificado en producción: la certificación documentada es para el corte `d2c9c24`/`26ef6c8`, no para `4cda16d` (y menos para el worktree con F2/F3 sin commitear).

---

## 8. Current Production vs Worktree

```text
PRODUCTIVE (main HEAD 4cda16d + previos):
  - canonical ingestion, profiler, P6/P7/P8, kernel, derived evidence REN_001,
    LIQ_001/REN_001 evaluadores+outcome+delivery, generic registry+engine (11),
    web assisted legacy + working_capital, tenant persistence wiring code

WORKTREE-ONLY (F2/F3, 7 archivos, NO committeado):
  - service_1_assisted_semantic_product_wiring_v1.py (capability-neutral initial)
  - service_1_assisted_web_semantic_reception_v1.py (workbook-first + discovery)
  - service_1_assisted_web_v1.py (run_working_capital override, post-discovery)
  - service_1_llm_semantic_contract_v1.py (nullable requested_capability)
  - service_1_ui_v1.py (render blocked options)
  - 2 tests nuevos

NO EXISTENTE EN ESTE WORKTREE:
  - pymia/smartpyme/service_1_commercial_analytics_v1.py  -> NO existe (sólo en main sucio)
```

`NO_SECOND_XLSX_PARSER` cumple: `read_xlsx_to_normalized_tables_v1` es el único reader productivo (verificado por grep: ningún otro `.py` productivo importa `load_workbook` salvo el parser canónico + delivery/quality/reconciliation).

---

## 9. Canonical Journey Audit

Cadena documentada (README / product state):
```text
XLSX -> canonical ingestion -> WorkbookProfiler -> semantic assistance ->
deterministic validation -> owner material confirmation -> canonical owner evidence ->
P6 -> P7 + Grain -> P8 -> Derived Evidence (cuando corresponde) ->
Kernel -> bounded outcome -> controlled delivery
```

### 9.1 ¿Es la ruta productiva real?

**SÍ en su esencia**, con estas precisiones:

1. El root llama `run_initial_pass` o `run_service_1_assisted_semantic_*` para producir `CONFIRMED_BINDINGS`; luego P8; luego `evaluate_liq_001`/`ren_001` o `execute_generic_capability_v1`.
2. **Bypass encontrado**: para `requested_capability=working_capital`, el root usa `build_service_1_composite_governed_computation_input_v1` y NO pasa por P8 (decisión de arquitectura: la composición usa catálogo + registry, no P8). Bypass documentado (composite).
3. **Bypass legacy**: la web `run_review` para `_REVIEW_BY_REF` usa `run_owner_reentry`/`run_initial_pass` cuando NO hay assisted state; y la ruta legacy `owner_answers` se bloquea en el root (`LEGACY_OWNER_ANSWERS_REQUIRE_UPSTREAM_COMPATIBILITY`). La ruta productiva canónica pasó al camino asistido.
4. **Delivery condicionada**: `deliver_result` sólo se setea en web para `sold_vs_collected_gap` y `net_margin_real`; otras capabilities quedan `delivery_authorized=False` (correcto fail-closed).

### 9.2 ¿Rutas paralelas de cálculo?

- `run_service_1_product_pipeline_v1` → `run_service_1_pipeline_v1` (physical tools, `tool_requests`) es una ruta física de herramientas que NO calcula fórmulas; se gatilla sólo si no hay `requested_capability`.
- `build_collection_aging_product_request_v1` / `build_expense_variance_product_request_v1` son frentes separados (consorcios) que retornan ANTES de la semántica dentro del root.
- No hay segundo motor matemático productivo.

---

## 10. Semantic Brain Audit

### 10.1 Estructura física

```text
SEM-0 ADR boundary            (docs)
SEM-1 WorkbookProfiler        service_1_workbook_profiler_v1.py
SEM-2 provider-neutral ctx    service_1_llm_semantic_contract_v1.py (build_context nullable)
SEM-3 deterministic validator service_1_semantic_proposal_validator_v1.py
SEM-4 OwnerDialoguePlan       service_1_owner_semantic_dialogue_v1.py
SEM-5 owner evidence          service_1_owner_semantic_answer_projection_v1.py
SEM-6 reentry -> P6           service_1_owner_semantic_evidence_reentry_v1.py / reinjection
SEM-7 structural compat       service_1_tenant_semantic_contract_v1.py + store
SEM-8 wiring root             service_1_assisted_semantic_product_wiring_v1.py
SEM-9 assisted web            service_1_assisted_web_semantic_reception_v1.py (F2)
```

### 10.2 Roles semánticos disponibles (determinísticos)

`service_1_column_understanding_engine_v1.py::_ROLE_RULES` (~37 roles):
`operation_date, quantity, unit_sale_price, unit_cost_candidate, sales_amount,
period_sales_total, period_costs_total, period_taxes_total, purchase_amount,
collected_amount, accounts_receivable_amount, initial_balance, expected_collections,
expected_payments, period_days, average_sales, lead_time, safety_stock,
cost_of_goods_sold, average_stock, current_assets, current_liabilities,
main_sku_sales, total_sales, interest_expense, ebitda, closing_index, origin_index,
tax_amount, list_price, discount_candidate, subtotal_amount, product_identifier,
product_name, ...`

### 10.3 Frontera semantic provider

- `Service1PydanticAIColumnSemanticProviderV1` (pydantic-ai, google model) existe como código, con `semantic_provider_from_environment_v1()`.
- En este entorno NO hay variable para modelo externo → `receive_xlsx` usa el provider determinístico (`build_service_1_deterministic_semantic_proposal_v1`), como se verificó en la sonda.
- `NO_LLM_RUNTIME_AUTHORITY` se cumple: el provider produce sólo `ColumnSemanticBatchV1` (proposiciones), no calculate/execute.

### 10.4 F2 workbook-first (worktree)

- `run_service_1_assisted_semantic_initial_v1(requested_capability=None)` → usará `allowed_roles` completos en vez de `_capability_relevant_roles`; el diálogo pide confirmación de la columna más material (1 pregunta agrupada por concepto).
- El fixture cafeteria físico con provider determinístico: 2 preguntas → CONFIRMED_BINDINGS con 15 eventos owner.
- **Observación crítica**: el camino workbook-first NO persiste los eventos de owner confirmation post-discovery en la ruta F3 (`_confirm_workbook_first_semantics` → `_post_semantic_analysis_menu_page`), mientras que la ruta legacy `run_review` SÍ llama `_persist_owner_confirmation_events`. Esto es un GAP de coherencia de memoria semántica en la nueva ruta (bug F3, no implementado por esta auditoría).

---

## 11. Deterministic Brain Audit

### 11.1 P6

`build_service_1_p6_approval_decision_v1` decide significado por columna; consume owner evidence; `OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION` se cumple (la confirmación se convierte en evidencia canónica, no en autorización de ejecución).

### 11.2 P7 + Grain

- `VARIABLE_FAMILY_DEFINITIONS` (14) cubre exactamente las 10+ family verticales de las capabilities; cada una declara `grain` (`Service1GrainV1` con 4 ejes: structural_scope / business_entity_grain / temporal_grain / aggregation_grain).
- Todas las familias café-relevantes tienen grain flat: `REGION / NONE / NONE / ATOMIC` (CASH_COLLECTIONS, RECEIVABLES_DSO, CURRENT_RATIO, CASH_PROJECTION) y sólo PERIOD_NET_MARGIN es `SHEET / NONE / PERIOD / AGGREGATED`.
- No existe ninguna familia con `business_entity_grain` distinto de NONE o PRODUCT, ni producto×sucursal, ni producto×categoría, ni sucursal×día, ni hora. Esta es la limitación central de P7 para análisis multidimensional.

### 11.3 P8

- `build_service_1_computability_decision_v1` requiere P6 APPROVED + P7 match + matriz + catálogo + exactly one formula mapping.
- `governed_computation_input` lleva `grain` y `source_bindings`; pero el generic engine y los evaluadores LIQ/REN NO usan el `grain` para agrupar; sólo suman o toman un único valor.
- `build_service_1_composite_governed_computation_input_v1` (working_capital) construye `source_bindings` desde registry sin pasar por P8; bypass legítimo de composición.
- Los 3 fallos de controles físicos (§10) muestran que P8/P7 fail-closed está correcto (bloquea cuando falta evidencia), pero el corpus de prueba está incompleto.

---

## 12. Mathematical Brain / Kernel Audit

### 12.1 Inventario físico de fórmulas

| formula_id | Estado | Implementación |
|---|---|---|
| `margen_bruto`, `ganancia_bruta` | kernel | `FormulaEngineService._calculate_*` |
| `REN_001_margen_neto_real` | kernel | `_calculate_ren_001_margen_neto_real` |
| `LIQ_001_vendido_cobrado` | kernel | `_ok(..., sold - collected)` |
| `INV_001_punto_reposicion`, `INV_002_rotacion_stock` | kernel | `_calculate_*` |
| `PYME_011_dso`, `LIQ_002_saldo_final_proyectado`, `PYME_024_liquidez_corriente`, `PYME_017_pricing_drift`, `punto_equilibrio_ventas`, `PYME_026_flujo_operativo`, `PYME_027_intereses_ebitda`, `PYME_044_margen_cliente`, `PYME_033_concentracion_sku`, `REN_002_coeficiente_reposicion` | kernel | `_calculate_*` o `_ok` |
| `PYME_026_adjusted_operating_cash_flow` | NO en kernel, NO en SUPPORTED_FORMULAS | generic engine resuelve via registry `FormulaNodeV1` |
| `PYME_013_PREREQUISITE_dpo` | NO en kernel ni SUPPORTED_FORMULAS | generic engine resuelve via registry |
| `PYME_004_recpam_basico`, `PYME_047_tiempo_manual_automatizado`, `M05_roi_automatizacion`, `OPE_001_decisiones_centralizadas` | CALCULABLE_CON_SUPUESTOS en catálogo; NO en kernel ni registry | DECLARED_NOT_IMPLEMENTED |

### 12.2 Métricas de la auditoría del Kernel

```text
FORMULA_COUNT (implementadas): 17 en kernel + 2 vía generic FormulaNode = 19 ejecutables
FORMULA_CONTRACT_DRIFT: baja para las 17; alta para PYME_026/PYME_013 (registry+kernel desincronizados);
                        PYME_004/047/M05/OPE_001 declaradas pero no implementadas
MATHEMATICS_OUTSIDE_KERNEL:
  1) SUM/COUNT en evaluadores (LIQ_001 agrega columnas; generic _resolve_atomic_inputs suma)
  2) multiplicación cantidad×precio + join en Derived Evidence REN_001
  3) cálculo de working_capital en web (sólo reúne resultados, no matemática real)
SCALAR_LIMITATIONS: FormulaInput/FormulaResult(value: float) -> solo escalar;
                    no soporta arrays ni grains
MULTI_GRAIN_SUPPORT: NINGUNO (ni en kernel ni en generic; _resolve_atomic_inputs agrega columna entera)
EXTENSIBILITY_RISK:
  - AGREGAR una fórmula escalar nueva es trivial (registry+node o entrada en SUPPORTED_FORMULAS).
  - AGREGAR un análisis grupal (por producto/sucursal/temporal) NO es posible hoy
    sin tocar: family/registry + formula + evaluador + outcome + root + UI.
```

### 12.3 ¿Puede crecer a decenas/cientos de análisis?

Parcialmente. El modelo `FormulaNodeV1` del registry es extensible para fórmulas escalares (árbol binario: ADD/SUBTRACT/MULTIPLY/DIVIDE + VARIABLE/VALUE), y el generic engine ya resuelve cualquier fórmula del registry sin tocar el kernel. PERO:

- No soporta funciones de agregación (`GROUP BY`, `SUM over group`, `RANKING`, `COUNT`).
- No soporta joins con grain (derivación por grupo).
- No soporta resultados multidimensionales (cada `computed` es un dict plano con un `result_key`).
- No soporta series temporales (evolución por día/hora).

Respuesta a las preguntas del prompt:

> ¿FormulaEngineService puede crecer ordenadamente a decenas/cientos de análisis?

NO en su forma actual sin un plan de agregación gobernado. Puede crecer en fórmulas escalares ilimitadas, pero no en análisis grupales.

> ¿Su modelo FormulaInput/FormulaResult es suficiente? ¿Orientado exclusivamente a resultados escalares?

Escalar hoy (`value: float`).

> ¿Puede expresar razonablemente cálculos por múltiples grains?

No. El grain existe en `Service1GrainV1` y en `GovernedComputationInputV1.grain`, pero ningún consumidor (evaluador) lo usa para agrupar.

---

## 13. Derived Evidence Boundary Audit

### 13.1 Qué hace hoy (100% físico)

```text
Derived Evidence V1 (service_1_derived_evidence_v1.py):
  - V1 SÓLO soporta REN_001 (capability == "net_margin_real")
  - Deriva sale_price = SUMA(quantity × unit_sale_price) con descuento gobernado
  - Deriva costs     = SUMA(quantity × unit_cost_value vía join ProductoID)
  - Exige relationship confirmada cuando sales_sheet != cost_sheet
  - Exige unit de descuento confirmado (fraction/percent/line_amount) o bloquea
  - Nunca inventa impuestos; impuestos deben venir como variable confirmada
```

### 13.2 Separación A (estructuración) vs B (matemática)

Derived Evidence **sí ejecuta matemática de línea/producto** (multiplicación cantidad×precio, suma filas, aplicación de descuento). Frente a `KERNEL_IS_FORMULA_EXECUTION_AUTHORITY`:

```text
INFERENCE: YES
El kernel ejecuta la fórmula final (REN_001 margen). Derived Evidence produce los
inputs (agregando líneas). Si se interpreta "toda aritmética debe correr en el Kernel",
Derived Evidence lo viola. Si se interpreta "la fórmula de negocio final corre en el
Kernel" (interpretación documentada en SEM/derived), NO lo viola. La tensión existe
pero está gobernada por diseño; el código la resuelve manteniendo la fórmula final
en el Kernel.
```

**Verdict**: NO hay violación material del invariante, porque el Kernel ejecuta la fórmula final del margen. Pero:

1. La agregación de filas (suma) vive en Derived Evidence y en los evaluadores LIQ_001/generic.
2. Si mañana se quiere un análisis "ventas por producto", Derived Evidence no lo puede hacer porque está hardcodeada a REN_001 (capability + columnas fijas) y no puede emitir arrays por grupo.
3. `_apply_discount` es la única matemática no-kernel con semántica de negocio real (fraction/percent/amount). Es una decisión soportada, pero debería documentarse como "derivación de línea" y no como "fórmula de negocio".

---

## 14. Memory Brain Audit

```text
A. MEMORIA SEMÁNTICA
   - IMPLEMENTED: TenantSemanticContractV1 + append-only store + revision/supersession
   - Persistencia física: service_1_tenant_confirmation_persistence_wiring_v1.py ->
     persist_contract (Supabase adapter) + load_prior_contract
   - CALLERS: ruta legacy run_review (assisted_web_v1.py L2134 _persist_owner_confirmation_events)

B. MEMORIA DE EJECUCIÓN Y RESULTADOS
   - PARTIAL: _remember_case persiste listado/reentry, pero NO hay snapshot durable del
     resultado completo tras reinicio (documentado: DURABLE_REENTRY_SCOPE=OWNER_EVIDENCE_ONLY)

C. MEMORIA LONGITUDINAL EMPRESARIAL (series temporales)
   - NOT_IMPLEMENTED_AS_EXPLICIT_ENGINE (documentado igual en Five Brains)

GAP CRÍTICO F3 (audit): la ruta workbook-first post-discovery NO llama
_persist_owner_confirmation_events (ver L10.4). Esto significa que en el nuevo journey
las confirmaciones owner de la recepción semántica se quedan en memoria de sesión y
no se convierten en TenantSemanticContract durable. Es un bug de wiring, no de
arquitectura del memory brain.
```

---

## 15. Cognitive Brain Audit

```text
EXISTE como frontera provider-neutral:
  - build_service_1_llm_semantic_context_v1 (nullable requested_capability post-F2)
  - Service1LLMSemanticContext/Proposal/Batch (pydantic, extra=forbid)
  - Service1PydanticAIColumnSemanticProviderV1 + deterministic fallback
  - semantic_assist (web) para CORRECTION/CONVERSATION (sin perseguir ejecución)

NO EXISTE:
  - LLM con autoridad de runtime/matemática/tools/delivery (confirmado en código)
  - Provider externo activado en producción (documentado NOT_PROVEN)
```

El cerebro cognitivo se comporta como traductor lingüístico y proponente acotado, respetando `NO_LLM_RUNTIME_AUTHORITY`. El único matiz: el provider LLM puede proponer `confirmed_role`/`variable_name` dentro del contrato, y la validación determinística rechaza todo lo que no pase el validator (fail-closed).

---
