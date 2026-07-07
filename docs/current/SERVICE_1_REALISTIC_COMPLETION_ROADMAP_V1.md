# SERVICE_1_REALISTIC_COMPLETION_ROADMAP_V1

Status: PROPOSED
Scope: Servicio 1 complete-product roadmap
Date: 2026-07-06

## 1. Veredicto

Servicio 1 no debe progresar por acumulación de módulos ni por promesas macro.
Debe progresar por cadenas verificables, con una separación explícita entre:

```text
A. Servicio 1 operativo XLSX-first, gobernado por evidencia, reglas y policy guard.
B. Autonomía guardada SaaS como objetivo macro posterior.
```

El estado canónico vigente mantiene como objetivo macro `S1_AUTONOMOUS_GUARDED_SAAS_V1`, pero el camino realista exige terminar primero el Servicio 1 operativo XLSX-first, porque ahí se prueba el valor PyME real y se evita que la autonomía gobierne capacidades inmaduras.

## 2. Base actual certificada para este roadmap

### 2.1 Servicio 1 Full Assisted V1

Estado canónico:

```text
SERVICE_1_FULL_ASSISTED_V1: CLOSED_WITH_LIMITS
NEXT_OBJECTIVE: S1_AUTONOMOUS_GUARDED_SAAS_V1
```

### 2.2 Bloque Pathology / Anamnesis / Triage

Bloque cerrado y pusheado:

```text
SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE
Commit reportado: 0fbc0cc
Working tree reportado: clean
```

Capacidades:

```text
owner narrative / owner answer reentry
-> anamnesis record
-> pathology candidates
-> triage decision
-> question bundle output
-> loop composition
```

Validación focal reportada:

```text
28 passed in 1.41s
```

### 2.3 Entrypoint candidate reciente

Slice creado:

```text
SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_ENTRYPOINT_CANDIDATE_V1
```

Validación focal:

```text
7 passed in 0.52s
```

Estado:

```text
PENDING_SELECTIVE_COMMIT
```

## 3. Principio de integridad

Cada nuevo bloque debe seguir esta cadena:

```text
1. Contract puro.
2. Bridge mínimo.
3. Output usable.
4. Composition.
5. Test focal.
6. Guard audit chico.
7. Commit selectivo.
8. Recién después próximo frente.
```

Reglas permanentes:

```text
NO_SECOND_XLSX_PARSER
NO_NEW_SOVEREIGN_GATE_CHAIN
NO_PIPELINE_TOOL_REQUESTS_OUTSIDE_EXPLICIT_GATE
NO_HUMAN_PROXY_ROLE_IN_SERVICE_1
ONLY_OWNER_DIALOGUES_WITH_PYMIA
NO_AUTONOMOUS_DELIVERY_BEFORE_POLICY_GUARD
```

## 4. Definición realista de “Servicio 1 completo”

Servicio 1 completo no significa SaaS autónomo total.
Para este roadmap, Servicio 1 completo significa:

```text
Una PyME puede entregar un XLSX o narrativa operacional inicial;
PymIA puede entender el problema,
pedir confirmaciones al dueño,
seleccionar una patología candidata,
verificar evidencia mínima,
proponer o ejecutar un cómputo permitido en modo controlado,
generar un hallazgo operativo acotado,
controlar claims con delivery_policy_guard,
y producir una salida usable para el dueño sin prometer diagnóstico definitivo ni contabilidad soberana.
```

## 5. Roadmap por fases

## Fase 0 — Cierre del entrypoint candidate actual

### Objetivo

Cerrar el slice ya creado:

```text
SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_ENTRYPOINT_CANDIDATE_V1
```

### Estado

```text
IMPLEMENTADO
TEST FOCAL PASS: 7 passed in 0.52s
PENDING_SELECTIVE_COMMIT
```

### DoD

```text
- Audit guard focal PASS.
- Commit selectivo de los 2 archivos del entrypoint.
- Push OK.
- Working tree clean.
```

### No-alcance

```text
No runtime.
No delivery.
No accounting.
No SaaS.
```

---

## Fase 1 — Pathology to allowed computation candidate

### Frente

```text
SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1
```

### Objetivo

Mapear una patología candidata a una o más computaciones permitidas, sin ejecutar.

Ejemplos:

```text
REN_001 -> first_aid_precio_margen_basico_v1
LIQ_001 -> caja/cobranzas basic candidate o invoice_collection_matching basic candidate
STK_001 -> first_aid_stock_alertas_basicas_v1
CST_001 -> costeo básico candidate
SAL_001 -> ventas segmentación candidate
CSH_001 -> caja diaria triage candidate
```

### Output esperado

```text
Service1AllowedComputationCandidateV1
- pathology_code
- allowed_computation_ref
- required_fields
- missing_fields
- readiness_status
- runtime_authorized=False
```

### DoD

```text
- Contract puro.
- Test por 3 patologías iniciales como mínimo: REN_001, LIQ_001, STK_001.
- No ejecución de tools.
- No delivery.
```

---

## Fase 2 — Evidence readiness gate

### Frente

```text
SERVICE_1_PATHOLOGY_EVIDENCE_READINESS_GATE_V1
```

### Objetivo

Decidir si la evidencia mínima permite pasar de triage a plan de cómputo.

### Estados

```text
READY_FOR_COMPUTATION_PLAN
NEEDS_OWNER_CONFIRMATION
NEEDS_EVIDENCE
BLOCKED_UNSUPPORTED_PATHOLOGY
```

### Input

```text
entrypoint_candidate_result
allowed_computation_candidate
available_data_fields
column_meaning_confirmations
business_period_reference
```

### Output

```text
Service1PathologyEvidenceReadinessGateV1
```

### DoD

```text
- Falla cerrado si falta período, columnas o campos mínimos.
- Nunca autoriza runtime.
- Produce next_owner_questions si faltan datos.
```

---

## Fase 3 — Controlled computation plan

### Frente

```text
SERVICE_1_CONTROLLED_COMPUTATION_PLAN_V1
```

### Objetivo

Construir un plan de cómputo permitido, todavía sin ejecución.

### Output esperado

```text
Service1ControlledComputationPlanV1
- case_id
- pathology_code
- computation_ref
- input_field_bindings
- blocked_items
- execution_mode=DRY_RUN_CANDIDATE
- runtime_authorized=False
```

### DoD

```text
- No llama tools.
- No llama pipeline.
- No crea delivery.
- Sólo produce plan verificable.
```

---

## Fase 4 — Dry-run computation candidate

### Frente

```text
SERVICE_1_PATHOLOGY_FIRST_AID_DRY_RUN_CANDIDATE_V1
```

### Objetivo

Ejecutar controladamente sólo computaciones First Aid maduras cuando la evidencia esté lista.

### Orden recomendado de patologías

```text
1. REN_001 — Margen invisible.
2. STK_001 — Stock incierto.
3. CSH_001 — Caja desordenada por período.
4. LIQ_001 — Descalce ventas-cobranzas.
```

### DoD

```text
- Usa herramientas existentes.
- No duplica parser XLSX.
- No crea nuevo runtime general.
- Output candidate, no delivery final.
- delivery_authorized=False.
```

---

## Fase 5 — Assisted finding owner view

### Frente

```text
SERVICE_1_ASSISTED_FINDING_OWNER_VIEW_V1
```

### Objetivo

Traducir el resultado técnico en una vista entendible para el dueño.

### Output esperado

```text
- qué se encontró
- qué evidencia se usó
- qué falta confirmar
- qué no se puede afirmar
- próxima acción recomendada
```

### DoD

```text
- Lenguaje PyME.
- No diagnóstico definitivo.
- No promesa contable.
- No delivery final.
```

---

## Fase 6 — Finding delivery policy guard

### Frente

```text
SERVICE_1_PATHOLOGY_FINDING_DELIVERY_POLICY_GUARD_V1
```

### Objetivo

Controlar claims antes de convertir un hallazgo operativo acotado en salida entregable.

### Reglas

```text
- No afirmar más que la evidencia.
- No convertir candidato en diagnóstico definitivo.
- No ocultar faltantes.
- No usar human_review como concepto primario.
- Usar delivery_policy_guard.
```

### DoD

```text
- PASS/BLOCKED/NEEDS_OWNER_CONFIRMATION.
- Bloquea hallazgos sin evidencia suficiente.
- Bloquea lenguaje de autonomía o certeza absoluta.
```

---

## Fase 7 — Delivery package controlled integration

### Frente

```text
SERVICE_1_PATHOLOGY_FINDING_DELIVERY_PACKAGE_V1
```

### Objetivo

Integrar hallazgo operativo validado al paquete de entrega existente.

### DoD

```text
- Reusa service_1_case_delivery_folder_v1.py o capa existente.
- No crea delivery paralelo.
- Incluye manifest/summary/owner view.
- Preserva delivery_policy_guard.
```

---

## Fase 8 — Entrypoint oficial Servicio 1 operativo XLSX-first

### Frente

```text
SERVICE_1_ASSISTED_PRODUCT_ENTRYPOINT_V1
```

### Objetivo

Definir una entrada oficial controlada para el Servicio 1 operativo completo.

### Input

```text
XLSX/case metadata
owner narrative
column confirmations
available data fields
```

### Output

```text
status
selected pathology
next owner question OR finding candidate OR delivery blocked
trace packet
```

### DoD

```text
- Un entrypoint recomendado.
- Los otros entrypoints quedan como legacy/candidates/harness.
- No API/SaaS todavía.
```

---

## Fase 9 — Real client pilot pack

### Frente

```text
SERVICE_1_REAL_CLIENT_ASSISTED_PILOT_PACK_V1
```

### Objetivo

Preparar un caso real XLSX-first sin autonomía.

### DoD

```text
- Input checklist.
- Owner script.
- Operator runbook mínimo.
- Expected outputs.
- Stop rules.
- QA checklist.
```

---

## Fase 10 — SaaS/autonomy re-entry

### Frente

```text
S1_AUTONOMOUS_GUARDED_SAAS_V1_REENTRY_AFTER_ASSISTED_PRODUCT
```

### Objetivo

Recién después de cerrar el Servicio 1 operativo XLSX-first, volver al carril macro SaaS/autonomía.

### Condición previa

```text
Servicio 1 operativo XLSX-first ejecuta un ciclo útil completo:
owner narrative/XLSX -> pathology -> evidence readiness -> computation candidate/dry run -> assisted finding -> policy guard -> controlled delivery.
```

### No antes de eso

```text
No API endpoint.
No worker/queue.
No upload/storage runtime.
No autonomous delivery.
```

## 6. Orden de implementación recomendado

```text
0. Commit entrypoint candidate actual.
1. SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1
2. SERVICE_1_PATHOLOGY_EVIDENCE_READINESS_GATE_V1
3. SERVICE_1_CONTROLLED_COMPUTATION_PLAN_V1
4. SERVICE_1_PATHOLOGY_FIRST_AID_DRY_RUN_CANDIDATE_V1
5. SERVICE_1_ASSISTED_FINDING_OWNER_VIEW_V1
6. SERVICE_1_PATHOLOGY_FINDING_DELIVERY_POLICY_GUARD_V1
7. SERVICE_1_PATHOLOGY_FINDING_DELIVERY_PACKAGE_V1
8. SERVICE_1_ASSISTED_PRODUCT_ENTRYPOINT_V1
9. SERVICE_1_REAL_CLIENT_ASSISTED_PILOT_PACK_V1
10. S1_AUTONOMOUS_GUARDED_SAAS_V1_REENTRY_AFTER_ASSISTED_PRODUCT
```

## 7. Stop rules

Detener si aparece cualquiera de estos riesgos:

```text
- Nuevo parser XLSX.
- Nuevo gate soberano paralelo.
- Nuevo delivery paralelo.
- human_review como campo primario.
- runtime_authorized=True antes de readiness + policy guard.
- accounting amplio antes de First Aid seco.
- Servicio 2.
- SaaS/API/worker antes de Servicio 1 operativo XLSX-first completo.
- diagnóstico definitivo sin evidencia.
```

## 8. Métrica de progreso

No medir por cantidad de archivos.
Medir por cadenas cerradas:

```text
CHAIN_1: owner narrative -> triage -> next owner question       CLOSED
CHAIN_2: pathology -> allowed computation candidate             NEXT
CHAIN_3: candidate -> evidence readiness                         PENDING
CHAIN_4: readiness -> controlled computation plan                 PENDING
CHAIN_5: plan -> dry-run candidate                               PENDING
CHAIN_6: dry-run -> assisted finding owner view                   PENDING
CHAIN_7: finding -> delivery policy guard                         PENDING
CHAIN_8: guard -> controlled delivery package                     PENDING
CHAIN_9: assisted entrypoint -> real client pilot                  PENDING
CHAIN_10: assisted product -> autonomous guarded SaaS re-entry     PENDING
```

## 9. Próximo paso exacto

Antes de escribir más código:

```text
1. Audit guard focal del entrypoint candidate.
2. Commit/push selectivo del entrypoint candidate.
3. Working tree clean.
```

Luego abrir:

```text
SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1
```

## 10. Veredicto final

```text
ROADMAP_CREATED
NEXT_SAFE_FRONT_AFTER_ENTRYPOINT_COMMIT:
SERVICE_1_PATHOLOGY_TO_ALLOWED_COMPUTATION_CANDIDATE_V1
```
