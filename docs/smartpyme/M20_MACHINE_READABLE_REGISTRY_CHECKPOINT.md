# M20 — Checkpoint Machine-Readable Capability Registry

Fecha: 2026-06-02
Estado: READY_COMMITTED_PUSHED

## Veredicto

M20 queda cerrado.

SmartPyme ahora tiene un registry de capacidades legible por maquina y un lector Python minimo.

## Incorporado

- pymia/smartpyme/capabilities.yaml
- pymia/smartpyme/capability_registry.py
- tests/smartpyme/test_capability_registry.py
- docs/smartpyme/M20_MACHINE_READABLE_REGISTRY_AUDIT.md

Tambien se actualizo:

- docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md

## Estado actual de capacidades

### excel_diagnostic

- status: PIPELINE_CERTIFIED
- pipeline_certified: true
- dispatcher_available: true
- cli_available: true
- plugin_module: pymia.smartpyme.excel_diagnostic
- plugin_function: diagnose_excel
- dispatcher_classification: excel_diagnostic

Lectura operativa:

excel_diagnostic es la primera capacidad formalmente certificada por Pipeline Radiography.

### supplier_duplicate_check

- status: PARTIALLY_AVAILABLE_BY_PATH
- pipeline_certified: false
- dispatcher_available: false
- cli_available: true
- plugin_module: pymia.smartpyme.classifications.supplier_duplicate_check
- plugin_function: diagnose_supplier_duplicates
- dispatcher_classification: supplier_duplicate_check

Lectura operativa:

supplier_duplicate_check existe y funciona por camino lateral/CLI, pero no esta conectado al dispatcher formal. M20 no cambia ese estado.

### report_html

- status: NOT_FOUND
- pipeline_certified: false
- dispatcher_available: false
- cli_available: false

Lectura operativa:

No debe prometerse como capacidad disponible.

### document_parser_front

- status: NOT_FOUND
- pipeline_certified: false
- dispatcher_available: false
- cli_available: false

Lectura operativa:

No debe prometerse como capacidad disponible al cierre de M20.

## Lector Python incorporado

pymia/smartpyme/capability_registry.py expone:

- load_registry()
- list_capabilities()
- get_capability(capability_id)
- is_pipeline_certified(capability_id)
- is_dispatcher_available(capability_id)

Validaciones incluidas:

- capability_id unico
- status permitido
- campos minimos presentes
- consistencia plugin_module / plugin_function

## Validaciones reportadas

- tests/smartpyme/test_capability_registry.py: 5 passed
- tests/smartpyme: 602 passed

Validaciones de seguridad reportadas:

- supplier_duplicate_check no aparece como dispatcher_available true en capabilities.yaml
- supplier_duplicate_check no fue conectado en microservice_dispatcher.py

## Que NO hace M20

- No conecta supplier_duplicate_check al dispatcher.
- No implementa M17.
- No modifica el dispatcher.
- No mezcla Telegram/PDF/HTML/UI.
- No convierte capacidades NOT_FOUND en disponibles.

## Significado

Antes de M20, el registry era principalmente Markdown explicativo.

Ahora existe una fuente machine-readable para que Pipeline Radiography, futuros gates, dispatcher checks e IA residente puedan consultar capacidades sin inferir desde texto libre.

## Proximos frentes recomendados

- M17: supplier_duplicate_check al dispatcher formal, actualizando capabilities.yaml.
- M19.8: CI/GitHub Actions para ejecutar radiografia automaticamente.
- M21: arnes minimo que lea registry + traces + reports.

Recomendacion: avanzar con M17 si el objetivo inmediato es demostrar una segunda maquina formal dentro del dispatcher.

## Frase rectora

El registry no debe describir deseos: debe describir la capacidad real observable del sistema.
