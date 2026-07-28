# Servicio 1 — eje canónico actual

## Propósito

Este documento define una sola orientación para Servicio 1. Sustituye cadenas documentales paralelas, checkpoints superados y cualquier proyección legacy que pretenda gobernar runtime.

## Definición

Servicio 1 es el laboratorio operacional de PymIA para datos y archivos de una PyME. El dueño aporta datos y significado operativo; PymIA comprende, valida, calcula y produce salidas gobernadas.

```text
La IA conversa.
PymIA gobierna.
Las tools determinísticas ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

La confirmación del dueño es evidencia de entrada y de reentry. No es permiso autónomo de ejecución ni revisión posterior obligatoria.

## Única raíz productiva

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
```

No existe segunda raíz productiva autorizada.

## Secuencia canónica

```text
P0 intake
→ P1 canonical XLSX ingestion
→ P2 profiling / physical evidence
→ P3 semantic hypothesis
→ P4 contextual evidence
→ P5 OwnerConfirmationEvent
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ P9 deterministic execution
→ P10 QA / delivery
```

## Estado actual

```text
STAGE2 = CLOSED_PASS
CURRENT_ACTIVE_FRONT = CONTROLLED_PRODUCT_READINESS_CORPUS
NEXT_AUTHORIZED_ACTION = CAPABILITY_PHYSICAL_COVERAGE_GATE_V1
SAAS_RUNTIME = NOT_AUTHORIZED
AUTONOMOUS_DELIVERY = NOT_AUTHORIZED
```

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector y normalizador XLSX canónico.
- Ninguna respuesta libre desbloquea un rol semántico desconocido.
- `unknown` permanece bloqueado hasta recibir una opción canónica o exclusión explícita.
- La confirmación del dueño prevalece sobre hipótesis secundarias, pero no reemplaza P7/P8.
- Una relación de catálogo no autoriza runtime por existir.
- La capa conversacional no selecciona tools, no diagnostica y no altera gates.
- No se crean nuevas cadenas soberanas alrededor de piezas existentes.
- No LLM como autoridad de cálculo, diagnóstico o estado.
- No documentación histórica, Hermes, Conversa, `PymIA-Live` ni landings como autoridad runtime.

## Próximo frente autorizado

```text
CAPABILITY_PHYSICAL_COVERAGE_GATE_V1
```

La autonomía SaaS sólo puede reconsiderarse después de certificación productiva explícita.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/service_1_module_disposition.v1.json
```
