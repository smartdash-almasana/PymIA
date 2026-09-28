## 24. Root Causes

Ordenadas por impacto arquitectónico (máximo 10):

```text
ROOT_CAUSE 1: El modelo de ejecución es escalar (FormulaInput/FormulaResult + generic
   _resolve_atomic_inputs) sin representación de agregación/grupo/serie.
EVIDENCE: formula_contract.py (value: float); generic _resolve_atomic_inputs suma columna entera;
          computability.governed_computation_input.grain nunca consumido.
AFFECTED_COMPONENTS: Kernel, generic engine, P8, Derived Evidence, evaluadores.
PRODUCT_IMPACT: los análisis multidimensionales del café son imposibles sin tocar 5+ capas.
SEVERITY: CRITICAL
CONFIDENCE: HIGH (code + tests)

ROOT_CAUSE 2: Dual path semántico/especializado (LIQ/REN) + menú con tres fuentes de
   verdad (_REVIEW_OPTIONS, _LAUNCH_REVIEW_OPTIONS, discovery).
EVIDENCE: root branches L482/L525; web L136/155; discovery L65+.
AFFECTED: product root, web, discovery.
PRODUCT_IMPACT: cada análisis nuevo requiere wiring manual de menú + preflight + discovery + root.
SEVERITY: HIGH
CONFIDENCE: HIGH

ROOT_CAUSE 3: Derived Evidence hardcodeada por capability (net_margin_real) y con
   agregación plana de período.
EVIDENCE: derived_evidence_v1.py CAPABILITY_NET_MARGIN / DERIVATION_*.
AFFECTED: Derived Evidence, P8, evaluadores.
PRODUCT_IMPACT: no generaliza a joins×grupo para margen por producto.
SEVERITY: HIGH
CONFIDENCE: HIGH

ROOT_CAUSE 4: Grain declarativo pero sin consumidor (P7→P8→execution ignora grain).
EVIDENCE: Service1GrainV1 + Grain en P7/P8; sin group_by en ningún plan.
AFFECTED: P7, P8, evaluadores.
PRODUCT_IMPACT: no hay forma de pedir "ventas por sucursal" a la máquina.
SEVERITY: HIGH
CONFIDENCE: HIGH

ROOT_CAUSE 5: Registry/generic cubren fórmulas escalares simples (ADD/SUB/MUL/DIV),
   sin funciones de agregación (GROUP BY, SUM_GROUP, RANK, PERCENT, cuenta de filas).
EVIDENCE: FormulaNodeV1 ops en capability_contracts_v1; _evaluate_formula sólo 4 ops.
PRODUCT_IMPACT: ticket promedio, ranking, mix no se pueden expresar.
SEVERITY: HIGH
CONFIDENCE: HIGH

ROOT_CAUSE 6: Fixtures físicos de controles positivos/matrix faltan en el worktree
   (S1-PHY-005/006/007, S1-POS-001/002/003).
EVIDENCE: prueba_excels no contiene cobros_marzo_2026.xlsx / taller_mecanico... /
          first_aid_pilot_004... / SERVICE_1_PHYSICAL_POSITIVE_*.xlsx; ejecución real.
AFFECTED: tests físico de matriz P6/P7/P8 + controles positivos.
PRODUCT_IMPACT: evidencia de regresión física degradada (3+1 tests rojos).
SEVERITY: MEDIUM
CONFIDENCE: HIGH (verificado con pytest)

ROOT_CAUSE 7: Drift de fórmulas catálogo vs implementación (PYME_026/PYME_013 no en
   kernel; PYME_004/047/M05/OPE_001 declaradas y no implementadas).
EVIDENCE: formula_catalog.v1.json vs SUPPORTED_FORMULAS vs registry.
PRODUCT_IMPACT: P8 puede bloquear capabilities que sí tienen fórmula en registry pero no
   en kernel (o al revés).
SEVERITY: MEDIUM
CONFIDENCE: HIGH

ROOT_CAUSE 8: Ruta workbook-first (F2/F3 worktree) no persiste owner evidence durable
   (no llama _persist_owner_confirmation_events).
EVIDENCE: reception_v1 _confirm_workbook_first -> _post_semantic_analysis_menu_page sin persist;
          web_v1 run_review sí llama.
PRODUCT_IMPACT: memoria semántica del tenant incompleta en el nuevo journey.
SEVERITY: MEDIUM (bug F3)
CONFIDENCE: HIGH

ROOT_CAUSE 9: Tools/landing usan openpyxl para contexto chat demostrativo (duplicación
   de lectura de excel fuera del parser canónico).
EVIDENCE: landing/build_service1_excel_ingestion_chat_web.py `_build_file_context`.
PRODUCT_IMPACT: riesgo de que un futuro componente re-parsee sin gobernar; no es
   productivo hoy.
SEVERITY: LOW
CONFIDENCE: HIGH (no es ruta productiva)

ROOT_CAUSE 10: Memory brain sin serie longitudinal y con snapshot de resultado no durable
   (documentado como deuda).
SEVERITY: MEDIUM (producto "evolución" no soportable).
CONFIDENCE: HIGH (documentado + código _remember_case)
```

---

## 25. Components to KEEP

| Componente | Razón |
|---|---|
| `service_1_xlsx_to_normalized_table_v1.py` (único parser) | Cumple NO_SECOND_XLSX_PARSER; robusto y fail-closed |
| `WorkbookProfiler` | Valor estructural real; bajo riesgo |
| `service_1_p6_approval_decision_v1.py` | Autoridad semántica por columna correcta |
| `service_1_computability_v1.py` (P8 + GovernedInput) | La autoridad de computabilidad correcta |
| `FormulaEngineService` (kernel escalar) | Autoridad matemática válida para fórmulas escalares; preservable |
| `service_1_derived_evidence_v1.py` | Patrón correcto de derivación gobernada; hay que generalizar no reemplazar |
| `service_1_xlsx_delivery_v1.py` | Deterministic delivery con quality gate |
| `service_1_tenant_semantic_contract_*.py` | Memoria semántica durable correcta |
| `service_1_workbook_profiler_v1.py` | Relaciones candidatas útiles |
| `AssistantSemanticReception` (F2 sandwich) | El camino workbook-first es correcto |

---

## 26. Components to EXTEND

| Componente | Extensión requerida |
|---|---|
| `FormulaNodeV1`/registry | Añadir operadores de agregación: `SUM_GROUP`, `COUNT`, `RANK`, `PERCENT_TOTAL`, `AVG_GROUP`, filtros por valor |
| `Service1GrainV1` | Añadir `group_columns`, `order`, `limit` (o measure semantics) y `temporal_bin` (day/hour/week) |
| `GovernedComputationInputV1` | Añadir `aggregation_plan` (group_by + measures) además de `source_bindings` |
| `build_service_1_computability_decision_v1` | Permitir N conjuntos de inputs (por grupo) y validar aggregation plan |
| `service_1_derived_evidence_v1` | Generalizar de capability única a "join spec" + "group measures" (sin hardcodear REN_001) |
| `_capability_relevant_roles` | Extender a roles de grupo (sucursal, categoría, hora, empleado, canal) |
| `service_1_assisted_web_*` | En F3: llamar `_persist_owner_confirmation_events` en la ruta workbook-first |

---

## 27. Components to GENERALIZE

| Componente | Generalización |
|---|---|
| `execute_generic_capability_v1` | De "suma de columna" a "evaluate aggregation plan por grain"; los evaluadores LIQ/REN podrían convertirse en "measure specs" dentro del registry |
| Evaluadores especializados LIQ_001/REN_001 | Converger a un único evaluador genérico que reciba `aggregation_plan` (manteniendo los evaluadores actuales como compat wrapper) |
| `_REVIEW_OPTIONS`/`_LAUNCH_REVIEW_OPTIONS`/discovery | Una sola fuente: registry → menú derivado dinámicamente por P8 |
| Owner evidence projection | Generalizar de "por columna" a "por columna + por relación + por grupo (material)" |

---

## 28. Components to CONVERGE / DEPRECATE / REPLACE

```text
CONVERGE:
  - Familia SALES_MARGIN/PERIOD_NET_MARGIN: unificarlas con plan de agregación
  - SUPPORTED_FORMULAS (kernel) y FormulaNodeV1 (registry): un solo contrato de fórmula
  - run_owner_reentry (adapter legacy) -> deprecar; unificar en reentrada canónica

DEPRECATE:
  - _available_launch_review_options_v1 (preflight por roles) -> reemplazar por P8 discovery
  - _review_selection_page legacy (12 options sin preflight) -> reemplazar por menú
    post-semantics (discovery)
  - _REVIEW_OPTIONS 12 -> derivarse del registry + matrix

REPLACE:
  - landing/demo chat parser (openpyxl en build_service1_excel_ingestion_chat_web)
    no es productivo; si se vuelve productivo, debe usar el parser canónico.
  - NO reemplazar el Kernel; reemplazar el "modelo de ejecución" por un sub-motor de
    agregación sobre el mismo kernel (ver §29).
```

---

## 29. Recommended Target Architecture

Objetivo: que agregar "ventas por producto" no requiera 8 toques. Diseño mínimo que preserva todo lo sano:

```text
[ Proposal ]
1. Introducir "AnalysisPlan V1":
   kind: SINGLE_VALUE | GROUPED | SERIES
   measures: [ {variable, op: SUM|COUNT|AVG, multiplier?, denominator?} ]
   group_by: {variable, granularity} | none
   filter: [{role, pred}] | none
   join: [{left_relation_ref, right_sheet}] | none
   grain_reference: Service1GrainV1

2. Extender P7 para emitir "requirement matches por plan" (P7 sigue siendo la autoridad
   de requisitos y grain; ahora el grain es *computable*).

3. Extender P8 para validar "plan" (formula_ref + measures + group_by) y producir
   GovernedComputationInputV1 + aggregation_plan. Repetir por grupo si hace falta.

4. Nuevo "AggregationExecutorV1" que:
   - consume GovernanceInput + normalized_tables + column_refs
   - ejecuta GROUP BY / SUM / COUNT / RANK / PERCENT sobre columnas confirmadas
   - produce {group_key: {measures...}} con provenance por grupo
   - NUNCA decide semántica ni inventa inputs
   El Kernel queda como autoridad de fórmulas *post-agregación* (p.ej. margen =
   kernel(margen_bruto, {ventas: sum(group), costos: sum(group)})).

5. Registry: cada capability pasa a tener "analysis_plan" + "formula" (el registry
   ya tiene formula; sumar measures/granularity/group). LIQ_001/REN_001 se
   re-expresan como capabilities con plan SINGLE_VALUE para mantener el behavior.

6. Delivery: un outcome genérico por capability (dict de grupos) + XLSX multiline por
   grupo; preservando bounded findings/limitations por grupo.

7. Menú: derivado de P8 (discovery) — registry + confirmed bindings + aggregation plan
   => disponibilidad real. Eliminar el preflight por roles y la lista manual.
```

El **Kernel se conserva en su rol** (fórmulas post-agregación y escalares); la agregación vía nuevo executor NO compite con el Kernel: es la capa de *derivación estructural* (el mismo rol que hoy juega Derived Evidence, pero parametrizado por plan en vez de hardcodeado).

---

## 30. Incremental Migration Plan

Fases incrementales, cada una con ROLLBACK_BOUNDARY:

```text
FASE A (objetivo: cerrar F3 y evidencia física)
  OBJECTIVE: commitear F2/F3 + arreglar persistencia owner en ruta workbook-first,
             y restaurar/añadir fixtures faltantes de controles positivos/matrix.
  ROOT_CAUSE_RESOLVED: 8, 6
  COMPONENTS_TOUCHED: service_1_assisted_web_semantic_reception_v1,
                      service_1_assisted_web_v1, prueba_excels/, tests físico
  INVARIANTS_PRESERVED: todos
  RISKS: bajo; sólo wiring + fixtures
  ACCEPTANCE_EVIDENCE: los 4 tests rojos pasan; post-discovery persiste eventos
  ROLLBACK_BOUNDARY: revertir el commit del patch; no toca kernel/root

FASE B (objetivo: unificación del menú)
  OBJECTIVE: una sola fuente de disponibilidad (P8 discovery) reemplaza preflight roles
             y _REVIEW_OPTIONS manual.
  ROOT_CAUSE_RESOLVED: 2
  COMPONENTS_TOUCHED: service_1_assisted_web_v1 (menú), reception (discovery ya),
                      tests UI
  ACCEPTANCE_EVIDENCE: menú idéntico en las 3 rutas; ninguna capability nueva requiere
                       tocar UI
  ROLLBACK_BOUNDARY: flag de feature (mantener preflight por defecto)

FASE C (objetivo: plan de agregación gobernado)
  OBJECTIVE: extender P7/P8 + GovernedInput con aggregation_plan; añadir operadores
             al registry (SUM_GROUP etc).
  ROOT_CAUSE_RESOLVED: 3, 4, 5
  COMPONENTS_TOUCHED: computability, capability_contracts, registry, generic engine,
                      P7 families, tests
  INVARIANTS: P8 sigue siendo autoridad de computabilidad; kernel sigue siendo formula
              authority (sólo post-agregación)
  RISKS: cambio de contrato en GovernedInput -> tests de compat (wrappers)
  ROLLBACK_BOUNDARY: versionar schema service_1_governed_computation_input_v1 -> v2,
                     mantener v1 aceptado

FASE D (objetivo: capabilities grupales/escalables del café)
  OBJECTIVE: primera capability GROUPED productiva (ventas por producto; luego ventas
             por sucursal; ticket promedio).
  ROOT_CAUSE_RESOLVED: 1 (deja de ser blocker)
  COMPONENTS_TOUCHED: registry (nueva capability con plan), generic engine (GROUP),
                      outcome genérico, UI (derived menu), tests
  INVARIANTS: fail-closed, no inventar evidencia, bounded findings
  RISKS: volumen de datos (5000 filas ok; millones -> streaming simple)
  ROLLBACK_BOUNDARY: capability no autorizada en producción hasta test+e2e

FASE E (objetivo: Derived Evidence generalizada)
  OBJECTIVE: spec de join + group measures; REN_001 re-expresado sobre plan;
             desactivar hardcode.
  ROOT_CAUSE_RESOLVED: 3
  COMPONENTS: derived_evidence -> spec-driven; tests REN_001 re-baseline
  ROLLBACK_BOUNDARY: mantener derived_evidence_v1 como fallback por capacidad

FASE F (objetivo: memoria completa)
  OBJECTIVE: persistir resultado durable + serie longitudinal (por tipo de capability)
  ROOT_CAUSE_RESOLVED: 10
  INVARIANTS: resultado histórico inmutable
```

---

## 31. Risk Assessment

```text
HIGH:
  - Cambiar GovernedComputationInputV1 sin compat rompe P8/evaluadores (mitigar: v2 + wrapper)
  - Añadir agregación sin modelo de grain provoca "ventas por sucursal" mal agregadas
    en producción (mitigar: P7/P8 autorizan el plan; fail-closed si no cubre bindings)
  - Menú único derivado puede ocultar análisis computables si P8 falla (mitigar:
    discovery devuelve bloqueados con causa, nunca silencio)

MEDIUM:
  - Drift fórmula kernel vs registry (PYME_026/PYME_013)
  - Fixtures faltantes degradan regresión física (arreglar en Fase A)
  - F3 persistencia: confirmaciones del nuevo journey no duran (bug abierto)

LOW:
  - Parser demo en landing (no productivo)
  - Dual path semántico (mantenimiento)
```

---

## 32. Final Answers to the 17 Mandatory Questions

```text
1. ¿Servicio 1 es arquitectura general o colección de verticales?
   > GENERALIZABLE CON EVOLUCIÓN DIRIGIDA. La base (P6/P7/P8/kernel/derived/registry/web)
   es general. El "techo" está en el modelo de ejecución escalar mono-capability.

2. ¿Cuánto del producto general existe realmente?
   > ~9-10 de 15 apoyos del journey SUPPORTED. Computable hoy: 10 capabilities de la
   matrix (AL MENOS 3 con camino productivo: LIQ_001, REN_001, working_capital).

3. ¿Qué limita hoy que cafeteria_abc.xlsx produzca todos los análisis legítimos?
   > 1) No hay plan de agregación/grupo; 2) no hay fórmulas de ventas/margen por grupo;
   3) no hay rol de grupo por sucursal/hora/categoría con consumidor; 4) las capabilities
   existentes son escalares y exigen evidencia que el café no tiene (cobranzas, caja).

4. ¿El problema principal es semántico, P7/P8, grain, Derived, Kernel, capability,
   product wiring o combinación?
   > COMBINACIÓN de P7/P8/grain + Derived + capability model + Kernel (escalar),
   todos en el mismo "aggregation ceiling". NO es semántica (la semántica funciona).

5. ¿Hay matemática fuera del Kernel?
   > SÍ: agregación SUM en evaluadores/generic y multiplicación/join en Derived
   Evidence; y un par de fórmulas en registry sin kernel.

6. ¿Eso viola materialmente la arquitectura o es derivación legítima?
   > ES DERIVACIÓN/AGREGACIÓN LEGÍTIMA (el kernel ejecuta la fórmula final). No
   viola el invariante bajo la interpretación documentada, pero la regla debería
   formalizarse: "kernel = fórmula final; agregación/derivación = capa especificada".

7. ¿FormulaEngineService debe preservarse, generalizarse o reemplazarse?
   > PRESERVARSE (fórmulas escalares) y COMPLEMENTARSE con un executor de agregación
   especificado; NO reemplazarlo.

8. ¿Puede evolucionarse sin destruirlo?
   > SÍ: el kernel ya está aislado; añadir aggregation_plan en P8/GovernedInput y un
   nuevo executor por encima NO toca SUPPORTED_FORMULAS.

9. ¿P7/P8 pueden soportar análisis multidimensionales?
   > HOY NO de forma computable (grain declarativo ignorado). CON el plan de
   agregación (Fase C) sí.

10. ¿El modelo de capability actual escala a cientos de análisis?
    > A cientos de *fórmulas escalares* SÍ. A cientos de *análisis grupales* NO
    (requiere plan + group executor + outcome genérico).

11. ¿Cuántas capacidades del café ya están casi resueltas pero no conectadas?
    > ~4-5 (ventas brutas, unidades, ticket, mix sucursal, ranking) — dependen de
    fórmulas/plans que faltan pero cuya semántica ya está disponible.

12. ¿Cuántas requieren nueva matemática?
    > ~7 (ventas netas con descuento, ranking, participación, ticket promedio,
    ventas por producto/sucursal/categoría, margen bruto por producto).

13. ¿Cuántas requieren sólo nueva derivación?
    > ~3 (margen por producto/sucursal/categoría: join ProductoID + group).

14. ¿Cuántas requieren nuevo grain?
    > ~10 (todas las grupales requieren grain product/sucursal/categoría/hora/día).

15. ¿Cuántas son imposibles por ausencia de evidencia?
    > ~2-3 (margen neto real sin impuestos; working capital sin caja; DSO sin
    cuentas por cobrar). El sistema ya las bloquea correctamente.

16. ¿Qué arquitectura evita hardcodear cafetería, retail, distribución, consorcios...?
    > la que hace a P7/P8 emitir "analysis plans" parametrizados por grain+measures
    sobre bindings confirmadas, y registry como única fuente de capability; el rubro
    entra como *grain y roles*, nunca como código.

17. ¿Cuál es la mínima evolución arquitectónica que convierte Servicio 1 en el
    producto general pretendido?
    > analysis_plan (grain+group+measures) en P7/P8 + executor de agregación + registry
    como menú único + outcome genérico. Ese es el mínimo; Fases B/C del plan.
```

---

## 33. Final Verdict

```text
FINAL VERDICT: TARGETED_EVOLUTION_REQUIRED

Arquitectura: ARCHITECTURE_GENERALIZABLE_WITH_TARGETED_EVOLUTION

No es una colección de verticales sin generalización: la separación de autoridades,
el pipeline canónico y el journey workbook-first (F2) son la base correcta. La
evolución dirigida es:

1. cerrar F3 (persistir owner evidence en ruta workbook-first) y restaurar fixtures;
2. una sola fuente de disponibilidad (P8 discovery);
3. aggregation_plan + executor de agregación sobre bindings confirmadas;
4. registry/declaración como menú único;
5. memoria de ejecución durable + serie longitudinal.

Fases A-F. Ningún componente sano se pierde; el Kernel se preserva. El ceiling real
del producto general está en el "modelo de agregación por grain", no en la semántica
ni en el gobierno.
```

---

**Nota de evidencia final:** toda afirmación de "PASS"/"certificado" de este informe se limita al estado físico verificado en el worktree y a las ejecuciones listadas en §3.3. Ninguna afirmación de producción certificada (LIQ_001/REN_001/working_capital) es válida para HEAD `4cda16d` ni para el worktree F2/F3 sin commitear.
