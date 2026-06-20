# FIRST_AID_GPT_V1_PILOT_SCRIPT

## Estado

```text
Tipo: PRODUCT_OPERATING_SCRIPT
Estado: CANDIDATE_READY_FOR_ASSISTED_PILOT
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Definir un guion operativo simple para ejecutar pilotos asistidos de `Primeros Auxilios GPT V1` con dueños PyME reales, sin abrir runtime nuevo, sin diagnóstico y sin prometer más que una revisión inicial prudente.

Este documento baja a operación la oferta definida en:

```text
docs/producto/FIRST_AID_GPT_V1_PILOT_OFFER.md
```

Y respeta los límites de:

```text
docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md
docs/producto/FIRST_AID_OWNER_EXPERIENCE_V1.md
docs/producto/FIRST_AID_PYME_PAIN_AUDIT_V1.md
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
```

---

# 1. Veredicto

```text
FIRST_AID_GPT_V1_PILOT_SCRIPT = READY_FOR_ASSISTED_PILOT
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

Este guion sirve para operación asistida manual o semi-manual, no para activar producto automático.

---

# 2. Objetivo del piloto

Validar si un dueño PyME obtiene claridad inmediata cuando entrega una fuente o problema puntual.

El piloto debe responder:

```text
¿El dueño entiende mejor qué tiene?
¿El dueño entiende qué dato falta?
¿El dueño confía en los límites de la respuesta?
¿Aparece un próximo paso razonable?
¿El caso escala naturalmente o se cierra como revisión puntual?
```

---

# 3. Mensaje inicial al dueño

```text
Te propongo hacer una revisión inicial y prudente.
No es un diagnóstico completo de tu empresa.
Primero ubicamos mínimamente tu negocio, después miramos el archivo o problema puntual.
Al final te devuelvo qué se puede leer, qué señales aparecen, qué no se puede afirmar todavía y cuál sería el próximo paso razonable.
```

Mensaje breve alternativo:

```text
Vamos a ordenar este problema puntual sin vender humo: vemos qué hay, qué falta y qué se puede afirmar con prudencia.
```

---

# 4. Pregunta madre

```text
¿Qué necesitás resolver hoy?
```

Para este piloto, sólo avanzar si la respuesta entra en:

```text
Primeros Auxilios:
Tengo algo puntual para ordenar o revisar ahora.
```

Si el dueño pide diagnóstico completo, responder:

```text
Eso ya no es Primeros Auxilios. Podemos empezar por una revisión puntual, pero para diagnosticar necesitamos más evidencia y otro alcance.
```

---

# 5. Ficha mínima obligatoria

Antes de analizar la evidencia, pedir:

```text
Para ubicar bien el caso, respondeme esto:

1. ¿Cómo se llama tu empresa o negocio?
2. ¿A qué se dedica?
3. ¿Qué tipo de operación tiene?
   - comercio
   - servicios
   - fábrica / producción
   - distribución / mayorista
   - gastronomía
   - profesional / estudio
   - otra
4. ¿Vendés por qué canales?
   - local físico
   - WhatsApp
   - Mercado Libre
   - ecommerce
   - redes sociales
   - vendedores
   - mayorista
   - otro
5. ¿Manejás stock?
   - sí
   - no
   - no estoy seguro / depende
6. ¿Qué querés revisar ahora?
```

Regla:

```text
No bloquear si una respuesta es incompleta.
Aceptar “no sé”, “no estoy seguro” o “depende”.
No empezar por el archivo sin esta capa mínima.
```

---

# 6. Selección del caso puntual

Luego preguntar:

```text
¿Qué querés revisar ahora?
```

Opciones:

```text
A. Un Excel o planilla desordenada
B. Fórmulas, totales o cálculos que no cierran
C. Una lista de precios o costos
D. Stock o inventario
E. Caja, banco o conciliación simple
F. Ventas o datos comerciales
G. Una tarea manual repetitiva
H. Otro archivo o problema puntual
```

El operador debe registrar:

```text
case_option
owner_phrase
expected_evidence
known_limit
```

---

# 7. Pedido de evidencia por opción

## A. Excel o planilla desordenada

```text
Subí la planilla y contame en una frase qué querés que miremos.
```

## B. Fórmulas, totales o cálculos que no cierran

```text
Subí una copia del archivo y decime qué resultado te parece incorrecto.
```

Límite:

```text
No ejecutar macros automáticamente.
No certificar cálculo crítico sin entender proceso y evidencia.
```

## C. Lista de precios o costos

```text
Subí la lista y decime si querés mirar precios, costos o margen estimado.
```

Límite:

```text
No calcular rentabilidad real sin costos suficientes, comisiones, impuestos o contexto aplicable.
```

## D. Stock o inventario

```text
Subí el archivo de stock y contame si representa stock físico, sistema o control manual.
```

Límite:

```text
No confirmar stock real sin conteo o evidencia observada.
```

## E. Caja, banco o conciliación simple

```text
Subí el extracto o reporte que no te cierra y decime contra qué debería coincidir.
```

Límite:

```text
Con una sola fuente se hace triage.
Para conciliación real suele hacer falta una segunda fuente.
```

## F. Ventas o datos comerciales

```text
Subí el archivo de ventas y contame qué querés mirar: productos, clientes, fechas, canales o totales.
```

Límite:

```text
Ventas no es ganancia.
No concluir rentabilidad sin costos.
```

## G. Tarea manual repetitiva

```text
Contame qué tarea repetís, cada cuánto, cuánto tarda y qué archivos o sistemas intervienen.
```

Límite:

```text
Primeros Auxilios sólo evalúa si parece automatizable.
No implementa automatización.
```

## H. Otro archivo o problema puntual

```text
Subí el archivo o explicá brevemente qué necesitás ordenar.
```

Límite:

```text
Si excede una revisión inicial, escalar a diagnóstico acotado o laboratorio organizacional.
```

---

# 8. Plantilla de recepción interna

```yaml
pilot_case:
  business_name:
  business_activity:
  operation_type:
  sales_channels: []
  handles_stock:
  selected_first_aid_option:
  owner_phrase:
  evidence_received:
  evidence_type:
  operator_initial_read:
  obvious_limitations: []
  missing_evidence: []
  safe_to_review: true|false
```

---

# 9. Checklist de admisión

Antes de revisar, confirmar:

```text
[ ] Hay una frase del dueño sobre lo que quiere revisar.
[ ] Hay ficha mínima suficiente.
[ ] Hay archivo, muestra o descripción suficiente.
[ ] El caso cabe en Primeros Auxilios.
[ ] No exige diagnóstico completo.
[ ] No exige ejecutar macros riesgosas.
[ ] No exige certificar stock, caja, fraude o resultado contable.
[ ] Se pueden declarar límites de forma clara.
```

Si falla uno de los puntos críticos, bloquear con pedido de evidencia.

---

# 10. Plantilla de devolución owner-safe

```text
## Revisión inicial

### 1. Qué recibimos
[archivo / fuente / descripción recibida]

### 2. Qué sabemos del negocio
[nombre, actividad, operación, canales, stock si aplica]

### 3. Qué parece ser el problema
[clasificación simple: Excel desordenado, precios/costos, stock, caja, ventas, etc.]

### 4. Qué se pudo revisar
[observaciones concretas sin diagnóstico]

### 5. Señales visibles
[señales puntuales, no conclusiones causales]

### 6. Qué no puedo afirmar todavía
[límites por evidencia insuficiente]

### 7. Qué dato falta
[evidencia concreta necesaria]

### 8. Próximo paso razonable
[pregunta siguiente o acción proporcional]
```

---

# 11. Ejemplo de devolución breve

```text
Recibimos una planilla de ventas con productos, cantidades y precios, pero sin costos.
Sabemos que el negocio vende por local físico y WhatsApp, y maneja stock.
La fuente permite ordenar ventas y detectar productos más vendidos.
No permite afirmar margen ni rentabilidad real porque faltan costos, comisiones y descuentos.
La señal visible es que hay productos con mucha venta, pero todavía no sabemos si dejan plata.
El próximo paso razonable es sumar una lista de costos o precios de compra para revisar margen estimado.
```

---

# 12. Bloqueos sanos

## Sin evidencia suficiente

```text
Con lo que tengo puedo entender el pedido, pero no revisar el problema. Necesito que subas una planilla, captura o ejemplo concreto.
```

## Columna ambigua

```text
Veo una columna llamada “precio”, pero no puedo saber si es precio de venta, costo o lista sin IVA. ¿Qué representa?
```

## Rentabilidad sin costos

```text
Puedo ordenar ventas, pero no afirmar rentabilidad. Para margen necesito costos o precios de compra.
```

## Stock real sin conteo

```text
Puedo revisar el archivo de stock, pero no confirmar stock físico real sin conteo o fuente observada.
```

## Conciliación con una sola fuente

```text
Con una sola fuente puedo marcar movimientos y faltantes, pero no cerrar una conciliación. Necesito la fuente contra la que debería coincidir.
```

## Macro riesgosa

```text
No conviene ejecutar macros automáticamente. Puedo revisar la estructura del archivo y marcar zonas de riesgo, pero no correr lógica desconocida sin copia segura y autorización explícita.
```

---

# 13. Escalamiento a Nivel 2

Escalar sólo si aparece una pregunta causal o una señal que exige cruce de evidencia.

Disparadores:

```text
¿Por qué no me queda plata?
¿Qué productos pierden margen?
¿Por qué no cierra la caja?
¿Qué stock me inmoviliza capital?
¿Qué canal me conviene?
```

Frase de transición:

```text
Esto ya excede Primeros Auxilios. Podemos pasar a un diagnóstico acotado si sumamos la evidencia necesaria.
```

No usar frases de venta agresiva.

---

# 14. Registro de resultado del piloto

Al terminar, registrar:

```yaml
pilot_result:
  clarity_delivered: yes|no|partial
  owner_understood_limits: yes|no|partial
  missing_evidence_identified: yes|no
  next_step_defined: yes|no
  escalated_to_level_2: yes|no
  owner_feedback:
  operator_notes:
```

---

# 15. Criterio de éxito

El piloto es exitoso si el dueño puede decir:

```text
Ahora entiendo mejor qué tengo.
Ahora sé qué dato falta.
Ahora sé qué no se puede afirmar todavía.
Ahora sé cuál es el próximo paso.
```

---

# 16. Criterio de fracaso

El piloto falla si:

```text
parece un lector genérico de Excel
no produce claridad
no pide evidencia faltante
promete diagnóstico
usa lenguaje demasiado técnico
no deja próximo paso
```

---

# 17. Regla final del operador

```text
Primero ubicar.
Después revisar.
Después limitar.
Después preguntar.
```

No diagnosticar.
No inventar.
No rellenar huecos.
No vender Nivel 2 sin señal real.

---

# 18. Próximo documento posible

Si este guion se acepta, el siguiente documento comercial puede ser:

```text
FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE.md
```

Para registrar 3 a 5 pilotos reales sin convertirlos en runtime.
