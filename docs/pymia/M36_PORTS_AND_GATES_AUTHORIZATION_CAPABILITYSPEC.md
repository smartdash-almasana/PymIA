# M36 — Ports and Gates Authorization CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M36_PORTS_AND_GATES_AUTHORIZATION`

---

## 1. Capacidad

PymIA puede exponer puertos y gates ejecutables mínimos entre evidencia estructurada, suficiencia de inputs y `DiagnosticCoreV1`, sin ampliar diagnóstico ni cálculo.

La capacidad autorizada es:

```text
StructuredEvidence
→ FormulaInputGate
→ EvidenceSufficiencyGate
→ DiagnosticCoreV1
```

---

## 2. Qué puede hacer

La capacidad M36 puede:

- representar contractualmente el estado de inputs por fórmula;
- representar contractualmente la decisión de gate previa al core;
- separar frontera de evidencia vs frontera de ejecución;
- bloquear avance cuando falten inputs;
- autorizar avance cuando la fórmula esté `READY`;
- preservar `formula_id`, variables requeridas, variables disponibles y faltantes.

---

## 3. Inputs requeridos

- `StructuredEvidence`
- `formula_ids`
- `case_id`
- `tenant_id`
- metadata de `source_refs` ya existente cuando aplique

---

## 4. Outputs requeridos

### FormulaInputGateResult

- `formula_id`
- `required_variables`
- `available_variables`
- `missing_variables`
- `status`

Estados:

- `READY`
- `MISSING_INPUTS`

### EvidenceGateDecision

- `formula_id`
- `decision`
- `missing_variables`

Decisiones:

- `ALLOW_EXECUTION`
- `BLOCK_MISSING_INPUTS`

---

## 5. Limitaciones obligatorias

M36 no autoriza:

- fórmulas nuevas;
- diagnóstico nuevo;
- findings nuevos;
- narrativa;
- reportes owner-facing;
- cambios en `DiagnosticCoreV1`;
- cambios en parser Excel;
- cambios en Telegram;
- cambios en runtime.

---

## 6. Failure states

La capacidad debe admitir explícitamente:

- fórmula con inputs completos → `READY` / `ALLOW_EXECUTION`
- fórmula con inputs faltantes → `MISSING_INPUTS` / `BLOCK_MISSING_INPUTS`
- orden determinístico por fórmula
- fail-closed si no existe evidencia suficiente

---

## 7. Fuera de alcance

- confirmación diagnóstica
- evaluación patológica nueva
- grounding de findings
- generación de reportes
- guided evidence recovery
- apertura de `M37`

---

## 8. Evidencia mínima esperada antes de PASS implementativo

La implementación posterior de M36 sólo podrá declararse `PASS` si aporta:

- tests focales del gate de inputs;
- tests focales del gate de suficiencia;
- evidencia de no invocación del core cuando el gate bloquea;
- checkpoint posterior del frente.
