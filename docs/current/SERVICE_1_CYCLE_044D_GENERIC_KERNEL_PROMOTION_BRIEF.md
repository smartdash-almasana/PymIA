# Servicio 1 — CYCLE_044D promoción del Generic Capability Kernel

**Ciclo:** `CYCLE_044D_PROMOTE_GENERIC_KERNEL`  
**Estado inicial:** `AUTHORIZED_FOR_IMPLEMENTATION`  
**Base certificada:** `CYCLE_044C_RUN_GENERIC_SHADOW_EQUIVALENCE = CLOSED_PASS`  
**Regresión base:** `1723 passed`  
**Rollback base:** `9b0de91`

## Objetivo

Promover el Generic Capability Kernel como camino productivo primario exclusivamente para:

- `LIQ_002 / projected_closing_cash_balance`;
- `PYME_011 / dso`.

La promoción no crea una segunda raíz. La única raíz continúa siendo:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

## Decisión de diseño

La raíz productiva invocará directamente:

```text
execute_generic_capability_v1
```

para `LIQ_002` y `PYME_011` cuando exista:

- solicitud explícita de capacidad;
- plan gobernado `READY_FOR_COMPUTATION`;
- evidencia normalizada completa;
- bindings confirmados;
- flags de seguridad explícitamente `false`.

Los módulos actuales de evaluator, normalized evidence y outcome permanecen sin eliminar ni reescribir durante este ciclo. Continúan siendo:

- APIs públicas compatibles;
- referencia de equivalencia;
- mecanismo de rollback;
- cobertura histórica.

No se ejecutarán en paralelo dentro de la raíz.

## Flujo promovido

```text
solicitud explícita
→ plan gobernado
→ Generic Capability Kernel
→ computation_result genérico
→ bounded_outcome embebido promovido a salida de raíz
→ política de entrega bloqueada
```

## Compatibilidad del paquete de raíz

La raíz debe conservar:

- `status = COMPUTATION_PLAN_READY` cuando la ejecución finaliza correctamente;
- `computation_executed = true`;
- `bounded_finding_generated = true`;
- `delivery_generated = false`;
- `diagnosis_generated = false`;
- `runtime_authorized = false`;
- `delivery_authorized = false`.

El `bounded_outcome` promovido debe contener al menos:

- `status = OUTCOME_READY`;
- `capability_ref`;
- `classification`;
- `finding`;
- `treatment_actions`;
- `limitations`;
- `forbidden_claims`;
- `inputs_used`;
- `computed_results`;
- `bounded_finding_generated = true`;
- `causal_diagnosis_generated = false`;
- `runtime_authorized = false`;
- `delivery_authorized = false`.

## Seguridad canónica

La promoción adopta como contrato obligatorio:

```text
flag seguro = clave presente y valor exactamente false
```

La ausencia de un flag no se interpreta como seguridad.

Flags:

- `runtime_authorized`;
- `tool_execution_authorized`;
- `product_ready`;
- `delivery_authorized`;
- `diagnosis_generated`.

## Prohibiciones

Este ciclo no autoriza:

- conectar `PYME_013`;
- modificar `LIQ_001` o `REN_001`;
- eliminar módulos legacy;
- ejecutar camino legacy y kernel simultáneamente en producción;
- crear una segunda raíz;
- selección automática de capacidad;
- LLM runtime;
- diagnóstico causal;
- entrega XLSX para `LIQ_002` o `PYME_011`;
- ampliar el AST matemático;
- agregar nuevas patologías al registro.

## Criterios de aceptación

1. La raíz importa y ejecuta el kernel para `LIQ_002` y `PYME_011`.
2. Los adapters legacy dejan de ser callers de la raíz para esas dos capacidades.
3. Las APIs públicas legacy permanecen importables y sus tests siguen verdes.
4. Existe una sola ejecución por solicitud.
5. Los tests de shadow equivalence siguen verdes.
6. Los resultados y clasificaciones continúan equivalentes.
7. Los flags de seguridad deben estar explícitamente en `false`.
8. La entrega permanece bloqueada con los mismos códigos públicos:
   - `LIQ_002_DELIVERY_NOT_AUTHORIZED`;
   - `PYME_011_DELIVERY_NOT_AUTHORIZED`.
9. La raíz productiva sigue siendo única.
10. La regresión completa queda verde.

## Rollback

Ante divergencia no resoluble dentro del ciclo:

```text
git revert de la promoción
→ restaurar callers legacy en service_1_product_pipeline_v1.py
→ conservar kernel y shadow tests aislados
```

El rollback no requiere eliminar el kernel ni sus contratos.

## Próximo ciclo condicionado

Sólo después de `CYCLE_044D = CLOSED_PASS`:

```text
CYCLE_045_CONNECT_PYME_013_USING_GENERIC_KERNEL
```

`PYME_013` deberá implementarse como capacidad compuesta y no reconstruir implícitamente `DSO` desde evidencia cruda.
