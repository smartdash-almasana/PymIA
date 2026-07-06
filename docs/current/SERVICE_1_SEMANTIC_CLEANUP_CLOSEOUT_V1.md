# SERVICE_1_SEMANTIC_CLEANUP_CLOSEOUT_V1

Status: CLOSED_FOR_CONTINUATION
Scope: Servicio 1 semantic cleanup and next functional lane
Date: 2026-07-06

## 1. Cierre

La fase de saneamiento semántico de Servicio 1 queda cerrada para continuidad operativa.

Este cierre no declara Servicio 1 completo. Declara que la contaminación principal de nombres y fronteras quedó corregida o aislada como compatibilidad legacy explícita.

## 2. Semántica canónica vigente

### Intake / Reentry / QuestionBundle

Campo primario:

```text
owner_confirmation_required
```

Significado:

```text
El dueño confirma datos, columnas, contexto, período o evidencia durante intake/reentry.
```

No significa revisión humana final de carpeta.

### Delivery / QA / Release / Signoff

Campo/objeto primario:

```text
delivery_policy_guard
```

Significado:

```text
Control de política de entrega, claims, límites y no-autonomía antes de usar la salida.
```

No significa revisión humana difusa ni aprobación contable.

## 3. Legacy permitido sólo como compatibilidad

Los siguientes nombres pueden existir sólo como alias, shim o fallback temporal:

```text
human_review_required
human_review_gate
build_service_1_human_review_gate_v1
PENDING_HUMAN_REVIEW
READY_FOR_HUMAN_REVIEW
```

Regla:

```text
No pueden volver a ser campo primario, status primario, contrato nuevo ni narrativa principal de Servicio 1.
```

## 4. Commits de saneamiento reportados

```text
9989f3b84ac3f1622cac85d939f0cdb3ab7f6608
- owner_confirmation para intake/reentry/question_bundle
- tests focales reportados: 87 passed

ddbbea0
- delivery human review gate -> delivery_policy_guard
- tests focales reportados: 40 passed

d3d0192
- release/signoff -> delivery_policy_guard
- tests focales reportados: 49 passed
```

## 5. ADR funcional creada

Archivo:

```text
docs/adr/SERVICE_1_PATHOLOGY_CATALOG_AND_ANAMNESIS_ADR_V1.md
```

Estado:

```text
Proposed
```

Lectura correcta:

```text
La ADR no reemplaza el objetivo macro vigente de docs/current/SERVICE_1_STATUS.md.
Ordena el próximo sub-frente implementable del carril asistido XLSX dentro de Servicio 1.
```

## 6. Qué queda cerrado

```text
1. Intake semántico.
2. Reentry semántico.
3. QuestionBundle semántico.
4. Delivery policy guard.
5. Signoff/release policy guard.
6. ADR Pathology Catalog + Anamnesis creada y alineada.
```

## 7. Qué NO se debe reabrir ahora

```text
- human_review como concepto de diseño.
- delivery/signoff/release rename.
- owner_confirmation rename.
- discusión de autonomía vs asistido en esta fase.
- accounting.
- Servicio 2.
- SaaS/autonomous.
- entrypoint unification.
- marketing.
```

## 8. Próximo frente único permitido

```text
SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_CONTRACT_V1
```

Modo recomendado:

```text
módulo puro, pequeño, sin IO, sin LLM, sin diagnóstico final, sin accounting, sin delivery.
```

Debe materializar los contratos conceptuales de la ADR:

```text
Service1AnamnesisRecordV1
Service1PathologyCandidateV1
Service1AnamnesisTriageDecisionV1
```

## 9. Regla de continuación

Antes de abrir nuevas capacidades, cualquier agente debe respetar:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma datos durante intake/reentry.
La entrega se controla por delivery_policy_guard.
```

## 10. Veredicto final

```text
SEMANTIC_CLEANUP_CLOSED
READY_FOR_SINGLE_FUNCTIONAL_SLICE
```
