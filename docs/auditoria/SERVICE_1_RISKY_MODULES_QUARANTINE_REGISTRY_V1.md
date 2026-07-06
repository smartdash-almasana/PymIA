# SERVICE_1_RISKY_MODULES_QUARANTINE_REGISTRY_V1

## Estado

```text
STATUS: ACTIVE_AUDIT_MEMORY
PURPOSE: persistir clasificación de módulos riesgosos / futuros / legacy para evitar deriva en Servicio 1
DATE: 2026-07-06
SOURCE: auditoría local MCP sobre PymIA-Live/pymia/smartpyme
```

Este documento es memoria versionable del repo. No es roadmap de producto. No autoriza implementación. No autoriza runtime nuevo.

---

## Regla madre

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

Servicio 1 actual se desarrolla sobre flujo controlado:

```text
XLSX / evidencia
→ question_bundle
→ respuesta del dueño
→ owner_reentry_bridge
→ tools determinísticas
→ case folder
→ product_gate
→ manifest
→ operator_packet
```

No abrir por inercia:

```text
LLM runtime
chatbot libre
LangGraph
FastAPI
Telegram
OCR
parser PDF
API banco
API Mercado Pago
SaaS real
Servicio 2
entrega autónoma
```

---

## Categorías de cuarentena

```text
ACTIVE
SANDBOX_ONLY
FUTURE_BOUNDARY
FROZEN_LEGACY
OUT_OF_SCOPE
SEMANTIC_DEBT
```

Definiciones:

- `ACTIVE`: puede participar en Servicio 1 actual.
- `SANDBOX_ONLY`: puede ejecutarse como ensayo controlado, no producción ni entrega final.
- `FUTURE_BOUNDARY`: contrato/candidato útil para una etapa futura, no conectar ahora.
- `FROZEN_LEGACY`: conservar por trazabilidad/tests, no extender sin decisión explícita.
- `OUT_OF_SCOPE`: fuera del ciclo actual de Servicio 1.
- `SEMANTIC_DEBT`: término o nombre que contamina lectura, aunque el código pueda ser inocuo.

---

## Clasificación por familia riesgosa

| Familia | Clasificación | Decisión | Motivo |
|---|---:|---|---|
| `autonomous` | `FROZEN_LEGACY` / `FUTURE_BOUNDARY` | No conectar al flujo actual | Nombre contaminante; algunos módulos llaman pipeline bajo flags. |
| `assisted` | `SEMANTIC_DEBT` | No seguir usando el término | Ambiguo; reemplazar por owner evidence / human review / controlled delivery. |
| `operator` | Mixto | Conservar sólo artefactos técnicos | `operator_packet` y `operator_notes` son sanos; `operator_supervision_candidate` queda congelado. |
| `llm_guarded` | `FUTURE_BOUNDARY` | Conservar sin conectar | Gate puro; todos los flags LLM/runtime/API quedan false. |
| `web_test` | `SANDBOX_ONLY` | Conservar como registry de ensayo | No es producto web; bloquea real_client_delivery y rutas peligrosas. |
| `saas` | `FUTURE_BOUNDARY` | Congelar | Candidatos puros; no API, no upload, no job real. |
| `service_2` | `OUT_OF_SCOPE` | No tocar en Servicio 1 | Puede tener lógica útil, pero contamina foco actual. |

---

## Archivos leídos / relevantes

### `autonomous`

```text
PymIA-Live/pymia/smartpyme/service_1_autonomous_pipeline_runner_v1.py
PymIA-Live/pymia/smartpyme/service_1_autonomous_delivery_release_gate_v1.py
```

Decisión:

```text
service_1_autonomous_delivery_release_gate_v1.py:
  clasificación: FUTURE_BOUNDARY
  conservar: sí
  conectar ahora: no
  razón: produce release candidate no publicable; mantiene flags de autorización false.

service_1_autonomous_pipeline_runner_v1.py:
  clasificación: FROZEN_LEGACY
  conservar: sí, por trazabilidad/tests
  conectar ahora: no
  razón: llama run_service_1_pipeline_v1 si recibe autorización previa; el nombre y la semántica son peligrosos para el ciclo actual.
```

### `assisted`

Referencias detectadas:

```text
S1_FULL_ASSISTED_V1_HARDENING
use_as_assisted_lab_component
QA Delivery Gate for assisted delivery
service_2_reconciliation_assisted_review_block_v1.py
service_2_reconciliation_assisted_review_delivery_packet_v1.py
```

Decisión:

```text
clasificación: SEMANTIC_DEBT
acción: no usar más en nuevos módulos/docs de Servicio 1
reemplazos: owner evidence, owner review, human review, controlled delivery, operator notes
```

### `operator`

Uso sano:

```text
operator_packet.json
operator_notes
operator_summary
operator_or_accountant
```

Uso riesgoso:

```text
operator_supervision_candidate
SUPERVISED_CLI_OPERATOR_FLOW
controlled client case operator supervision
```

Decisión:

```text
operator_packet / operator_notes:
  clasificación: ACTIVE
  conservar: sí

operator_supervision_candidate / controlled operator supervision:
  clasificación: FROZEN_LEGACY
  extender: no sin decisión explícita
```

### `llm_guarded`

Archivo:

```text
PymIA-Live/pymia/smartpyme/service_1_llm_guarded_response_gate_v1.py
```

Decisión:

```text
clasificación: FUTURE_BOUNDARY
conservar: sí
conectar ahora: no
razón: gate puro, no llama LLM/API/tools/pipeline/storage/runtime.
```

Flags obligatorios:

```text
llm_authorized = false
pydantic_ai_authorized = false
prompt_runtime_authorized = false
chatbot_authorized = false
tool_authorized = false
pipeline_authorized = false
runner_authorized = false
mutation_authorized = false
runtime_authorized = false
api_exposed = false
```

### `web_test`

Archivo:

```text
PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
```

Decisión:

```text
clasificación: SANDBOX_ONLY
conservar: sí
usar como producto web: no
```

Rutas permitidas sólo como ensayo:

```text
excel_treatment_lab_sandbox
invoice_collection_matching_sandbox
bank_reconciliation_sandbox
accounting_workpaper_draft_sandbox
first_aid_synthetic_delivery_rehearsal
```

Rutas bloqueadas:

```text
mercado_pago_reconciliation
servicio_2_diagnostic
ocr_ingestion
api_ingestion
chatbot_autonomo
real_client_delivery
final_accounting_review
```

### `saas`

Archivo leído:

```text
PymIA-Live/pymia/smartpyme/service_1_saas_case_session_model_v1.py
```

Familia relacionada:

```text
service_1_saas_file_intake_api_v1.py
service_1_saas_job_orchestration_v1.py
service_1_saas_job_to_pipeline_request_adapter_v1.py
service_1_real_auth_boundary_contract_v1.py
service_1_real_endpoint_api_boundary_contract_v1.py
service_1_real_storage_upload_boundary_contract_v1.py
service_1_real_worker_runtime_boundary_contract_v1.py
```

Decisión:

```text
clasificación: FUTURE_BOUNDARY
conservar: sí
conectar ahora: no
razón: candidatos puros; declaran sin API, sin upload, sin job real, sin ejecución.
```

Flags obligatorios:

```text
runtime_authorized = false
job_authorized = false
file_upload_authorized = false
api_exposed = false
```

### `service_2`

Archivo leído parcialmente:

```text
PymIA-Live/pymia/smartpyme/service_2_reconciliation_match_candidates_v1.py
```

Decisión:

```text
clasificación: OUT_OF_SCOPE
conservar: sí
usar en Servicio 1 actual: no
```

Límites declarados:

```text
No conciliación definitiva.
No certifica saldo bancario real.
No reemplaza revisión humana.
No detecta fraude.
No produce cierre contable o fiscal.
```

---

## Decisiones persistidas

```text
1. No borrar todavía módulos riesgosos.
2. No extender módulos autonomous/saas/service_2 en Servicio 1 actual.
3. No usar más el término assisted para nuevos artefactos de Servicio 1.
4. Mantener operator_packet/operator_notes como artefactos técnicos sanos.
5. Congelar operator_supervision_candidate como legacy controlado.
6. Mantener llm_guarded como future boundary desconectado.
7. Mantener web_test como sandbox-only, no producto web.
8. Mantener service_2 fuera de alcance para el ciclo actual.
```

---

## Próximo patch recomendado

```text
SERVICE_1_MICROSERVICE_REGISTRY_MATURITY_PATCH_V1
```

Objetivo:

```text
Actualizar service_1_microservice_registry_contract_v1.py para reflejar madurez real:
- RUNTIME_READY
- RUNTIME_READY_IN_CLI
- DELIVERY_READY_DRAFT
- SANDBOX_READY
- CONTRACT_ONLY
- FUTURE_BOUNDARY
- FROZEN_LEGACY
- OUT_OF_SCOPE
```

No debe:

```text
- conectar autonomous runner
- abrir SaaS runtime
- abrir web runtime
- abrir LLM runtime
- mezclar Servicio 2
- prometer entrega autónoma
```

---

## Regla de consulta futura

Antes de tocar cualquier módulo que contenga estos términos:

```text
autonomous
assisted
operator_supervision
llm_guarded
web_test
saas
service_2
```

leer este documento y responder:

```text
MODULE_QUARANTINE_STATUS:
- family:
- classification:
- allowed_action:
- forbidden_action:
- reason:
```
