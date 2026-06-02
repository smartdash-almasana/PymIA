# M21 — Minimal Operational Harness v0 Checkpoint

## Estado

CLOSED_PUSHED

## Commit

```text
866fbed feat(smartpyme): add minimal operational harness
```

## Alcance del hito

M21 agregó un arnés operacional mínimo para consolidar el estado observable del pipeline SmartPyme a partir de artefactos ya generados.

El arnés es:

- lector puro;
- determinístico;
- sin ejecución de pipeline;
- sin integración con dispatcher;
- sin IA;
- sin red;
- sin UI.

## Archivos agregados

```text
pymia/operational_harness/__init__.py
pymia/operational_harness/harness.py
tests/smartpyme/test_operational_harness.py
docs/smartpyme/M21_MINIMAL_OPERATIONAL_HARNESS_AUDIT.md
```

## API implementada

```text
load_radiography_bundle(output_dir: Path | str) -> dict
build_operational_status(output_dir: Path | str) -> dict
```

## Fuentes consolidadas

El harness lee y consolida:

- capability registry mediante `pymia.smartpyme.capability_registry.load_registry()`;
- `summary.json` de Pipeline Radiography;
- `trace.json` por escenario listado en el summary.

No parsea `capabilities.yaml` directamente.

## Output operacional

El output mínimo expone:

```text
harness_version
pipeline_status
next_action
counts
certified_capabilities
partial_capabilities
failed_scenarios
blocked_expected_scenarios
ambiguous_scenarios
```

## Reglas principales

```text
RED    -> existen failed_scenarios
YELLOW -> existen ambiguous_scenarios, orphan classifications o partial_capabilities
GREEN  -> no hay fallos, ambigüedades ni inconsistencias relevantes
```

`next_action` queda cerrado por valores explícitos:

```text
NONE
RE_RUN_RADIOGRAPHY
FIX_SCENARIO
FIX_SCENARIOS
REVIEW_REGISTRY
REVIEW_PARTIAL_CAPABILITY
```

## Validaciones ejecutadas

```text
python -m pytest tests/smartpyme/test_operational_harness.py -q
```

Resultado:

```text
11 passed
```

```text
python -m pytest tests/smartpyme -q
```

Resultado:

```text
613 passed
```

Validación de imports prohibidos:

```text
rg -n "requests|httpx|urllib|langchain|openai|google|telegram|pdf|html|dashboard|microservice_dispatcher|diagnose_excel|diagnose_supplier" pymia/operational_harness tests/smartpyme/test_operational_harness.py
```

Resultado:

```text
sin matches
```

Estado Git al cierre:

```text
git status --short -> limpio
```

## Límites preservados

M21 v0 preservó explícitamente estos límites:

- No CLI.
- No integración CI del harness.
- No dashboard.
- No IA / LLM.
- No red.
- No `requests`, `httpx` ni `urllib`.
- No dispatcher.
- No plugins.
- No modificación de `capabilities.yaml`.
- No modificación de Pipeline Radiography existente.
- No Telegram.
- No PDF.
- No HTML.
- No UI.

## Resultado metodológico

M21 no declara capacidades nuevas.

M21 agrega una capa de lectura operacional sobre evidencia ya producida:

```text
capability registry
+ summary.json
+ trace.json
-> estado operacional semaforizado
-> próxima acción explícita
```

El harness no decide negocio, no ejecuta microservicios y no reemplaza Pipeline Radiography.

Su función es hacer observable el estado consolidado del pipeline para futuros pasos de gobierno técnico.

## Próximos pasos posibles

No decididos en este checkpoint.

Opciones a evaluar en un hito posterior:

1. Integrar el harness a un comando existente o nuevo.
2. Integrar el harness al CI.
3. Usar el harness para seleccionar la próxima capacidad certificable.
4. Endurecer contratos de registry/radiography.
5. Avanzar una nueva capacidad/plugin sólo después de auditoría y recorte de scope.

## Regla de continuidad

No reabrir M21 para agregar CLI, CI, dashboard o IA sin crear un hito nuevo y pasar por auditoría previa.
