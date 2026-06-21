# FIRST_AID_TOOL_ACTIVATION_V1

## Estado

- **Tipo:** PRODUCT_CONTRACT
- **Estado:** DRAFT_APPLIED
- **Runtime impact:** NONE
- **Code impact:** NONE
- **Tests impact:** CONTRACT_ONLY

## Propósito

Definir cuándo una herramienta First Aid puede considerarse elegible para ejecución futura, sin autorizar ejecución todavía.

Este contrato es el puente seguro entre el seed contractual (`first_aid_toolbox_pack_seed_v1.json`) y la eventual activación de herramientas. Responde una sola pregunta:

> ¿Esta herramienta puede activarse con la evidencia disponible?

No ejecuta cálculo. No genera XLSX. No diagnostica. No llama IA. No toca pipeline.

## Regla central

Una herramienta First Aid sólo puede activarse si:

1. Pertenece al pack First Aid validado (source_seed: `first_aid_toolbox_pack_seed_v1.json`)
2. Tiene `tool_component_mapping` con status `ALIGNED` en el seed
3. Tiene `evidence_requirements` definidas en el seed
4. La evidencia mínima disponible cubre todos los campos en `minimum`
5. No requiere ninguna `restricted_formula_ref` para funcionar
6. No viola ningún `forbidden_claim` del pack ni de la herramienta específica
7. No hay columnas computacionales sin confirmar por el dueño
8. El `service_depth` permitido incluye `FIRST_AID`
9. El `runtime_authorized` del contrato sigue siendo `false`

Si alguna de estas condiciones falla, la herramienta se bloquea con una razón específica. No hay estado intermedio: o es elegible, o está bloqueada por una razón explícita.

## Estados de activación

| Estado | Condición | Acción |
|---|---|---|
| `ELIGIBLE` | Todas las condiciones conceptuales se cumplen | Herramienta conceptualmente elegible; no ejecutable mientras `runtime_authorized` sea `false` |
| `BLOCKED_MISSING_EVIDENCE` | Falta al menos un campo de `minimum_evidence` | Pedir evidencia faltante al dueño |
| `BLOCKED_COLUMN_CONFIRMATION` | Hay columnas computacionales sin confirmar por el dueño | Preguntar al dueño qué columna es qué |
| `BLOCKED_RESTRICTED_FORMULA` | La herramienta requiere una fórmula restringida para funcionar | Escalar a `DETERMINISTIC_DIAGNOSIS` |
| `BLOCKED_FORBIDDEN_CLAIM` | El pedido del dueño viola un `forbidden_claim` de la herramienta | Reformular el pedido o escalar |
| `BLOCKED_SCOPE_MISMATCH` | El `service_depth` pedido no incluye `FIRST_AID` | Escalar al servicio correspondiente |
| `BLOCKED_COMPONENT_NOT_ALIGNED` | El `tool_component_mapping` no tiene status `ALIGNED` | No activable; requiere auditoría de seed |
| `BLOCKED_RUNTIME_NOT_AUTHORIZED` | El `runtime_authorized` del contrato es `false` | Elegible conceptualmente pero no ejecutable |

Nota: estos estados son **mutuamente excluyentes** en una evaluación dada. La primera condición que falla determina el estado. `ELIGIBLE` sólo se alcanza cuando todas las condiciones anteriores pasan.

## Inputs conceptuales

El evaluador de activación recibe:

| Campo | Tipo | Descripción |
|---|---|---|
| `tool_ref` | string | ID de la herramienta (`caja_diaria_triage`, etc.) |
| `owner_problem` | string | Descripción del problema que el dueño quiere resolver |
| `service_depth` | string | Profundidad solicitada (`FIRST_AID`, `DETERMINISTIC_DIAGNOSIS`, etc.) |
| `available_evidence` | object | Campos disponibles con sus valores |
| `column_confirmation_status` | object | Para cada columna: `confirmed`, `unconfirmed`, `ambiguous` |
| `requested_formula_refs` | array | Fórmulas que el dueño pide calcular |
| `requested_claims` | array | Afirmaciones que el dueño espera del sistema |
| `pack_seed_status` | string | Estado del seed (`CANDIDATE_SEED`, etc.) |
| `runtime_authorized` | boolean | Si runtime está autorizado globalmente. En este contrato permanece `false`; por eso la elegibilidad conceptual no equivale a ejecución autorizada. |

## Output conceptual

El evaluador devuelve:

| Campo | Tipo | Descripción |
|---|---|---|
| `tool_ref` | string | ID de la herramienta evaluada |
| `activation_status` | string | Uno de los 8 estados definidos arriba |
| `blocking_reasons` | array | Lista de razones específicas de bloqueo (vacía si ELIGIBLE) |
| `missing_inputs` | array | Campos de `minimum_evidence` que faltan (si aplica) |
| `owner_questions` | array | Preguntas para el dueño para destrabar el bloqueo |
| `limitations` | array | Limitaciones que aplican aunque sea ELIGIBLE |
| `escalation_hint` | string | Sugerencia de escalamiento si el bloqueo es estructural |
| `runtime_authorized` | boolean | Siempre `false` hasta autorización posterior |

## Matriz de activación

| Herramienta | Componente requerido | Evidencia mínima | Fórmulas permitidas | Fórmulas restringidas | Bloqueo si... |
|---|---|---|---|---|---|
| `caja_diaria_triage` | `caja_diaria` | saldo_inicial, ingresos, egresos | flujo_caja_neto, saldo_acumulado, ingresos_totales, egresos_totales | resultado_neto | Falta alguno de los 3 mínimos |
| `precio_margen_basico` | `precio_margen` | precio_venta, costo_unitario | margen_bruto, margen_bruto_pesos, markup, precio_venta_con_margen | Todas las restringidas | Falta alguno de los 2 mínimos |
| `stock_alertas_basicas` | `StockDesvioAlertRule` | producto, stock_actual, stock_minimo | alerta_stock_minimo, dias_stock_restante | rotacion_inventario, costo_reposicion_promedio | Falta alguno de los 3 mínimos |
| `gastos_triage` | `gastos_triage` | concepto, importe | egresos_totales | resultado_neto, punto_equilibrio_unidades, punto_equilibrio_pesos | Falta alguno de los 2 mínimos |
| `proveedores_precio_variacion_triage` | `proveedores_precio_variacion_triage` | proveedor, producto_o_insumo, precio_o_costo | margen_bruto_pesos | rotacion_inventario, costo_reposicion_promedio | Falta alguno de los 3 mínimos |

## Prohibiciones

Este contrato **no autoriza**:

- Ejecutar cálculo real
- Generar XLSX descargable
- Diagnosticar la empresa
- Modificar `vertical_pipeline.py`
- Cambiar el OCF (Operational Case File)
- Llamar a IA para decidir
- Usar herramienta si falta evidencia mínima
- Prometer resultados que violen `forbidden_claims`
- Activar fórmulas restringidas bajo ningún pretexto
- Mezclar Servicio 1 con Servicio 2 o 3

## Reglas de bloqueo

1. **Evidencia mínima es innegociable.** Si falta un campo de `minimum`, la herramienta se bloquea con `BLOCKED_MISSING_EVIDENCE`. No hay fallback a cálculo parcial sin declaración explícita.

2. **Fórmulas restringidas son puerta de escalamiento.** Si una herramienta requiere `resultado_neto`, `punto_equilibrio_unidades`, `punto_equilibrio_pesos`, `rotacion_inventario` o `costo_reposicion_promedio` para funcionar, se bloquea con `BLOCKED_RESTRICTED_FORMULA` y se sugiere escalamiento a `DETERMINISTIC_DIAGNOSIS`.

3. **Forbidden claims son innegociables.** Si el dueño pide algo que viola `forbidden_claims`, se bloquea con `BLOCKED_FORBIDDEN_CLAIM` y se reformula el pedido o se escala.

4. **Columnas sin confirmar son bloqueo explícito.** Si hay columnas computacionales sin confirmar por el dueño, se bloquea con `BLOCKED_COLUMN_CONFIRMATION` y se pregunta al dueño qué columna es qué.

5. **Runtime authorization es global.** Aunque una herramienta sea `ELIGIBLE` conceptualmente, si `runtime_authorized` es `false`, el estado final es `BLOCKED_RUNTIME_NOT_AUTHORIZED`.

## Relación con otros contratos

| Contrato | Rol | Relación |
|---|---|---|
| `first_aid_toolbox_pack_seed_v1.json` | Define el pack, herramientas, componentes, evidencia | Este contrato **consume** el seed; no lo reemplaza |
| `FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` | Define la visión documental del pack | Este contrato **implementa** la regla de activación |
| `FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1.md` | Documenta creación de componentes triage | Este contrato **usa** los componentes creados |
| `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Catálogo maestro de Servicio 1 | Este contrato **operacionaliza** las 5 herramientas First Aid |

## Próximos pasos seguros (no runtime)

1. Crear test contractual para validar este JSON contra campos obligatorios
2. Validar consistencia entre este contrato y el seed
3. Documentar escenarios de activación (elegible, bloqueado por evidencia, bloqueado por fórmula)
4. Definir contrato de activación evaluator (función que consume inputs y devuelve output)
5. **Después** de todo lo anterior: considerar loader o wiring a pipeline

## Lo que NO debe pasar en este frente

- No crear `first_aid_tool_activation.py` todavía
- No tocar `vertical_pipeline.py`
- No implementar XLSX delivery
- No crear LLM adapter
- No autorizar runtime
- No correr herramientas reales
- No hacer commit de código productivo
