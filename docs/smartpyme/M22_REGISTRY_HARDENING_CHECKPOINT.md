# M22 — Registry Hardening Checkpoint

## Estado

CLOSED_PUSHED

## Commit

```text
425d9f3 fix(smartpyme): detect stale certified capabilities
```

## Contexto

M22 se ejecutó después del cierre de:

```text
866fbed feat(smartpyme): add minimal operational harness
a694742 docs(smartpyme): checkpoint operational harness
```

M21 agregó el Operational Harness mínimo como lector puro y determinístico.
M22 endureció ese harness para detectar inconsistencias entre el registry y la radiografía actual.

## Problema tratado

Antes de M22, el harness podía reportar un estado demasiado sano si una capability marcada como certificada en el registry no estaba cubierta por trazas de la radiografía actual.

La brecha concreta era:

```text
capability registry declara PIPELINE_CERTIFIED
+
radiography actual no contiene trace con runtime_classification compatible
=
riesgo de certificación stale/no ejercitada
```

## Cambio implementado

Se agregó al output del harness:

```text
stale_certified_capabilities
```

Una capability certificada se considera stale si:

```text
pipeline_certified == true
```

y no existe ninguna traza actual con:

```text
trace.trace.final_summary.runtime_classification == capability.dispatcher_classification
```

## Efecto operacional

El harness ahora marca estado `YELLOW` cuando existen stale certified capabilities.

La prioridad de `next_action` quedó:

```text
1. FAIL                         -> FIX_SCENARIO / FIX_SCENARIOS
2. AMBIGUOUS real del trace      -> RE_RUN_RADIOGRAPHY
3. orphan classification         -> REVIEW_REGISTRY
4. stale certified capabilities  -> REVIEW_REGISTRY
5. partial capabilities          -> REVIEW_PARTIAL_CAPABILITY
6. sin inconsistencias           -> NONE
```

## Archivos modificados

```text
pymia/operational_harness/harness.py
tests/smartpyme/test_operational_harness.py
```

## Tests agregados

```text
test_detects_stale_certified_capability
test_no_stale_certified_capability_when_traces_exist
test_stale_takes_precedence_over_partial
test_fails_take_precedence_over_stale
test_ambiguous_take_precedence_over_stale
```

## Validaciones ejecutadas

```text
python -m pytest tests/smartpyme/test_operational_harness.py -q
```

Resultado:

```text
16 passed
```

```text
python -m pytest tests/smartpyme -q
```

Resultado:

```text
618 passed
```

Validación de imports prohibidos:

```text
rg -n "requests|httpx|urllib|langchain|openai|google|telegram|pdf|html|dashboard|microservice_dispatcher|diagnose_excel|diagnose_supplier" pymia/operational_harness tests/smartpyme/test_operational_harness.py
```

Resultado:

```text
sin matches / exit code 1
```

Estado Git tras push:

```text
git status --short -> limpio
```

## Límites preservados

M22 preservó explícitamente estos límites:

- No se modificó `capabilities.yaml`.
- No se modificó `capability_registry.py`.
- No se modificó `pymia/pipeline_radiography/*`.
- No se modificó CI.
- No se agregó CLI.
- No se tocó dispatcher.
- No se tocaron plugins.
- No se tocó Telegram.
- No se tocó PDF.
- No se tocó HTML.
- No se tocó UI.
- No se agregó IA.
- No se agregó red.

## Resultado metodológico

M22 no certifica nuevas capacidades.

M22 mejora el control de verdad entre:

```text
capability registry
+
radiography traces
+
operational harness
```

El harness ahora puede señalar que una capacidad registrada como certificada requiere revisión si la radiografía actual no la ejercita.

## Regla de continuidad

No tratar entradas `NOT_FOUND` del registry como capacidades candidatas reales sin auditoría previa.

Ejemplo documentado:

```text
report_html
```

En el registry figura como:

```text
status: NOT_FOUND
pipeline_certified: false
dispatcher_available: false
cli_available: false
plugin_module: null
plugin_function: null
tests: []
```

Por lo tanto, no debe presentarse como capacidad activa ni como próximo hito sin lectura y auditoría.

## Próximo paso posible

No decidido en este checkpoint.

Antes de abrir un nuevo hito, corresponde auditoría Coder para decidir si avanzar sobre:

1. nueva capacidad certificable;
2. integración del harness al flujo de radiografía;
3. endurecimiento adicional de registry/radiography;
4. documentación de contrato operacional.

No iniciar implementación sin recorte de scope y revisión externa.
