# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-20

**Última regresión completa observada:** `1694 passed, 0 failed`, ejecutada por el asistente en local después del cierre de `CYCLE_043`.

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
LIQ_001: CÁLCULO + HALLAZGO ACOTADO + ENTREGA XLSX EXPLÍCITA
REN_001: CÁLCULO + HALLAZGO ACOTADO; ENTREGA XLSX NO AUTORIZADA
LIQ_002: CÁLCULO + HALLAZGO ACOTADO; ENTREGA XLSX NO AUTORIZADA
PYME_011: CÁLCULO + HALLAZGO ACOTADO; ENTREGA XLSX NO AUTORIZADA
CYCLE_040_CONNECT_REN_001_TO_PRODUCTIVE_ROOT: CLOSED_PASS
CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP: DECIDED
CYCLE_042_CONNECT_LIQ_002_TO_PRODUCTIVE_ROOT: CLOSED_PASS
CYCLE_043_CONNECT_PYME_011_TO_PRODUCTIVE_ROOT: CLOSED_PASS
PATOLOGÍAS PRODUCTIVAS ACTUALES: 4 DE 12
SIGUIENTE PATOLOGÍA: PYME_013
SERIE CONTROLADA PLANIFICADA: COMPLETA
SCRAP/OEE: NO SOPORTADO
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
- construir y ejecutar `sold_vs_collected_gap` / `LIQ_001_vendido_cobrado` con filas normalizadas completas y bindings confirmados;
- producir para `LIQ_001` un hallazgo acotado, tratamiento determinístico y XLSX sólo con `--deliver-result`;
- construir y ejecutar `net_margin_real` / `REN_001_margen_neto_real` ante solicitud explícita, evidencia normalizada completa y bindings confirmados;
- calcular para `REN_001` margen monetario, margen porcentual y egresos totales;
- clasificar `REN_001` como `POSITIVE_MARGIN`, `BREAK_EVEN` o `NEGATIVE_MARGIN`;
- producir para `REN_001` un hallazgo acotado y tratamiento determinístico sin atribución causal;
- construir y ejecutar `projected_closing_cash_balance` / `LIQ_002_saldo_final_proyectado` ante solicitud explícita, evidencia normalizada completa y bindings confirmados para CASH_PROJECTION family;
- calcular para `LIQ_002` saldo final proyectado;
- clasificar `LIQ_002` como `POSITIVE_PROJECTED_BALANCE`, `ZERO_PROJECTED_BALANCE` o `NEGATIVE_PROJECTED_BALANCE`;
- producir para `LIQ_002` un hallazgo acotado y tratamiento determinístico sin atribución causal;
- construir y ejecutar `dso` / `PYME_011_dso` ante solicitud explícita, evidencia normalizada completa y bindings confirmados para RECEIVABLES_DSO family;
- calcular para `PYME_011` Days Sales Outstanding;
- clasificar `PYME_011` como `DSO_WITHIN_PERIOD`, `DSO_EQUALS_PERIOD` o `DSO_EXCEEDS_PERIOD`;
- producir para `PYME_011` un hallazgo acotado y tratamiento determinístico sin atribución causal;
- mantener en falso `runtime_authorized`, `tool_execution_authorized`, `product_ready`, `delivery_authorized` y `diagnosis_generated`;
- producir salida trazable.

## Capacidades productivas actuales

### LIQ_001

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

`LIQ_001` no afirma morosidad, fraude, incobrabilidad, error contable ni responsabilidad causal sin evidencia adicional.

### REN_001

```text
XLSX real
→ confirmación del dueño
→ solicitud explícita net_margin_real
→ plan gobernado
→ resolución exacta de sale_price, costs y taxes
→ agregación determinística de filas normalizadas
→ margen monetario y porcentual
→ clasificación acotada
→ hallazgo y tratamiento determinísticos
```

Reglas y límites:

- la capacidad se activa únicamente ante request explícito `net_margin_real`;
- requiere plan listo y bindings confirmados;
- cada variable debe resolver determinísticamente desde evidencia normalizada;
- no usa muestras ni selección automática;
- no atribuye causas, responsabilidad, fraude, error de precios ni error contable;
- no genera diagnóstico causal;
- la entrega XLSX de `REN_001` permanece bloqueada.

### LIQ_002

```text
XLSX real
→ confirmación del dueño
→ plan gobernado (CASH_PROJECTION family)
→ agregación determinística de filas
→ cálculo initial_balance + expected_collections - expected_payments
→ clasificación acotada
→ hallazgo y tratamiento determinísticos
```

`LIQ_002` no afirma iliquidez, déficit estructural, error de caja, fraude ni responsabilidad causal sin evidencia adicional.

Reglas y límites:

- la capacidad se activa únicamente ante request explícito `projected_closing_cash_balance`;
- requiere plan listo y bindings confirmados para CASH_PROJECTION family;
- cada variable debe resolver determinísticamente desde evidencia normalizada;
- no usa muestras ni selección automática;
- no atribuye causas, responsabilidad, fraude, error de caja ni proyección contable;
- no genera diagnóstico causal;
- la entrega XLSX de `LIQ_002` permanece bloqueada.

### PYME_011

```text
XLSX real
→ confirmación del dueño
→ plan gobernado (RECEIVABLES_DSO family)
→ agregación determinística de filas
→ cálculo accounts_receivable / sales * days
→ clasificación acotada
→ hallazgo y tratamiento determinísticos
```

`PYME_011` no afirma morosidad, riesgo crediticio, error de cobranzas, fraude ni responsabilidad causal sin evidencia adicional.

Reglas y límites:

- la capacidad se activa únicamente ante request explícito `dso`;
- requiere plan listo y bindings confirmados para RECEIVABLES_DSO family;
- cada variable debe resolver determinísticamente desde evidencia normalizada;
- no usa muestras ni selección automática;
- no atribuye causas, responsabilidad, fraude, error de cobranzas ni diagnóstico contable;
- no genera diagnóstico causal;
- la entrega XLSX de `PYME_011` permanece bloqueada.

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe una segunda raíz para las capacidades productivas.

## Serie de pilotos controlados

```text
SERIE: COMPLETE
FUENTE: prueba_excels/
CASOS PASS: S1-PILOT-001, 003, 004, 005, 006, 007, 008
PILOTOS PLANIFICADOS PENDIENTES: 0
```

El Piloto 005 demostró el recorrido canónico sobre evidencia industrial, pero no autorizó diagnóstico industrial, scrap, OEE, eficiencia de máquina, paradas o pérdidas productivas.

## Hoja de ruta de doce patologías

```text
CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP: DECIDED
BASE PRODUCTIVA: LIQ_001, REN_001, LIQ_002, PYME_011
ORDEN RESTANTE:
5. PYME_013
6. INV_001
7. INV_002
8. PYME_024
9. PYME_033
10. REN_002
11. PYME_027
12. PYME_026
```

La meta de doce patologías no se satisface por presencia en catálogo. Cada una deberá cerrar contrato, fórmula, evidencia mínima, dominio matemático, evaluación, hallazgo, tratamiento, integración, decisión de entrega, tests, ejecución observada y actualización de guards.

Reglas:

- una patología por ciclo funcional;
- solicitud explícita de capacidad;
- sin selección automática;
- sin diagnóstico causal;
- sin implementación masiva de las diez patologías;
- scrap/OEE permanece fuera de esta hoja de ruta.

Evidencia:

```text
docs/current/SERVICE_1_12_PRODUCTIVE_PATHOLOGY_ROADMAP.md
docs/service_1_12_productive_pathology_roadmap.v1.json
tests/smartpyme/test_service_1_12_productive_pathology_roadmap_v1.py
```

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que las doce patologías ya estén conectadas.
- No existe selección automática de tool o capacidad desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto.
- `REN_001` está conectado, pero su entrega XLSX no está autorizada.
- Scrap y OEE no son capacidades soportadas actualmente.
- Las fórmulas contables o financieras con supuestos exigen evidencia y convenciones explícitas.

## Próximo ciclo autorizado

```text
CYCLE_044_CONNECT_PYME_013_TO_PRODUCTIVE_ROOT
```

Alcance:

```text
Conectar exclusivamente PYME_013 (DSO-DPO gap).
Requerir dso y dpo.
Definir dominio matemático, clasificaciones, hallazgo y tratamiento acotados.
Usar la raíz productiva única y solicitud explícita de capacidad.
No implementar INV_001 ni otra patología en paralelo.
No autorizar entrega XLSX hasta decisión explícita del ciclo.
No introducir selección automática, causalidad ni runtime autónomo.
```
