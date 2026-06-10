# MISSING_INPUT_TYPE_CLASSIFICATION_TASKSPEC

Fecha: 2026-06-10
Estado: READY_FOR_IMPLEMENTATION
Frente: clasificación explícita de faltantes

## 1. Problema

El flujo actual distingue correctamente que una respuesta narrativa del dueño no debe convertirse en evidencia estructural.

Sin embargo, los faltantes expuestos por el sistema no tienen una clasificación contractual explícita.

Hoy los faltantes reales nacen principalmente de:

```text
formula gates
evidence gates
DiagnosticCoreResult.missing_evidence
```

Eso implica, en la práctica, faltantes estructurales.

La deuda profunda es que esa condición no está formalizada como contrato visible.

## 2. Objetivo

Agregar clasificación explícita de missing inputs sin cambiar la semántica de los gates.

Tipos mínimos:

```text
STRUCTURAL_INPUT
OWNER_SEMANTIC_CLARIFICATION
MIXED
```

Estados mínimos de resolución frente a una respuesta del dueño:

```text
resolved_by_owner_answer
still_blocked_requires_structured_evidence
partially_resolved_still_blocked
not_applicable_to_missing_input
```

## 3. Principios

- No promover narrativa del dueño a evidencia estructural.
- No destrabar formula gates con declaraciones no validadas.
- No inventar evidencia.
- No cambiar DiagnosticCore.
- No cambiar fórmulas.
- No cambiar graph salvo necesidad mínima demostrada.
- Preservar trazabilidad interna.
- Mejorar explicación owner-facing.

## 4. Alcance técnico esperado

Auditar y modificar sólo si corresponde:

```text
pymia/audit_result/core_delivery_bridge.py
pymia/smartpyme/owner_questions_builder.py
pymia/contracts/owner_questions.py
pymia/contracts/owner_answers.py
pymia/contracts/owner_evaluation.py
pymia/smartpyme/owner_answers_evaluator.py
pymia/smartpyme/owner_actions_projector.py
```

Tests focales esperados:

```text
tests/smartpyme/test_owner_questions_builder.py
tests/smartpyme/test_core_delivery_bridge_reentry.py
tests/smartpyme/test_owner_answers_evaluator.py
```

## 5. Fuera de alcance

No tocar:

- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- runtime externo;
- DiagnosticCore;
- gates de fórmula/evidencia salvo lectura;
- nuevas fórmulas;
- reportes nuevos;
- refactor amplio.

## 6. Comportamiento requerido

### 6.1 Faltante estructural

Si un missing input proviene de formula gate, evidence gate o `DiagnosticCoreResult.missing_evidence`, debe clasificarse como:

```text
STRUCTURAL_INPUT
```

Si el dueño responde narrativamente, el estado debe ser:

```text
still_blocked_requires_structured_evidence
```

La salida visible debe poder explicar:

```text
Tu respuesta fue considerada, pero todavía falta evidencia o dato estructurado para resolver este punto.
```

### 6.2 Faltante semántico

Si en el futuro se crea una pregunta cuyo faltante sea de sentido operativo, no de dato duro, debe poder clasificarse como:

```text
OWNER_SEMANTIC_CLARIFICATION
```

Una respuesta narrativa válida podría resolverla como:

```text
resolved_by_owner_answer
```

Este TaskSpec no exige crear nuevos faltantes semánticos si no existen hoy.

### 6.3 Faltante mixto

Si una pregunta combina dato estructural y aclaración de sentido, debe clasificarse como:

```text
MIXED
```

Una respuesta parcial puede quedar como:

```text
partially_resolved_still_blocked
```

## 7. Criterios PASS

- Todo missing input real generado por gates actuales queda clasificado como `STRUCTURAL_INPUT`.
- La clasificación se conserva en `owner_questions_bundle` o metadata equivalente.
- La respuesta narrativa del dueño no resuelve faltantes estructurales.
- El render visible explica que la respuesta fue considerada pero falta evidencia estructural.
- Tests focales cubren al menos:
  - structural input no resuelto por narrativa;
  - trazabilidad del missing key;
  - ausencia de `evidence_candidate`;
  - preservación de warning/next_step owner-facing.

## 8. Criterios FAIL

- Una declaración narrativa se promueve a evidencia dura.
- Un formula/evidence gate se destraba sin dato estructurado.
- Se pierde `missing_key` o trazabilidad técnica.
- La clasificación sólo existe en texto visible y no en contrato/metadata.
- Se toca runtime externo o DiagnosticCore sin necesidad.

## 9. Resultado esperado

Checkpoint final:

```text
docs/pymia/MISSING_INPUT_TYPE_CLASSIFICATION_CHECKPOINT.md
```

Salida esperada:

```text
VEREDICTO: PASS / PARTIAL / BLOCKED
CLASIFICACIÓN: PATCH_MINIMO / SIN_CODIGO / BLOQUEADO
TESTS EJECUTADOS
RESULTADO
ARCHIVOS MODIFICADOS
DECISIÓN CONTRACTUAL
FRICCIONES REMANENTES
NO PUSH
```
