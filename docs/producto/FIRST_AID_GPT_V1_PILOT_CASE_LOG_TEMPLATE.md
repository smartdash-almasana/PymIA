# FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE

## Estado

```text
Tipo: PRODUCT_OPERATING_TEMPLATE
Estado: CANDIDATE_READY_FOR_PILOT_LOGGING
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Definir una plantilla única para registrar 3 a 5 pilotos asistidos de `Primeros Auxilios GPT V1` sin convertirlos en runtime, sin diagnosticar y sin abrir integración productiva.

Este documento operacionaliza:

```text
docs/producto/FIRST_AID_GPT_V1_PILOT_OFFER.md
docs/producto/FIRST_AID_GPT_V1_PILOT_SCRIPT.md
docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md
```

---

# 1. Veredicto

```text
FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE = READY_FOR_3_TO_5_ASSISTED_PILOTS
```

Pero:

```text
NO_RUNTIME_AUTHORIZED
NO_DIAGNOSTIC_AUTHORIZED
NO_OCF_PRODUCTIVE_WRITE
NO_CHANNEL_INTEGRATION
NO_AUTOMATION_IMPLEMENTATION
NO_ACCOUNTING_AUDIT
```

Esta plantilla registra aprendizaje de producto. No es ficha clínica productiva ni expediente operativo definitivo.

---

# 2. Uso previsto

Crear un archivo por piloto o una sección por piloto dentro de un registro manual.

Formato recomendado:

```text
PILOT_001
PILOT_002
PILOT_003
PILOT_004
PILOT_005
```

Cada piloto debe cerrar con un veredicto:

```text
SUCCESS
PARTIAL
BLOCKED
OUT_OF_SCOPE
ESCALATED_TO_LEVEL_2
```

---

# 3. Plantilla base

```yaml
pilot_case_log:
  pilot_id:
  date:
  operator:
  source_channel:

  business_minimal_profile:
    business_name:
    business_activity:
    operation_type:
    sales_channels: []
    handles_stock:
    owner_role:

  owner_request:
    original_phrase:
    selected_first_aid_option:
    expected_outcome_by_owner:
    urgency:

  evidence_received:
    evidence_type:
    file_names: []
    source_description:
    number_of_sources:
    safe_to_review:
    macro_or_execution_risk:
    sensitive_data_notes:

  admission_check:
    has_minimal_business_context: yes|no|partial
    has_owner_problem_phrase: yes|no
    has_reviewable_evidence: yes|no|partial
    fits_first_aid_scope: yes|no|partial
    requires_diagnosis: yes|no
    requires_second_source: yes|no
    requires_macro_execution: yes|no
    admission_verdict: ACCEPTED|BLOCKED|OUT_OF_SCOPE|ESCALATE

  review_summary:
    what_was_received:
    what_could_be_reviewed:
    visible_signals: []
    visible_disorder_or_quality_issues: []
    computed_or_normalized_values: []
    warnings: []
    what_cannot_be_claimed: []
    missing_evidence: []

  owner_safe_output:
    short_summary:
    limits_declared: []
    next_step_suggested:
    questions_back_to_owner: []

  result:
    clarity_delivered: yes|no|partial
    owner_understood_limits: yes|no|partial|unknown
    missing_evidence_identified: yes|no
    next_step_defined: yes|no
    escalated_to_level_2: yes|no
    final_verdict: SUCCESS|PARTIAL|BLOCKED|OUT_OF_SCOPE|ESCALATED_TO_LEVEL_2

  product_learning:
    what_worked:
    what_confused_owner:
    repeated_pain_detected:
    missing_tool_or_template:
    language_adjustment_needed:
    candidate_future_improvement:

  operator_notes:
```

---

# 4. Campos obligatorios

Un piloto no se considera registrado si faltan:

```text
pilot_id
date
business_activity
owner_request.original_phrase
selected_first_aid_option
evidence_received.evidence_type
admission_verdict
what_could_be_reviewed
what_cannot_be_claimed
missing_evidence
next_step_suggested
final_verdict
```

---

# 5. Catálogo de opciones

## selected_first_aid_option

```text
EXCEL_DISORDER
FORMULA_OR_TOTALS_NOT_MATCHING
PRICE_OR_COST_LIST
STOCK_OR_INVENTORY
CASH_BANK_OR_SIMPLE_RECONCILIATION
SALES_OR_COMMERCIAL_DATA
MANUAL_REPETITIVE_TASK
OTHER_POINT_PROBLEM
```

## evidence_type

```text
XLSX
CSV
PDF
IMAGE_OR_SCREENSHOT
TEXT_DESCRIPTION
BANK_EXTRACT
SALES_EXPORT
STOCK_EXPORT
PRICE_LIST
OTHER
```

## admission_verdict

```text
ACCEPTED
BLOCKED
OUT_OF_SCOPE
ESCALATE
```

## final_verdict

```text
SUCCESS
PARTIAL
BLOCKED
OUT_OF_SCOPE
ESCALATED_TO_LEVEL_2
```

---

# 6. Reglas de registro

## 6.1 No registrar diagnóstico

Prohibido escribir:

```text
causa final del problema
rentabilidad real si faltan costos
stock físico real sin conteo
conciliación cerrada con una sola fuente
fraude o intención
recomendación estratégica completa
```

Permitido escribir:

```text
señal visible
límite de evidencia
dato faltante
pregunta siguiente
necesidad de segunda fuente
```

## 6.2 Preservar frase textual del dueño

El campo `owner_request.original_phrase` debe conservar el lenguaje del dueño.

Ejemplo:

```text
"Tengo este Excel hecho un quilombo y no sé qué vende más."
```

No reemplazarlo por una categoría técnica sin dejar la frase original.

## 6.3 Separar señal de conclusión

Correcto:

```text
visible_signals:
  - Hay productos con ventas altas.
what_cannot_be_claimed:
  - No puede afirmarse margen porque faltan costos.
```

Incorrecto:

```text
visible_signals:
  - Los productos más vendidos son los más rentables.
```

## 6.4 Registrar bloqueo como resultado válido

Un piloto bloqueado puede ser exitoso como aprendizaje si identifica claramente qué evidencia falta.

---

# 7. Plantilla breve para uso manual

```text
## PILOT_[NNN]

Fecha:
Operador:
Canal:

### 1. Negocio
Nombre:
Actividad:
Tipo de operación:
Canales:
Maneja stock:
Rol del interlocutor:

### 2. Pedido del dueño
Frase textual:
Opción First Aid:
Resultado esperado por el dueño:
Urgencia:

### 3. Evidencia recibida
Tipo de evidencia:
Archivos/fuentes:
Cantidad de fuentes:
Riesgo de macro/ejecución:
Datos sensibles:

### 4. Admisión
Contexto mínimo: sí/no/parcial
Evidencia revisable: sí/no/parcial
Entra en First Aid: sí/no/parcial
Necesita diagnóstico: sí/no
Necesita segunda fuente: sí/no
Veredicto de admisión:

### 5. Revisión
Qué recibimos:
Qué se pudo revisar:
Señales visibles:
Problemas de calidad o desorden:
Warnings:
Qué no se puede afirmar:
Evidencia faltante:

### 6. Devolución owner-safe
Resumen breve:
Límites declarados:
Próximo paso:
Preguntas al dueño:

### 7. Resultado
Claridad entregada: sí/no/parcial
El dueño entendió límites: sí/no/parcial/desconocido
Dato faltante identificado: sí/no
Próximo paso definido: sí/no
Escaló a Nivel 2: sí/no
Veredicto final:

### 8. Aprendizaje de producto
Qué funcionó:
Qué confundió:
Dolor repetido:
Herramienta o plantilla faltante:
Ajuste de lenguaje:
Mejora futura candidata:

### 9. Notas del operador
```

---

# 8. Ejemplo sintético

```yaml
pilot_case_log:
  pilot_id: PILOT_001
  date: 2026-06-20
  operator: assisted
  source_channel: manual_chat

  business_minimal_profile:
    business_name: Comercio Textil Demo
    business_activity: venta minorista de indumentaria
    operation_type: comercio
    sales_channels:
      - local físico
      - WhatsApp
    handles_stock: sí
    owner_role: dueño

  owner_request:
    original_phrase: "Tengo este Excel de ventas y no sé qué productos se mueven más."
    selected_first_aid_option: SALES_OR_COMMERCIAL_DATA
    expected_outcome_by_owner: entender productos más vendidos
    urgency: media

  evidence_received:
    evidence_type: XLSX
    file_names:
      - ventas_demo.xlsx
    source_description: planilla de ventas exportada manualmente
    number_of_sources: 1
    safe_to_review: true
    macro_or_execution_risk: false
    sensitive_data_notes: contiene nombres de clientes

  admission_check:
    has_minimal_business_context: yes
    has_owner_problem_phrase: yes
    has_reviewable_evidence: yes
    fits_first_aid_scope: yes
    requires_diagnosis: no
    requires_second_source: no
    requires_macro_execution: no
    admission_verdict: ACCEPTED

  review_summary:
    what_was_received: planilla de ventas con productos, cantidades y precios
    what_could_be_reviewed: productos con más unidades vendidas y estructura básica de columnas
    visible_signals:
      - productos con alta frecuencia de venta
    visible_disorder_or_quality_issues:
      - faltan costos unitarios
    computed_or_normalized_values:
      - cantidad_total si el dato es legible
    warnings:
      - ventas no equivalen a ganancia
    what_cannot_be_claimed:
      - no se puede afirmar margen ni rentabilidad real
    missing_evidence:
      - lista de costos o precios de compra

  owner_safe_output:
    short_summary: La planilla sirve para ordenar ventas y detectar productos más vendidos, pero no para saber rentabilidad.
    limits_declared:
      - faltan costos
      - no hay comisiones ni descuentos
    next_step_suggested: sumar lista de costos para revisar margen estimado
    questions_back_to_owner:
      - ¿Tenés una lista de costos o precios de compra actualizada?

  result:
    clarity_delivered: yes
    owner_understood_limits: unknown
    missing_evidence_identified: yes
    next_step_defined: yes
    escalated_to_level_2: no
    final_verdict: SUCCESS

  product_learning:
    what_worked: el dueño entiende rápido diferencia entre ventas y ganancia
    what_confused_owner: margen vs markup puede requerir explicación simple
    repeated_pain_detected: ventas sin costos
    missing_tool_or_template: plantilla de devolución para ventas sin costos
    language_adjustment_needed: evitar términos como rentabilidad si sólo hay ventas
    candidate_future_improvement: checklist específico de ventas + costos

  operator_notes: Caso apto para piloto de ventas básico.
```

---

# 9. Criterio de cierre de la tanda 3–5 pilotos

La tanda se considera útil si permite responder:

```text
qué dolores aparecen más
qué evidencia trae realmente el dueño
qué preguntas entiende o no entiende
qué límites generan confianza
qué casos escalan naturalmente a Nivel 2
qué herramientas faltan para First Aid
```

No se considera útil si sólo registra:

```text
cantidad de archivos procesados
cantidad de respuestas bonitas
opiniones sin evidencia
casos sin frase textual del dueño
```

---

# 10. Salida esperada después de 3–5 pilotos

Después de registrar 3–5 casos, producir un documento separado:

```text
FIRST_AID_GPT_V1_PILOT_BATCH_REVIEW.md
```

Debe contener:

```text
patrones de dolor
fricciones de admisión
faltantes de evidencia repetidos
lenguaje owner-facing que funcionó
límites que evitaron sobrediagnóstico
candidatos de mejora
recomendación: mantener, ajustar, escalar o pausar
```

---

# 11. Veredicto final

```text
FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE = PRODUCT_LEARNING_READY
```

Este documento no autoriza runtime ni implementación. Autoriza únicamente registro manual/asistido de pilotos y aprendizaje de producto.
