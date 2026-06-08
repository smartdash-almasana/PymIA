# PymIA Motherboard — 01 Invariants

Estado: fundacional
Propósito: declarar leyes operativas no negociables

---

## 1. Qué es un invariante

Un invariante es una regla que debe seguir siendo verdadera aunque cambien módulos, canales, modelos, proveedores, formatos o interfaces.

No describe una feature.

Describe una condición de identidad.

Si un cambio rompe un invariante, el cambio no es una mejora local: es una alteración genética de PymIA.

---

## 2. Invariante de evidencia

PymIA no debe convertir una afirmación en conclusión fuerte sin evidencia suficiente.

Regla:

```text
sin evidencia suficiente → no CONFIRMED
```

Conductas válidas:

```text
calcular
bloquear
preguntar
marcar faltante
producir hipótesis candidata
```

Conducta inválida:

```text
presentar como confirmado lo que sólo está sugerido o incompleto
```

---

## 3. Invariante de faltantes explícitos

PymIA debe declarar lo que falta.

No debe rellenar silenciosamente variables ausentes.

Regla:

```text
missing input → missing input explícito
```

Ejemplo:

```text
faltan taxes → MISSING_INPUTS: taxes
```

No se permite:

```text
asumir taxes = 0
usar promedio oculto
inventar proxy sin declararlo
```

---

## 4. Invariante de trazabilidad

Todo cálculo operativo debe poder rastrearse a sus variables y fuentes.

Regla:

```text
resultado → formula_id → variables → source_refs
```

Si un resultado no puede explicar su origen, no debe escalar a diagnóstico fuerte.

---

## 5. Invariante de source_refs por fórmula

Las referencias de evidencia deben quedar acotadas a lo que usa cada fórmula.

Regla:

```text
formula_result.source_refs = refs de inputs requeridos por esa fórmula
```

No se permite arrastrar un pool común de evidencia que ensucie la trazabilidad.

---

## 6. Invariante de cálculo determinístico

Una misma entrada debe producir la misma salida.

Regla:

```text
same input → same formula result
```

El motor de cálculo no debe depender de estilo, temperatura, contexto conversacional ni intuición generativa.

---

## 7. Invariante de separación cálculo/diagnóstico

Un resultado calculado no equivale automáticamente a una patología confirmada.

Regla:

```text
formula OK → diagnostic CANDIDATE, no CONFIRMED
```

La confirmación requiere gates adicionales de evidencia, contexto y criterio clínico-operativo.

---

## 8. Invariante de bloqueo válido

Bloquear no es fallar.

Cuando faltan datos, hay divisor cero, input inválido o evidencia insuficiente, el bloqueo es comportamiento correcto.

Regla:

```text
no calculable honestamente → BLOCKED
```

El sistema debe preferir bloqueo explícito antes que cálculo falso.

---

## 9. Invariante de caso y tenant

La información de una PyME/caso no debe mezclarse con otra.

Regla:

```text
tenant_id + case_id delimitan contexto operacional
```

Memoria, evidencia, resultados y estado deben respetar esa frontera.

---

## 10. Invariante de estado

PymIA debe operar sobre estado de caso, no sobre respuestas sueltas.

Regla:

```text
cada interacción relevante actualiza o consulta estado
```

El estado debe poder contener:

```text
evidencia recibida
variables disponibles
variables faltantes
fórmulas aplicables
resultados
hipótesis candidatas
bloqueos
próxima pregunta operativa
```

---

## 11. Invariante de puertos

Los módulos se conectan por puertos, no por conocimiento implícito.

Regla:

```text
module output must satisfy next module input contract
```

Si una salida no cumple contrato, debe transformarse explícitamente o bloquear.

---

## 12. Invariante de gates

Todo avance crítico debe pasar por una compuerta explícita.

Ejemplos:

```text
EVIDENCE_SUFFICIENCY_GATE
FORMULA_INPUT_GATE
DIAGNOSTIC_EVIDENCE_GATE
FINDING_GROUNDING_GATE
DELIVERY_GATE
```

Regla:

```text
sin gate aprobado → no avanzar a conclusión superior
```

---

## 13. Invariante de modularidad obediente

Un módulo puede cambiar si preserva sus contratos.

Regla:

```text
replaceable implementation, stable contract
```

Un parser, canal o renderer puede ser reemplazado.

La obligación de no inventar evidencia no puede ser reemplazada.

---

## 14. Invariante de tests de obediencia

Cada invariante debe tener, progresivamente, tests que lo custodien.

Regla:

```text
invariant without test = doctrine vulnerable
```

No todos los tests deben existir desde el primer día, pero cada avance arquitectónico debe acercar doctrina y ejecución.

---

## 15. Invariante de no deriva

PymIA debe evitar crecer por acumulación de piezas desconectadas.

Regla:

```text
no new module without declared port/gate or explicit temporary exception
```

La fragmentación es una forma de deuda genética.

---

## 16. Invariante de lenguaje operativo

PymIA debe hablar en lenguaje útil para el dueño PyME sin traicionar la precisión técnica.

Regla:

```text
claridad operativa + trazabilidad técnica
```

No se permite simplificar ocultando incertidumbre relevante.

---

## 17. Invariante de auditoría

Cada cierre relevante debe poder auditarse.

Regla:

```text
files changed + diff summary + tests + commit + status
```

La auditoría no es burocracia. Es continuidad operacional.

---

## 18. Invariante de escalabilidad genética

PymIA debe poder crecer sin perder forma.

Regla:

```text
new capability must reinforce or preserve motherboard invariants
```

Si una nueva capacidad exige romper invariantes, debe tratarse como rediseño mayor, no como feature.

---

## 19. Tabla inicial de obediencia

| Invariante | Código actual relacionado | Estado |
|---|---|---|
| Evidencia antes de diagnóstico | `DiagnosticCoreV1`, evidence binding | parcial |
| Faltantes explícitos | `FormulaEngineService` | activo |
| Source refs | `DiagnosticCoreV1` | activo |
| Cálculo determinístico | `FormulaEngineService` | activo |
| CANDIDATE no CONFIRMED | `DiagnosticCoreV1` | activo |
| Puertos/gates | docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md | documental |
| Tests de obediencia | tests focales M34/M35 | parcial |
| Estado de caso | orchestration/domain docs | pendiente de integración |

---

## 20. Próximo endurecimiento

Estos invariantes deben convertirse progresivamente en:

```text
schemas
validators
contract tests
gates ejecutables
runtime checks
```

La etapa natural para eso es:

```text
M36 — Port Hardening / Contract Enforcement
```

Pero M36 debe apoyarse sobre M35, no reemplazarlo.
