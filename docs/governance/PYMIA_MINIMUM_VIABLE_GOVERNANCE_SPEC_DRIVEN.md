# PymIA — Minimum Viable Governance para Spec-Driven Development endurecido

**Estado:** PROPUESTA METODOLÓGICA / NON_NORMATIVE  
**Objetivo:** reducir deriva de agentes IA, improvisación arquitectónica, ampliación silenciosa de alcance y ciclos de auditoría repetitivos.  
**Base:** metodología PymIA Governed Agentic Development ya documentada en Notion, condensada aquí como propuesta operativa mínima.

---

## 1. Problema que resuelve

El problema actual no es la falta de tests ni de documentación. El problema es que, durante una implementación, el agente puede:

- reinterpretar el problema;
- ampliar alcance;
- rediseñar sobre la marcha;
- crear caminos paralelos;
- cambiar criterios de aceptación;
- introducir deuda técnica fuera del objetivo;
- convertir hallazgos laterales en nuevas tareas sin decisión del owner.

El patrón que se quiere evitar es:

```text
problema
→ razonamiento del agente
→ prompt
→ implementación
→ aparece otro hallazgo
→ nuevo prompt
→ nueva auditoría
→ nueva corrección
→ más deriva
```

El patrón deseado es:

```text
SPEC congelada
→ contratos ejecutables
→ implementación acotada
→ gates automáticos
→ verificación independiente
→ evidencia
→ absorción
→ STOP
```

---

## 2. Principio rector

> **La especificación aprobada por el owner no se reinterpreta durante la implementación.**

Si aparece un hallazgo nuevo:

```text
¿está dentro de CHANGE_SPEC?
    ├── SÍ → resolver dentro del contrato
    └── NO → OUT_OF_SCOPE / BLOCKED / STOP
```

No existe el “ya que estamos”.

---

## 3. Flujo obligatorio

```text
OWNER DECISION
      ↓
NOP-1 CHECK
      ↓
CHANGE_SPEC
      ↓
ACCEPTANCE CONTRACT
      ↓
ARCHITECTURE FITNESS
      ↓
IMPLEMENTATION PLAN
      ↓
IMPLEMENTACIÓN
      ↓
GATES AUTOMÁTICOS
      ↓
VERIFICADOR INDEPENDIENTE
      ↓
EVIDENCE PACK
      ↓
ABSORCIÓN EN CURRENT STATE
      ↓
STOP
```

---

# 4. Artefactos mínimos obligatorios

## 4.1 CHANGE_SPEC

Es la única definición del cambio que se está construyendo.

Formato recomendado:

```yaml
change_id:
product_problem:
current_behavior:
target_behavior:

authoritative_inputs:
  - NOP-1
  - fragmento NOP-2 relevante
  - contratos públicos afectados

invariants:

in_scope:
out_of_scope:

architecture_before:
architecture_after:

public_contracts:

acceptance_scenarios:

golden_cases:

forbidden_behaviors:

allowed_files:
expected_blast_radius:

stop_conditions:
```

### Reglas

- Debe aprobarse antes de modificar código.
- Una vez aprobada, el implementador no puede ampliarla.
- Un hallazgo fuera del perímetro no autoriza una nueva implementación.
- Si la solución requiere salir del perímetro: `BLOCKED + STOP`.

---

## 4.2 ACCEPTANCE CONTRACT

Antes de implementar deben existir escenarios que demuestren que la pieza funciona.

No deben limitarse a unit tests técnicos. Deben cubrir comportamiento de producto.

Ejemplo para una capability semántica:

```text
GOLD-01 Lubricentro
→ comprende las 3 hojas como conjunto
→ reconoce economía de mano de obra
→ stock_actual / stock_minimo coherentes
→ no hardcode por header

GOLD-02 Cafetería
→ ventas/costos/productos/canales contextualizados

GOLD-03 Caso desconocido
→ no inventa semántica
→ pide owner cuando corresponde

GOLD-04 Output LLM inválido
→ validator bloquea
→ no contamina mapping

GOLD-05 Tenant ya aprendido
→ reutiliza sólo semántica confirmada del tenant
```

Estos casos son oráculos de aceptación, no documentación narrativa.

---

## 4.3 ARCHITECTURE FITNESS

El repositorio debe rechazar automáticamente violaciones estructurales.

Ejemplos:

```text
SECOND_PRODUCT_ROOT = 0
SECOND_SEMANTIC_ENGINE = 0
SECOND_MATH_ENGINE = 0
SECOND_PARSER = 0

WEB_ANALYTICAL_AUTHORITY = 0
LLM_AUTO_CONFIRM = 0
LLM_MATH_AUTHORITY = 0

CROSS_TENANT_PATH = 0
UNAUTHORIZED_FILES_CHANGED = 0

HARDCODE_VERTICAL_IN_CORE = 0
```

Si cualquiera falla:

```text
BLOCKED
STOP
```

Aunque todos los tests funcionales estén verdes.

---

## 4.4 IMPLEMENTATION PLAN

El implementador debe recibir únicamente el contexto necesario.

### AUTHORIZED_CONTEXT_BUNDLE

```text
NOP-1
+
fragmento relevante de NOP-2
+
CHANGE_SPEC
+
contratos públicos afectados
+
acceptance tests
+
archivos autorizados
```

No se le entrega por defecto:

- histórico masivo;
- ADR irrelevantes;
- auditorías antiguas;
- proposals superseded;
- chats previos;
- documentación lateral.

El objetivo es reducir contaminación de contexto.

---

## 4.5 EVIDENCE PACK

El implementador no certifica su propio trabajo narrativamente.

Formato mínimo:

```text
CHANGE_ID:
SPEC_VERSION:

FILES_ALLOWED:
FILES_CHANGED:
UNAUTHORIZED_FILES:

CONTRACT_TESTS:
GOLDEN_CASES:
FITNESS_FUNCTIONS:
TYPECHECK:

SECOND_ROOTS:
SECOND_SEMANTIC_ENGINES:
SECOND_MATH_ENGINES:
FORBIDDEN_IMPORTS:
HARDCODES:

SPEC_DEVIATIONS:

VERDICT:
```

Luego un verificador independiente, read-only, revisa el resultado.

---

# 5. Separación de poderes

## Implementer

Puede:

- modificar sólo el perímetro autorizado;
- cumplir la CHANGE_SPEC;
- producir evidencia.

No puede:

- ampliar alcance;
- mover oráculos;
- alterar tests para hacer pasar una implementación incorrecta;
- redefinir arquitectura;
- certificar convergencia por sí mismo.

## Verifier

Debe:

- operar read-only;
- verificar scope;
- verificar contratos;
- verificar fitness;
- verificar golden cases;
- identificar divergencias.

No implementa correcciones.

---

# 6. Cuatro reglas mínimas

El Minimum Viable Governance puede resumirse en cuatro reglas:

```text
1. NO CODE WITHOUT APPROVED CHANGE_SPEC

2. NO CHANGE_SPEC WITHOUT NOP-1 CHECK

3. NO PASS WITHOUT
   EXECUTABLE ACCEPTANCE
   + ARCHITECTURE FITNESS
   + GOLDEN BUSINESS CASES

4. NO NEXT TASK UNTIL
   ABSORPTION
   + STOP
```

---

# 7. Regla especial para agentes IA

> **ChatGPT, Gemini, OpenCode o cualquier otro agente no pueden generar el siguiente cambio mientras el anterior no haya cerrado contra la SPEC original.**

Esto implica:

```text
hallazgo lateral
→ registrar
→ clasificar
→ OUT_OF_SCOPE si corresponde
→ STOP
```

Nunca:

```text
hallazgo lateral
→ rediseño improvisado
→ nueva implementación
```

---

# 8. Protección contra cuatro tipos de deriva

## 8.1 Deriva de intención

El código deja de corresponder al cambio autorizado.

Control:

- CHANGE_SPEC
- allowed_files
- expected_blast_radius

## 8.2 Deriva arquitectónica

Aparecen caminos o autoridades paralelas.

Control:

- architecture fitness
- forbidden imports
- second-root / second-engine checks

## 8.3 Deriva semántica

El sistema mantiene estructura correcta pero cambia significado empresarial.

Control:

- Golden Business Corpus
- owner-confirmed mappings
- semantic contract tests

## 8.4 Deriva sistémica acumulativa

Cada cambio parece correcto, pero el sistema deja de contar una sola historia.

Control:

- absorción en CURRENT STATE
- system coherence review por hitos
- NOP-1/NOP-2 como autoridad

---

# 9. Aplicación inmediata a la capa semántica

Antes de tocar nuevamente el código de semantic mapping, la pieza debe tener una CHANGE_SPEC única que defina:

```text
qué parte de C2 existente se reutiliza
qué parte se extrae
qué authority queda
qué entrypoint único habrá
qué consume VTV
qué consume Service 1
qué mapper paralelo se elimina
qué output estructurado produce
qué validator lo gobierna
qué hace el owner
qué persiste por tenant
qué Golden Business Cases debe superar
```

Una vez congelado esto:

> **no se vuelve a diseñar durante la implementación.**

---

# 10. Resultado esperado

El objetivo no es generar más documentación.

El objetivo es que la documentación pase a ser una restricción operativa real.

La cadena correcta debe quedar así:

```text
SPEC
→ código
→ contratos
→ evidencia
→ convergencia
```

y no:

```text
chat
→ idea
→ código
→ auditoría
→ nueva idea
→ más código
```

---

# 11. Estado

**PROPUESTA METODOLÓGICA / NON_NORMATIVE**

Este documento no modifica NOP-1, NOP-2 ni CURRENT STATE.

Para convertir este régimen en obligatorio dentro de PymIA debe existir una autorización explícita del owner y, si corresponde, el Change Contract gobernado correspondiente.
