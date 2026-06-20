# FIRST_AID_GPT_V1_ASSISTED_PILOT_004

## Estado

```text
Tipo: PRODUCT_PILOT_LOG
Estado: SIMULATED_CONTROLLED_PILOT
Runtime impact: NONE
Code impact: NONE
Evidence impact: SYNTHETIC_XLSX_EXTERNAL
```

## Propósito

Registrar el cuarto piloto asistido controlado de `Primeros Auxilios GPT V1`, usando un Excel sintético de caja/banco/conciliación simple para probar el límite entre:

```text
movimientos observables
vs
conciliación parcial
vs
conciliación real no afirmable sin segunda fuente suficiente
```

Este piloto usa como evidencia externa sintética:

```text
first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx
```

El archivo no se considera evidencia real de una PyME ni se incorpora como runtime.

---

# 1. Veredicto

```text
PILOT_004: COMPLETED_SIMULATED_CONTROLLED
FIRST_AID_SCOPE: RESPECTED
DIAGNOSTIC_CLAIMS: NONE
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
FORMULA_ERRORS: 0
```

---

# 2. Caso usado

```yaml
pilot_case_log:
  pilot_id: PILOT_004
  date: 2026-06-20
  operator: assisted_simulated
  source_channel: uploaded_xlsx_sandbox

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
    original_phrase: "Tengo movimientos de banco, caja, POS y Mercado Pago, pero no sé qué coincide, qué falta y qué no puedo cerrar todavía."
    selected_first_aid_option: CASH_BANK_OR_SIMPLE_RECONCILIATION
    expected_outcome_by_owner: revisar coincidencias, diferencias visibles, movimientos sin contraparte y límites de conciliación
    urgency: media

  evidence_received:
    evidence_type: XLSX_SYNTHETIC
    file_names:
      - first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx
    source_description: workbook sintético con movimientos de banco, caja diaria, POS y Mercado Pago; incluye importes, medios de pago, referencias externas, diferencias y señales First Aid
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
Categorias
Caja_Banco
Revision_PymIA
```

La hoja principal contiene 20 movimientos con campos de:

```text
ID movimiento
Fecha
Fuente
Tipo movimiento
Descripción
Importe declarado
Importe banco
Importe caja/POS
Medio de pago
Referencia externa
Estado esperado
Observación dueño
Diferencia banco vs caja
Señal First Aid
Límite owner-safe
```

El archivo contiene fórmulas en:

```text
Caja_Banco!M:O
Revision_PymIA!B16:B27
```

---

# 4. Validación del Excel

```text
Total movimientos: 20
OK_COINCIDENTE: 4
DIFERENCIA_MENOR_COMISION: 2
BANCO_SIN_CONTRAPARTE: 2
CAJA_SIN_BANCO: 2
IMPORTE_FALTANTE: 1
IMPORTE_AMBIGUO_NO_COMPARABLE: 2
IMPORTE_CERO_A_CONFIRMAR: 1
POSIBLE_DUPLICADO: 2
FECHA_FUERA_DE_PERIODO: 1
RETIRO_DECLARADO: 1
NO_CONCILIABLE_CON_UNA_FUENTE: 2
Formula errors: 0
```

---

# 5. Casos de prueba incluidos

```text
movimiento coincidente exacto
movimiento coincidente con diferencia menor por comisión
movimiento en banco sin caja/POS
movimiento en caja/POS sin banco
importe negativo válido
importe cero sospechoso
importe faltante
importe textual ambiguo
formato argentino monetario como texto literal
movimiento duplicado posible
referencia externa faltante
retiro del dueño declarado
comisión de Mercado Pago
transferencia sin identificación
fecha fuera de período
movimiento unilateral no conciliable con una sola fuente
```

---

# 6. Lectura de admisión

El caso entra en Primeros Auxilios porque:

```text
hay una fuente puntual y revisable
el objetivo es marcar señales de conciliación, no cerrar conciliación real
la salida esperada es advertencia, clasificación y pedido de evidencia
no requiere ejecutar macros
no requiere auditoría contable
no requiere afirmar fraude, pérdida o dolo
no requiere afirmar caja real ni banco conciliado definitivamente
```

Clasificación:

```text
selected_first_aid_option: CASH_BANK_OR_SIMPLE_RECONCILIATION
service_depth: FIRST_AID
```

---

# 7. Revisión simulada

```yaml
review_summary:
  what_was_received: workbook sintético con 20 movimientos de banco, caja diaria, POS y Mercado Pago
  what_could_be_reviewed: coincidencias exactas, diferencias menores, movimientos sin contraparte, importes faltantes, importes ambiguos, duplicados posibles, retiros declarados y fechas fuera de período

  visible_signals:
    - 4 movimientos aparecen como OK_COINCIDENTE
    - 2 movimientos muestran DIFERENCIA_MENOR_COMISION
    - 2 movimientos aparecen como BANCO_SIN_CONTRAPARTE
    - 2 movimientos aparecen como CAJA_SIN_BANCO
    - 1 movimiento tiene IMPORTE_FALTANTE
    - 2 movimientos tienen IMPORTE_AMBIGUO_NO_COMPARABLE
    - 1 movimiento tiene IMPORTE_CERO_A_CONFIRMAR
    - 2 movimientos aparecen como POSIBLE_DUPLICADO
    - 1 movimiento está en FECHA_FUERA_DE_PERIODO
    - 1 movimiento es RETIRO_DECLARADO
    - 2 movimientos son NO_CONCILIABLE_CON_UNA_FUENTE

  visible_disorder_or_quality_issues:
    - importes textuales ambiguos
    - importes faltantes entre banco y caja/POS
    - referencias externas faltantes
    - posibles duplicados por misma fecha, importe y referencia
    - movimientos fuera del período
    - transferencias sin identificación de contraparte
    - diferencias compatibles con comisiones que requieren liquidación externa

  computed_or_normalized_values:
    - diferencia_banco_vs_caja cuando los importes son comparables
    - señal First Aid por movimiento
    - conteos automáticos por categoría de señal

  warnings:
    - coincidencia exacta no equivale a auditoría completa
    - diferencia menor puede ser comisión, retención u otra causa
    - banco sin contraparte no implica fraude
    - caja sin banco no implica pérdida
    - retiro declarado no implica irregularidad
    - importe ambiguo no debe calcularse silenciosamente
    - con una sola fuente no se cierra conciliación real

  what_cannot_be_claimed:
    - no puede afirmarse fraude
    - no puede afirmarse dolo o responsabilidad humana
    - no puede afirmarse pérdida definitiva
    - no puede afirmarse conciliación cerrada
    - no puede afirmarse caja real
    - no puede afirmarse exactitud contable

  missing_evidence:
    - extracto bancario oficial
    - liquidaciones POS y Mercado Pago
    - arqueo físico de caja
    - comprobantes o recibos
    - identificación de transferencias
    - detalle de comisiones y retenciones
    - período contable confirmado
```

---

# 8. Señales owner-safe destacables

## 8.1 Movimiento coincidente exacto

```text
Hay movimientos donde banco y caja/POS coinciden en importe.
Esto permite marcarlos como comparables, pero no cierra una auditoría completa.
```

## 8.2 Diferencia menor por comisión

```text
Hay diferencias menores compatibles con comisión, retención o gasto operativo de pasarela.
Requieren liquidación externa para confirmar causa.
```

## 8.3 Banco sin contraparte

```text
Hay movimientos visibles en banco sin equivalente en caja/POS.
Esto es una señal para investigar, no una prueba de pérdida o fraude.
```

## 8.4 Caja/POS sin banco

```text
Hay movimientos visibles en caja o POS sin contraparte bancaria.
Puede ser efectivo, cierre pendiente, demora de acreditación o falta de registro.
```

## 8.5 Importe ambiguo no comparable

```text
Un importe textual o ambiguo no debe calcularse silenciosamente.
Se pide aclaración antes de comparar.
```

## 8.6 Posible duplicado

```text
Movimientos con misma fecha, importe y referencia pueden indicar duplicado.
No se elimina ni corrige sin validación del dueño.
```

## 8.7 No conciliable con una fuente

```text
Cuando hay una sola fuente o información unilateral, puede marcarse señal.
No puede cerrarse conciliación real.
```

---

# 9. Devolución owner-safe simulada

```text
Recibimos una planilla de movimientos de banco, caja diaria, POS y Mercado Pago con 20 registros.
Con esta fuente se puede hacer una primera revisión: movimientos coincidentes, diferencias menores, movimientos sin contraparte, importes faltantes, valores ambiguos y posibles duplicados.

Lo que sí se puede revisar:
- movimientos donde banco y caja/POS coinciden;
- diferencias menores compatibles con comisiones;
- movimientos de banco sin contraparte interna;
- movimientos de caja/POS sin contraparte bancaria;
- importes faltantes o ambiguos;
- posibles duplicados;
- registros fuera del período;
- retiros declarados.

Señales visibles:
- hay movimientos comparables;
- hay diferencias menores que podrían corresponder a comisiones;
- hay movimientos sin contraparte;
- hay importes ambiguos que no deben calcularse automáticamente;
- hay posibles duplicados que requieren validación;
- hay movimientos que no pueden conciliarse con una sola fuente.

Lo que no se puede afirmar todavía:
- no se puede afirmar fraude;
- no se puede afirmar pérdida definitiva;
- no se puede cerrar conciliación real;
- no se puede confirmar caja real;
- no se puede atribuir responsabilidad humana;
- no se puede dar validez contable final.

Próximo paso razonable:
conseguir extracto bancario oficial, liquidaciones de POS/Mercado Pago, arqueo de caja y comprobantes de movimientos sin contraparte.
```

---

# 10. Preguntas siguientes al dueño

```text
1. ¿Tenés el extracto bancario oficial del período?
2. ¿Tenés las liquidaciones de Mercado Pago o POS?
3. ¿La caja diaria representa efectivo contado o carga manual?
4. ¿Los retiros del dueño están documentados?
5. ¿Los movimientos duplicados son repetición real o error de carga?
6. ¿Querés revisar sólo señales o avanzar hacia conciliación con segunda fuente?
```

---

# 11. Bloqueos sanos aplicados

```text
No se afirmó fraude.
No se afirmó pérdida definitiva.
No se afirmó conciliación cerrada.
No se confirmó caja real.
No se atribuyó responsabilidad humana.
No se calculó sobre importes ambiguos.
No se trató una fuente unilateral como prueba suficiente.
```

---

# 12. Resultado del piloto

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

# 13. Aprendizaje de producto

```yaml
product_learning:
  what_worked:
    - El límite entre señal de conciliación y conciliación real queda claro.
    - Banco sin contraparte y caja sin banco se expresan como señales, no como acusaciones.
    - IMPORTE_AMBIGUO_NO_COMPARABLE evita cálculos silenciosos.
    - NO_CONCILIABLE_CON_UNA_FUENTE protege contra sobrediagnóstico.
    - El retiro declarado puede registrarse sin moralizar ni diagnosticar irregularidad.

  what_confused_owner:
    - Puede confundir coincidencia exacta con conciliación cerrada.
    - Puede interpretar movimiento sin contraparte como pérdida o fraude.
    - Puede asumir que diferencia menor siempre es comisión.
    - Puede no distinguir extracto oficial, caja manual y liquidación POS.

  repeated_pain_detected:
    - banco/caja/POS dispersos
    - comisiones no documentadas
    - transferencias sin identificación
    - referencias faltantes
    - movimientos duplicados posibles
    - importes manuales ambiguos

  missing_tool_or_template:
    - FIRST_AID_CASH_BANK_RESPONSE_TEMPLATE
    - FIRST_AID_RECONCILIATION_MINIMUM_EVIDENCE_CHECKLIST
    - FIRST_AID_BANK_WITHOUT_COUNTERPART_OWNER_QUESTION_TEMPLATE
    - FIRST_AID_CASH_WITHOUT_BANK_OWNER_QUESTION_TEMPLATE

  language_adjustment_needed:
    - usar "sin contraparte visible" en vez de "faltante"
    - usar "diferencia compatible con comisión" en vez de "comisión confirmada"
    - usar "conciliación parcial" en vez de "conciliación cerrada"
    - usar "movimiento a validar" en vez de "error"

  candidate_future_improvement:
    - checklist de suficiencia para conciliación real
    - plantilla owner-safe para movimientos sin contraparte
    - plantilla owner-safe para diferencias por comisión
    - plantilla owner-safe para retiros declarados
```

---

# 14. Riesgos observados

```text
Riesgo 1: El dueño puede interpretar movimientos sin contraparte como fraude.
Mitigación: declarar que son señales a investigar, no prueba de irregularidad.

Riesgo 2: Coincidencias exactas pueden confundirse con conciliación cerrada.
Mitigación: declarar que coincidencia local no equivale a auditoría completa.

Riesgo 3: Diferencias menores pueden asumirse como comisión.
Mitigación: pedir liquidación de pasarela o extracto oficial.

Riesgo 4: Con una fuente unilateral se puede sobrediagnosticar.
Mitigación: categoría NO_CONCILIABLE_CON_UNA_FUENTE.
```

---

# 15. Decisión sobre el piloto

```text
PILOT_004_RESULT: SUCCESS_SIMULATED
PRODUCT_SIGNAL: VALID
FIRST_AID_CASH_BANK_USE_CASE: VALIDATED_AS_CONTROLLED_CASE
READY_FOR_REAL_PILOT: YES
```

El piloto valida que `Primeros Auxilios GPT V1` puede revisar caja/banco/conciliación simple de forma útil sin afirmar fraude, pérdida ni conciliación real cerrada.

---

# 16. Próximo paso recomendado

Crear el cierre de tanda piloto:

```text
FIRST_AID_GPT_V1_PILOT_BATCH_REVIEW.md
```

Debe revisar:

```text
PILOT_001 — ventas sin costos
PILOT_002 — precios/costos/margen estimado
PILOT_003 — stock/inventario
PILOT_004 — caja/banco/conciliación simple
```

---

# 17. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_DIAGNOSTIC
NO_OCF_PRODUCTIVE_WRITE
NO_AUTOMATION
NO_CHANNEL_INTEGRATION
```

Este piloto es aprendizaje de producto, no implementación.
