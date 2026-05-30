# MicroSaaS Code Quarries Checkpoint

Fecha: 2026-05-30
Estado: DOCUMENTACION_DE_RESCATE_SIN_IMPLEMENTACION

## Proposito

Este documento conserva la auditoria de canteras de codigo para futuros microSaaS dentro de PymIA.

No implementa microSaaS. No modifica Domain Core V1. No copia codigo externo. No abre runtime, frontend, DB, auth, Hermes, Telegram ni LangGraph.

## Decision vigente

Los microSaaS futuros deben convivir dentro de PymIA en una bahia enchufable, probablemente bajo:

```text
pymia/microsaas/
```

Regla de frontera:

```text
Los microSaaS pueden consumir capacidades externas/controladas, pero no deben importar ni modificar pymia/domain/* sin contrato explicito.
```

## Contexto PymIA previo

Antes de este checkpoint, PymIA venia de cerrar:

- M16.5: estabilizacion Domain Core V1.
- M17: Domain Core V1 Closure Marker.
- M18: SmartPyme Domain Core V1 consumption smoke.
- M19: Orchestration conversation adapter consumption smoke.

El frente microSaaS queda pausado para retomar despues del roadmap PymIA.

## Canteras auditadas

### E:\BuenosPasos\smartcounter

Veredicto: EXTRAER_PIEZAS.

Valor principal: ingesta tabular, normalizacion, deteccion de headers, mapeo semantico de columnas, revision tabular y diagnostico de archivos reales.

Piezas candidatas:

```text
smartcounter/value_normalizer.py
smartcounter/tabular_header_detector.py
smartcounter/semantic_column_mapper.py
smartcounter/excel_reader.py
smartcounter/revision_tabular.py
smartcounter/structured_warnings.py
smartcounter/docs/MVP.md
smartcounter/docs/PRODUCT_SCOPE.md
smartcounter/docs/DICCIONARIO_COLUMNAS_INICIAL.md
smartcounter/docs/MATRIZ_VALIDACION_TABULAR_HEADER.md
```

Riesgos: no traer todo smartcounter; no traer Playwright; no traer OCR/PDF pesado en primer ciclo; evitar scripts con estado global, logs, cache o rutas absolutas.

Uso recomendado: primer microSaaS candidato `intake_normalizer`.

### E:\BuenosPasos\exeland2

Veredicto: REUTILIZAR COMO REFERENCIA / EXTRAER_PIEZAS.

Valor principal: factoria deterministica de Excel, specs YAML, catalogos, generacion de plantillas, tests y arquitectura fail-closed.

Piezas candidatas:

```text
exeland2/src/exceland_factory/models.py
exeland2/src/exceland_factory/factory.py
exeland2/src/exceland_factory/spec_compiler.py
exeland2/src/exceland_factory/postprocess.py
exeland2/src/exceland_factory/protection.py
exeland2/src/exceland_factory/registry.py
exeland2/catalog/formulas.yaml
exeland2/catalog/validations.yaml
exeland2/specs/precio_margen.yaml
exeland2/specs/stock_control.yaml
exeland2/warehouse/templates/precio_margen.xlsx
exeland2/warehouse/templates/stock_control.xlsx
```

Riesgos: no copiar dist ni templates generados como core; no traer toda la CLI si solo se necesita builder; no mezclar generacion de plantillas con diagnostico en el primer ciclo.

Uso recomendado futuro: `excel_template_generator`.

### E:\BuenosPasos\smartbridge\smartcounter_core

Veredicto: SOLO_ESQUELETO_LIMPIO / RESCATAR_CON_ADAPTACION.

Valor principal: modelo minimo de comparacion/reconciliacion con Entity, Uncertainty, Finding y pipeline conceptual ingest -> normalize -> resolve -> compare -> findings.

Piezas candidatas:

```text
smartbridge/smartcounter_core/models.py
smartbridge/smartcounter_core/entity_resolution.py
smartbridge/smartcounter_core/comparison.py
smartbridge/smartcounter_core/findings.py
smartbridge/smartcounter_core/pipeline.py
```

Limitacion: `ingestion.py` es stub y `normalization.py` es passthrough.

Uso recomendado: inspiracion para contratos internos de hallazgos y comparacion, no motor productivo directo.

### E:\BuenosPasos\smartexcel

Veredicto: SOLO_REFERENCIA.

Valor principal: PoC agente PyME, backend/webhook/logs, posibles reglas/scoring y experiencia previa de normalizacion.

Piezas candidatas a revisar despues:

```text
smartexcel/poc-agente-pyme/
smartexcel/src/
smartexcel/docs/
smartexcel/config/
smartexcel/db/
```

Riesgos: mezcla Node/TS con Python; posible acoplamiento a backend previo; logs y cloudflared no deben copiarse.

### E:\BuenosPasos\SmartSheet

Veredicto: SOLO_REFERENCIA_UI.

Valor principal: UI/experiencia vinculada a hojas de calculo, posible referencia para producto o add-on.

Piezas candidatas:

```text
SmartSheet/README.md
SmartSheet/implementation-roadmap.md
SmartSheet/src/
SmartSheet/.kiro/specs/
```

Riesgos: acoplamiento a Google Sheets / Apps Script; Node/TS; no usar en primer ciclo backend.

## Primer microSaaS recomendado para retomar

```text
intake_normalizer
```

Motivo:

- es la capacidad previa necesaria antes de diagnosticar margen, stock, proveedores o conciliacion;
- trabaja con el caos real de Excel/CSV;
- aporta valor a contadores y PyMEs;
- puede ser local, deterministica y testeable;
- encaja con la filosofia SmartPyme: recibir caos, estructurarlo y devolver claridad.

## Capacidades objetivo del primer microSaaS

Nombre tentativo:

```text
contador_excel_review / intake_normalizer
```

Entrada:

```text
- archivo Excel o CSV;
- o filas tabulares ya leidas;
- tenant_id futuro;
- contexto opcional del tipo de archivo.
```

Salida:

```text
- headers detectados;
- columnas vacias;
- duplicados;
- tipos inferidos;
- columnas semanticas probables;
- warnings estructurados;
- estado: OK / NEEDS_REVIEW / BLOCKED;
- recomendaciones de evidencia o limpieza.
```

## Estructura propuesta futura

No implementada todavia.

```text
pymia/microsaas/
  __init__.py
  contracts.py
  registry.py
  intake_normalizer/
    __init__.py
    models.py
    service.py
    adapters.py
    README.md

tests/microsaas/
  test_registry.py
  test_intake_normalizer.py

docs/microsaas/
  MICROSAAS_PLUGIN_BAY.md
  MICROSAAS_CODE_QUARRIES_CHECKPOINT.md
```

## Criterios de compatibilidad con PymIA

Un archivo rescatado debe cumplir preferentemente:

- deterministico;
- testeable offline;
- sin red;
- sin DB obligatoria;
- sin Playwright;
- sin OCR pesado;
- sin rutas absolutas;
- sin credenciales;
- sin dependencia de frontend;
- sin imports a pymia/domain/*;
- entrada y salida estructuradas.

## No copiar

```text
node_modules/
dist/
build/
.pytest_cache/
logs
*.log
cloudflared scripts
Playwright outputs
archivos pesados generados
caches
zips/rar
runtime service files
credenciales
rutas absolutas operativas
```

## Plan de rescate en tres ciclos

### Ciclo 1 — Bahia de microSaaS

Crear solo:

```text
pymia/microsaas/contracts.py
pymia/microsaas/registry.py
tests/microsaas/test_microsaas_registry.py
docs/microsaas/MICROSAAS_PLUGIN_BAY.md
```

Sin microSaaS concreto.

### Ciclo 2 — intake_normalizer minimo

Crear un servicio local deterministico que acepte filas tabulares simples y devuelva diagnostico estructural.

Canteras principales:

```text
smartcounter/value_normalizer.py
smartcounter/tabular_header_detector.py
smartcounter/semantic_column_mapper.py
smartcounter/structured_warnings.py
```

### Ciclo 3 — primer output vendible

Agregar reporte legible:

```text
Markdown / JSON / Excel simple
```

Canteras secundarias:

```text
exeland2/src/exceland_factory/*
smartbridge/smartcounter_core/findings.py
```

## Reglas de pausa

Este checkpoint existe para pausar microSaaS y volver al roadmap PymIA sin perder la excavacion.

Cuando se retome:

1. leer este documento;
2. no volver a auditar desde cero;
3. crear primero la bahia pymia/microsaas/;
4. luego implementar intake_normalizer como primer plugin;
5. no tocar Domain Core V1.
