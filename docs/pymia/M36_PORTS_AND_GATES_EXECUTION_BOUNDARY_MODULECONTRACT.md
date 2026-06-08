# M36 — Ports and Gates Execution Boundary ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M36_PORTS_AND_GATES_AUTHORIZATION`

---

## 1. Módulo / frontera

Frontera mínima entre evidencia estructurada y ejecución del core diagnóstico.

```text
StructuredEvidence
→ gate de inputs por fórmula
→ gate de suficiencia por fórmula
→ DiagnosticCoreV1
```

---

## 2. Responsabilidades

La frontera M36 debe:

- transformar estado de evidencia en estado contractual por fórmula;
- expresar una decisión explícita de avance o bloqueo antes del core;
- separar preparación de inputs de ejecución del core;
- reutilizar binding y suficiencia existentes donde sea posible;
- mantener salidas determinísticas y serializables.

---

## 3. Inputs

- `StructuredEvidence`
- `case_id`
- `tenant_id`
- `formula_ids`
- `hypothesis_codes` opcional

---

## 4. Outputs

### Port 1 — `FORMULA_INPUT_GATE`

Devuelve `FormulaInputGateResult` por fórmula:

- `formula_id`
- `required_variables`
- `available_variables`
- `missing_variables`
- `status`

### Port 2 — `EVIDENCE_STATUS_PORT`

Puede proyectar el estado de cada fórmula ya calculado por el gate:

- `READY`
- `MISSING_INPUTS`

### Port 3 — `EVIDENCE_SUFFICIENCY_GATE`

Devuelve `EvidenceGateDecision` por fórmula:

- `formula_id`
- `decision`
- `missing_variables`

---

## 5. Errores y bloqueos

La frontera debe bloquear por:

- variables faltantes;
- evidencia insuficiente por fórmula;
- intento de avanzar una fórmula sin inputs requeridos.

No debe degradar esos bloqueos a narrativa ni a hallazgo.

---

## 6. Side effects

No debe tener side effects.

Explícitamente prohibido:

- ejecutar Telegram;
- tocar runtime;
- persistir estado;
- mutar evidencia;
- calcular fórmulas;
- invocar diagnóstico fuera de contrato.

---

## 7. Determinism expectations

- mismo input → mismo orden y misma salida
- no inventar variables
- no inferir faltantes por heurística
- no cambiar `DiagnosticCoreV1`

---

## 8. Dependency boundaries

Dependencias permitidas:

- `pymia/contracts/evidence_v1.py`
- `pymia/contracts/formula_contract.py`
- `pymia/diagnostic_core/evidence_binding.py`
- `pymia/diagnostic_core/evidence_sufficiency.py`
- `pymia/diagnostic_core/models.py`
- `pymia/diagnostic_core/core.py` sólo como frontera consumidora, no como dependencia a ejecutar siempre

Dependencias prohibidas:

- parser Excel
- `pymia/smartpyme/runtime_bridge.py`
- `pymia/telegram_*`
- `conversa-engine/`

---

## 9. Forbidden responsibilities

La frontera M36 no puede:

- confirmar patologías;
- producir findings;
- generar narrativa;
- generar reportes;
- abrir casos;
- agregar fórmulas nuevas.
