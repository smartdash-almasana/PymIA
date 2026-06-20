# FIRST_AID_GPT_V1_ASSISTED_PILOT_001

## Estado

```text
Tipo: PRODUCT_PILOT_LOG
Estado: SIMULATED_CONTROLLED_PILOT
Runtime impact: NONE
Code impact: NONE
Evidence impact: NONE
```

## Propósito

Registrar el primer piloto asistido controlado de `Primeros Auxilios GPT V1` usando el guion operativo y la plantilla de log definidos en:

```text
docs/producto/FIRST_AID_GPT_V1_PILOT_SCRIPT.md
docs/producto/FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE.md
```

Este piloto es simulado/controlado porque en esta sesión no se recibió un archivo real ni una PyME real.

No autoriza runtime, diagnóstico, OCF productivo, automatización, canal externo ni nueva feature.

---

# 1. Veredicto

```text
PILOT_001: COMPLETED_SIMULATED_CONTROLLED
FIRST_AID_SCOPE: RESPECTED
DIAGNOSTIC_CLAIMS: NONE
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
```

---

# 2. Caso usado

```yaml
pilot_case_log:
  pilot_id: PILOT_001
  date: 2026-06-20
  operator: assisted_simulated
  source_channel: manual_chat_simulation

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
    expected_outcome_by_owner: entender productos más vendidos y ordenar la planilla
    urgency: media

  evidence_received:
    evidence_type: XLSX_SIMULATED
    file_names:
      - ventas_demo_simulado.xlsx
    source_description: planilla simulada de ventas con productos, cantidades y precios; sin costos unitarios
    number_of_sources: 1
    safe_to_review: true
    macro_or_execution_risk: false
    sensitive_data_notes: sin datos reales; caso sintético

  admission_check:
    has_minimal_business_context: yes
    has_owner_problem_phrase: yes
    has_reviewable_evidence: partial
    fits_first_aid_scope: yes
    requires_diagnosis: no
    requires_second_source: no
    requires_macro_execution: no
    admission_verdict: ACCEPTED
```

---

# 3. Lectura de admisión

El caso entra en Primeros Auxilios porque:

```text
hay una fuente puntual
hay un pedido acotado
la pregunta inicial es de orden/lectura, no de causa profunda
no requiere diagnóstico empresarial completo
no requiere ejecutar macros
no requiere conciliación ni certificación contable
```

Clasificación:

```text
selected_first_aid_option: SALES_OR_COMMERCIAL_DATA
service_depth: FIRST_AID
```

---

# 4. Revisión simulada

```yaml
review_summary:
  what_was_received: planilla simulada de ventas con columnas de producto, cantidad y precio de venta
  what_could_be_reviewed: estructura básica de ventas, productos más vendidos y consistencia mínima de campos numéricos
  visible_signals:
    - hay productos con mayor frecuencia de venta
    - la fuente permite ordenar ventas por producto si cantidad y producto están legibles
    - el archivo no permite distinguir rentabilidad
  visible_disorder_or_quality_issues:
    - faltan costos unitarios
    - no hay comisiones, descuentos, impuestos ni envíos
    - no hay fuente de stock físico ni compras
  computed_or_normalized_values:
    - cantidad_total si la columna cantidad es legible
    - ventas_total si precio y cantidad son legibles
  warnings:
    - ventas no equivalen a ganancia
    - productos más vendidos no necesariamente son productos más rentables
  what_cannot_be_claimed:
    - no puede afirmarse margen real
    - no puede afirmarse rentabilidad por producto
    - no puede afirmarse conveniencia comercial de un canal
    - no puede afirmarse stock real
  missing_evidence:
    - lista de costos o precios de compra
    - descuentos o comisiones si existen
    - stock o inventario si se quiere cruzar venta con disponibilidad
```

---

# 5. Devolución owner-safe simulada

```text
Recibimos una planilla de ventas con productos, cantidades y precios de venta.
Con esa fuente se puede ordenar la información y ver qué productos se mueven más.

Lo que sí se puede leer:
- qué productos aparecen con más ventas o unidades;
- si la estructura de la tabla permite sumar cantidades o ventas;
- si hay campos incompletos o ambiguos.

Lo que no se puede afirmar todavía:
- no se puede saber qué producto deja más plata;
- no se puede calcular margen real;
- no se puede concluir rentabilidad;
- no se puede confirmar stock físico.

La señal visible es que la planilla puede servir para ordenar ventas, pero todavía no sirve para decidir rentabilidad.

Para avanzar, el dato que falta es una lista de costos o precios de compra. Con eso se podría revisar margen estimado por producto, siempre declarando límites.
```

---

# 6. Preguntas siguientes al dueño

```text
1. ¿Tenés una lista de costos o precios de compra actualizada?
2. ¿El precio de venta de la planilla incluye descuentos o promociones?
3. ¿Querés mirar sólo productos más vendidos o también margen estimado?
4. ¿El stock que manejás está en otra planilla o sistema?
```

---

# 7. Bloqueos sanos aplicados

```text
No se diagnosticó la empresa.
No se afirmó rentabilidad.
No se confundió venta con ganancia.
No se confirmó stock físico.
No se pidió OCF completa.
No se abrió Nivel 2 sin señal causal suficiente.
```

---

# 8. Resultado del piloto

```yaml
result:
  clarity_delivered: yes
  owner_understood_limits: simulated_yes
  missing_evidence_identified: yes
  next_step_defined: yes
  escalated_to_level_2: no
  final_verdict: SUCCESS
```

---

# 9. Aprendizaje de producto

```yaml
product_learning:
  what_worked:
    - La diferencia ventas vs ganancia se comunica de forma simple.
    - El bloqueo por falta de costos es comprensible y no frena la utilidad inicial.
    - La pregunta siguiente surge naturalmente sin vender diagnóstico.

  what_confused_owner:
    - Puede confundir "producto más vendido" con "producto más rentable".
    - Puede requerir explicación simple de margen vs venta.

  repeated_pain_detected:
    - ventas disponibles sin costos asociados
    - planillas útiles para ordenar, insuficientes para rentabilidad

  missing_tool_or_template:
    - plantilla específica de devolución para ventas sin costos
    - checklist de columnas mínimas para margen estimado

  language_adjustment_needed:
    - usar "deja plata" con cautela
    - preferir "margen estimado" sobre "rentabilidad" cuando sólo hay costos parciales

  candidate_future_improvement:
    - FIRST_AID_SALES_WITHOUT_COSTS_RESPONSE_TEMPLATE
    - FIRST_AID_MARGIN_MINIMUM_EVIDENCE_CHECKLIST
```

---

# 10. Riesgos observados

```text
Riesgo 1: El dueño puede esperar diagnóstico de rentabilidad aunque sólo haya ventas.
Mitigación: declarar explícitamente que ventas no son ganancia.

Riesgo 2: El operador puede sobrediagnosticar productos con alta venta.
Mitigación: separar señal visible de conclusión causal.

Riesgo 3: El caso puede derivar rápido a Nivel 2.
Mitigación: escalar sólo si el dueño pide causa o si aporta costos/evidencia suficiente.
```

---

# 11. Decisión sobre el piloto

```text
PILOT_001_RESULT: SUCCESS_SIMULATED
PRODUCT_SIGNAL: VALID
READY_FOR_REAL_PILOT: YES
```

Este piloto controlado valida que el guion permite producir claridad sin diagnóstico.

---

# 12. Próximo paso recomendado

Ejecutar `PILOT_002` con un caso real o semirreal de una de estas categorías:

```text
A. Excel desordenado real
B. Lista de precios/costos
C. Stock o inventario
D. Caja/banco con una fuente
```

Si no hay caso real disponible, preparar un segundo piloto simulado con:

```text
PRICE_OR_COST_LIST
```

para probar el límite entre margen estimado y rentabilidad real.

---

# 13. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_DIAGNOSTIC
NO_OCF_PRODUCTIVE_WRITE
NO_AUTOMATION
NO_CHANNEL_INTEGRATION
```

Este piloto es aprendizaje de producto, no implementación.
