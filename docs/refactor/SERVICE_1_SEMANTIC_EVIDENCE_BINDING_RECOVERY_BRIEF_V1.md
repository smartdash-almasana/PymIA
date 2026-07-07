# SERVICE_1_SEMANTIC_EVIDENCE_BINDING_RECOVERY_BRIEF_V1

**Proyecto:** PymIA / SmartPyme / Servicio 1  
**Tipo:** Documento operativo para Codex / LLM ejecutor  
**Uso:** Continuidad técnica obligatoria antes de tocar código  
**Estado:** Diagnóstico y plan de reconstrucción  

---

# 1. Resumen en una línea

Servicio 1 hoy puede leer un Excel y entrar en triage, pero **no puede convertir columnas del Excel + respuestas del dueño + catálogos de fórmulas/patologías en un mapa semántico que habilite cómputo controlado**.

Esa es la falla.

---

# 2. Qué pasó en CASE_001

## Entrada del dueño

```text
Vendo bastante, pero no me queda claro si estoy ganando.
Tengo una planilla de ventas de junio 2026.
Quiero saber si hay algo raro.
```

## Columnas reales del Excel

```text
fecha
comprobante
producto_codigo
producto
categoria
cantidad
precio_unitario
costo_unitario
canal
venta_total
```

## Resultado real del sistema

PymIA leyó el Excel, vio columnas y filas, pero quedó detenido en triage.

Resultado observado:

```text
selected_primary_pathology = SAL_001
next_owner_question = ¿Qué columnas separan producto, canal o categoría?
allowed_computation_ref = null
package_candidate_ref = null
runtime_authorized = false
delivery_authorized = false
entrypoint_trace = {"triage_entrypoint_status": "BUILT"}
```

## Problema visible

La pregunta no sirve para este caso porque el Excel ya contiene:

```text
producto
categoria
canal
```

La pregunta correcta debería ir hacia las ambigüedades reales:

```text
¿costo_unitario es el costo real unitario aplicable a esas ventas?
¿precio_unitario es el precio final de venta?
¿venta_total surge de cantidad × precio_unitario o incluye ajustes?
```

---

# 3. Qué hace hoy el flujo real

El flujo actual se mueve así:

```text
1. Recibe enunciado del dueño.
2. Lee el XLSX.
3. Detecta columnas y filas.
4. Entra a triage de patologías hardcodeado.
5. Selecciona SAL_001.
6. Pide una pregunta genérica.
7. Se bloquea antes de cómputo.
```

El flujo real NO hace esto todavía:

```text
columnas observadas
→ significado semántico
→ variables de fórmula
→ evidencia requerida
→ patología candidata
→ pregunta precisa
→ respuesta aplicada
→ binding semántico
→ computation candidate
→ dry run
→ hallazgo
```

---

# 4. Qué debería hacer PymIA como proceso diagnóstico

El proceso correcto debe moverse así:

```text
Pedido del dueño
→ Caso abierto

Excel
→ Estructura observada

Columnas
→ Candidatos semánticos

Candidatos semánticos
+ Catálogo de fórmulas
+ Catálogo de patologías
→ Hipótesis investigables

Hipótesis investigables
→ Preguntas precisas al dueño

Respuestas del dueño
→ Mapa de datos confirmado o rectificado

Mapa suficiente
→ Plan de cómputo

Plan de cómputo
→ Tool calcula

Resultado calculado
→ Hallazgo operativo con límites
```

PymIA no debe diagnosticar por palabras.  
PymIA no debe calcular por nombres de columnas sueltos.  
PymIA no debe convertir bloqueo en éxito.  
PymIA no debe simular buen funcionamiento.

---

# 5. La pieza faltante

Falta una capa integrada que haga esto:

```text
Columnas XLSX
+ muestras de datos
+ diccionario semántico
+ catálogo de fórmulas
+ catálogo de patologías
+ respuestas del dueño
= Semantic Evidence Binding
```

Nombre de trabajo:

```text
SERVICE_1_SEMANTIC_EVIDENCE_BINDING_ENGINE_V1
```

Esta capa debe producir un mapa como:

```text
precio_venta        ← precio_unitario
costo_unitario      ← costo_unitario
volumen_vendido     ← cantidad
importe_venta       ← venta_total
producto            ← producto / producto_codigo
segmento            ← categoria / canal
fecha_operacion     ← fecha
periodo             ← junio 2026
```

Cada vínculo debe tener estado:

```text
candidate
confirmed_by_owner
missing
ambiguous
blocked
```

Sólo si el mapa es suficiente se habilita cómputo.

---

# 6. Por qué no sirve parchear CASE_001

No hacer estos parches:

```text
NO agregar sólo venta_total → importe como solución de fondo.
NO mapear SAL_001 a un computation_ref inexistente.
NO crear first_aid_ventas_basicas_v1 para hacer pasar el caso.
NO cambiar el test que hoy bloquea SAL_001 unsupported.
NO declarar que CASE_001 funciona porque llegó a una pregunta.
```

Motivo:

```text
Eso ocultaría la falla estructural.
El problema no es un alias.
El problema es que no existe binding semántico integrado.
```

---

# 7. Piezas existentes y estado real

| Pieza | Existe | Estado |
|---|---:|---|
| Lectura XLSX | Sí | Funciona |
| Detección de columnas | Sí | Funciona |
| Triage de patologías | Sí | Parcial, hardcodeado |
| Catálogo de patologías JSON | Sí | No gobierna runtime |
| Catálogo de fórmulas JSON | Sí | No gobierna runtime |
| ColumnConfirmationMatrix | Sí | Existe como isla |
| Reentry de respuestas | Sí | Persiste/proyecta, pero no recalcula |
| Pathology → computation map | Sí | Parcial, hardcodeado |
| Dry run | Sí | Sólo si llega input válido |
| Semantic Evidence Binding | No | Falta integrado |

---

# 8. Archivos principales involucrados

## Flujo XLSX-first

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_first_product_entrypoint_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_runtime_bridge_v1.py
PymIA-Live/pymia/smartpyme/service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py
```

## Triage / patologías

```text
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_entrypoint_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_loop_composition_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_intake_bridge_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_question_bundle_output_v1.py
```

## Cómputo / evidence gate

```text
PymIA-Live/pymia/smartpyme/service_1_pathology_to_allowed_computation_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_evidence_readiness_gate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_first_aid_dry_run_candidate_v1.py
```

## Column confirmation

```text
PymIA-Live/pymia/contracts/column_confirmation_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_structure_to_column_confirmation_v1.py
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_classifier_v1.py
PymIA-Live/pymia/smartpyme/service_1_owner_answers_to_column_confirmation_matrix_application_v1.py
```

## Reentry

```text
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_v1.py
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_persistence_v1.py
PymIA-Live/pymia/smartpyme/service_1_case_reentry_read_model_v1.py
PymIA-Live/pymia/smartpyme/service_1_reentry_projection_v1.py
```

## Catálogos

```text
PymIA-Live/docs/formula_catalog.v1.json
PymIA-Live/docs/pathology_catalog.v1.json
```

---

# 9. Plan de refactorización concreto

## Fase 0 — Test de caracterización del fallo actual

Crear un test que demuestre que CASE_001 queda detenido antes del binding semántico.

Archivo:

```text
PymIA-Live/tests/smartpyme/test_service_1_case_001_semantic_binding_gap_v1.py
```

Este test debe pasar porque caracteriza el fallo actual, no porque el producto funcione.

Debe verificar:

```text
selected_primary_pathology = SAL_001
allowed_computation_ref = None
next_owner_question = pregunta genérica actual
trace corta en triage
no hay dry run
no hay hallazgo
```

## Fase 1 — Contratos semánticos

Crear contratos puros:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_evidence_contracts_v1.py
```

Contratos mínimos:

```text
ColumnSemanticCandidateV1
FormulaVariableRequirementV1
ColumnVariableBindingV1
PathologyFormulaCandidateV1
SemanticEvidenceBindingResultV1
SemanticOwnerQuestionV1
```

## Fase 2 — Loader y normalizador de catálogos

Crear:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_catalog_loader_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_variable_dictionary_v1.py
```

Objetivo:

```text
Leer formula_catalog.v1.json y pathology_catalog.v1.json.
Normalizar variables y evidencia a nombres canónicos.
```

## Fase 3 — Mapper semántico de columnas

Crear:

```text
PymIA-Live/pymia/smartpyme/service_1_column_semantic_mapper_v1.py
```

Debe convertir:

```text
headers + sample_values + diccionario semántico
→ ColumnSemanticCandidateV1[]
```

## Fase 4 — Binding engine

Crear:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_evidence_binding_engine_v1.py
```

Debe cruzar:

```text
column_semantic_candidates
+ formula catalog
+ pathology catalog
+ owner confirmations
→ SemanticEvidenceBindingResultV1
```

## Fase 5 — Entry point semántico paralelo

Crear un entrypoint nuevo sin romper el viejo:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_xlsx_first_entrypoint_v1.py
```

Este entrypoint debe usar:

```text
XLSX normalized payload
→ ColumnConfirmationMatrix
→ ColumnSemanticMapper
→ CatalogLoader
→ BindingEngine
→ owner questions OR computation candidate
```

## Fase 6 — Reentry operacional semántico

Crear:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_reentry_cycle_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_case_state_v1.py
```

Debe hacer:

```text
respuesta del dueño
→ aplicar a matriz/mapa semántico
→ rerun binding engine
→ decidir si pregunta, bloquea o habilita cómputo
```

## Fase 7 — Cableado al CLI / bridge

Sólo después de que el entrypoint paralelo pase tests, conectar el CLI real.

Archivos probables:

```text
PymIA-Live/pymia/cli/service_1_xlsx_runtime_bridge.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_runtime_bridge_v1.py
PymIA-Live/pymia/smartpyme/service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py
```

## Fase 8 — Validación CASE_001 end-to-end

Recién acá CASE_001 debe llegar a:

```text
preguntas precisas
→ respuestas aplicadas
→ semantic binding suficiente
→ computation candidate
→ dry run
→ hallazgo operativo con límites
```

---

# 10. Orden obligatorio

```text
0. Test de caracterización
1. Contratos semánticos
2. Loader/normalizador de catálogos
3. Mapper semántico de columnas
4. Binding engine
5. Entry point paralelo
6. Reentry semántico
7. CLI/bridge
8. CASE_001 end-to-end
```

No saltear fases.

---

# 11. Prompt mínimo para Codex

```text
Antes de tocar código, leer:

docs/auditoria/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_FAILURE_AUDIT_V1.md
docs/arquitectura/SERVICE_1_DIAGNOSTIC_PROCESS_FLOW_TARGET_V1.md
docs/refactor/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_REFACTOR_PLAN_V1.md

Diagnóstico central:
Servicio 1 no tiene Semantic Evidence Binding integrado en el entrypoint XLSX-first.

Reglas:
- No simular buen funcionamiento.
- No parchear SAL_001.
- No inventar computation_ref.
- No cambiar tests para ocultar el defecto.
- No usar ground truth de CASE_001.
- No tocar runtime fuera de la fase autorizada.
- No git.
- No commit.
- No push.

Fase activa:
Fase 0 — crear test de caracterización del fallo actual.

Salida obligatoria:
VERDICT:
DOCS_READ:
FILES_READ:
FILES_CREATED:
FILES_MODIFIED:
TEST_COMMAND:
TEST_RESULT:
CHARACTERIZED_FAILURE:
NEXT_SAFE_ACTION:
```

---

# 12. Dónde guardar este documento

Guardar como:

```text
docs/refactor/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_RECOVERY_BRIEF_V1.md
```

No guardarlo en `docs/producto/`.

Motivo:

```text
Esto no es una capacidad de producto cerrada.
Es un documento de recuperación técnica y refactorización.
```

---

# 13. Frase de control

Si un LLM propone arreglar CASE_001 agregando aliases, mapeando SAL_001 o cambiando tests, detenerlo.

La respuesta correcta es:

```text
No se corrige el síntoma.
Primero se congela la falla.
Después se construye Semantic Evidence Binding.
```
