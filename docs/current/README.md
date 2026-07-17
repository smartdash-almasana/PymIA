# PymIA — autoridad documental actual

Esta carpeta contiene la documentación rectora vigente. **No todo archivo presente en `docs/current/` gobierna por existir:** solo gobiernan los documentos enumerados en este índice.

## Jerarquía de verdad

1. Código físico y tests verdes.
2. `AGENTS.md` y `ARCHITECTURE_GUARDRAILS.md`.
3. Los documentos rectores listados aquí.
4. Evidencia técnica citada explícitamente por un documento rector.

La memoria conversacional, documentos no listados, landings, pilotos, auditorías antiguas y diseños abandonados no autorizan arquitectura ni código.

## Documentos rectores

- `ARCHITECTURE_BOUNDARY.md` — separación entre dueño, capa conversacional y PymIA computacional.
- `PRODUCT_VISION.md` — visión final del producto.
- `SERVICE_1_STATUS.md` — estado verificable actual.
- `SERVICE_1_CANONICAL_AXIS.md` — raíz, recorrido y límites de Servicio 1.
- `SERVICE_1_ARCHITECTURE_LOCK.md` — superficie oficial, soporte retenido, legacy y laboratorio congelado de Servicio 1.
- `SERVICE_1_PRODUCT_COMPLETION_GATE.md` — cierre verificable del MVP determinístico asistido de Servicio 1.
- `SERVICE_1_OPERABILITY_PACKET.md` — runbook operativo del MVP de Servicio 1.
- `SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md` — método de ingeniería del recorrido determinístico.
- `SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md` — serie, orden, estados y límites de los pilotos controlados basados en `prueba_excels/`.
- `FACTORY_AND_ADN_AXIS.md` — separación metodológica de Factoría/ADN.
- `HERMES_AXIS.md` — Hermes no gobierna Servicio 1.
- `SMARTPYME_PRODUCT_AXIS.md` — separación entre memoria de producto y autoridad técnica.

## Política de eliminación

La documentación obsoleta, duplicada, contradictoria o sustituida se elimina físicamente del árbol activo. No se mueve a museo, legacy ni archivo. Git conserva la trazabilidad histórica.

Un documento no listado aquí queda sin autoridad y debe ser evaluado para eliminación en los siguientes lotes de saneamiento.

## Servicio 1

La autoridad operativa está en:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
docs/service_1_module_disposition.v1.json
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/current/SERVICE_1_OPERABILITY_PACKET.md
docs/current/SERVICE_1_FIRST_OPERATORLESS_CASE.md
docs/current/SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md
```

La carpeta `landing/` no gobierna Servicio 1.

## Evidencia de pilotos registrada

Los siguientes documentos registran ejecuciones observadas. Son evidencia de la serie y no autorizan por sí mismos nuevas capacidades, fórmulas, tools ni cambios de arquitectura:

- `SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md` — ejecución registrada del piloto textil complejo.
- `SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md` — ejecución registrada del piloto distribuidora mayorista.
- `SERVICE_1_PILOT_006_TALLER_MECANICO.md` — ejecución registrada del piloto taller mecánico.
- `SERVICE_1_PILOT_007_CONSTRUCTORA.md` — ejecución registrada del piloto constructora.
