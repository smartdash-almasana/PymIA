# Servicio 1 — architecture lock

**Status:** `ACTIVE`  
**Cycle:** `CYCLE_018_ARCHITECTURE_LOCK`  
**Reconciled on:** `2026-07-20`

## Software objetivo

Servicio 1 es un microservicio determinístico para evidencia Excel de PyMEs. Lee archivos reales, conserva evidencia estructural, pregunta al dueño cuando el significado operativo no está cerrado, construye estado canónico, aplica gates determinísticos, ejecuta sólo capacidades o tools explícitamente autorizadas y produce archivos trazables.

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

## Entrada oficial

```text
pymia/cli/service_1_product.py
```

Esta es la única entrada de usuario autorizada para tratar a Servicio 1 como producto.

## Raíz productiva canónica

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

Sólo los módulos marcados `PRODUCTIVE` en `docs/service_1_module_disposition.v1.json` forman el núcleo productivo. La lista verificable vive en `docs/service_1_architecture_lock.v1.json` y se contrasta por test.

## Núcleo productivo relevante para LIQ_001

Además de la raíz semántica y física, forman parte de la clausura productiva:

```text
service_1_liq_001_evaluator_v1
service_1_liq_001_outcome_v1
service_1_xlsx_delivery_v1
```

`service_1_xlsx_delivery_v1` ya no es soporte externo: es dependencia productiva porque LIQ_001 lo alcanza desde la raíz para una entrega explícitamente solicitada.

## Soporte retenido

Quedan como soporte, no como raíces productivas:

```text
service_1_web_column_confirmation_intake_boundary_v1
service_1_owner_confirmation_to_canonical_ingestion_output_v1
service_1_accounting_contracts_v1
service_1_ren_001_evaluator_v1
```

`service_1_ren_001_evaluator_v1` permanece como evaluador aislado. No puede ser invocado por la raíz ni por la CLI oficial hasta un ciclo de absorción expresamente autorizado.

## Legacy eliminado

- CLI operator legacy: removido.
- Runtime bridge y pathology/anamnesis legacy: removidos.
- Exceland/laboratorio paralelo: removido.
- No queda superficie transicional runtime activa.

## Reglas de bloqueo

- No nueva raíz productiva fuera de `service_1_product_pipeline_v1`.
- No nueva entrada oficial fuera de `pymia/cli/service_1_product.py`.
- Un módulo `SUPPORT_NECESSARY` no puede ejecutar desde la raíz por existir.
- No autorización de runtime, diagnóstico, delivery o selección de tool desde soporte.
- LIQ_001 puede calcular y entregar sólo dentro de su recorrido absorbido y con delivery explícito.
- REN_001 no puede conectarse productivamente sin checkpoint documental previo.
- La memoria conversacional no autoriza arquitectura ni código.
- Un documento no listado en `docs/current/README.md` no tiene autoridad arquitectónica sobre Servicio 1.

## Evidencia verificable

```text
docs/service_1_architecture_lock.v1.json
tests/smartpyme/test_service_1_architecture_lock_v1.py
docs/service_1_module_disposition.v1.json
```

**Última regresión completa observada:** `1644 passed in 175.30s`.
