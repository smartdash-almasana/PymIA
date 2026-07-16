# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-16

**Baseline funcional comprometida:** `4dc4bf3`

**Regresión posterior al saneamiento estructural:** `1558 passed` en Python 3.11 limpio

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
XLSX REAL → CONFIRMACIÓN → SEMÁNTICA → PLAN/EJECUCIÓN EXPLÍCITA: PROBADO
EXPERIMENTAL_FROZEN: 0
OPERATOR LEGACY: ELIMINADO
RUNTIME LEGACY: ELIMINADO
EXCELAND/LAB LEGACY: ELIMINADO
SERVICIO 1 EN TODA SU AMPLITUD FUTURA: NO
```

## Alcance completo declarado

Servicio 1 está completo como MVP para:

- leer XLSX real por la CLI oficial;
- preguntar al dueño por columnas cuando falta confirmación;
- construir salida canónica de ingesta;
- pasar por comprensión semántica determinística;
- pedir confirmación semántica cuando la evidencia no alcanza;
- rechazar reentry semántico de texto libre;
- ejecutar una tool explícitamente solicitada y permitida;
- construir plan computable gobernado para `sold_vs_collected_gap` / `LIQ_001_vendido_cobrado` sin ejecución;
- mantener flags de autorización en falso salvo autorización explícita futura;
- producir salida trazable.

## Evidencia rectora

```text
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/service_1_product_completion_gate.v1.json
tests/smartpyme/test_service_1_product_completion_gate_v1.py
tests/cli/test_service_1_product_cli_v1.py
```

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que todas las patologías/fórmulas futuras estén conectadas.
- `LIQ_001_vendido_cobrado` queda como plan computable, no ejecución automática.
- No existe selección automática de tool desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto, no un gap.


## Operabilidad MVP

```text
OPERABILITY PACKET: ACTIVO
COMANDO OFICIAL: python -m pymia.cli.service_1_product
RUNBOOK: docs/current/SERVICE_1_OPERABILITY_PACKET.md
PAQUETE VERIFICABLE: docs/service_1_operability_packet.v1.json
```
