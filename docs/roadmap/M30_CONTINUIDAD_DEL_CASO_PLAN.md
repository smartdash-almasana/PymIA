# M30 — Continuidad del caso Plan

## Estado

PLAN_DRAFT

## Contexto

M27 cerró el puente mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.

M28 cerró ActionableFinding[] -> NarrativeReport grounded -> markdown legible/auditable.

M29 cerró owner_message + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.

M30 debe demostrar continuidad mínima del caso asistido por tenant.

No declara producto final, autonomía end-to-end ni servicio comercial validado.

## Objetivo

Demostrar que un caso asistido puede persistir y recuperarse sin reiniciar desde cero:

- dolor inicial;
- evidencia usada;
- hallazgos generados;
- reporte o resumen entregable;
- próximo paso sugerido;
- estado del caso;
- aislamiento entre tenants.

## Alcance permitido

- test de aceptación con storage local aislado;
- uso de PymIAState;
- uso de save_state/load_state/find_conversations_by_tenant;
- persistencia en progressive_context y campos existentes;
- sin producción nueva.

## Fuera de alcance

- registry/capabilities.yaml;
- dispatcher;
- plugins;
- Telegram/PDF/HTML/UI;
- CI;
- ERP/Odoo/Dolibarr;
- LLM/red;
- producto final;
- servicio comercial validado.

## Test esperado

Archivo:

tests/orchestration/test_m30_case_continuity_acceptance.py

Debe validar:

1. tenant_a guarda un caso asistido con problema, evidencia, hallazgos, reporte y próximo paso.
2. tenant_b guarda un caso distinto.
3. tenant_a vuelve y recupera su contexto útil.
4. tenant_a evoluciona sin perder el contexto previo.
5. tenant_a y tenant_b no se mezclan.
6. find_conversations_by_tenant mantiene aislamiento.

## Criterio PASS

M30 pasa si los tests demuestran continuidad mínima de caso asistido usando contratos existentes de state/state_storage.

## Criterio BLOCKED

Bloquear si para persistir el caso hay que tocar producción, dispatcher, registry, UI, red o crear arquitectura nueva.
