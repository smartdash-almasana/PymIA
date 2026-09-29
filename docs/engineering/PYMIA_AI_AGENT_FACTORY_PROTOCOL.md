# PYMIA_AI_AGENT_FACTORY_PROTOCOL

## Estado

POLÍTICA OPERATIVA DE AGENTES IA

---

# Propósito

Este documento define cómo deben trabajar los agentes IA que participan en la fabricación de PymIA.

Su objetivo es reducir fricción, deriva y sobreproducción, manteniendo trazabilidad y comportamiento de unidad.

Los agentes IA no deben operar como colaboradores genéricos.

Deben operar como máquinas especializadas con contratos estrictos.

---

# Principio central

```text
Un agente no debe pensar todo.
Debe cumplir una función clara dentro de la fábrica.
```

La IA puede asistir, auditar, implementar, revisar, redactar o integrar.

No debe mezclar esas funciones sin autorización explícita.

---

# Relación con la plantilla de fabricación

Este protocolo complementa:

```text
docs/engineering/PYMIA_SOFTWARE_FABRICATION_TEMPLATE.md
```

La plantilla define cómo se fabrica un hito.

Este protocolo define cómo se distribuye el trabajo entre agentes IA.

---

# Roles mínimos

## 1. Auditor

Función:

- detectar huecos;
- identificar riesgos;
- verificar evidencia;
- señalar deriva;
- recomendar PASS / PARTIAL / BLOCKED.

No debe:

- implementar;
- refactorizar;
- crear archivos;
- redefinir arquitectura;
- inventar roadmap.

---

## 2. Implementador

Función:

- cerrar un hueco declarado;
- escribir el test/código mínimo necesario;
- respetar archivos permitidos;
- correr validaciones;
- devolver resultados exactos.

No debe:

- expandir scope;
- crear capabilities nuevas;
- tocar fronteras prohibidas;
- resolver fallos preexistentes salvo autorización;
- convertir una tarea test-only en refactor.

---

## 3. Revisor crítico

Función:

- buscar contradicciones;
- detectar claims falsos;
- verificar que el alcance no haya crecido;
- señalar regresiones conceptuales;
- aprobar o pedir cambios.

No debe:

- reescribir todo;
- agregar features;
- cambiar el objetivo del hito;
- mezclar opinión estética con corrección factual.

---

## 4. Redactor documental

Función:

- convertir evidencia en documento;
- producir checkpoints;
- resumir decisiones;
- preservar límites y riesgo residual.

No debe:

- inventar evidencia;
- afirmar tests no ejecutados;
- prometer capacidades no implementadas;
- reemplazar auditoría técnica.

---

## 5. Integrador

Función:

- crear branch;
- abrir PR;
- verificar diff;
- mergear cuando corresponde;
- mantener continuidad entre hitos.

No debe:

- modificar scope;
- reinterpretar el trabajo técnico;
- mezclar cambios ajenos;
- saltar checkpoints.

---

# Regla de contexto mínimo suficiente

Cada agente debe recibir solo el contexto necesario para su función.

Formato recomendado:

```text
HITO
HUECO
ARCHIVOS A LEER
ARCHIVOS QUE PUEDE TOCAR
PROHIBIDO
VALIDACIONES
SALIDA ESPERADA
```

No debe recibir una enciclopedia del proyecto si no la necesita.

Demasiado contexto aumenta la probabilidad de deriva.

---

# Regla de una función por agente

Antipatrón:

```text
Auditá, pensá arquitectura, implementá, documentá y proponé roadmap.
```

Patrón correcto:

```text
Agregá un test que demuestre continuidad tenant.
No toques código productivo.
Devolvé PASS / PARTIAL / BLOCKED.
```

---

# Salida normalizada

Todo agente debe responder, salvo excepción justificada, con:

```text
1. VEREDICTO
   PASS / PARTIAL / BLOCKED / APPROVE / REQUEST_CHANGES

2. ARCHIVOS MODIFICADOS O LEÍDOS

3. TESTS EJECUTADOS

4. RESULTADOS EXACTOS

5. JUSTIFICACIÓN DE SCOPE

6. RIESGO RESIDUAL

7. PRÓXIMO PASO RECOMENDADO
```

La normalización reduce fricción entre agentes.

---

# Prohibiciones explícitas

Toda tarea debe declarar fronteras.

Ejemplo base:

```text
No tocar CI.
No tocar registry.
No tocar dispatcher.
No tocar plugins.
No tocar Telegram/PDF/HTML/UI.
No agregar LLM.
No agregar red.
No crear capability nueva.
No resolver fallos preexistentes sin autorización.
```

Una IA sin fronteras tiende a expandir el problema.

---

# Fricción útil vs fricción inútil

## Fricción útil

- test;
- evidencia;
- scope;
- revisión;
- checkpoint;
- CI.

## Fricción inútil

- opiniones largas sin decisión;
- rediseños no pedidos;
- nuevas abstracciones sin test;
- documentación sin efecto operativo;
- refactors por estética;
- propuestas de features no solicitadas.

---

# Flujo recomendado de agentes

```text
Dirección / ChatGPT
→ define hito, hueco y contrato

Implementador / DeepSeek u otro
→ test/código mínimo

Auditor crítico / Nemotron u otro
→ aprueba, bloquea o pide cambios

Redactor / MiniMax u otro
→ checkpoint/documento

Integrador / ChatGPT
→ PR, merge, continuidad
```

Los nombres de agentes son reemplazables.

Los roles no.

---

# Contrato del implementador

El implementador debe cerrar el hueco declarado.

No debe intentar mejorar el sistema global.

No debe agregar arquitectura si el test puede cerrarse con comportamiento existente.

Si detecta que el hueco no puede cerrarse sin arquitectura nueva, debe devolver:

```text
BLOCKED
```

con causa exacta.

---

# Contrato del auditor

El auditor debe proteger el sistema contra:

- claims falsos;
- scope creep;
- optimismo no probado;
- mezcla de dominios;
- ruptura del comportamiento de unidad.

El auditor no debe bloquear por gusto.

Debe bloquear solo cuando exista una causa verificable.

---

# Contrato del redactor

El redactor solo puede escribir lo que está sustentado.

Un checkpoint debe distinguir:

```text
qué se probó
qué no se probó
qué queda parcial
qué riesgo residual persiste
```

No debe convertir una mejora parcial en cierre total.

---

# Contrato del integrador

El integrador debe preservar la linealidad del repo.

Antes de mergear debe verificar:

- PR chico;
- alcance declarado;
- branch correcto;
- archivos esperados;
- ausencia de cambios laterales;
- estado de draft/mergeability.

Si el PR no coincide con el contrato, no se mergea.

---

# Regla de comportamiento de unidad

Los agentes no fabrican partes aisladas.

Fabrican incrementos que deben fortalecer uno o más fundamentos:

```text
Acoplamiento significativo
Retroalimentación
Continuidad
Coherencia
```

La pregunta final para aceptar un trabajo no es solamente:

```text
¿El cambio funciona?
```

La pregunta final es:

```text
¿El cambio funciona como parte del uno?
```

---

# Regla contra el agente brillante

El agente no está para brillar.

Está para cerrar un hueco sin romper el uno.

Una respuesta extensa, creativa o ambiciosa que no cierre el hueco declarado es una falla operativa.

---

# Regla de bloqueo sano

Un agente debe bloquear cuando:

- la tarea viola scope;
- falta evidencia;
- el repo contradice la consigna;
- el test exige arquitectura no autorizada;
- el cambio produciría Frankenstein;
- no puede verificar lo que afirma.

Bloquear con causa exacta es una salida válida.

---

# Regla final

Los agentes IA son parte de la fábrica, no del producto final.

Su valor se mide por:

- reducción de incertidumbre;
- cierre de huecos;
- evidencia reproducible;
- preservación de límites;
- fortalecimiento del comportamiento de unidad.

No por cantidad de texto ni por cantidad de cambios.
