# PymIA — autoridad documental actual

Esta carpeta contiene la documentación rectora vigente. **No todo archivo presente en `docs/current/` gobierna por existir:** solo gobiernan los documentos enumerados en este índice.

## Jerarquía de verdad

1. Código físico y tests verdes.
2. `AGENTS.md` y `ARCHITECTURE_GUARDRAILS.md`.
3. Los documentos rectores listados aquí.
4. Evidencia técnica citada explícitamente por un documento rector.

La memoria conversacional, la landing, los pilotos históricos, los roadmaps vencidos y cualquier documentación legacy no autorizan arquitectura ni código salvo cita explícita desde esta carpeta.

## Documentos rectores

- `docs/current/ARCHITECTURE_BOUNDARY.md` — separación entre dueño, capa conversacional y PymIA computacional.
- `docs/current/PRODUCT_VISION.md` — visión del producto sin abrir autoridad runtime paralela.
- `docs/current/SERVICE_1_STATUS.md` — estado verificable actual.
- `docs/current/SERVICE_1_CANONICAL_AXIS.md` — raíz, recorrido y límites de Servicio 1.
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — invariantes de autoridad productiva, soporte, promoción y límites post-Stage-2 de Servicio 1.
- `docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` — mapa de la arquitectura actual por planos: producto, plataforma/soporte y capacidades todavía no integradas.
- `docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md` — cierre verificable del MVP determinístico asistido.
- `docs/current/SERVICE_1_OPERABILITY_PACKET.md` — runbook operativo vigente.
- `docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md` — método permanente del recorrido determinístico y del control enterprise de cambios.
- `docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md` — estado operativo recuperable de Servicio 1.
- `docs/current/ACTIVE_ROADMAP.md` — roadmap activo post-Stage-2 y próximo frente autorizado.
- `docs/current/SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1.md` — checkpoint vigente del carril SaaS acotado.
- `docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md` — reconciliación documental del estado actual de Servicio 1.
- `docs/current/SERVICE_1_CONTROLLED_PRODUCT_READINESS_CORPUS_V1.md` — evidencia del corpus físico de readiness.
- `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` — cierre del carril XLSX-first con límites explícitos.
- `docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` — evidencia acotada del runtime bridge.
- `docs/current/SERVICE_1_POST_P8_EXECUTION_BOUNDARY_AND_LEGACY_PROJECTIONS_AUDIT_V1.md` — auditoría de convergencia post-P8.
- `docs/current/WEB_INTAKE_ROOT_ALIGNMENT_V1.md` — alineación de la frontera web con la raíz canónica.
- `docs/current/SAAS_AUTONOMY_TARGET.md` — objetivo de autonomía sólo como frente posterior a certificación.
- `docs/current/SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md` — serie controlada oficial basada en `prueba_excels/`.
- `docs/current/SERVICE_1_FIRST_OPERATORLESS_CASE.md` — primer caso operatorless certificado por CLI oficial.
- `docs/current/SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md` — siguiente capacidad autorizada para conexión productiva.
- `docs/current/SERVICE_1_RECONCILIATION_ENGINEERING_STATE_V1.md` — checkpoint técnico de conciliación existente, hallazgos del matcher, límites y próximo incremento; no autoriza promoción productiva por sí mismo.

## Política de eliminación

La documentación obsoleta, duplicada, contradictoria o sustituida se elimina físicamente del árbol activo. Git conserva la trazabilidad histórica.

Los documentos de Hermes/Conversa, `PymIA-Live`, pilots comerciales viejos, staging migrado y artefactos arqueológicos no son autoridad runtime.

## Servicio 1

La autoridad operativa está en:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
docs/service_1_module_disposition.v1.json
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/ACTIVE_ROADMAP.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
```

La carpeta `landing/` no gobierna Servicio 1.

## Evidencia de pilotos registrada

Los siguientes documentos registran ejecuciones observadas. Son evidencia de la serie y no autorizan por sí mismos nuevas capacidades, fórmulas, tools ni cambios de arquitectura:

- `SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md`
- `SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md`
- `SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md`
- `SERVICE_1_PILOT_006_TALLER_MECANICO.md`
- `SERVICE_1_PILOT_007_CONSTRUCTORA.md`
- `SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md`

## Fronteras explícitas

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
```
