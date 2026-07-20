# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-20

**Última regresión completa observada:** `1644 passed in 120s`, ejecutada por el usuario en PowerShell local.

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
LIQ_001: CÁLCULO + HALLAZGO ACOTADO + ENTREGA XLSX EXPLÍCITA
REN_001: EVALUADOR AISLADO DE SOPORTE, NO CONECTADO A RAÍZ
S1-PILOT-008 TEXTIL COMPLETA: PASS
EXPERIMENTAL_FROZEN: 0
OPERATOR LEGACY: ELIMINADO
RUNTIME LEGACY: ELIMINADO
EXCELAND/LAB LEGACY: ELIMINADO
SERVICIO 1 EN TODA SU AMPLITUD FUTURA: NO
```

## Alcance certificado

Servicio 1 está certificado para:

- leer XLSX real por la CLI oficial;
- preguntar al dueño por columnas cuando falta confirmación;
- construir salida canónica de ingesta;
- pasar por comprensión semántica determinística;
- pedir confirmación semántica cuando la evidencia no alcanza;
- rechazar reentrada semántica de texto libre;
- ejecutar una tool explícitamente solicitada y permitida;
- construir y ejecutar el cálculo gobernado `sold_vs_collected_gap` / `LIQ_001_vendido_cobrado` cuando existen filas normalizadas completas y bindings confirmados;
- producir para LIQ_001 un hallazgo acotado y tratamiento determinístico sin atribuir causa;
- generar el XLSX de LIQ_001 sólo ante solicitud explícita `--deliver-result`;
- mantener en falso `runtime_authorized`, `tool_execution_authorized`, `product_ready`, `delivery_authorized` y `diagnosis_generated`;
- producir salida trazable.

## Estado de LIQ_001

```text
XLSX real
→ confirmación del dueño
→ plan gobernado
→ agregación determinística de filas
→ cálculo vendido vs cobrado
→ hallazgo acotado
→ tratamiento determinístico
→ entrega XLSX sólo con --deliver-result
```

LIQ_001 no afirma morosidad, fraude, incobrabilidad, error contable ni responsabilidad causal sin evidencia adicional.

## Estado de REN_001

`service_1_ren_001_evaluator_v1.py` existe y está probado como evaluador determinístico aislado para:

```text
margen monetario = sale_price - costs - taxes
margen porcentual = margen monetario / sale_price * 100
```

Su clasificación actual en `docs/service_1_module_disposition.v1.json` es `SUPPORT_NECESSARY`.

Por lo tanto:

- no forma parte de la clausura productiva;
- no está conectado a la CLI oficial;
- no genera hallazgo, tratamiento ni XLSX;
- no autoriza ampliar la raíz sin un ciclo documental explícito posterior.

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

## Primer caso sin intermediario obligatorio

```text
PRIMER CASO OPERATORLESS: PASS
CYCLE_031_RUN_FIRST_OPERATORLESS_SERVICE_1_CASE
CLI: python -m pymia.cli.service_1_product
FIXTURE: prueba_excels/cafeteria_abc.xlsx
SHEET: Ventas
PRIMER PASE: NEEDS_OWNER_CONFIRMATION
SEGUNDO PASE: PRODUCT_PIPELINE_READY
TOOL EJECUTADA: precio_margen_basico
SALIDA XLSX: first_aid_001_precio_margen_basico.xlsx
```

La evidencia rectora permanece en:

```text
docs/current/SERVICE_1_FIRST_OPERATORLESS_CASE.md
docs/service_1_first_operatorless_case.v1.json
tests/smartpyme/test_service_1_first_operatorless_case_v1.py
```

## Serie de pilotos controlados

```text
SERIE: ACTIVE
FUENTE: prueba_excels/
CASOS PASS: S1-PILOT-001, 003, 004, 006, 007, 008
NEXT: S1-PILOT-005
```

### S1-PILOT-008 — textil completa

```text
Estado: PASS
Ciclo: CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA
Archivo: prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
Sheet: ventas
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas al dueño: 4
Columnas: cliente, descuento_pct, medio_cobro, plazo_cobro_dias
Segundo pase: PRODUCT_PIPELINE_READY
Bindings confirmados: true
Tool ejecutada explícitamente: precio_margen_basico
Salida: first_aid_001_precio_margen_basico.xlsx
```

Límite: prueba el recorrido canónico sobre un workbook textil completo multihoja; no declara diagnóstico textil integral, selección automática de tool ni nuevas fórmulas. `REN_001` permanece fuera de la raíz.

Evidencia:

```text
docs/current/SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md
docs/service_1_pilot_008_textil_completa.v1.json
tests/smartpyme/test_service_1_pilot_008_textil_completa_v1.py
```

## Evidencia rectora

```text
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/service_1_product_completion_gate.v1.json
docs/service_1_architecture_lock.v1.json
docs/service_1_module_disposition.v1.json
tests/smartpyme/test_service_1_product_completion_gate_v1.py
tests/smartpyme/test_service_1_architecture_lock_v1.py
```

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que todas las patologías y fórmulas estén conectadas.
- No existe selección automática de tool desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto.
- REN_001 permanece fuera de la raíz productiva hasta autorización documental explícita.

## Próximo paso autorizado

```text
CYCLE_038_RUN_S1_PILOT_005_FABRICA_INDUSTRIAL
fixture: prueba_excels/fabrica_industrial_compleja.xlsx
sheet primaria: PRODUCCION
modo: confirmación del dueño + tool request explícito
prohibido: agregar fórmulas, seleccionar tools automáticamente o declarar diagnóstico industrial, scrap u OEE
```
