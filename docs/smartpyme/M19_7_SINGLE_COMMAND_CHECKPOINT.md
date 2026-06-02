# M19.7 — Checkpoint Single Command

Fecha: 2026-06-02
Estado: READY_COMMITTED_PUSHED
Commit funcional: b58aba9 feat(smartpyme): add pipeline radiography scenario runner

## Veredicto

M19.7 queda cerrado.

Pipeline Radiography ahora puede ejecutarse localmente con comando unico:

python -m pymia.pipeline_radiography.run_scenarios

Con directorio de salida configurable:

python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/manual_m19_7

## Incorporado

- pymia/pipeline_radiography/run_scenarios.py
- pymia/pipeline_radiography/scenarios_registry.py
- tests/smartpyme/test_pipeline_radiography_run_scenarios.py
- docs/smartpyme/M19_7_SINGLE_COMMAND_AUDIT.md

Tambien se actualizaron:

- pymia/pipeline_radiography/__init__.py
- tests/smartpyme/e2e/test_pipeline_radiography_excel.py

## Escenarios actuales

- margin_excel_happy_path
- margin_excel_missing_evidence
- evidence_type_mismatch
- unsupported_runtime_classification

## Artefactos generados

Por escenario:

- report.md
- trace.json

Globales:

- summary.json
- index.md

## Exit codes

- 0 si todos los escenarios quedan en PASS o BLOCKED_EXPECTED.
- 1 si algun escenario queda en FAIL o AMBIGUOUS.

AMBIGUOUS se trata como fallo operativo para evitar aprobar estados no concluyentes.

## Validaciones reportadas

- tests/smartpyme/test_pipeline_radiography_run_scenarios.py: 2 passed
- tests/smartpyme/e2e/test_pipeline_radiography_excel.py: 4 passed
- suite focal radiography: 9 passed
- tests/smartpyme: 597 passed

Validacion manual reportada:

python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/manual_m19_7

Resultado: exit code 0.

summary.json reportado:

- total_scenarios: 4
- passed: 2
- blocked_expected: 2
- failed: 0
- ambiguous: 0

## Que no mezcla

- e2e_cli.py
- Telegram
- PDF
- HTML
- Docling
- UI
- supplier_duplicate_check
- IA residente runtime

## Significado

Pipeline Radiography deja de ser solo una suite e2e y pasa a ser una herramienta local ejecutable:

un comando -> cuatro escenarios -> reportes por escenario -> summary global -> exit code operativo.

## Proximos frentes posibles

- M20: capability registry machine-readable.
- M17: supplier_duplicate_check al dispatcher formal.
- M19.8: CI/GitHub Actions para correr radiografia automaticamente.

Recomendacion: avanzar con M20 antes de M17 para gobernar capacidades desde una fuente de verdad legible por maquina.

## Frase rectora

Una radiografia util debe poder correrse con un comando.
