# Servicio 1 — Excel Reality Lab + Instance Migration Roadmap V1

**Fecha de corte:** 2026-08-15
**Estado:** ACTIVE
**Prerequisito:** `SERVICE_1_TECHNICAL_CLOSURE: PASS`
**Producción certificada base:** `pymia-service1-00009-czm` / app SHA `4db43ae`

## 1. Objetivo

Validar Servicio 1 contra una población progresivamente diversa de Excel PyME reales o representativos, cubriendo variabilidad estructural, cálculos y rubros, sin reabrir la arquitectura cerrada ni crear caminos productivos paralelos.

En paralelo, continuar la migración controlada de la experiencia enterprise validada hacia la instancia pública Cloud Run de Servicio 1.

```text
EXCEL REALITY LAB
+
INSTANCE MIGRATION
```

Son dos tracks coordinados, no una misma tarea.

---

## 2. Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
LEGACY_SUPPORT_RESIDUAL_IS_FROZEN
```

Regla adicional:

```text
UN EXCEL NUEVO NO AUTORIZA UNA NUEVA ARQUITECTURA.
```

Si un caso falla, primero se clasifica el fallo. Sólo un defecto causal demostrado habilita cambio productivo.

---

# TRACK A — EXCEL REALITY LAB

## A0. Corpus Contract

Crear un corpus versionado de pruebas físicas. Cada caso debe declarar:

```text
case_id
rubro
fuente/sinteticidad
cantidad_hojas
volumen_filas
estructura
nombres_columnas
idioma/convenciones
presencia_formulas_excel
presencia_totales/subtotales
presencia_celdas_vacias
presencia_duplicados
fechas
monedas
unidades
capability_target
resultado_esperado_o_estado_fail_closed
```

No almacenar secretos ni datos personales reales sin sanitización.

### Gate A0

```text
CORPUS_SCHEMA: PASS
TRACEABILITY: PASS
NO_UNGOVERNED_FIXTURES: PASS
```

---

## A1. Variabilidad estructural de Excel

Probar, como mínimo, las siguientes familias físicas:

```text
1. una hoja / tabla limpia
2. múltiples hojas
3. encabezados desplazados
4. columnas extra irrelevantes
5. columnas faltantes
6. nombres ambiguos
7. nombres abreviados
8. columnas duplicadas o casi duplicadas
9. filas vacías intermedias
10. subtotales y totales mezclados
11. fechas en formatos distintos
12. números como texto
13. separadores decimales/miles variados
14. moneda mezclada o declarada
15. fórmulas Excel + valores
16. hojas auxiliares
17. tablas de distinta granularidad
18. datasets pequeños
19. datasets medianos
20. datasets grandes dentro del límite operativo autorizado
```

### Gate A1

Cada caso termina únicamente en:

```text
PASS_COMPUTABLE
PASS_NEEDS_OWNER
PASS_NEEDS_EVIDENCE
PASS_BLOCKED_FAIL_CLOSED
FAIL_DEFECT
```

`FAIL_DEFECT` exige evidencia causal antes de modificar runtime.

---

## A2. Matriz de cálculos

Ejecutar el corpus sobre capacidades ya autorizadas por el catálogo productivo.

Prioridad inicial certificada:

```text
LIQ_001 / sold_vs_collected_gap
REN_001 / net_margin_real
WORKING_CAPITAL:
- projected_closing_cash_balance
- dso
- current_ratio
```

Después extender el corpus a otras capacidades existentes sólo si ya están autorizadas por catálogo/gates. No crear capacidades para satisfacer el corpus.

Para cada cálculo verificar:

```text
SEMANTIC_BINDING
OWNER_CONFIRMATION
P6
P7
P8
GOVERNED_INPUT
KERNEL_RESULT
CLASSIFICATION
DELIVERY cuando esté autorizada
FAIL_CLOSED negativos
```

### Gate A2

```text
NO_FORMULA_DRIFT
NO_SECOND_CALCULATION_AUTHORITY
EXPECTED_NUMERIC_RESULT_OR_EXPLICIT_BLOCK
```

---

## A3. Matriz de rubros

Los rubros son contexto de prueba y lenguaje real; no implican nuevas capabilities.

Corpus prioritario:

```text
comercio minorista
mayorista / distribuidora
textil
producción / fábrica
servicios profesionales / estudio contable
gastronomía
administración de consorcios
seller Mercado Libre / Mercado Pago
```

Para cada rubro recolectar variantes de:

```text
vocabulario de columnas
hojas habituales
granularidad
unidades
periodicidad
campos faltantes frecuentes
ambigüedades semánticas
```

### Gate A3

El sistema debe:

```text
entender determinísticamente cuando hay evidencia suficiente;
preguntar al dueño cuando el significado es materialmente ambiguo;
bloquear cuando falta evidencia material;
no inventar equivalencias de rubro.
```

---

## A4. Pathology / adversarial Excel corpus

Agregar casos deliberadamente difíciles:

```text
columnas semánticamente engañosas
signos invertidos
cero vs vacío
fechas fuera de período
monedas inconsistentes
filas repetidas
subtotales tratados como operaciones
hojas con distinta granularidad
relaciones incompletas
valores extremos
inputs materialmente ausentes
```

Objetivo: demostrar que Servicio 1 falla cerrado antes de producir cálculo engañoso.

---

## A5. Real-client shadow runs

Con archivos reales sanitizados o autorizados:

```text
archivo real
→ ejecución shadow
→ resultado esperado revisado
→ divergencia registrada
→ root cause
→ decisión
```

No corregir caso por caso con hacks ni alias no gobernados.

Métrica central:

```text
PHYSICAL_CASE_PASS_RATE
SEMANTIC_OWNER_QUESTION_RATE
NEEDS_EVIDENCE_RATE
FAIL_CLOSED_RATE
TRUE_DEFECT_RATE
```

No optimizar para minimizar preguntas al dueño a costa de precisión.

---

## A6. Regression corpus permanente

Todo defecto real corregido agrega un fixture/regression case permanente.

```text
REAL_CASE
→ DEFECT
→ MINIMAL_FIX
→ REGRESSION_FIXTURE
→ FULL SUITE
→ PRODUCTION SMOKE
```

El corpus crece; la arquitectura no se bifurca.

---

# TRACK B — MIGRACIÓN A LA INSTANCIA PÚBLICA

## B0. Baseline

Instancia canónica pública:

```text
Cloud Run service: pymia-service1
última revisión productiva certificada: pymia-service1-00009-czm
```

No crear una segunda instancia productiva de Servicio 1 para el mismo producto.

---

## B1. Enterprise UI parity

Migrar la experiencia enterprise ya trabajada localmente hacia la app productiva, preservando lógica y contratos.

Scope permitido:

```text
presentación
jerarquía visual
copy
estados de interacción
flujo de upload/confirmación/review ya existente
responsive/accessibility
```

Fuera de scope:

```text
nuevo parser
nueva authority
nuevo cálculo
cambio Supabase no requerido
nueva capability
cambio P6/P7/P8/kernel
```

### Gate B1

```text
UI_FOCAL_TESTS: PASS
CANONICAL_ROOT_UNCHANGED_SEMANTICS: PASS
LANDING/APP_BOUNDARY: EXPLICIT
```

---

## B2. Staged instance migration

Secuencia por corte:

```text
LOCAL UI PASS
→ COMMIT AISLADO
→ DEPLOY SHA EXACTO
→ CLOUD RUN REVISION NUEVA
→ 100% TRAFFIC sólo después de smoke
→ GENERAL PRODUCTION SMOKE
→ LIQ_001 REGRESSION
→ REN_001 REGRESSION
→ WORKING_CAPITAL REGRESSION
```

Rollback por revisión previa si falla smoke.

---

## B3. Persistence / multi-instance hardening

La migración de UI no debe confundirse con persistencia enterprise multi-instancia.

Alcance durable actualmente certificado:

```text
OWNER_EVIDENCE_ONLY
```

Antes de prometer restauración completa de casos tras restart/multi-instancia debe existir evidencia separada para:

```text
case snapshot durable
uploaded source restoration
result snapshot restoration
cross-revision reentry
multi-instance consistency
```

Hasta entonces: no ampliar claim.

---

# 3. Orden de ejecución

```text
A0 CORPUS CONTRACT
→ A1 STRUCTURAL MATRIX
→ A2 CALCULATION MATRIX
→ A3 RUBRO MATRIX
→ A4 ADVERSARIAL MATRIX
→ A5 REAL-CLIENT SHADOW RUNS
→ A6 PERMANENT REGRESSION CORPUS
```

Track B puede avanzar en paralelo únicamente como cambios aislados de UI/instancia que no modifiquen las authorities de Track A.

Orden recomendado inmediato:

```text
1. construir corpus inicial de 20–30 Excel
2. cubrir LIQ_001 + REN_001 + working_capital
3. ejecutar matriz física
4. clasificar divergencias
5. corregir sólo defectos reales
6. incorporar regressions
7. migrar UI enterprise por cortes pequeños a Cloud Run
8. repetir production smoke después de cada deploy
```

---

# 4. Definition of Done del programa

No existe promesa de “funciona con cualquier Excel”.

El programa se considera maduro cuando existe evidencia de cobertura por dimensiones:

```text
STRUCTURAL_COVERAGE
CALCULATION_COVERAGE
RUBRO_COVERAGE
ADVERSARIAL_COVERAGE
REAL_CASE_COVERAGE
REGRESSION_STABILITY
PRODUCTION_INSTANCE_PARITY
```

Y se mantiene:

```text
ONE_CANONICAL_PRODUCT_ROOT
FULL_SUITE_PASS
ARCHITECTURE_BASELINE_PASS
PRODUCTION_SMOKE_PASS
```

---

# 5. Regla operativa

```text
un Excel
→ una ejecución
→ una clasificación
→ una evidencia
→ una decisión
```

Nunca:

```text
un Excel raro
→ una excepción ad hoc
→ nueva deriva arquitectónica
```
