# SERVICE_1_SEMANTIC_EVIDENCE_BINDING_FAILURE_AUDIT_V1

**Proyecto:** PymIA / SmartPyme / Servicio 1  
**Tipo:** Auditoría técnica de falla estructural  
**Caso detonante:** `CASE_001_MARGIN_LEAK_MISSING_COSTS`  
**Archivo XLSX:** `prueba_excels\CASE_001_ventas_junio_2026_margin_leak.xlsx`  
**Fecha de informe:** 2026-07-07  
**Estado:** `FAIL_DE_INTEGRACION_ARQUITECTONICA`  

---

## 1. Propósito del informe

Este informe documenta el problema técnico detectado en el flujo real de Servicio 1 durante la ejecución de `CASE_001`, donde PymIA logró leer y normalizar un XLSX, pero no pudo avanzar desde triage hacia consolidación semántica, fórmula candidata, cómputo controlado ni hallazgo operativo.

El objetivo no es justificar el estado actual ni proponer parches superficiales. El objetivo es dejar una pieza técnica de referencia para reconstruir el tramo roto sin seguir agregando humo documental, alias sueltos o microcomponentes desconectados.

---

## 2. Veredicto ejecutivo

```text
VERDICT:
FAIL — el flujo XLSX-first no tiene Semantic Evidence Binding integrado.
```

El sistema tiene varias piezas parciales correctas, pero están funcionando como islas:

```text
isla XLSX runtime
isla triage hardcodeado
isla column confirmation
isla owner reentry
isla formula catalog
isla pathology catalog
isla dry run
```

La falla principal no es `SAL_001`, ni un alias faltante, ni la respuesta del dueño. Es una falla de integración arquitectónica:

```text
NO HAY UNA CAPA INTEGRADA QUE CONECTE:
columnas XLSX observadas
→ significado semántico de columnas
→ variables de fórmulas
→ evidencia requerida
→ patologías candidatas
→ preguntas al dueño
→ mapa semántico consolidado
→ computation candidate
→ hallazgo operativo
```

---

## 3. Contexto del caso `CASE_001`

### 3.1 Narrativa del dueño usada en corrida ciega

```text
Vendo bastante, pero no me queda claro si estoy ganando.
Tengo una planilla de ventas de junio 2026.
Quiero saber si hay algo raro.
```

### 3.2 Columnas detectadas en el XLSX

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

### 3.3 Resultado operativo observado

```text
normalized_status: OK
row_count: 24
column_count: 10
pilot_status: REAL_OWNER_NEEDS_OWNER_INPUT
adapter_status: DELIVERY_PACKET_NEEDS_OWNER_INPUT
bridge_status: BRIDGE_NEXT_OWNER_QUESTION
pilot_pack_status: PILOT_PACK_NEEDS_OWNER_INPUT
selected_primary_pathology: SAL_001
allowed_computation_ref: null
package_candidate_ref: null
runtime_authorized: false
delivery_authorized: false
entrypoint_trace: {"triage_entrypoint_status": "BUILT"}
```

### 3.4 Pregunta repetida por el sistema

```text
¿Qué columnas separan producto, canal o categoría?
```

### 3.5 Respuesta legítima del dueño en reentry

```text
La columna producto identifica el producto vendido.
La columna categoria agrupa el tipo de producto.
La columna canal indica por dónde se vendió: local, web, mayorista o marketplace.
```

### 3.6 Resultado después de reentry

El estado no cambió:

```text
bridge_status = BRIDGE_NEXT_OWNER_QUESTION
pilot_pack_status = PILOT_PACK_NEEDS_OWNER_INPUT
allowed_computation_ref = null
package_candidate_ref = null
runtime_authorized = false
delivery_authorized = false
```

Interpretación:

```text
La respuesta del dueño no fue consumida por una capa de resolución semántica.
Fue tratada como string plano o metadata, no como confirmación estructurada aplicable.
```

---

## 4. Call graph real del flujo ejecutado

El flujo real de `CASE_001` no usa todos los componentes existentes. La cadena ejecutada fue:

```text
CASE_001_reentry_001_column_confirmation.py
→ read_xlsx_to_normalized_table_v1
→ build_service_1_real_owner_pilot_case_run_v1
→ build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1
→ build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1
→ build_service_1_xlsx_runtime_bridge_v1
→ build_service_1_xlsx_first_product_entrypoint_v1
→ build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1
→ build_service_1_pathology_anamnesis_triage_loop_composition_v1
→ build_service_1_pathology_anamnesis_triage_intake_bridge_v1
→ create_service_1_anamnesis_record_v1
→ build_service_1_anamnesis_triage_decision_v1
→ build_service_1_pathology_anamnesis_triage_question_bundle_output_v1
```

La cadena se corta antes de:

```text
build_service_1_pathology_to_allowed_computation_candidate_v1
build_service_1_pathology_evidence_readiness_gate_v1
build_service_1_controlled_computation_plan_v1
build_service_1_pathology_first_aid_dry_run_candidate_v1
build_service_1_operational_finding_owner_view_v1
build_service_1_pathology_finding_delivery_policy_guard_v1
build_service_1_pathology_finding_delivery_package_v1
```

Evidencia:

```text
entrypoint_trace = {"triage_entrypoint_status": "BUILT"}
```

Esto significa que Servicio 1 quedó en triage y no pasó a evidencia/cómputo.

---

## 5. Piezas auditadas

Se revisaron, directa o indirectamente, las siguientes piezas de código y datos:

```text
PymIA-Live/pymia/smartpyme/service_1_real_owner_pilot_case_run_v1.py
PymIA-Live/pymia/smartpyme/service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_runtime_bridge_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_first_product_entrypoint_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_entrypoint_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_loop_composition_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_intake_bridge_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_anamnesis_triage_question_bundle_output_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_to_allowed_computation_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_evidence_readiness_gate_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_first_aid_dry_run_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_v1.py
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_persistence_v1.py
PymIA-Live/pymia/smartpyme/service_1_case_reentry_read_model_v1.py
PymIA-Live/pymia/smartpyme/service_1_reentry_projection_v1.py
PymIA-Live/pymia/smartpyme/service_1_question_bundle_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_structure_to_column_confirmation_v1.py
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_classifier_v1.py
PymIA-Live/pymia/smartpyme/service_1_owner_answers_to_column_confirmation_matrix_application_v1.py
PymIA-Live/pymia/contracts/column_confirmation_v1.py
PymIA-Live/docs/formula_catalog.v1.json
PymIA-Live/docs/pathology_catalog.v1.json
PymIA-Live/tests/smartpyme/test_service_1_pathology_to_allowed_computation_candidate_v1.py
PymIA-Live/tests/smartpyme/test_service_1_xlsx_first_product_entrypoint_v1.py
```

---

## 6. Diagnóstico técnico por componente

### 6.1 XLSX normalization

**Estado:** `OK`

La normalización funcionó:

```text
24 filas
10 columnas
headers detectados correctamente
```

No hay evidencia de que el problema esté en la lectura XLSX.

---

### 6.2 `service_1_real_owner_pilot_case_run_v1.py`

**Rol:** wrapper de caso real/piloto.

Recibe narrativa, ingestión y confirmaciones planas. Luego delega al adapter.

**Problema:** no consume ni aplica reentry estructurado. Sólo pasa `column_meaning_confirmations` como tuple de strings.

**Impacto:** no puede transformar respuestas del dueño en mapa semántico operativo.

---

### 6.3 `service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py`

**Rol:** adapta output de ingestión al bridge XLSX runtime.

Extrae:

```text
available_data_fields
input_values
source_file_ref
declared_data_sources
```

**Problema:** arma un `normalized_payload`, pero no construye ni consume:

```text
ColumnConfirmationMatrix
SemanticDataMap
FormulaVariableBinding
PathologyEvidenceCandidate
```

**Impacto:** el bridge recibe campos planos y pierde la riqueza semántica de columnas/valores.

---

### 6.4 `service_1_xlsx_runtime_bridge_v1.py`

**Rol:** puente hacia entrypoint XLSX-first.

**Problema:** su función es de composición, no de semántica. Pasa los datos al entrypoint sin resolver bindings.

**Impacto:** la cadena depende de que el entrypoint pueda resolver semántica, pero el entrypoint tampoco tiene esa capacidad.

---

### 6.5 `service_1_xlsx_first_product_entrypoint_v1.py`

**Rol:** entrypoint puro del flujo XLSX-first.

Secuencia interna:

```text
triage_entrypoint
→ allowed_computation_candidate
→ evidence_readiness_gate
→ computation_plan
→ dry_run
→ owner_view
→ policy_guard
→ package_candidate
```

**Problema:** la secuencia sólo avanza si `triage_entrypoint.status == NO_OWNER_QUESTIONS_REQUIRED`.

En `CASE_001`, el trace fue:

```text
triage_entrypoint_status = BUILT
```

Eso activa:

```text
STATUS_NEXT_OWNER_QUESTION
```

y corta la cadena antes de evidence/computation.

**Impacto:** cualquier falla semántica en triage bloquea todo el resto del sistema.

---

### 6.6 `service_1_pathology_anamnesis_triage_contract_v1.py`

**Rol:** contrato hardcodeado de triage/anamnesis.

Define internamente:

```text
_PATHOLOGY_DEFINITIONS
_FIELD_ALIASES
```

Contiene pocas patologías:

```text
LIQ_001
REN_001
STK_001
CST_001
SAL_001
CSH_001
```

**Problema 1:** no lee `pathology_catalog.v1.json`.

**Problema 2:** no lee `formula_catalog.v1.json`.

**Problema 3:** no trabaja con fórmulas, sólo con `required_evidence` y alias locales.

**Problema 4:** `column_meaning_confirmations` sólo se usa como presencia, no como estructura semántica.

Función crítica:

```python
def _owner_confirmation_missing(...):
    if business_period_reference is None:
        return True
    if not declared_data_sources:
        return True
    if not column_meaning_confirmations:
        return True
    return False
```

Esto significa:

```text
hay strings → hay confirmación
no hay strings → falta confirmación
```

No significa:

```text
producto fue confirmado como producto vendido
categoria fue confirmada como agrupador comercial
canal fue confirmado como canal de venta
venta_total fue confirmada como importe de venta
```

**Impacto:** se simula una confirmación por presencia, pero no se consolida semántica.

---

### 6.7 `SAL_001` en triage

En runtime, `SAL_001` significa:

```text
Mezcla de ventas sin segmentación
```

Requiere:

```text
fecha
producto_servicio
importe
```

Pregunta:

```text
¿Qué columnas separan producto, canal o categoría?
```

**Problema local:** el XLSX trae `venta_total`, pero los alias de `importe` son:

```text
importe
monto
total
importe_total
```

No incluyen:

```text
venta_total
```

**Impacto local:** `SAL_001` puede quedar como evidencia incompleta aunque el Excel tenga la columna de total vendido.

**Advertencia:** esto explica un síntoma, pero no resuelve la arquitectura. Agregar un alias no reconstruye el flujo.

---

### 6.8 `service_1_pathology_to_allowed_computation_candidate_v1.py`

**Rol:** mapear patología a cómputo permitido.

Mapa actual:

```text
REN_001 → first_aid_precio_margen_basico_v1
LIQ_001 → first_aid_caja_diaria_triage_v1
STK_001 → first_aid_stock_alertas_basicas_v1
CSH_001 → first_aid_caja_diaria_triage_v1
```

No incluye:

```text
SAL_001
```

El test lo confirma:

```text
test_returns_blocked_for_unsupported_pathology
pathology_code="SAL_001"
expected: BLOCKED_UNSUPPORTED_PATHOLOGY
allowed_computation_ref is None
```

**Impacto:** incluso si `SAL_001` superara triage, no tendría cómputo permitido.

**Conclusión:** el camino de margen disponible en runtime pasa por `REN_001`, no por `SAL_001`.

---

### 6.9 `service_1_pathology_evidence_readiness_gate_v1.py`

**Rol:** validar si hay evidencia suficiente para plan de cómputo.

**Problema:** depende del `allowed_computation_candidate`, que a su vez depende de mapas hardcodeados. No lee catálogo de fórmulas ni catálogo de patologías.

También usa su propio `_FIELD_ALIASES`, duplicado respecto de otros módulos.

**Impacto:** hay múltiples fuentes de verdad para alias/variables, con riesgo de divergencia.

---

### 6.10 `service_1_pathology_first_aid_dry_run_candidate_v1.py`

**Rol:** construir dry-run candidate para cómputos soportados.

Soporta:

```text
first_aid_precio_margen_basico_v1
first_aid_caja_diaria_triage_v1
first_aid_stock_alertas_basicas_v1
```

Para margen requiere:

```text
precio_venta
costo_unitario
volumen_vendido
```

**Problema:** esta pieza podría calcular si recibe los inputs correctos, pero el flujo no llega hasta acá en `CASE_001`.

**Impacto:** el cómputo no está roto como función aislada; está inaccesible desde el flujo real por falta de binding semántico previo.

---

### 6.11 `formula_catalog.v1.json`

**Estado:** existe.

Contiene:

```text
formula_id
pathology_code
expression
display_expression
required_variables
required_evidence
calculation_state
interpretation
```

Ejemplo:

```text
REN_001_margen_neto_real
pathology_code: REN_001
required_variables: sale_price, costs, taxes
required_evidence: ventas_del_periodo, costos_directos, impuestos_y_comisiones
```

**Problema:** el runtime XLSX-first no lo carga.

**Impacto:** el catálogo de fórmulas no gobierna las decisiones operativas.

---

### 6.12 `pathology_catalog.v1.json`

**Estado:** existe.

Contiene 50 patologías.

**Problema:** el runtime usa su propio diccionario local de pocas patologías.

**Impacto:** hay dos mundos de patología:

```text
catálogo documental/machine-readable
runtime hardcodeado
```

Esto genera deriva inevitable.

---

### 6.13 Column confirmation contract

Archivo:

```text
PymIA-Live/pymia/contracts/column_confirmation_v1.py
```

Tiene piezas útiles:

```text
ColumnConfirmationMatrix
ColumnConfirmationEntry
OwnerColumnConfirmationAnswer
ConfirmationStatus
OwnerColumnConfirmationOutcome
CalculationRelevance
SemanticRectificationStatus
```

También tiene noción de relevancia:

```text
VENTAS
COSTOS
MARGEN
STOCK
PAGOS
CANTIDADES
SEGMENTATION
INFORMATIONAL
```

**Problema:** no está integrado al flujo `service_1_xlsx_first_product_entrypoint_v1`.

**Impacto:** la confirmación de columnas existe como isla contractual, no como paso obligatorio antes del evidence gate.

---

### 6.14 `service_1_xlsx_structure_to_column_confirmation_v1.py`

**Rol:** generar una matriz de confirmación desde estructura XLSX.

Construye entradas con:

```text
original_column_name
sheet_name
sample_values
inferred_type
suggested_semantic_role
suggested_data_type
calculation_relevance
confidence
owner_question
confirmation_status
```

**Problema:** inicializa `suggested_semantic_role` como `unknown` y `calculation_relevance` como `INFORMATIONAL`.

No hay motor semántico fuerte que proponga roles ricos.

**Impacto:** sirve como contenedor, pero no como resolver semántico.

---

### 6.15 `service_1_column_confirmation_classifier_v1.py`

**Rol:** clasificar texto del dueño como respuesta a una pregunta de confirmación de columna.

Tiene alias normalizables limitados:

```text
saldo
payment_method
venta_total
cantidad
producto
```

Faltan roles críticos para `CASE_001`:

```text
fecha
producto_codigo
categoria
canal
precio_unitario
costo_unitario
```

Además, el parser favorece respuestas en patrón:

```text
tu respuesta: ...
```

La respuesta natural del dueño:

```text
La columna producto identifica el producto vendido.
```

no queda bien absorbida por ese contrato.

**Impacto:** incluso si se usara esta pieza, su volumen semántico actual sería insuficiente.

---

### 6.16 `service_1_owner_answers_to_column_confirmation_matrix_application_v1.py`

**Rol:** aplicar respuestas clasificadas a una matriz.

Correctamente no clasifica free text ni autoriza runtime.

**Problema:** no está en el flujo CASE_001.

**Impacto:** la respuesta del dueño nunca actualiza una matriz semántica que luego alimente evidencia/cómputo.

---

### 6.17 Reentry general

Archivos:

```text
service_1_owner_answer_reentry_v1.py
service_1_owner_answer_reentry_persistence_v1.py
service_1_case_reentry_read_model_v1.py
service_1_reentry_projection_v1.py
```

Estas piezas hacen:

```text
bind answer
persist answer
load answers
project answered/pending
```

Declaran explícitamente que no hacen:

```text
no apply column confirmation
no recalculate evidence
no rerun pipeline
```

**Impacto:** existe reentry administrativo, no reentry operacional aplicado.

---

## 7. Diagnóstico de root cause

### 7.1 Causa raíz principal

```text
El flujo XLSX-first carece de Semantic Evidence Binding integrado.
```

### 7.2 Causas secundarias

```text
1. Los catálogos JSON existen pero no gobiernan runtime.
2. El triage usa diccionarios hardcodeados.
3. Hay alias duplicados en varios módulos.
4. Column confirmation existe como isla, no como gate integrado.
5. Owner reentry existe como persistencia/proyección, no como actualización semántica.
6. Fórmula/cómputo existe, pero sólo se alcanza si el path hardcodeado llega a REN_001 con campos simples.
7. No existe estructura central para Column → SemanticRole → FormulaVariable → EvidenceRequirement.
```

---

## 8. Qué NO debe hacerse

No hacer:

```text
- Agregar venta_total como alias de importe y cantar victoria.
- Mapear SAL_001 a first_aid_precio_margen_basico_v1 sin contrato.
- Forzar que CASE_001 elija REN_001 por string matching.
- Meter respuestas del dueño como strings planos en column_meaning_confirmations.
- Duplicar otro diccionario de alias.
- Crear otro documento de producto prometiendo capacidades no integradas.
- Ejecutar dry run manual bypassing triage/evidence.
- Usar ground truth del caso para guiar el runtime.
- Convertir owner answer en evidencia validada automáticamente.
- Crear chatbot/LLM/FSM externo para tapar el defecto.
```

Cualquier acción de ese tipo agrava la deriva.

---

## 9. Modelo de reconstrucción recomendado

### 9.1 Principio rector

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El operador humano controla la entrega.
```

Para Servicio 1, esto debe traducirse en:

```text
El Semantic Evidence Binding gobierna antes del cómputo.
```

---

### 9.2 Capa faltante

Nombre recomendado:

```text
SERVICE_1_SEMANTIC_EVIDENCE_BINDING_V1
```

No debe ser una pieza “inteligente” que diagnostica. Debe ser un contrato determinístico para consolidar correspondencias semánticas.

---

### 9.3 Responsabilidad exacta de la capa

Debe conectar:

```text
observed_xlsx_columns
sample_values
owner_narrative
owner_answers
column_confirmation_matrix
formula_catalog
pathology_catalog
required_variables
required_evidence
```

Debe producir:

```text
semantic_data_map
formula_variable_bindings
pathology_evidence_candidates
missing_bindings
ambiguous_bindings
owner_questions
readiness_status
computation_candidate_refs
```

No debe producir:

```text
diagnóstico definitivo
hallazgo contable final
autorización de delivery
autorización de runtime real
promoción automática de respuesta del dueño a verdad validada
```

---

## 10. Contratos mínimos necesarios

### 10.1 `ColumnSemanticCandidateV1`

Propósito: representar qué podría significar una columna observada.

Campos mínimos:

```text
observed_column_name
normalized_column_name
sheet_name
sample_values
inferred_data_type
candidate_semantic_roles
candidate_formula_variables
candidate_evidence_items
calculation_relevance
confidence
ambiguity_reason
owner_confirmation_required
owner_confirmed_role
validation_status
```

Estados:

```text
INFERRED_NOT_CONFIRMED
DECLARED_BY_OWNER_NOT_VALIDATED
CONFIRMED_FOR_COMPUTATION_CANDIDATE
BLOCKED_AMBIGUOUS
IGNORED_NOT_RELEVANT
```

---

### 10.2 `FormulaRequirementBindingV1`

Propósito: conectar fórmula con columnas candidatas.

Campos mínimos:

```text
formula_id
pathology_code
required_variables
required_evidence
variable_to_column_candidates
matched_variables
missing_variables
ambiguous_variables
unit_compatibility_status
grain_compatibility_status
owner_confirmations_required
binding_status
```

Estados:

```text
READY_CANDIDATE
NEEDS_COLUMN_CONFIRMATION
NEEDS_VARIABLE_BINDING
NEEDS_EVIDENCE
BLOCKED_UNSUPPORTED_FORMULA
```

---

### 10.3 `PathologyEvidenceCandidateV1`

Propósito: conectar patología con evidencia y fórmulas posibles.

Campos mínimos:

```text
pathology_code
pathology_name
source_catalog_ref
formula_refs
required_evidence_patterns
matched_evidence_items
missing_evidence_items
ambiguous_evidence_items
supporting_columns
owner_disambiguation_questions
false_positive_risks
candidate_status
```

Estados:

```text
PATHOLOGY_CANDIDATE_ONLY
NEEDS_DISAMBIGUATION
EVIDENCE_CANDIDATE_READY
BLOCKED_INSUFFICIENT_EVIDENCE
BLOCKED_UNSUPPORTED_PATHOLOGY
```

---

### 10.4 `SemanticDataMapV1`

Propósito: ser el bus central entre XLSX, dueño, catálogos, fórmula y hallazgo.

Campos mínimos:

```text
case_id
tenant_id
intake_id
run_id
source_file_ref
observed_columns
column_semantic_candidates
formula_requirement_bindings
pathology_evidence_candidates
owner_answers_used
owner_answers_pending
missing_bindings
ambiguous_bindings
next_owner_questions
readiness_status
allowed_computation_candidates
blocked_reason
runtime_authorized=false
delivery_authorized=false
metadata
```

Estados:

```text
NEEDS_COLUMN_SEMANTIC_CONFIRMATION
NEEDS_FORMULA_INPUTS
NEEDS_PATHOLOGY_DISAMBIGUATION
SEMANTIC_MAP_READY_FOR_COMPUTATION_CANDIDATE
BLOCKED_INSUFFICIENT_EVIDENCE
BLOCKED_UNSUPPORTED_PATHOLOGY
BLOCKED_UNSUPPORTED_FORMULA
```

---

## 11. Flujo reconstruido recomendado

### 11.1 Flujo actual roto

```text
XLSX normalized fields
→ triage textual
→ owner question
→ loop
```

### 11.2 Flujo objetivo sano

```text
1. Leer XLSX.
2. Extraer headers + sample values + tipos.
3. Construir ColumnConfirmationMatrix inicial.
4. Construir ColumnSemanticCandidates.
5. Leer formula_catalog.v1.json.
6. Leer pathology_catalog.v1.json.
7. Resolver candidatos columna→variable de fórmula.
8. Resolver candidatos fórmula→patología.
9. Resolver candidatos patología→evidencia.
10. Generar preguntas específicas al dueño por ambigüedad real.
11. Persistir respuestas del dueño como DECLARED_NOT_VALIDATED.
12. Clasificar respuestas de columnas.
13. Aplicar respuestas a matriz.
14. Reconstruir SemanticDataMap.
15. Si el mapa es suficiente, emitir computation candidate.
16. Recién entonces pasar a evidence readiness gate.
17. Recién entonces computation plan.
18. Recién entonces dry-run candidate.
19. Recién entonces owner view.
20. Recién entonces package candidate bajo policy guard.
```

---

## 12. Comportamiento esperado para `CASE_001` tras reconstrucción

Para columnas:

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

La capa semántica debería producir candidatos como:

```text
fecha → fecha de venta / período operativo
producto_codigo → identificador de producto
producto → producto vendido
categoria → agrupador comercial
cantidad → volumen vendido
precio_unitario → precio de venta unitario
costo_unitario → posible costo unitario declarado
canal → canal de venta
venta_total → importe total de venta
```

Debe preguntar, por ejemplo:

```text
¿costo_unitario representa costo real vigente, costo promedio, costo de reposición o un costo incompleto?
¿precio_unitario es precio de venta antes o después de descuentos/impuestos/comisiones?
¿venta_total es cantidad × precio_unitario o ya incluye ajustes?
¿categoria y canal deben usarse como segmentadores del análisis?
```

No debe concluir todavía:

```text
margen negativo
fuga de margen
costos faltantes
```

Sí puede concluir:

```text
Hay columnas candidatas suficientes para preparar un computation candidate de margen, sujeto a confirmación semántica del dueño.
```

---

## 13. Refacción recomendada por fases

### Fase 0 — Congelar daño

Objetivo: impedir nuevos parches inconexos.

Acciones:

```text
- No tocar CASE_001 para “hacerlo pasar”.
- No agregar alias aislados como solución final.
- No mapear SAL_001 a margen.
- No crear docs comerciales.
- Declarar este informe como auditoría de falla activa.
```

Resultado esperado:

```text
El equipo deja de resolver síntomas.
```

---

### Fase 1 — Inventario de fuentes de verdad

Objetivo: determinar qué catálogos viven y cuáles quedan obsoletos.

Acciones:

```text
- Auditar pathology_catalog.v1.json.
- Auditar formula_catalog.v1.json.
- Auditar _PATHOLOGY_DEFINITIONS runtime.
- Auditar _PATHOLOGY_TO_COMPUTATION runtime.
- Auditar _FIELD_ALIASES duplicados.
- Auditar column_confirmation_v1.py.
```

Decisión necesaria:

```text
El runtime debe tener una sola fuente de verdad o loaders controlados desde catálogos versionados.
```

---

### Fase 2 — Crear contrato de Semantic Evidence Binding

Objetivo: definir el bus semántico central.

Archivos tentativos:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_evidence_binding_v1.py
PymIA-Live/tests/smartpyme/test_service_1_semantic_evidence_binding_v1.py
```

Debe ser puro:

```text
no IO
no runtime
no delivery
no LLM
no mutation
no diagnosis
```

---

### Fase 3 — Integrar ColumnConfirmationMatrix

Objetivo: dejar de pasar strings planos como confirmación.

Acciones:

```text
- La matriz de confirmación debe entrar al semantic binding.
- Las respuestas del dueño deben clasificarse.
- Las respuestas clasificadas deben aplicarse a la matriz.
- La matriz actualizada debe alimentar el SemanticDataMap.
```

Prohibido:

```text
- owner_answer_001 como string libre consumido por triage.
```

---

### Fase 4 — Integrar catálogos reales

Objetivo: que runtime deje de depender de diccionarios internos desconectados.

Acciones:

```text
- Cargar formula_catalog.v1.json mediante loader puro/controlado.
- Cargar pathology_catalog.v1.json mediante loader puro/controlado.
- Normalizar required_variables y required_evidence.
- Relacionar formula_id ↔ pathology_code.
```

Advertencia:

```text
No migrar todo de golpe. Primero lectura pura y snapshot de compatibilidad.
```

---

### Fase 5 — Reemplazar evidence readiness gate hardcodeado

Objetivo: que evidence readiness consuma SemanticDataMap.

Acciones:

```text
- El gate debe recibir FormulaRequirementBindingV1.
- El gate debe recibir PathologyEvidenceCandidateV1.
- El gate no debe resolver alias internamente.
- El gate no debe tener su propio diccionario paralelo.
```

---

### Fase 6 — Reconectar reentry operacional

Objetivo: que una respuesta del dueño altere el estado semántico sin diagnosticar.

Acciones:

```text
owner_answer_reentry
→ persistence
→ read_model
→ projection
→ classification
→ matrix application
→ semantic map rebuild
→ new next question OR computation candidate
```

El reentry no debe recalcular directamente. Debe gatillar reconstrucción semántica controlada.

---

### Fase 7 — Reintentar CASE_001

Objetivo: validar el nuevo flujo sin ground truth.

Criterios mínimos:

```text
- No repetir la misma pregunta si el dueño ya respondió.
- No diagnosticar por narrativa.
- No hardcodear CASE_001.
- Generar preguntas específicas sobre costo/precio/total/canal si son necesarias.
- Emitir computation candidate sólo si los bindings están completos.
```

---

## 14. Tests mínimos a crear

### 14.1 Test de no-regresión del loop

```text
Dado CASE_001 con respuesta del dueño a producto/categoria/canal,
el sistema no debe volver a preguntar exactamente lo mismo.
```

### 14.2 Test de binding semántico de columnas

```text
fecha → fecha
cantidad → volumen_vendido
precio_unitario → precio_venta
costo_unitario → costo_unitario
venta_total → importe/ventas_periodo
producto/categoria/canal → segmentación/producto
```

Debe quedar como candidate, no evidencia validada.

### 14.3 Test de catálogos usados

```text
El matcher debe consumir formula_catalog/pathology_catalog o snapshots derivados,
no diccionarios locales divergentes.
```

### 14.4 Test de owner answer no validada

```text
Una respuesta del dueño puede cerrar ambigüedad declarada,
pero no autoriza diagnóstico ni delivery.
```

### 14.5 Test de computation candidate

```text
Si variables requeridas están mapeadas y confirmadas,
el sistema puede emitir allowed_computation_ref candidate,
con runtime_authorized=false y delivery_authorized=false.
```

### 14.6 Test anti-hardcode CASE_001

```text
El resultado no debe depender del nombre del archivo,
case_id,
ni strings específicos del ground truth.
```

---

## 15. Criterios de aceptación de la reconstrucción

La reconstrucción no puede considerarse cerrada hasta que se cumpla:

```text
1. El flujo XLSX-first usa SemanticDataMap.
2. Las columnas se ligan a variables/evidencias mediante contrato explícito.
3. Las respuestas del dueño actualizan una matriz o binding estructurado.
4. Formula catalog y pathology catalog son fuentes vivas o snapshots gobernados.
5. No existen alias críticos duplicados en tres módulos diferentes sin control.
6. El entrypoint no pasa de triage por strings planos.
7. El sistema pregunta sobre ambigüedad real, no sobre preguntas genéricas repetidas.
8. Computation candidate sólo aparece después de binding suficiente.
9. Runtime/delivery siguen false en candidatos.
10. CASE_001 puede avanzar sin ground truth y sin diagnóstico prematuro.
```

---

## 16. Dónde guardar este informe en el repo

Guardar en:

```text
docs/auditoria/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_FAILURE_AUDIT_V1.md
```

Justificación:

```text
- Es una auditoría de falla, no un documento de producto.
- No debe ir en docs/producto porque aún no describe una capacidad cerrada.
- No debe ir en docs/current como verdad operativa hasta que haya refacción implementada.
- Debe quedar en auditoría para guiar reconstrucción y evitar más deriva.
```

Cuando la reconstrucción esté implementada y testeada, recién debería generarse un documento de cierre en `docs/producto/`.

---

## 17. Consejo de saneamiento documental

Este informe debe tratarse como documento de control de daño.

Recomendación:

```text
No crear nuevos documentos de visión hasta cerrar la refacción.
No seguir acumulando roadmaps.
No mezclar este diagnóstico con narrativa comercial.
No usarlo como promesa de capacidad.
```

Después de corregir el flujo, crear una auditoría secundaria:

```text
docs/auditoria/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_REPAIR_VERIFICATION_V1.md
```

Sólo si los tests pasan, crear:

```text
docs/producto/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CAPABILITY_CLOSEOUT_V1.md
```

---

## 18. Resumen final

El daño principal no viene de que falte un alias o de que `SAL_001` sea incorrecto. Viene de haber construido muchas piezas correctas como objetos aislados, sin una capa central de binding semántico.

La prioridad no es “hacer pasar CASE_001”. La prioridad es reconstruir el tramo:

```text
XLSX columns
→ column semantics
→ formula variables
→ pathology evidence
→ owner clarification
→ semantic data map
→ computation candidate
```

Hasta que eso exista, Servicio 1 seguirá bloqueando sano, pero no podrá producir hallazgos operativos confiables desde archivos reales.
