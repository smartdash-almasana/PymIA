# Servicio 1 — architecture lock

**Status:** `ACTIVE`  
**Cycle:** `CYCLE_018_ARCHITECTURE_LOCK`  
**Locked on:** `2026-07-16`

## Software objetivo

Servicio 1 es un microservicio determinístico para evidencia Excel de PyMEs. Lee archivos reales, conserva evidencia estructural, pregunta al dueño cuando el significado operativo no está cerrado, construye estado canónico, aplica gates determinísticos, ejecuta sólo tools explícitamente autorizadas y produce archivos trazables.

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

## Soporte retenido

Quedan como soporte, no como raíces productivas:

```text
service_1_web_column_confirmation_intake_boundary_v1
service_1_owner_confirmation_to_canonical_ingestion_output_v1
service_1_xlsx_delivery_v1
service_1_accounting_contracts_v1
```

`service_1_xlsx_runtime_bridge_v1` queda como soporte transicional. No es entrada oficial, no es raíz productiva y no autoriza una cadena soberana.

## Legacy eliminable

```text
pymia/cli/service_1_operator.py
```

Este CLI y su cluster de reentry quedan como candidatos de eliminación/absorción por cluster completo. No se deben seguir extendiendo.

## Runtime legacy congelado

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_real_client_xlsx_first_pilot_pack_v1
pathology/anamnesis stack
controlled computation legacy stack
```

Este bloque no gobierna el producto. Sólo puede ser eliminado, absorbido o reclasificado por decisión explícita de cluster.

## Laboratorio congelado

```text
excel_treatment_lab_v1
exceland_bridge_v1
```

No gobiernan Servicio 1. Pueden quedar como laboratorio congelado o ser removidos en ciclos posteriores; no pueden transformarse en producto por acumulación de referencias.

## Reglas de bloqueo

- No nueva raíz productiva fuera de `service_1_product_pipeline_v1`.
- No nueva entrada oficial fuera de `pymia/cli/service_1_product.py`.
- No borrado individual de módulos congelados que pertenezcan a clusters vivos.
- No autorización de runtime, diagnóstico, delivery o tool selection desde soporte transicional.
- Un documento no listado en `docs/current/README.md` no tiene autoridad arquitectónica sobre Servicio 1.

## Evidencia verificable

```text
docs/service_1_architecture_lock.v1.json
tests/smartpyme/test_service_1_architecture_lock_v1.py
docs/service_1_module_disposition.v1.json
```
