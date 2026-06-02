# M17 — Checkpoint Supplier Dispatcher Integration

Fecha: 2026-06-02
Estado: READY_COMMITTED_PUSHED
Commit: d55e350 feat(smartpyme): dispatch supplier duplicate check

## Veredicto

M17 queda cerrado.

supplier_duplicate_check dejo de ser una capacidad solo disponible por camino lateral y quedo integrada al dispatcher formal de SmartPyme.

## Incorporado

- Integracion de supplier_duplicate_check en pymia/smartpyme/microservice_dispatcher.py
- Fixture tests/fixtures/smartpyme/proveedores_duplicados.xlsx
- Smoke dispatcher para supplier_duplicate_check
- Escenario Pipeline Radiography supplier_duplicate_check_happy_path
- Actualizacion de capabilities.yaml
- Actualizacion de test_capability_registry.py
- Auditoria docs/smartpyme/M17_SUPPLIER_DISPATCHER_INTEGRATION_AUDIT.md

## Estado de supplier_duplicate_check despues de M17

En capabilities.yaml:

- status: PIPELINE_CERTIFIED
- pipeline_certified: true
- dispatcher_available: true
- cli_available: true
- dispatcher_classification: supplier_duplicate_check

Lectura operativa:

supplier_duplicate_check ahora es una capacidad formal del pipeline, ejecutable por dispatcher y radiografiada por Pipeline Radiography.

## Detalle tecnico clave

El plugin diagnose_supplier_duplicates devuelve una tupla:

result, _ = diagnose_supplier_duplicates(...)

El dispatcher desempaqueta la tupla y serializa el primer elemento como resultado real.

Esto evita pasar una tupla completa a raw_result o a serializacion de resultado.

## Tests reportados

- tests/smartpyme/test_one_microservice_smoke.py: 14 passed
- tests/smartpyme/test_capability_registry.py: 5 passed
- tests/smartpyme/e2e/test_pipeline_radiography_excel.py: 5 passed
- tests/smartpyme: 602 passed

Validacion de prohibidos:

- Sin matches para telegram/pdf/docling/html en los archivos del scope M17.

## Que se preserva

- excel_diagnostic sigue pasando.
- unknown_classification sigue retornando UNSUPPORTED.
- No se toca Telegram/PDF/HTML/UI.
- No se usa e2e_cli.py para certificar pipeline formal.
- No se elimina camino CLI existente.

## Significado

Antes de M17, SmartPyme tenia una unica capacidad formalmente certificada por dispatcher y radiografia: excel_diagnostic.

Despues de M17, SmartPyme tiene dos capacidades formales certificadas:

- excel_diagnostic
- supplier_duplicate_check

Esto confirma que el pipeline no es un caso especial de Excel, sino un circuito extensible para mas maquinas bajo contratos, registry y radiografia.

## Estado del pipeline tras M17

Componentes consolidados:

- Pipeline Radiography v0
- negativos sanos
- report.md y trace.json
- comando unico run_scenarios
- registry machine-readable
- segunda capacidad formal en dispatcher

## Proximos frentes recomendados

Opciones sanas:

1. M19.8 — CI/GitHub Actions para ejecutar radiografia automaticamente.
2. M21 — arnes minimo que lea registry + traces + reports.
3. M22 — tercer plugin/capacidad solo despues de consolidar CI o arnes.

Recomendacion metodologica:

Avanzar con M19.8 si el objetivo inmediato es evitar regresiones automaticamente en cada push.
Avanzar con M21 si el objetivo inmediato es preparar IA residente sobre hechos del sistema.

## Frase rectora

Una capacidad no esta cerrada porque existe un plugin: esta cerrada cuando registry, dispatcher, radiografia y tests la sostienen.
