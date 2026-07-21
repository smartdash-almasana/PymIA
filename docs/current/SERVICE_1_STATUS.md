# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-20

**Última regresión completa observada:** `1694 passed, 0 failed`, ejecutada en local después del cierre de `CYCLE_043`.

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
CYCLE_044_CONNECT_PYME_013_TO_PRODUCTIVE_ROOT: SUSPENDED_BY_ARCHITECTURAL_DECISION
PATOLOGÍAS PRODUCTIVAS ACTUALES: 4 DE 12
SIGUIENTE PATOLOGÍA FUNCIONAL: PYME_013, DIFERIDA
PRÓXIMO CICLO: CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE
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
- rechazar reentrada semántica de texto libre;
- construir planes gobernados por solicitud explícita;
- ejecutar `LIQ_001`, `REN_001`, `LIQ_002` y `PYME_011` con evidencia normalizada y bindings confirmados;
- producir clasificaciones y outcomes acotados sin atribución causal;
- mantener en falso `runtime_authorized`, `tool_execution_authorized`, `product_ready`, `delivery_authorized` y `diagnosis_generated`;
- producir salida trazable.

## Capacidades productivas actuales

| Patología | Capacidad | Entrega |
|---|---|---|
| `LIQ_001` | `sold_vs_collected_gap` | XLSX sólo con solicitud explícita |
| `REN_001` | `net_margin_real` | no autorizada |
| `LIQ_002` | `projected_closing_cash_balance` | no autorizada |
| `PYME_011` | `dso` | no autorizada |

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe una segunda raíz productiva.

## Hoja de ruta de doce patologías

```text
BASE PRODUCTIVA: LIQ_001, REN_001, LIQ_002, PYME_011
RESTANTES:
5. PYME_013
6. INV_001
7. INV_002
8. PYME_024
9. PYME_033
10. REN_002
11. PYME_027
12. PYME_026
```

`PYME_013` permanece en la hoja de ruta, pero queda diferida para ser la primera capacidad `COMPOSITE` implementada sobre el kernel genérico validado.

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que las doce patologías ya estén conectadas.
- No existe selección automática de tool o capacidad desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto.
- Scrap y OEE no son capacidades soportadas actualmente.
- Las fórmulas con supuestos exigen evidencia y convenciones explícitas.

## Próximo ciclo autorizado

```text
CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE
```

Estado del ciclo:

```text
ARCHITECTURE_DECISION_ONLY
NO_PRODUCTIVE_CODE
```

Alcance autorizado:

- inventariar duplicación entre las capacidades productivas actuales;
- definir el límite exacto del Generic Productive Capability Kernel;
- definir contratos para capacidades `ATOMIC` y `COMPOSITE`;
- definir expresión matemática segura, estrategias de agregación y resultados tipados;
- definir estados de migración y criterios de equivalencia;
- fijar `LIQ_002` y `PYME_011` como casos piloto.

Prohibiciones del ciclo:

- no implementar código productivo;
- no modificar la raíz productiva;
- no conectar `PYME_013`;
- no eliminar módulos existentes;
- no habilitar selección automática;
- no incorporar LLM runtime;
- no generar diagnóstico causal;
- no crear una segunda raíz productiva.