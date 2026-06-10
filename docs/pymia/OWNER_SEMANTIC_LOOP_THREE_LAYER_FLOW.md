# OWNER_SEMANTIC_LOOP_THREE_LAYER_FLOW

Fecha: 2026-06-10
Estado: DRAFT_FOR_REVIEW
Frente: lógica semántica Dueño / Hermes-IA / PymIA

## 1. Propósito

Este documento consolida el flujo semántico correcto entre tres capas del sistema:

```text
Dueño
→ Hermes / IA conversacional
→ PymIA computacional
```

La tesis central es:

```text
El dueño da sentido.
Hermes / IA traduce, repregunta y pide autorización.
PymIA valida, estructura y computa.
```

La lógica semántica no debe degenerar en un catálogo infinito de preguntas prearmadas. Los apoyos duros son:

```text
1. catálogo de patologías;
2. catálogo de fórmulas;
3. evidencia disponible y faltante;
4. repregunta semántica abierta;
5. confirmación explícita del dueño.
```

## 2. Fundamento documental

La arquitectura vigente establece:

```text
SmartPyme no decide. SmartPyme propone. El dueño confirma.
```

Sin autorización explícita y trazable del dueño, no hay ejecución.

La ontología de agentes define:

```text
Dueño          = agente creacional
Hermes         = organismo operativo / conversacional
PymIA          = inteligencia computacional de Hermes
PyME / negocio = universo observado conocido/desconocido
```

El dueño no es usuario testimonial. Es función activa del sistema: declara síntomas, acepta o rechaza pedidos de evidencia, aprueba hallazgos, autoriza intervenciones, corrige rumbo y valida si el resultado sirve.

## 3. Las tres capas

### 3.1 Dueño — fuente de sentido y autorización

El dueño expresa el mundo PyME en lenguaje propio:

```text
“vendo más pero no me queda plata”
“la tela subió”
“los clientes pagan tarde”
“el stock lo llevo a ojo”
“ese cliente me mata”
```

Eso no entra como dato limpio. Entra como narrativa operativa, con dolor, intuición, contradicción, memoria tácita, hipótesis propia y datos parciales.

El dueño cumple funciones soberanas:

```text
- declara el síntoma;
- aporta contexto;
- aporta evidencia;
- confirma o corrige interpretaciones;
- acepta o rechaza pedidos de evidencia;
- autoriza el eje de análisis;
- decide si se avanza o no.
```

### 3.2 Hermes / IA conversacional — traductor semántico-operativo

Hermes / IA no diagnostica ni calcula. Su función es escuchar, traducir, repreguntar, aproximar y pedir autorización.

Ante una frase como:

```text
“Los precios los fui cambiando porque subió la tela.”
```

Hermes / IA puede proponer una interpretación tentativa:

```text
Estoy entendiendo que el eje a revisar es si la suba de la tela obligó a cambiar precios y eso pudo afectar el margen. ¿Confirmás que vamos por ese lado?
```

Esa interpretación no es verdad operativa confirmada hasta que el dueño la autoriza.

### 3.3 PymIA — validación, estructura y computabilidad

PymIA no conversa libremente con el dueño. PymIA recibe artefactos estructurados, valida contratos, clasifica evidencia, consulta catálogos, computa fórmulas y produce hallazgos sólo cuando hay evidencia suficiente.

PymIA debe preservar la diferencia entre:

```text
verdad declarada por el dueño;
interpretación tentativa de Hermes / IA;
evidencia estructural validada;
hallazgo computado.
```

## 4. Flujo canónico

```text
1. Dueño expresa narrativa operativa.
2. Hermes / IA escucha y traduce tentativamente.
3. Hermes / IA contrasta contra patologías y fórmulas candidatas.
4. Hermes / IA formula repregunta de aproximación.
5. Dueño confirma, rechaza o corrige.
6. PymIA registra el gate semántico.
7. PymIA determina evidencia faltante y computabilidad.
8. Hermes / IA pide evidencia concreta y accionable.
9. Dueño aporta datos, documentos o nueva aclaración.
10. PymIA computa sólo si la evidencia alcanza.
11. Hermes traduce resultado o límite.
12. Dueño decide siguiente acción.
```

Versión sintética:

```text
Dueño expresa.
Hermes interpreta y repregunta.
Dueño confirma o corrige.
PymIA estructura y computa.
Hermes traduce el próximo paso.
Dueño autoriza avanzar.
```

## 5. Catálogo de patologías y catálogo de fórmulas

El sistema no debe intentar anticipar todas las preguntas posibles.

Debe usar dos apoyos duros:

```text
SymptomPathologyCatalog
FormulaCatalog / Knowledge Tank
```

La conversación se orienta por patologías candidatas y fórmulas posibles, no por un árbol cerrado de preguntas.

Ejemplo:

```text
Narrativa: “vendo más pero no me queda plata”

Patologías candidatas:
- deterioro de margen;
- descalce de caja;
- cobranzas lentas;
- stock inmovilizado;
- retiros o gastos no controlados.

Fórmulas candidatas:
- margen bruto;
- margen por producto;
- días de cobranza;
- rotación de stock;
- flujo operativo.
```

Hermes / IA repregunta para reducir incertidumbre:

```text
Cuando decís que vendés más pero no te queda plata, ¿lo ves más por aumento de costos, por demora en cobrar, por stock parado o por gastos que crecieron?
```

Si la incertidumbre sigue alta, Hermes / IA propone una interpretación y pide autorización.

## 6. Gate soberano de confirmación

Toda interpretación semántica abierta debe pasar por un gate de confirmación del dueño.

Contrato implementado:

```text
OwnerSemanticConfirmationGate
```

Estados:

```text
PENDING_OWNER_CONFIRMATION
CONFIRMED_BY_OWNER
REJECTED_BY_OWNER
CORRECTED_BY_OWNER
```

Regla:

```text
Una interpretación tentativa no puede tratarse como confirmada sin acto explícito del dueño.
```

Ejemplo:

```text
Hermes / IA:
Estoy entendiendo que el problema principal es variación de precios por suba de tela. ¿Confirmás que este es el eje correcto?

Dueño:
Sí, es eso.

Gate:
CONFIRMED_BY_OWNER
```

Si el dueño dice:

```text
No, el problema principal es que me pagan tarde.
```

Gate:

```text
CORRECTED_BY_OWNER
```

con interpretación corregida trazable.

## 7. Pedido semántico de evidencia

Una vez confirmado o corregido el eje, el sistema puede generar un pedido accionable de evidencia.

Contrato implementado:

```text
OwnerSemanticEvidenceRequest
```

Regla:

```text
La narrativa del dueño puede refinar el pedido de evidencia.
No destraba evidencia estructural.
No produce findings.
```

Ejemplo:

```text
Eje confirmado:
precios cambiantes por suba de tela

Faltante estructural:
own_price

Pedido owner-facing:
Para calcular margen necesito precios de venta por producto/SKU de la última semana y, si cambiaron durante el período, desde qué fecha rigió cada precio.
```

## 8. Estados lógicos esperados

El flujo semántico debería permitir representar estados como:

```text
NARRATIVE_RECEIVED
SEMANTIC_INTERPRETATION_PROPOSED
PENDING_OWNER_CONFIRMATION
CONFIRMED_BY_OWNER
REJECTED_BY_OWNER
CORRECTED_BY_OWNER
EVIDENCE_REQUESTED
STRUCTURAL_INPUT_PENDING
BLOCKED_ACTIONABLE
READY_FOR_COMPUTATION
DIAGNOSTIC_RESULT_AVAILABLE
OWNER_DECISION_PENDING
```

El estado crítico de producto es:

```text
BLOCKED_ACTIONABLE
```

Significa:

```text
No puedo diagnosticar todavía, pero sé exactamente qué pedirte para avanzar.
```

## 9. Ejemplo completo

### Turno 1 — Dueño

```text
Estoy vendiendo más, pero no me queda plata. Encima la tela subió y fui cambiando precios.
```

### Turno 2 — Hermes / IA

```text
Estoy entendiendo dos posibles ejes:

1. puede haber caída de margen porque la tela subió y los precios no acompañaron igual;
2. puede haber descalce de caja aunque vendas más.

¿Confirmás que querés empezar por revisar margen y precios?
```

### Turno 3 — Dueño

```text
Sí, primero margen y precios.
```

### Gate

```text
OwnerSemanticConfirmationGate
status = CONFIRMED_BY_OWNER
target_type = PATHOLOGY_AXIS
proposed_interpretation = revisar margen/precios por suba de tela
```

### PymIA

```text
Patología candidata: deterioro de margen
Fórmulas candidatas: margen bruto, margen por producto, precio efectivo, costo unitario
Faltantes: precio por producto, costo por producto, unidades vendidas, período
```

### Hermes / IA

```text
Para revisar margen necesito una base mínima:

- producto/SKU;
- precio de venta de la última semana;
- costo aproximado por producto;
- unidades vendidas;
- período analizado.

Si los precios cambiaron, agregá desde qué semana rigió cada precio.
```

### Estado

```text
BLOCKED_ACTIONABLE
```

No hay diagnóstico todavía.

## 10. Antipatrones prohibidos

```text
- Tomar la narrativa del dueño como evidencia dura.
- Tomar una interpretación de IA como confirmada sin OK del dueño.
- Convertir el builder semántico en catálogo infinito de preguntas fijas.
- Usar Hermes / IA para diagnosticar o calcular.
- Hacer que PymIA converse libremente con el dueño.
- Producir findings antes de evidencia suficiente.
- Ocultar al dueño que el caso sigue bloqueado.
```

## 11. Fórmula final

```text
Dueño da sentido.
Hermes / IA traduce sentido.
Dueño confirma sentido.
PymIA computa sobre evidencia.
Hermes traduce límites y próximos pasos.
Dueño decide acción.
```

Este flujo preserva inteligencia semántica abierta sin perder soberanía computacional ni trazabilidad.
