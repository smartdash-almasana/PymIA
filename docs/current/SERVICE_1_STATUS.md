# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-17

**Baseline funcional comprometida:** `4dc4bf3`

**Última regresión completa observada:** `1599 passed` en PowerShell local, reportada por el usuario antes del commit `203730c`.

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

## Primer caso sin intermediario obligatorio

```text
ESTADO: PASS
CICLO: CYCLE_031_RUN_FIRST_OPERATORLESS_SERVICE_1_CASE
CLI: python -m pymia.cli.service_1_product
FIXTURE: prueba_excels/cafeteria_abc.xlsx
SHEET: Ventas
PRIMER PASE: NEEDS_OWNER_CONFIRMATION
SEGUNDO PASE: PRODUCT_PIPELINE_READY
TOOL EJECUTADA: precio_margen_basico
SALIDA XLSX: first_aid_001_precio_margen_basico.xlsx
```

La evidencia rectora está en:

```text
docs/current/SERVICE_1_FIRST_OPERATORLESS_CASE.md
docs/service_1_first_operatorless_case.v1.json
tests/smartpyme/test_service_1_first_operatorless_case_v1.py
```

## Serie de pilotos controlados

```text
SERIE: ACTIVE
FUENTE: prueba_excels/
DOCUMENTO RECTOR: docs/current/SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md
CASOS REGISTRADOS: 7
PASS: S1-PILOT-001, 003, 004, 006, 007
NEXT: S1-PILOT-008
PLANNED_AFTER_008: S1-PILOT-005
GUARDA ANTI-DERIVA: simple_bem_test.xlsx permanece excluido aunque tenga headers válidos.
```

La serie prueba generalización del recorrido canónico sobre distintos vocabularios PyME. No prueba por sí misma diagnóstico integral por rubro ni diversidad completa de tools.

## Pilotos cerrados

### S1-PILOT-003 — textil compleja

```text
Estado: PASS
Archivo: prueba_excels/pyme_textil_compleja.xlsx
Sheet: VENTAS
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas semánticas: 2
Segundo pase: PRODUCT_PIPELINE_READY
Tool ejecutada: precio_margen_basico, explícita por tool_requests
Salida: first_aid_001_precio_margen_basico.xlsx
Límite: no prueba diagnóstico textil completo ni selección automática de tool.
```

### S1-PILOT-004 — distribuidora mayorista

```text
Estado: PASS
Archivo: prueba_excels/distribuidora_mayorista_compleja.xlsx
Sheet: OPERACION
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas semánticas: 3
Segundo pase: PRODUCT_PIPELINE_READY
Tool ejecutada: precio_margen_basico, explícita por tool_requests
Límite: no prueba rentabilidad integral de ruta, SKU o cliente.
```

### S1-PILOT-006 — taller mecánico

```text
Estado: PASS
Archivo: prueba_excels/taller_mecanico_lubricar_srl.xlsx
Sheet: ORDENES_TRABAJO
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas semánticas: 9
Segundo pase: PRODUCT_PIPELINE_READY
Tool ejecutada explícitamente: precio_margen_basico
Límite: no declara diagnóstico integral de taller, stock, clientes ni repuestos.
```

### S1-PILOT-007 — constructora

```text
Estado: PASS
Archivo: prueba_excels/constructora_nueva_era_srl.xlsx
Sheet: OBRAS
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas semánticas: 16
Segundo pase: PRODUCT_PIPELINE_READY
Tool ejecutada explícitamente: precio_margen_basico
Límite: no declara diagnóstico integral de obra.
```

## Próximo paso autorizado

```text
CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA
fixture: prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
sheet primaria: ventas
modo: confirmación del dueño + tool request explícito
prohibido: agregar fórmulas, seleccionar tools automáticamente o declarar diagnóstico textil integral
```
