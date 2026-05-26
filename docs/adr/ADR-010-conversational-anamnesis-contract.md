# ADR-010 — Conversational Anamnesis Contract

Status: Accepted

## Context

El repositorio usa el término "anamnesis" en múltiples capas:

1. `AnamnesisOriginaria` en `pymia/services/initial_laboratory_anamnesis_service.py`.
2. `payload.anamnesis` y `mode=anamnesis_inicial` en `pymia/hermes/adapter.py`.
3. Diseño aspiracional en `docs/catalogo/anamnesis-y-catalogos.md` (ADR-CAT-001).
4. Taxonomía de interrogación en `docs/smartpyme/SMARTPYME_INTERROGATION_TAXONOMY.md`.

Estos usos no están reconciliados en un contrato único.

Además, existe una brecha entre:
- runtime SmartPyme determinístico actual (cadena de contratos y gates),
- y el alcance aspiracional documental de largo plazo.

El método hipotético-deductivo requiere hipótesis como entidad explícita y
trazable, no solo síntomas y pedidos de evidencia.

## Decision

1. "Anamnesis" se define como el primer tiempo lógico de encuadre y
   formulación inicial, cuyo resultado formal esperado es un
   `BusinessAnamnesisRecord`.
2. "Hipótesis" se define como entidad operacional (`OperationalHypothesis`) con
   ciclo de vida: `ABIERTA | EN_CONTRASTE | CONFIRMADA | DESCARTADA | EVIDENCIA_INSUFICIENTE`.
3. "Laboratorio" se define como ciclo de contraste de hipótesis contra evidencia.
4. `BusinessTaxonomySnapshot` se define como input obligatorio antes de
   hipótesis investigables de negocio (ej. rentabilidad/margen).
5. ADR-CAT-001 queda explícitamente como aspiracional de largo plazo y no
   autoriza implementación automática de sus 12 catálogos.

## Required Conceptual Contracts (documental)

### BusinessTaxonomySnapshot
- tenant_id
- organism_type
- industry
- size
- complexity
- sales_channels
- operational_flow_stages
- areas_present
- systems_available
- jurisdiction
- currency
- confidence
- source
- created_at

### BusinessAnamnesisRecord
- anamnesis_id
- tenant_id
- intake_id
- raw_narrative
- declared_pains
- owner_hypotheses
- linguistic_signals
- business_taxonomy
- documents_declared
- documents_available
- conversational_state
- created_at
- updated_at

### OperationalHypothesis
- hypothesis_id
- tenant_id
- intake_id
- formulation
- source
- domain
- related_symptoms
- required_evidence
- status
- findings_refs
- created_at
- closed_at

### ConversationContract
- contract_id
- tenant_id
- anamnesis_ref
- taxonomy_ref
- hypotheses_open
- hypotheses_closed
- evidence_received
- evidence_pending
- current_phase
- allowed_actions
- forbidden_actions

### AnamnesisReadiness
- tenant_id
- anamnesis_id
- status
- taxonomy_complete
- narrative_sufficient
- blocking_reasons

## Hermes ↔ Kernel Boundary

Hermes puede:
- conversar,
- pedir evidencia faltante,
- explicar outputs permitidos,
- proponer próximo paso permitido,
- escalar a HITL.

Hermes no puede:
- diagnosticar por fuera del kernel,
- inventar hallazgos,
- saltar gates,
- convertir warnings en diagnóstico,
- mezclar tenants,
- reinterpretar raw_input como verdad confirmada.

Regla de oro:
Sin `DeliveryPackage` con `gate_verdict=PASS`, Hermes no afirma hallazgos
como confirmados.

## Consequences

Positivas:
- unificación semántica,
- menor deriva conversacional,
- menor sobrepromesa documental,
- base clara para futuros slices de contratos.

Negativas:
- postergación explícita de implementación de menú/bot,
- necesidad de cerrar primero contratos documentales adicionales.

## Not Authorized By This ADR

Este ADR no autoriza:
- runtime nuevo,
- nuevas MCP tools,
- cambios en `run_interrogation`, `select_tanks`, `intake`, `evidence_gate`,
  `readiness`, `dispatcher`, `execution_gate`, `delivery_package`,
  `delivery_markdown`,
- cambios en `HermesAdapter` ni `ClinicalConversationalPort`,
- UI, menú, bot Telegram real, producción,
- implementación inmediata de los 12 catálogos de ADR-CAT-001.

## Follow-up Roadmap (non-binding)

1. SMARTPYME_BUSINESS_TAXONOMY_SNAPSHOT_SLICE (contrato + tests).
2. SMARTPYME_OPERATIONAL_HYPOTHESIS_SLICE (contrato + tests).
3. SMARTPYME_ANAMNESIS_UNIFIED_RECORD (reconciliar usos actuales).
