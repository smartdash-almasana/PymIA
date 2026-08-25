# Servicio 1 — Architecture Fitness Harness Proposal V1

**Estado:** `PROPOSAL_NOT_IMPLEMENTED`  
**Fecha/hora de registro:** `2026-08-24 14:28 ART (UTC-03:00)`  
**Origen:** decisión de continuidad posterior a R9 y previa a R10 cleanup  
**Propósito:** convertir la arquitectura de Servicio 1 en un conjunto de reglas ejecutables que detecten desvíos de circuitado, autoridades, rutas legacy y entropía antes de que obliguen a una nueva reconstrucción.

---

## 1. Problema que resuelve

Servicio 1 ya dispone de tests funcionales, architecture guards, documentación normativa y evidencia por nodo. Sin embargo, durante R0–R9 fue necesario detectar manualmente regresiones y deuda arquitectónica como:

- rutas que no transportaban D4/D7 provenance hasta P8/F7;
- tests todavía acoplados a `run_initial_pass` después de retirar la composition root legacy;
- posibles segundos roots, FSMs, parsers o motores;
- `sheet1`/filename fallbacks;
- matemática o clasificación inline;
- lectura F13 que pudiera volver a ejecutar análisis;
- desalineación entre filesystem, registry y arquitectura declarada.

La propuesta es que el repositorio falle automáticamente cuando reaparezca cualquiera de esas condiciones.

---

## 2. Piezas que ya existen físicamente

### 2.1 Graphify

Existe `graphify-out/` con `graph.json` y `GRAPH_REPORT.md`.

El reporte físico actual declara:

```text
Built from commit: aa3d873b
```

Por lo tanto está desactualizado respecto del worktree reconstruido R0–R9. Debe regenerarse una vez estabilizada la limpieza/registry y conservarse como radiografía estructural y base de comparación.

### 2.2 Pipeline Radiography

Existe:

```text
pymia/pipeline_radiography/
```

con runner, escenarios, traces y generación de reportes.

Pero el runner físico actual todavía traza una arquitectura histórica:

```text
intake
→ evidence
→ evidence_gate
→ readiness
→ runtime_bridge
→ microservice_dispatcher
→ execution_result_gate
→ delivery
```

No representa el pipeline canónico reconstruido de Servicio 1 y no puede utilizarse todavía como certificador de D1–D7/SEM/P7/P8/F7/F8/F9/F13.

### 2.3 Architecture pytest + Completion Contract

Ya existen guards y un Completion Contract que define los gates finales A01–A30 y métricas de entropía. Esos contratos deben convertirse progresivamente en checks ejecutables y agregarse a un único harness.

---

## 3. Pipeline canónico que debe vigilarse

```text
XLSX
 ↓
CanonicalIngestionOutput
 ↓
D1 → D2 → D3 → D4 → D5 → D6 → D7
                              ↓
                            SEM-8
                              ↓
                            OWNER
                              ↓
                             P7
                              ↓
                             P8
                              ↓
                             F7
                              ↓
                             F8
                              ↓
                             F9
                              ↓
                            F13
                              ↓
                     ResultReadBoundary
```

La herramienta no debe limitarse a comprobar que los nodos existen. Debe comprobar que las dependencias y rutas permitidas/prohibidas son correctas.

---

## 4. Relaciones prohibidas que deben convertirse en reglas

Ejemplos mínimos:

```text
Web        -X→ F7
Web        -X→ F8
Web        -X→ F9

LLM        -X→ F7
LLM        -X→ F8
LLM        -X→ FormulaEngine

D4         -X→ JOIN MATERIALIZATION
P8         -X→ JOIN MATERIALIZATION

F13 READ   -X→ F8
F13 READ   -X→ LLM
```

También deben ser bloqueadas automáticamente rutas que introduzcan:

```text
second productive root
fifth execution command path
parallel semantic FSM
second XLSX reader
second math engine
productive legacy shim
productive sheet1 fallback
post-build envelope mutation
workflow dispatch inferred from shape/kwargs
join materialization outside F7
LLM math/runtime authority
```

---

## 5. Herramientas candidatas

### 5.1 Import Linter

Uso propuesto: contratos de capas/imports prohibidos/ciclos arquitectónicos.

Ejemplo de objetivo:

```text
semantic
   ↓
computability
   ↓
evidence preparation
   ↓
math
   ↓
projection
```

Un import prohibido, por ejemplo Web → FormulaEngine, debe volver rojo el gate de arquitectura.

### 5.2 Grimp

Uso propuesto: consultar el grafo de imports Python para responder automáticamente preguntas específicas de PymIA:

```text
NUMBER_OF_PRODUCT_ROOTS = 1
WEB_TO_F8_PATHS = 0
LLM_TO_MATH_PATHS = 0
F13_READ_TO_EXECUTION_PATHS = 0
SECOND_SEMANTIC_FSM_PATHS = 0
```

### 5.3 Semgrep

Uso propuesto: reglas estructurales que no son sólo imports.

Patrones candidatos a bloquear:

```text
"sheet1" usado como fallback
run_initial_pass
semantic_run_override
use_assisted_semantics
pandas merge/join productivo fuera de F7
math empresarial inline en evaluadores migrados
LLM call desde math/runtime authority
filename usado como workbook identity
```

### 5.4 Graphify

Conservar como radiografía y comparación de grafo, no como autoridad única. Debe actualizarse después de estabilizar R10/R11 y puede servir para comparar `grafo certificado` vs `grafo actual`.

### 5.5 Pipeline Radiography canónica

Reconvertir la herramienta existente para producir una traza de Servicio 1 real:

```text
CanonicalIngestion  PASS
D1                  PASS
D2                  PASS
D3                  PASS
D4                  PASS
D5                  PASS
D6                  PASS
D7                  PASS
SEM                  PASS
Owner                PASS
P7                   PASS
P8                   PASS
F7                   PASS
F8                   PASS
F9                   PASS
F13                  PASS
ResultRead           PASS
```

Por transición registrar, cuando corresponda:

```text
input type
output type
source_artifact_ref
workbook_ref
sheet/schema refs
relationship_ref
owner_confirmation_event_ref
formula_ref / primitive operation
integrity digest
duration
status
blocked_reason
```

---

## 6. Interfaz objetivo

Un comando único, por ejemplo:

```text
python -m pymia.architecture_guard
```

Salida objetivo:

```text
PYMIA SERVICE 1 — ARCHITECTURE GUARD

Execution roots .................... 1 PASS
Execution commands ................. 4 PASS
Canonical XLSX readers ............. 1 PASS
Semantic FSMs ...................... 1 PASS
Legacy semantic callers ............ 0 PASS
Productive sheet1 fallbacks ........ 0 PASS
Web → F7 bypasses .................. 0 PASS
Web → F8 bypasses .................. 0 PASS
D4 → P8 provenance ................. PASS
F7 join authorities ................ 1 PASS
Math engines ....................... 1 PASS
Inline business math ............... 0 PASS
LLM → math paths ................... 0 PASS
Post-build envelope mutations ...... 0 PASS
ResultRead → recalculation paths ... 0 PASS
Registry drift ..................... 0 PASS

ARCHITECTURE: PASS
```

Debe ejecutarse como mínimo:

```text
cada cambio arquitectónico significativo
cada PR
antes del integration checkpoint
antes del full suite
antes de release/deploy
```

Un gate rojo debe detener el avance.

---

## 7. Integración propuesta con Reconstruction Plan

No desviar R10 mientras todavía se está limpiando deuda activa.

Secuencia propuesta:

```text
R10   cleanup
R11   registry reconciliation
R11.5 Architecture Fitness Harness
R12   integration checkpoint usando el harness
R13   full suite
R14   real XLSX / certification
```

`R11.5` debe ser permanente: no es sólo una tarea de reconstrucción, sino el mecanismo para impedir regresiones arquitectónicas futuras.

---

## 8. Lección operacional

La regresión R6→F12 habría sido detectada inmediatamente por un harness que exigiera explícitamente:

```text
Product Root
 → D7 evidence
 → P8
 → F7
```

La traza habría mostrado la ausencia de provenance D4/D7 en F7 antes de avanzar a nodos posteriores.

El objetivo final es que la arquitectura deje de depender de memoria humana, documentación interpretada o auditoría posterior. La arquitectura declarada debe ser una propiedad verificable del repositorio.

---

## 9. Estado de decisión

```text
ARCHITECTURE_FITNESS_HARNESS = PROPOSED
IMPLEMENTED = NO
RECOMMENDED_INSERTION_POINT = AFTER_R11_BEFORE_R12
R10_SCOPE_CHANGED = NO
```

La adopción de herramientas externas concretas debe validarse antes de fijarlas como dependencia del proyecto; la necesidad del harness y sus gates deriva directamente de la arquitectura y del Completion Contract actuales.
