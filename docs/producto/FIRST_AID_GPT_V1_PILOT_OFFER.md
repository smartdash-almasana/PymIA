# FIRST_AID_GPT_V1_PILOT_OFFER

## Estado

```text
Tipo: PRODUCT_OFFER_SPEC
Estado: CANDIDATE_READY_FOR_PILOT
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Convertir el cierre técnico de `Primeros Auxilios GPT V1` en una oferta simple, vendible y piloteable para PyMEs, sin abrir runtime nuevo ni prometer diagnóstico.

Este documento se apoya en:

```text
docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md
docs/producto/FIRST_AID_OWNER_EXPERIENCE_V1.md
docs/producto/FIRST_AID_PYME_PAIN_AUDIT_V1.md
docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
```

---

# 1. Veredicto de producto

```text
PRIMEROS_AUXILIOS_GPT_V1 = PILOTABLE_SERVICE_OFFER
```

Pero:

```text
NO_DIAGNOSTIC_PRODUCT
NO_FULL_CONSULTING
NO_ERP
NO_BI_GENERIC
NO_AUTOMATION_IMPLEMENTATION
NO_ACCOUNTING_AUDIT
```

La oferta correcta es:

```text
Revisión inicial, prudente y accionable de una fuente o problema puntual de la PyME.
```

---

# 2. Nombre comercial de trabajo

```text
Primeros Auxilios GPT para PyMEs
```

Subtítulo:

```text
Ordenamos tu archivo o problema puntual y te decimos qué se puede saber, qué no se puede afirmar todavía y cuál es el próximo paso razonable.
```

---

# 3. Cliente objetivo inicial

Dueño o responsable administrativo de una PyME que dice algo como:

```text
Tengo este Excel desordenado.
No me cierran unos números.
Quiero mirar precios, costos o stock.
Tengo una planilla que nadie entiende.
Quiero sacar algo claro de estos datos.
No sé qué dato falta para poder revisar esto bien.
```

No está buscando todavía:

```text
diagnóstico integral
implementación de ERP
auditoría contable
consultoría estratégica completa
automatización productiva
```

---

# 4. Promesa central

```text
En una primera revisión te devolvemos una lectura clara y limitada:
qué recibimos, qué se pudo ordenar, qué señales aparecen, qué dato falta y qué conviene hacer después.
```

La promesa no es “resolver la empresa”.

La promesa es:

```text
bajar incertidumbre inmediata sin inventar diagnóstico.
```

---

# 5. Entrada del servicio

El servicio empieza con la pregunta madre:

```text
¿Qué necesitás resolver hoy?
```

Para este piloto sólo se acepta la opción:

```text
Primeros Auxilios
Tengo algo puntual para ordenar o revisar ahora.
```

Luego se captura una ficha mínima:

```text
nombre visible del negocio
a qué se dedica
tipo de operación
canales de venta
si maneja stock
qué quiere revisar ahora
frase textual del dueño
evidencia disponible
```

---

# 6. Casos aceptados en el piloto

```text
A. Excel o planilla desordenada
B. Fórmulas, totales o cálculos que no cierran
C. Lista de precios o costos
D. Stock o inventario
E. Caja, banco o conciliación simple
F. Ventas o datos comerciales
G. Tarea manual repetitiva para triage
H. Otro archivo o problema puntual, si cabe en revisión inicial
```

---

# 7. Casos rechazados o escalados

Rechazar o escalar si el dueño pide:

```text
diagnóstico completo de la empresa
rentabilidad real sin costos suficientes
conciliación bancaria certificada
stock físico real sin conteo
auditoría contable o fiscal
detección de fraude
ejecución automática de macros
reparación de sistema crítico
automatización productiva completa
```

Mensaje de bloqueo:

```text
Con esto puedo hacer una primera lectura y ordenar la fuente, pero no confirmar ese punto. Para avanzar haría falta: [evidencia concreta].
```

---

# 8. Entregable mínimo

Toda entrega piloto debe contener:

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

Formato recomendado:

```text
reporte breve owner-safe
lista de advertencias
preguntas siguientes
opcional: archivo o tabla ordenada si corresponde
```

---

# 9. Frases permitidas

```text
Con esta evidencia puedo hacer una primera lectura.
Esto alcanza para ordenar la fuente, pero no para diagnosticar toda la empresa.
Veo una señal que conviene revisar con más evidencia.
Para confirmar esto necesito otra fuente.
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
Esto reemplaza al contador.
Esto reemplaza un ERP.
```

---

# 11. Precio piloto sugerido

Este documento no fija pricing definitivo. Para piloto asistido se sugieren tres formatos de prueba:

```text
Piloto 0 — prueba interna: sin precio, caso controlado.
Piloto 1 — revisión puntual: precio bajo, una fuente, una devolución.
Piloto 2 — revisión asistida: una fuente + breve llamada o intercambio de aclaración.
```

Regla:

```text
Cobrar por claridad inicial, no por diagnóstico completo.
```

---

# 12. Criterio de éxito del piloto

Un piloto es exitoso si el dueño puede decir:

```text
Ahora entiendo mejor qué tengo.
Ahora sé qué dato falta.
Ahora sé qué no se puede afirmar todavía.
Ahora sé cuál es el próximo paso.
```

Métricas cualitativas:

```text
claridad percibida
confianza en los límites
utilidad del próximo paso
cantidad de aclaraciones necesarias
si el caso escala naturalmente a Nivel 2
```

---

# 13. Criterio de no-éxito

El piloto falla si:

```text
parece un lector genérico de Excel
promete más de lo que evidencia permite
usa lenguaje técnico incomprensible
no pide evidencia faltante
no declara límites
se convierte en consultoría abstracta
```

---

# 14. Regla de escalamiento comercial sano

No vender Nivel 2 como upsell forzado.

Escalar sólo si aparece una pregunta causal o una señal material:

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

---

# 15. Definición de listo para pilotos reales

```text
CHECKPOINT CREADO: YES
DOCUMENTATION_INDEX UPDATED: YES
RUNTIME NUEVO: NO
DIAGNÓSTICO: NO
PROMESA OWNER-SAFE: YES
ENTREGABLE MÍNIMO DEFINIDO: YES
LÍMITES EXPLÍCITOS: YES
ESCALAMIENTO DEFINIDO: YES
```

---

# 16. Próximo paso autorizado

Siguiente frente documental o comercial, no runtime:

```text
FIRST_AID_GPT_V1_PILOT_SCRIPT.md
```

Debe definir:

```text
mensaje inicial
preguntas mínimas
pedido de evidencia
plantilla de devolución
checklist de bloqueo
criterio de escalamiento
```

No autoriza código, pipeline, OCF productivo ni canales externos.
