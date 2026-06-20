# FIRST_AID_GPT_V1_PILOT_BATCH_REVIEW

## Estado

```text
Tipo: PRODUCT_PILOT_BATCH_REVIEW
Estado: CANDIDATE_READY_FOR_REAL_ASSISTED_PILOTS
Runtime impact: NONE
Code impact: NONE
```

Esta revisión consolida la tanda de cuatro pilotos asistidos controlados de `Primeros Auxilios GPT V1` y decide si el frente está listo para salir a pilotos reales asistidos.

No autoriza runtime, diagnóstico real, OCF productivo, integración, canales externos, automatización ni nuevas features.

---

# 1. Veredicto

```text
FIRST_AID_GPT_V1_ASSISTED_PILOT_BATCH: PASS_CONTROLLED
READY_FOR_REAL_ASSISTED_PILOTS: YES
READY_FOR_AUTOMATED_PRODUCT: NO
READY_FOR_RUNTIME_EXPANSION: NO
```

La tanda controlada muestra que `Primeros Auxilios GPT V1` puede entregar claridad inicial a un dueño PyME sin cruzar a diagnóstico, sin prometer producto automático y sin abrir Nivel 2 antes de tiempo.

La salida recomendada no es automatización. La salida recomendada es piloto real asistido, manual, registrado y con límites owner-safe explícitos.

---

# 2. Alcance de la tanda

La tanda revisada incluye cuatro pilotos simulados/controlados:

```text
PILOT_001 — ventas sin costos
PILOT_002 — lista de precios/costos/margen estimado
PILOT_003 — stock/inventario
PILOT_004 — caja/banco/conciliación simple
```

Fuentes documentales:

```text
docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_001.md
docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_002.md
docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_003.md
docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_004.md
docs/producto/FIRST_AID_GPT_V1_PILOT_OFFER.md
docs/producto/FIRST_AID_GPT_V1_PILOT_SCRIPT.md
docs/producto/FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE.md
docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md
```

La tanda evalúa aprendizaje de producto, no performance técnica ni suficiencia de runtime.

---

# 3. Resumen de pilotos

## PILOT_001 — ventas sin costos

```text
Resultado: SUCCESS_SIMULATED
Caso: SALES_OR_COMMERCIAL_DATA
```

Validó que una planilla de ventas puede ordenar productos, cantidades y ventas, pero no permite afirmar rentabilidad. La falta de costos bloquea margen y convierte el próximo paso natural en pedir lista de costos.

Validaciones principales:

```text
ventas disponibles no equivalen a rentabilidad
productos más vendidos no necesariamente dejan más plata
falta de costos bloquea margen/rentabilidad
próximo paso natural: pedir lista de costos
```

## PILOT_002 — precios/costos

```text
Resultado: SUCCESS_SIMULATED
Caso: PRICE_OR_COST_LIST
```

Validó que puede estimarse margen bruto cuando hay precio y costo legibles, sin afirmar rentabilidad real ni recomendar precio definitivo.

Validaciones principales:

```text
margen bruto estimado vs rentabilidad real
costo faltante
precio ambiguo
costo "nan"
costo cero declarado
margen negativo como señal
formato argentino monetario
no recomendar precio definitivo
```

## PILOT_003 — stock/inventario

```text
Resultado: SUCCESS_SIMULATED
Caso: STOCK_OR_INVENTORY
```

Validó que el sistema puede revisar señales de stock sin afirmar stock físico real, merma, robo, rotación ni capital inmovilizado confirmado.

Validaciones principales:

```text
stock declarado vs stock físico real
stock bajo declarado
stock negativo
diferencia sistema/físico
dato ambiguo no comparable
posible stock inmovilizado
rotación no afirmable sin histórico suficiente
```

## PILOT_004 — caja/banco/conciliación simple

```text
Resultado: SUCCESS_SIMULATED
Caso: CASH_BANK_OR_SIMPLE_RECONCILIATION
```

Validó que se pueden marcar coincidencias, diferencias visibles y movimientos sin contraparte sin afirmar fraude, pérdida ni conciliación cerrada.

Validaciones principales:

```text
movimiento coincidente exacto
diferencia menor compatible con comisión
banco sin contraparte
caja/POS sin banco
importe faltante
importe ambiguo no comparable
importe cero a confirmar
posible duplicado
fecha fuera de período
retiro declarado
no conciliable con una sola fuente
no afirmar fraude, pérdida ni conciliación cerrada
```

---

# 4. Tabla comparativa

| Piloto | Caso | Evidencia | Qué pudo revisar | Qué no pudo afirmar | Dato faltante principal | Resultado | Listo para piloto real |
|---|---|---|---|---|---|---|---|
| PILOT_001 | SALES_OR_COMMERCIAL_DATA | Planilla de ventas sin costos | Productos más vendidos, cantidades y estructura básica de ventas | Rentabilidad, margen real, stock físico o conveniencia comercial | Lista de costos o precios de compra | SUCCESS_SIMULATED | YES |
| PILOT_002 | PRICE_OR_COST_LIST | Lista de precios, costos y stock declarado | Margen bruto estimado, costo faltante, precio ambiguo, costo cero, margen negativo | Rentabilidad real, precio definitivo, stock físico o conveniencia por canal | Comisiones, descuentos, impuestos, envíos y costos indirectos | SUCCESS_SIMULATED | YES |
| PILOT_003 | STOCK_OR_INVENTORY | Stock sistema, stock declarado, conteo físico parcial y ventas 30d declaradas | Stock bajo, stock negativo, diferencias sistema/físico, dato ambiguo, posible inmovilización | Stock físico real, merma, robo, rotación real o capital inmovilizado confirmado | Conteo físico completo, movimientos y ventas históricas suficientes | SUCCESS_SIMULATED | YES |
| PILOT_004 | CASH_BANK_OR_SIMPLE_RECONCILIATION | Movimientos de banco, caja, POS y Mercado Pago | Coincidencias, diferencias menores, movimientos sin contraparte, importes ambiguos, posibles duplicados | Fraude, pérdida definitiva, caja real o conciliación cerrada | Extracto oficial, liquidaciones POS/MP, arqueo de caja y comprobantes | SUCCESS_SIMULATED | YES |

---

# 5. Patrones de dolor detectados

1. El dueño trae fuentes parciales, no evidencia completa.
2. La primera utilidad no es diagnosticar, sino ordenar límites.
3. Los datos ambiguos deben bloquear cálculo silencioso.
4. El lenguaje owner-safe reduce riesgo.
5. Cada caso genera una pregunta siguiente natural.
6. First Aid puede entregar valor sin cruzar a Nivel 2.
7. El dueño suele pedir una conclusión más fuerte que la evidencia disponible.
8. Las fuentes operativas mezclan datos declarados, datos de sistema y valores manuales.
9. La ambigüedad de formato es un riesgo de producto, no sólo un problema técnico.
10. La claridad sobre lo que no se puede afirmar genera confianza y evita sobrediagnóstico.

---

# 6. Evidencia que los dueños suelen traer

```text
planillas de ventas
listas de precios
listas de costos incompletas
stock declarado o exportado de sistema
conteos físicos parciales
movimientos de caja
movimientos bancarios
liquidaciones o resúmenes de pasarelas
notas manuales del dueño
campos con formatos mixtos
```

Esta evidencia suele ser suficiente para ordenar señales iniciales, pero no para cerrar diagnóstico ni concluir causalidad.

---

# 7. Evidencia que suele faltar

```text
costos actualizados
comisiones por canal
impuestos aplicables
descuentos y promociones
costos de envío o packaging
costos indirectos
conteo físico completo
movimientos de stock
histórico de ventas suficiente
extracto bancario oficial
liquidaciones POS o Mercado Pago
arqueo de caja
comprobantes de movimientos sin contraparte
período contable confirmado
```

La falta de evidencia no debe ocultarse ni compensarse con inferencias. Debe convertirse en pregunta siguiente owner-safe.

---

# 8. Límites owner-safe que funcionaron

```text
ventas no equivalen a ganancia
margen bruto estimado no equivale a rentabilidad real
stock declarado no equivale a stock físico
conteo parcial no confirma merma
stock inmovilizado es señal, no diagnóstico
coincidencia bancaria local no cierra conciliación
banco sin contraparte no implica fraude
caja/POS sin banco no implica pérdida
importe ambiguo no se calcula silenciosamente
una sola fuente no permite cerrar conciliación real
```

Estos límites funcionaron porque traducen incertidumbre técnica en lenguaje comprensible para el dueño.

---

# 9. Riesgos de sobrediagnóstico controlados

| Riesgo | Control aplicado |
|---|---|
| Confundir ventas con ganancia | Declarar que faltan costos para hablar de margen o rentabilidad. |
| Confundir margen bruto con rentabilidad real | Usar “margen bruto estimado” y pedir costos indirectos/comisiones. |
| Tratar margen negativo como diagnóstico | Presentarlo como señal a validar. |
| Tratar stock declarado como stock real | Pedir conteo físico y movimientos. |
| Afirmar merma o robo por diferencia de stock | Usar “diferencia visible” y no atribuir causa. |
| Confundir días de stock con rotación real | Pedir histórico suficiente. |
| Interpretar banco sin contraparte como fraude | Usar “sin contraparte visible” y pedir soporte. |
| Cerrar conciliación con una fuente | Declarar “no conciliable con una sola fuente”. |
| Calcular valores ambiguos | Bloquear cálculo y pedir aclaración. |

---

# 10. Plantillas candidatas faltantes

Estas plantillas son candidatas documentales. No se implementan en este documento.

```text
FIRST_AID_SALES_WITHOUT_COSTS_RESPONSE_TEMPLATE
FIRST_AID_MARGIN_MINIMUM_EVIDENCE_CHECKLIST
FIRST_AID_PRICE_COST_RESPONSE_TEMPLATE
FIRST_AID_STOCK_RESPONSE_TEMPLATE
FIRST_AID_STOCK_MINIMUM_EVIDENCE_CHECKLIST
FIRST_AID_CASH_BANK_RESPONSE_TEMPLATE
FIRST_AID_RECONCILIATION_MINIMUM_EVIDENCE_CHECKLIST
FIRST_AID_AMBIGUOUS_VALUE_OWNER_QUESTION_TEMPLATE
```

Prioridad sugerida:

| Plantilla | Motivo |
|---|---|
| FIRST_AID_AMBIGUOUS_VALUE_OWNER_QUESTION_TEMPLATE | Aparece en precios, stock y caja/banco. |
| FIRST_AID_MARGIN_MINIMUM_EVIDENCE_CHECKLIST | Se necesita para evitar confundir margen bruto con rentabilidad. |
| FIRST_AID_RECONCILIATION_MINIMUM_EVIDENCE_CHECKLIST | Protege contra conciliación prematura con fuente única. |
| FIRST_AID_STOCK_MINIMUM_EVIDENCE_CHECKLIST | Protege contra afirmar stock físico o rotación real. |

---

# 11. Casos listos para piloto real

```text
ventas sin costos
lista de precios/costos
stock/inventario declarado
caja/banco/conciliación simple con alcance limitado
```

Condiciones para aceptarlos:

```text
el dueño entiende que es revisión asistida, no diagnóstico final
hay una fuente revisable
hay una frase de preocupación concreta
el operador declara límites antes de devolver señales
el caso se registra manualmente en plantilla de piloto
no se promete automatización ni integración
```

La recomendación es recibir 3 casos reales, no escalar a producción.

---

# 12. Casos que NO deben venderse todavía

```text
rentabilidad real por producto o canal
recomendación definitiva de precios
conciliación bancaria cerrada
detección de fraude o pérdida
confirmación de stock físico real
diagnóstico de merma o robo
rotación real sin histórico suficiente
capital inmovilizado confirmado
auditoría contable
OCF productivo automático
```

Estos casos requieren más evidencia, otro nivel de servicio o una frontera contractual todavía no abierta para este frente.

---

# 13. Criterio de salida a la calle

Primeros Auxilios GPT V1 puede salir a piloto real asistido sólo si se cumplen estas condiciones:

```text
se reciben máximo 3 casos reales iniciales
el operador usa el guion vigente
cada caso queda registrado en la plantilla de log
la devolución distingue “señal visible” de “conclusión no afirmable”
los datos ambiguos bloquean cálculo
no se promete diagnóstico
no se promete automatización
no se escribe OCF productivo
no se abren canales externos automatizados
no se modifica runtime
```

Criterio de éxito del piloto real:

```text
el dueño entiende qué puede revisar hoy
el dueño entiende qué no se puede afirmar todavía
aparece una pregunta siguiente natural
se identifica evidencia faltante concreta
no se produce sobrediagnóstico
```

---

# 14. Recomendación final

```text
FIRST_AID_GPT_V1_ASSISTED_PILOT_BATCH: PASS_CONTROLLED
READY_FOR_REAL_ASSISTED_PILOTS: YES
READY_FOR_AUTOMATED_PRODUCT: NO
READY_FOR_RUNTIME_EXPANSION: NO
```

Recomendación de producto:

```text
Avanzar a 3 pilotos reales asistidos, manuales y registrados.
No venderlo como producto automático.
No abrir runtime.
No prometer diagnóstico.
No convertir aprendizaje en OCF productivo.
```

---

# 15. Próximo frente recomendado

```text
FIRST_AID_GPT_V1_REAL_PILOT_INTAKE_PROTOCOL
```

Objetivo:

```text
definir cómo recibir 3 casos reales de dueños PyME sin abrir runtime ni prometer diagnóstico.
```

Debe resolver:

```text
criterios de admisión real
texto de consentimiento y límites
qué evidencia puede recibir el operador
cómo registrar aprendizaje sin OCF productivo
cómo cerrar una devolución owner-safe
cuándo rechazar o pausar un caso
```

---

# 16. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_TESTS
NO_DIAGNOSTIC
NO_OCF_PRODUCTIVE_WRITE
NO_AUTOMATION
NO_CHANNEL_INTEGRATION
NO_NEW_FEATURES
```

Este documento cierra aprendizaje de tanda piloto controlada. No implementa, no integra y no autoriza producto automático.
