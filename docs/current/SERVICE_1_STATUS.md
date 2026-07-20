# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-20

**Última regresión completa observada:** `1671 passed, 0 failed in 139s`, ejecutada por el usuario en PowerShell local después de integrar `REN_001` y alinear disposición modular, lock y completion gate.

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
LIQ_001: CÁLCULO + HALLAZGO ACOTADO + ENTREGA XLSX EXPLÍCITA
REN_001: CÁLCULO + HALLAZGO ACOTADO; ENTREGA XLSX NO AUTORIZADA
CYCLE_040_CONNECT_REN_001_TO_PRODUCTIVE_ROOT: CLOSED_PASS
S1-PILOT-005 FÁBRICA INDUSTRIAL: PASS
S1-PILOT-008 TEXTIL COMPLETA: PASS
SERIE CONTROLADA PLANIFICADA: COMPLETA
DECISIÓN POST-PILOTOS: CYCLE_039 DECIDED
EXPANSIÓN A 12 PATOLOGÍAS: ROADMAP PENDIENTE
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

`LIQ_001` no afirma morosidad, fraude, incobrabilidad, error contable ni responsabilidad causal sin evidencia adicional.

## Estado de REN_001

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

Superficie productiva:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_ren_001_evaluator_v1.py
pymia/smartpyme/service_1_ren_001_normalized_evidence_v1.py
pymia/smartpyme/service_1_ren_001_outcome_v1.py
```

Reglas y límites:

- la capacidad se activa únicamente ante request explícito `net_margin_real`;
- requiere plan listo y bindings confirmados;
- cada variable debe resolver determinísticamente desde evidencia normalizada;
- no usa muestras ni selección automática;
- no atribuye causas, responsabilidad, fraude, error de precios ni error contable;
- no genera diagnóstico causal;
- la entrega XLSX de `REN_001` permanece bloqueada;
- los módulos REN_001 están absorbidos por `docs/service_1_module_disposition.v1.json`, architecture lock y product completion gate.

Evidencia de cierre:

```text
docs/current/SERVICE_1_CYCLE_040_REN_001_PRODUCTIVE_ROOT_CLOSURE.md
docs/service_1_cycle_040_ren_001_productive_root_closure.v1.json
tests/smartpyme/test_service_1_cycle_040_ren_001_closure_v1.py
tests/smartpyme/test_service_1_ren_001_productive_root_v1.py
```

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe una segunda raíz para `REN_001`.

## Serie de pilotos controlados

```text
SERIE: COMPLETE
FUENTE: prueba_excels/
CASOS PASS: S1-PILOT-001, 003, 004, 005, 006, 007, 008
PILOTOS PLANIFICADOS PENDIENTES: 0
```

El Piloto 005 demostró el recorrido canónico sobre evidencia industrial, pero no autorizó diagnóstico industrial, scrap, OEE, eficiencia de máquina, paradas o pérdidas productivas.

## Decisión de capacidades posteriores

```text
CYCLE_039_SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION: DECIDED
1. CONNECT_REN_001_TO_PRODUCTIVE_ROOT: CLOSED_PASS
2. COMPLETE_12_PRODUCTIVE_PATHOLOGIES: NEXT
3. DESIGN_INDUSTRIAL_SCRAP_OEE_CAPABILITIES: BLOCKED_UNTIL_PRECEDING_WORK
```

La meta de doce patologías no se satisface por presencia en catálogo. Cada patología deberá cerrar definición, fórmula, evidencia mínima, límites matemáticos, evaluación, hallazgo, tratamiento, integración, entrega cuando corresponda, tests y ejecución observada.

Scrap/OEE permanece bloqueado hasta disponer de contratos matemáticos y reglas explícitas para disponibilidad, rendimiento, calidad, período, denominadores, datos faltantes, paradas y reproceso.

## Evidencia rectora

```text
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md
docs/current/SERVICE_1_CYCLE_040_REN_001_PRODUCTIVE_ROOT_CLOSURE.md
docs/service_1_product_completion_gate.v1.json
docs/service_1_architecture_lock.v1.json
docs/service_1_module_disposition.v1.json
docs/service_1_next_productive_capability_decision.v1.json
docs/service_1_cycle_040_ren_001_productive_root_closure.v1.json
tests/smartpyme/test_service_1_product_completion_gate_v1.py
tests/smartpyme/test_service_1_architecture_lock_v1.py
tests/smartpyme/test_service_1_next_productive_capability_decision_v1.py
tests/smartpyme/test_service_1_cycle_040_ren_001_closure_v1.py
```

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que todas las patologías y fórmulas estén conectadas.
- No existe selección automática de tool o capacidad desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto.
- `REN_001` está conectado, pero su entrega XLSX no está autorizada.
- Scrap y OEE no son capacidades soportadas actualmente.
- El próximo ciclo es documental y no autoriza implementar simultáneamente diez patologías.

## Próximo paso autorizado

```text
CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP
```

Alcance:

```text
Inventariar las capacidades productivas completas actuales: LIQ_001 y REN_001.
Seleccionar exactamente diez patologías adicionales para alcanzar doce.
Ordenarlas por dependencia matemática, evidencia disponible y valor PyME.
Definir para cada una fórmula, variables, evidencia mínima, dominio y límites.
Asignar un ciclo funcional individual o una secuencia explícitamente acotada.
No implementar evaluadores ni conectar nuevas patologías durante CYCLE_041.
No incluir scrap/OEE salvo como línea posterior bloqueada.
```
