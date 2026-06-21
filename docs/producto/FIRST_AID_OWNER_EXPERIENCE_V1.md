# FIRST_AID_OWNER_EXPERIENCE_V1

## Estado

```text
Tipo: PRODUCT_UX_SPEC
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Definir la experiencia visible del dueño cuando elige:

```text
Primeros Auxilios
Tengo algo puntual para ordenar o revisar ahora.
```

Este documento no autoriza runtime, CLI, UI, rendering, storage, OCF write-model ni application wiring.

---

# 1. Regla rectora

Aunque el dueño elija Primeros Auxilios, PymIA debe capturar primero la primera capa formal mínima de la ficha organizacional.

Primeros Auxilios no empieza directamente por el archivo.

Primeros Auxilios empieza por una identificación mínima del organismo PyME.

Regla:

```text
opción elegida
→ primera capa formal de ficha organizacional
→ problema puntual
→ evidencia
→ revisión proporcional
```

---

# 2. Pregunta madre

La experiencia comienza con:

```text
¿Qué necesitás resolver hoy?
```

Opciones:

```text
1. Primeros Auxilios
   Tengo algo puntual para ordenar o revisar ahora.

2. Problema específico / diagnóstico sectorial
   Tengo un problema más complejo que quiero entender.

3. Estructura completa de la empresa
   Quiero analizar y ordenar la empresa como sistema.
```

Si elige `Primeros Auxilios`, no se salta la ficha mínima.

---

# 3. Primera capa formal obligatoria

Antes de pedir o analizar el archivo, PymIA debe capturar una capa mínima.

## Preguntas mínimas owner-facing

```text
Para ubicar bien tu caso, respondeme esto primero:

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

Estas preguntas no buscan completar toda la ficha.

Buscan evitar que el archivo sea tratado como si explicara por sí solo a la empresa.

---

# 4. Datos mínimos de ficha

La primera capa debe dejar, cuando sea posible:

```text
nombre visible del negocio
tipo de empresa
rubro o actividad
modelo operativo básico
canales de venta
presencia de stock
problema puntual elegido
frase textual del dueño
evidencia disponible o pendiente
```

Si el dueño no sabe responder algo, se acepta:

```text
desconocido
no estoy seguro
depende
```

No se debe bloquear Primeros Auxilios por falta de ficha completa.

Sí se debe evitar análisis sin encuadre mínimo.

---

# 5. Subopciones de Primeros Auxilios

Después de la capa formal mínima, PymIA pregunta:

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

---

# 6. Pedido de evidencia según subopción

## A. Excel o planilla desordenada

Pedir:

```text
Subí la planilla y contame en una frase qué querés que miremos.
```

Salida esperada:

```text
estructura probable
hojas útiles
columnas ambiguas
problemas visibles
datos faltantes
siguiente pregunta
```

## B. Fórmulas, totales o cálculos que no cierran

Pedir:

```text
Subí una copia del archivo y decime qué resultado te parece incorrecto.
```

Regla:

```text
No ejecutar macros automáticamente.
No certificar cálculo crítico sin entender proceso y evidencia.
```

## C. Lista de precios o costos

Pedir:

```text
Subí la lista y decime si querés mirar precios, costos o margen estimado.
```

Regla:

```text
No calcular rentabilidad real sin costos suficientes, comisiones, impuestos o contexto aplicable.
```

## D. Stock o inventario

Pedir:

```text
Subí el archivo de stock y contame si representa stock físico, sistema o control manual.
```

Regla:

```text
No confirmar stock real sin conteo o evidencia observada.
```

## E. Caja, banco o conciliación simple

Pedir:

```text
Subí el extracto o reporte que no te cierra y decime contra qué debería coincidir.
```

Regla:

```text
Con una sola fuente se hace triage.
Para conciliación real suele hacer falta una segunda fuente.
```

## F. Ventas o datos comerciales

Pedir:

```text
Subí el archivo de ventas y contame qué querés mirar: productos, clientes, fechas, canales o totales.
```

Regla:

```text
Ventas no es ganancia.
No concluir rentabilidad sin costos.
```

## G. Tarea manual repetitiva

Pedir:

```text
Contame qué tarea repetís, cada cuánto, cuánto tarda y qué archivos o sistemas intervienen.
```

Regla:

```text
Primeros Auxilios sólo evalúa si parece automatizable.
No implementa automatización.
```

## H. Otro archivo o problema puntual

Pedir:

```text
Subí el archivo o explicá brevemente qué necesitás ordenar.
```

Regla:

```text
Si el caso excede Primeros Auxilios, redirigir a diagnóstico sectorial o estructura completa.
```

---

# 7. Promesa visible al dueño

Mensaje recomendado:

```text
Vamos a hacer una revisión inicial y prudente.
No es un diagnóstico completo de la empresa.
Primero ubicamos mínimamente tu negocio, después revisamos el archivo o problema puntual.
Te vamos a decir qué se puede leer, qué está desordenado, qué señales aparecen, qué dato falta y cuál sería el siguiente paso razonable.
```

---

# 8. Salida mínima

Toda entrega de Primeros Auxilios debe responder:

```text
1. Qué recibimos.
2. Qué sabemos mínimamente del negocio.
3. Qué tipo de archivo o problema parece ser.
4. Qué se pudo revisar.
5. Qué señales o problemas visibles aparecen.
6. Qué no se puede afirmar todavía.
7. Qué evidencia falta.
8. Próximo paso sugerido.
```

---

# 9. Frases permitidas

```text
Con esta planilla puedo hacer una primera lectura.
Esto alcanza para ordenar la fuente, pero no para diagnosticar toda la empresa.
Veo una señal que conviene revisar con más evidencia.
Para confirmar esto necesito una segunda fuente.
No puedo afirmar margen real porque faltan costos.
No puedo confirmar stock real sin conteo o fuente observada.
```

---

# 10. Frases prohibidas

```text
Ya diagnosticamos tu empresa.
Tu empresa pierde plata por X.
Tu margen real es X si faltan costos.
Tu stock real es X sin conteo.
La conciliación está cerrada con una sola fuente.
La macro es segura sin revisión.
Esto reemplaza al contador.
Esto reemplaza un ERP.
```

---

# 11. Bloqueo sano

Primeros Auxilios debe bloquear o pedir aclaración si:

```text
no hay archivo ni descripción suficiente
no se puede ubicar mínimamente el tipo de negocio
la columna clave es ambigua
el archivo mezcla procesos incompatibles
la macro exige ejecución riesgosa
se pide rentabilidad sin costos
se pide conciliación sin segunda fuente
se pide stock real sin conteo
```

Mensaje recomendado:

```text
Con lo que tengo puedo ordenar la fuente, pero no confirmar el problema. Para avanzar necesito: [evidencia concreta].
```

---

# 12. Escalamiento

Primeros Auxilios escala a Nivel 2 cuando aparece una pregunta causal:

```text
¿Por qué no me queda plata?
¿Qué productos pierden margen?
¿Por qué no cierra la caja?
¿Qué stock me inmoviliza capital?
¿Qué canal me conviene?
```

Primeros Auxilios escala a Nivel 3 cuando el dueño plantea:

```text
Quiero ordenar toda la empresa.
Quiero profesionalizar.
Quiero que no dependa de mí.
Quiero revisar estructura completa.
```

Regla:

```text
Nivel 1 ordena y detecta señal.
Nivel 2 explica cuello de botella con evidencia suficiente.
Nivel 3 estudia la organización como sistema.
```

---

# 13. Criterio de aceptación

La experiencia de Primeros Auxilios es válida si cumple:

```text
pregunta madre explícita
primera capa formal de ficha obligatoria
subopciones claras
pedido de evidencia concreto
promesa limitada
salida mínima útil
bloqueo sano
escalamiento proporcional
```

---

# 14. Veredicto

```text
FIRST_AID_OWNER_EXPERIENCE_V1 = PRODUCT_READY_AS_SPEC
```

Pero:

```text
NO_RUNTIME_AUTHORIZED
NO_APPLICATION_WIRING_AUTHORIZED
NO_UI_AUTHORIZED
NO_STORAGE_AUTHORIZED
NO_OCF_WRITE_MODEL_AUTHORIZED
```

Siguiente paso posible:

```text
Auditar este documento contra PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md, EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md y ANAMNESIS_TAXONOMICA_MINIMA.md.
```
