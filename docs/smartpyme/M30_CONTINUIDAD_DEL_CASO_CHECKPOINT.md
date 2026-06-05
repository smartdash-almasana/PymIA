# M30 — Continuidad del caso Checkpoint

## Estado

PASS

## Contexto

M30 continúa el roadmap de servicio asistido Excel + semántica PyME.

M27 cerró el puente: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.

M28 cerró el puente: ActionableFinding[] -> EvidenceItem[] -> NarrativeReport grounded -> markdown legible/auditable.

M29 cerró el puente: owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.

M30 demuestra continuidad mínima del caso asistido por tenant usando contratos existentes de orquestación y storage.

No declara producto final, autonomía end-to-end ni servicio comercial validado.

## Archivos creados

- docs/roadmap/M30_CONTINUIDAD_DEL_CASO_PLAN.md
- tests/orchestration/test_m30_case_continuity_acceptance.py

## Objetivo del slice

Demostrar que un caso asistido puede persistir y recuperarse sin reiniciar desde cero, conservando:

- dolor inicial;
- evidencia usada;
- hallazgos generados;
- reporte mínimo o referencia de reporte;
- próximo paso sugerido;
- estado del caso;
- aislamiento entre tenants.

## Contratos usados

- pymia.orchestration.state.PymIAState
- pymia.orchestration.state_storage.save_state
- pymia.orchestration.state_storage.load_state
- pymia.orchestration.state_storage.find_conversations_by_tenant

No se modificó producción.
No se tocó dispatcher, registry, plugins, Telegram, PDF, HTML, UI, CI, ERP, red ni LLM.

## Validación reportada por agente local

El asistente de chat no ejecutó pytest directamente. La siguiente evidencia fue reportada por el usuario desde agente local.

Comando focal:

python -m pytest tests/orchestration/test_m30_case_continuity_acceptance.py -q

Resultado reportado:

1 passed in 4.20s

Comando de continuidad combinada:

python -m pytest tests/orchestration/test_tenant_continuity_acceptance.py tests/orchestration/test_m30_case_continuity_acceptance.py -q

Resultado reportado:

2 passed in 3.33s

## Veredicto

M30 PASS.

Certificado por evidencia reportada:

caso asistido tenant_a -> persistencia de contexto útil -> tenant_b independiente -> tenant_a vuelve -> recuperación y evolución del caso -> aislamiento entre tenants.

No certificado:

- producto final;
- servicio comercial validado;
- diagnóstico integral;
- flujo con dispatcher;
- casos reales de cliente;
- automatización end-to-end.

## Próximo hito sugerido

Según el roadmap vigente, el siguiente hito natural es M31 — Servicio asistido repetible.

Antes de abrir M31, cerrar M30 con commit/push y dejar repo limpio.
