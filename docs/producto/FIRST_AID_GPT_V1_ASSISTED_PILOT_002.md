# FIRST_AID_GPT_V1_ASSISTED_PILOT_002

## Estado

```text
Tipo: PRODUCT_PILOT_LOG
Estado: SIMULATED_CONTROLLED_PILOT
Runtime impact: NONE
Code impact: NONE
Evidence impact: SYNTHETIC_XLSX_EXTERNAL
```

## Propósito

Registrar el segundo piloto asistido controlado de `Primeros Auxilios GPT V1`, usando un Excel sintético de lista de precios y costos para probar el límite entre:

```text
margen bruto estimado
vs
rentabilidad real no afirmable
```

Este piloto usa como evidencia externa sintética:

```text
first_aid_pilot_002_lista_precios_costos_demo.xlsx
```

El archivo no se considera evidencia real de una PyME ni se incorpora como runtime.

---

# 1. Veredicto

```text
PILOT_002: COMPLETED_SIMULATED_CONTROLLED
FIRST_AID_SCOPE: RESPECTED
DIAGNOSTIC_CLAIMS: NONE
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
```

---

# 2. Caso usado

```yaml
pilot_case_log:
  pilot_id: PILOT_002
  date: 2026-06-20
  operator: assisted_simulated
  source_channel: generated_xlsx_sandbox

  business_minimal_profile:
    business_name: Comercio Textil Demo
    business_activity: venta minorista de indumentaria y accesorios
    operation_type: comercio
    sales_channels:
      - local físico
      - WhatsApp
      - Mercado Libre
      - ecommerce
    handles_stock: sí
    owner_role: dueño

  owner_request:
    original_phrase: "Tengo una lista de precios y costos, quiero saber qué productos dejan margen y cuáles tengo que revisar."
    selected_first_aid_option: PRICE_OR_COST_LIST
    expected_outcome_by_owner: revisar margen estimado y detectar productos problemáticos
    urgency: media

  evidence_received:
    evidence_type: XLSX_SYNTHETIC
    file_names:
      - first_aid_pilot_002_lista_precios_costos_demo.xlsx
    source_description: workbook sintético con lista de precios, costos, stock declarado y hoja de revisión First Aid
    number_of_sources: 1
    safe_to_review: true
    macro_or_execution_risk: false
    sensitive_data_notes: sin datos reales; caso sintético controlado

  admission_check:
    has_minimal_business_context: yes
    has_owner_problem_phrase: yes
    has_reviewable_evidence: yes
    fits_first_aid_scope: yes
    requires_diagnosis: no
    requires_second_source: partial
    requires_macro_execution: no
    admission_verdict: ACCEPTED
```

---

# 3. Estructura del Excel sintético

El workbook contiene:

```text
README_PILOT
Lista_Precios_Costos
Revision_PymIA
Categorias
```

La hoja principal contiene 12 productos con campos de:

```text
SKU
Producto
Categoría
Canal principal
Precio venta declarado
Costo unitario declarado
Stock actual declarado
Stock mínimo
Última actualización
Notas del dueño
```

---

# 4. Casos de prueba incluidos

```text
precio/costo válidos
costo faltante
precio ambiguo
costo "nan"
costo cero declarado
margen negativo
stock bajo
stock faltante
formato argentino: "18.500,00" y "$ 12.300,50"
precio cero declarado
producto sin stock
```

---

# 5. Lectura de admisión

El caso entra en Primeros Auxilios porque:

```text
hay una única fuente puntual
el objetivo es revisar precios/costos, no diagnosticar la empresa
la salida esperada es margen bruto estimado y advertencias
no requiere ejecución de macros
no requiere auditoría contable
no requiere afirmar rentabilidad real
```

Clasificación:

```text
selected_first_aid_option: PRICE_OR_COST_LIST
service_depth: FIRST_AID
```

---

# 6. Revisión simulada

```yaml
review_summary:
  what_was_received: lista sintética de precios, costos y stock declarado de 12 productos
  what_could_be_reviewed: margen bruto estimado cuando precio y costo son válidos; stock bajo declarado; campos faltantes o ambiguos

  visible_signals:
    - 6 productos aparecen como OK_ESTIMABLE para margen bruto simple
    - 1 producto muestra margen negativo
    - 2 productos tienen precio faltante o inválido
    - 2 productos tienen costo faltante o inválido
    - 1 producto tiene costo cero declarado y requiere confirmación
    - 2 productos muestran stock bajo o sin stock según fuente declarada

  visible_disorder_or_quality_issues:
    - precio ambiguo en formato no interpretable
    - costo expresado como "nan"
    - costo faltante
    - precio cero declarado
    - stock faltante en un producto
    - formatos monetarios mixtos

  computed_or_normalized_values:
    - margen_bruto_pesos cuando precio y costo son válidos
    - margen_bruto_porcentaje cuando precio > 0 y costo válido
    - markup_porcentaje cuando costo > 0
    - alerta_stock cuando stock_actual < stock_minimo

  warnings:
    - margen bruto estimado no es rentabilidad real
    - faltan descuentos, comisiones, impuestos, envíos y costos indirectos
    - stock del archivo es declarado, no stock físico confirmado
    - precio/costo ambiguo requiere aclaración antes de calcular

  what_cannot_be_claimed:
    - no puede afirmarse rentabilidad real por producto
    - no puede recomendarse precio definitivo
    - no puede confirmarse stock físico real
    - no puede concluirse conveniencia de canal
    - no puede diagnosticarse caja ni resultado del negocio

  missing_evidence:
    - comisiones por canal
    - impuestos aplicables
    - descuentos/promociones
    - costos de envío o packaging
    - costos indirectos
    - fuente de stock físico o sistema confiable
```

---

# 7. Señales owner-safe destacables

## 7.1 Margen negativo

```text
Hay al menos un producto donde el costo declarado supera el precio de venta.
Esto es una señal para revisar, no un diagnóstico definitivo.
```

Límite:

```text
Puede deberse a error de carga, precio viejo, costo mal informado o producto vendido con pérdida.
Se necesita validación del dueño antes de concluir.
```

## 7.2 Costo faltante o inválido

```text
Hay productos con precio, pero sin costo válido.
Con esos productos no se puede estimar margen.
```

## 7.3 Costo cero declarado

```text
Un costo cero puede ser real o puede ser falta de carga.
Debe confirmarse antes de calcular margen.
```

## 7.4 Formato argentino normalizable

```text
El caso prueba valores tipo "18.500,00" y "$ 12.300,50".
Estos valores pueden normalizarse si el formato es reconocible.
```

## 7.5 Precio ambiguo

```text
Un valor como "12,34,56" debe bloquearse o pedir aclaración.
No debe calcularse silenciosamente.
```

---

# 8. Devolución owner-safe simulada

```text
Recibimos una lista de precios y costos con 12 productos.
Con esta fuente se puede hacer una revisión inicial de margen bruto estimado cuando precio y costo están completos y son legibles.

Lo que sí se puede revisar:
- productos con precio y costo válidos;
- margen bruto estimado en pesos y porcentaje;
- productos con costo faltante o inválido;
- productos con precio ambiguo;
- señales de stock bajo según el stock declarado.

Señales visibles:
- hay productos donde el margen bruto puede estimarse;
- hay al menos un producto con costo mayor al precio;
- hay productos que no se pueden calcular por falta de costo o precio válido;
- hay un costo cero que requiere confirmación;
- hay formatos monetarios mezclados que deben normalizarse con cuidado.

Lo que no se puede afirmar todavía:
- no se puede afirmar rentabilidad real;
- no se puede recomendar un precio definitivo;
- no se puede confirmar stock físico;
- no se puede concluir si un canal conviene o no;
- no se puede diagnosticar el negocio sólo con esta lista.

Próximo paso razonable:
confirmar costos faltantes, aclarar valores ambiguos y sumar comisiones/descuentos/impuestos si se quiere pasar de margen bruto estimado a un análisis más profundo.
```

---

# 9. Preguntas siguientes al dueño

```text
1. ¿El costo cero del producto indicado es real o significa que falta cargar el costo?
2. ¿El precio ambiguo corresponde a 1234,56, 123.456 o es un error de carga?
3. ¿Los precios incluyen IVA?
4. ¿Hay descuentos, comisiones o costos de envío por canal?
5. ¿Querés revisar sólo margen bruto estimado o avanzar hacia rentabilidad por canal con más evidencia?
```

---

# 10. Bloqueos sanos aplicados

```text
No se afirmó rentabilidad real.
No se recomendó precio definitivo.
No se confirmó stock físico.
No se diagnosticó la empresa.
No se confundió margen bruto con ganancia neta.
No se calculó sobre valores ambiguos.
```

---

# 11. Resultado del piloto

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

# 12. Aprendizaje de producto

```yaml
product_learning:
  what_worked:
    - El límite entre margen bruto estimado y rentabilidad real queda claro.
    - El sistema puede entregar valor aunque algunos productos no sean calculables.
    - Las advertencias owner-safe evitan sobrediagnóstico.
    - El caso prueba formatos argentinos y valores ambiguos.

  what_confused_owner:
    - Margen bruto, markup y rentabilidad pueden confundirse.
    - Costo cero requiere una explicación cuidadosa.
    - Un producto con margen negativo puede sonar diagnóstico si no se declara como señal.

  repeated_pain_detected:
    - listas con precios pero costos incompletos
    - formatos monetarios mezclados
    - deseo de rentabilidad real con evidencia insuficiente

  missing_tool_or_template:
    - FIRST_AID_PRICE_COST_RESPONSE_TEMPLATE
    - FIRST_AID_MARGIN_MINIMUM_EVIDENCE_CHECKLIST
    - FIRST_AID_AMBIGUOUS_VALUE_OWNER_QUESTION_TEMPLATE

  language_adjustment_needed:
    - usar "margen bruto estimado" en vez de "ganancia"
    - usar "señal para revisar" en vez de "problema confirmado"
    - explicar que markup y margen no son equivalentes

  candidate_future_improvement:
    - checklist de suficiencia para margen por canal
    - plantilla owner-safe para productos con costo faltante
    - plantilla owner-safe para margen negativo
```

---

# 13. Riesgos observados

```text
Riesgo 1: El dueño puede interpretar margen bruto como ganancia real.
Mitigación: declarar explícitamente costos faltantes y límites.

Riesgo 2: Margen negativo puede sonar a hallazgo causal.
Mitigación: tratarlo como señal visible a validar.

Riesgo 3: Costo cero puede producir cálculo engañoso.
Mitigación: marcarlo como costo a confirmar.

Riesgo 4: Formatos ambiguos pueden contaminar cálculos.
Mitigación: bloquear o preguntar antes de calcular.
```

---

# 14. Decisión sobre el piloto

```text
PILOT_002_RESULT: SUCCESS_SIMULATED
PRODUCT_SIGNAL: VALID
FIRST_AID_PRICE_COST_USE_CASE: VALIDATED_AS_CONTROLLED_CASE
READY_FOR_REAL_PILOT: YES
```

El piloto valida que `Primeros Auxilios GPT V1` puede revisar una lista de precios/costos de forma útil sin diagnosticar rentabilidad real.

---

# 15. Próximo paso recomendado

Ejecutar `PILOT_003` con una de estas opciones:

```text
STOCK_OR_INVENTORY
CASH_BANK_OR_SIMPLE_RECONCILIATION
EXCEL_DISORDER
```

Preferencia:

```text
PILOT_003 = STOCK_OR_INVENTORY
```

Motivo:

```text
Permite probar límite entre stock declarado, stock físico y capital inmovilizado sin diagnosticar ni afirmar rotación real.
```

---

# 16. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_DIAGNOSTIC
NO_OCF_PRODUCTIVE_WRITE
NO_AUTOMATION
NO_CHANNEL_INTEGRATION
```

Este piloto es aprendizaje de producto, no implementación.
