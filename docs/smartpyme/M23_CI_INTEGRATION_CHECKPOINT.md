# M23 — Operational Harness CI Integration Checkpoint

## Fecha

2026-06-04

## Estado

READY_COMMITTED_PUSHED

## Veredicto

M23 queda cerrado.

## Commit principal

```text
e87d8be ci(smartpyme): publish operational harness status
```

## Commits de contexto

```text
866fbed feat(smartpyme): add minimal operational harness
425d9f3 fix(smartpyme): detect stale certified capabilities
af52536 docs(smartpyme): audit operational harness ci integration
```

## Objetivo del hito

Integrar el Operational Harness al workflow de Pipeline Radiography como artefacto observable de CI.

El harness en CI no reemplaza Pipeline Radiography, no ejecuta capacidades y no decide negocio.

Su función es publicar el estado consolidado derivado de artefactos ya generados:

```text
capability registry
+ summary.json
+ trace.json
-> harness_status.json
```

## Incorporado

### 1. Entry point mínimo

Archivo:

```text
pymia/operational_harness/__main__.py
```

Función:

- acepta `--output-dir`;
- llama `build_operational_status(output_dir)`;
- escribe `<output_dir>/harness_status.json`;
- serializa JSON determinístico con `sort_keys=True`;
- no ejecuta Pipeline Radiography;
- no importa dispatcher/plugins;
- no usa red ni IA.

### 2. Workflow CI

Archivo:

```text
.github/workflows/smartpyme-radiography.yml
```

Cambio:

- agrega paso para ejecutar:

```text
python -m pymia.operational_harness --output-dir .pipeline_radiography/ci
```

- sube `.pipeline_radiography/ci/harness_status.json` como artefacto:

```text
operational-harness-status
```

El paso es observacional: no se agregó lógica para fallar el job por `pipeline_status` YELLOW/RED.

### 3. Test del entry point

Archivo:

```text
tests/smartpyme/test_operational_harness.py
```

Test agregado:

```text
test_harness_main_writes_status_json
```

Verifica que `python -m pymia.operational_harness --output-dir <dir>` genera `harness_status.json` con JSON válido y claves operacionales mínimas.

### 4. Forbidden imports ampliado

El test de imports prohibidos quedó endurecido para revisar todos los `.py` bajo:

```text
pymia/operational_harness/
```

incluyendo `__main__.py`.

## Validaciones reportadas

```text
python -m pytest tests/smartpyme/test_operational_harness.py -q
```

Resultado:

```text
17 passed
```

```text
python -m pytest tests/smartpyme -q
```

Resultado:

```text
619 passed
```

Validación de imports prohibidos:

```text
rg -n "requests|httpx|urllib|langchain|openai|google|telegram|pdf|html|dashboard|microservice_dispatcher|diagnose_excel|diagnose_supplier" pymia/operational_harness tests/smartpyme/test_operational_harness.py
```

Resultado:

```text
sin matches / exit code 1
```

## Límites preservados

M23 preservó explícitamente estos límites:

- No modificar `capabilities.yaml`.
- No modificar `capability_registry.py`.
- No modificar `pymia/pipeline_radiography/*`.
- No tocar dispatcher.
- No tocar plugins.
- No tocar `conversa-engine/`.
- No tocar producto/capacidades nuevas.
- No tocar Telegram.
- No tocar PDF.
- No tocar HTML.
- No tocar UI/dashboard.
- No agregar IA.
- No agregar red.
- No convertir el harness en ejecutor.
- No gatear CI por el estado semaforizado del harness.

## Resultado metodológico

M23 no certifica nuevas capacidades.

M23 conecta la capa de observabilidad operacional al CI:

```text
Pipeline Radiography CI
-> summary.json / trace.json
-> Operational Harness
-> harness_status.json
-> artifact de CI
```

El gate formal sigue siendo:

```text
Pipeline Radiography + pytest
```

El harness aporta trazabilidad consolidada y lectura operacional, no autoridad de despliegue ni decisión de producto.

## Estado de capacidades al cierre

Capacidades certificadas al cierre de esta línea:

```text
excel_diagnostic
supplier_duplicate_check
```

Entradas registradas como no encontradas/no certificadas:

```text
report_html
document_parser_front
```

Estas entradas no deben tratarse como capacidades activas ni como candidatas reales sin auditoría previa.

## Próximos frentes posibles

No decididos por este checkpoint.

Cualquier próximo hito debe partir de auditoría explícita y no de inferencias por nombre.

Opciones abstractas a evaluar:

1. auditoría de brecha producto;
2. selección de próxima capacidad certificable con evidencia real;
3. contrato mínimo de entrega/producto;
4. endurecimiento adicional de registry/radiography sólo si aparece inconsistencia real;
5. documentación de skills/specs de factoría si se conecta directamente con construcción de producto.

## Regla de continuidad

No abrir nuevas capacidades, producto, UI, HTML/PDF, Telegram ni dashboard a partir de M23 sin pasar por:

```text
Coder audit
-> reviewer externo
-> recorte de scope
-> implementación mínima
-> pytest/CI
-> checkpoint
```
