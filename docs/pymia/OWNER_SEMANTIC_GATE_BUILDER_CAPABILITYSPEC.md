# Owner Semantic Gate Builder CapabilitySpec

Fecha: 2026-06-10
Estado: DRAFT_FOR_REVIEW
Frente: `OWNER_SEMANTIC_GATE_BUILDER`

---

## 1. Objetivo

Autorizar documentalmente una futura capacidad pura:

```text
structured_semantic_translation_payload
→ OwnerSemanticConfirmationGate(status=PENDING_OWNER_CONFIRMATION)
```

La capacidad debe permitir que una traducción conversacional estructurada, producida fuera del kernel por Hermes/IA, sea convertida en un gate pendiente de confirmación explícita del dueño.

Este documento no autoriza implementación todavía.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/pymia/OWNER_SEMANTIC_LOOP_THREE_LAYER_FLOW.md`
- `docs/pymia/SEMANTIC_CONFIRMATION_REENTRY_BLOCK_CLOSURE.md`
- `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION_CAPABILITYSPEC.md`

---

## 3. Capacidad autorizada

Se autoriza, sólo a nivel de capacidad futura, un builder/adaptador puro en la capa `pymia/smartpyme/` que reciba un payload estructurado de traducción semántica y construya un `OwnerSemanticConfirmationGate` en estado pendiente.

Módulo futuro candidato:

```text
pymia/smartpyme/owner_semantic_gate_builder.py
```

Función futura candidata:

```text
build_pending_owner_semantic_confirmation_gate_from_translation(...)
```

La función debe operar sobre datos estructurados. No debe recibir ni interpretar texto libre directamente.

---

## 4. Input permitido

El payload estructurado podrá contener únicamente campos orientados a proponer una interpretación para confirmar.

Campos permitidos mínimos:

- `proposed_interpretation`
- `target_type`
- `source_ref`
- `related_missing_keys`
- `related_pathology_candidates`
- `related_formula_candidates`
- `tenant_id`, opcional
- `metadata`, opcional y no soberana

---

## 5. Output esperado

El output esperado es un `OwnerSemanticConfirmationGate` con:

- `status = PENDING_OWNER_CONFIRMATION`
- `target_type` explícito
- `proposed_interpretation` no vacío
- `source_ref` trazable
- candidatos relacionados preservados como listas

El gate resultante debe ser apto para proyectarse posteriormente hacia `OwnerQuestion.metadata` mediante la capacidad ya autorizada de proyección gate → metadata.

---

## 6. Reglas obligatorias

El builder futuro debe:

- exigir `proposed_interpretation` no vacío;
- exigir `target_type` válido;
- exigir `source_ref` no vacío;
- normalizar candidatos relacionados como listas;
- crear sólo gates pendientes;
- fallar cerrado ante payload inválido;
- preservar trazabilidad;
- no mutar el payload de entrada.

---

## 7. Invariantes

La capacidad debe ser:

- pura;
- determinística;
- local;
- sin IO;
- sin LLM;
- sin runtime;
- sin acceso a Telegram;
- sin acceso a Hermes runtime;
- sin integración con graph;
- sin integración con bridge;
- sin DiagnosticCore;
- sin fórmulas nuevas;
- sin generación de findings;
- sin diagnóstico;
- sin evidencia estructural;
- sin inferencia de confirmación desde texto libre.

---

## 8. Prohibiciones explícitas

Este CapabilitySpec no autoriza:

- interpretar texto libre dentro de PymIA;
- inferir que el dueño confirmó algo;
- construir gates terminales;
- promover narrativa del dueño a evidencia dura;
- crear `evidence_candidate`;
- crear `computed_variables`;
- modificar `pymia/contracts/owner_semantic_confirmation.py`;
- modificar `pymia/audit_result/core_delivery_bridge.py`;
- modificar `pymia/orchestration/graph.py`;
- modificar runtime;
- modificar Telegram;
- modificar PDF;
- modificar ERP.

---

## 9. Tests futuros sugeridos

Cuando se abra el frente implementativo, deberán existir tests focales en `tests/smartpyme/` que cubran:

1. payload válido crea gate pendiente;
2. falta `proposed_interpretation` falla cerrado;
3. falta `source_ref` falla cerrado;
4. `target_type` inválido falla cerrado;
5. status terminal en payload es ignorado o rechazado;
6. no aparecen `evidence_candidate` ni `computed_variables`;
7. candidatos relacionados se preservan como listas;
8. el payload de entrada no se muta;
9. el gate resultante puede proyectarse a `OwnerQuestion.metadata` sin confirmación terminal.

---

## 10. Frontera con Hermes/IA

Hermes/IA puede producir una traducción semántica estructurada como hipótesis conversacional.

PymIA no debe interpretar texto libre en este frente. PymIA sólo debe validar el payload estructurado y construir el gate pendiente que exige confirmación explícita del dueño.

La cadena esperada es:

```text
Dueño narra en lenguaje propio
→ Hermes/IA produce structured_semantic_translation_payload
→ PymIA construye OwnerSemanticConfirmationGate pendiente
→ PymIA proyecta OwnerQuestion.metadata
→ dueño confirma, rechaza o corrige
```

---

## 11. Veredicto

`CAPABILITY_DRAFTED_FOR_REVIEW`

La capacidad queda propuesta documentalmente. No habilita código hasta que exista autorización explícita posterior con ModuleContract/TaskSpec o decisión metodológica equivalente.
