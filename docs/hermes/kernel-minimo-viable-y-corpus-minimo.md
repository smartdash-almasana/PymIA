# Kernel mínimo confiable y corpus mínimo

## Estado

Documento de arquitectura operativa.

Este documento nace de la conclusión de que el bypass de Hermes no es solamente un problema de configuración conversacional.

El problema raíz es que el kernel determinístico de PymIA todavía no está ensamblado como autoridad operativa completa.

---

## Tesis

```text
Primero kernel.
Después Hermes.
```

Hermes no debe compensar huecos del kernel.

Si el kernel no puede recibir, validar, ejecutar y devolver un estado trazable, el sistema debe bloquear.

```text
BLOCKED antes que workaround.
```

---

## Definición

```text
Kernel mínimo confiable = circuito determinístico mínimo capaz de transformar una demanda operativa PyME en un estado trazable: BLOCKED, PARTIAL o PASS.
```

No es una app completa.
No es un bot.
No es una interfaz.
No es un agente LLM.
No es una factoría de ejecución.

Es el núcleo que decide si hay evidencia suficiente para investigar, ejecuta una skill bajo condiciones y devuelve resultado trazable.

---

## Circuito mínimo cerrado

```text
entrada conversacional
→ síntoma operativo
→ hipótesis investigable
→ evidencia mínima requerida
→ validación de suficiencia
→ skill determinística candidata
→ ejecución
→ resultado cuantificado
→ estado BLOCKED / PARTIAL / PASS
→ trazabilidad
```

Si una etapa no existe o no alcanza:

```text
BLOCKED
```

No se delega a Hermes.
No se improvisa.
No se ejecutan scripts laterales.

---

## Corpus mínimo del kernel

El corpus mínimo es el conjunto de documentos, contratos y reglas que permite operar el circuito sin interpretación libre.

Componentes mínimos:

```text
1. Contrato de entrada conversacional.
2. Catálogo mínimo de síntomas operativos.
3. Catálogo mínimo de patologías candidatas.
4. Mapa síntoma → hipótesis investigable.
5. Mapa hipótesis → evidencia requerida.
6. Mapa hipótesis → skill candidata.
7. Contrato de evidencia estructurada.
8. Reglas de suficiencia de evidencia.
9. Reglas de bloqueo.
10. Contrato de salida diagnóstica.
11. Contrato de trazabilidad.
12. Tests de regresión anti-bypass.
```

---

## Corrección: no inventar familias desde conversación

Se descarta cualquier recorte tipo “familia rentabilidad”, “familia margen” o similar si no existe físicamente como parte del corpus, contrato, catálogo o función ejecutable del sistema.

El kernel no debe funcionar porque una IA proponga una familia conceptual desde chat.

Debe funcionar por sus propias piezas existentes:

```text
- funciones reales;
- contratos reales;
- catálogos físicos;
- reglas documentadas;
- tests verificables;
- comportamiento ejecutable.
```

Regla:

```text
Si una categoría no existe en el corpus o en el código, no pertenece al sistema.
```

Por lo tanto, el fortalecimiento del kernel debe partir de inventariar lo que ya existe, no de empujar una ontología nueva desde conversación.

El orden correcto es:

```text
1. leer funciones existentes;
2. leer contratos existentes;
3. leer catálogos existentes;
4. identificar rutas ejecutables reales;
5. documentar solo lo comprobado;
6. recién después proponer gaps explícitos.
```

No se debe asumir que una “familia clínica-operativa” existe hasta encontrarla en archivos, contratos o tests.

---

## Estados permitidos

### BLOCKED

Se devuelve cuando falta evidencia mínima, el contrato no alcanza o la entrada no puede mapearse a una hipótesis investigable.

Ejemplos:

```text
- falta período;
- no hay ventas;
- no hay costo directo;
- la evidencia no es trazable;
- el archivo no fue estructurado;
- la hipótesis no tiene skill candidata;
- el output no puede reproducirse.
```

### PARTIAL

Se devuelve cuando hay indicios útiles pero no alcanza para cerrar hallazgo cuantificado.

Ejemplos:

```text
- hay ventas pero costos incompletos;
- hay margen bruto pero no gastos;
- hay datos de un período parcial;
- hay evidencia manual no respaldada por fuente.
```

### PASS

Se devuelve cuando hay hallazgo trazable, cuantificado y reproducible.

Condiciones mínimas:

```text
- evidencia suficiente;
- cálculo reproducible;
- diferencia cuantificada;
- fuente identificada;
- trazabilidad de entrada/salida;
- sin contradicción con reglas de bloqueo.
```

---

## Regla de autoridad

```text
Hermes conversa.
PymIA computa.
```

El kernel debe ser la autoridad sobre:

```text
- suficiencia de evidencia;
- bloqueo;
- selección de skill;
- ejecución;
- resultado;
- trazabilidad.
```

Hermes solo puede:

```text
- recibir la demanda;
- entregar preguntas del kernel;
- transmitir outputs verbatim;
- preservar trazabilidad.
```

---

## Primer backlog técnico sugerido

Orden mínimo:

```text
1. Formalizar contrato de entrada.
2. Formalizar familia rentabilidad/margen.
3. Formalizar evidencia mínima para esa familia.
4. Formalizar reglas BLOCKED/PARTIAL/PASS.
5. Crear tests de suficiencia y bloqueo.
6. Conectar una skill determinística mínima.
7. Validar output trazable.
8. Recién después conectar Hermes como gateway.
```

---

## Criterio de éxito

El kernel mínimo confiable existe cuando puede responder correctamente a estos tres casos:

### Caso 1: evidencia insuficiente

Entrada:

```text
vendo mucho pero no sé si gano
```

Sin ventas ni costos.

Resultado esperado:

```text
BLOCKED
```

Con pregunta mayéutica mínima por evidencia faltante.

### Caso 2: evidencia parcial

Entrada con ventas y costos directos, pero sin gastos básicos o período claro.

Resultado esperado:

```text
PARTIAL
```

Con indicio limitado y pedido de evidencia faltante.

### Caso 3: evidencia suficiente

Entrada con ventas, costos directos, período y fuente trazable.

Resultado esperado:

```text
PASS
```

Con margen bruto calculado, fuente, período y trazabilidad.

---

## Decisión

```text
No seguir ampliando Hermes hasta definir y probar el kernel mínimo confiable.
```

La prioridad deja de ser integración conversacional y pasa a ser ensamble determinístico del corpus mínimo.

---

## Criterio anti-alucinación del sistema

El sistema no debe considerarse funcional si depende de que ChatGPT, Hermes u otra IA complete huecos del kernel por conversación.

```text
Si el resultado existe porque la IA lo infirió libremente,
no es salida del sistema.
Es simulación conversacional.
```

El kernel mínimo confiable debe operar con contratos, corpus y reglas verificables.

La IA puede ayudar a conversar, reformular o transportar mensajes, pero no puede ser la pieza que:

```text
- decide qué evidencia alcanza;
- inventa una hipótesis no registrada;
- ejecuta un cálculo fuera del kernel;
- completa una skill inexistente;
- convierte una intuición en hallazgo;
- reemplaza una regla de bloqueo;
- sostiene el sistema cuando falta corpus.
```

### Regla de validez

```text
Un output solo pertenece a PymIA si puede trazarse al kernel:
entrada → contrato → corpus → regla → ejecución → estado → salida.
```

Si no puede trazarse, debe tratarse como:

```text
NO_VALID_SYSTEM_OUTPUT
```

No como diagnóstico, no como hallazgo y no como funcionamiento válido.

### Consecuencia

El objetivo no es que el chat parezca inteligente.

El objetivo es que el sistema pueda bloquear correctamente cuando no tiene corpus, evidencia o regla suficiente.

```text
Un BLOCKED honesto vale más que un diagnóstico fluido alucinado.
```
