# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-20

**Última regresión completa observada:** `1644 passed in 175.30s`, ejecutada por el usuario en PowerShell local.

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
LIQ_001: CÁLCULO + HALLAZGO ACOTADO + ENTREGA XLSX EXPLÍCITA
REN_001: EVALUADOR AISLADO DE SOPORTE, NO CONECTADO A RAÍZ
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

Se conserva como próximo ciclo operativo rector:

```text
CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA
fixture: prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
sheet primaria: ventas
modo: confirmación del dueño + tool request explícito
prohibido: agregar fórmulas, seleccionar tools automáticamente o declarar diagnóstico textil integral
```
