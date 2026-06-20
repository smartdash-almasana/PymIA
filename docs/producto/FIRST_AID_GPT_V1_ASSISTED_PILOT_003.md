# FIRST_AID_GPT_V1_ASSISTED_PILOT_003

## Estado

```text
Tipo: PRODUCT_PILOT_LOG
Estado: SIMULATED_CONTROLLED_PILOT
Runtime impact: NONE
Code impact: NONE
Evidence impact: SYNTHETIC_XLSX_EXTERNAL
```

## Propósito

Registrar el tercer piloto asistido controlado de `Primeros Auxilios GPT V1`, usando un Excel sintético de stock/inventario para probar el límite entre:

```text
stock declarado
vs
stock físico no confirmado
vs
stock bajo
vs
posible stock inmovilizado
vs
rotación no afirmable sin histórico suficiente
```

Este piloto usa como evidencia externa sintética:

```text
first_aid_pilot_003_stock_inventory_demo.xlsx
```

El archivo no se considera evidencia real de una PyME ni se incorpora como runtime.

---

# 1. Veredicto

```text
PILOT_003: COMPLETED_SIMULATED_CONTROLLED
FIRST_AID_SCOPE: RESPECTED
DIAGNOSTIC_CLAIMS: NONE
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
```

---

# 2. Caso usado

```yaml
pilot_case_log:
  pilot_id: PILOT_003
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
    original_phrase: "Tengo una planilla de stock y no sé si lo que dice el sistema coincide con lo que hay. También quiero saber qué productos están bajos o parados."
    selected_first_aid_option: STOCK_OR_INVENTORY
    expected_outcome_by_owner: revisar señales de stock bajo, diferencias visibles y productos que requieren conteo o aclaración
    urgency: media

  evidence_received:
    evidence_type: XLSX_SYNTHETIC
    file_names:
      - first_aid_pilot_003_stock_inventory_demo.xlsx
    source_description: workbook sintético con stock de sistema, stock declarado, conteo físico parcial, stock mínimo, costo, precio y ventas declaradas de 30 días
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
Stock_Inventario
Revision_PymIA
Categorias
```

La hoja principal contiene 15 productos con campos de:

```text
SKU
Producto
Categoría
Canal principal
Stock sistema
Stock declarado dueño
Conteo físico informado
Stock mínimo
Costo unitario declarado
Precio venta declarado
Ventas 30d declaradas
Última actualización
Notas del dueño
```

Y columnas calculadas:

```text
Valor stock declarado
Diferencia sistema vs físico
Días stock estimados
Señal First Aid
Límite owner-safe
```

---

# 4. Casos de prueba incluidos

```text
stock/costo válidos
stock bajo declarado
sin stock declarado
conteo físico parcial
sistema vs conteo físico con diferencia
stock declarado faltante
conteo físico ambiguo escrito como texto
costo faltante
stock con cero ventas recientes
alto valor unitario
stock negativo declarado
formato argentino monetario
stock sistema ambiguo
posible stock inmovilizado
```

---

# 5. Lectura de admisión

El caso entra en Primeros Auxilios porque:

```text
hay una única fuente puntual
el objetivo es revisar señales de stock, no diagnosticar la empresa
la salida esperada es advertencia y pedido de evidencia
no requiere ejecutar macros
no requiere auditoría contable
no requiere afirmar stock físico real
no requiere afirmar rotación real
```

Clasificación:

```text
selected_first_aid_option: STOCK_OR_INVENTORY
service_depth: FIRST_AID
```

---

# 6. Revisión simulada

```yaml
review_summary:
  what_was_received: lista sintética de stock con sistema, stock declarado, conteo físico parcial, mínimos, costos y ventas declaradas de 30 días
  what_could_be_reviewed: stock bajo declarado, sin stock declarado, diferencias sistema/conteo informado, posibles datos ambiguos y señales de inmovilización

  visible_signals:
    - 4 productos aparecen como OK_ESTIMABLE
    - 1 producto muestra stock bajo declarado
    - 1 producto aparece sin stock declarado
    - 1 producto tiene stock negativo declarado
    - 2 productos muestran diferencia sistema/físico informada
    - 1 producto muestra posible stock inmovilizado
    - 1 producto tiene stock declarado faltante
    - 4 productos tienen datos ambiguos o no comparables

  visible_disorder_or_quality_issues:
    - conteo físico escrito como texto
    - stock sistema ambiguo
    - costo faltante
    - stock declarado faltante
    - stock negativo declarado
    - fechas de actualización antiguas en algunos productos
    - ventas 30d insuficientes para afirmar rotación real

  computed_or_normalized_values:
    - valor_stock_declarado cuando stock y costo son válidos
    - diferencia_sistema_vs_fisico cuando ambas fuentes son numéricas
    - dias_stock_estimados como señal exploratoria cuando hay ventas 30d declaradas
    - señal First Aid por producto

  warnings:
    - stock declarado no equivale a stock físico confirmado
    - conteo físico parcial no permite concluir merma, robo ni error causal
    - días de stock estimados no equivalen a rotación real
    - posible stock inmovilizado es una señal, no un diagnóstico
    - valor de stock declarado depende de costo confirmado

  what_cannot_be_claimed:
    - no puede afirmarse stock físico real
    - no puede afirmarse merma
    - no puede afirmarse robo o pérdida
    - no puede afirmarse rotación real
    - no puede afirmarse capital inmovilizado real
    - no puede recomendarse reposición definitiva

  missing_evidence:
    - conteo físico completo
    - export confiable del sistema
    - movimientos de entradas y salidas
    - compras o remitos
    - ajustes manuales de stock
    - histórico de ventas suficiente
    - costos confirmados
```

---

# 7. Señales owner-safe destacables

## 7.1 Stock bajo declarado

```text
Hay productos cuyo stock declarado está por debajo del mínimo definido.
Esto es una señal operativa para revisar, no una confirmación de faltante físico.
```

## 7.2 Diferencia sistema vs físico informado

```text
Hay diferencias visibles entre el stock del sistema y el conteo físico informado.
Esto requiere validación antes de concluir causa.
```

Límite:

```text
La diferencia puede deberse a error de carga, conteo incompleto, ventas no registradas, compras no cargadas, ajustes manuales o merma.
```

## 7.3 Stock negativo declarado

```text
Un stock negativo suele indicar error de carga, sincronización o movimiento no registrado.
No debe tratarse como realidad física.
```

## 7.4 Posible stock inmovilizado

```text
Hay productos con stock declarado y ventas recientes bajas o nulas.
Esto puede ser señal de stock inmovilizado, pero no confirma rotación real.
```

## 7.5 Dato ambiguo no comparable

```text
Si un valor viene como texto ambiguo o formato no interpretable, no se calcula silenciosamente.
Se pide aclaración.
```

---

# 8. Devolución owner-safe simulada

```text
Recibimos una planilla de stock con 15 productos.
Con esta fuente se puede hacer una primera revisión de señales: stock bajo declarado, productos sin stock, diferencias visibles entre sistema y conteo informado, y productos que podrían estar parados.

Lo que sí se puede revisar:
- productos con stock declarado por debajo del mínimo;
- productos sin stock declarado;
- diferencias entre stock sistema y conteo físico informado cuando ambos datos son numéricos;
- productos con datos faltantes o ambiguos;
- señales de posible inmovilización cuando hay stock y ventas recientes muy bajas.

Señales visibles:
- hay productos con stock bajo declarado;
- hay al menos un stock negativo declarado;
- hay diferencias entre sistema y conteo físico en algunos productos;
- hay datos ambiguos que no deben calcularse automáticamente;
- hay productos con stock y ventas recientes bajas que conviene revisar.

Lo que no se puede afirmar todavía:
- no se puede confirmar stock físico real;
- no se puede afirmar merma o robo;
- no se puede afirmar rotación real;
- no se puede concluir capital inmovilizado real;
- no se puede recomendar reposición definitiva sólo con esta fuente.

Próximo paso razonable:
confirmar conteo físico, exportar movimientos de entradas y salidas, y sumar histórico de ventas suficiente para pasar de señal de stock a análisis de rotación.
```

---

# 9. Preguntas siguientes al dueño

```text
1. ¿El stock declarado viene del sistema, de una planilla manual o de conteo físico?
2. ¿Tenés un conteo físico completo o sólo parcial?
3. ¿Hay movimientos de entradas y salidas del período?
4. ¿Los productos con stock negativo son errores conocidos o aparecen así en el sistema?
5. ¿Querés revisar faltantes urgentes o productos parados?
6. ¿Tenés ventas históricas por producto de más de 30 días?
```

---

# 10. Bloqueos sanos aplicados

```text
No se afirmó stock físico real.
No se afirmó merma.
No se afirmó robo.
No se afirmó rotación real.
No se afirmó capital inmovilizado real.
No se recomendó reposición definitiva.
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
    - El límite entre stock declarado y stock físico real queda claro.
    - El sistema entrega valor aunque sólo haya conteo físico parcial.
    - La categoría DATO_AMBIGUO_NO_COMPARABLE evita cálculos silenciosos.
    - Stock bajo, stock cero y stock negativo son señales owner-safe entendibles.

  what_confused_owner:
    - Puede confundir días de stock estimados con rotación real.
    - Puede interpretar diferencia sistema/físico como merma confirmada.
    - Puede interpretar stock inmovilizado como diagnóstico definitivo.

  repeated_pain_detected:
    - stock sistema vs stock físico no coincidente
    - faltantes sin conteo físico confiable
    - stock negativo
    - productos parados sin histórico suficiente

  missing_tool_or_template:
    - FIRST_AID_STOCK_RESPONSE_TEMPLATE
    - FIRST_AID_STOCK_MINIMUM_EVIDENCE_CHECKLIST
    - FIRST_AID_STOCK_MISMATCH_OWNER_QUESTION_TEMPLATE

  language_adjustment_needed:
    - usar "stock declarado" en vez de "stock real"
    - usar "diferencia visible" en vez de "merma"
    - usar "posible inmovilización" en vez de "stock muerto"
    - usar "días estimados" en vez de "rotación"

  candidate_future_improvement:
    - checklist de suficiencia para rotación real
    - plantilla owner-safe para stock negativo
    - plantilla owner-safe para diferencias sistema/físico
```

---

# 13. Riesgos observados

```text
Riesgo 1: El dueño puede asumir que la planilla confirma stock físico real.
Mitigación: declarar que la fuente es stock declarado hasta validar conteo.

Riesgo 2: La diferencia sistema/físico puede leerse como merma o robo.
Mitigación: tratarla como diferencia visible a investigar.

Riesgo 3: Los días de stock estimados pueden confundirse con rotación real.
Mitigación: exigir histórico suficiente antes de hablar de rotación.

Riesgo 4: El stock negativo puede contaminar cálculos.
Mitigación: bloquear como probable error de carga o sincronización.
```

---

# 14. Decisión sobre el piloto

```text
PILOT_003_RESULT: SUCCESS_SIMULATED
PRODUCT_SIGNAL: VALID
FIRST_AID_STOCK_USE_CASE: VALIDATED_AS_CONTROLLED_CASE
READY_FOR_REAL_PILOT: YES
```

El piloto valida que `Primeros Auxilios GPT V1` puede revisar una planilla de stock de forma útil sin afirmar stock físico real ni diagnosticar rotación.

---

# 15. Próximo paso recomendado

Ejecutar `PILOT_004` con:

```text
CASH_BANK_OR_SIMPLE_RECONCILIATION
```

Motivo:

```text
Permite probar el límite entre caja/banco con una fuente, conciliación parcial y conciliación real no afirmable sin segunda fuente suficiente.
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
