# OWNER_QUESTIONS_HUMANIZATION_GATE — TaskSpec

Fecha: 2026-06-10
Estado: READY_FOR_IMPLEMENTATION
Origen: `SIMULATED_PILOT_FRICTION_RECONCILIATION.md`
Fricción: SPFR-003 — Owner-facing questions mezclan lenguaje legible con claves técnicas crudas

## 1. Objetivo

Evitar que el dueño PyME vea claves técnicas crudas en preguntas visibles.

El sistema puede conservar identificadores técnicos internamente, pero todo texto mostrado al dueño debe estar escrito en castellano operativo, simple y natural.

## 2. Problema observado

Durante `ASSISTED_SIMULATED_PILOT_001`, el paquete owner-facing mezcló preguntas legibles con claves técnicas como:

```text
amortization
dso
own_price
```

Esto no es aceptable para un dueño PyME.

## 3. Principio rector

Las preguntas para el dueño deben sonar como una persona de operaciones que entiende una PyME, no como un esquema técnico.

Ejemplos de transformación:

```text
amortization
→ ¿Tenés algún gasto grande o compra de maquinaria/equipos que estés pagando en cuotas o amortizando?
```

```text
dso
→ ¿Más o menos cuántos días tardan tus clientes en pagarte después de venderles?
```

```text
own_price
→ ¿Cuál es el precio al que vendés ese producto hoy?
```

## 4. Alcance permitido

Auditar y modificar sólo el punto donde se genera o serializa el texto visible del `owner_questions_bundle`.

Permitido:

- agregar un mapper de claves técnicas a preguntas naturales;
- preservar claves técnicas como metadata interna;
- agregar tests focales de legibilidad;
- actualizar checkpoint documental.

No permitido:

- tocar Telegram;
- tocar Hermes;
- tocar ERP;
- tocar PDF productivo;
- crear reportes nuevos;
- crear fórmulas nuevas;
- tocar runtime externo;
- reescribir graph;
- reescribir bridge completo;
- tocar DiagnosticCore salvo que la generación visible viva ahí y no haya alternativa menor.

## 5. Contrato owner-facing

Toda pregunta visible al dueño debe cumplir:

- castellano natural;
- sin snake_case;
- sin nombres internos de variables;
- sin ids técnicos crudos;
- sin jerga financiera innecesaria;
- una pregunta por necesidad;
- decir qué dato falta o qué sentido se necesita;
- si el dueño puede responder con aproximación, indicarlo.

## 6. Reglas de preservación técnica

El sistema puede mantener internamente:

```text
variable_id
formula_id
missing_input
source_ref
technical_key
```

Pero esos campos no deben aparecer como texto visible principal para el dueño.

## 7. Tests mínimos esperados

Crear o extender test focal que verifique que el texto visible del `owner_questions_bundle` no contiene:

```text
amortization
dso
own_price
snake_case
formula_id
variable_id
missing_input
```

Y que sí contiene preguntas naturales equivalentes, por ejemplo:

```text
cuántos días tardan tus clientes en pagarte
precio al que vendés
pagando en cuotas o amortizando
```

## 8. Criterio PASS

PASS si:

- el bundle visible para dueño no expone claves técnicas crudas;
- las claves técnicas siguen disponibles internamente para trazabilidad;
- no se altera owner-answer reentry;
- no se altera DiagnosticCore;
- no se altera graph salvo necesidad mínima justificada;
- tests focales pasan.

## 9. Criterio FAIL

FAIL si:

- se eliminan claves técnicas internas necesarias;
- se oculta trazabilidad;
- se generan preguntas vagas;
- se toca runtime externo;
- se mezclan múltiples frentes;
- se promete diagnóstico cuando sólo falta evidencia.

## 10. Implementación sugerida

Auditar primero dónde nace el texto de `owner_questions_bundle`.

Luego aplicar el menor cambio posible:

```text
technical_key → owner_visible_question
```

No convertir esto en un nuevo sistema de reportes.

## 11. Estado

```text
READY_FOR_IMPLEMENTATION
```

Debe ser ejecutado con patch mínimo y evidencia de tests.
