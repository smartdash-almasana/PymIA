# M19.8 — Checkpoint Pipeline Radiography CI

Fecha: 2026-06-02
Estado: READY_COMMITTED_PUSHED_GREEN

## Veredicto

M19.8 queda cerrado.

GitHub Actions quedo operativo para ejecutar Pipeline Radiography y la suite SmartPyme automaticamente.

## Workflow

Archivo:

- .github/workflows/smartpyme-radiography.yml

Nombre:

- SmartPyme Pipeline Radiography CI

Triggers:

- push a main
- pull_request a main
- workflow_dispatch manual

## Comandos ejecutados por CI

- python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/ci
- python -m pytest tests/smartpyme -q

## Artefactos

El workflow sube como artifact:

- .pipeline_radiography/ci

Contenido esperado:

- index.md
- summary.json
- report.md por escenario
- trace.json por escenario

## Correcciones realizadas durante estabilizacion

### Backend de build

Se reemplazo en pyproject.toml:

- setuptools.backends.legacy:build

por:

- setuptools.build_meta

Motivo:

El entorno de GitHub Actions no podia importar setuptools.backends.legacy durante pip install editable.

### Instalacion CI sin editable install

Se elimino del workflow:

- pip install -e .[dev]

Y se uso:

- PYTHONPATH: github.workspace
- instalacion explicita de dependencias runtime/test

Motivo:

Evitar fallos de build editable no necesarios para correr radiografia y tests.

### Dependencias citadas y PyYAML

Se agregaron dependencias entre comillas para evitar interpretacion incorrecta de >= por shell.

Se agrego:

- PyYAML>=6.0

Motivo:

capability_registry.py importa yaml para leer capabilities.yaml.

### Timeout

Se agrego:

- timeout-minutes: 30

Motivo:

Evitar jobs colgados.

## Estado funcional esperado

- Pipeline Radiography command: OK
- tests/smartpyme: OK
- Artifact upload: OK
- GitHub Actions: verde

## Que no usa

- VM
- Google Cloud
- Gemini/Vertex
- secretos
- Telegram/PDF/HTML/UI
- servicios externos adicionales

## Significado

Antes de M19.8, la radiografia se podia correr localmente.

Despues de M19.8, el repositorio se radiografia automaticamente en GitHub ante cambios relevantes.

Esto reduce regresiones sobre:

- intake
- evidence_gate
- readiness
- runtime_bridge
- dispatcher
- execution_result_gate
- delivery_package
- capabilities.yaml
- excel_diagnostic
- supplier_duplicate_check

## Estado de la base tras M19.8

Capacidades certificadas:

- excel_diagnostic
- supplier_duplicate_check

Infraestructura de control:

- Pipeline Radiography
- Developer reports
- Single command runner
- Machine-readable registry
- GitHub Actions verde

## Proximos frentes recomendados

1. M21 — arnes minimo que lea registry + traces + reports.
2. M22 — nueva capacidad/plugin solo despues de arnes minimo.
3. M19.9 — endurecimiento menor CI si aparece necesidad real.

Recomendacion:

Avanzar con M21. La base deterministica ya tiene radiografia automatica; el siguiente paso sano es crear un lector/arnes operacional que consolide el estado del sistema desde registry, summary.json y traces.

## Frase rectora

Cada cambio relevante debe dejar una radiografia automatica del estado operacional del pipeline.
