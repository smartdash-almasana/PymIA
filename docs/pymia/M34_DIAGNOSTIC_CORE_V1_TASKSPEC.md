# M34 — DiagnosticCoreV1 TaskSpec

Fecha: 2026-06-07
Estado: TaskSpec inicial
Frente activo: `DIAGNOSTIC_CORE_V1`

---

## 1. Objetivo

Crear el primer slice de `DiagnosticCoreV1` sin tocar Telegram, LangGraph, runtime productivo ni legacy.

Este slice no debe intentar resolver todo el diagnóstico PyME.

Debe crear una columna vertebral mínima, testeable y bloqueante para que los siguientes slices implementen fórmulas y patologías reales sin volver a emparchar el pipeline.

---

## 2. Slice

```text
M34-S1 — DiagnosticCoreV1 skeleton
```

---

## 3. Puertos afectados

Según `docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md`:

```text
EVIDENCE_STATUS_PORT
FORMULA_EXECUTION_PORT
DIAGNOSTIC_RESULT_PORT
FINDING_PORT
```

---

## 4. Gates afectados

```text
EVIDENCE_SUFFICIENCY_GATE
FORMULA_INPUT_GATE
DIAGNOSTIC_EVIDENCE_GATE
FINDING_GROUNDING_GATE
```

---

## 5. Problema que resuelve

Actualmente existen piezas parciales:

```text
pymia/audit_result/evidence_requirement_matcher.py
pymia/audit_result/builder.py
pymia/audit_result/models.py
pymia/services/formula_engine_service.py
pymia/services/pathology_engine_service.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

Pero no existe un módulo central `DiagnosticCoreV1` que reciba un caso/evidencia y coordine:

```text
evidencia disponible/faltante
→ fórmula ejecutable o bloqueada
→ diagnóstico confirmado/insuficiente/bloqueado
→ hallazgo mínimo trazable
```

---

## 6. Alcance permitido

Crear, como máximo:

```text
pymia/diagnostic_core/__init__.py
pymia/diagnostic_core/models.py
pymia/diagnostic_core/core.py
tests/diagnostic_core/test_diagnostic_core_v1.py
```

Opcional si Codex justifica necesidad mínima:

```text
pymia/diagnostic_core/adapters.py
```

---

## 7. Archivos read-only

Pueden leerse, no modificarse en M34-S1:

```text
pymia/audit_result/evidence_requirement_matcher.py
pymia/audit_result/builder.py
pymia/audit_result/models.py
pymia/contracts/evidence_v1.py
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/services/pathology_engine_service.py
pymia/services/pathology_knowledge_tank.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
docs/pymia/KERNEL_PIPELINE_INVENTORY.md
```

---

## 8. Archivos prohibidos

No tocar:

```text
pymia/telegram_bot_runtime.py
pymia/telegram_document_handler.py
pymia/smartpyme/post_ficha_evidence_gate.py
pymia/smartpyme/anamnesis_fsm.py
pymia/smartpyme/anamnesis_fsm_integration.py
pymia/smartpyme/intake.py
pymia/smartpyme/runtime_bridge.py
pymia/smartpyme/microservice_dispatcher.py
pymia/smartpyme/capabilities.yaml
conversa-engine/
tools/
SmartPyme/
```

---

## 9. Conducta obligatoria del core

`DiagnosticCoreV1` debe:

```text
1. aceptar un input estructurado mínimo;
2. preservar referencias de evidencia;
3. consultar o aceptar estado de evidencia;
4. no inventar variables;
5. no ejecutar fórmulas no soportadas;
6. devolver bloqueo explícito si una fórmula no está implementada;
7. no producir hallazgo confirmado sin fórmula OK y evidencia suficiente;
8. producir output determinístico serializable;
9. no emitir texto conversacional para dueño PyME;
10. no depender de Telegram, LangGraph, Hermes ni localhost.
```

---

## 10. Modelos mínimos esperados

Codex puede ajustar nombres internos, pero debe preservar esta semántica:

```text
DiagnosticCoreInput
- case_id
- tenant_id
- hypothesis_codes
- formula_ids
- variables
- evidence_refs
- evidence_status opcional

DiagnosticCoreResult
- case_id
- tenant_id
- status: READY | PARTIAL | BLOCKED | INSUFFICIENT
- formula_results
- diagnostic_results
- findings
- missing_evidence
- blocked_reasons

CoreFormulaResult
- formula_id
- status
- value
- source_refs
- blocking_reason

CoreDiagnosticResult
- pathology_code
- status: CONFIRMED | NOT_CONFIRMED | INSUFFICIENT | CANDIDATE | BLOCKED
- formula_id
- reason
- evidence_refs

CoreFinding
- finding_id
- pathology_code
- formula_id
- status
- summary
- evidence_refs
```

---

## 11. Fórmulas en M34-S1

M34-S1 no debe implementar todavía `REN_001_margen_neto_real` ni `LIQ_001_vendido_cobrado` si no existen en `FormulaEngineService`.

Debe probar bloqueo honesto para fórmulas no soportadas.

Puede usar fórmulas ya soportadas:

```text
margen_bruto
ganancia_bruta
```

Sólo para demostrar coordinación del core.

---

## 12. Tests obligatorios

Crear `tests/diagnostic_core/test_diagnostic_core_v1.py` con tests mínimos:

### Test 1 — bloquea fórmula no soportada

Dado:

```text
formula_id = REN_001_margen_neto_real
variables suficientes aparentes
```

Debe devolver:

```text
status BLOCKED o INSUFFICIENT
blocked_reason incluye FORMULA_NOT_SUPPORTED o equivalente
sin finding confirmado
```

### Test 2 — calcula fórmula soportada

Dado:

```text
formula_id = margen_bruto
ventas = 1000
costos = 700
source_refs presentes
```

Debe devolver:

```text
formula_result OK
value = 0.3
source_refs preservados
```

### Test 3 — no inventa inputs

Dado:

```text
formula_id = margen_bruto
ventas presente
costos ausente
```

Debe devolver:

```text
formula_result BLOCKED
blocked_reason menciona missing input
sin finding confirmado
```

### Test 4 — output serializable

El resultado completo debe poder serializarse a dict/json sin objetos opacos.

---

## 13. Criterios PASS

PASS sólo si:

```text
- sólo se crean archivos permitidos;
- no se toca Telegram;
- no se toca legacy;
- no se toca smartpyme runtime;
- tests nuevos pasan;
- tests focales de servicios de fórmula siguen pasando si se ejecutan;
- output bloquea fórmulas no soportadas sin simular soporte;
- git status final limpio tras commit;
- no push.
```

---

## 14. Criterios PARTIAL

PARTIAL si:

```text
- skeleton creado;
- tests escritos;
- algún test falla por contrato existente;
- no se tocó código prohibido;
- se informa causa exacta.
```

---

## 15. Criterios BLOCKED

BLOCKED si:

```text
- falta acceso al repo;
- hay dirty state no relacionado;
- no se puede crear tests;
- para implementar se necesitaría modificar archivos prohibidos;
- Codex detecta contradicción entre contratos existentes y este TaskSpec.
```

---

## 16. Evidencia obligatoria de salida

Codex debe devolver:

```text
VEREDICTO
FILES CHANGED
DIFF SUMMARY
TEST RESULTS
COMMIT HASH
GIT STATUS FINAL
CONFIRMACIÓN NO PUSH
```

---

## 17. No objetivos

No hacer en M34-S1:

```text
- no Telegram;
- no LangGraph;
- no FastAPI;
- no UI;
- no localhost;
- no migrar SmartPyme;
- no refactor masivo;
- no ampliar catálogos;
- no implementar 50 patologías;
- no declarar producto;
- no generar reporte final para dueño.
```
