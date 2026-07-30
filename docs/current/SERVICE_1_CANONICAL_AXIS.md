# Servicio 1 — eje canónico actual

**Estado:** `ACTIVE`  
**Reconciliado:** 2026-07-29

## Propósito

Este documento define una sola orientación para Servicio 1. Sustituye cadenas documentales paralelas, checkpoints superados y cualquier proyección legacy que pretenda gobernar runtime.

Servicio 1 evolucionó después del cierre de Stage 2: el repositorio incorporó fundaciones de dominio, admisión, narrativa, radiografía operacional, harness y operador fiel. Esas capas amplían la plataforma, pero no alteran la autoridad productiva salvo integración explícita y clasificación `PRODUCTIVE`.

## Definición

Servicio 1 es el laboratorio operacional determinístico de PymIA para evidencia PyME, con XLSX como fuente productiva principal actual. El dueño aporta datos y significado operativo; PymIA conserva evidencia, comprende, valida, decide computabilidad, calcula y produce salidas gobernadas.

```text
La capa conversacional conversa y pregunta.
PymIA gobierna estados y evidencia.
Las tools determinísticas calculan.
Los archivos son una forma de producto.
El dueño confirma significado durante la lectura.
```

La confirmación del dueño es evidencia de entrada y reentry. No es autorización autónoma de ejecución, diagnóstico ni delivery.

## Única raíz productiva

```text
pymia/cli/service_1_product.py
→ pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe segunda raíz productiva autorizada.

La presencia de otros flujos locales o de aplicación, incluidos `vertical_slice`, `faithful_operator`, admission, diagnostic core, narrative u operational harness, no crea autoridad productiva paralela.

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

P0–P10 expresa orden y autoridad, no una obligación de once módulos físicos.

## Separación de decisiones

```text
hipótesis
≠ evidencia
≠ confirmación del dueño
≠ aprobación semántica
≠ match de requisitos
≠ computabilidad
≠ ejecución
≠ delivery
```

En particular:

- una hipótesis de admisión no confirma semántica;
- un `confidence_score` no autoriza matching ni ejecución;
- una respuesta del dueño no elimina P6/P7/P8;
- un cálculo disponible no equivale a diagnóstico final;
- una narrativa no crea evidencia;
- un estado GREEN del harness no autoriza runtime de producto.

## Arquitectura por planos

### Plano A — producto

```text
service_1_product_pipeline_v1
+ módulos PRODUCTIVE
+ P0–P10
```

Es la única autoridad de ejecución del producto.

### Plano B — plataforma y soporte

Incluye componentes integrados que pueden asistir recepción, evidencia, dominio, presentación o medición:

```text
pymia/domain/*
pymia/pipeline/admission/v1/*
pymia/faithful_operator.py
pymia/application/vertical_pipeline.py
pymia/diagnostic_core/*
pymia/narrative/*
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Estos componentes no reemplazan la raíz productiva ni los gates P0–P10.

### Plano C — contratos y capacidades con integración acotada

La familia contable general continúa como soporte, pero la revisión asistida de conciliación ya tiene acceso controlado desde la raíz productiva:

```text
service_1_accounting_contracts_v1 = SUPPORT_NECESSARY
service_1_reconciliation_request_gate_v1 = PRODUCTIVE
service_1_reconciliation_candidate_to_assisted_review_v1 = PRODUCTIVE
service_1_reconciliation_product_request_v1 = PRODUCTIVE
service_2_reconciliation_match_candidates_v1 = matcher determinístico reutilizado
```

Esta integración sólo prepara resultados para revisión humana. No autoriza cierre contable, aceptación automática ni modificación de movimientos.

## Ejecución

La raíz canónica distingue:

```text
LIQ_001 / REN_001
→ evaluadores especializados

capacidad genérica gobernada por registry
→ CapabilityRegistry
→ GenericCapabilityEngine
```

Una nueva capacidad genérica debe incorporarse por contratos, registry, P8 y kernel; no mediante proliferación de branches por identidad en la raíz.

## Estado de clasificación Service 1

Fuente física:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado al 2026-07-29:

```text
TOTAL = 59
PRODUCTIVE = 30
SUPPORT_NECESSARY = 29
CANONICAL_PRODUCT_ROOT = service_1_product_pipeline_v1
```

`SUPPORT_NECESSARY` no significa productivo.

## Fundaciones integradas después de Stage 2

```text
039f0cd  domain model foundation
1b62053  deterministic narrative layer
05cf07b  admission pipeline foundation
bc2fabf  pipeline radiography + operational harness
c240080  removal of live-root dependency / legacy evidence bridge
9181abf  faithful operator + document parsing support
48aa4a0  documentary authority reconciliation / Hermes retirement
17e36a2  regression coverage and local tooling retention
```

Estas integraciones forman la nueva envolvente arquitectónica de PymIA alrededor de Servicio 1. Ninguna de ellas, por sí sola, crea una segunda ejecución soberana.

## Conciliación

La conciliación bancaria y Mercado Pago están integradas a Servicio 1 como preparación gobernada para revisión humana.

Principios cerrados:

```text
fecha + importe = evidencia fuerte, no identidad
referencia = evidencia, no verdad absoluta
confidence score = no autoridad
ambigüedad = estado explícito
1:N / N:1 / N:M = no resolver codiciosamente
movimientos no imputados = nunca ocultar por diferencias parciales
caso ambiguo = escalar a humano
```

El matcher existente debe madurar dentro de su módulo actual. No se crea un core paralelo.

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector/normalizador XLSX productivo canónico.
- Ninguna respuesta libre desbloquea un rol semántico desconocido.
- `unknown` permanece bloqueado hasta evidencia o elección canónica suficiente.
- La confirmación del dueño no sustituye P6/P7/P8.
- Un componente SUPPORT no ejecuta por existir.
- No LLM como autoridad de cálculo, diagnóstico, estado o computabilidad.
- No event bus, colas ni microservicios distribuidos para resolver fronteras internas actuales.
- No API productiva antes de cerrar las capacidades y contratos correspondientes.
- No documentación histórica, Hermes, Conversa, `PymIA-Live` ni landings como autoridad runtime.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
docs/service_1_module_disposition.v1.json
docs/service_1_architecture_lock.v1.json
```
